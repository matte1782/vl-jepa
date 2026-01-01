"""
SPEC: S012 - CLI Interface
TEST_IDs: T012.1-T012.2
"""

import pytest


class TestCLI:
    """Tests for command-line interface (S012)."""

    # T012.1: Parse process command
    @pytest.mark.unit
    def test_parse_process_command(self):
        """
        SPEC: S012
        TEST_ID: T012.1
        Given: CLI args "process video.mp4 --output data/"
        When: CLI parser processes args
        Then: Correct command and paths are extracted
        """
        from vl_jepa.cli import parse_args

        args = parse_args(["process", "video.mp4", "--output", "data/"])
        assert args.command == "process"
        assert args.video == "video.mp4"
        assert args.output == "data/"

    # T012.2: Parse query command
    @pytest.mark.unit
    def test_parse_query_command(self):
        """
        SPEC: S012
        TEST_ID: T012.2
        Given: CLI args "query data/ --question 'What is ML?'"
        When: CLI parser processes args
        Then: Correct command and query are extracted
        """
        from vl_jepa.cli import parse_args

        args = parse_args(["query", "data/", "--question", "What is ML?"])
        assert args.command == "query"
        assert args.data_dir == "data/"
        assert args.question == "What is ML?"

    @pytest.mark.unit
    def test_parse_events_command(self):
        """Parse events listing command."""
        from vl_jepa.cli import parse_args

        args = parse_args(["events", "data/processed/"])
        assert args.command == "events"
        assert args.data_dir == "data/processed/"

    @pytest.mark.unit
    def test_parse_demo_command(self):
        """Parse demo launch command."""
        from vl_jepa.cli import parse_args

        args = parse_args(["demo", "--port", "8080", "--share"])
        assert args.command == "demo"
        assert args.port == 8080
        assert args.share is True

    @pytest.mark.unit
    def test_default_values(self):
        """Verify default values for optional args."""
        from vl_jepa.cli import parse_args

        args = parse_args(["process", "video.mp4"])
        assert args.output == "data/"
        assert args.fps == 1.0
        assert args.threshold == 0.3

    @pytest.mark.unit
    def test_verbose_flag(self):
        """Parse verbose flag."""
        from vl_jepa.cli import parse_args

        args = parse_args(["--verbose", "process", "video.mp4"])
        assert args.verbose is True

    @pytest.mark.unit
    def test_no_command_returns_none(self):
        """No command specified returns None."""
        from vl_jepa.cli import parse_args

        args = parse_args([])
        assert args.command is None

    @pytest.mark.unit
    def test_setup_logging_verbose(self):
        """Setup logging with verbose mode."""
        import logging

        from vl_jepa.cli import setup_logging

        # Reset root logger first
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)
        root.setLevel(logging.WARNING)

        setup_logging(verbose=True)
        # Verify debug level is set
        assert root.level == logging.DEBUG

    @pytest.mark.unit
    def test_setup_logging_normal(self):
        """Setup logging without verbose mode."""
        import logging

        from vl_jepa.cli import setup_logging

        # Reset root logger first
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)
        root.setLevel(logging.WARNING)

        setup_logging(verbose=False)
        assert root.level == logging.INFO
