# run.py
import os
from app import create_app

# 從環境變數讀取組態名稱，預設為 'development'
config_name = os.getenv('FLASK_ENV', 'development')

# 建立應用實例
app = create_app(config_name)

if __name__ == '__main__':
    # 啟動開發伺服器
    # host='0.0.0.0' 表示允許外部訪問
    # port=5000 表示使用 5000 埠
    app.run(host='0.0.0.0', port=5000)