# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date:2026/1/12 
版本: 1.0.0
Design by V01ta
"""
import requests


class QuakeClient:
    def __init__(self, key):
        self.key = key or ""

    def validate_key(self):
        """验证 Quake API Key 是否有效"""
        if not self.key.strip():
            return False

        try:
            # 发送一个简单的测试请求
            resp = requests.post(
                'https://quake.360.net/api/quake_service/query_quota',
                headers={'X-QuakeToken': self.key},
                timeout=10,
                verify=False
            )
            if resp.status_code == 200:
                data = resp.json()
                # Quake 的 quota 接口返回 code=0 表示有效
                return data.get('code') == 0
        except Exception as e:
            print(f"Quake 验证错误: {e}")
        return False

    def search_by_domain(self, domain, size=30):
        if not self.key.strip():
            print("Quake API 密钥未配置，跳过查询")
            return []

        try:
            resp = requests.post(
                'https://quake.360.net/api/quake_service/search/quake_http',
                headers={'X-QuakeToken': self.key},
                json={"query": f'domain:"{domain}"', "size": size},
                timeout=20,
                verify=False
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get('code') == 0:
                    return [
                        {'host': item['service']['http'].get('host', ''),
                         'ip': item['ip'], 'port': item['port'],
                         'protocol': 'https' if item['port'] == 443 else 'http',
                         'title': item['service']['http'].get('title', ''),
                         'source': 'quake'}
                        for item in data.get('data', []) if 'service' in item
                    ]
        except Exception as e:
            print(f"Quake Error: {e}")
        return []