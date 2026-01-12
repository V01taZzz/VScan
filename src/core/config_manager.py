# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date:2026/1/12
版本: 1.0.0
Design by V01ta
"""
import yaml
from pathlib import Path

CONFIG_FILE = "config.yaml"

def load_config():
    """加载配置，若不存在则返回默认模板"""
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {
        'api': {'fofa': {'email': '', 'key': ''}, 'quake': {'key': ''}},
        'ollama': {'enabled': True, 'host': 'http://localhost:11434', 'model': 'llama3'}
    }

def save_config(config):
    """保存配置到 YAML 文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)