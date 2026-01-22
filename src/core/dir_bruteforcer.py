# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date:2026/1/22 
版本: 1.0.0
Design by V01ta
"""
# src/core/dir_bruteforcer.py
import requests
from urllib.parse import urljoin
from queue import Queue
import threading
from typing import List, Dict, Callable


class DirBruteforcer:
    """目录爆破核心逻辑类"""

    def __init__(self):
        self.is_running = False
        self.session = requests.Session()
        self.session.verify = False
        self.session.timeout = 10

        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def start_bruteforce(self, base_url: str, paths: List[str], thread_count: int,
                         callback: Callable[[Dict], None], status_callback: Callable[[str], None]):
        """
        开始目录爆破

        Args:
            base_url: 目标URL
            paths: 路径列表
            thread_count: 线程数
            callback: 结果回调函数
            status_callback: 状态更新回调函数
        """
        self.is_running = True

        # 创建队列
        path_queue = Queue()
        result_queue = Queue()

        # 添加路径到队列
        for path in paths:
            path_queue.put(path)

        # 启动工作线程
        threads = []
        for i in range(thread_count):
            t = threading.Thread(
                target=self._worker_thread,
                args=(base_url, path_queue, result_queue, callback),
                daemon=True
            )
            t.start()
            threads.append(t)

        # 启动结果收集线程
        collector_thread = threading.Thread(
            target=self._result_collector,
            args=(result_queue, len(paths), status_callback),
            daemon=True
        )
        collector_thread.start()

        return threads, collector_thread

    def stop_bruteforce(self):
        """停止目录爆破"""
        self.is_running = False

    def _worker_thread(self, base_url: str, path_queue: Queue, result_queue: Queue, callback: Callable):
        """工作线程"""
        while not path_queue.empty() and self.is_running:
            try:
                path = path_queue.get_nowait()
                result = self._check_path(base_url, path)
                if result:
                    result_queue.put(result)
                    callback(result)
                else:
                    result_queue.put(None)
            except:
                break

    def _check_path(self, base_url: str, path: str) -> Dict:
        """检查单个路径"""
        try:
            # 构建完整URL
            if path.startswith('/'):
                full_url = urljoin(base_url, path)
            else:
                full_url = urljoin(base_url.rstrip('/') + '/', path)

            # 发送请求
            resp = self.session.get(
                full_url,
                timeout=10,
                allow_redirects=False,
                headers=self.headers
            )

            status_code = resp.status_code
            content_length = len(resp.content)

            # 过滤有效响应
            if status_code in [200, 301, 302, 401, 403]:
                title = ""
                if status_code == 200:
                    try:
                        resp.encoding = resp.apparent_encoding
                        title_start = resp.text.find('<title>')
                        title_end = resp.text.find('</title>')
                        if title_start != -1 and title_end != -1:
                            title = resp.text[title_start + 7:title_end].strip()[:50]
                    except:
                        pass

                return {
                    'url': full_url,
                    'status_code': status_code,
                    'length': content_length,
                    'title': title
                }

        except Exception as e:
            pass

        return None

    def _result_collector(self, result_queue: Queue, total_paths: int, status_callback: Callable):
        """结果收集线程"""
        completed = 0
        found_count = 0

        while completed < total_paths and self.is_running:
            try:
                result = result_queue.get(timeout=1)
                if result is not None:
                    found_count += 1
                completed += 1

                # 每10个路径更新一次状态
                if completed % 10 == 0 or completed == total_paths:
                    status_callback(f"已扫描 {completed}/{total_paths} 个路径，发现 {found_count} 个有效路径")

            except:
                continue

        # 最终状态
        status_callback(f"爆破完成，共发现 {found_count} 个有效路径")