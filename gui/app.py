import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk

from gui.framework import AppContext
from gui.components import DataConfigTab, GAParamsTab, ExecutionTab, ResultTab, SettingsTab
from gui.i18n import t, set_language
from gui.settings import Settings


class JSPGuiApp:
    """JSP调度优化智能体 - Tkinter GUI"""

    def __init__(self):
        self.root = None
        self.context = AppContext()
        self.settings = Settings()

        set_language(self.settings.get_language())

        self.tabs = {}

    def _process_queue(self):
        """处理队列消息"""
        while not self.context.queue.empty():
            try:
                item = self.context.queue.get_nowait()
                if item[0] == "log":
                    log_line = item[1]
                    if hasattr(self, 'log_text'):
                        self.log_text.insert(tk.END, log_line + "\n")
                        self.log_text.see(tk.END)
            except Exception:
                break

    def _build_ui(self):
        """构建UI"""
        self.root = tk.Tk()
        self.root.title(t("app_title"))
        self.root.geometry("1200x850")

        self.context.set_root(self.root)

        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 顶部优化说明栏
        self._build_overview_bar()

        # 创建Notebook标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建各个标签页
        self.tabs['data'] = DataConfigTab(self.notebook, self.context)
        self.tabs['data'].build()
        self.notebook.add(self.tabs['data'].frame, text=t("data_config"))

        self.tabs['ga'] = GAParamsTab(self.notebook, self.context)
        self.tabs['ga'].build()
        self.notebook.add(self.tabs['ga'].frame, text=t("ga_params"))

        self.tabs['execution'] = ExecutionTab(self.notebook, self.context)
        self.tabs['execution'].build()
        self.notebook.add(self.tabs['execution'].frame, text=t("execution_control"))
        self.log_text = self.tabs['execution'].log_text

        self.tabs['result'] = ResultTab(self.notebook, self.context)
        self.tabs['result'].build()
        self.notebook.add(self.tabs['result'].frame, text=t("result_display"))

        self.tabs['settings'] = SettingsTab(self.notebook, self.context)
        self.tabs['settings'].build()
        self.notebook.add(self.tabs['settings'].frame, text=t("settings"))

        # 保存组件引用到context
        self.context._data_config_tab = self.tabs['data']
        self.context._ga_params_tab = self.tabs['ga']
        self.context._execution_tab = self.tabs['execution']
        self.context._result_tab = self.tabs['result']

        # 启动队列处理
        self._check_queue()
        # 定期刷新优化说明栏
        self._check_overview_refresh()

    def _build_overview_bar(self):
        """构建顶部优化说明栏 - 包含文字说明和汇总表格"""
        overview_frame = ttk.LabelFrame(self.root, text=t("optimization_overview"), padding=10)
        overview_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # 文字说明区域
        desc_frame = ttk.Frame(overview_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(desc_frame, text=t("optimization_desc"),
                  font=('Arial', 9), wraplength=1150, justify=tk.LEFT).pack(anchor=tk.W)
        ttk.Label(desc_frame, text=t("optimization_method"),
                  font=('Arial', 9), wraplength=1150, justify=tk.LEFT).pack(anchor=tk.W, pady=(2, 0))

        # 汇总表格区域 - 显示当前算法结果的Makespan对比
        self.overview_table = ttk.Frame(overview_frame)
        self.overview_table.pack(fill=tk.X, pady=(5, 0))

        # 表头
        headers = ["算法", "Makespan", "优化率", "设备利用率"]
        for col, header in enumerate(headers):
            ttk.Label(self.overview_table, text=header,
                      font=('Arial', 9, 'bold')).grid(row=0, column=col, padx=15, pady=3)

        # 占位提示
        self.overview_placeholder = ttk.Label(self.overview_table, text=t("overview_no_data"),
                                              font=('Arial', 9), foreground='gray')
        self.overview_placeholder.grid(row=1, column=0, columnspan=4, pady=5)

    def _check_overview_refresh(self):
        """定期检查并刷新优化说明栏"""
        self._refresh_overview()
        self.root.after(500, self._check_overview_refresh)

    def _refresh_overview(self):
        """刷新优化说明栏的汇总表格"""
        # 清空表格内容（保留表头）
        for widget in self.overview_table.winfo_children():
            widget.destroy()

        # 表头
        headers = ["算法", "Makespan", "优化率", "设备利用率"]
        for col, header in enumerate(headers):
            ttk.Label(self.overview_table, text=header,
                      font=('Arial', 9, 'bold')).grid(row=0, column=col, padx=15, pady=3)

        # 收集结果
        results = []
        if self.context.ga_result:
            results.append(("GA", self.context.ga_result))
        if self.context.fcfs_result:
            results.append(("FCFS", self.context.fcfs_result))
        if self.context.spt_result:
            results.append(("SPT", self.context.spt_result))

        if not results:
            ttk.Label(self.overview_table, text=t("overview_no_data"),
                      font=('Arial', 9), foreground='gray').grid(
                      row=1, column=0, columnspan=4, pady=5)
            return

        # 计算基线Makespan（用于优化率计算，取FCFS和SPT中较小者）
        baseline_makespan = None
        for name, res in results:
            if name in ("FCFS", "SPT"):
                ms = res.get("makespan", 0)
                if baseline_makespan is None or ms < baseline_makespan:
                    baseline_makespan = ms

        # 填充数据行
        row = 1
        for name, res in results:
            makespan = res.get("makespan", 0)
            ttk.Label(self.overview_table, text=name,
                      font=('Arial', 9, 'bold') if name == "GA" else ('Arial', 9)).grid(
                      row=row, column=0, padx=15, pady=2)
            ttk.Label(self.overview_table, text=f"{makespan:.2f}").grid(
                      row=row, column=1, padx=15, pady=2)

            # 优化率
            if name == "GA" and baseline_makespan and baseline_makespan > 0:
                opt_rate = (baseline_makespan - makespan) / baseline_makespan * 100
                ttk.Label(self.overview_table, text=f"{opt_rate:.1f}%",
                          foreground='green').grid(row=row, column=2, padx=15, pady=2)
            else:
                ttk.Label(self.overview_table, text="-").grid(
                      row=row, column=2, padx=15, pady=2)

            # 设备利用率（简化计算）
            ttk.Label(self.overview_table, text="-").grid(
                      row=row, column=3, padx=15, pady=2)
            row += 1

    def _check_queue(self):
        """定期检查队列"""
        self._process_queue()
        self.root.after(100, self._check_queue)

    def run(self):
        """运行应用"""
        self._build_ui()
        self.root.mainloop()


if __name__ == "__main__":
    app = JSPGuiApp()
    app.run()
