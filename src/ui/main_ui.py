# ui/main_ui.py
# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan (无影风格)
Date: 2026/1/13
版本: 1.4.0
Design by V01ta
"""
import threading
import tkinter as tk
from tkinter import ttk, messagebox, StringVar, BooleanVar, END
from src.ui.config_ui import ConfigDialog
from src.core.config_manager import load_config
from src.core.fofa_client import FofaClient
from src.core.quake_client import QuakeClient

# ui/main_ui.py
# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date: 2026/1/13
版本: 1.2.0
Design by V01ta
"""
import threading
import tkinter as tk
from tkinter import ttk, messagebox, StringVar, BooleanVar, END
from .config_ui import ConfigDialog
from ..core.config_manager import load_config
from ..core.fofa_client import FofaClient
from ..core.quake_client import QuakeClient


class SecurityScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("安全空间测绘 - tkinter 版")
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

        tk.Label(search_frame, text="目标域名:").pack(side="left")
        self.target_var = StringVar(value="baidu.com")
        target_entry = tk.Entry(search_frame, textvariable=self.target_var, width=30)
        target_entry.pack(side="left", padx=5)

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

        self.ai_var = BooleanVar(value=True)
        ai_check = tk.Checkbutton(search_frame, text="启用AI分析", variable=self.ai_var)
        ai_check.pack(side="left", padx=10)

        scan_btn = tk.Button(search_frame, text="查询", command=self.start_scan, bg="#0d6efd", fg="white")
        scan_btn.pack(side="left", padx=5)

        export_btn = tk.Button(search_frame, text="导出 CSV", command=self.export_csv)
        export_btn.pack(side="left", padx=5)

        # 配置按钮
        config_btn = tk.Button(
            search_frame, text="配置API", command=self.open_config_dialog,
            bg="#6c757d", fg="white"
        )
        config_btn.pack(side="right", padx=(0, 10))

    def create_table(self):
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("ID", "URL", "IP", "端口", "协议", "标题", "来源", "AI判断")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        col_widths = [40, 150, 120, 60, 60, 200, 80, 80]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def create_status_bar(self):
        """创建底部状态栏"""
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=5)

        self.status_var = StringVar(value="就绪")
        status_label = tk.Label(status_frame, textvariable=self.status_var, fg="blue", anchor="w")
        status_label.pack(side="left")

    def open_config_dialog(self):
        ConfigDialog(self.root, self.config)
        # 重新加载配置
        self.config = load_config()
        if self.config is None:
            self.config = {}

    def start_scan(self):
        if self.is_scanning:
            return

        target = self.target_var.get().strip()
        if not target:
            messagebox.showwarning("错误", "请输入目标域名")
            return

        # 检查 API 密钥是否已配置
        engine = self.engine_var.get()
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

        if engine in ["全部", "FOFA"]:
            fofa_key = self.config.get('api', {}).get('fofa', {}).get('key', '')
            if fofa_key:
                fofa = FofaClient(fofa_key)
                results.extend(fofa.search_by_domain(target))

        if engine in ["全部", "Quake"]:
            quake_key = self.config.get('api', {}).get('quake', {}).get('key', '')
            if quake_key:
                quake = QuakeClient(quake_key)
                results.extend(quake.search_by_domain(target))

        # 去重
        seen = set()
        unique_results = []
        for r in results:
            host = r['host']
            if host and host not in seen:
                seen.add(host)
                unique_results.append(r)

        # 更新 UI
        self.root.after(0, self.update_results, unique_results)

    def update_results(self, results):
        for i, item in enumerate(results, 1):
            ai_status = "✅有效" if self.ai_var.get() else "-"
            self.tree.insert("", END, values=(
                i,
                item['host'],  # 注意：这里还是 host，不是完整 URL
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