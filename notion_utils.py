# 標準ライブラリのインポート
import os

# サードパーティライブラリのインポート
import pandas as pd
import requests


def Get_Database_Items_Id_test(Notion_API_Key, Database_Id, X_Days_Ago=None):


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
        response.raise_for_status()  # エラーチェック
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
                
                page_info = {
                    'title': result.get('properties').get('タイトル').get('title')[0].get('plain_text'),
                    'page_id': result.get('id'),
                    'created_time': result.get('created_time')
                }
                pages.append(page_info)

    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"予期せぬエラー: {e}")
        return pd.DataFrame()

    # DataFrameを作成
    df = pd.DataFrame(pages)

    # 日付でフィルタリング
    if X_Days_Ago is not None:
        current_date = pd.Timestamp.now(tz='UTC')
        x_days_ago = current_date - pd.Timedelta(days=X_Days_Ago)
        df = df[pd.to_datetime(df['created_time']).between(x_days_ago, current_date)]

    return df