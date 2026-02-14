import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.knowledge_service import KnowledgeService

# 初始化
knowledge_service = KnowledgeService()
knowledge_service.initialize_knowledge_base(
    pdf_directory="data/knowledge_base",
    force_rebuild=False
)

# 測試檢索
test_questions = [
    "生活津貼最長可以領幾個月",
    "學習獎勵金每個月多少錢"
]

for question in test_questions:
    print(f"\n問題：{question}")
    print("=" * 50)
    
    results = knowledge_service.search_knowledge(question, k=3)
    
    if results:
        print(f"✅ 找到 {len(results)} 筆相關文件")
        for i, doc in enumerate(results, 1):
            print(f"\n--- 文件 {i} ---")
            print(doc.page_content[:200])  # 顯示前 200 字
    else:
        print("❌ 沒有找到相關文件")