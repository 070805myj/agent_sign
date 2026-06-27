# -*- coding: utf-8 -*-
"""
JSP调度优化智能体主程序入口
"""

import os
import random

from config.settings import get_ga_config, get_global_config
from data.test_case import get_test_case
from core.jsp_model import JSPModel
from core.genetic_algorithm import GeneticAlgorithm
from core.baseline_solvers import FCFSSolver, SPTSolver
from utils.metrics_calculator import MetricsCalculator
from utils.visualizer import Visualizer


def main():
    """主程序入口"""
    # 获取配置
    ga_config = get_ga_config()
    global_config = get_global_config()
    random_seed = global_config["random_seed"]
    verbose = global_config["verbose"]
    save_results = global_config["save_results"]

    # 设置随机种子
    random.seed(random_seed)

    # 加载测试用例（FT06）
    test_case = get_test_case("FT06")
    processing_times = test_case["processing_times"]
    machine_sequences = test_case["machine_sequences"]
    num_jobs = test_case["num_jobs"]
    num_machines = test_case["num_machines"]
    optimal_makespan = test_case["optimal_makespan"]

    if verbose:
        print(f"========== JSP调度优化智能体 ==========")
        print(f"测试用例: {test_case['name']}")
        print(f"工件数量: {num_jobs}, 机器数量: {num_machines}")
        print(f"理论最优Makespan: {optimal_makespan}")
        print(f"随机种子: {random_seed}")
        print("=" * 45)

    # 创建JSP模型
    model = JSPModel(processing_times, machine_sequences)

    # 基线算法求解
    if verbose:
        print("\n--- 基线算法求解 ---")

    # FCFS
    fcfs_solver = FCFSSolver(model)
    fcfs_result = fcfs_solver.solve()
    fcfs_makespan = fcfs_result["makespan"]

    if verbose:
        print(f"FCFS Makespan: {fcfs_makespan:.2f}")

    # SPT
    spt_solver = SPTSolver(model)
    spt_result = spt_solver.solve()
    spt_makespan = spt_result["makespan"]

    if verbose:
        print(f"SPT Makespan: {spt_makespan:.2f}")

    # GA求解
    if verbose:
        print("\n--- 遗传算法求解 ---")

    config = {
        **ga_config,
        **global_config
    }

    ga = GeneticAlgorithm(model, config)
    ga_result = ga.solve()
    ga_makespan = ga_result["makespan"]
    ga_schedule = ga_result["schedule"]
    convergence = ga_result["convergence"]

    # 计算KPI指标
    calculator = MetricsCalculator()
    ga_kpi = calculator.calculate_all(
        ga_schedule,
        num_machines,
        num_jobs,
        baseline_makespan=fcfs_makespan
    )

    # 输出结果
    if verbose:
        print("\n--- KPI指标 ---")
        print(f"GA Makespan: {ga_kpi['makespan']:.2f}")
        print(f"总完工时间: {ga_kpi['total_completion_time']:.2f}")
        print(f"平均流程时间: {ga_kpi['avg_flow_time']:.2f}")
        print(f"机器平均利用率: {ga_kpi['machine_utilization']:.2%}")
        print(f"机器总空闲时间: {ga_kpi['total_idle_time']:.2f}")
        print(f"负载方差: {ga_kpi['load_variance']:.2f}")
        print(f"优化率(vs FCFS): {ga_kpi['optimization_rate']:.2f}%")
        print(f"优化率(vs SPT): {calculator.calculate_optimization_rate(ga_makespan, spt_makespan):.2f}%")

    # 保存结果图片
    if save_results:
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)

        visualizer = Visualizer()

        # 绘制甘特图
        gantt_path = os.path.join(output_dir, "gantt.png")
        visualizer.draw_gantt(ga_schedule, num_machines, gantt_path, title=f"{test_case['name']}调度甘特图")
        if verbose:
            print(f"\n甘特图已保存: {gantt_path}")

        # 绘制收敛曲线
        convergence_path = os.path.join(output_dir, "convergence.png")
        visualizer.draw_convergence(convergence, convergence_path, title=f"{test_case['name']}收敛曲线")
        if verbose:
            print(f"收敛曲线已保存: {convergence_path}")

        # 绘制对比柱状图
        comparison_path = os.path.join(output_dir, "comparison.png")
        visualizer.draw_comparison_bar(ga_makespan, fcfs_makespan, spt_makespan,
                                       comparison_path, title=f"{test_case['name']}算法对比")
        if verbose:
            print(f"对比图已保存: {comparison_path}")

    if verbose:
        print("\n========== 求解完成 ==========")


if __name__ == "__main__":
    main()