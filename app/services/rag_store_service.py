from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import time

class RagStoreService:
    def __init__(self, domain='salary'):
        self.domain = domain
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            task_type="retrieval_document"
        )
        self.vectorstore = None
        self.persist_directory = f"instance/vectorstore/{domain}"
        self.vectorstore_path = os.path.join(self.persist_directory, "faiss_index")
    
    def initialize_vectorstore(self, chunks, force_rebuild=False):
        """初始化向量資料庫"""
        os.makedirs(self.persist_directory, exist_ok=True)
        
        vectorstore_file = os.path.join(self.vectorstore_path, "index.faiss")
        
        if os.path.exists(vectorstore_file) and not force_rebuild:
            try:
                print(f"✅ 載入現有向量資料庫 (領域: {self.domain})")
                self.vectorstore = FAISS.load_local(
                    self.vectorstore_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return
            except Exception as e:
                print(f"⚠️ 載入失敗: {e}")
                print("🔄 將重新建立向量資料庫...")
                force_rebuild = True
        
        if not chunks:
            print("❌ 沒有文件可處理")
            raise Exception("沒有文件可處理")
        
        print(f"🔄 建立向量資料庫 (領域: {self.domain})...")
        
        batch_size = 20
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            print(f"處理批次 {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
            
            try:
                if i == 0:
                    self.vectorstore = FAISS.from_documents(
                        documents=batch,
                        embedding=self.embeddings
                    )
                else:
                    self.vectorstore.add_documents(batch)
                
                if i + batch_size < len(chunks):
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ 批次處理錯誤: {e}")
                time.sleep(5)
        
        if self.vectorstore:
            self.vectorstore.save_local(self.vectorstore_path)
            print(f"✅ 向量資料庫建立完成 (領域: {self.domain})")
        else:
            print("❌ 向量資料庫建立失敗")
            raise Exception("向量資料庫建立失敗")
    
    def similarity_search(self, query, k=3):
        """相似度檢索"""
        if not self.vectorstore:
            return []
        return self.vectorstore.similarity_search(query, k=k)