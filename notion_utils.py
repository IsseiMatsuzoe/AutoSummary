# 標準ライブラリのインポート
import os

# サードパーティライブラリのインポート
import pandas as pd
import requests
import datetime
import json


def get_database_items_id(Notion_API_Key, Database_Id, X_Days_Ago=None):
    # ヘッダーを設定
    headers = {
        "Authorization": f"Bearer {Notion_API_Key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    try:
        # データベースをクエリするリクエスト
        response = requests.post(
            f"https://api.notion.com/v1/databases/{Database_Id}/query",
            headers=headers
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
                    
                    page_info = {
                        'title': title_text,
                        'page_id': result.get('id'),
                        'created_time': result.get('created_time')
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

    # 日付でフィルタリング
    if X_Days_Ago is not None and not df.empty:
        current_date = pd.Timestamp.now(tz='UTC')
        x_days_ago = current_date - pd.Timedelta(days=X_Days_Ago)
        df = df[pd.to_datetime(df['created_time']).between(x_days_ago, current_date)]

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

def get_database_text(NOTION_API_KEY: str, DB_ID: str, X_DAYS_AGO: int = 7):
    page_id_list = get_database_items_id(NOTION_API_KEY, DB_ID, X_DAYS_AGO)['page_id'].to_list()

    text_list = []
    for page_id in page_id_list:
        text_list.append(page_to_text(NOTION_API_KEY, page_id))
    
    # 各テキストの間に区切り文字を挿入して結合
    combined_text = "<|DOCUMENT|>\n" + "\n<|DOCUMENT|>\n".join(text_list) + "\n<|DOCUMENT|>"
    return combined_text

def post_page(notion_api_key, database_id, blocks_json):

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
                            "content": f"AI進捗要約 {datetime.datetime.today().strftime('%Y/%m/%d')}"
                        }
                    }
                ]
            },
            "From": {
                "select": {
                    "name": "openAI"
                }
            },
            "Category": {
                "select": {
                    "name": "ProgressReport"
                }
            },
            "Team": {
                "select": {
                    "name": "DQC"
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
