# AutoSummary

量子情報技術研究グループ向けの進捗要約ツールです。Notion データベースからチームメンバーの Weekly Report を取得し、OpenAI API を使用して要約し、別の Notion データベースに投稿します。

## 機能

- **進捗データ表示**: 指定されたチームの進捗データを表示
- **AI 要約**: チームの進捗を自動要約して Notion に投稿
- **チーム対応**: DQC、ML、NetExp、NetTheory の各チームに対応
- **対話モード**: CLI で対話的に操作可能
- **コマンドライン**: 引数指定でバッチ実行可能

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の環境変数を設定してください：

```
OPENAI_TOKEN=your_openai_api_key
NOTION_TOKEN=your_notion_integration_token
NOTION_DB_INPUT=input_database_id
NOTION_DB_OUTPUT=output_database_id
```

### 3. Notion データベース ID の設定

`main.py`の`Input_Databse_Id_dict`を実際のデータベース ID に更新してください：

```python
Input_Databse_Id_dict = {
    "DQC": "actual_database_id_1",
    "ML": "actual_database_id_2",
    "NetExp": "actual_database_id_3",
    "NetTheory": "actual_database_id_4",
}
```

## 使用方法

### 対話モード（推奨）

```bash
python main.py --interactive
```

または

```bash
python main.py -i
```

対話モードでは以下を順次選択できます：

1. 対象チーム（DQC, ML, NetExp, NetTheory）
2. 対象期間（何日前からのデータか）
3. 実行操作（データ表示 or 要約投稿）
4. カテゴリ（要約投稿の場合：ProgressReport, Note, Paper）

### コマンドライン引数

#### 進捗データを表示

```bash
python main.py --team DQC --days 7 --action show
```

#### 要約して Notion に投稿

```bash
python main.py --team ML --days 14 --action summary --category ProgressReport
```

### コマンドライン引数一覧

- `--team`: 対象チーム（DQC, ML, NetExp, NetTheory）**必須**
- `--days`: 何日前からのデータを対象にするか（デフォルト: 7）
- `--action`: 実行する操作
  - `show`: 進捗データを表示
  - `summary`: 要約して Notion に投稿（デフォルト）
- `--category`: 投稿カテゴリ（ProgressReport, Note, Paper）（デフォルト: ProgressReport）
- `--interactive`, `-i`: 対話モードで実行

### ヘルプ表示

```bash
python main.py --help
```

## 使用例

### 例 1: DQC チームの過去 7 日間のデータを表示

```bash
python main.py --team DQC --action show
```

### 例 2: ML チームの過去 14 日間の進捗を要約して Notion に投稿

```bash
python main.py --team ML --days 14 --action summary --category ProgressReport
```

### 例 3: 対話モードで全ての選択を行う

```bash
python main.py -i
```

## ファイル構成

- `main.py`: メインエントリーポイント（CLI 機能）
- `notion_utils.py`: Notion API 操作
- `openai_chat.py`: OpenAI API 操作（要約・変換）
- `prompt/`: AI 用プロンプトファイル
  - `first_prompt.txt`: 要約用プロンプト
  - `second_prompt.txt`: Notion API 形式変換用プロンプト

## エラー対処

### 環境変数エラー

```
❌ エラー: 環境変数OPENAI_TOKENまたはNOTION_TOKENが設定されていません。
```

→ `.env`ファイルで環境変数を正しく設定してください。

### データベース ID エラー

```
❌ {Team}チームの過去{X}日間にデータが見つかりませんでした。
```

→ データベース ID が正しく設定されているか、対象期間にデータが存在するかを確認してください。

## 注意事項

- OpenAI API の使用料金が発生します
- Notion API の制限に注意してください
- テスト用の`.ipynb`ファイルは本システムには不要です
