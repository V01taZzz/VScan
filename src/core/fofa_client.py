# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date:2026/1/12 
版本: 1.0.0
Design by V01ta
"""
# core/fofa_client.py
# core/fofa_client.py
import base64
import requests


class FofaClient:
    def __init__(self, email, key):
        # 注意：FOFA 实际上只需要 key，email 参数保留但不使用
        self.key = key or ""

    def validate_key(self):
        """验证 FOFA API Key 是否有效"""
        if not self.key.strip():
            return False

        try:
            # 使用一个简单的查询来验证密钥
            query = 'domain="example.com"'
            qbase64 = base64.b64encode(query.encode()).decode()
            resp = requests.get(
                'https://fofa.info/api/v1/search/all',
                params={'key': self.key, 'qbase64': qbase64, 'size': 1},
                timeout=10,
                verify=False
            )
            if resp.status_code == 200:
                data = resp.json()
                # 如果没有 error 字段或 error 为 False，说明密钥有效
                return not data.get('error', True)
        except Exception as e:
            print(f"FOFA 验证错误: {e}")
        return False

    def search_by_domain(self, domain, size=30):
        if not self.key.strip():
            print("FOFA API 密钥未配置，跳过查询")
            return []

        query = f'domain="{domain}"'
        qbase64 = base64.b64encode(query.encode()).decode()
        try:
            resp = requests.get(
                'https://fofa.info/api/v1/search/all',
                params={'key': self.key, 'qbase64': qbase64, 'size': size},
                timeout=20,
                verify=False
            )
            if resp.status_code == 200:
                data = resp.json()
                if not data.get('error'):
                    return [
                        {'host': r[0], 'ip': r[1], 'port': r[2], 'protocol': r[3] or 'http',
                         'title': r[4] or '', 'source': 'fofa'}
                        for r in data.get('results', [])
                    ]
        except Exception as e:
            print(f"FOFA Error: {e}")
        return []