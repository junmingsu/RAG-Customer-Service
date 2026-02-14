from app.services.file_processor_service import FileProcessorService
from app.services.rag_store_service import RagStoreService
import os

class KnowledgeService:
    def __init__(self, domain='salary'):
        self.domain = domain
        self.file_processor = FileProcessorService()
        self.rag_store = RagStoreService(domain=domain)
    
    def initialize_knowledge_base(self, pdf_directory, force_rebuild=False):
        """初始化知識庫"""
        print("=" * 50)
        print(f"開始初始化知識庫 (領域: {self.domain})")
        print("=" * 50)
        
        vectorstore_file = os.path.join(self.rag_store.vectorstore_path, "index.faiss")
        
        if os.path.exists(vectorstore_file) and not force_rebuild:
            try:
                print("✅ 嘗試載入現有向量資料庫")
                self.rag_store.initialize_vectorstore([], force_rebuild=False)
                print("✅ 向量資料庫載入成功")
                return True
            except Exception as e:
                print(f"⚠️ 載入失敗，將重新建立: {e}")
                force_rebuild = True
        
        print("\n[1/3] 載入 PDF 文件...")
        documents = self.file_processor.load_pdfs_from_directory(pdf_directory)
        
        if not documents:
            print("❌ 沒有找到任何文件")
            return False
        
        print("\n[2/3] 文件分塊...")
        chunks = self.file_processor.split_documents(documents)
        
        print("\n[3/3] 向量嵌入與儲存...")
        self.rag_store.initialize_vectorstore(chunks, force_rebuild=True)
        
        print("\n" + "=" * 50)
        print("✅ 知識庫初始化完成！")
        print("=" * 50)
        
        return True
    
    def search_knowledge(self, question, k=3):
        """檢索知識"""
        return self.rag_store.similarity_search(question, k=k)