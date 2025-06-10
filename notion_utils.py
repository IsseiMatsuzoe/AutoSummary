# 標準ライブラリのインポート
import os

# サードパーティライブラリのインポート
import pandas as pd
import requests
import datetime
import json


def get_database_items_id(Notion_API_Key, Database_Id, X_Days_Ago=None, Team=None, Category=None):
    # ヘッダーを設定
    headers = {
        "Authorization": f"Bearer {Notion_API_Key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # フィルタークエリを構築
    filter_conditions = []
    
    # 日付フィルター
    if X_Days_Ago is not None:
        x_days_ago = (datetime.datetime.now() - datetime.timedelta(days=X_Days_Ago)).isoformat()
        filter_conditions.append({
            "property": "Created time",
            "created_time": {
                "on_or_after": x_days_ago
            }
        })
    
    # Teamフィルター
    if Team is not None:
        filter_conditions.append({
            "property": "Team",
            "select": {
                "equals": Team
            }
        })
    
    # Categoryフィルター
    if Category is not None:
        filter_conditions.append({
            "property": "Category",
            "select": {
                "equals": Category
            }
        })
    
    # クエリボディを構築
    query_body = {}
    if filter_conditions:
        if len(filter_conditions) == 1:
            query_body["filter"] = filter_conditions[0]
        else:
            query_body["filter"] = {
                "and": filter_conditions
            }
    
    # デバッグ用：フィルタークエリを表示
    if filter_conditions:
        print(f"🔍 フィルター適用中: {len(filter_conditions)}個の条件")
        if Team:
            print(f"  - Team: {Team}")
        if Category:
            print(f"  - Category: {Category}")
        if X_Days_Ago:
            print(f"  - 過去{X_Days_Ago}日間")

    try:
        # データベースをクエリするリクエスト
        response = requests.post(
            f"https://api.notion.com/v1/databases/{Database_Id}/query",
            headers=headers,
            json=query_body
        )
        
        # レスポンスを取得
        if response.status_code == 401:
            print(f"認証エラー: Notion APIキーが無効または権限が不足しています。APIキーを確認してください。")
            return pd.DataFrame()
        elif response.status_code == 400:
            print(f"リクエストエラー: データベースID '{Database_Id}' が無効です。データベースIDを確認してください。")
            return pd.DataFrame()
        elif response.status_code == 404:
            print(f"リソースが見つかりません: データベースID '{Database_Id}' が存在しないか、アクセス権限がありません。")
            return pd.DataFrame()
        
        response.raise_for_status()  # その他のエラーチェック
        data = response.json()
        
        # 各ページの情報を辞書に追加
        results = data.get('results', [])  
        if not results:
            print("データベースにページが存在しません")
            return pd.DataFrame()
        else:
            # 複数のページの情報を格納するためにリストを使用
            pages = []
            
            for result in results:
                try:
                    # プロパティの存在チェック
                    properties = result.get('properties', {})
                    title_property = properties.get('Title', {})
                    title_array = title_property.get('title', [])
                    
                    # タイトルが存在するかチェック
                    if not title_array:
                        print(f"警告: ページID {result.get('id')} にタイトルが設定されていません")
                        title_text = "タイトルなし"
                    else:
                        title_text = title_array[0].get('plain_text', 'タイトルなし')
                    
                    # 作成者情報を取得
                    created_by_property = properties.get('Created by', {})
                    created_by_info = created_by_property.get('created_by', {})
                    created_by_name = created_by_info.get('name', '不明')
                    
                    page_info = {
                        'title': title_text,
                        'page_id': result.get('id'),
                        'created_time': result.get('created_time'),
                        'created_by': created_by_name
                    }
                    pages.append(page_info)
                except Exception as e:
                    print(f"警告: ページID {result.get('id')} の処理中にエラーが発生しました: {e}")
                    continue

    except requests.exceptions.RequestException as e:
        print(f"データベースID取得：APIリクエストエラー: {e}")
        print(f"エラーの詳細: {response.text if 'response' in locals() else 'レスポンスなし'}")
        return pd.DataFrame()
    except Exception as e:
        print(f"予期せぬエラー: {e}")
        return pd.DataFrame()

    # DataFrameを作成
    df = pd.DataFrame(pages)

    # APIクエリで既にフィルタリングされているため、追加の日付フィルタリングは不要
    return df

def fetch_blocks(NOTION_API_KEY, page_id: str, page_size: int = 100):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    params = {"page_size": page_size}

    blocks = []
    while True:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        blocks.extend(data["results"])
        if not data.get("has_more"):
            break
        params["start_cursor"] = data["next_cursor"]
    return blocks


def extract_plain_text(block):
    t = ""
    # 多くのブロックは block[block["type"]]["rich_text"] を持つ
    rich = block.get(block["type"], {}).get("rich_text", [])
    for part in rich:
        t += part.get("plain_text", "")
    return t

def page_to_text(NOTION_API_KEY, page_id):
    blocks = fetch_blocks(NOTION_API_KEY, page_id)
    lines = []
    for blk in blocks:
        text = extract_plain_text(blk).strip()
        if text:
            lines.append(text)
        
    return "\n".join(lines)

def page_to_text_with_metadata(NOTION_API_KEY, page_id, title, created_by, created_time):
    """ページのテキストに作成者などのメタデータを含めて取得"""
    blocks = fetch_blocks(NOTION_API_KEY, page_id)
    lines = []
    
    # メタデータをテキストの先頭に追加
    lines.append(f"📝 ページタイトル: {title}")
    lines.append(f"👤 作成者: {created_by}")
    lines.append(f"📅 作成日時: {created_time}")
    lines.append("---")
    
    # ページ内容を追加
    for blk in blocks:
        text = extract_plain_text(blk).strip()
        if text:
            lines.append(text)
        
    return "\n".join(lines)

def get_database_text(NOTION_API_KEY: str, DB_ID: str, X_DAYS_AGO: int = 7, Team: str = None, Category: str = None):
    page_data = get_database_items_id(NOTION_API_KEY, DB_ID, X_DAYS_AGO, Team, Category)
    
    if page_data.empty:
        return "<|DOCUMENT|>\n(データが見つかりませんでした)\n<|DOCUMENT|>"

    text_list = []
    for _, row in page_data.iterrows():
        page_text = page_to_text_with_metadata(
            NOTION_API_KEY, 
            row['page_id'], 
            row['title'], 
            row['created_by'], 
            row['created_time']
        )
        text_list.append(page_text)
    
    # 各テキストの間に区切り文字を挿入して結合
    combined_text = "<|DOCUMENT|>\n" + "\n<|DOCUMENT|>\n".join(text_list) + "\n<|DOCUMENT|>"
    
    # デバッグ用：最初の500文字を表示
    print("🤖 ChatGPTに送信されるテキストの先頭部分:")
    print("-" * 50)
    print(combined_text[:500] + "..." if len(combined_text) > 500 else combined_text)
    print("-" * 50)
    
    return combined_text

def post_page(notion_api_key, database_id, blocks_json, Team:str=None, Category:str=None):
    """
    Team: "DQC", "ML", "NetExp", "NetTheory"
    Category: "ProgressReport", "Note", "Paper"
    """

    blocks_json = blocks_json.replace('```json\n', '').replace('\n```', '')

    url = "https://api.notion.com/v1/pages"
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": f"AI-Summary {Team} {datetime.datetime.today().strftime('%Y/%m/%d')}"
                        }
                    }
                ]
            },
            "From": {
                "select": {
                    "name": "OpenAI"
                }
            },
            "Category": {
                "select": {
                    "name": Category
                }
            },
            "Team": {
                "select": {
                    "name": Team
                }
            },
        },
        "children": json.loads(blocks_json)
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("ページの作成に成功しました")
        return response.json()
    else:
        print(f"エラーが発生しました: {response.status_code}")
        print(response.text)
        return None
