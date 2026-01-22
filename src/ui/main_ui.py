# src/ui/main_ui.py
# -*- coding: utf-8 -*-
"""
VScan 主界面 - 标签页容器
"""

import tkinter as tk
from tkinter import ttk, StringVar
from src.ui.space_mapping_ui import SpaceMappingUI
from src.ui.dir_bruteforce_ui import DirBruteforceUI


class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VScan安全空间测绘 - 金小白特供版")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)

        # 创建主标签页
        self.create_main_notebook()

        # 创建共享状态栏
        self.create_shared_status_bar()

    def create_main_notebook(self):
        """创建主功能标签页"""
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # 创建空间测绘页面
        self.space_mapping_ui = SpaceMappingUI(self.main_notebook, self)

        # 创建目录爆破页面
        self.dir_bruteforce_ui = DirBruteforceUI(self.main_notebook, self)

    def create_shared_status_bar(self):
        """创建共享状态栏"""
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=5)

        self.status_var = StringVar(value="就绪")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, fg="blue", anchor="w")
        self.status_label.pack(side="left")

    def update_status(self, message):
        """更新状态栏消息"""
        self.status_var.set(message)

    def get_status_var(self):
        """获取状态变量（用于直接绑定）"""
        return self.status_var

    def switch_to_bruteforce_tab(self, url):
        """切换到目录爆破标签页并设置目标URL"""
        # 切换到目录爆破标签页（索引为1）
        self.main_notebook.select(1)

        # 设置目标URL
        if hasattr(self.dir_bruteforce_ui, 'brute_target_var'):
            self.dir_bruteforce_ui.brute_target_var.set(url)
            self.update_status(f"已发送 {url} 到目录爆破")