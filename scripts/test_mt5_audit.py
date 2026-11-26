from html import escape
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/mql5-ea/scripts"


def row(*values):
    return "<tr>" + "".join(f"<td>{escape(value)}</td>" for value in values) + "</tr>"


def report_html(ambiguous=False, net="1,50", summary_only=False):
    rows = [
        row("Initial Deposit:", "", "1 000.00", "Total Net Profit:", net),
        row("Total Trades:", "2", "Profit Factor:", "1.75"),
    ]
    if not summary_only:
        rows += [
            row("Orders"),
            row("Open Time", "Order", "S / L", "T / P"),
            row("2025.01.01 01:00:00", "1", "9.1", "11.5"),
            row("2025.01.01 04:00:00", "3", "0", ""),
            row("Deals"),
            row("Time", "Deal", "Symbol", "Type", "Direction", "Volume", "Order", "Commission", "Swap", "Profit", "Comment"),
            row("2025.01.01 01:00:00", "1", "EXAMPLE", "buy", "in", "0.10", "1", "-0.50", "0", "0", ""),
            row("2025.01.01 02:00:00", "2", "EXAMPLE", "sell", "in" if ambiguous else "out", "0.10", "2", "0", "0", "4", "tp"),
            row("2025.01.01 04:00:00", "3", "EXAMPLE", "sell", "in", "0.10", "3", "-0.50", "0", "0", ""),
            row("2025.01.01 04:10:00", "4", "EXAMPLE", "buy", "out", "0.10", "4", "0", "-0.50", "-1", "manual"),
        ]
    return "<html><table>" + "".join(rows) + "</table></html>"


class AuditTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)

    def run_cli(self, script, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *map(str, args)],
            cwd=self.folder, capture_output=True, text=True, encoding="utf-8",
        )

    def audit(self, html, encoding):
        report = self.folder / "example.htm"
        report.write_bytes(html.encode(encoding))
        return self.run_cli("audit_report.py", report, "--block-size", 2, "--iterations", 20, "--seed", 19)

    def test_offline_report_reads_formats_and_reconciles_returns(self):
        for encoding in ("utf-8", "utf-16", "utf-16be"):
            with self.subTest(encoding=encoding):
                result = self.audit(report_html(), encoding)
                self.assertEqual(result.returncode, 0, result.stderr)
                result = json.loads(result.stdout)
                self.assertEqual(result["summary"]["Initial Deposit"], "1 000.00")
                self.assertEqual(result["matched_trades"], 2)
                self.assertEqual(result["vectors"]["entry"]["side_counts"], {"buy": 1, "sell": 1})
                self.assertEqual(result["vectors"]["temporal"]["holding_seconds_for_matched_trades"], [3600, 600])
                self.assertEqual(result["vectors"]["sizing"]["entry_volume_counts"], {"0.10": 2})
                self.assertEqual(result["vectors"]["invalidation"]["entries_with_recorded_stop"], 1)
                self.assertEqual(result["vectors"]["invalidation"]["entries_with_recorded_zero_stop"], 1)
                self.assertEqual(result["vectors"]["exit"]["exit_comments"], {"tp": 1, "manual": 1})
                self.assertEqual(result["bootstrap"]["drawdown_percent"]["95"], 0.199302)
                self.assertEqual(result["bootstrap"]["probability_of_zero_balance"], 0)

    def test_missing_or_ambiguous_returns_do_not_get_risk_estimates(self):
        for html in (report_html(ambiguous=True), report_html(net="99"), report_html(summary_only=True)):
            result = self.audit(html, "utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["bootstrap"]["status"], "unavailable")
        self.assertNotEqual(self.audit("<html>unrelated</html>", "utf-8").returncode, 0)

    def tuning_case(self, code, same_window=False, timeout=10):
        train = {"start": "2025-01-01", "end": "2025-01-31"}
        holdout = {"start": "2025-02-01", "end": "2025-02-28"}
        spec = self.folder / "spec.json"
        spec.write_text(json.dumps({
            "direction": "maximize", "parameters": {"value": [1, 2, 3]},
            "train": train, "holdout": train if same_window else holdout,
        }), encoding="utf-8")
        adapter = self.folder / "adapter.py"
        adapter.write_text(code, encoding="utf-8")
        return self.run_cli("tune_parameters.py", spec, "--evaluator", adapter, "--workspace", self.folder,
                            "--trials", 12, "--budget", 30, "--trial-timeout", timeout, "--seed", 9)

    def test_tpe_uses_separate_holdout_and_bounded_trials(self):
        result = self.tuning_case(
            "import json, sys\nfrom pathlib import Path\n"
            "assert Path.cwd().name.startswith('trial-')\n"
            "request=json.load(sys.stdin)\n"
            "day='2025-01-01' if request['partition']=='train' else '2025-02-01'\n"
            "assert request['window']['start']==day\n"
            "value=request['parameters']['value']\n"
            "print(json.dumps({'score': float(value if request['partition']=='train' else -value)}))\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["evaluated_trials"], 12)
        self.assertEqual(data["best_parameters"], {"value": 3})
        self.assertEqual(data["train"]["score"], 3)
        self.assertEqual(data["holdout"]["score"], -3)
        self.assertFalse(list(self.folder.glob("trial-*")))

    def test_tpe_rejects_overlapping_windows_and_fails_on_timeout(self):
        invalid = self.tuning_case("raise AssertionError('must not run')", same_window=True)
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("after the training window ends", invalid.stderr)
        timeout = self.tuning_case("import time; time.sleep(5)", timeout=0.2)
        self.assertNotEqual(timeout.returncode, 0)
        self.assertIn("exceeded its time limit", timeout.stderr)
        self.assertFalse(list(self.folder.glob("trial-*")))


if __name__ == "__main__":
    unittest.main()
