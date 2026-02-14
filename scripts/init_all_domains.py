import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.knowledge_service import KnowledgeService
from config import Config

def main():
    print("=" * 60)
    print("初始化所有領域知識庫")
    print("=" * 60)
    
    for domain_key, domain_config in Config.KNOWLEDGE_DOMAINS.items():
        print(f"\n>>> 領域: {domain_config['name']} ({domain_key})")
        
        # 檢查目錄是否有 PDF
        pdf_dir = domain_config['pdf_dir']
        if not os.path.exists(pdf_dir):
            print(f"⚠️ 目錄不存在，跳過: {pdf_dir}")
            continue
        
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        if not pdf_files:
            print(f"⚠️ 沒有 PDF 文件，跳過")
            continue
        
        print(f"找到 {len(pdf_files)} 個 PDF 文件")
        
        # 初始化知識庫
        knowledge_service = KnowledgeService(domain=domain_key)
        success = knowledge_service.initialize_knowledge_base(
            pdf_directory=pdf_dir,
            force_rebuild=False
        )
        
        if success:
            print(f"✅ {domain_config['name']} 初始化成功")
        else:
            print(f"❌ {domain_config['name']} 初始化失敗")
    
    print("\n" + "=" * 60)
    print("✅ 所有領域處理完成")
    print("=" * 60)

if __name__ == "__main__":
    main()