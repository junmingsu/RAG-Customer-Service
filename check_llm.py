import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. 載入環境變數
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ 找不到 GOOGLE_API_KEY")
    exit()

genai.configure(api_key=api_key)

print("📡 正在查詢您的帳號可用模型清單...\n")
found_any = False

# 2. 列出所有支援「內容生成」的模型
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"✅ 可用模型: {m.name}")
        found_any = True

if not found_any:
    print("\n❌ 您的帳號似乎沒有任何可用模型，請檢查 Google AI Studio 設定。")
else:
    print("\n👉 請將上面的其中一個模型名稱 (例如 models/gemini-pro) 填入 chat_service.py")