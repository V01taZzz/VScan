# # src/ui/dir_bruteforce_ui.py
# # -*- coding: utf-8 -*-
# """
# 目录爆破功能界面 - 只包含UI代码
# """
#
# import tkinter as tk
# from tkinter import ttk, messagebox, StringVar, END
# from src.core.dir_bruteforcer import DirBruteforcer
# import threading
#
#
# class DirBruteforceUI:
#     def __init__(self, parent_notebook, main_gui):
#         self.parent_notebook = parent_notebook
#         self.main_gui = main_gui
#         self.root = parent_notebook.winfo_toplevel()
#
#         # 初始化UI状态
#         self.is_bruteforcing = False
#
#         # 创建目录爆破标签页
#         self.create_tab()
#
#     def create_tab(self):
#         """创建目录爆破标签页"""
#         self.frame = ttk.Frame(self.parent_notebook)
#         self.parent_notebook.add(self.frame, text="目录爆破")
#
#         # 创建 UI 组件
#         self.create_widgets()
#         self.create_results()
#         # 状态栏由主界面管理
#
#     def create_widgets(self):
#         """创建目录爆破控件"""
#         search_frame = tk.Frame(self.frame, padx=10, pady=10)
#         search_frame.pack(fill="x")
#
#         # 目标域名输入
#         tk.Label(search_frame, text="目标域名:").pack(side="left")
#         self.brute_target_var = StringVar(value="http://baidu.com")
#         target_entry = tk.Entry(search_frame, textvariable=self.brute_target_var, width=30)
#         target_entry.pack(side="left", padx=5)
#
#         # 字典文件选择
#         dict_frame = tk.Frame(search_frame)
#         dict_frame.pack(side="left", padx=10)
#
#         tk.Label(dict_frame, text="字典文件:").pack(side="left")
#         self.dict_path_var = StringVar(value="")
#         dict_entry = tk.Entry(dict_frame, textvariable=self.dict_path_var, width=20)
#         dict_entry.pack(side="left", padx=5)
#
#         dict_btn = tk.Button(dict_frame, text="选择", command=self.select_dict_file)
#         dict_btn.pack(side="left", padx=2)
#
#         # 线程数设置
#         thread_frame = tk.Frame(search_frame)
#         thread_frame.pack(side="left", padx=10)
#
#         tk.Label(thread_frame, text="线程数:").pack(side="left")
#         self.thread_count_var = StringVar(value="10")
#         thread_entry = tk.Entry(thread_frame, textvariable=self.thread_count_var, width=5)
#         thread_entry.pack(side="left", padx=5)
#
#         # 控制按钮
#         btn_frame = tk.Frame(search_frame)
#         btn_frame.pack(side="right")
#
#         self.brute_start_btn = tk.Button(
#             btn_frame, text="开始爆破", command=self.start_bruteforce,
#             bg="#0d6efd", fg="white"
#         )
#         self.brute_start_btn.pack(side="left", padx=5)
#
#         self.brute_stop_btn = tk.Button(
#             btn_frame, text="停止", command=self.stop_bruteforce,
#             bg="#dc3545", fg="white", state="disabled"
#         )
#         self.brute_stop_btn.pack(side="left", padx=5)
#
#         # 搜索功能
#         search_result_frame = tk.Frame(self.frame, padx=10, pady=5)
#         search_result_frame.pack(fill="x")
#
#         tk.Label(search_result_frame, text="结果搜索:").pack(side="left")
#         self.brute_search_var = StringVar()
#         self.brute_search_var.trace('w', self.on_brute_search_change)
#         search_entry = tk.Entry(search_result_frame, textvariable=self.brute_search_var, width=30)
#         search_entry.pack(side="left", padx=5)
#
#         clear_search_btn = tk.Button(
#             search_result_frame, text="清除搜索", command=self.clear_brute_search
#         )
#         clear_search_btn.pack(side="left", padx=5)
#
#     def select_dict_file(self):
#         """选择字典文件"""
#         from tkinter import filedialog
#         file_path = filedialog.askopenfilename(
#             title="选择字典文件",
#             filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
#         )
#         if file_path:
#             self.dict_path_var.set(file_path)
#
#     def create_results(self):
#         """创建目录爆破结果表格"""
#         table_frame = tk.Frame(self.frame)
#         table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
#
#         columns = ("ID", "URL", "状态码", "长度", "标题")
#         self.brute_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
#
#         col_widths = [40, 300, 80, 80, 200]
#         for col, width in zip(columns, col_widths):
#             self.brute_tree.heading(col, text=col)
#             self.brute_tree.column(col, width=width, anchor="center")
#
#         # 绑定双击事件
#         self.brute_tree.bind("<Double-1>", self.on_brute_url_double_click)
#
#         vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.brute_tree.yview)
#         hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.brute_tree.xview)
#         self.brute_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
#
#         self.brute_tree.grid(row=0, column=0, sticky="nsew")
#         vsb.grid(row=0, column=1, sticky="ns")
#         hsb.grid(row=1, column=0, sticky="ew")
#         table_frame.grid_rowconfigure(0, weight=1)
#         table_frame.grid_columnconfigure(0, weight=1)
#
#         # 存储所有结果用于搜索
#         self.all_brute_results = []
#         self.filtered_brute_results = []
#
#     def on_brute_url_double_click(self, event):
#         """处理目录爆破结果URL双击事件"""
#         selection = self.brute_tree.selection()
#         if not selection:
#             return
#
#         item = selection[0]
#         values = self.brute_tree.item(item)['values']
#
#         if len(values) > 1:
#             url = values[1]
#             try:
#                 import webbrowser
#                 webbrowser.open(url)
#             except Exception as e:
#                 messagebox.showerror("错误", f"无法打开链接: {str(e)}")
#
#     def start_bruteforce(self):
#         """开始目录爆破 - UI层"""
#         if self.is_bruteforcing:
#             return
#
#         target = self.brute_target_var.get().strip()
#         if not target:
#             messagebox.showwarning("错误", "请输入目标域名")
#             return
#
#         dict_path = self.dict_path_var.get().strip()
#         if not dict_path:
#             messagebox.showwarning("错误", "请选择字典文件")
#             return
#
#         try:
#             thread_count = int(self.thread_count_var.get())
#             if thread_count <= 0 or thread_count > 100:
#                 messagebox.showwarning("错误", "线程数应在 1-100 之间")
#                 return
#         except ValueError:
#             messagebox.showwarning("错误", "线程数必须是数字")
#             return
#
#         # 验证目标URL
#         if not target.startswith(('http://', 'https://')):
#             target = 'http://' + target
#
#         # 验证字典文件
#         try:
#             with open(dict_path, 'r', encoding='utf-8', errors='ignore') as f:
#                 paths = [line.strip() for line in f if line.strip() and not line.startswith('#')]
#             if not paths:
#                 messagebox.showwarning("错误", "字典文件为空或格式不正确")
#                 return
#         except Exception as e:
#             messagebox.showwarning("错误", f"读取字典文件失败: {str(e)}")
#             return
#
#         # 初始化爆破器
#         self.bruteforcer = DirBruteforcer()
#         self.is_bruteforcing = True
#         self.brute_start_btn.config(state="disabled")
#         self.brute_stop_btn.config(state="normal")
#         self.update_status(f"开始爆破，共 {len(paths)} 个路径...")
#         self.clear_brute_results()
#
#         # 启动爆破
#         self.bruteforcer.start_bruteforce(
#             target,
#             paths,
#             thread_count,
#             self._on_result_found,
#             self.update_status
#         )
#
#     def stop_bruteforce(self):
#         """停止目录爆破"""
#         if hasattr(self, 'bruteforcer'):
#             self.bruteforcer.stop_bruteforce()
#         self.is_bruteforcing = False
#         self.update_status("正在停止...")
#         self.brute_start_btn.config(state="normal")
#         self.brute_stop_btn.config(state="disabled")
#
#     def _on_result_found(self, result):
#         """当发现有效路径时的回调"""
#         self.all_brute_results.append(result)
#         self.filtered_brute_results.append(result)
#         self.update_brute_results()
#
#     def update_brute_results(self):
#         """更新目录爆破结果"""
#         self.clear_brute_tree()
#
#         for i, result in enumerate(self.filtered_brute_results, 1):
#             self.brute_tree.insert("", END, values=(
#                 i,
#                 result['url'],
#                 result['status_code'],
#                 result['length'],
#                 result['title']
#             ))
#
#     def clear_brute_results(self):
#         """清空目录爆破结果"""
#         self.all_brute_results = []
#         self.filtered_brute_results = []
#         self.clear_brute_tree()
#
#     def clear_brute_tree(self):
#         """清空目录爆破表格"""
#         for item in self.brute_tree.get_children():
#             self.brute_tree.delete(item)
#
#     def on_brute_search_change(self, *args):
#         """目录爆破结果搜索"""
#         search_term = self.brute_search_var.get().lower().strip()
#
#         if not search_term:
#             self.filtered_brute_results = self.all_brute_results.copy()
#         else:
#             self.filtered_brute_results = [
#                 result for result in self.all_brute_results
#                 if (search_term in result['url'].lower() or
#                     search_term in str(result['status_code']) or
#                     search_term in str(result['length']) or
#                     search_term in result['title'].lower())
#             ]
#
#         self.update_brute_results()
#
#     def clear_brute_search(self):
#         """清除目录爆破搜索"""
#         self.brute_search_var.set("")
#         self.filtered_brute_results = self.all_brute_results.copy()
#         self.update_brute_results()
#
#     def update_status(self, message):
#         """更新共享状态栏"""
#         self.main_gui.update_status(message)
#
#     def set_target_url(self, url):
#         """设置目标URL（供外部调用）"""
#         if hasattr(self, 'brute_target_var'):
#             self.brute_target_var.set(url)


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

        # 存储每个目标的爆破结果
        self.tab_frames = {}
        self.tab_trees = {}

        # 创建目录爆破标签页
        self.create_tab()

    def create_tab(self):
        """创建目录爆破标签页"""
        self.frame = ttk.Frame(self.parent_notebook)
        self.parent_notebook.add(self.frame, text="目录爆破")

        # 创建 UI 组件
        self.create_widgets()
        self.create_notebook()  # 标签页容器用于结果展示

    def create_widgets(self):
        """创建目录爆破控件（移除搜索功能）"""
        search_frame = tk.Frame(self.frame, padx=10, pady=10)
        search_frame.pack(fill="x")

        # 目标域名输入（多行文本框）
        tk.Label(search_frame, text="目标域名:").pack(side="left")
        self.target_text = tk.Text(search_frame, height=3, width=30)
        self.target_text.pack(side="left", padx=5)
        self.target_text.insert("1.0", "http://baidu.com")
        self.target_text.bind('<FocusIn>', self.on_target_focus_in)
        self.target_text.bind('<FocusOut>', self.on_target_focus_out)
        self.target_text.config(fg="gray")

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

    def on_target_focus_in(self, event):
        """目标输入框获得焦点"""
        if self.target_text.get("1.0", "end-1c") == "http://baidu.com":
            self.target_text.delete("1.0", "end")
            self.target_text.config(fg="black")

    def on_target_focus_out(self, event):
        """目标输入框失去焦点"""
        if not self.target_text.get("1.0", "end-1c").strip():
            self.target_text.insert("1.0", "http://baidu.com")
            self.target_text.config(fg="gray")

    def select_dict_file(self):
        """选择字典文件"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择字典文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.dict_path_var.set(file_path)

    def create_notebook(self):
        """创建标签页容器用于结果展示"""
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def get_targets_from_text(self):
        """从多行文本框获取目标列表"""
        content = self.target_text.get("1.0", "end-1c").strip()
        if not content:
            return []

        # 如果是占位符内容，返回空列表
        if content == "http://baidu.com":
            return []

        # 按行分割，过滤空行
        targets = [line.strip() for line in content.split('\n') if line.strip()]
        return targets

    def start_bruteforce(self):
        """开始目录爆破 - 支持多目标"""
        if self.is_bruteforcing:
            return

        targets = self.get_targets_from_text()
        if not targets:
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

        # 验证并标准化目标URL
        valid_targets = []
        for target in targets:
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
            valid_targets.append(target)

        self.is_bruteforcing = True
        self.brute_start_btn.config(state="disabled")
        self.brute_stop_btn.config(state="normal")
        self.update_status(f"开始爆破 {len(valid_targets)} 个目标...")
        self.clear_all_results()

        # 启动爆破线程
        brute_thread = threading.Thread(
            target=self.batch_bruteforce_worker,
            args=(valid_targets, paths, thread_count),
            daemon=True
        )
        brute_thread.start()

    def batch_bruteforce_worker(self, targets, paths, thread_count):
        """批量爆破工作线程"""
        all_results = {}

        for i, target in enumerate(targets):
            try:
                self.root.after(0, lambda t=target, idx=i:
                self.update_status(f"正在爆破 {idx + 1}/{len(targets)}: {t}"))

                # 为每个目标创建独立的爆破器
                bruteforcer = DirBruteforcer()
                results = []

                # 执行爆破
                threads, collector = bruteforcer.start_bruteforce(
                    target,
                    paths,
                    thread_count,
                    lambda result: results.append(result),
                    lambda msg: None  # 不使用状态回调
                )

                # 等待完成
                for t in threads:
                    t.join(timeout=30)

                all_results[target] = results

            except Exception as e:
                print(f"爆破 {target} 失败: {e}")
                all_results[target] = []

        # 更新 UI
        self.root.after(0, self.update_batch_results, all_results)

    def update_batch_results(self, all_results):
        """更新批量爆破结果到标签页"""
        # 清除现有标签页
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        self.tab_frames.clear()
        self.tab_trees.clear()

        # 为每个目标创建标签页
        for target, results in all_results.items():
            if results:  # 只为有结果的目标创建标签页
                self.create_result_tab(target, results)

        # 如果没有结果，创建一个空标签页
        if not all_results or not any(results for results in all_results.values()):
            empty_frame = ttk.Frame(self.notebook)
            self.notebook.add(empty_frame, text="无结果")
            label = tk.Label(empty_frame, text="未找到任何有效路径", fg="gray")
            label.pack(expand=True)

        self.update_status(
            f"爆破完成，{len(all_results)} 个目标共发现 {sum(len(r) for r in all_results.values())} 个有效路径")
        self.is_bruteforcing = False
        self.brute_start_btn.config(state="normal")
        self.brute_stop_btn.config(state="disabled")

    def create_result_tab(self, target, results):
        """为单个目标创建结果标签页（带排序功能）"""
        tab_frame = ttk.Frame(self.notebook)
        tab_name = self.truncate_target_name(target)
        self.notebook.add(tab_frame, text=tab_name)

        # 存储引用
        self.tab_frames[target] = tab_frame
        self.tab_trees[target] = None

        # 创建表格
        columns = ("ID", "URL", "状态码", "长度", "标题")
        tree = ttk.Treeview(tab_frame, columns=columns, show="headings")

        col_widths = [40, 300, 80, 80, 200]
        for col, width in zip(columns, col_widths):
            # 为状态码列添加排序绑定
            if col == "状态码":
                tree.heading(col, text=col, command=lambda: self.sort_by_status_code(target))
            else:
                tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        # 绑定双击事件
        tree.bind("<Double-1>", self.on_brute_url_double_click)

        # 创建滚动条
        vsb = ttk.Scrollbar(tab_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tab_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tab_frame.grid_rowconfigure(0, weight=1)
        tab_frame.grid_columnconfigure(0, weight=1)

        # 添加关闭按钮（右上角）
        close_btn = tk.Button(
            tab_frame,
            text="×",
            command=lambda t=target: self.close_tab(t),
            width=2,
            height=1,
            font=("Arial", 10, "bold"),
            relief="flat",
            fg="white",
            bg="#dc3545",
            activebackground="#c82333"
        )
        close_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)

        # 更新存储引用
        self.tab_trees[target] = tree

        # 插入数据并按状态码升序排序
        self.insert_results_to_tree(tree, results)
        self.sort_by_status_code(target, ascending=True)

    def sort_by_status_code(self, target, ascending=None):
        """按状态码排序"""
        if target not in self.tab_trees:
            return

        tree = self.tab_trees[target]

        # 获取当前排序状态
        if ascending is None:
            # 切换排序方向
            if not hasattr(self, '_status_sort_ascending'):
                self._status_sort_ascending = {}
            current_ascending = self._status_sort_ascending.get(target, True)
            ascending = not current_ascending
            self._status_sort_ascending[target] = ascending
        else:
            # 设置指定排序方向
            if not hasattr(self, '_status_sort_ascending'):
                self._status_sort_ascending = {}
            self._status_sort_ascending[target] = ascending

        # 获取所有项目
        items = [(tree.set(item, "状态码"), item) for item in tree.get_children()]

        # 排序（处理非数字状态码）
        def safe_int(x):
            try:
                return int(x)
            except ValueError:
                return 999  # 非数字放在最后

        items.sort(key=lambda x: safe_int(x[0]), reverse=not ascending)

        # 重新排列项目
        for index, (val, item) in enumerate(items):
            tree.move(item, '', index)

    def truncate_target_name(self, target, max_length=15):
        """截断目标名称以适应标签页"""
        if len(target) <= max_length:
            return target
        return target[:max_length - 3] + "..."

    def insert_results_to_tree(self, tree, results):
        """将结果插入到指定的表格中"""
        for i, result in enumerate(results, 1):
            tree.insert("", END, values=(
                i,
                result['url'],
                result['status_code'],
                result['length'],
                result['title']
            ))

    def on_brute_url_double_click(self, event):
        """处理目录爆破结果URL双击事件"""
        # 找到当前选中的标签页
        current_tab = self.notebook.select()
        if not current_tab:
            return

        # 获取当前标签页的 treeview
        tree = None
        for target, frame in self.tab_frames.items():
            if str(frame) == current_tab:
                tree = self.tab_trees[target]
                break

        if not tree:
            return

        selection = tree.selection()
        if not selection:
            return

        item = selection[0]
        values = tree.item(item)['values']

        if len(values) > 1:
            url = values[1]
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开链接: {str(e)}")

    def stop_bruteforce(self):
        """停止目录爆破"""
        self.is_bruteforcing = False
        self.update_status("正在停止...")

    # def on_brute_search_change(self, *args):
    #     """目录爆破结果搜索"""
    #     search_term = self.brute_search_var.get().lower().strip()
    #
    #     # 搜索所有标签页的结果
    #     if not search_term:
    #         # 显示所有结果
    #         for target, tree in self.tab_trees.items():
    #             self.refresh_tab_results(target)
    #     else:
    #         # 过滤结果
    #         for target, tree in self.tab_trees.items():
    #             self.filter_tab_results(target, search_term)

    # def refresh_tab_results(self, target):
    #     """刷新指定标签页的所有结果"""
    #     if target in self.tab_trees:
    #         tree = self.tab_trees[target]
    #         # 这里需要存储原始结果，暂时简化处理
    #         pass

    # def filter_tab_results(self, target, search_term):
    #     """过滤指定标签页的结果"""
    #     if target in self.tab_trees:
    #         tree = self.tab_trees[target]
    #         # 简化处理：清空并重新插入匹配的结果
    #         pass

    # def clear_brute_search(self):
    #     """清除目录爆破搜索"""
    #     self.brute_search_var.set("")

    def clear_all_results(self):
        """清除所有标签页结果"""
        for tab in list(self.tab_frames.keys()):
            self.close_tab(tab)

    def close_tab(self, target):
        """关闭指定的标签页"""
        try:
            if target in self.tab_frames:
                self.notebook.forget(self.tab_frames[target])
                del self.tab_frames[target]
                if target in self.tab_trees:
                    del self.tab_trees[target]
        except Exception as e:
            print(f"关闭标签页失败: {e}")

    def update_status(self, message):
        """更新共享状态栏"""
        self.main_gui.update_status(message)

    def set_target_urls(self, urls):
        """接收来自空间测绘页面的多个URL"""
        if isinstance(urls, str):
            urls = [urls]

        # 清空当前输入框并设置新内容
        self.target_text.delete("1.0", "end")
        self.target_text.insert("1.0", "\n".join(urls))
        self.target_text.config(fg="black")