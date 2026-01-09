"""Entry point for running the UI module directly with `python -m vl_jepa.ui`."""

import argparse
import os

from vl_jepa.ui.app import launch


def main() -> None:
    """Launch Lecture Mind UI."""
    parser = argparse.ArgumentParser(description="Lecture Mind - AI Lecture Summarizer")
    parser.add_argument("--share", action="store_true", help="Create public link")
    parser.add_argument("--port", type=int, default=7860, help="Server port")
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1"),
        help="Server host (use 0.0.0.0 for Docker)",
    )
    parser.add_argument(
        "--no-placeholders",
        action="store_true",
        help="Use real encoders instead of placeholders",
    )

    args = parser.parse_args()

    launch(
        share=args.share,
        server_port=args.port,
        server_name=args.host,
        use_placeholders=not args.no_placeholders,
    )


if __name__ == "__main__":
    main()
