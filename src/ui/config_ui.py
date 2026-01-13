# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date:2026/1/13
版本: 1.0.0
Design by V01ta
"""
# src/ui/config_ui.py
# -*- coding: utf-8 -*-
"""
API 配置界面
"""
import tkinter as tk
from tkinter import Toplevel, StringVar, messagebox
# 修复导入路径 - 使用绝对导入
from src.core.config_manager import load_config, save_config
from src.core.fofa_client import FofaClient
from src.core.quake_client import QuakeClient


class ConfigDialog:
    def __init__(self, parent, config):
        self.parent = parent
        self.original_config = config

        # 保存当前密钥值用于检测修改
        self.current_fofa_key = config.get('api', {}).get('fofa', {}).get('key', '')
        self.current_quake_key = config.get('api', {}).get('quake', {}).get('key', '')

        self.config = {
            'api': {
                'fofa': {
                    'key': self.current_fofa_key,
                    'validated': config.get('api', {}).get('fofa', {}).get('validated', False)
                },
                'quake': {
                    'key': self.current_quake_key,
                    'validated': config.get('api', {}).get('quake', {}).get('validated', False)
                }
            }
        }

        self.create_dialog()

    def create_dialog(self):
        self.dialog = Toplevel(self.parent)
        self.dialog.title("API Key配置")
        self.dialog.geometry("450x180")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # FOFA Key - 明文显示（关键：不设置 show="*"）
        tk.Label(self.dialog, text="FOFA Key:").grid(row=0, column=0, sticky="w", padx=20, pady=10)
        self.fofa_key_var = StringVar(value=self.current_fofa_key)  # 显示已保存的值
        self.fofa_key_entry = tk.Entry(self.dialog, textvariable=self.fofa_key_var, width=30)
        self.fofa_key_entry.grid(row=0, column=1, padx=10, pady=10)
        # 绑定修改事件，用于重置验证状态
        self.fofa_key_var.trace('w', lambda *args: self.on_fofa_key_change())

        # FOFA 验证状态框
        fofa_status_frame = tk.Frame(self.dialog, relief="solid", borderwidth=1, width=60, height=25)
        fofa_status_frame.grid(row=0, column=2, padx=5, pady=10)
        fofa_status_frame.pack_propagate(False)
        self.fofa_status_label = tk.Label(fofa_status_frame, text="未验证", fg="red")
        self.fofa_status_label.pack(expand=True)

        # FOFA 验证按钮
        fofa_validate_btn = tk.Button(
            self.dialog,
            text="验证",
            command=lambda: self.validate_key('fofa'),
            bg="#17a2b8",
            fg="white",
            width=6
        )
        fofa_validate_btn.grid(row=0, column=3, padx=5, pady=10)

        # Quake Key - 明文显示
        tk.Label(self.dialog, text="Quake Key:").grid(row=1, column=0, sticky="w", padx=20, pady=10)
        self.quake_key_var = StringVar(value=self.current_quake_key)
        self.quake_key_entry = tk.Entry(self.dialog, textvariable=self.quake_key_var, width=30)
        self.quake_key_entry.grid(row=1, column=1, padx=10, pady=10)
        # 绑定修改事件
        self.quake_key_var.trace('w', lambda *args: self.on_quake_key_change())

        # Quake 验证状态框
        quake_status_frame = tk.Frame(self.dialog, relief="solid", borderwidth=1, width=60, height=25)
        quake_status_frame.grid(row=1, column=2, padx=5, pady=10)
        quake_status_frame.pack_propagate(False)
        self.quake_status_label = tk.Label(quake_status_frame, text="未验证", fg="red")
        self.quake_status_label.pack(expand=True)

        # Quake 验证按钮
        quake_validate_btn = tk.Button(
            self.dialog,
            text="验证",
            command=lambda: self.validate_key('quake'),
            bg="#17a2b8",
            fg="white",
            width=6
        )
        quake_validate_btn.grid(row=1, column=3, padx=5, pady=10)

        # 按钮区域
        button_frame = tk.Frame(self.dialog)
        button_frame.grid(row=2, column=0, columnspan=4, pady=15)

        save_btn = tk.Button(
            button_frame,
            text="保存",
            command=self.save_config,
            bg="#28a745",
            fg="white",
            width=10
        )
        save_btn.pack(side="left", padx=10)

        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            command=self.dialog.destroy,
            width=8
        )
        cancel_btn.pack(side="left", padx=10)

        # 初始化验证状态显示
        self.update_validation_status()

    def on_fofa_key_change(self):
        """当 FOFA 密钥被修改时，重置验证状态"""
        current_value = self.fofa_key_var.get()
        if current_value != self.current_fofa_key:
            self.fofa_status_label.config(text="未验证", fg="red")

    def on_quake_key_change(self):
        """当 Quake 密钥被修改时，重置验证状态"""
        current_value = self.quake_key_var.get()
        if current_value != self.current_quake_key:
            self.quake_status_label.config(text="未验证", fg="red")

    def update_validation_status(self):
        """根据配置中的验证状态更新UI显示"""
        # FOFA 状态
        if self.config['api']['fofa']['validated'] and self.current_fofa_key:
            self.fofa_status_label.config(text="可用", fg="green")
        else:
            if self.current_fofa_key:
                self.fofa_status_label.config(text="未验证", fg="red")
            else:
                self.fofa_status_label.config(text="未设置", fg="red")

        # Quake 状态
        if self.config['api']['quake']['validated'] and self.current_quake_key:
            self.quake_status_label.config(text="可用", fg="green")
        else:
            if self.current_quake_key:
                self.quake_status_label.config(text="未验证", fg="red")
            else:
                self.quake_status_label.config(text="未设置", fg="red")

    def validate_key(self, engine):
        if engine == 'fofa':
            key = self.fofa_key_var.get().strip()
            if key:
                client = FofaClient(key)
                if client.validate_key():
                    self.fofa_status_label.config(text="可用", fg="green")
                    self.config['api']['fofa']['validated'] = True
                else:
                    self.fofa_status_label.config(text="不可用", fg="red")
                    self.config['api']['fofa']['validated'] = False
            else:
                self.fofa_status_label.config(text="未设置", fg="red")
                self.config['api']['fofa']['validated'] = False

        elif engine == 'quake':
            key = self.quake_key_var.get().strip()
            if key:
                client = QuakeClient(key)
                if client.validate_key():  # ← 调用新的验证方法
                    self.quake_status_label.config(text="可用", fg="green")
                    self.config['api']['quake']['validated'] = True
                else:
                    self.quake_status_label.config(text="不可用", fg="red")
                    self.config['api']['quake']['validated'] = False
            else:
                self.quake_status_label.config(text="未设置", fg="red")
                self.config['api']['quake']['validated'] = False

    def save_config(self):
        # 保存密钥和验证状态
        fofa_key = self.fofa_key_var.get()
        quake_key = self.quake_key_var.get()

        config_to_save = {
            'api': {
                'fofa': {
                    'key': fofa_key,
                    'validated': self.config['api']['fofa']['validated'] if fofa_key == self.current_fofa_key else False
                },
                'quake': {
                    'key': quake_key,
                    'validated': self.config['api']['quake'][
                        'validated'] if quake_key == self.current_quake_key else False
                }
            }
        }

        save_config(config_to_save)
        messagebox.showinfo("成功", "配置已保存！")
        self.dialog.destroy()