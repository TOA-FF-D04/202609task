import tempfile
import unittest
from pathlib import Path

import pandas as pd

from nikkei_predictor import make_features, train_and_predict, validation_predictions


class NikkeiPredictorTest(unittest.TestCase):
    def test_features_do_not_contain_missing_values(self) -> None:
        close = pd.Series(
            range(100, 230),
            index=pd.date_range("2025-01-01", periods=130, freq="B"),
            dtype=float,
        )
        features = make_features(close)

        self.assertFalse(features.isna().any().any())
        self.assertEqual(features.iloc[0]["return_1d"], close.iloc[20] / close.iloc[19] - 1)

    def test_train_and_predict_uses_time_order(self) -> None:
        close = pd.Series(
            [100 * (1.001**index) for index in range(150)],
            index=pd.date_range("2025-01-01", periods=150, freq="B"),
        )
        with tempfile.TemporaryDirectory() as directory:
            result = train_and_predict(close, Path(directory) / "metrics.txt")

        self.assertGreater(result.predicted_close, 0)
        self.assertGreaterEqual(result.validation_directional_accuracy, 0)
        self.assertLessEqual(result.validation_directional_accuracy, 1)

    def test_validation_predictions_are_next_business_day_prices(self) -> None:
        close = pd.Series(
            [100 * (1.001**index) for index in range(150)],
            index=pd.date_range("2025-01-01", periods=150, freq="B"),
        )

        predictions = validation_predictions(close)

        self.assertFalse(predictions.empty)
        self.assertTrue((predictions.index.dayofweek < 5).all())
        self.assertTrue((predictions > 0).all())

    def test_validation_predictions_support_multiple_horizons(self) -> None:
        close = pd.Series(
            [100 * (1.001**index) for index in range(180)],
            index=pd.date_range("2025-01-01", periods=180, freq="B"),
        )

        predictions = validation_predictions(close, horizon=20)

        self.assertFalse(predictions.empty)
        self.assertEqual(predictions.index[-1], close.index[-1])


if __name__ == "__main__":
    unittest.main()