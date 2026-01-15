# src/core/ollama_analyzer.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class OllamaAnalyzer:
    def __init__(self, host="http://localhost:11434", model="qwen3-coder:30b"):
        self.host = host
        self.model = model
        # 创建带重试机制的 session
        self.session = self._create_session()

    def _create_session(self):
        """创建带重试机制的 requests session"""
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def analyze_website(self, info):
        """对网站进行AI分析并自动生成标签"""
        try:
            url = f"{info.get('protocol', 'http')}://{info.get('host', '')}"
            if info.get('port') not in ['80', '443']:
                url += f":{info.get('port', '')}"

            prompt = f"""你是一个专业的网络安全分析专家，请为以下网站生成安全相关的标签：

URL: {url}
标题: {info.get('title', 'N/A')}

请根据网站特征自动生成2-5个安全相关的标签。严格按照以下JSON格式返回：

{{
    "tags": ["标签1", "标签2", "标签3"],
    "summary": "简要分析说明"
}}
"""

            # 使用 session 发送请求
            resp = self.session.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.3,
                        "num_ctx": 2048
                    }
                },
                timeout=120  # 增加超时时间（30B模型需要更多时间）
            )

            if resp.status_code == 200:
                import json
                response_data = resp.json()
                result_text = response_data.get("response", "{}")

                try:
                    result = json.loads(result_text)
                    if "tags" not in result or not isinstance(result["tags"], list):
                        result["tags"] = ["AI分析"]
                    if "summary" not in result:
                        result["summary"] = "AI安全分析完成"

                    return {
                        "tags": result["tags"][:5],
                        "summary": result["summary"],
                        "confidence": 0.9
                    }
                except json.JSONDecodeError:
                    # 如果 JSON 解析失败，返回原始文本作为标签
                    return {
                        "tags": [result_text[:30]],
                        "summary": "非结构化响应",
                        "confidence": 0.7
                    }
            else:
                error_msg = f"API错误 {resp.status_code}"
                print(f"Ollama API 错误: {error_msg}")
                return self._get_fallback_result(error_msg)

        except requests.exceptions.ConnectionError as e:
            error_msg = f"连接错误: {str(e)}"
            print(f"Ollama 连接错误: {error_msg}")
            return self._get_fallback_result(error_msg)
        except requests.exceptions.Timeout as e:
            error_msg = f"超时错误: {str(e)}"
            print(f"Ollama 超时错误: {error_msg}")
            return self._get_fallback_result(error_msg)
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(f"Ollama 未知错误: {error_msg}")
            return self._get_fallback_result(error_msg)

    def _get_fallback_result(self, error_msg):
        """获取降级分析结果"""
        return {
            "tags": ["AI分析", error_msg[:20]],
            "summary": error_msg,
            "confidence": 0.0
        }