"""Paired security evaluation; Python 3.11+, standard library only.

Input: one independently sampled case per row, with paired binary outcomes.
Do not put repeated variants of the same source case into separate rows.
"""
import argparse
import csv
import json
import math
import random
import sys
from pathlib import Path

FIELDS = ["case_id", "baseline_success", "hardened_success"]


def wilson(k, n, z=1.959963984540054):
    if n <= 0 or not 0 <= k <= n:
        raise ValueError("Need n > 0 and 0 <= successes <= n")
    p = k / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return [max(0.0, center - half), min(1.0, center + half)]


def mcnemar_exact(improved, regressed):
    discordant = improved + regressed
    if discordant == 0:
        return 1.0
    # Integer arithmetic avoids overflow before the final division.
    tail = sum(math.comb(discordant, i)
               for i in range(min(improved, regressed) + 1))
    return min(1.0, (2 * tail) / (1 << discordant))


def quantile(sorted_values, probability):
    position = (len(sorted_values) - 1) * probability
    left = math.floor(position)
    right = math.ceil(position)
    return (sorted_values[left] * (right - position)
            + sorted_values[right] * (position - left)
            if left != right else sorted_values[left])


def paired_bootstrap(pairs, repeats=10000, seed=20261004):
    # Each pair is one independent case, so resampling preserves pairing.
    # For nested repeated trials, aggregate by independent case first.
    rng = random.Random(seed)
    differences = [baseline - hardened for baseline, hardened in pairs]
    n = len(differences)
    estimates = sorted(sum(rng.choices(differences, k=n)) / n
                       for _ in range(repeats))
    return [quantile(estimates, 0.025), quantile(estimates, 0.975)]


def read_pairs(path):
    pairs = []
    seen = set()
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError("CSV header must be: " + ",".join(FIELDS))
        for line_number, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Malformed CSV row at line {line_number}")
            case_id = row["case_id"].strip()
            if not case_id or case_id in seen:
                raise ValueError(f"Missing or duplicate case_id at line {line_number}")
            values = [row[key].strip() for key in FIELDS[1:]]
            if any(value not in {"0", "1"} for value in values):
                raise ValueError(f"Outcomes must be 0 or 1 at line {line_number}")
            seen.add(case_id)
            pairs.append(tuple(int(value) for value in values))
    if not pairs:
        raise ValueError("CSV contains no cases")
    if len(pairs) > 10000:
        raise ValueError("This teaching implementation accepts at most 10,000 cases")
    return pairs


def report(pairs):
    n = len(pairs)
    baseline = sum(pair[0] for pair in pairs)
    hardened = sum(pair[1] for pair in pairs)
    improved = sum(pair == (1, 0) for pair in pairs)
    regressed = sum(pair == (0, 1) for pair in pairs)
    return {
        "interpretation": "Conditional inference; independent sampled cases required",
        "independent_cases": n,
        "baseline_successes": baseline,
        "hardened_successes": hardened,
        "baseline_rate": baseline / n,
        "hardened_rate": hardened / n,
        "baseline_wilson_95": wilson(baseline, n),
        "hardened_wilson_95": wilson(hardened, n),
        "paired_reduction": (baseline - hardened) / n,
        "improved_cases": improved,
        "regressed_cases": regressed,
        "mcnemar_exact_two_sided_p": mcnemar_exact(improved, regressed),
        "paired_percentile_bootstrap_95": paired_bootstrap(pairs),
        "bootstrap_repeats": 10000,
        "bootstrap_seed": 20261004,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv", type=Path)
    source.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    try:
        # Constructed teaching counts; these are NOT experimental findings.
        pairs = ([(1, 1)] * 2 + [(1, 0)] * 28 + [(0, 0)] * 70
                 if args.demo else read_pairs(args.csv))
        print(json.dumps(report(pairs), indent=2, allow_nan=False))
    except (OSError, ValueError, csv.Error) as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
