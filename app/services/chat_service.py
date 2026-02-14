from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.knowledge_service import KnowledgeService
from app.services.api_monitor_service import ApiMonitorService
from config import Config
import os

class ChatService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-flash-latest",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7
            convert_system_message_to_human=True 
        )
        
        self.knowledge_services = {}
        self.current_domain = Config.DEFAULT_DOMAIN
        self.api_monitor = ApiMonitorService()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是專業客服助手。請仔細閱讀知識庫內容並清楚回答問題。

知識庫內容：
{context}

對話歷史：
{history}

回答規則：
1. 知識庫有相關資訊時，直接提取並回答
2. 回答要清楚、簡潔、易讀
3. 使用繁體中文

格式要求（非常重要）：
1. 如果有多個項目，使用編號列表（1. 2. 3.）
2. 每個重點之間要換行
3. 重要關鍵字用 **粗體** 標記（例如：**申請資格**）
4. 條件說明要分行，不要全部擠在一起

範例格式：
問：需要哪些文件？
答：申請時需要準備以下文件：

**必備文件**：
1. 國民身份證正反面影本
2. 申請切結書（正本）

**特定身分需加附**：
1. 身心障礙者：身心障礙證明
2. 原住民：戶口名簿或戶籍謄本

請記得換行與分點說明。"""),
            ("human", "{question}")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
        
        # 改用多層結構：chat_histories[session_id][domain] = []
        self.chat_histories = {}
    
    def switch_domain(self, domain):
        """切換領域（不清空歷史）"""
        if domain not in Config.KNOWLEDGE_DOMAINS:
            return False
        
        self.current_domain = domain
        print(f"✅ 切換至領域: {Config.KNOWLEDGE_DOMAINS[domain]['name']}")
        return True
    
    def _get_knowledge_service(self, domain):
        if domain not in self.knowledge_services:
            try:
                service = KnowledgeService(domain=domain)
                domain_config = Config.KNOWLEDGE_DOMAINS[domain]
                service.initialize_knowledge_base(
                    pdf_directory=domain_config['pdf_dir'],
                    force_rebuild=False
                )
                self.knowledge_services[domain] = service
                print(f"✅ 領域 {domain} 知識庫載入成功")
            except Exception as e:
                print(f"⚠️ 領域 {domain} 知識庫載入失敗: {e}")
                return None
        
        return self.knowledge_services.get(domain)
    
    def get_history(self, session_id, domain=None):
        """取得特定領域的對話歷史"""
        if domain is None:
            domain = self.current_domain
        
        # 確保結構存在
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = {}
        
        if domain not in self.chat_histories[session_id]:
            self.chat_histories[session_id][domain] = []
        
        return self.chat_histories[session_id][domain]
    
    def add_to_history(self, session_id, question, answer, domain=None):
        """加入對話歷史到特定領域"""
        if domain is None:
            domain = self.current_domain
        
        history = self.get_history(session_id, domain)
        history.append(f"使用者: {question}")
        history.append(f"助手: {answer}")
        
        # 限制每個領域的歷史長度
        if len(history) > 20:
            self.chat_histories[session_id][domain] = history[-20:]
    
    def generate_answer(self, question, session_id="default"):
        try:
            knowledge_service = self._get_knowledge_service(self.current_domain)
            
            context = "無相關資料"
            if knowledge_service:
                relevant_docs = knowledge_service.search_knowledge(question, k=3)
                if relevant_docs:
                    context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # 取得當前領域的歷史
            history = self.get_history(session_id, self.current_domain)
            history_text = "\n".join(history[-10:]) if history else "無"
            
            self.api_monitor.log_api_call("gemini")
            
            answer = self.chain.invoke({
                "context": context,
                "history": history_text,
                "question": question
            })
            
            # 儲存到當前領域的歷史
            self.add_to_history(session_id, question, answer, self.current_domain)
            return answer
            
        except Exception as e:
            error_msg = str(e)
            print(f"錯誤: {error_msg}")
            
            if "404" in error_msg or "NOT_FOUND" in error_msg:
                return "系統暫時無法連接 AI 服務，請稍後再試。"
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return "API 額度已達上限，請明日再試或聯絡管理員。"
            else:
                return f"系統發生錯誤，請稍後再試。"
    
    def reset_conversation(self, session_id="default", domain=None):
        """重置特定領域的對話（不指定則重置當前領域）"""
        if domain is None:
            domain = self.current_domain
        
        if session_id in self.chat_histories:
            if domain in self.chat_histories[session_id]:
                del self.chat_histories[session_id][domain]
        return True
    
    def reset_all_conversations(self, session_id="default"):
        """重置所有領域的對話"""
        if session_id in self.chat_histories:
            del self.chat_histories[session_id]
        return True
    
    def get_api_usage(self):
        return self.api_monitor.get_today_usage()
    
    def get_current_domain(self):
        return {
            'domain': self.current_domain,
            'config': Config.KNOWLEDGE_DOMAINS[self.current_domain]
        }
    
    def get_domain_history(self, session_id, domain):
        """取得特定領域的對話歷史（供前端使用）"""
        return self.get_history(session_id, domain)