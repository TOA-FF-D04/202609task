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

Gemini の要約も公開したい場合は、リポジトリの `Settings` > `Secrets and variables` > `Actions` に `GEMINI_API_KEY` という名前で API キーを登録します。グラフだけなら Secret は不要です。

## 日経平均ボット

Yahoo Finance から日経平均（`^N225`）の過去1年分を取得し、`output/nikkei225.png` にグラフを保存します。

```powershell
uv run python nikkei_bot.py
```

`GEMINI_API_KEY` を設定している場合は、取得した値動きの要約も表示します。未設定でも、データ取得とグラフ作成は実行できます。データは市場休場日には更新されません。

## Web ダッシュボード

1年・1か月は日足、1日は前日分も含む5分足の期間切り替え、範囲スライダー、マウスオーバーによる終値表示に対応しています。

```powershell
uv run python nikkei_dashboard.py
Start-Process .\output\nikkei_dashboard.html
```

マウスをグラフ上に移動すると、その日の終値がカーソル付近に表示されます。