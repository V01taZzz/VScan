# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date:2026/1/12 
版本: 1.0.0
Design by V01ta
"""
import requests


class OllamaAnalyzer:
    def __init__(self, host="http://localhost:11434", model="llama3"):
        self.host = host
        self.model = model

    def is_valid_website(self, info):
        prompt = f"判断网站是否有效：Host={info.get('host', '')}, Title={info.get('title', '')}。回答仅用“有效”或“无效”"
        try:
            resp = requests.post(
                f"{self.host}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30
            )
            return "有效" in resp.json().get("response", "")
        except:
            return True