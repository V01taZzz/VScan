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
        self.key = key

    def search_by_domain(self, domain, size=30):
        if not self.key:
            return []
        try:
            resp = requests.post(
                'https://quake.360.net/api/quake_service/search/quake_http',
                headers={'X-QuakeToken': self.key},
                json={"query": f'domain:"{domain}"', "size": size},
                timeout=20, verify=False
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