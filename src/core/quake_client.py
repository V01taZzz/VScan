# core/quake_client.py
# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date: 2026/1/13
版本: 1.2.0
Design by V01ta
"""
import requests
import time


class QuakeClient:
    def __init__(self, key):
        self.key = key or ""

    def validate_key(self):
        """验证 Quake API Key 是否有效 - 使用简单搜索"""
        if not self.key.strip():
            return False

        try:
            headers = {'X-QuakeToken': self.key, 'Content-Type': 'application/json'}
            # 使用最简单的查询来验证密钥
            data = {
                "query": "app:\"nginx\"",
                "start": 0,
                "size": 1
            }

            resp = requests.post(
                'https://quake.360.net/api/v3/search/quake_service',  # 注意：cn 域名
                headers=headers,
                json=data,
                timeout=10
            )

            if resp.status_code == 200:
                data_resp = resp.json()
                # Quake 成功响应的 code 为 0
                if data_resp.get('code') == 0:
                    print("✅ Quake API 密钥验证成功")
                    return True
                else:
                    error_msg = data_resp.get('message', 'Unknown error')
                    print(f"❌ Quake API 错误: {error_msg}")
                    return False
            elif resp.status_code == 401:
                print("❌ Quake API 密钥无效或未授权")
                return False
            else:
                print(f"❌ Quake HTTP 错误: {resp.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"🌐 Quake 网络错误: {e}")
            return False
        except Exception as e:
            print(f"💥 Quake 验证异常: {e}")
            return False

    def search_by_domain(self, domain, total_size=100):
        """Quake 完整扫描 - 使用正确的域名"""
        if not self.key.strip():
            print("❌ Quake 密钥未配置")
            return []

        all_results = []
        page_size = 100
        start = 0
        pages_fetched = 0
        max_pages = min((total_size + page_size - 1) // page_size, 100)

        while start < total_size and pages_fetched < max_pages:
            try:
                headers = {'X-QuakeToken': self.key, 'Content-Type': 'application/json'}
                query = f'domain:"{domain}"'
                data = {
                    "query": query,
                    "start": start,
                    "size": min(page_size, total_size - len(all_results))
                }

                # 使用 .cn 域名（官方域名）
                resp = requests.post(
                    'https://quake.360.net/api/v3/search/quake_service',
                    headers=headers,
                    json=data,
                    timeout=30
                )

                if resp.status_code != 200:
                    print(f"❌ Quake HTTP 错误: {resp.status_code}")
                    break

                data_resp = resp.json()

                if data_resp.get('code') != 0:
                    error_msg = data_resp.get('message', 'Unknown error')
                    print(f"❌ Quake API 错误: {error_msg}")
                    break

                results = data_resp.get('data', [])
                if not results:
                    break

                parsed_results = self._parse_results(results)
                all_results.extend(parsed_results)

                if len(results) < min(page_size, total_size - len(all_results)):
                    break

                start += len(results)
                pages_fetched += 1
                time.sleep(0.5)

            except Exception as e:
                print(f"💥 Quake 请求失败: {e}")
                break

        print(f"🎯 Quake 总共获取 {len(all_results)} 条有效资产")
        return all_results

    def _parse_results(self, results):
        """解析 Quake 结果 - 统一字段名"""
        parsed_results = []

        for item in results:
            if not isinstance(item, dict):
                continue

            ip = item.get('ip', '')
            port = str(item.get('port', ''))

            service = item.get('service', {}).get('http', {})
            host = service.get('host', '')
            title = service.get('title', '')
            server = service.get('server', '')

            # 清理 host
            if host.startswith(('http://', 'https://')):
                from urllib.parse import urlparse
                host = urlparse(host).netloc

            # 如果 host 为空，使用 IP
            if not host:
                host = ip

            protocol = 'https' if port == '443' else 'http'

            # 构建可访问 URL（用于显示）
            if port in ['80', '443']:
                display_url = f"{protocol}://{host}"
            else:
                display_url = f"{protocol}://{host}:{port}"

            parsed_results.append({
                'host': host,  # ✅ 统一使用 'host' 字段
                'ip': ip,
                'port': port,
                'protocol': protocol,
                'title': title,
                'source': 'quake'
            })

        return parsed_results