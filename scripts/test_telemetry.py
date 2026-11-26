import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SCRIPT = Path(__file__).resolve().parents[1] / "skills/tokens/scripts/telemetry.py"


class TelemetryTest(unittest.TestCase):
    def setUp(self):
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        self.home = Path(home.name)
        self.brain = self.home / ".gemini/antigravity/brain"

    def transcript(self, name, data, nested=False):
        layout = ".system_generated/logs/transcript.jsonl" if nested else "transcript.jsonl"
        path = self.brain / name / layout
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")
        return path

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home)),
        )

    def read_json(self, *args):
        result = self.run_cli("--json", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_selects_latest_exact_file_and_reads_other_layout_by_id(self):
        nested = self.transcript("nested", '{"input_tokens": 55}\n', nested=True)
        stale_nested = self.transcript("flat", '{"input_tokens": 99}\n', nested=True)
        flat = self.transcript("flat", '{"input_tokens": 10, "cache_read_tokens": 5, "output_tokens": 4}\n'
                               '{"source": "USER_EXPLICIT", "type": "USER_INPUT"}\n'
                               '{"input_tokens": 20, "cache_read_tokens": 5, "output_tokens": 2}\n')
        for path, seconds in ((nested, 10), (stale_nested, 11), (flat, 20)):
            os.utime(path, (seconds, seconds))
        report = self.read_json()
        self.assertEqual(report["conv_id"], "flat")
        self.assertEqual(report["fresh_input"], 30)
        self.assertEqual(report["base_input"], 15)
        self.assertEqual(report["cache_read"], 10)
        self.assertEqual(report["cache_hit_pct"], 25)
        self.assertEqual(report["output_tokens"], 6)
        self.assertEqual(report["turns"], 1)
        self.assertEqual(report["last_step"], {"input": 20, "cache": 5, "output": 2})
        self.assertEqual(self.read_json("--conv", "nested")["fresh_input"], 55)

    def test_ignores_incomplete_tail_and_reports_partial(self):
        self.transcript("one", '{"input_tokens": 8}\n{"output_tok')
        report = self.read_json()
        self.assertEqual(report["status"], "partial")
        self.assertEqual(report["steps"], 1)
        self.assertEqual(report["observed_metrics"], ["input_tokens"])
        self.assertIn("Data status: partial", self.run_cli().stdout)

    def test_latest_metrics_come_from_one_record(self):
        self.transcript("one", '{"input_tokens": 10, "cache_read_tokens": 5, "output_tokens": 4}\n'
                        '{"input_tokens": 20}\n{"type": "USER_INPUT"}\n')
        report = self.read_json()
        self.assertEqual(report["fresh_input"], 30)
        self.assertEqual(report["cache_read"], 5)
        self.assertEqual(report["output_tokens"], 4)
        self.assertEqual(report["last_step"], {"input": 20, "cache": 0, "output": 0})
        self.assertEqual(report["last_step_observed_metrics"], ["input_tokens"])
        self.assertIn("Latest step recorded metrics: input_tokens", self.run_cli().stdout)

    def test_reports_empty_unavailable_and_measured_zero_separately(self):
        for key, content, expected in [
            ("empty", "", "empty"),
            ("unavailable", '{"type": "USER_INPUT"}\n', "no_usage"),
            ("zero", '{"output_tokens": 0}', "ok"),
        ]:
            with self.subTest(key=key):
                self.transcript(key, content)
                report = self.read_json("--conv", key)
                self.assertEqual(report["status"], expected)
                self.assertEqual(report["output_tokens"], 0)

    def test_reports_corrupt_line_and_invalid_metric(self):
        for key, record, diagnostic in [
            ("bad", "{\n", "Invalid JSON at line 2"),
            ("wrong", '{"input_tokens": true}\n', "Invalid input_tokens at line 2"),
            ("array", "[]\n", "Expected an object at line 2"),
        ]:
            with self.subTest(key=key):
                self.transcript(key, '{}\n' + record)
                result = self.run_cli("--json", "--conv", key)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(diagnostic, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_missing_and_outside_conversations_fail(self):
        self.assertIn("not found", self.run_cli("--conv", "missing").stderr)
        for key in ("../other", r"..\other", "C:other", ""):
            with self.subTest(key=key):
                result = self.run_cli("--conv", key)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Invalid conversation ID", result.stderr)


if __name__ == "__main__":
    unittest.main()
