#!/usr/bin/env python3
"""
Notion API接続テストスクリプト
"""

from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

def test_environment_variables():
    """環境変数のテスト"""
    print("🔍 環境変数のチェック...")
    
    OPENAI_API_KEY = os.getenv("OPENAI_TOKEN")
    NOTION_API_KEY = os.getenv("NOTION_TOKEN")
    INPUT_DB_ID = os.getenv("NOTION_DB_INPUT")
    OUTPUT_DB_ID = os.getenv("NOTION_DB_OUTPUT")
    
    results = {
        "OPENAI_TOKEN": "✅ 設定済み" if OPENAI_API_KEY else "❌ 未設定",
        "NOTION_TOKEN": "✅ 設定済み" if NOTION_API_KEY else "❌ 未設定",
        "NOTION_DB_INPUT": "✅ 設定済み" if INPUT_DB_ID else "❌ 未設定",
        "NOTION_DB_OUTPUT": "✅ 設定済み" if OUTPUT_DB_ID else "❌ 未設定"
    }
    
    for key, status in results.items():
        print(f"  {key}: {status}")
    
    return NOTION_API_KEY, results

def test_notion_api_auth(notion_api_key):
    """Notion APIの認証テスト"""
    print("\n🔑 Notion API認証テスト...")
    
    if not notion_api_key:
        print("❌ NOTION_TOKENが設定されていません")
        return False
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # Notion APIのユーザー情報を取得してテスト
        response = requests.get("https://api.notion.com/v1/users/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 認証成功！ユーザー: {user_data.get('name', 'Unknown')}")
            return True
        elif response.status_code == 401:
            print("❌ 認証失敗：APIキーが無効です")
            print(f"詳細: {response.text}")
            return False
        else:
            print(f"❌ 認証エラー (ステータス: {response.status_code})")
            print(f"詳細: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False

def test_database_access(notion_api_key, db_id, db_name):
    """データベースアクセステスト"""
    print(f"\n📊 データベースアクセステスト ({db_name}): {db_id}")
    
    if not notion_api_key:
        print("❌ APIキーが設定されていません")
        return False
    
    if not db_id or db_id == "1234567890":
        print("❌ データベースIDが設定されていないか、デフォルト値です")
        return False
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # データベース情報を取得
        response = requests.get(f"https://api.notion.com/v1/databases/{db_id}", headers=headers)
        
        if response.status_code == 200:
            db_data = response.json()
            title = db_data.get('title', [{}])[0].get('plain_text', 'Unknown')
            print(f"✅ データベースアクセス成功！タイトル: {title}")
            
            # プロパティの確認
            properties = db_data.get('properties', {})
            print(f"📋 プロパティ一覧:")
            for prop_name, prop_data in properties.items():
                prop_type = prop_data.get('type', 'unknown')
                print(f"  - {prop_name}: {prop_type}")
            
            return True
            
        elif response.status_code == 404:
            print("❌ データベースが見つかりません（IDが間違っているか、アクセス権限がありません）")
            print(f"詳細: {response.text}")
            return False
        elif response.status_code == 401:
            print("❌ 認証エラー：データベースへのアクセス権限がありません")
            print(f"詳細: {response.text}")
            return False
        else:
            print(f"❌ アクセスエラー (ステータス: {response.status_code})")
            print(f"詳細: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False

def test_database_query(notion_api_key, db_id, db_name):
    """データベースクエリテスト"""
    print(f"\n🔍 データベースクエリテスト ({db_name})")
    
    if not notion_api_key or not db_id:
        print("❌ APIキーまたはデータベースIDが設定されていません")
        return False
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # 最大5件のページを取得
        query_body = {"page_size": 5}
        response = requests.post(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            headers=headers,
            json=query_body
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✅ クエリ成功！取得したページ数: {len(results)}")
            
            for i, page in enumerate(results[:3], 1):  # 最初の3件だけ表示
                properties = page.get('properties', {})
                title_prop = properties.get('Title', {}) or properties.get('Name', {})
                title_array = title_prop.get('title', [])
                title = title_array[0].get('plain_text', 'タイトルなし') if title_array else 'タイトルなし'
                created_time = page.get('created_time', 'Unknown')
                print(f"  {i}. {title} (作成日: {created_time})")
            
            return True
        else:
            print(f"❌ クエリエラー (ステータス: {response.status_code})")
            print(f"詳細: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ クエリエラー: {e}")
        return False

def main():
    print("🤖 Notion API接続テスト")
    print("=" * 50)
    
    # 環境変数テスト
    notion_api_key, env_results = test_environment_variables()
    
    # APIキーが設定されていない場合は終了
    if not notion_api_key:
        print("\n❌ NOTION_TOKENが設定されていないため、テストを継続できません")
        return
    
    # API認証テスト
    if not test_notion_api_auth(notion_api_key):
        print("\n❌ API認証に失敗したため、テストを継続できません")
        return
    
    # データベースID辞書（main.pyと同じIDに更新）
    Input_Database_Id_dict = {
        "DQC": "1e656d7a44ed80849205ddfa38bd29f2",
        "ML": "1e656d7a44ed80849205ddfa38bd29f2",
        "NetExp": "1e656d7a44ed80849205ddfa38bd29f2",
        "NetTheory": "1e656d7a44ed80849205ddfa38bd29f2",
    }
    
    # 各データベースのテスト
    print("\n" + "="*50)
    for team_name, db_id in Input_Database_Id_dict.items():
        success = test_database_access(notion_api_key, db_id, team_name)
        if success:
            test_database_query(notion_api_key, db_id, team_name)
        print("-" * 30)
    
    print("\n🏁 テスト完了")

if __name__ == "__main__":
    main() 