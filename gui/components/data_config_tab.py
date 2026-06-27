import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os
import random
from gui.framework import BaseTab, create_section_header
from gui.i18n import t
from data.test_case import get_test_case, list_test_cases


class DataConfigTab(BaseTab):
    """数据配置标签页"""

    def __init__(self, parent, context):
        super().__init__(parent, context, t("data_config"))
        self.default_pt = [
            [1, 3, 6, 7, 3, 6],
            [8, 5, 10, 10, 10, 4],
            [5, 4, 8, 9, 1, 7],
            [5, 5, 5, 3, 8, 9],
            [9, 3, 5, 4, 3, 1],
            [3, 3, 9, 10, 4, 1],
        ]
        self.default_ms = [
            [0, 1, 2, 3, 4, 5],
            [2, 3, 5, 0, 1, 4],
            [3, 4, 5, 0, 1, 2],
            [1, 2, 0, 5, 3, 4],
            [2, 1, 4, 3, 5, 0],
            [1, 0, 2, 5, 4, 3],
        ]

    def _format_matrix(self, matrix):
        return "\n".join(",".join(str(x) for x in row) for row in matrix)

    def _parse_matrix(self, text):
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        matrix = []
        for line in lines:
            row = [int(x.strip()) for x in line.split(',') if x.strip()]
            matrix.append(row)
        return matrix

    def validate_input(self):
        """验证输入数据"""
        try:
            num_jobs = int(self.num_jobs_var.get())
            num_machines = int(self.num_machines_var.get())
            processing_times = self._parse_matrix(self.pt_text.get("1.0", tk.END))
            machine_sequences = self._parse_matrix(self.ms_text.get("1.0", tk.END))

            if num_jobs <= 0 or num_machines <= 0:
                self.context.log("Error: Jobs and machines must be > 0")
                return None

            if len(processing_times) != num_jobs or len(machine_sequences) != num_jobs:
                self.context.log(f"Error: Row count mismatch")
                return None

            for row in processing_times:
                if len(row) != num_machines:
                    self.context.log(f"Error: Processing time column mismatch")
                    return None

            for row in machine_sequences:
                if len(row) != num_machines:
                    self.context.log(f"Error: Machine sequence column mismatch")
                    return None

            return {
                "num_jobs": num_jobs,
                "num_machines": num_machines,
                "processing_times": processing_times,
                "machine_sequences": machine_sequences,
            }
        except ValueError as e:
            self.context.log(f"Error: Invalid input format - {str(e)}")
            return None

    def _load_test_case(self):
        test_case_name = self.test_case_var.get()
        if not test_case_name:
            return

        if test_case_name == "自定义":
            self.context.log("已选择自定义模式，请修改参数或点击生成矩阵")
            return

        try:
            test_case = get_test_case(test_case_name)
            self.num_jobs_var.set(test_case["num_jobs"])
            self.num_machines_var.set(test_case["num_machines"])
            self.pt_text.delete("1.0", tk.END)
            self.pt_text.insert("1.0", self._format_matrix(test_case["processing_times"]))
            self.ms_text.delete("1.0", tk.END)
            self.ms_text.insert("1.0", self._format_matrix(test_case["machine_sequences"]))
            self.context.log(f"Loaded test case: {test_case_name} (Optimal: {test_case['optimal_makespan']})")
        except Exception as e:
            self.context.log(f"Failed to load test case: {str(e)}")

    def _generate_random_matrix(self):
        """随机生成加工时间矩阵和机器序列矩阵"""
        try:
            num_jobs = int(self.num_jobs_var.get())
            num_machines = int(self.num_machines_var.get())

            if num_jobs <= 0 or num_machines <= 0:
                self.context.log("Error: Jobs and machines must be > 0")
                return

            processing_times = []
            for _ in range(num_jobs):
                row = [random.randint(1, 20) for _ in range(num_machines)]
                processing_times.append(row)

            machine_sequences = []
            for _ in range(num_jobs):
                seq = list(range(num_machines))
                random.shuffle(seq)
                machine_sequences.append(seq)

            self.pt_text.delete("1.0", tk.END)
            self.pt_text.insert("1.0", self._format_matrix(processing_times))
            self.ms_text.delete("1.0", tk.END)
            self.ms_text.insert("1.0", self._format_matrix(machine_sequences))

            self.context.log(f"Generated random matrix: {num_jobs} jobs, {num_machines} machines")
        except ValueError as e:
            self.context.log(f"Error: Invalid input - {str(e)}")

    def _select_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.csv_path_var.set(file_path)
            self._load_csv()

    def _load_csv(self):
        file_path = self.csv_path_var.get()
        if not file_path or not os.path.exists(file_path):
            self.context.log("Error: Please select a valid CSV file")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                lines = list(reader)

            if len(lines) < 4:
                self.context.log("Error: CSV format incorrect")
                return

            num_jobs = int(lines[0][0])
            num_machines = int(lines[1][0])

            processing_times = []
            machine_sequences = []
            pt_end = 2 + num_jobs
            ms_end = pt_end + num_jobs

            for i in range(2, pt_end):
                row = [int(x) for x in lines[i] if x.strip()]
                processing_times.append(row)

            for i in range(pt_end, ms_end):
                row = [int(x) for x in lines[i] if x.strip()]
                machine_sequences.append(row)

            self.num_jobs_var.set(num_jobs)
            self.num_machines_var.set(num_machines)
            self.pt_text.delete("1.0", tk.END)
            self.pt_text.insert("1.0", self._format_matrix(processing_times))
            self.ms_text.delete("1.0", tk.END)
            self.ms_text.insert("1.0", self._format_matrix(machine_sequences))

            self.context.log(f"Loaded from CSV: {num_jobs} jobs, {num_machines} machines")
        except Exception as e:
            self.context.log(f"Failed to load CSV: {str(e)}")

    def build(self):
        frame = super().build()
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左右布局
        left_frame = ttk.Frame(frame)
        right_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # 左半边：数据输入
        create_section_header(left_frame, t("job_machine_count"))

        count_frame = ttk.Frame(left_frame)
        ttk.Label(count_frame, text="Jobs:").pack(side=tk.LEFT, padx=5)
        self.num_jobs_var = tk.IntVar(value=6)
        ttk.Entry(count_frame, textvariable=self.num_jobs_var, width=8).pack(side=tk.LEFT)
        ttk.Label(count_frame, text="Machines:").pack(side=tk.LEFT, padx=5)
        self.num_machines_var = tk.IntVar(value=6)
        ttk.Entry(count_frame, textvariable=self.num_machines_var, width=8).pack(side=tk.LEFT)
        ttk.Button(count_frame, text="生成矩阵", command=self._generate_random_matrix).pack(side=tk.LEFT, padx=10)
        count_frame.pack(pady=5)

        create_section_header(left_frame, t("processing_times"))
        pt_frame = ttk.Frame(left_frame)
        self.pt_text = tk.Text(pt_frame, height=10, width=40, font=('Consolas', 9))
        self.pt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pt_scroll = ttk.Scrollbar(pt_frame, orient=tk.VERTICAL, command=self.pt_text.yview)
        self.pt_text.configure(yscrollcommand=pt_scroll.set)
        pt_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        pt_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.pt_text.insert("1.0", self._format_matrix(self.default_pt))

        create_section_header(left_frame, t("machine_sequences"))
        ms_frame = ttk.Frame(left_frame)
        self.ms_text = tk.Text(ms_frame, height=10, width=40, font=('Consolas', 9))
        self.ms_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ms_scroll = ttk.Scrollbar(ms_frame, orient=tk.VERTICAL, command=self.ms_text.yview)
        self.ms_text.configure(yscrollcommand=ms_scroll.set)
        ms_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        ms_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.ms_text.insert("1.0", self._format_matrix(self.default_ms))

        # 右半边：CSV导入和测试用例
        create_section_header(right_frame, t("csv_import"))
        csv_frame = ttk.Frame(right_frame)
        self.csv_path_var = tk.StringVar()
        ttk.Entry(csv_frame, textvariable=self.csv_path_var, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(csv_frame, text=t("select_csv"), command=self._select_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(csv_frame, text=t("import_csv"), command=self._load_csv).pack(side=tk.LEFT, padx=5)
        csv_frame.pack(pady=5)

        create_section_header(right_frame, t("test_case"))
        test_case_frame = ttk.Frame(right_frame)
        self.test_case_var = tk.StringVar()
        test_cases = ["自定义"] + list_test_cases()
        if test_cases:
            self.test_case_var.set(test_cases[0])
        ttk.Combobox(test_case_frame, textvariable=self.test_case_var, values=test_cases, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(test_case_frame, text=t("load_test_case"), command=self._load_test_case).pack(side=tk.LEFT, padx=5)
        test_case_frame.pack(pady=5)

        return frame
