import os
import json
import csv
import shutil
import tempfile
from datetime import datetime
from utils.metrics_calculator import MetricsCalculator


class ExportService:
    """导出服务类"""

    def __init__(self, context):
        self.context = context
        self.metrics_calculator = MetricsCalculator()

    def export(self, export_dir=None):
        if export_dir is None:
            from gui.settings import Settings
            settings = Settings()
            export_dir = settings.get_chart_output_dir()

        if not export_dir or not os.path.exists(export_dir):
            self.context.log("Please select a valid export directory")
            return

        if not self.context._last_data:
            self.context.log("No data available, please run an algorithm first")
            return

        try:
            # 从数据中获取num_jobs和num_machines
            num_jobs = len(self.context._last_data["processing_times"])
            # 从machine_sequences中推断机器数量（取最大机器编号+1）
            num_machines = 0
            if self.context._last_data["machine_sequences"]:
                for seq in self.context._last_data["machine_sequences"]:
                    if seq:
                        current_max = max(seq)
                        if current_max + 1 > num_machines:
                            num_machines = current_max + 1

            if self.context.ga_result:
                gantt_src = os.path.join(tempfile.gettempdir(), "jsp_gantt_temp.png")
                convergence_src = os.path.join(tempfile.gettempdir(), "jsp_convergence_temp.png")
                comparison_src = os.path.join(tempfile.gettempdir(), "jsp_comparison_temp.png")

                if os.path.exists(gantt_src):
                    shutil.copy(gantt_src, os.path.join(export_dir, "gantt.png"))
                if os.path.exists(convergence_src):
                    shutil.copy(convergence_src, os.path.join(export_dir, "convergence.png"))
                if os.path.exists(comparison_src):
                    shutil.copy(comparison_src, os.path.join(export_dir, "comparison.png"))

            results = {
                "ga_result": self.context.ga_result,
                "fcfs_result": self.context.fcfs_result,
                "spt_result": self.context.spt_result,
                "export_time": datetime.now().isoformat(),
            }

            with open(os.path.join(export_dir, "results.json"), 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            with open(os.path.join(export_dir, "results.csv"), 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Algorithm", "Makespan", "Total Completion Time",
                                "Avg Flow Time", "Machine Utilization",
                                "Total Idle Time", "Load Variance"])

                if self.context.ga_result:
                    ga_kpi = self.metrics_calculator.calculate_all(
                        self.context.ga_result["schedule"],
                        num_machines,
                        num_jobs,
                    )
                    writer.writerow([
                        "GA", ga_kpi.get('makespan', ''), ga_kpi.get('total_completion_time', ''),
                        ga_kpi.get('avg_flow_time', ''), ga_kpi.get('machine_utilization', ''),
                        ga_kpi.get('total_idle_time', ''), ga_kpi.get('load_variance', '')
                    ])

                if self.context.fcfs_result:
                    fcfs_kpi = self.metrics_calculator.calculate_all(
                        self.context.fcfs_result["schedule"],
                        num_machines,
                        num_jobs,
                    )
                    writer.writerow([
                        "FCFS", fcfs_kpi.get('makespan', ''), fcfs_kpi.get('total_completion_time', ''),
                        fcfs_kpi.get('avg_flow_time', ''), fcfs_kpi.get('machine_utilization', ''),
                        fcfs_kpi.get('total_idle_time', ''), fcfs_kpi.get('load_variance', '')
                    ])

                if self.context.spt_result:
                    spt_kpi = self.metrics_calculator.calculate_all(
                        self.context.spt_result["schedule"],
                        num_machines,
                        num_jobs,
                    )
                    writer.writerow([
                        "SPT", spt_kpi.get('makespan', ''), spt_kpi.get('total_completion_time', ''),
                        spt_kpi.get('avg_flow_time', ''), spt_kpi.get('machine_utilization', ''),
                        spt_kpi.get('total_idle_time', ''), spt_kpi.get('load_variance', '')
                    ])

            self.context.log(f"Results exported to: {export_dir}")
        except Exception as e:
            self.context.log(f"Export failed: {str(e)}")
