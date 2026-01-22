# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date: 2026/1/13
版本: 1.2.0
Design by V01ta
"""

import base64
import requests
import time


class FofaClient:
    def __init__(self, key):
        self.key = key or ""

    def validate_key(self):
        """验证 VIP 账户"""
        if not self.key.strip():
            return False

        try:
            resp = requests.get(
                'https://fofa.info/api/v1/info/my',
                params={'key': self.key},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if not data.get('error'):
                    email = data.get('email', '未知')
                    is_vip = data.get('isvip', False)
                    print(f"✅ FOFA 账户: {email}, VIP: {is_vip}")
                    return True
        except Exception as e:
            print(f"FOFA 验证错误: {e}")
        return False

    def search_by_query(self, query, total_size=100):
        """使用自定义查询语法进行搜索"""
        if not self.key.strip():
            print("❌ FOFA 密钥未配置")
            return []

        try:
            qbase64 = base64.b64encode(query.encode()).decode()

            params = {
                'key': self.key,
                'qbase64': qbase64,
                'size': total_size,
                'full': 'true',
                'fields': 'host,ip,port,protocol,title,domain'
            }

            resp = requests.get(
                'https://fofa.info/api/v1/search/all',
                params=params,
                timeout=20
            )

            if resp.status_code != 200:
                print(f"❌ FOFA HTTP 错误: {resp.status_code}")
                return []

            data = resp.json()
            if data.get('error'):
                print(f"❌ FOFA API 错误: {data.get('errmsg')}")
                return []

            results = data.get('results', [])
            return self._parse_results(results)

        except Exception as e:
            print(f"💥 FOFA 请求异常: {e}")
            return []

    def search_by_domain(self, domain, total_size=100):
        """VIP 账户完整扫描"""
        if not self.key.strip():
            print("❌ FOFA 密钥未配置")
            return []

        # 构建查询语法
        query = f'domain="{domain}"'
        print(f"🔍 FOFA 查询语法: {query}")

        all_results = []
        page_size = 3000 # VIP 单次最大
        max_pages = (total_size + page_size - 1) // page_size

        for page in range(1, min(max_pages, 2) + 1):  # 最多2页（20,000条）
            try:
                qbase64 = base64.b64encode(query.encode()).decode()

                params = {
                    'key': self.key,
                    'qbase64': qbase64,
                    'size': min(page_size, total_size - len(all_results)),
                    'page': page,
                    'full': 'true',  # ✅ 关键：启用完整数据
                    'fields': 'host,ip,port,protocol,title,domain'
                }

                # print(f"📡 请求第 {page} 页，参数: size={params['size']}")
                resp = requests.get(
                    'https://fofa.info/api/v1/search/all',
                    params=params,
                    timeout=30
                )

                print(f"📊 响应状态: {resp.status_code}, 内容长度: {len(resp.text)}")

                if resp.status_code != 200:
                    print(f"❌ HTTP 错误: {resp.status_code}")
                    break

                data = resp.json()

                if data.get('error'):
                    print(f"❌ API 错误: {data.get('errmsg')}")
                    break

                results = data.get('results', [])
                print(f"✅ 第 {page} 页获取 {len(results)} 条结果")

                if not results:
                    break

                parsed_results = self._parse_results(results)
                all_results.extend(parsed_results)

                if len(results) < min(page_size, total_size - len(all_results)):
                    break  # 没有更多数据了

                time.sleep(0.5)  # 避免触发限流

            except Exception as e:
                print(f"💥 第 {page} 页请求失败: {e}")
                break

        print(f"🎯 FOFA 总共获取 {len(all_results)} 条有效资产")
        return all_results



    def _parse_results(self, results):
            """解析 FOFA 结果"""
            parsed_results = []

            for r in results:
                if not isinstance(r, list) or len(r) < 3:
                    continue

                host = r[0].strip() if r[0] else ''

                # 清理 host（移除协议）
                if host.startswith(('http://', 'https://')):
                    from urllib.parse import urlparse
                    host = urlparse(host).netloc

                # 提取 IP 和端口
                ip = r[1] if len(r) > 1 and r[1] else ''
                port = r[2] if len(r) > 2 and r[2] else ''

                # 协议推断
                protocol = 'https' if str(port) == '443' else 'http'
                if len(r) > 3 and r[3]:
                    protocol = r[3]

                # 标题
                title = r[4] if len(r) > 4 and r[4] else ''

                # 域名
                domain_field = r[5] if len(r) > 5 and r[5] else host

                parsed_results.append({
                    'host': host,
                    'ip': ip,
                    'port': port,
                    'protocol': protocol,
                    'title': title,
                    'domain': domain_field,
                    'source': 'fofa'
                })

            return parsed_results