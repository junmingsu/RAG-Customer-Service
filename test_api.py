import os
from dotenv import load_dotenv  # <--- 新增這行
import google.generativeai as genai


# 1. 強制載入 .env 檔案
load_dotenv()  # <--- 新增這行，這會讀取您專案目錄下的 .env 檔案


# 1. 檢查環境變數
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ 嚴重錯誤: 系統找不到 GOOGLE_API_KEY 環境變數！")
    print("👉 請確認您是否有在 .env 檔案中設定，或是否已執行 load_dotenv")
    exit()

print(f"🔑 偵測到 API Key: {api_key[:6]}......{api_key[-4:]}")

# 2. 設定 SDK
genai.configure(api_key=api_key)

# 3. 嘗試列出所有可用模型
print("\n📡 正在連線 Google 伺服器查詢模型清單...")
try:
    available_models = []
    for m in genai.list_models():
        if 'embed' in m.name:
            available_models.append(m.name)
            print(f"   ✅ 發現模型: {m.name}")

    if not available_models:
        print("\n⚠️ 警告: 連線成功，但您的帳號「沒有權限」使用任何 Embedding 模型。")
        print("👉 可能原因: 您的 Google Cloud 專案未啟用 'Generative Language API'，或該 Key 僅限於 Vertex AI。")
    else:
        print(f"\n🎉 恭喜！您的 API Key 功能正常，共發現 {len(available_models)} 個嵌入模型。")
        
        # 4. 測試實際嵌入
        print("\n🧪 正在測試 embedding-004 模型寫入...")
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content="測試文字",
                task_type="retrieval_document"
            )
            print("✅ 寫入測試成功！向量長度:", len(result['embedding']))
        except Exception as e:
            print(f"❌ 模型存在但寫入失敗: {e}")

except Exception as e:
    print(f"\n❌ 連線完全失敗: {e}")
    print("👉 請檢查: 1. 網路是否通暢 2. API Key 是否已失效 3. 是否需開啟 VPN")