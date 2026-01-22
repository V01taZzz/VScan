# src/ui/dir_bruteforce_ui.py
# -*- coding: utf-8 -*-
"""
目录爆破功能界面 - 只包含UI代码
"""

import tkinter as tk
from tkinter import ttk, messagebox, StringVar, END
from src.core.dir_bruteforcer import DirBruteforcer
import threading


class DirBruteforceUI:
    def __init__(self, parent_notebook, main_gui):
        self.parent_notebook = parent_notebook
        self.main_gui = main_gui
        self.root = parent_notebook.winfo_toplevel()

        # 初始化UI状态
        self.is_bruteforcing = False

        # 创建目录爆破标签页
        self.create_tab()

    def create_tab(self):
        """创建目录爆破标签页"""
        self.frame = ttk.Frame(self.parent_notebook)
        self.parent_notebook.add(self.frame, text="目录爆破")

        # 创建 UI 组件
        self.create_widgets()
        self.create_results()
        # 状态栏由主界面管理

    def create_widgets(self):
        """创建目录爆破控件"""
        search_frame = tk.Frame(self.frame, padx=10, pady=10)
        search_frame.pack(fill="x")

        # 目标域名输入
        tk.Label(search_frame, text="目标域名:").pack(side="left")
        self.brute_target_var = StringVar(value="http://baidu.com")
        target_entry = tk.Entry(search_frame, textvariable=self.brute_target_var, width=30)
        target_entry.pack(side="left", padx=5)

        # 字典文件选择
        dict_frame = tk.Frame(search_frame)
        dict_frame.pack(side="left", padx=10)

        tk.Label(dict_frame, text="字典文件:").pack(side="left")
        self.dict_path_var = StringVar(value="")
        dict_entry = tk.Entry(dict_frame, textvariable=self.dict_path_var, width=20)
        dict_entry.pack(side="left", padx=5)

        dict_btn = tk.Button(dict_frame, text="选择", command=self.select_dict_file)
        dict_btn.pack(side="left", padx=2)

        # 线程数设置
        thread_frame = tk.Frame(search_frame)
        thread_frame.pack(side="left", padx=10)

        tk.Label(thread_frame, text="线程数:").pack(side="left")
        self.thread_count_var = StringVar(value="10")
        thread_entry = tk.Entry(thread_frame, textvariable=self.thread_count_var, width=5)
        thread_entry.pack(side="left", padx=5)

        # 控制按钮
        btn_frame = tk.Frame(search_frame)
        btn_frame.pack(side="right")

        self.brute_start_btn = tk.Button(
            btn_frame, text="开始爆破", command=self.start_bruteforce,
            bg="#0d6efd", fg="white"
        )
        self.brute_start_btn.pack(side="left", padx=5)

        self.brute_stop_btn = tk.Button(
            btn_frame, text="停止", command=self.stop_bruteforce,
            bg="#dc3545", fg="white", state="disabled"
        )
        self.brute_stop_btn.pack(side="left", padx=5)

        # 搜索功能
        search_result_frame = tk.Frame(self.frame, padx=10, pady=5)
        search_result_frame.pack(fill="x")

        tk.Label(search_result_frame, text="结果搜索:").pack(side="left")
        self.brute_search_var = StringVar()
        self.brute_search_var.trace('w', self.on_brute_search_change)
        search_entry = tk.Entry(search_result_frame, textvariable=self.brute_search_var, width=30)
        search_entry.pack(side="left", padx=5)

        clear_search_btn = tk.Button(
            search_result_frame, text="清除搜索", command=self.clear_brute_search
        )
        clear_search_btn.pack(side="left", padx=5)

    def select_dict_file(self):
        """选择字典文件"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择字典文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.dict_path_var.set(file_path)

    def create_results(self):
        """创建目录爆破结果表格"""
        table_frame = tk.Frame(self.frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("ID", "URL", "状态码", "长度", "标题")
        self.brute_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        col_widths = [40, 300, 80, 80, 200]
        for col, width in zip(columns, col_widths):
            self.brute_tree.heading(col, text=col)
            self.brute_tree.column(col, width=width, anchor="center")

        # 绑定双击事件
        self.brute_tree.bind("<Double-1>", self.on_brute_url_double_click)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.brute_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.brute_tree.xview)
        self.brute_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.brute_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # 存储所有结果用于搜索
        self.all_brute_results = []
        self.filtered_brute_results = []

    def on_brute_url_double_click(self, event):
        """处理目录爆破结果URL双击事件"""
        selection = self.brute_tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.brute_tree.item(item)['values']

        if len(values) > 1:
            url = values[1]
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开链接: {str(e)}")

    def start_bruteforce(self):
        """开始目录爆破 - UI层"""
        if self.is_bruteforcing:
            return

        target = self.brute_target_var.get().strip()
        if not target:
            messagebox.showwarning("错误", "请输入目标域名")
            return

        dict_path = self.dict_path_var.get().strip()
        if not dict_path:
            messagebox.showwarning("错误", "请选择字典文件")
            return

        try:
            thread_count = int(self.thread_count_var.get())
            if thread_count <= 0 or thread_count > 100:
                messagebox.showwarning("错误", "线程数应在 1-100 之间")
                return
        except ValueError:
            messagebox.showwarning("错误", "线程数必须是数字")
            return

        # 验证目标URL
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target

        # 验证字典文件
        try:
            with open(dict_path, 'r', encoding='utf-8', errors='ignore') as f:
                paths = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if not paths:
                messagebox.showwarning("错误", "字典文件为空或格式不正确")
                return
        except Exception as e:
            messagebox.showwarning("错误", f"读取字典文件失败: {str(e)}")
            return

        # 初始化爆破器
        self.bruteforcer = DirBruteforcer()
        self.is_bruteforcing = True
        self.brute_start_btn.config(state="disabled")
        self.brute_stop_btn.config(state="normal")
        self.update_status(f"开始爆破，共 {len(paths)} 个路径...")
        self.clear_brute_results()

        # 启动爆破
        self.bruteforcer.start_bruteforce(
            target,
            paths,
            thread_count,
            self._on_result_found,
            self.update_status
        )

    def stop_bruteforce(self):
        """停止目录爆破"""
        if hasattr(self, 'bruteforcer'):
            self.bruteforcer.stop_bruteforce()
        self.is_bruteforcing = False
        self.update_status("正在停止...")
        self.brute_start_btn.config(state="normal")
        self.brute_stop_btn.config(state="disabled")

    def _on_result_found(self, result):
        """当发现有效路径时的回调"""
        self.all_brute_results.append(result)
        self.filtered_brute_results.append(result)
        self.update_brute_results()

    def update_brute_results(self):
        """更新目录爆破结果"""
        self.clear_brute_tree()

        for i, result in enumerate(self.filtered_brute_results, 1):
            self.brute_tree.insert("", END, values=(
                i,
                result['url'],
                result['status_code'],
                result['length'],
                result['title']
            ))

    def clear_brute_results(self):
        """清空目录爆破结果"""
        self.all_brute_results = []
        self.filtered_brute_results = []
        self.clear_brute_tree()

    def clear_brute_tree(self):
        """清空目录爆破表格"""
        for item in self.brute_tree.get_children():
            self.brute_tree.delete(item)

    def on_brute_search_change(self, *args):
        """目录爆破结果搜索"""
        search_term = self.brute_search_var.get().lower().strip()

        if not search_term:
            self.filtered_brute_results = self.all_brute_results.copy()
        else:
            self.filtered_brute_results = [
                result for result in self.all_brute_results
                if (search_term in result['url'].lower() or
                    search_term in str(result['status_code']) or
                    search_term in str(result['length']) or
                    search_term in result['title'].lower())
            ]

        self.update_brute_results()

    def clear_brute_search(self):
        """清除目录爆破搜索"""
        self.brute_search_var.set("")
        self.filtered_brute_results = self.all_brute_results.copy()
        self.update_brute_results()

    def update_status(self, message):
        """更新共享状态栏"""
        self.main_gui.update_status(message)

    def set_target_url(self, url):
        """设置目标URL（供外部调用）"""
        if hasattr(self, 'brute_target_var'):
            self.brute_target_var.set(url)