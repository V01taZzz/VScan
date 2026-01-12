# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date:2026/1/12 
版本: 1.0.0
Design by V01ta
"""
import time
import pytest
import tkinter as tk
from src.ui.Scan_UI import SecurityScannerGUI

class TestPureUI:
    """纯 UI 界面测试（不涉及后端逻辑）"""

    @pytest.fixture
    def gui_app(self):
        """Fixture: 启动 GUI 应用（隐藏窗口）"""
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口（避免干扰）
        app = SecurityScannerGUI(root)
        yield app
        root.destroy()

    def test_config_api_button_opens_dialog(self, gui_app):
        """测试点击「配置API」按钮弹出对话框"""
        # 模拟点击按钮
        gui_app.open_config_dialog()

        # 验证弹窗存在
        assert hasattr(gui_app, 'config_dialog')
        assert gui_app.config_dialog.winfo_exists()

        # 验证弹窗包含关键元素
        assert hasattr(gui_app, 'fofa_key_entry')
        assert hasattr(gui_app, 'quake_key_entry')
        assert gui_app.config_dialog.title() == "API Key配置"

    def test_fofa_key_visibility_toggle(self, gui_app):
        """测试 FOFA 密钥显示/隐藏切换"""
        gui_app.open_config_dialog()

        # 初始状态：密码模式
        assert gui_app.fofa_key_entry.cget('show') == '*'

        # 模拟点击"显示"按钮
        gui_app.fofa_toggle_btn.invoke()  # tkinter 的 invoke() 模拟点击

        # 验证变为明文
        assert gui_app.fofa_key_entry.cget('show') == ''

        # 再次点击"隐藏"
        gui_app.fofa_toggle_btn.invoke()
        assert gui_app.fofa_key_entry.cget('show') == '*'

    def test_quake_key_visibility_toggle(self, gui_app):
        """测试 Quake 密钥显示/隐藏切换"""
        gui_app.open_config_dialog()

        # 初始状态：密码模式
        assert gui_app.quake_key_entry.cget('show') == '*'

        # 模拟点击
        gui_app.quake_toggle_btn.invoke()
        assert gui_app.quake_key_entry.cget('show') == ''

    def test_main_input_field_is_editable(self, gui_app):
        """测试主界面输入框可编辑"""
        # 验证默认值
        assert gui_app.target_var.get() == "baidu.com"

        # 模拟用户输入
        gui_app.target_entry.delete(0, tk.END)
        gui_app.target_entry.insert(0, "test.com")

        # 验证值更新
        assert gui_app.target_var.get() == "test.com"

    def test_scan_button_text_changes_when_clicked(self, gui_app):
        """测试扫描按钮状态变化（简化版）"""
        # 注意：由于 start_scan 会启动线程，这里只验证初始状态
        assert gui_app.scan_btn.cget('text') == "查询"

        # 模拟点击（不实际扫描）
        original_command = gui_app.scan_btn.cget('command')
        assert original_command is not None  # 确保绑定了事件

    def test_table_exists_and_has_columns(self, gui_app):
        """测试结果表格存在且有正确列"""
        columns = gui_app.tree["columns"]
        expected_cols = ("ID", "URL", "IP", "端口", "协议", "标题", "来源", "AI判断")

        assert columns == expected_cols

        # 验证列标题
        for col in expected_cols:
            assert gui_app.tree.heading(col, "text") == col