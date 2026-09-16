"""日経平均の翌営業日リターンを予測する学習用モデル。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from nikkei_bot import fetch_nikkei


FEATURE_COLUMNS = [
    "return_1d",
    "return_2d",
    "return_5d",
    "return_10d",
    "return_20d",
    "mean_5d",
    "mean_20d",
    "volatility_20d",
    "weekday",
]
DEFAULT_MODEL_PATH = Path("output/nikkei_model_metrics.txt")


@dataclass(frozen=True)
class PredictionResult:
    latest_date: pd.Timestamp
    latest_close: float
    predicted_return: float
    predicted_close: float
    validation_mae: float
    validation_directional_accuracy: float


def make_features(close: pd.Series, horizon: int = 1) -> pd.DataFrame:
    """終値から未来を参照しない予測特徴量を作る。"""
    if horizon < 1:
        raise ValueError("予測期間は1営業日以上にしてください。")
    frame = pd.DataFrame({"close": close.astype(float)})
    returns = frame["close"].pct_change()
    frame["return_1d"] = returns
    frame["return_2d"] = frame["close"].pct_change(2)
    frame["return_5d"] = frame["close"].pct_change(5)
    frame["return_10d"] = frame["close"].pct_change(10)
    frame["return_20d"] = frame["close"].pct_change(20)
    frame["mean_5d"] = returns.rolling(5).mean()
    frame["mean_20d"] = returns.rolling(20).mean()
    frame["volatility_20d"] = returns.rolling(20).std()
    frame["weekday"] = frame.index.dayofweek
    frame["target"] = frame["close"].pct_change(horizon).shift(-horizon)
    return frame.dropna()


def create_model() -> RandomForestRegressor:
    """予測に使うモデルを作る。"""
    return RandomForestRegressor(
        n_estimators=300,
        max_depth=6,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1,
    )


def validation_predictions(close: pd.Series, horizon: int = 1) -> pd.Series:
    """検証期間について、各時点の指定営業日先予測価格を返す。"""
    features = make_features(close, horizon)
    if len(features) < 80:
        raise ValueError("予測には少なくとも80営業日分のデータが必要です。")

    split = int(len(features) * 0.8)
    train = features.iloc[:split]
    validation = features.iloc[split:]
    model = create_model()
    model.fit(train[FEATURE_COLUMNS], train["target"])
    predicted_returns = model.predict(validation[FEATURE_COLUMNS])
    predicted_prices = validation["close"].to_numpy() * (1 + predicted_returns)
    feature_positions = close.index.get_indexer(validation.index)
    prediction_dates = close.index[feature_positions + horizon]
    return pd.Series(predicted_prices, index=prediction_dates, name="predicted_close")


def train_and_predict(
    close: pd.Series,
    model_path: Path = DEFAULT_MODEL_PATH,
    horizon: int = 1,
) -> PredictionResult:
    """時系列順に検証し、全データで学習して指定営業日先を予測する。"""
    features = make_features(close, horizon)
    if len(features) < 80:
        raise ValueError("予測には少なくとも80営業日分のデータが必要です。")

    split = int(len(features) * 0.8)
    train = features.iloc[:split]
    validation = features.iloc[split:]
    model = create_model()
    model.fit(train[FEATURE_COLUMNS], train["target"])
    validation_prediction = model.predict(validation[FEATURE_COLUMNS])
    validation_actual = validation["target"].to_numpy()
    mae = mean_absolute_error(validation_actual, validation_prediction)
    direction = (validation_prediction >= 0) == (validation_actual >= 0)

    model.fit(features[FEATURE_COLUMNS], features["target"])
    latest_features = features.iloc[[-1]][FEATURE_COLUMNS]
    predicted_return = float(model.predict(latest_features)[0])
    latest_close = float(close.iloc[-1])
    result = PredictionResult(
        latest_date=pd.Timestamp(close.index[-1]),
        latest_close=latest_close,
        predicted_return=predicted_return,
        predicted_close=latest_close * (1 + predicted_return),
        validation_mae=float(mae),
        validation_directional_accuracy=float(direction.mean()),
    )
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(
        "翌営業日の日経平均予測モデル\n"
        f"基準日: {result.latest_date:%Y-%m-%d}\n"
        f"最新終値: {result.latest_close:,.2f}円\n"
        f"予測終値: {result.predicted_close:,.2f}円\n"
        f"予測リターン: {result.predicted_return:+.2%}\n"
        f"検証MAE: {result.validation_mae:.4%}\n"
        f"方向一致率: {result.validation_directional_accuracy:.2%}\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    print("日経平均の予測モデルを学習しています...")
    close = fetch_nikkei(period="5y", interval="1d")
    result = train_and_predict(close)
    print(f"基準日: {result.latest_date:%Y-%m-%d}")
    print(f"最新終値: {result.latest_close:,.2f}円")
    print(f"翌営業日予測: {result.predicted_close:,.2f}円 ({result.predicted_return:+.2%})")
    print(f"検証方向一致率: {result.validation_directional_accuracy:.2%}")
    print(f"指標を保存しました: {DEFAULT_MODEL_PATH}")
    print("注意: これは学習用の統計モデルであり、投資助言や利益を保証するものではありません。")


if __name__ == "__main__":
    main()