import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import herdr_api  # noqa: E402


def fake_herdr(folder, body):
    """herdr 대신 실행할 가짜 실행 파일을 만든다. body 는 파이썬 코드다."""
    script = Path(folder) / "fake_herdr.py"
    script.write_text(body, encoding="utf-8")
    if herdr_api.IS_WINDOWS:
        command = Path(folder) / "fake_herdr.cmd"
        command.write_text(f'@echo off\r\n"{sys.executable}" "{script}" %*\r\n', encoding="utf-8")
    else:
        command = Path(folder) / "fake_herdr"
        command.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{script}" "$@"\n', encoding="utf-8")
        command.chmod(0o755)
    return str(command)


class CliTimeoutTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

    def run_cli(self, body, *args, check=True, timeout="1"):
        command = fake_herdr(self.folder.name, body)
        with mock.patch.dict(os.environ, {"HERDR_BIN_PATH": command, "HERDR_CLI_TIMEOUT_SECONDS": timeout}):
            return herdr_api.cli(*args, check=check)

    def test_unresponsive_herdr_raises_herdr_error_within_the_timeout(self):
        started = time.monotonic()
        with self.assertRaises(herdr_api.HerdrError) as caught:
            self.run_cli("import time\ntime.sleep(20)\n", "pane", "list")
        self.assertLess(time.monotonic() - started, 8)
        self.assertIn("no response", str(caught.exception))

    def test_unresponsive_herdr_returns_none_when_check_is_false(self):
        self.assertIsNone(self.run_cli("import time\ntime.sleep(20)\n", "pane", "list", check=False))

    def test_normal_response_is_unchanged(self):
        body = 'import json\nprint(json.dumps({"result": {"panes": [{"pane_id": "w1:p1"}]}}))\n'
        self.assertEqual(self.run_cli(body, "pane", "list", timeout="10"), {"panes": [{"pane_id": "w1:p1"}]})

    def test_empty_output_is_an_empty_result(self):
        self.assertEqual(self.run_cli("pass\n", "pane", "list", timeout="10"), {})

    def test_failed_exit_still_raises_as_before(self):
        self.assertRaises(herdr_api.HerdrError, self.run_cli, "import sys\nsys.exit(3)\n", "pane", "list", timeout="10")


class CliTimeoutSettingTest(unittest.TestCase):
    def test_default_is_ten_seconds(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("HERDR_CLI_TIMEOUT_SECONDS", None)
            self.assertEqual(herdr_api.cli_timeout(), 10)

    def test_environment_value_is_used(self):
        with mock.patch.dict(os.environ, {"HERDR_CLI_TIMEOUT_SECONDS": "2.5"}):
            self.assertEqual(herdr_api.cli_timeout(), 2.5)

    def test_invalid_or_non_positive_value_falls_back_to_default(self):
        for value in ("abc", "0", "-3"):
            with self.subTest(value=value), mock.patch.dict(os.environ, {"HERDR_CLI_TIMEOUT_SECONDS": value}):
                self.assertEqual(herdr_api.cli_timeout(), 10)


if __name__ == "__main__":
    unittest.main()
