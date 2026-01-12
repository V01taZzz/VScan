# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date:2026/1/12 
版本: 1.0.0
Design by V01ta
"""
import threading
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, StringVar, BooleanVar, END
from ..core.config_manager import load_config, save_config
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

        # 创建 UI
        self.create_menu()
        self.create_widgets()
        self.create_table()

        # 状态变量
        self.is_scanning = False

    def create_menu(self):
        menu_bar = tk.Frame(self.root, bg="#f0f0f0", height=30)
        menu_bar.pack(fill="x", side="top")

        config_btn = tk.Button(
            menu_bar, text="配置API", command=self.open_config_dialog,
            relief="flat", padx=10, pady=2
        )
        config_btn.pack(side="right", padx=10, pady=2)

    def create_widgets(self):
        search_frame = tk.Frame(self.root, padx=10, pady=10)
        search_frame.pack(fill="x")

        tk.Label(search_frame, text="目标域名:").pack(side="left")
        self.target_var = StringVar(value="baidu.com")
        target_entry = tk.Entry(search_frame, textvariable=self.target_var, width=30)
        target_entry.pack(side="left", padx=5)

        self.ai_var = BooleanVar(value=True)
        ai_check = tk.Checkbutton(search_frame, text="启用AI分析", variable=self.ai_var)
        ai_check.pack(side="left", padx=10)

        scan_btn = tk.Button(search_frame, text="查询", command=self.start_scan, bg="#0d6efd", fg="white")
        scan_btn.pack(side="left", padx=5)

        export_btn = tk.Button(search_frame, text="导出 CSV", command=self.export_csv)
        export_btn.pack(side="left", padx=5)

        self.status_var = StringVar(value="就绪")
        status_label = tk.Label(search_frame, textvariable=self.status_var, fg="blue")
        status_label.pack(side="right")

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

    def open_config_dialog(self):
        dialog = Toplevel(self.root)
        dialog.title("API Key配置")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # FOFA 邮箱
        tk.Label(dialog, text="Fofa 邮箱:").grid(row=0, column=0, sticky="w", padx=20, pady=10)
        fofa_email_var = StringVar()
        fofa_email_var.set(self.config['api']['fofa']['email'])
        fofa_email_entry = tk.Entry(dialog, textvariable=fofa_email_var, width=30)
        fofa_email_entry.grid(row=0, column=1, padx=10, pady=10)

        # FOFA Key
        tk.Label(dialog, text="Fofa Key:").grid(row=1, column=0, sticky="w", padx=20, pady=10)
        fofa_key_var = StringVar()
        fofa_key_var.set(self.config['api']['fofa']['key'])
        fofa_key_entry = tk.Entry(dialog, textvariable=fofa_key_var, width=30, show="*")
        fofa_key_entry.grid(row=1, column=1, padx=10, pady=10)

        # Quake Key
        tk.Label(dialog, text="Quake Key:").grid(row=2, column=0, sticky="w", padx=20, pady=10)
        quake_key_var = StringVar()
        quake_key_var.set(self.config['api']['quake']['key'])
        quake_key_entry = tk.Entry(dialog, textvariable=quake_key_var, width=30, show="*")
        quake_key_entry.grid(row=2, column=1, padx=10, pady=10)

        # 显示/隐藏按钮
        def toggle_visibility(entry, btn_text):
            if entry.cget('show') == '*':
                entry.config(show='')
                btn_text.set('隐藏')
            else:
                entry.config(show='*')
                btn_text.set('显示')

        fofa_btn_text = StringVar()
        fofa_btn_text.set("显示")
        fofa_toggle = tk.Button(
            dialog, textvariable=fofa_btn_text,
            command=lambda: toggle_visibility(fofa_key_entry, fofa_btn_text)
        )
        fofa_toggle.grid(row=1, column=2, padx=5)

        quake_btn_text = StringVar()
        quake_btn_text.set("显示")
        quake_toggle = tk.Button(
            dialog, textvariable=quake_btn_text,
            command=lambda: toggle_visibility(quake_key_entry, quake_btn_text)
        )
        quake_toggle.grid(row=2, column=2, padx=5)

        def save_config_action():
            self.config['api']['fofa']['email'] = fofa_email_var.get()
            self.config['api']['fofa']['key'] = fofa_key_var.get()
            self.config['api']['quake']['key'] = quake_key_var.get()
            save_config(self.config)
            messagebox.showinfo("成功", "配置已保存！")
            dialog.destroy()

        tk.Button(dialog, text="保存", command=save_config_action, bg="#28a745", fg="white", width=10).grid(row=3,
                                                                                                            column=1,
                                                                                                            pady=20,
                                                                                                            sticky="e")
        tk.Button(dialog, text="取消", command=dialog.destroy, width=8).grid(row=3, column=0, pady=20, sticky="w")

    def start_scan(self):
        if self.is_scanning:
            return

        target = self.target_var.get().strip()
        if not target:
            messagebox.showwarning("错误", "请输入目标域名")
            return

        self.is_scanning = True
        self.status_var.set("正在扫描...")
        self.clear_results()

        thread = threading.Thread(target=self.scan_worker, args=(target,), daemon=True)
        thread.start()

    def scan_worker(self, target):
        results = []

        # 调用 core 模块
        fofa = FofaClient(
            self.config['api']['fofa']['email'],
            self.config['api']['fofa']['key']
        )
        results.extend(fofa.search_by_domain(target))

        quake = QuakeClient(self.config['api']['quake']['key'])
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
                item['host'],
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