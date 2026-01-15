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
    """加载配置，若不存在则返回空结构"""
    config_path = Path(CONFIG_FILE)

    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config is None:
                    config = {}
                return config
        except (yaml.YAMLError, IOError) as e:
            print(f"配置文件加载错误: {e}")

    # 返回简化结构（包含验证状态）
    return {
        'api': {
            'fofa': {'key': '', 'validated': False},
            'quake': {'key': '', 'validated': False}
        }
    }


def save_config(config):
    """保存配置到 YAML 文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    except Exception as e:
        print(f"配置保存失败: {e}")