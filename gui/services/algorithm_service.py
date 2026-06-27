import time
import queue
from core.genetic_algorithm import GeneticAlgorithm
from core.baseline_solvers import FCFSSolver, SPTSolver
from core.jsp_model import JSPModel
from gui.i18n import t


class AlgorithmService:
    """算法服务类"""

    def __init__(self, context):
        self.context = context

    def run_ga(self, data, ga_params):
        """运行GA算法"""
        self.context.log(t("starting_ga"))

        # 创建JSP模型（只需要processing_times和machine_sequences）
        model = JSPModel(data["processing_times"], data["machine_sequences"])

        # 构建配置参数
        config = {
            "population_size": ga_params.get("population_size", 50),
            "max_generations": ga_params.get("max_generations", 500),
            "crossover_rate": ga_params.get("crossover_rate", 0.8),
            "mutation_rate_init": ga_params.get("mutation_rate", 0.1),
            "early_stop_generations": ga_params.get("early_stop", 50),
            "adaptive_mutation": ga_params.get("adaptive_mutation", True),
            "diversity_ratio_threshold": ga_params.get("diversity_threshold", 0.3),
            "random_seed": ga_params.get("random_seed", 42),
        }

        ga = GeneticAlgorithm(model, config)

        start_time = time.time()

        # 创建进度队列
        progress_queue = queue.Queue()

        # log_callback签名是(message)
        def log_callback(message):
            self.context.log(message)

        # 使用solve_with_progress方法
        result = ga.solve_with_progress(log_callback, progress_queue)

        elapsed_time = time.time() - start_time

        # 直接使用解码后的schedule格式（包含operations列表）
        self.context.ga_result = {
            "schedule": result["schedule"],
            "makespan": result["makespan"],
            "generations": len(result["convergence"]),
            "convergence": result["convergence"],
            "elapsed_time": elapsed_time,
        }

        self.context.log(t("ga_completed").format(makespan=result["makespan"]))

    def run_fcfs(self, data):
        """运行FCFS算法"""
        self.context.log("Starting FCFS...")

        # 创建JSP模型
        model = JSPModel(data["processing_times"], data["machine_sequences"])
        solver = FCFSSolver(model)

        start_time = time.time()
        result = solver.solve()
        elapsed_time = time.time() - start_time

        # 直接使用求解结果中的schedule格式
        self.context.fcfs_result = {
            "schedule": result["schedule"],
            "makespan": result["makespan"],
            "elapsed_time": elapsed_time,
        }

        self.context.log(t("fcfs_completed").format(makespan=result["makespan"]))

    def run_spt(self, data):
        """运行SPT算法"""
        self.context.log("Starting SPT...")

        # 创建JSP模型
        model = JSPModel(data["processing_times"], data["machine_sequences"])
        solver = SPTSolver(model)

        start_time = time.time()
        result = solver.solve()
        elapsed_time = time.time() - start_time

        # 直接使用求解结果中的schedule格式
        self.context.spt_result = {
            "schedule": result["schedule"],
            "makespan": result["makespan"],
            "elapsed_time": elapsed_time,
        }

        self.context.log(t("spt_completed").format(makespan=result["makespan"]))