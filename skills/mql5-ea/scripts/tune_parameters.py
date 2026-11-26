"""Run bounded TPE trials with a reviewed, isolated Strategy Tester adapter."""

import argparse
from datetime import date
import json
import math
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def read_spec(path):
    spec = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(spec, dict) or spec.get("direction") not in ("maximize", "minimize"):
        raise ValueError("Specify direction as maximize or minimize.")
    space = spec.get("parameters")
    if not isinstance(space, dict) or not space:
        raise ValueError("Specify a nonempty parameters object.")
    for name, values in space.items():
        if (not name or not isinstance(values, list) or not values or
                any(type(value) not in (str, int, float, bool) or
                    (type(value) is float and not math.isfinite(value)) for value in values) or
                len(set(values)) != len(values)):
            raise ValueError(f"Parameter {name!r} needs a list of distinct scalar values.")
    windows = []
    for partition in ("train", "holdout"):
        period = spec.get(partition)
        if not isinstance(period, dict):
            raise ValueError(f"Specify a {partition} window with start and end dates.")
        fields = [period.get(key) for key in ("start", "end")]
        if not all(isinstance(value, str) for value in fields):
            raise ValueError(f"Specify ISO dates for {partition}.")
        start, end = map(date.fromisoformat, fields)
        if start >= end:
            raise ValueError(f"Expected start before end for {partition}.")
        windows.append((start, end))
    if windows[0][1] >= windows[1][0]:
        raise ValueError("The holdout must start after the training window ends.")
    return spec


def evaluate(adapter, request, workspace, timeout):
    with TemporaryDirectory(prefix="trial-", dir=workspace) as trial_dir:
        result = subprocess.run(
            [sys.executable, str(adapter)], input=json.dumps(request),
            cwd=trial_dir, capture_output=True, encoding="utf-8",
            timeout=timeout, check=False,
        )
    if result.returncode:
        raise ValueError(f"Evaluator exited with status {result.returncode} in {request['partition']}.")
    response = json.loads(result.stdout)
    score = response.get("score") if isinstance(response, dict) else None
    if type(score) not in (int, float) or not math.isfinite(score):
        raise ValueError("Evaluator must return one JSON object with a finite numeric score.")
    return score


def tune(spec, adapter, workspace, trials, trial_timeout, budget, seed):
    try:
        import optuna
    except ImportError as error:
        raise ValueError("TPE requires Optuna in the selected Python environment.") from error

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    sampler = optuna.samplers.TPESampler(seed=seed, n_startup_trials=min(5, trials))
    study = optuna.create_study(sampler=sampler, direction=spec["direction"])
    deadline = monotonic() + budget

    def run(parameters, partition):
        remaining = deadline - monotonic()
        if remaining <= 0:
            raise ValueError(f"Time budget expired before {partition} evaluation.")
        request = {"parameters": parameters, "partition": partition, "window": spec[partition]}
        return evaluate(adapter, request, workspace, min(trial_timeout, remaining))

    def objective(trial):
        parameters = {key: trial.suggest_categorical(key, values) for key, values in spec["parameters"].items()}
        return run(parameters, "train")

    study.optimize(objective, n_trials=trials, timeout=budget)
    parameters = study.best_params
    return {
        "status": "ok",
        "sampler": "TPE",
        "seed": seed,
        "direction": spec["direction"],
        "evaluated_trials": len(study.trials),
        "best_parameters": parameters,
        "train": {"window": spec["train"], "score": study.best_value},
        "holdout": {"window": spec["holdout"], "score": run(parameters, "holdout")},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--evaluator", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--trial-timeout", type=float, default=60)
    parser.add_argument("--budget", type=float, default=300)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if (not 1 <= args.trials <= 1000 or
            not all(math.isfinite(value) and value > 0 for value in (args.trial_timeout, args.budget))):
        parser.error("Use 1–1000 trials and positive, finite time limits.")
    try:
        spec = read_spec(args.spec)
        adapter = args.evaluator.resolve(strict=True)
        workspace = args.workspace.resolve(strict=True)
        if not adapter.is_file() or adapter.suffix.lower() != ".py" or not workspace.is_dir():
            raise ValueError("Provide a Python evaluator and an existing scratch workspace.")
        result = tune(spec, adapter, workspace, args.trials, args.trial_timeout, args.budget, args.seed)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except subprocess.TimeoutExpired:
        parser.exit(1, "Tuning failed: evaluator exceeded its time limit.\n")
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Tuning failed: {error}\n")


if __name__ == "__main__":
    main()
