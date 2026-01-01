"""
SPEC: S012 - CLI Interface

Command-line interface for VL-JEPA lecture summarizer.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    IMPLEMENTS: S012

    Args:
        args: Arguments to parse (default: sys.argv[1:])

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog="vl-jepa",
        description="VL-JEPA Lecture Summarizer - Event-aware video summarization",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Process command
    process_parser = subparsers.add_parser(
        "process",
        help="Process a video file",
    )
    process_parser.add_argument(
        "video",
        type=str,
        help="Path to video file",
    )
    process_parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="data/",
        help="Output directory for embeddings and events",
    )
    process_parser.add_argument(
        "--fps",
        type=float,
        default=1.0,
        help="Frames per second to sample",
    )
    process_parser.add_argument(
        "--threshold",
        type=float,
        default=0.3,
        help="Event detection threshold",
    )

    # Query command
    query_parser = subparsers.add_parser(
        "query",
        help="Query processed lecture",
    )
    query_parser.add_argument(
        "data_dir",
        type=str,
        help="Directory containing processed data",
    )
    query_parser.add_argument(
        "--question",
        "-q",
        type=str,
        required=True,
        help="Question to search for",
    )
    query_parser.add_argument(
        "--top-k",
        "-k",
        type=int,
        default=5,
        help="Number of results to return",
    )

    # Events command
    events_parser = subparsers.add_parser(
        "events",
        help="List detected events",
    )
    events_parser.add_argument(
        "data_dir",
        type=str,
        help="Directory containing processed data",
    )

    # Demo command
    demo_parser = subparsers.add_parser(
        "demo",
        help="Launch Gradio demo UI",
    )
    demo_parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port for Gradio server",
    )
    demo_parser.add_argument(
        "--share",
        action="store_true",
        help="Create public Gradio link",
    )

    return parser.parse_args(args)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging.

    Args:
        verbose: Enable debug logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def cmd_process(args: argparse.Namespace) -> int:
    """Process a video file.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    import numpy as np

    from vl_jepa.detector import EventDetector
    from vl_jepa.frame import FrameSampler
    from vl_jepa.storage import Storage
    from vl_jepa.video import VideoInput

    logging.info(f"Processing video: {args.video}")

    # Initialize components
    video = VideoInput.open(args.video)
    sampler = FrameSampler()
    detector = EventDetector(threshold=args.threshold)
    storage = Storage(Path(args.output))

    logging.info(f"Video: {video.width}x{video.height} @ {video.fps} fps")
    logging.info(f"Output: {args.output}")

    # Process frames
    frame_interval = 1.0 / args.fps
    last_sample_time = -frame_interval
    embeddings: list[np.ndarray] = []

    for frame in video.frames():
        if frame.timestamp - last_sample_time < frame_interval:
            continue

        last_sample_time = frame.timestamp

        # Process frame and encode
        processed = sampler.process(frame.data)

        # TODO: Use actual encoder when model is available
        # encoder = VisualEncoder.load("models/vjepa.safetensors")
        # embedding = encoder.encode_single(processed)
        # For now, use random embedding based on processed frame hash
        np.random.seed(hash(processed.tobytes()) % (2**32))
        embedding = np.random.randn(768).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)

        embeddings.append(embedding)

        # Detect events
        event = detector.process(embedding, frame.timestamp)
        if event:
            logging.info(
                f"Event at {event.timestamp:.1f}s (confidence: {event.confidence:.2f})"
            )
            storage.save_event(event.timestamp, event.confidence, "")

    video.close()

    # Save embeddings
    if embeddings:
        storage.save_embeddings(np.stack(embeddings))
        logging.info(f"Saved {len(embeddings)} embeddings")

    return 0


def cmd_query(args: argparse.Namespace) -> int:
    """Query processed lecture.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    from vl_jepa.index import EmbeddingIndex
    from vl_jepa.text import TextEncoder

    logging.info(f"Querying: {args.question}")

    # Load index
    index = EmbeddingIndex.load(Path(args.data_dir) / "index")
    encoder = TextEncoder.load()

    # Encode query
    query_embedding = encoder.encode(args.question)

    # Search
    results = index.search(query_embedding, k=args.top_k)

    print(f"\nTop {len(results)} results for: {args.question}\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. ID={result.id}, Score={result.score:.3f}")
        if result.metadata:
            print(f"   Metadata: {result.metadata}")

    return 0


def cmd_events(args: argparse.Namespace) -> int:
    """List detected events.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    from vl_jepa.storage import Storage

    storage = Storage(Path(args.data_dir))
    events = storage.get_events()

    print(f"\n{len(events)} events detected:\n")
    for event in events:
        print(
            f"  [{event['id']}] {event['timestamp']:.1f}s "
            f"(confidence: {event['confidence']:.2f})"
        )
        if event["summary"]:
            print(f"      {event['summary']}")

    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    """Launch Gradio demo.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    logging.info(f"Launching demo on port {args.port}")

    try:
        # Import UI module (to be implemented)
        # from vl_jepa.ui import create_demo
        # demo = create_demo()
        # demo.launch(server_port=args.port, share=args.share)
        logging.error("Demo UI not yet implemented")
        return 1

    except ImportError:
        logging.error("Gradio not installed. Run: pip install gradio")
        return 1


def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    args = parse_args()
    setup_logging(args.verbose)

    if args.command is None:
        print("No command specified. Use --help for usage.")
        return 1

    commands = {
        "process": cmd_process,
        "query": cmd_query,
        "events": cmd_events,
        "demo": cmd_demo,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
