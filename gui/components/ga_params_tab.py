import tkinter as tk
from tkinter import ttk
from gui.framework import BaseTab, create_section_header
from gui.i18n import t


class GAParamsTab(BaseTab):
    """GA参数标签页"""

    def __init__(self, parent, context):
        super().__init__(parent, context, t("ga_params"))
        self.ga_params = {
            "population_size": 50,
            "max_generations": 500,
            "crossover_rate": 0.8,
            "mutation_rate": 0.1,
            "early_stop": 50,
            "adaptive_mutation": True,
            "diversity_threshold": 0.3,
            "random_seed": 42,
        }

    def update_params(self):
        """更新参数"""
        try:
            self.ga_params["population_size"] = int(self.population_var.get())
            self.ga_params["max_generations"] = int(self.generations_var.get())
            self.ga_params["crossover_rate"] = float(self.crossover_var.get())
            self.ga_params["mutation_rate"] = float(self.mutation_var.get())
            self.ga_params["early_stop"] = int(self.early_stop_var.get())
            self.ga_params["adaptive_mutation"] = bool(self.adaptive_var.get())
            self.ga_params["diversity_threshold"] = float(self.diversity_var.get())
            self.ga_params["random_seed"] = int(self.seed_var.get())
            self.context.log(t("params_updated"))
        except ValueError:
            self.context.log(t("invalid_params"))

    def build(self):
        frame = super().build()
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建参数输入区域
        param_frame = ttk.Frame(frame)
        param_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        row = 0
        # 种群大小
        ttk.Label(param_frame, text=t("population_size")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.population_var = tk.IntVar(value=self.ga_params["population_size"])
        ttk.Entry(param_frame, textvariable=self.population_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)

        # 最大代数
        row += 1
        ttk.Label(param_frame, text=t("max_generations")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.generations_var = tk.IntVar(value=self.ga_params["max_generations"])
        ttk.Entry(param_frame, textvariable=self.generations_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)

        # 交叉率
        row += 1
        ttk.Label(param_frame, text=t("crossover_rate")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.crossover_var = tk.DoubleVar(value=self.ga_params["crossover_rate"])
        ttk.Entry(param_frame, textvariable=self.crossover_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)

        # 变异率
        row += 1
        ttk.Label(param_frame, text=t("mutation_rate")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.mutation_var = tk.DoubleVar(value=self.ga_params["mutation_rate"])
        ttk.Entry(param_frame, textvariable=self.mutation_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)

        # 早停代数
        row += 1
        ttk.Label(param_frame, text=t("early_stop")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.early_stop_var = tk.IntVar(value=self.ga_params["early_stop"])
        ttk.Entry(param_frame, textvariable=self.early_stop_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)

        # 自适应变异
        row += 1
        ttk.Label(param_frame, text=t("adaptive_mutation")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.adaptive_var = tk.BooleanVar(value=self.ga_params["adaptive_mutation"])
        ttk.Checkbutton(param_frame, variable=self.adaptive_var).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)

        # 多样性阈值
        row += 1
        ttk.Label(param_frame, text=t("diversity_threshold")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.diversity_var = tk.DoubleVar(value=self.ga_params["diversity_threshold"])
        ttk.Entry(param_frame, textvariable=self.diversity_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)

        # 随机种子
        row += 1
        ttk.Label(param_frame, text=t("random_seed")).grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.seed_var = tk.IntVar(value=self.ga_params["random_seed"])
        ttk.Entry(param_frame, textvariable=self.seed_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)

        # 更新按钮
        row += 1
        ttk.Button(param_frame, text=t("update_params"), command=self.update_params).grid(row=row, column=0, columnspan=2, pady=20)

        return frame
