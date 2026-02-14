from flask import Blueprint, render_template, jsonify
from app.controllers.chat_controller import chat_service
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
    
    # 向量庫資訊（檢查目錄，不是檔案）
    vectorstore_dir = "instance/vectorstore/faiss_index"
    vectorstore_file = os.path.join(vectorstore_dir, "index.faiss")
    
    vectorstore_exists = os.path.exists(vectorstore_file)
    
    if vectorstore_exists:
        vectorstore_size = os.path.getsize(vectorstore_file) / 1024  # KB
    else:
        vectorstore_size = 0
    
    return jsonify({
        "usage": usage,
        "vectorstore": {
            "exists": vectorstore_exists,
            "size_kb": round(vectorstore_size, 2)
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
        from config import Config
        
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