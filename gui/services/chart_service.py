import os
import tempfile
from utils.visualizer import Visualizer
from gui.i18n import t


class ChartService:
    """图表服务类"""

    def __init__(self, context):
        self.context = context
        self.visualizer = None
        self.temp_chart_paths = {}

    def _init_visualizer(self):
        if self.visualizer is None:
            self.visualizer = Visualizer()

    def generate_charts(self, data=None):
        """生成图表（仅用于预览，不保存）"""
        if data is None:
            data = self.context._last_data

        if not data or not self.context.ga_result:
            self.context.log("No data to generate charts")
            return {}

        self._init_visualizer()

        # 从machine_sequences中推断机器数量（取最大机器编号+1）
        num_machines = 0
        if data["machine_sequences"]:
            for seq in data["machine_sequences"]:
                if seq:
                    current_max = max(seq)
                    if current_max + 1 > num_machines:
                        num_machines = current_max + 1

        # 使用临时目录生成预览图表
        temp_dir = tempfile.gettempdir()
        os.makedirs(temp_dir, exist_ok=True)

        chart_paths = {}

        try:
            gantt_path = os.path.join(temp_dir, "jsp_gantt_temp.png")
            self.visualizer.draw_gantt(
                self.context.ga_result["schedule"],
                num_machines,
                gantt_path,
                "JSP Gantt Chart"
            )
            chart_paths["gantt"] = gantt_path

            convergence_path = os.path.join(temp_dir, "jsp_convergence_temp.png")
            self.visualizer.draw_convergence(
                self.context.ga_result["convergence"],
                convergence_path,
                "Convergence Curve"
            )
            chart_paths["convergence"] = convergence_path

            fcfs_ms = self.context.fcfs_result["makespan"] if self.context.fcfs_result else float('inf')
            spt_ms = self.context.spt_result["makespan"] if self.context.spt_result else float('inf')
            comparison_path = os.path.join(temp_dir, "jsp_comparison_temp.png")
            self.visualizer.draw_comparison_bar(
                self.context.ga_result["makespan"],
                fcfs_ms,
                spt_ms,
                comparison_path,
                "Algorithm Comparison"
            )
            chart_paths["comparison"] = comparison_path

            self.temp_chart_paths = chart_paths
            self.context.log("图表生成完成（预览模式）")
        except Exception as e:
            self.context.log(f"Chart generation warning: {str(e)}")

        # 更新结果标签页的图表预览（线程安全）
        if hasattr(self.context, '_result_tab'):
            self.context.safe_update(self.context._result_tab.update_chart_preview, chart_paths)

        return chart_paths

    def save_charts(self, output_dir):
        """保存图表到指定目录"""
        if not output_dir:
            self.context.log("请选择保存目录")
            return

        if not self.temp_chart_paths:
            self.context.log("请先生成图表")
            return

        os.makedirs(output_dir, exist_ok=True)

        chart_names = {
            "gantt": "jsp_gantt.png",
            "convergence": "jsp_convergence.png",
            "comparison": "jsp_comparison.png"
        }

        try:
            for chart_type, temp_path in self.temp_chart_paths.items():
                if os.path.exists(temp_path):
                    import shutil
                    dest_path = os.path.join(output_dir, chart_names[chart_type])
                    shutil.copy(temp_path, dest_path)

            self.context.log(t("charts_saved").format(path=output_dir))
        except Exception as e:
            self.context.log(f"保存图表失败: {str(e)}")