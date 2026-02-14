import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change-in-production'
    DEBUG = True
    
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600
    
    # 領域知識庫設定
    KNOWLEDGE_DOMAINS = {
        'salary': {
            'name': '薪資福利諮詢',
            'pdf_dir': 'data/knowledge_base/salary',
            'vectorstore': 'instance/vectorstore/salary',
            'description': '薪資、津貼、獎勵金相關諮詢'
        },
        'ecommerce': {
            'name': '電商客服',
            'pdf_dir': 'data/knowledge_base/ecommerce',
            'vectorstore': 'instance/vectorstore/ecommerce',
            'description': '商品、訂單、退換貨相關諮詢'
        },
        'finance': {
            'name': '金融理財',
            'pdf_dir': 'data/knowledge_base/finance',
            'vectorstore': 'instance/vectorstore/finance',
            'description': '投資、貸款、保險相關諮詢'
        }
    }
    
    # 預設領域
    DEFAULT_DOMAIN = 'salary'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}