"""Regression checks for the book's paired-analysis teaching code."""
import contextlib
import io
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import decision_stats as stats


class StatisticalCalculationTests(unittest.TestCase):
    def test_wilson_extreme_outcomes_preserve_uncertainty(self):
        lower, upper = stats.wilson(0, 10)
        self.assertAlmostEqual(lower, 0.0)
        self.assertGreater(upper, 0.0)
        self.assertLess(upper, 1.0)
        all_lower, all_upper = stats.wilson(10, 10)
        self.assertAlmostEqual(all_lower, 1.0 - upper)
        self.assertAlmostEqual(all_upper, 1.0)

    def test_wilson_matches_reference_interval(self):
        # Independently tabulated 95% Wilson interval for 50 successes in 100.
        lower, upper = stats.wilson(50, 100)
        self.assertAlmostEqual(lower, 0.4038315303659956, places=12)
        self.assertAlmostEqual(upper, 0.5961684696340044, places=12)

    def test_wilson_rejects_impossible_counts(self):
        for successes, cases in ((0, 0), (0, -1), (-1, 10), (11, 10)):
            with self.subTest(successes=successes, cases=cases):
                with self.assertRaises(ValueError):
                    stats.wilson(successes, cases)

    def test_exact_mcnemar_discordance_and_direction(self):
        self.assertEqual(stats.mcnemar_exact(0, 0), 1.0)
        self.assertEqual(stats.mcnemar_exact(1, 1), 1.0)
        self.assertEqual(stats.mcnemar_exact(8, 2), 0.109375)
        self.assertEqual(stats.mcnemar_exact(2, 8), 0.109375)
        self.assertEqual(stats.mcnemar_exact(28, 0), 2 / (2 ** 28))

    def test_exact_mcnemar_large_balanced_counts_remain_finite(self):
        result = stats.mcnemar_exact(1000, 1000)
        self.assertTrue(math.isfinite(result))
        self.assertEqual(result, 1.0)

    def test_quantile_interpolates_and_retains_endpoints(self):
        values = [0, 10, 20, 30]
        self.assertEqual(stats.quantile(values, 0), 0)
        self.assertEqual(stats.quantile(values, 1), 30)
        self.assertEqual(stats.quantile(values, 0.25), 7.5)
        self.assertEqual(stats.quantile([4], 0.975), 4)

    def test_bootstrap_handles_degenerate_and_negative_differences(self):
        for pair, expected in (((1, 0), 1), ((0, 1), -1), ((0, 0), 0)):
            with self.subTest(pair=pair):
                self.assertEqual(
                    stats.paired_bootstrap([pair], repeats=200),
                    [expected, expected],
                )

    def test_bootstrap_preserves_pairs_and_is_reproducible(self):
        # Equal marginals alone do not guarantee equal paired observations.
        concordant = [(1, 1), (0, 0)] * 5
        self.assertEqual(stats.paired_bootstrap(concordant, repeats=200), [0, 0])
        mixed = [(1, 0), (0, 1), (1, 1), (0, 0)] * 3
        original = list(mixed)
        first = stats.paired_bootstrap(mixed, repeats=500, seed=17)
        self.assertEqual(first, stats.paired_bootstrap(mixed, repeats=500, seed=17))
        self.assertLess(first[0], 0)
        self.assertGreater(first[1], 0)
        self.assertEqual(mixed, original)

    def test_report_reconciles_paired_counts(self):
        result = stats.report([(1, 1), (1, 0), (1, 0), (0, 1), (0, 0)])
        self.assertEqual(result["independent_cases"], 5)
        self.assertEqual(result["baseline_successes"], 3)
        self.assertEqual(result["hardened_successes"], 2)
        self.assertEqual(result["improved_cases"], 2)
        self.assertEqual(result["regressed_cases"], 1)
        self.assertAlmostEqual(result["paired_reduction"], 0.2)
        self.assertAlmostEqual(
            result["baseline_rate"] - result["hardened_rate"],
            result["paired_reduction"],
        )
        self.assertIn("independent sampled cases required", result["interpretation"])


class StatisticalInputTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="purple-statistics-test-")
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "pairs.csv"

    def read(self, content):
        self.path.write_text(content, encoding="utf-8")
        return stats.read_pairs(self.path)

    def test_valid_csv_accepts_whitespace_and_quoted_identifiers(self):
        content = (
            "case_id,baseline_success,hardened_success\r\n"
            '"case, one", 1 ,0\r\n'
            "case-two,0, 1 \r\n"
        )
        self.assertEqual(self.read(content), [(1, 0), (0, 1)])

    def test_csv_requires_exact_ordered_header(self):
        for header in (
            "baseline_success,case_id,hardened_success",
            "case_id,baseline_success,hardened_success,extra",
            "case_id,baseline_success",
            "case_id,baseline_success, hardened_success",
        ):
            with self.subTest(header=header):
                with self.assertRaisesRegex(ValueError, "CSV header must be"):
                    self.read(header + "\na,1,0\n")

    def test_csv_rejects_blank_or_duplicate_normalized_ids(self):
        for rows in (" ,1,0\n", "a,1,0\n a ,0,1\n"):
            with self.subTest(rows=rows):
                with self.assertRaisesRegex(ValueError, "Missing or duplicate"):
                    self.read(",".join(stats.FIELDS) + "\n" + rows)

    def test_csv_rejects_nonbinary_and_malformed_rows(self):
        for row, expected in (
            ("a,2,0", "Outcomes must"),
            ("a,1.0,0", "Outcomes must"),
            ("a,true,0", "Outcomes must"),
            ("a,,0", "Outcomes must"),
            ("a,1", "Malformed CSV"),
            ("a,1,0,extra", "Malformed CSV"),
        ):
            with self.subTest(row=row):
                with self.assertRaisesRegex(ValueError, expected):
                    self.read(",".join(stats.FIELDS) + "\n" + row + "\n")

    def test_csv_rejects_empty_samples_and_caps_independent_cases(self):
        header = ",".join(stats.FIELDS) + "\n"
        with self.assertRaisesRegex(ValueError, "no cases"):
            self.read(header)
        rows = "".join(f"case-{index},1,0\n" for index in range(10000))
        self.assertEqual(len(self.read(header + rows)), 10000)
        with self.assertRaisesRegex(ValueError, "at most 10,000"):
            self.read(header + rows + "case-10000,1,0\n")

    def test_cli_input_error_has_failure_exit_and_no_result(self):
        self.path.write_text("wrong,header\n", encoding="utf-8")
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("sys.argv", ["decision_stats.py", "--csv", str(self.path)]):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = stats.main()
        self.assertEqual(status, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("Input error:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
