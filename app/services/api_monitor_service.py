import os
import json
from datetime import datetime

class ApiMonitorService:
    def __init__(self):
        self.monitor_file = "instance/api_usage.json"
        os.makedirs(os.path.dirname(self.monitor_file), exist_ok=True)
    
    def _load_data(self):
        """載入使用紀錄"""
        if os.path.exists(self.monitor_file):
            try:
                with open(self.monitor_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_data(self, data):
        """儲存使用紀錄"""
        with open(self.monitor_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def log_api_call(self, api_type):
        """記錄 API 呼叫"""
        data = self._load_data()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in data:
            data[today] = {"gemini": 0, "embeddings": 0, "total": 0}
        
        data[today][api_type] = data[today].get(api_type, 0) + 1
        data[today]["total"] = data[today]["gemini"] + data[today]["embeddings"]
        
        self._save_data(data)
    
    def get_today_usage(self):
        """取得今日用量"""
        data = self._load_data()
        today = datetime.now().strftime("%Y-%m-%d")
        return data.get(today, {"gemini": 0, "embeddings": 0, "total": 0})
    
    def get_all_usage(self):
        """取得所有歷史紀錄"""
        return self._load_data()