#!/usr/bin/env python3
"""Validate the companion offline with the current Python (3.11 or newer).

Run from any directory. With no --output, all logs and scenario artifacts are
temporary. Supply an empty/new output directory to retain validation.json,
per-command logs, the constructed statistics demo, and the 96-case evidence.
This is a regression check of teaching controls, not a live-model evaluation.
"""
import argparse
import csv
import hashlib
import json
import math
import platform
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = {f"S{index:02d}" for index in range(1, 13)}
MODES = {"vulnerable", "hardened"}
RESULT_CLASS = "deterministic-control-simulation"


def require(condition, message):
    """Keep validation enabled even when this script is run with Python -O."""
    if not condition:
        raise ValueError(message)


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def command(name, arguments, output, report):
    # -E prevents inherited PYTHONOPTIMIZE from disabling the original self-test
    # assertions. -B avoids bytecode output; UTF-8 makes logs portable on Windows.
    invocation = [sys.executable, "-E", "-B", "-X", "utf8", *arguments]
    step = {"name": name, "command": invocation, "status": "running"}
    report["steps"].append(step)
    started = time.perf_counter()
    print(f"Running {name} ...", flush=True)
    try:
        result = subprocess.run(
            invocation, cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=180, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        step.update(status="failed", error=str(error))
        raise RuntimeError(f"{name}: {error}") from error
    finally:
        step["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    stdout_path, stderr_path = output / f"{name}.stdout.txt", output / f"{name}.stderr.txt"
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    step.update(returncode=result.returncode, stdout=stdout_path.name, stderr=stderr_path.name)
    step["status"] = "passed" if result.returncode == 0 else "failed"
    if result.returncode:
        # The default temporary output is removed after exit; print diagnostics too.
        print(result.stdout, end="", file=sys.stderr)
        print(result.stderr, end="", file=sys.stderr)
        raise RuntimeError(f"{name} exited with status {result.returncode}")
    return result


def check_demo(data):
    expected = {
        "independent_cases": 100, "baseline_successes": 30,
        "hardened_successes": 2, "improved_cases": 28, "regressed_cases": 0,
        "bootstrap_repeats": 10000, "bootstrap_seed": 20261004,
    }
    for key, value in expected.items():
        require(data.get(key) == value, f"Statistics demo: unexpected {key}")
    for key, expected_value in (
        ("baseline_rate", 0.30), ("hardened_rate", 0.02),
        ("paired_reduction", 0.28), ("mcnemar_exact_two_sided_p", 2 / (2 ** 28)),
    ):
        require(math.isclose(data[key], expected_value, rel_tol=1e-12),
                f"Statistics demo: unexpected {key}")
    for key in ("baseline_wilson_95", "hardened_wilson_95", "paired_percentile_bootstrap_95"):
        interval = data[key]
        require(len(interval) == 2 and all(math.isfinite(value) for value in interval),
                f"Statistics demo: invalid {key}")
        require(-1 <= interval[0] <= interval[1] <= 1,
                f"Statistics demo: unordered or unbounded {key}")
    require("independent sampled cases required" in data["interpretation"],
            "Statistics demo lost its sampling qualification")


def check_matrix(directory):
    summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    require(summary["result_class"] == RESULT_CLASS, "Unexpected simulation result class")
    require(summary["protocol_profile"] == "2025-11-25", "Unexpected teaching protocol profile")
    runs, rows = summary["runs"], summary["rows"]
    require(len(runs) == 96, f"Expected 96 executions; observed {len(runs)}")
    require(len(rows) == 24, f"Expected 24 grouped rows; observed {len(rows)}")
    identity = lambda row: (row["mode"], row["scenario"], row["case"])
    identities = {identity(run) for run in runs}
    require(len(identities) == 96, "Duplicate case execution identities")
    groups = {(row["mode"], row["scenario"]) for row in rows}
    require(groups == {(mode, scenario) for mode in MODES for scenario in SCENARIOS},
            "Missing or unexpected scenario/mode groups")
    for run in runs:
        require(type(run["attack"]) is bool, "Case attack label must be boolean")
        expected_breach = run["attack"] and run["mode"] == "vulnerable"
        require(run["attack_success"] == expected_breach,
                f"Attack result changed: {identity(run)}")
        require(run["benign_success"] == (not run["attack"]),
                f"Benign result changed: {identity(run)}")
        require(bool(run["violations"]) == expected_breach,
                f"Violation evidence disagrees with result: {identity(run)}")
    totals = {}
    for mode in sorted(MODES):
        group = [run for run in runs if run["mode"] == mode]
        totals[mode] = {
            "executions": len(group),
            "attack_cases": sum(run["attack"] for run in group),
            "attack_successes": sum(run["attack_success"] for run in group),
            "benign_cases": sum(not run["attack"] for run in group),
            "benign_successes": sum(run["benign_success"] for run in group),
        }
        require(totals[mode] == {
            "executions": 48, "attack_cases": 24,
            "attack_successes": 24 if mode == "vulnerable" else 0,
            "benign_cases": 24, "benign_successes": 24,
        }, f"Unexpected totals for {mode}")
    for row in rows:
        group = [run for run in runs if (run["mode"], run["scenario"]) ==
                 (row["mode"], row["scenario"])]
        expected = {
            "cases": 4, "attack_cases": 2, "benign_cases": 2,
            "attack_successes": sum(run["attack_success"] for run in group),
            "benign_successes": sum(run["benign_success"] for run in group),
        }
        require(len(group) == 4, "Scenario/mode group must contain four executions")
        require(sum(run["attack"] for run in group) == 2,
                "Scenario/mode group must contain two attack cases")
        for key, value in expected.items():
            require(row[key] == value, f"Grouped metric disagrees with runs: {key}")
        require(row["attack_success_rate"] == expected["attack_successes"] / 2,
                "Incorrect grouped attack success rate")
        require(row["benign_success_rate"] == expected["benign_successes"] / 2,
                "Incorrect grouped benign success rate")
    with (directory / "summary.csv").open(newline="", encoding="utf-8") as stream:
        csv_rows = list(csv.DictReader(stream))
    require(len(csv_rows) == 24, "CSV grouped row count disagrees with JSON")
    for csv_row, row in zip(csv_rows, rows):
        require(csv_row == {key: str(value) for key, value in row.items()},
                "CSV grouped metrics disagree with JSON")
    records, covered, event_counts, units = Counter(), set(), {}, Counter()
    with (directory / "evidence.jsonl").open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            record = json.loads(line)
            case_identity = identity(record)
            require(case_identity in identities, f"Unknown evidence identity at line {line_number}")
            require(record["record"] in {"event", "protocol"}, "Unknown evidence record kind")
            records[record["record"]] += 1
            covered.add((case_identity, record["record"]))
            if record["record"] == "event":
                group = (record["mode"], record["scenario"])
                event_counts.setdefault(group, Counter())[record["kind"]] += 1
                units[group] += record.get("units", 0)
    require(all((case, kind) in covered for case in identities
                for kind in ("event", "protocol")),
            "Each execution must retain application events and protocol evidence")
    for row in rows:
        group = (row["mode"], row["scenario"])
        require(row["tool_attempts"] == event_counts[group]["tool_attempt"],
                "Tool attempt count disagrees with evidence")
        require(row["denials"] == event_counts[group]["denied"],
                "Denial count disagrees with evidence")
        require(row["synthetic_work_units"] == units[group],
                "Work-unit count disagrees with evidence")
    return {"executions": 96, "scenario_groups": 24, "totals": totals,
            "evidence_records": dict(records), "result_class": RESULT_CLASS}


def validate(output):
    report = {
        "status": "running", "started_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "executable": sys.executable,
        "platform": platform.platform(), "steps": [],
        "interpretation": "Offline teaching-code regression; no live-model efficacy claim.",
    }
    started = time.perf_counter()
    exit_code = 0
    try:
        tests = command("unit_tests", ["-m", "unittest", "discover", "-s", "tests", "-v"],
                        output, report)
        match = re.search(r"Ran (\d+) tests? in ", tests.stderr + tests.stdout)
        require(match is not None, "Could not read unittest execution count")
        report["test_methods"] = int(match.group(1))
        require(report["test_methods"] >= 45, "Expected at least 45 unittest methods")
        fixture = command("field_self_test", ["field_server.py", "--self-test"], output, report)
        require("PASS:" in fixture.stdout, "Field fixture self-test omitted completion marker")
        statistics = command("statistics_demo", ["decision_stats.py", "--demo"], output, report)
        demo = json.loads(statistics.stdout)
        check_demo(demo)
        write_json(output / "statistics_demo.json", demo)
        report["statistics_demo"] = {"constructed_cases": 100,
                                      "interpretation": "Constructed counts, not an experiment."}
        matrix = output / "matrix"
        execution = command("scenario_matrix", ["-m", "purplelab", "run", "--mode", "both",
                            "--scenario", "all", "--output", str(matrix)], output, report)
        cli = json.loads(execution.stdout)
        require(cli["cases_executed"] == 96, "Matrix CLI did not report 96 executions")
        require(cli["result_class"] == RESULT_CLASS, "Unexpected CLI result class")
        report["matrix"] = check_matrix(matrix)
        report["artifact_sha256"] = {
            str(path.relative_to(output)).replace("\\", "/"): sha256(path)
            for path in sorted(output.rglob("*")) if path.is_file()
        }
        report["status"] = "passed"
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        report.update(status="failed", error=str(error))
        print(f"Validation failed: {error}", file=sys.stderr)
        exit_code = 1
    finally:
        report["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        report["completed_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(output / "validation.json", report)
    if exit_code == 0:
        print(f"PASS: {report['test_methods']} unit tests; field routes; statistics demo; "
              "96 scenario executions.")
        print("Vulnerable: 24/24 attack successes, 24/24 benign successes. "
              "Hardened: 0/24 attack successes, 24/24 benign successes.")
        print("These counts validate deterministic fixtures; no live model was run.")
    return exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="Retain results in a new or empty directory (default: temporary)")
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error("Python 3.11 or newer is required")
    if args.output is not None:
        output = args.output.expanduser().resolve()
        if output.exists() and (not output.is_dir() or any(output.iterdir())):
            parser.error("--output must be a new or empty directory; existing evidence is preserved")
        output.mkdir(parents=True, exist_ok=True)
        status = validate(output)
        print(f"Results retained in: {output}")
        return status
    with tempfile.TemporaryDirectory(prefix="purple-companion-validation-") as directory:
        status = validate(Path(directory))
    print("Temporary results removed. Use --output to retain logs and evidence.")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
