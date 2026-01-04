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

    @pytest.mark.unit
    def test_main_no_command(self, capsys):
        """
        SPEC: S012
        TEST_ID: T012.3

        Given: No command specified
        When: main() is called
        Then: Returns exit code 1 and prints help message
        """
        import sys
        from unittest.mock import patch

        from vl_jepa.cli import main

        with patch.object(sys, "argv", ["vl-jepa"]):
            exit_code = main()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "No command specified" in captured.out

    @pytest.mark.unit
    def test_main_verbose_flag(self):
        """
        SPEC: S012
        TEST_ID: T012.4

        Given: --verbose flag with no command
        When: main() is called
        Then: Logging is set to DEBUG level
        """
        import logging
        import sys
        from unittest.mock import patch

        from vl_jepa.cli import main

        # Reset logging
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)

        with patch.object(sys, "argv", ["vl-jepa", "--verbose"]):
            main()

        assert root.level == logging.DEBUG

    @pytest.mark.unit
    def test_cmd_demo_not_implemented(self):
        """
        SPEC: S012
        TEST_ID: T012.5

        Given: demo command
        When: cmd_demo is called
        Then: Returns exit code 1 (not implemented)
        """
        import argparse

        from vl_jepa.cli import cmd_demo

        args = argparse.Namespace(port=7860, share=False)
        exit_code = cmd_demo(args)
        assert exit_code == 1

    @pytest.mark.unit
    def test_parse_query_top_k(self):
        """Parse query with custom top-k."""
        from vl_jepa.cli import parse_args

        args = parse_args(["query", "data/", "-q", "test", "-k", "10"])
        assert args.top_k == 10

    @pytest.mark.unit
    def test_parse_process_custom_fps(self):
        """Parse process with custom FPS."""
        from vl_jepa.cli import parse_args

        args = parse_args(["process", "video.mp4", "--fps", "2.0"])
        assert args.fps == 2.0

    @pytest.mark.unit
    def test_parse_process_custom_threshold(self):
        """Parse process with custom threshold."""
        from vl_jepa.cli import parse_args

        args = parse_args(["process", "video.mp4", "--threshold", "0.5"])
        assert args.threshold == 0.5
