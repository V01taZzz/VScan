# ui/main_ui.py
# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date: 2026/1/13
版本: 1.2.0
Design by V01ta
"""

import webbrowser
import threading
import tkinter as tk
from tkinter import ttk, messagebox, StringVar, BooleanVar, END
from src.ui.config_ui import ConfigDialog
from src.core.config_manager import load_config
from src.core.fofa_client import FofaClient
from src.core.quake_client import QuakeClient


class SecurityScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VScan安全空间测绘 - 金小白特供版")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)

        # 加载配置
        self.config = load_config()
        if self.config is None:
            self.config = {}

        # 创建 UI
        self.create_widgets()
        self.create_table()
        self.create_status_bar()

        # 状态变量
        self.is_scanning = False

    def create_widgets(self):
        search_frame = tk.Frame(self.root, padx=10, pady=10)
        search_frame.pack(fill="x")

        # 字段选择下拉框
        tk.Label(search_frame, text="字段:").pack(side="left")
        self.field_var = StringVar(value="域名")
        field_combo = ttk.Combobox(
            search_frame,
            textvariable=self.field_var,
            values=["域名", "IP", "端口", "标题", "icon", "body", "自定义"],
            state="readonly",
            width=8
        )
        field_combo.pack(side="left", padx=5)
        field_combo.bind('<<ComboboxSelected>>', self.on_field_change)

        # 目标输入框
        self.target_var = StringVar(value="baidu.com")
        target_entry = tk.Entry(search_frame, textvariable=self.target_var, width=30)
        target_entry.pack(side="left", padx=5)

        # 提示标签
        self.hint_var = StringVar(value="请输入域名，如: baidu.com")
        hint_label = tk.Label(search_frame, textvariable=self.hint_var, fg="gray", font=("Segoe UI", 8))
        hint_label.pack(side="left", padx=5)

        # 引擎选择下拉框
        tk.Label(search_frame, text="引擎:").pack(side="left", padx=(10, 0))
        self.engine_var = StringVar(value="全部")
        engine_combo = ttk.Combobox(
            search_frame,
            textvariable=self.engine_var,
            values=["全部", "FOFA", "Quake"],
            state="readonly",
            width=8
        )
        engine_combo.pack(side="left", padx=5)

        # AI分析勾选框
        self.ai_var = BooleanVar(value=True)
        ai_check = tk.Checkbutton(search_frame, text="启用AI分析", variable=self.ai_var)
        ai_check.pack(side="left", padx=10)

        scan_btn = tk.Button(search_frame, text="查询", command=self.start_scan, bg="#0d6efd", fg="white")
        scan_btn.pack(side="left", padx=5)

        export_btn = tk.Button(search_frame, text="导出 CSV", command=self.export_csv)
        export_btn.pack(side="left", padx=5)

        config_btn = tk.Button(
            search_frame, text="配置API", command=self.open_config_dialog,
            bg="#6c757d", fg="white"
        )
        config_btn.pack(side="right", padx=(0, 10))

        # 状态栏
        self.status_var = StringVar(value="就绪")
        status_label = tk.Label(search_frame, textvariable=self.status_var, fg="blue")
        status_label.pack(side="right")

    def create_table(self):
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("ID", "URL", "IP", "端口", "协议", "标题", "来源", "AI判断")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        col_widths = [40, 200, 120, 60, 60, 200, 80, 80]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        # 绑定双击事件
        self.tree.bind("<Double-1>", self.on_url_double_click)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def on_field_change(self, event=None):
        """当字段选择改变时更新提示"""
        field = self.field_var.get()
        hints = {
            "域名": "请输入域名，如: baidu.com",
            "IP": "请输入IP地址，如: 1.1.1.1",
            "端口": "请输入端口号，如: 80",
            "标题": "请输入页面标题关键词，如: 百度",
            "icon": "请输入icon_hash值，如: 123456789",
            "body": "请输入页面内容关键词，如: nginx",
            "自定义": "请输入完整查询语句"
        }
        self.hint_var.set(hints.get(field, ""))

    def build_search_query(self, field, value, engine):
        """根据字段、值和引擎构建查询语法"""
        if not value.strip():
            return ""

        value = value.strip()

        if field == "自定义":
            return value  # 自定义字段直接返回原内容

        if engine == "fofa":
            return self._build_fofa_query(field, value)
        elif engine == "quake":
            return self._build_quake_query(field, value)
        else:
            return ""

    def _build_fofa_query(self, field, value):
        """构建 FOFA 查询语法"""
        field_map = {
            "域名": "domain",
            "IP": "ip",
            "端口": "port",
            "标题": "title",
            "icon": "icon_hash",
            "body": "body"
        }

        fofa_field = field_map.get(field, "domain")

        # 特殊处理 icon_hash 和端口（数字类型）
        if field in ["icon", "端口"] and value.isdigit():
            return f'{fofa_field}="{value}"'
        else:
            return f'{fofa_field}="{value}"'

    def _build_quake_query(self, field, value):
        """构建 Quake 查询语法"""
        if field == "域名":
            return f'domain:"{value}"'
        elif field == "IP":
            return f'ip:"{value}"'
        elif field == "端口":
            if value.isdigit():
                return f'port:{value}'
            else:
                return f'port:"{value}"'
        elif field == "标题":
            return f'title:"{value}"'
        elif field == "icon":
            # Quake 不支持 icon_hash，使用 body 包含
            return f'body:"{value}"'
        elif field == "body":
            return f'body:"{value}"'
        else:
            return f'domain:"{value}"'

    def on_url_double_click(self, event):
        """处理 URL 双击事件"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.tree.item(item)['values']

        if len(values) > 1:
            url = values[1]

            # 确保 URL 有协议前缀
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            try:
                webbrowser.open(url)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开链接: {str(e)}")

    def create_status_bar(self):
        """创建底部状态栏"""
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=5)

        self.status_var = StringVar(value="就绪")
        status_label = tk.Label(status_frame, textvariable=self.status_var, fg="blue", anchor="w")
        status_label.pack(side="left")

    def open_config_dialog(self):
        dialog = ConfigDialog(self.root, self.config)

        # 等待对话框关闭（模态对话框会阻塞直到关闭）
        self.root.wait_window(dialog.dialog)

        # 对话框关闭后重新加载配置
        self.config = load_config()
        if self.config is None:
            self.config = {}

    def start_scan(self):
        if self.is_scanning:
            return

        target = self.target_var.get().strip()
        if not target:
            messagebox.showwarning("错误", "请输入搜索内容")
            return

        # 获取引擎选择
        engine = self.engine_var.get()

        # 检查 API 密钥
        fofa_key = self.config.get('api', {}).get('fofa', {}).get('key', '').strip()
        quake_key = self.config.get('api', {}).get('quake', {}).get('key', '').strip()

        if engine == "FOFA" and not fofa_key:
            messagebox.showwarning("警告", "请先在「配置API」中设置 FOFA API 密钥！")
            return
        elif engine == "Quake" and not quake_key:
            messagebox.showwarning("警告", "请先在「配置API」中设置 Quake API 密钥！")
            return
        elif engine == "全部" and not fofa_key and not quake_key:
            messagebox.showwarning("警告", "请先在「配置API」中设置至少一个 API 密钥！")
            return

        self.is_scanning = True
        self.status_var.set("正在扫描...")
        self.clear_results()

        thread = threading.Thread(target=self.scan_worker, args=(target, engine), daemon=True)
        thread.start()

    def scan_worker(self, target, engine):
        results = []
        field = self.field_var.get()

        if engine in ["全部", "FOFA"]:
            fofa_key = self.config.get('api', {}).get('fofa', {}).get('key', '')
            if fofa_key:
                fofa_query = self.build_search_query(field, target, "fofa")
                if fofa_query:
                    fofa = FofaClient(fofa_key)
                    results.extend(fofa.search_by_query(fofa_query))

        if engine in ["全部", "Quake"]:
            quake_key = self.config.get('api', {}).get('quake', {}).get('key', '')
            if quake_key:
                quake_query = self.build_search_query(field, target, "quake")
                if quake_query:
                    quake = QuakeClient(quake_key)
                    results.extend(quake.search_by_query(quake_query))

        # 去重
        seen = set()
        unique_results = []
        for r in results:
            host = r.get('host', '')
            if host and host not in seen:
                seen.add(host)
                unique_results.append(r)

        # 更新 UI
        self.root.after(0, self.update_results, unique_results)

    def update_results(self, results):
        for i, item in enumerate(results, 1):
            ai_status = "✅有效" if self.ai_var.get() else "-"

            # 构建完整的 URL
            host = item['host']
            port = item['port']
            protocol = item['protocol']

            if port in ['80', '443']:
                display_url = f"{protocol}://{host}"
            else:
                display_url = f"{protocol}://{host}:{port}"

            self.tree.insert("", END, values=(
                i,
                display_url,
                item['ip'],
                item['port'],
                item['protocol'],
                item['title'][:50],
                item['source'],
                ai_status
            ))

        self.status_var.set(f"扫描完成，共发现 {len(results)} 个资产")
        self.is_scanning = False

    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def export_csv(self):
        if not self.tree.get_children():
            messagebox.showinfo("提示", "没有数据可导出")
            return

        try:
            with open("scan_results.csv", "w", encoding="utf-8-sig") as f:
                f.write("ID,URL,IP,端口,协议,标题,来源,AI判断\n")
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    f.write(",".join(str(v) for v in values) + "\n")
            messagebox.showinfo("成功", "结果已导出到 scan_results.csv")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")