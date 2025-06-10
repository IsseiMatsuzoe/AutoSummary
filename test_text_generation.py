#!/usr/bin/env python3
"""
作成者情報を含むテキスト生成のテスト
"""

from dotenv import load_dotenv
import os
from notion_utils import get_database_text

load_dotenv()

def test_text_with_author():
    """作成者情報を含むテキスト生成をテスト"""
    NOTION_API_KEY = os.getenv("NOTION_TOKEN")
    
    if not NOTION_API_KEY:
        print("❌ NOTION_TOKENが設定されていません")
        return
    
    # テスト用の設定
    DB_ID = "1e656d7a44ed80849205ddfa38bd29f2"
    Team = "DQC"
    Category = "ProgressReport"
    X_DAYS_AGO = 7
    
    print(f"🔍 {Team}チームの{Category}カテゴリの過去{X_DAYS_AGO}日間のテキスト生成をテスト中...")
    
    # 作成者情報を含むテキストを生成
    combined_text = get_database_text(
        NOTION_API_KEY=NOTION_API_KEY,
        DB_ID=DB_ID,
        X_DAYS_AGO=X_DAYS_AGO,
        Team=Team,
        Category=Category
    )
    
    print(f"\n📝 生成されたテキストの文字数: {len(combined_text)}")
    print("✅ テスト完了！")
    
    return combined_text

if __name__ == "__main__":
    test_text_with_author() 