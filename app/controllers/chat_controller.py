from flask import Blueprint, render_template, request, jsonify, session
from app.services.chat_service import ChatService
from config import Config

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')
chat_service = ChatService()

@chat_bp.route('/')
def index():
    return render_template('chat/index.html')

@chat_bp.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'answer': '請輸入問題'}), 400
    
    session_id = session.get('session_id', 'default')
    answer = chat_service.generate_answer(question, session_id)
    
    return jsonify({'answer': answer})

@chat_bp.route('/reset', methods=['POST'])
def reset():
    """重置當前領域的對話"""
    session_id = session.get('session_id', 'default')
    chat_service.reset_conversation(session_id)
    return jsonify({'message': '當前領域對話已重置'})

@chat_bp.route('/reset-all', methods=['POST'])
def reset_all():
    """重置所有領域的對話"""
    session_id = session.get('session_id', 'default')
    chat_service.reset_all_conversations(session_id)
    return jsonify({'message': '所有對話已重置'})

@chat_bp.route('/domains', methods=['GET'])
def get_domains():
    return jsonify({
        'domains': Config.KNOWLEDGE_DOMAINS,
        'current': chat_service.get_current_domain()
    })

@chat_bp.route('/switch-domain', methods=['POST'])
def switch_domain():
    """切換領域（不清空歷史）"""
    data = request.get_json()
    domain = data.get('domain')
    
    if chat_service.switch_domain(domain):
        return jsonify({
            'success': True,
            'message': f"已切換至 {Config.KNOWLEDGE_DOMAINS[domain]['name']}",
            'current': chat_service.get_current_domain()
        })
    else:
        return jsonify({'success': False, 'message': '領域不存在'}), 404

@chat_bp.route('/history/<domain>', methods=['GET'])
def get_history(domain):
    """取得特定領域的對話歷史"""
    session_id = session.get('session_id', 'default')
    history = chat_service.get_domain_history(session_id, domain)
    
    # 轉換成前端格式
    messages = []
    for i in range(0, len(history), 2):
        if i + 1 < len(history):
            user_msg = history[i].replace('使用者: ', '')
            bot_msg = history[i + 1].replace('助手: ', '')
            messages.append({'type': 'user', 'text': user_msg})
            messages.append({'type': 'bot', 'text': bot_msg})
    
    return jsonify({'messages': messages})