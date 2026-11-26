# MT5 report audit and bounded tuning

## Offline report

Run `python scripts/audit_report.py <report.htm>` using the scripts directory next to this skill. The script reads English Strategy Tester exports in UTF-8, UTF-16 or Windows-1252, including layout spacers. It writes JSON to stdout and never starts the terminal. Inspect the raw report summary, the five observed categories and bootstrap status together.

- **Temporal:** Entry counts by report hour and holding time for unambiguously matched round trips. The report clock is the source. Identify its timezone before converting.
- **Entry:** Buy and sell entry counts. Check the report's own long and short win percentages separately.
- **Sizing:** Observed entry volume distribution. Treat position-sizing rules and pyramiding as hypotheses unless supported by separate evidence.
- **Invalidation:** Entry orders with explicit stop prices, explicit zero and missing evidence.
- **Exit:** Observed out deals, recorded target prices and comments. Comments can be examined for documented stop, target or trailing behavior.

Bootstrap uses realized, net trade returns after recorded costs. It runs only when the round trips are unambiguous, initial deposit is positive, the block has enough trades and net returns reconcile to the report. Record the seed, block size, iterations and sample window. The drawdown estimate uses realized balance and cannot capture intratrade equity movements. The depletion estimate is the simulated share of paths at or below zero during the sampled horizon. A summary-only export and complex deal sequences can still produce direct observations with a documented unavailable bootstrap. Report currency and periods from the original export.

## Bounded TPE

Use a Python environment with Optuna 4.x and a scratch directory already created. Run the following from the skill directory with your actual filenames:

```text
python scripts/tune_parameters.py search.json --evaluator tester_adapter.py --workspace scratch --trials 20 --trial-timeout 60 --budget 300
```

Provide a JSON spec with `direction` as `maximize` or `minimize`, `parameters` mapping each name to an explicit list of candidate scalar values, and `train` and `holdout` objects with ISO `start` and `end` dates. Holdout must start after train ends. Define the score and risk gates before beginning, and record fees, execution assumptions, EA revision and data provenance with the experiment.

The evaluator receives one JSON object on stdin containing `parameters`, `partition`, and `window`. It runs in a separate scratch directory per trial. It returns one JSON object with a finite numeric `score` on stdout, or a nonzero exit on failure. Use an explicitly reviewed evaluator for a dedicated Strategy Tester, with a fresh report for each candidate, and arrange for it to shut down its own tester process on completion or error. Existing scripts containing blanket terminal termination should be reviewed and isolated before use.

The harness bounds trial count and time and evaluates the selected candidate once on the withheld window. A failed evaluator or exhausted validation budget returns an error. The repository regression uses a deterministic experimental evaluator and does not require MetaTrader. When the live Tester adapter or data is unavailable, report that limitation and use exported reports for the checks they support.
