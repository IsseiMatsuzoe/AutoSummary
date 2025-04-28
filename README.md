# AutoSummary - Notion進捗レポート自動要約システム

## 概要
AutoSummaryは、Notionデータベースに保存された研究室の週次進捗レポートを自動的に要約し、新しいページとして保存するシステムです。OpenAI GPT-4を活用して、研究者向けの簡潔で有用な要約を生成します。

## 主な機能
- Notionデータベースからの進捗レポート取得（過去7日分）
  - Notion APIを使用して指定されたデータベースから最新の投稿を取得
  - 各ページの内容をテキスト形式に変換
- GPT-4による研究内容の要約生成
  - カスタマイズ可能なプロンプトテンプレートを使用
  - 研究内容を理解しやすい形式でマークダウン形式に要約
- 要約結果のNotion APIブロック形式への変換
  - マークダウン形式の要約をNotionブロックJSONに変換
  - Notionページの構造に最適化
- 新規ページとしての自動保存
  - 生成された要約を新しいNotionページとして保存
  - タイトルに日付を自動付与

## 技術スタック
- Python 3.12
- OpenAI API (GPT-4)
  - テキスト要約生成
  - Notionブロック形式への変換
- Notion API
  - データベース操作
  - ページ作成と更新
- その他のライブラリ
  - openai: OpenAI API操作
  - pandas: データ処理
  - requests: API通信
  - python-dotenv: 環境変数管理
  - datetime: 日付処理
  - json: JSONデータ処理
  - os: 環境変数・ファイル操作

---

# AutoSummary - Notion Progress Report Auto-Summarization System

## Overview
AutoSummary is a system that automatically summarizes weekly research progress reports stored in a Notion database and saves them as new pages. It utilizes OpenAI GPT-4 to generate concise and useful summaries for researchers.

## Key Features
- Retrieval of progress reports from Notion database (last 7 days)
  - Fetches recent posts from specified database using Notion API
  - Converts page contents to text format
- Research content summarization using GPT-4
  - Uses customizable prompt templates
  - Summarizes research content in markdown format for better understanding
- Conversion of summaries to Notion API block format
  - Converts markdown summaries to Notion block JSON
  - Optimized for Notion page structure
- Automatic saving as new pages
  - Saves generated summaries as new Notion pages
  - Automatically adds date to titles

## Tech Stack
- Python 3.12
- OpenAI API (GPT-4)
  - Text summarization generation
  - Notion block format conversion
- Notion API
  - Database operations
  - Page creation and updates
- Additional Libraries
  - openai: OpenAI API operations
  - pandas: Data processing
  - requests: API communication
  - python-dotenv: Environment variable management
  - datetime: Date handling
  - json: JSON data processing
  - os: Environment variables and file operations