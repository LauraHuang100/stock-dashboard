import math
import unittest

from utils.indicators import compute_bollinger_summary, compute_indicator_summary, compute_macd_summary, compute_volume_trend_summary


class IndicatorCalculationTests(unittest.TestCase):
    def test_macd_summary_is_numeric_and_histogram_matches(self):
        close = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125]
        summary = compute_macd_summary(close)

        for field in ("macd", "signal", "histogram"):
            self.assertIsNotNone(summary[field])
            self.assertTrue(math.isfinite(summary[field]))

        self.assertAlmostEqual(summary["histogram"], summary["macd"] - summary["signal"], places=4)

    def test_bollinger_summary_keeps_upper_above_middle_above_lower(self):
        close = [100 + i * 0.5 for i in range(40)]
        summary = compute_bollinger_summary(close)

        self.assertIsNotNone(summary["upper"])
        self.assertIsNotNone(summary["middle"])
        self.assertIsNotNone(summary["lower"])

        self.assertGreaterEqual(summary["upper"], summary["middle"])
        self.assertGreaterEqual(summary["middle"], summary["lower"])

    def test_volume_trend_summary_labels_ratio_correctly(self):
        volume = [1000] * 20
        volume[-1] = 1400
        summary = compute_volume_trend_summary(volume)

        self.assertEqual(summary["label"], "Expanding")
        self.assertIsNotNone(summary["volume_ratio"])
        self.assertGreater(summary["volume_ratio"], 1.2)

    def test_missing_volume_is_safe(self):
        summary = compute_volume_trend_summary([None] * 25)

        self.assertEqual(summary["label"], "N/A")
        self.assertIsNone(summary["volume_ratio"])

    def test_indicator_summary_handles_small_datasets(self):
        summary = compute_indicator_summary([100, 101, 102], [1000, 1100, 1050])

        self.assertEqual(summary["macd"]["trend"], "N/A")
        self.assertIsNone(summary["bollinger"]["upper"])
        self.assertEqual(summary["volume"]["label"], "N/A")


if __name__ == "__main__":
    unittest.main()
