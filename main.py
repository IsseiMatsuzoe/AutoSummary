from dotenv import load_dotenv
import os
import argparse
import sys
from notion_utils import *
from openai_chat import *

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_TOKEN")
Notion_API_Key = os.getenv("NOTION_TOKEN")
Input_Database_Id = os.getenv("NOTION_DB_INPUT")
Output_Database_Id = os.getenv("NOTION_DB_OUTPUT")

client = OpenAI(api_key=OPENAI_API_KEY)

Input_Databse_Id_dict = {
    "DQC": "1e656d7a44ed80849205ddfa38bd29f2",
    "ML": "1e656d7a44ed80849205ddfa38bd29f2",
    "NetExp": "1e656d7a44ed80849205ddfa38bd29f2",
    "NetTheory": "1e656d7a44ed80849205ddfa38bd29f2",
}

def post_summary(Output_Database_Id:str, OpenAI_API_KEY:str, X_DAYS_AGO:int, Team:str, Category:str):
    """指定されたチームの進捗を要約してNotionに投稿"""
    print(f"🔍 {Team}チームの{Category}カテゴリの過去{X_DAYS_AGO}日間のデータを取得中...")
    
    generated_page_json = suumarize_text(
        OPENAI_API_KEY=OpenAI_API_KEY,
        text = get_database_text(
            NOTION_API_KEY = Notion_API_Key,
            DB_ID = Input_Databse_Id_dict[Team],
            X_DAYS_AGO = X_DAYS_AGO,
            Team = Team,
            Category = Category
        )
    )
    
    print(f"📝 {Team}チームの要約をNotionに投稿中...")
    post_page(Notion_API_Key, Output_Database_Id, generated_page_json, Team=Team, Category=Category)
    print("✅ 完了しました！")

def show_team_progress(Team: str, X_DAYS_AGO: int, Category: str = None):
    """指定されたチームの進捗データを表示（要約なし）"""
    if Category:
        print(f"🔍 {Team}チームの{Category}カテゴリの過去{X_DAYS_AGO}日間のデータを取得中...")
    else:
        print(f"🔍 {Team}チームの過去{X_DAYS_AGO}日間のデータを取得中...")
    
    # データベースからページIDを取得
    page_data = get_database_items_id(Notion_API_Key, Input_Databse_Id_dict[Team], X_DAYS_AGO, Team, Category)
    
    if page_data.empty:
        category_text = f"の{Category}カテゴリ" if Category else ""
        print(f"❌ {Team}チーム{category_text}の過去{X_DAYS_AGO}日間にデータが見つかりませんでした。")
        return
    
    category_text = f" ({Category}カテゴリ)" if Category else ""
    print(f"\n📊 {Team}チームの進捗データ{category_text} ({len(page_data)}件):")
    print("-" * 50)
    
    for _, row in page_data.iterrows():
        print(f"📄 タイトル: {row['title']}")
        print(f"👤 作成者: {row['created_by']}")
        print(f"📅 作成日時: {row['created_time']}")
        print(f"🔗 ページID: {row['page_id']}")
        print("-" * 30)

def interactive_mode():
    """対話形式でオプションを選択"""
    print("🤖 AutoSummary CLI")
    print("=" * 40)
    
    # チーム選択
    teams = list(Input_Databse_Id_dict.keys())
    print("📋 利用可能なチーム:")
    for i, team in enumerate(teams, 1):
        print(f"  {i}. {team}")
    
    while True:
        try:
            team_choice = int(input(f"\nチームを選択してください (1-{len(teams)}): ")) - 1
            if 0 <= team_choice < len(teams):
                selected_team = teams[team_choice]
                break
            else:
                print("❌ 無効な選択です。")
        except ValueError:
            print("❌ 数字を入力してください。")
    
    # 日数選択
    while True:
        try:
            days_ago = int(input("📅 何日前からのデータを対象にしますか？ (デフォルト: 7): ") or "7")
            if days_ago > 0:
                break
            else:
                print("❌ 1以上の数字を入力してください。")
        except ValueError:
            print("❌ 数字を入力してください。")
    
    # 操作選択
    print("\n🎯 実行する操作を選択してください:")
    print("  1. 進捗データを表示")
    print("  2. 要約してNotionに投稿")
    
    while True:
        try:
            action_choice = int(input("操作を選択してください (1-2): "))
            if action_choice in [1, 2]:
                break
            else:
                print("❌ 1または2を入力してください。")
        except ValueError:
            print("❌ 数字を入力してください。")
    
    # カテゴリ選択（両方の操作で共通）
    categories = ["ProgressReport", "Note", "Paper", "すべて"]
    print("\n📂 カテゴリを選択してください:")
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat}")
    
    while True:
        try:
            cat_choice = int(input(f"カテゴリを選択してください (1-{len(categories)}): ")) - 1
            if 0 <= cat_choice < len(categories):
                selected_category = categories[cat_choice] if cat_choice < 3 else None
                break
            else:
                print("❌ 無効な選択です。")
        except ValueError:
            print("❌ 数字を入力してください。")
    
    if action_choice == 1:
        show_team_progress(selected_team, days_ago, selected_category)
    else:
        if selected_category is None:
            print("❌ 要約投稿にはカテゴリの指定が必要です。")
            return
        post_summary(Output_Database_Id, OPENAI_API_KEY, days_ago, selected_team, selected_category)

def main():
    parser = argparse.ArgumentParser(description="AutoSummary - Notion進捗要約ツール")
    parser.add_argument("--team", choices=list(Input_Databse_Id_dict.keys()), 
                       help="対象チーム (DQC, ML, NetExp, NetTheory)")
    parser.add_argument("--days", type=int, default=7, 
                       help="何日前からのデータを対象にするか (デフォルト: 7)")
    parser.add_argument("--category", choices=["ProgressReport", "Note", "Paper"], 
                       default="ProgressReport", help="投稿カテゴリ")
    parser.add_argument("--action", choices=["show", "summary"], default="summary",
                       help="実行する操作 (show: データ表示, summary: 要約投稿)")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="対話モードで実行")
    
    args = parser.parse_args()
    
    # 対話モード
    if args.interactive:
        interactive_mode()
        return
    
    # 引数チェック
    if not args.team:
        print("❌ エラー: --teamパラメータが必要です。")
        print("💡 対話モードを使用する場合は --interactive オプションを指定してください。")
        parser.print_help()
        sys.exit(1)
    
    # API キーチェック
    if not Notion_API_Key:
        print("❌ エラー: 環境変数NOTION_TOKENが設定されていません。")
        sys.exit(1)
    
    if not OPENAI_API_KEY and args.action == "summary":
        print("❌ エラー: 環境変数OPENAI_TOKENが設定されていません。")
        sys.exit(1)
    
    if not Output_Database_Id and args.action == "summary":
        print("❌ エラー: 環境変数NOTION_DB_OUTPUTが設定されていません。")
        sys.exit(1)
    
    # 実行
    if args.action == "show":
        show_team_progress(args.team, args.days, args.category)
    else:
        post_summary(Output_Database_Id, OPENAI_API_KEY, args.days, args.team, args.category)

if __name__ == "__main__":
    main()




