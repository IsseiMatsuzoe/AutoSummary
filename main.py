from dotenv import load_dotenv
import os
from notion_utils import *
from openai_chat import *

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_TOKEN")
Notion_API_Key = os.getenv("NOTION_TOKEN")
Input_Database_Id = os.getenv("NOTION_DB_INPUT")
Output_Database_Id = os.getenv("NOTION_DB_OUTPUT")

client = OpenAI(api_key=OPENAI_API_KEY)

if __name__ == "__main__":
    generated_page_json = suumarize_text(OPENAI_API_KEY, get_database_text(Notion_API_Key, Input_Database_Id, 7))
    post_page(Notion_API_Key, Output_Database_Id, generated_page_json)



