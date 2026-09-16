# SimpleAI

Gemini API を使って会話履歴を考慮した返答を生成できる、学習用の日本語チャットボットです。

## できること

- あいさつに返事する
- 名前を覚える
- 現在時刻を答える
- 入力に近い話題を推測して返事する
- Gemini API で複雑な会話を続ける
- 毎日の日経平均を取得してグラフ化する
- 日経平均の値動きを Gemini に要約させる
- 翌営業日の値動きを学習用モデルで予測する
- 期間切り替えとマウスオーバーに対応した Web グラフを表示する

## 実行方法

Python 3.10 以降と `uv` を用意したあと、PowerShell で次を実行します。

```powershell
uv sync
```

Gemini API を使う場合は、Google AI Studio で API キーを作成し、環境変数に設定します。キーはコードや Git に書き込まないでください。

```powershell
$env:GEMINI_API_KEY = "あなたのAPIキー"
```

```powershell
uv run python chatbot.py
```

終了するには `終了` と入力します。名前を覚えさせるには、たとえば `私の名前はさくら` と入力します。

## テスト

```powershell
uv run python -m unittest -v
```

`GEMINI_API_KEY` が未設定の場合は、API を呼ばずに従来のローカル版で動きます。API キーを設定すると、Gemini API を使う高性能版へ切り替わります。

API キーは [Google AI Studio](https://aistudio.google.com/apikey) で作成できます。

## 自動更新と公開

GitHub Actions で平日の日本時間16:30ごろに日経平均データを取得し、GitHub Pages へ自動公開します。手動で実行する場合は、GitHub の `Actions` > `Update Nikkei dashboard` > `Run workflow` を選択します。

GitHub リポジトリの `Settings` > `Pages` で、公開元を `GitHub Actions` に設定してください。公開 URL は通常 `https://<GitHubユーザー名>.github.io/202609task/` です。

実績ページは `/202609task/`、予測専用ページは `/202609task/prediction.html` で参照できます。GitHub Actions が毎日、両方のページを更新します。

当日の値動きページは `/202609task/realtime.html` です。平日の東京市場時間帯に5分足を再取得し、GitHub Actions で更新します。秒単位のリアルタイム価格ではなく、データ提供元と Actions の遅延を含む準リアルタイム表示です。

スケジュール実行は GitHub の混雑状況により遅延することがあります。Actions の `Update Nikkei dashboard` 画面で、`schedule` と表示された実行が作成されているか確認できます。

ニュース影響分析ページは `/202609task/news-impact.html` です。Google ニュース RSS を約5分ごとに取得し、見出しから日経平均への上昇・下落・中立の影響方向を推測します。Gemini API キーがある場合は補助要約も表示します。

Gemini の要約も公開したい場合は、リポジトリの `Settings` > `Secrets and variables` > `Actions` に `GEMINI_API_KEY` という名前で API キーを登録します。グラフだけなら Secret は不要です。

## 日経平均ボット

Yahoo Finance から日経平均（`^N225`）の過去1年分を取得し、`output/nikkei225.png` にグラフを保存します。

```powershell
uv run python nikkei_bot.py
```

`GEMINI_API_KEY` を設定している場合は、取得した値動きの要約も表示します。未設定でも、データ取得とグラフ作成は実行できます。データは市場休場日には更新されません。

## Web ダッシュボード

1年・1か月は日足、1日は前日分も含む5分足の期間切り替えに対応しています。破線で1営業日先・5営業日先（約1週間）・20営業日先（約1か月）の予測推移を表示し、各線の右端に現時点からの予測を追加します。

```powershell
uv run python nikkei_dashboard.py
Start-Process .\output\nikkei_dashboard.html
```

マウスをグラフ上に移動すると、その日の終値がカーソル付近に表示されます。

予測だけを確認する場合:

```powershell
uv run python nikkei_prediction_dashboard.py
Start-Process .\output\prediction.html
```

## 翌営業日の予測モデル

過去5年の日足から、直近のリターン・移動平均・ボラティリティ・曜日を特徴量にして、翌営業日のリターンを予測します。時系列順に過去80%を学習、残り20%を検証に使います。

```powershell
uv run python nikkei_predictor.py
```

予測結果と検証指標は `output/nikkei_model_metrics.txt` に保存されます。このモデルは学習用のベースラインであり、投資助言や利益を保証するものではありません。