from flask import Blueprint, render_template, jsonify
from app.controllers.chat_controller import chat_service
from config import Config
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/monitor')
def monitor():
    """監控儀表板頁面"""
    return render_template('admin/monitor.html')

@admin_bp.route('/api/usage')
def get_usage():
    """API 用量 API"""
    usage = chat_service.get_api_usage()
    
    # 檢查所有領域的向量庫
    vectorstore_status = {}
    total_size = 0
    
    for domain_key in Config.KNOWLEDGE_DOMAINS.keys():
        vectorstore_file = f"instance/vectorstore/{domain_key}/faiss_index/index.faiss"
        exists = os.path.exists(vectorstore_file)
        
        vectorstore_status[domain_key] = exists
        
        if exists:
            try:
                total_size += os.path.getsize(vectorstore_file) / 1024  # KB
            except:
                pass
    
    # 統計
    total_domains = len(Config.KNOWLEDGE_DOMAINS)
    initialized_domains = sum(vectorstore_status.values())
    
    return jsonify({
        "usage": usage,
        "vectorstore": {
            "initialized_count": initialized_domains,
            "total_count": total_domains,
            "size_kb": round(total_size, 2),
            "domains": vectorstore_status
        },
        "limits": {
            "gemini_daily": 1500,
            "embeddings_per_min": 1500
        }
    })

@admin_bp.route('/init-knowledge', methods=['GET', 'POST'])
def init_knowledge():
    """手動初始化知識庫"""
    try:
        from app.services.knowledge_service import KnowledgeService
        
        results = {}
        
        for domain_key, domain_config in Config.KNOWLEDGE_DOMAINS.items():
            try:
                knowledge_service = KnowledgeService(domain=domain_key)
                success = knowledge_service.initialize_knowledge_base(
                    pdf_directory=domain_config['pdf_dir'],
                    force_rebuild=True
                )
                results[domain_key] = 'success' if success else 'failed'
            except Exception as e:
                results[domain_key] = f'error: {str(e)}'
        
        return jsonify({
            'status': 'completed',
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500