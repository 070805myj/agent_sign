import tkinter as tk
from tkinter import ttk, filedialog
import threading
from gui.framework import BaseTab, create_section_header
from gui.i18n import t
from gui.services import AlgorithmService, ExportService, ChartService


class ExecutionTab(BaseTab):
    """执行控制标签页"""

    def __init__(self, parent, context):
        super().__init__(parent, context, t("execution_control"))
        self.algorithm_service = AlgorithmService(context)
        self.export_service = ExportService(context)
        self.chart_service = ChartService(context)

    def _run_ga(self):
        if self.context.is_running:
            self.context.log(t("task_running"))
            return

        data = self.context._data_config_tab.validate_input()
        if not data:
            return

        self.context._last_data = data
        self.context.set_running(True)
        self._ga_button.configure(state=tk.DISABLED)
        self._fcfs_button.configure(state=tk.DISABLED)
        self._spt_button.configure(state=tk.DISABLED)

        thread = threading.Thread(target=self._run_ga_thread, args=(data,))
        thread.daemon = True
        thread.start()

    def _run_ga_thread(self, data):
        try:
            self.algorithm_service.run_ga(data, self.context._ga_params_tab.ga_params)
            if hasattr(self.context._result_tab, 'update_kpi_display'):
                self.context._result_tab.update_kpi_display()
        except Exception as e:
            self.context.log(f"GA Error: {str(e)}")
        finally:
            self._ga_button.configure(state=tk.NORMAL)
            self._fcfs_button.configure(state=tk.NORMAL)
            self._spt_button.configure(state=tk.NORMAL)
            self.context.set_running(False)

    def _run_fcfs(self):
        if self.context.is_running:
            self.context.log(t("task_running"))
            return

        data = self.context._data_config_tab.validate_input()
        if not data:
            return

        self.context._last_data = data
        self.context.set_running(True)
        self._ga_button.configure(state=tk.DISABLED)
        self._fcfs_button.configure(state=tk.DISABLED)
        self._spt_button.configure(state=tk.DISABLED)

        thread = threading.Thread(target=self._run_fcfs_thread, args=(data,))
        thread.daemon = True
        thread.start()

    def _run_fcfs_thread(self, data):
        try:
            self.algorithm_service.run_fcfs(data)
            if hasattr(self.context._result_tab, 'update_kpi_display'):
                self.context._result_tab.update_kpi_display()
        except Exception as e:
            self.context.log(f"FCFS Error: {str(e)}")
        finally:
            self._ga_button.configure(state=tk.NORMAL)
            self._fcfs_button.configure(state=tk.NORMAL)
            self._spt_button.configure(state=tk.NORMAL)
            self.context.set_running(False)

    def _run_spt(self):
        if self.context.is_running:
            self.context.log(t("task_running"))
            return

        data = self.context._data_config_tab.validate_input()
        if not data:
            return

        self.context._last_data = data
        self.context.set_running(True)
        self._ga_button.configure(state=tk.DISABLED)
        self._fcfs_button.configure(state=tk.DISABLED)
        self._spt_button.configure(state=tk.DISABLED)

        thread = threading.Thread(target=self._run_spt_thread, args=(data,))
        thread.daemon = True
        thread.start()

    def _run_spt_thread(self, data):
        try:
            self.algorithm_service.run_spt(data)
            if hasattr(self.context._result_tab, 'update_kpi_display'):
                self.context._result_tab.update_kpi_display()
        except Exception as e:
            self.context.log(f"SPT Error: {str(e)}")
        finally:
            self._ga_button.configure(state=tk.NORMAL)
            self._fcfs_button.configure(state=tk.NORMAL)
            self._spt_button.configure(state=tk.NORMAL)
            self.context.set_running(False)

    def _select_export_dir(self):
        dir_path = filedialog.askdirectory(title="Select Export Directory")
        if dir_path:
            self.export_dir_var.set(dir_path)

    def _export_results(self):
        """导出结果到用户指定目录"""
        export_dir = self.export_dir_var.get()
        if not export_dir:
            dir_path = filedialog.askdirectory(title="选择导出目录")
            if dir_path:
                export_dir = dir_path
                self.export_dir_var.set(dir_path)
            else:
                self.context.log("请选择导出目录")
                return
        self.export_service.export(export_dir)

    def _generate_charts(self):
        if not self.context.ga_result:
            self.context.log(t("no_ga_result"))
            return
        thread = threading.Thread(target=self.chart_service.generate_charts)
        thread.daemon = True
        thread.start()

    def _save_charts(self):
        """保存图表到指定目录"""
        output_dir = self.export_dir_var.get()
        if not output_dir:
            dir_path = filedialog.askdirectory(title="选择图表保存目录")
            if dir_path:
                output_dir = dir_path
                self.export_dir_var.set(dir_path)
            else:
                self.context.log("请选择保存目录")
                return
        self.chart_service.save_charts(output_dir)

    def _reset_all(self):
        """重置日志、图表和结果"""
        # 清空日志
        self.log_text.delete("1.0", tk.END)

        # 清空算法结果
        self.context.ga_result = None
        self.context.fcfs_result = None
        self.context.spt_result = None

        # 清空图表服务缓存
        self.chart_service.temp_chart_paths = {}

        # 清空结果展示标签页
        if hasattr(self.context, '_result_tab'):
            self.context._result_tab.chart_paths = {}
            self.context._result_tab.chart_labels = {}
            for widget in self.context._result_tab.chart_frame.winfo_children():
                widget.destroy()
            for widget in self.context._result_tab.kpi_table.winfo_children():
                widget.destroy()

        self.context.log("已重置日志、图表和结果")

    def build(self):
        frame = super().build()
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 按钮区域
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self._ga_button = ttk.Button(btn_frame, text=t("run_ga"), command=self._run_ga)
        self._ga_button.pack(side=tk.LEFT, padx=5)

        self._fcfs_button = ttk.Button(btn_frame, text=t("run_fcfs"), command=self._run_fcfs)
        self._fcfs_button.pack(side=tk.LEFT, padx=5)

        self._spt_button = ttk.Button(btn_frame, text=t("run_spt"), command=self._run_spt)
        self._spt_button.pack(side=tk.LEFT, padx=5)

        # 重置按钮
        ttk.Button(btn_frame, text="重置", command=self._reset_all).pack(side=tk.LEFT, padx=5)

        # 日志区域
        create_section_header(frame, t("execution_log"))
        log_frame = ttk.Frame(frame)
        self.log_text = tk.Text(log_frame, height=15, width=80, font=('Consolas', 9))
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 导出区域
        export_frame = ttk.Frame(frame)
        export_frame.pack(fill=tk.X, pady=10)

        ttk.Label(export_frame, text=t("save_directory")).pack(side=tk.LEFT, padx=5)
        self.export_dir_var = tk.StringVar()
        ttk.Entry(export_frame, textvariable=self.export_dir_var, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text=t("select_directory"), command=self._select_export_dir).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text=t("export_results"), command=self._export_results).pack(side=tk.LEFT, padx=5)

        # 图表生成
        chart_frame = ttk.Frame(frame)
        chart_frame.pack(fill=tk.X, pady=5)
        ttk.Button(chart_frame, text=t("generate_charts"), command=self._generate_charts).pack(side=tk.LEFT, padx=5)
        ttk.Button(chart_frame, text="保存图表", command=self._save_charts).pack(side=tk.LEFT, padx=5)

        return frame
