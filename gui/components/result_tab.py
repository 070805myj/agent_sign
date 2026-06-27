import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from gui.framework import BaseTab, create_section_header
from gui.i18n import t
from utils.metrics_calculator import MetricsCalculator


class ResultTab(BaseTab):
    """结果展示标签页"""

    def __init__(self, parent, context):
        super().__init__(parent, context, t("result_display"))
        self.metrics_calculator = MetricsCalculator()
        self.chart_paths = {}
        self.chart_labels = {}

    def update_kpi_display(self, kpi_data=None):
        """更新KPI显示"""
        if kpi_data is None:
            # 只要有任何结果（GA/FCFS/SPT）且有数据就继续执行
            if not self.context._last_data:
                return
            if not (self.context.ga_result or self.context.fcfs_result or self.context.spt_result):
                return
            
            kpi_data = {}
            data = self.context._last_data

            # 从数据中获取num_jobs和num_machines
            num_jobs = len(data["processing_times"])
            # 从machine_sequences中推断机器数量（取最大机器编号+1）
            num_machines = 0
            if data["machine_sequences"]:
                for seq in data["machine_sequences"]:
                    if seq:
                        current_max = max(seq)
                        if current_max + 1 > num_machines:
                            num_machines = current_max + 1

            if self.context.ga_result:
                ga_kpi = self.metrics_calculator.calculate_all(
                    self.context.ga_result["schedule"], num_machines, num_jobs
                )
                kpi_data["GA"] = ga_kpi

            if self.context.fcfs_result:
                fcfs_kpi = self.metrics_calculator.calculate_all(
                    self.context.fcfs_result["schedule"], num_machines, num_jobs
                )
                kpi_data["FCFS"] = fcfs_kpi

            if self.context.spt_result:
                spt_kpi = self.metrics_calculator.calculate_all(
                    self.context.spt_result["schedule"], num_machines, num_jobs
                )
                kpi_data["SPT"] = spt_kpi

        for widget in self.kpi_table.winfo_children():
            widget.destroy()

        headers = [t("algorithm"), t("makespan"), t("utilization"), t("load_variance")]
        for col, header in enumerate(headers):
            ttk.Label(self.kpi_table, text=header, font=('Arial', 9, 'bold')).grid(row=0, column=col, padx=10, pady=5)

        row = 1
        for algo, kpi in kpi_data.items():
            ttk.Label(self.kpi_table, text=algo).grid(row=row, column=0, padx=10, pady=2)
            ttk.Label(self.kpi_table, text=f"{kpi.get('makespan', 0):.2f}").grid(row=row, column=1, padx=10, pady=2)
            ttk.Label(self.kpi_table, text=f"{kpi.get('machine_utilization', 0)*100:.1f}%").grid(row=row, column=2, padx=10, pady=2)
            ttk.Label(self.kpi_table, text=f"{kpi.get('load_variance', 0):.2f}").grid(row=row, column=3, padx=10, pady=2)
            row += 1

        # 同时更新调度方案详情表格
        self.update_schedule_details()

    def update_chart_preview(self, chart_paths):
        """更新图表预览 - 使用4x4 grid布局"""
        self.chart_paths = chart_paths

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        chart_names = {
            "gantt": "甘特图",
            "convergence": "收敛曲线",
            "comparison": "对比图"
        }

        chart_items = list(chart_paths.items())
        max_cols = 4
        max_rows = 4

        for idx, (chart_type, path) in enumerate(chart_items):
            try:
                img = Image.open(path)
                # 调整图片大小，保持比例，确保图表边框完整显示
                max_width = 300
                max_height = 250
                width, height = img.size
                if width > max_width or height > max_height:
                    ratio = min(max_width / width, max_height / height)
                    img = img.resize((int(width * ratio), int(height * ratio)), Image.LANCZOS)
                
                photo = ImageTk.PhotoImage(img)
                
                row = idx // max_cols
                col = idx % max_cols

                # 创建图表容器
                chart_container = ttk.Frame(self.chart_frame)
                chart_container.grid(row=row, column=col, padx=15, pady=10, sticky='n')
                
                # 图表标题 - 字体大小适中
                ttk.Label(chart_container, text=chart_names.get(chart_type, chart_type), 
                         font=('Arial', 12, 'bold')).pack(pady=(0, 5))
                
                # 图表图片
                label = ttk.Label(chart_container, image=photo, borderwidth=2, relief='solid')
                label.image = photo
                label.pack(padx=5, pady=5)

                self.chart_labels[chart_type] = label

            except Exception as e:
                self.context.log(f"Failed to load chart {chart_type}: {str(e)}")

        # 设置grid权重
        for i in range(max_cols):
            self.chart_frame.grid_columnconfigure(i, weight=1)
        for i in range(max_rows):
            self.chart_frame.grid_rowconfigure(i, weight=1)

    def update_schedule_details(self):
        """更新调度方案详情表格 - 按机器展示工序顺序"""
        # 清空表格
        for widget in self.schedule_table.winfo_children():
            widget.destroy()

        # 获取GA结果（优先展示GA调度方案）
        result = self.context.ga_result or self.context.fcfs_result or self.context.spt_result
        if not result or "schedule" not in result:
            ttk.Label(self.schedule_table, text=t("no_schedule_data"),
                      foreground='gray').grid(row=0, column=0, pady=10)
            return

        schedule = result["schedule"]
        operations = schedule.get("operations", [])
        if not operations:
            ttk.Label(self.schedule_table, text=t("no_schedule_data"),
                      foreground='gray').grid(row=0, column=0, pady=10)
            return

        # 表头
        ttk.Label(self.schedule_table, text=t("machine"),
                  font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=10, pady=3, sticky=tk.W)
        ttk.Label(self.schedule_table, text=t("operation_sequence"),
                  font=('Arial', 9, 'bold')).grid(row=0, column=1, padx=10, pady=3, sticky=tk.W)

        # 按机器分组工序，并按开始时间排序
        machine_ops = {}
        for op in operations:
            mid = op["machine_id"]
            if mid not in machine_ops:
                machine_ops[mid] = []
            machine_ops[mid].append(op)

        # 按机器编号排序
        row = 1
        for machine_id in sorted(machine_ops.keys()):
            ops = sorted(machine_ops[machine_id], key=lambda x: x["start_time"])

            # 机器编号
            ttk.Label(self.schedule_table, text=f"M{machine_id}",
                      font=('Arial', 9, 'bold')).grid(row=row, column=0, padx=10, pady=2, sticky=tk.W)

            # 工序顺序文字描述：J1O2(5-12) → J3O1(12-20) → ...
            seq_parts = []
            for op in ops:
                part = f"J{op['job_id']}O{op['op_id']}({op['start_time']:.0f}-{op['end_time']:.0f})"
                seq_parts.append(part)
            seq_text = " → ".join(seq_parts)

            ttk.Label(self.schedule_table, text=seq_text,
                      font=('Arial', 8)).grid(row=row, column=1, padx=10, pady=2, sticky=tk.W)
            row += 1

    def build(self):
        frame = super().build()
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # KPI指标表格
        create_section_header(frame, t("kpi_metrics"))
        self.kpi_table = ttk.Frame(frame)
        self.kpi_table.pack(fill=tk.X, pady=5)

        # 调度方案详情表格 - 使用Canvas+双滚动条实现水平和垂直滚动
        create_section_header(frame, t("schedule_details"))
        schedule_container = ttk.Frame(frame)
        schedule_container.pack(fill=tk.BOTH, expand=True, pady=5)

        # 创建Canvas和双滚动条
        self.schedule_canvas = tk.Canvas(schedule_container, height=200,
                                          highlightthickness=0)
        y_scrollbar = ttk.Scrollbar(schedule_container, orient="vertical",
                                    command=self.schedule_canvas.yview)
        x_scrollbar = ttk.Scrollbar(schedule_container, orient="horizontal",
                                    command=self.schedule_canvas.xview)
        self.schedule_canvas.configure(yscrollcommand=y_scrollbar.set,
                                       xscrollcommand=x_scrollbar.set)

        # 布局：Canvas居中，垂直滚动条右侧，水平滚动条底部
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.schedule_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.schedule_y_scrollbar = y_scrollbar
        self.schedule_x_scrollbar = x_scrollbar

        # 在Canvas内创建Frame用于放置表格内容
        self.schedule_table = ttk.Frame(self.schedule_canvas)
        self.schedule_window = self.schedule_canvas.create_window(
            (0, 0), window=self.schedule_table, anchor="nw"
        )

        # 绑定滚动区域更新事件
        self.schedule_table.bind("<Configure>", self._on_schedule_configure)
        # 鼠标滚轮支持
        self.schedule_canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.schedule_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        # 图表预览区域
        create_section_header(frame, t("chart_preview"))
        self.chart_frame = ttk.Frame(frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 刷新按钮
        ttk.Button(frame, text="Refresh Results", command=self.update_kpi_display).pack(pady=5)

        return frame

    def _on_schedule_configure(self, event):
        """调度表格内容变化时更新滚动区域"""
        self.schedule_canvas.configure(scrollregion=self.schedule_canvas.bbox("all"))

    def _bind_mousewheel(self):
        """绑定鼠标滚轮事件"""
        self.schedule_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        """解绑鼠标滚轮事件"""
        self.schedule_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """鼠标滚轮滚动处理"""
        self.schedule_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")