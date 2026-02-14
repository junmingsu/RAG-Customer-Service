#from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os

class FileProcessorService:
    def __init__(self, chunk_size=2000, chunk_overlap=100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
    
    def load_pdf(self, pdf_path):
        """載入單一 PDF 文件"""
        loader = PyPDFLoader(pdf_path)
        return loader.load()
    
    def load_pdfs_from_directory(self, directory):
        """載入目錄中所有 PDF"""
        documents = []
        
        if not os.path.exists(directory):
            print(f"目錄不存在: {directory}")
            return documents
        
        pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"目錄中沒有 PDF 文件: {directory}")
            return documents
        
        print(f"找到 {len(pdf_files)} 個 PDF 文件")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(directory, pdf_file)
            try:
                docs = self.load_pdf(pdf_path)
                documents.extend(docs)
                print(f"✅ 載入: {pdf_file} ({len(docs)} 頁)")
            except Exception as e:
                print(f"❌ 載入失敗: {pdf_file} - {e}")
        
        return documents
    
    def split_documents(self, documents):
        """分割文件為小塊"""
        chunks = self.text_splitter.split_documents(documents)
        print(f"文件分塊完成: {len(chunks)} 個片段")
        return chunks