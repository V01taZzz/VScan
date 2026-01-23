# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
Date:2026/1/22 
版本: 1.0.0
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

class SpaceMappingUI:
    def __init__(self, parent_notebook, main_gui):
        self.parent_notebook = parent_notebook
        self.main_gui = main_gui
        self.root = parent_notebook.winfo_toplevel()

        # 初始化基本属性
        self.is_scanning = False
        self.ollama_available = False  # 默认值
        self.ollama_model = None

        # 加载配置
        self.config = load_config()
        if self.config is None:
            self.config = {}

        # 检查 Ollama 是否可用
        try:
            self.ollama_available = self.check_ollama_available()
        except Exception as e:
            print(f"Ollama 检查失败: {e}")
            self.ollama_available = False

        # 创建空间测绘标签页
        self.create_tab()

    def create_tab(self):
        """创建空间测绘标签页"""
        self.frame = ttk.Frame(self.parent_notebook)
        self.parent_notebook.add(self.frame, text="空间测绘")

        # 创建 UI 组件
        self.create_widgets()
        self.create_notebook()  # ✅ 正确：使用 create_notebook

    def on_target_focus_in(self, event):
        """目标输入框获得焦点 - 改进版"""
        # 获取当前输入框内容
        current_content = self.target_text.get("1.0", "end-1c")

        # 定义所有可能的占位符
        all_placeholders = [
            "请输入域名，如: baidu.com",
            "请输入IP地址，如: 1.1.1.1",
            "请输入端口号，如: 80",
            "请输入页面标题关键词，如: 百度",
            "请输入icon_hash值，如: 123456789",
            "请输入页面内容关键词，如: nginx",
            "请输入完整查询语句"
        ]

        # 如果当前内容等于任何一个占位符，就清空输入框
        if current_content in all_placeholders:
            self.target_text.delete("1.0", "end")
            self.target_text.config(fg="black")

    def on_target_focus_out(self, event):
        """目标输入框失去焦点 - 改进版"""
        # 获取当前输入框内容（去除首尾空白）
        current_content = self.target_text.get("1.0", "end-1c").strip()

        # 如果输入框为空，显示当前字段对应的占位符
        if not current_content:
            current_placeholder = self.get_current_placeholder()
            self.target_text.delete("1.0", "end")
            self.target_text.insert("1.0", current_placeholder)
            self.target_text.config(fg="gray")

    def get_current_placeholder(self):
        """获取当前字段对应的占位符"""
        field = self.field_var.get()
        placeholders = {
            "域名": "请输入域名，如: baidu.com",
            "IP": "请输入IP地址，如: 1.1.1.1",
            "端口": "请输入端口号，如: 80",
            "标题": "请输入页面标题关键词，如: 百度",
            "icon": "请输入icon_hash值，如: 123456789",
            "body": "请输入页面内容关键词，如: nginx",
            "自定义": "请输入完整查询语句"
        }
        return placeholders.get(field, "请输入域名，如: baidu.com")

    def create_widgets(self):
        """创建空间测绘控件"""
        search_frame = tk.Frame(self.frame, padx=10, pady=10)
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

        # 目标输入框（多行文本框）
        self.target_text = tk.Text(search_frame, height=3, width=30)
        self.target_text.pack(side="left", padx=5)
        self.target_text.insert("1.0", "请输入域名，如: baidu.com")
        self.target_text.bind('<FocusIn>', self.on_target_focus_in)
        self.target_text.bind('<FocusOut>', self.on_target_focus_out)
        self.target_text.config(fg="gray")

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

        # AI分析勾选框 - 添加安全检查
        if hasattr(self, 'ollama_available') and self.ollama_available:
            ai_text = "启用AI分析（Ollama）"
            ai_state = "normal"
        else:
            ai_text = "启用AI分析（需Ollama）"
            ai_state = "disabled"

        self.ai_var = BooleanVar(value=getattr(self, 'ollama_available', False))
        ai_check = tk.Checkbutton(
            search_frame,
            text=ai_text,
            variable=self.ai_var,
            state=ai_state
        )
        ai_check.pack(side="left", padx=10)

        scan_btn = tk.Button(search_frame, text="查询", command=self.start_scan, bg="#0d6efd", fg="white")
        scan_btn.pack(side="left", padx=5)

        export_btn = tk.Button(search_frame, text="导出 CSV", command=self.export_csv)
        export_btn.pack(side="left", padx=5)

        # 导入Excel按钮
        import_excel_btn = tk.Button(
            search_frame, text="导入Excel", command=self.import_excel,
            bg="#ffc107", fg="black"
        )
        import_excel_btn.pack(side="right", padx=(0, 10))

        # 配置API按钮
        config_btn = tk.Button(
            search_frame, text="配置API", command=self.open_config_dialog,
            bg="#6c757d", fg="white"
        )
        config_btn.pack(side="right", padx=(0, 10))


    def create_notebook(self):
        """创建标签页容器"""
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 存储每个标签页的表格
        self.tab_frames = {}
        self.tab_trees = {}

        # 创建右键菜单
        # self.create_context_menu()


    def update_status(self, message):
        """更新共享状态栏"""
        self.main_gui.update_status(message)


    def on_field_change(self, event=None):
        """当字段选择改变时立即更新占位符"""
        # 定义所有可能的占位符
        all_placeholders = [
            "请输入域名，如: baidu.com",
            "请输入IP地址，如: 1.1.1.1",
            "请输入端口号，如: 80",
            "请输入页面标题关键词，如: 百度",
            "请输入icon_hash值，如: 123456789",
            "请输入页面内容关键词，如: nginx",
            "请输入完整查询语句"
        ]

        # 获取当前输入框内容
        current_content = self.target_text.get("1.0", "end-1c")

        # 获取新字段对应的占位符
        field = self.field_var.get()
        placeholders = {
            "域名": "请输入域名，如: baidu.com",
            "IP": "请输入IP地址，如: 1.1.1.1",
            "端口": "请输入端口号，如: 80",
            "标题": "请输入页面标题关键词，如: 百度",
            "icon": "请输入icon_hash值，如: 123456789",
            "body": "请输入页面内容关键词，如: nginx",
            "自定义": "请输入完整查询语句"
        }
        new_placeholder = placeholders.get(field, "请输入域名，如: baidu.com")

        # 如果当前内容是任何一个占位符，就立即替换为新占位符
        if current_content in all_placeholders:
            self.target_text.delete("1.0", "end")
            self.target_text.insert("1.0", new_placeholder)
            self.target_text.config(fg="gray")
        # 如果输入框为空，也设置新占位符
        elif not current_content.strip():
            self.target_text.delete("1.0", "end")
            self.target_text.insert("1.0", new_placeholder)
            self.target_text.config(fg="gray")
        # 如果用户已经输入了真实内容，保持不变
        else:
            # 保持用户输入的内容不变
            pass

    def build_search_query(self, field, value, engine):
        """根据字段、值和引擎构建查询语法（适配多行输入）"""
        if not value.strip():
            return ""

        value = value.strip()
        # 检查是否等于当前占位符（保持原有逻辑）
        if value == self.get_current_placeholder():
            return ""

        if field == "自定义":
            return value

        if engine == "fofa":
            return self._build_fofa_query(field, value)
        elif engine == "quake":
            return self._build_quake_query(field, value)
        else:
            return ""

    def _build_quake_query(self, field, value):
        """构建 Quake 查询语法（改进版）"""
        # 字段映射
        field_map = {
            "域名": "domain",
            "IP": "ip",
            "端口": "port",
            "标题": "title",
            "icon": "icon_hash",  # Quake 支持 icon_hash
            "body": "body"
        }

        quake_field = field_map.get(field, "domain")

        # 特殊处理：端口为数字时不用引号
        if field == "端口" and value.isdigit():
            return f'{quake_field}:{value}'
        else:
            return f'{quake_field}:"{value}"'

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

    def on_url_double_click(self, event):
        """处理 URL 双击事件（通用版本）"""
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

        # 修正：URL 是第3列（索引2），不是第2列（索引1）
        if len(values) > 2:
            url = values[2]  # ← 修正这里！
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

    def import_excel(self):
        """从Excel文件导入目标字段（简化版）"""
        try:
            import pandas as pd
            from tkinter import filedialog

            file_path = filedialog.askopenfilename(
                title="选择Excel文件",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )

            if not file_path:
                return

            # 读取Excel文件的第一列
            df = pd.read_excel(file_path, header=None)
            targets = [str(val).strip() for val in df.iloc[:, 0] if pd.notna(val) and str(val).strip()]

            if not targets:
                messagebox.showwarning("警告", "未找到有效的目标字段！")
                return

            self.target_text.delete("1.0", "end")
            self.target_text.insert("1.0", "\n".join(targets))
            self.target_text.config(fg="black")

            messagebox.showinfo("成功", f"成功导入 {len(targets)} 个目标字段！")

        except ImportError:
            messagebox.showerror("错误", "缺少必要的依赖库！\n请运行: pip install pandas openpyxl")
        except Exception as e:
            messagebox.showerror("错误", f"导入Excel失败: {str(e)}")

    def get_targets_from_text(self):
        """从多行文本框获取目标列表"""
        content = self.target_text.get("1.0", "end-1c").strip()
        if not content:
            return []

        # 如果是占位符内容，返回空列表
        if content == self.get_current_placeholder():
            return []

        # 按行分割，过滤空行
        targets = [line.strip() for line in content.split('\n') if line.strip()]
        return targets

    def start_scan(self):
        if self.is_scanning:
            return

        # 获取所有目标
        targets = self.get_targets_from_text()
        if not targets:
            messagebox.showwarning("错误", "请输入搜索内容")
            return

        # 检查 API 密钥
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
        if len(targets) == 1:
            self.update_status("正在扫描...")
        else:
            self.update_status(f"正在扫描 {len(targets)} 个目标...")
            # self.clear_all_results()

        thread = threading.Thread(target=self.batch_scan_worker, args=(targets, engine), daemon=True)
        thread.start()

    def batch_scan_worker(self, targets, engine):
        """批量扫描工作线程"""
        all_results = {}

        for i, target in enumerate(targets):
            try:
                if len(targets) > 1:
                    self.root.after(0, lambda t=target, idx=i:
                    self.update_status(f"正在扫描 {idx + 1}/{len(targets)}: {t}"))

                results = self.scan_single_target(target, engine)
                all_results[target] = results

            except Exception as e:
                print(f"扫描 {target} 失败: {e}")
                all_results[target] = []

        # 所有扫描完成后更新 UI
        self.root.after(0, self.update_batch_results, all_results)

    def scan_single_target(self, target, engine):
        """扫描单个目标"""
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

        return unique_results

    def update_batch_results(self, all_results):
        """更新批量扫描结果到标签页（保留历史结果）"""
        # ❌ 不再清除现有标签页
        # for tab in self.notebook.tabs():
        #     self.notebook.forget(tab)
        #
        # self.tab_frames.clear()
        # self.tab_trees.clear()

        # 为每个目标创建标签页（如果不存在的话）
        for target, results in all_results.items():
            if results:  # 只为有结果的目标创建标签页
                # 检查是否已经存在同名标签页
                tab_exists = False
                for existing_target in list(self.tab_frames.keys()):
                    if existing_target == target:
                        tab_exists = True
                        # 如果已存在，先关闭旧的标签页
                        self.close_tab(existing_target)
                        break

                # 创建新的标签页
                self.create_result_tab(target, results)

        # 如果没有结果，创建一个可关闭的空标签页
        if not all_results or not any(results for results in all_results.values()):
            empty_frame = ttk.Frame(self.notebook)
            # 为避免重复，使用带时间戳的标签名
            import time
            timestamp = time.strftime("%H:%M:%S")
            self.notebook.add(empty_frame, text=f"无结果({timestamp})")

            # 添加关闭按钮
            close_btn = tk.Button(
                empty_frame,
                text="×",
                command=lambda f=empty_frame: self.notebook.forget(f),
                width=2,
                height=1,
                font=("Arial", 10, "bold"),
                relief="flat",
                fg="white",
                bg="#dc3545"
            )
            close_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)

            label = tk.Label(empty_frame, text="未找到任何资产", fg="gray")
            label.pack(expand=True)

        # 更新状态
        total_targets = len(all_results)
        total_assets = sum(len(results) for results in all_results.values())
        if total_targets == 1:
            self.update_status(f"扫描完成，共发现 {total_assets} 个资产")
        else:
            self.update_status(f"扫描完成，{total_targets} 个目标共发现 {total_assets} 个资产")
        self.is_scanning = False

    def send_selected_url_to_bruteforce(self, tree, item):
        """发送选中的URL到目录爆破功能"""
        values = tree.item(item)['values']

        if len(values) > 1:
            url = values[1]
            # 确保URL有协议前缀
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            # 切换到目录爆破标签页并设置目标
            self.main_gui.switch_to_bruteforce_tab(url)


    def on_url_right_click(self, event):
        """处理 URL 右键点击事件"""
        # 找到当前选中的标签页
        current_tab = self.notebook.select()
        if not current_tab:
            return

        # 获取当前标签页的 treeview
        tree = None
        current_target = None
        for target, frame in self.tab_frames.items():
            if str(frame) == current_tab:
                tree = self.tab_trees[target]
                current_target = target
                break

        if not tree:
            return

        # 识别点击的项目
        item = tree.identify_row(event.y)
        if not item:
            return


        # 创建右键菜单
        context_menu = tk.Menu(self.root, tearoff=0)

        # 添加复制选项（复制当前右键点击的URL）
        values = tree.item(item)['values']
        if len(values) > 2:
            context_menu.add_command(
                label="复制",
                command=lambda: self.copy_single_url(values[2])  # ← 修正这里
            )

        # 添加发送到目录爆破选项（发送所有勾选的URL）
        context_menu.add_command(
            label="发送到目录爆破",
            command=self.send_selected_urls_to_bruteforce
        )

        # 添加全选/取消全选选项
        if current_target:
            context_menu.add_separator()
            context_menu.add_command(
                label="全选",
                command=lambda: self.select_all_urls(current_target)
            )
            context_menu.add_command(
                label="取消全选",
                command=lambda: self.unselect_all_urls(current_target)
            )

        # 显示右键菜单
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def copy_single_url(self, url):
        """复制单个URL到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        self.root.update()
        self.update_status(f"已复制: {url}")

    def select_all_urls(self, target):
        """全选指定标签页的所有URL"""
        if target in self.tab_trees:
            tree = self.tab_trees[target]
            items = tree.get_children()
            for item in items:
                values = tree.item(item)['values']
                if len(values) > 0:
                    values[0] = "✓"
                    tree.item(item, values=values)

    def unselect_all_urls(self, target):
        """取消全选指定标签页的所有URL"""
        if target in self.tab_trees:
            tree = self.tab_trees[target]
            items = tree.get_children()
            for item in items:
                values = tree.item(item)['values']
                if len(values) > 0:
                    values[0] = ""
                    tree.item(item, values=values)

    def on_checkbox_click(self, event):
        """处理勾选框点击事件 - 简化版本"""
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

        # 获取点击位置的列索引
        def get_column_index(tree, x):
            total_width = 0
            for i, col in enumerate(tree["columns"]):
                col_width = tree.column(col, 'width')
                if total_width <= x <= total_width + col_width:
                    return i
                total_width += col_width
            return -1

        # 获取点击的列索引
        col_index = get_column_index(tree, event.x)
        item = tree.identify_row(event.y)

        # 如果点击的是第一列（勾选框列）且有选中项目
        if col_index == 0 and item:
            values = tree.item(item)['values']
            if len(values) > 0:
                current_value = values[0]
                new_value = "✓" if current_value != "✓" else ""
                values[0] = new_value
                tree.item(item, values=values)

    def create_result_tab(self, target, results):
        """为单个目标创建结果标签页（带真正的勾选框）"""
        # 创建标签页框架
        tab_frame = ttk.Frame(self.notebook)
        tab_name = self.truncate_target_name(target)
        self.notebook.add(tab_frame, text=tab_name)

        # 存储引用
        self.tab_frames[target] = tab_frame
        self.tab_trees[target] = None

        # 创建表格 - 添加勾选框列
        columns = ("Select", "ID", "URL", "IP", "端口", "协议", "标题", "来源", "AI判断")
        tree = ttk.Treeview(tab_frame, columns=columns, show="headings")

        col_widths = [40, 40, 200, 120, 60, 60, 200, 80, 80]
        for i, (col, width) in enumerate(zip(columns, col_widths)):
            if col == "Select":
                # 勾选框列设置为可点击
                tree.heading(col, text=col)
                tree.column(col, width=width, anchor="center")
                # 绑定勾选框点击事件
                tree.bind("<Button-1>", self.on_checkbox_click)
            else:
                tree.heading(col, text=col)
                tree.column(col, width=width, anchor="center")

        # 绑定双击事件
        tree.bind("<Double-1>", self.on_url_double_click)

        # 绑定右键事件
        tree.bind("<Button-3>", self.on_url_right_click)

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

        # 插入数据
        self.insert_results_to_tree(tree, results, target)

    def truncate_target_name(self, target, max_length=15):
        """截断目标名称以适应标签页"""
        if len(target) <= max_length:
            return target
        return target[:max_length - 3] + "..."

    def insert_results_to_tree(self, tree, results, target):
        """将结果插入到指定的表格中（包含勾选框）"""
        # 如果启用了 AI 分析，先执行 AI 分析
        if self.ai_var.get() and self.ollama_available:
            # 在后台线程中执行 AI 分析
            ai_thread = threading.Thread(
                target=self.perform_ai_analysis_for_tab,
                args=(results, tree, target),
                daemon=True
            )
            ai_thread.start()
        else:
            # 直接显示结果
            self._insert_results_without_ai(tree, results)


    def _insert_results_without_ai(self, tree, results):
        """不使用 AI 分析直接插入结果（包含勾选框）"""
        for i, item in enumerate(results, 1):
            # 构建 URL 显示
            host = item['host']
            port = item['port']
            protocol = item['protocol']

            if port in ['80', '443']:
                display_url = f"{protocol}://{host}"
            else:
                display_url = f"{protocol}://{host}:{port}"

            # 插入带勾选框的数据
            tree.insert("", END, values=(
                "",  # 勾选框列（空，由用户勾选）
                i,
                display_url,
                item['ip'],
                item['port'],
                item['protocol'],
                item['title'][:50],
                item['source'],
                "✅有效" if self.ai_var.get() else "-"
            ))


    def _insert_results_with_ai(self, tree, results):
        """使用 AI 分析结果插入数据（包含勾选框）"""
        for i, item in enumerate(results, 1):
            # AI 分析结果处理
            if 'ai_analysis' in item:
                ai_result = item['ai_analysis']
                tags = ai_result.get('tags', [])

                if tags:
                    display_tags = " ".join(tags[:3])
                    ai_status = f"🏷️{display_tags}"
                else:
                    ai_status = "✅AI分析"
            else:
                ai_status = "✅有效" if self.ai_var.get() else "-"

            # 构建 URL 显示
            host = item['host']
            port = item['port']
            protocol = item['protocol']

            if port in ['80', '443']:
                display_url = f"{protocol}://{host}"
            else:
                display_url = f"{protocol}://{host}:{port}"

            # 插入带勾选框的数据
            tree.insert("", END, values=(
                "",  # 勾选框列
                i,
                display_url,
                item['ip'],
                item['port'],
                item['protocol'],
                item['title'][:50],
                item['source'],
                ai_status
            ))

    def perform_ai_analysis_for_tab(self, results, tree, target):
        """为特定标签页执行 AI 分析（带URL进度显示）"""
        try:
            from src.core.ollama_analyzer import OllamaAnalyzer

            model_name = getattr(self, 'ollama_model', 'qwen3-coder:30b')
            analyzer = OllamaAnalyzer(model=model_name)

            # 执行 AI 分析
            for i, item in enumerate(results):
                host = item.get('host', 'N/A')
                title = item.get('title', 'N/A')

                # 构建完整的URL用于显示
                port = item.get('port', '80')
                protocol = item.get('protocol', 'http')
                if port in ['80', '443']:
                    display_url = f"{protocol}://{host}"
                else:
                    display_url = f"{protocol}://{host}:{port}"

                # 更新状态栏显示当前分析的URL
                self.root.after(0, lambda url=display_url, idx=i + 1, total=len(results):
                self.update_status(f"AI分析中 ({idx}/{total}): {url}"))

                ai_result = analyzer.analyze_website(item)
                item['ai_analysis'] = ai_result

            # 在主线程中更新 UI
            self.root.after(0, self._insert_results_with_ai, tree, results)
            self.root.after(0, lambda: self.update_status(f"AI分析完成，共分析 {len(results)} 个网站"))

        except Exception as e:
            print(f"AI 分析异常: {e}")
            self.root.after(0, lambda: self.update_status("AI分析失败"))
            self.root.after(0, self._insert_results_without_ai, tree, results)

    def close_tab(self, target):
        """关闭指定的标签页"""
        try:
            if target in self.tab_frames:
                # 获取当前选中的标签页
                current_tab = self.notebook.select()
                closing_tab = str(self.tab_frames[target])

                # 关闭标签页
                self.notebook.forget(self.tab_frames[target])

                # 清理数据
                del self.tab_frames[target]
                if target in self.tab_trees:
                    del self.tab_trees[target]

                # 如果关闭的是当前选中的标签页，选择下一个或前一个
                if current_tab == closing_tab and len(self.tab_frames) > 0:
                    # 选择第一个可用的标签页
                    first_target = next(iter(self.tab_frames))
                    self.notebook.select(self.tab_frames[first_target])

                print(f"已关闭标签页: {target}")

        except Exception as e:
            print(f"关闭标签页失败: {e}")

    def close_empty_tab(self):
        """关闭空标签页"""
        try:
            self.notebook.forget(self.empty_tab_frame)
            delattr(self, 'empty_tab_frame')
        except Exception as e:
            print(f"关闭空标签页失败: {e}")

    def clear_all_results(self):
        """清除所有标签页结果"""
        for tab in list(self.tab_frames.keys()):
            self.close_tab(tab)
        if hasattr(self, 'empty_tab_frame'):
            self.close_empty_tab()

    def clear_results(self):
        """保持兼容性（已废弃）"""
        self.clear_all_results()

    def export_csv(self):
        """导出所有标签页的结果"""
        if not self.tab_trees:
            messagebox.showinfo("提示", "没有数据可导出")
            return

        try:
            with open("scan_results.csv", "w", encoding="utf-8-sig") as f:
                f.write("目标,ID,URL,IP,端口,协议,标题,来源,AI判断\n")

                for target, tree in self.tab_trees.items():
                    for item in tree.get_children():
                        values = tree.item(item)['values']
                        row = [target] + [str(v) for v in values]
                        f.write(",".join(row) + "\n")

            messagebox.showinfo("成功", "结果已导出到 scan_results.csv")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def check_ollama_available(self):
        """检查 Ollama 是否可用"""
        try:
            import requests
            resp = requests.get("http://localhost:11434/api/tags", timeout=5)
            if resp.status_code == 200:
                models = resp.json().get('models', [])
                # 检查是否有 qwen3-coder 模型
                coder_models = [m for m in models if 'qwen3-coder' in m.get('name', '').lower()]
                if coder_models:
                    self.ollama_model = coder_models[0]['name']
                    print(f"✅ 检测到 Ollama 模型: {self.ollama_model}")
                    return True
                else:
                    # 检查其他 qwen 模型
                    qwen_models = [m for m in models if 'qwen' in m.get('name', '').lower()]
                    if qwen_models:
                        self.ollama_model = qwen_models[0]['name']
                        print(f"⚠️ 未找到 qwen3-coder，使用备选模型: {self.ollama_model}")
                        return True
                    else:
                        print("⚠️ Ollama 可用，但未找到 Qwen 相关模型")
                        return False
        except Exception as e:
            print(f"❌ Ollama 不可用: {e}")
            return False

    def copy_selected_url(self, tree, item):
        """复制选中的URL到剪贴板"""
        values = tree.item(item)['values']

        if len(values) > 1:
            url = values[1]
            # 复制到剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.root.update()  # 确保剪贴板更新

            # 可选：显示状态提示
            self.update_status(f"已复制: {url}")

    def send_to_dir_bruteforce(self):
        """发送选中的URL到目录爆破功能"""
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

        # 获取选中的项目
        selection = tree.selection()
        if not selection:
            return

        item = selection[0]
        values = tree.item(item)['values']

        if len(values) > 1:
            url = values[1]
            # 确保URL有协议前缀
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            # 切换到目录爆破标签页
            self.main_gui.switch_to_bruteforce_tab(url)

    def toggle_select_all(self, target):
        """全选/取消全选"""
        if target in self.tab_trees:
            tree = self.tab_trees[target]
            items = tree.get_children()
            if items:
                # 检查是否已经全选
                first_item = tree.item(items[0])['values']
                if first_item[0] == "✓":
                    # 取消全选
                    for item in items:
                        values = tree.item(item)['values']
                        values[0] = ""
                        tree.item(item, values=values)
                else:
                    # 全选
                    for item in items:
                        values = tree.item(item)['values']
                        values[0] = "✓"
                        tree.item(item, values=values)

    def get_selected_urls(self):
        """获取所有勾选的URL（修正版）"""
        selected_urls = []

        # 遍历所有标签页
        for target, tree in self.tab_trees.items():
            items = tree.get_children()
            for item in items:
                values = tree.item(item)['values']
                # 修正：URL 是索引2，不是索引1
                if len(values) >= 3 and values[0] == "✓":  # Select列是索引0
                    url = values[2]  # URL列是索引2 ✅
                    if not url.startswith(('http://', 'https://')):
                        url = 'http://' + url
                    selected_urls.append(url)

        return selected_urls

    def send_selected_urls_to_bruteforce(self):
        """发送勾选的URL到目录爆破功能（修正版）"""
        selected_urls = self.get_selected_urls()

        if not selected_urls:
            # 如果没有勾选任何URL，检查是否有选中行
            current_tab = self.notebook.select()
            if not current_tab:
                messagebox.showwarning("提示", "请先选择或勾选要发送的URL")
                return

            tree = None
            for target, frame in self.tab_frames.items():
                if str(frame) == current_tab:
                    tree = self.tab_trees[target]
                    break

            if tree:
                selections = tree.selection()
                if selections:
                    # 从选中行获取URL
                    urls = []
                    for item in selections:
                        values = tree.item(item)['values']
                        if len(values) > 2:
                            url = values[2]  # ✅ 正确索引
                            if not url.startswith(('http://', 'https://')):
                                url = 'http://' + url
                            urls.append(url)
                    if urls:
                        self.main_gui.switch_to_bruteforce_tab_with_urls(urls)
                        return

            messagebox.showwarning("提示", "请先勾选要发送的URL")
            return

        # 切换到目录爆破标签页并设置目标
        self.main_gui.switch_to_bruteforce_tab_with_urls(selected_urls)
