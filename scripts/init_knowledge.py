import sys
import os

# 將專案根目錄加入路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.knowledge_service import KnowledgeService

def main():
    print("初始化知識庫...")
    
    knowledge_service = KnowledgeService()
    pdf_directory = "data/knowledge_base"
    
    # force_rebuild=True 表示重新建立
    success = knowledge_service.initialize_knowledge_base(
        pdf_directory=pdf_directory,
        force_rebuild=True  # 改成 True 可強制重建
    )
    
    if success:
        print("\n測試檢索...")
        results = knowledge_service.search_knowledge("測試問題", k=2)
        print(f"檢索到 {len(results)} 筆結果")
        
        if results:
            print("\n第一筆結果預覽:")
            print(results[0].page_content[:200])

if __name__ == "__main__":
    main()