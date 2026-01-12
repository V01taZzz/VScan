# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date:2026/1/12 
版本: 1.0.0
Design by V01ta
"""
import base64
import requests


class FofaClient:
    def __init__(self, email, key):
        self.email = email
        self.key = key

    def search_by_domain(self, domain, size=30):
        if not self.email or not self.key:
            return []
        query = f'domain="{domain}"'
        qbase64 = base64.b64encode(query.encode()).decode()
        try:
            resp = requests.get(
                'https://fofa.info/api/v1/search/all',
                params={'email': self.email, 'key': self.key, 'qbase64': qbase64, 'size': size},
                timeout=20, verify=False
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