"""
JSP 调度 MCP 服务器
提供作业车间调度求解的 MCP 服务接口
"""

import json
import sys

from core.jsp_model import JSPModel
from core.genetic_algorithm import GeneticAlgorithm
from core.baseline_solvers import FCFSSolver, SPTSolver
from utils.metrics_calculator import MetricsCalculator
from utils.visualizer import Visualizer


class JSPSolverMCP:
    """JSP 求解器 MCP 服务类"""

    def __init__(self):
        self.tools = {
            "jsp_solve_ga": {
                "name": "jsp_solve_ga",
                "description": "使用遗传算法求解JSP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "processing_times": {
                            "type": "array",
                            "description": "工件在各机器上的处理时间矩阵"
                        },
                        "machine_sequences": {
                            "type": "array",
                            "description": "工件的机器访问顺序"
                        },
                        "ga_params": {
                            "type": "object",
                            "description": "GA算法参数"
                        },
                        "random_seed": {
                            "type": "integer",
                            "default": 42,
                            "description": "全局随机种子"
                        }
                    },
                    "required": ["processing_times", "machine_sequences"]
                }
            },
            "jsp_solve_baseline": {
                "name": "jsp_solve_baseline",
                "description": "使用基线算法求解JSP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "processing_times": {
                            "type": "array",
                            "description": "工件在各机器上的处理时间矩阵"
                        },
                        "machine_sequences": {
                            "type": "array",
                            "description": "工件的机器访问顺序"
                        },
                        "algorithm_type": {
                            "type": "string",
                            "enum": ["FCFS", "SPT"],
                            "default": "FCFS",
                            "description": "基线算法类型"
                        }
                    },
                    "required": ["processing_times", "machine_sequences"]
                }
            },
            "jsp_calculate_kpi": {
                "name": "jsp_calculate_kpi",
                "description": "计算调度方案的关键性能指标",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "schedule": {
                            "type": "object",
                            "description": "调度方案"
                        },
                        "num_machines": {
                            "type": "integer",
                            "description": "机器数量"
                        },
                        "num_jobs": {
                            "type": "integer",
                            "description": "工件数量"
                        },
                        "baseline_makespan": {
                            "type": "number",
                            "description": "基线Makespan（可选）"
                        }
                    },
                    "required": ["schedule", "num_machines", "num_jobs"]
                }
            },
            "jsp_draw_gantt": {
                "name": "jsp_draw_gantt",
                "description": "生成调度甘特图",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "schedule": {
                            "type": "object",
                            "description": "调度方案"
                        },
                        "num_machines": {
                            "type": "integer",
                            "description": "机器数量"
                        },
                        "save_path": {
                            "type": "string",
                            "default": "./gantt.png",
                            "description": "保存路径"
                        },
                        "title": {
                            "type": "string",
                            "default": "JSP调度甘特图",
                            "description": "图表标题"
                        },
                        "show": {
                            "type": "boolean",
                            "default": false,
                            "description": "是否显示图表"
                        }
                    },
                    "required": ["schedule", "num_machines"]
                }
            }
        }

    def get_tools(self):
        """获取可用工具列表"""
        return {"tools": list(self.tools.values())}

    def call_tool(self, tool_name, arguments):
        """调用指定工具"""
        if tool_name not in self.tools:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        try:
            if tool_name == "jsp_solve_ga":
                return self._jsp_solve_ga(arguments)
            elif tool_name == "jsp_solve_baseline":
                return self._jsp_solve_baseline(arguments)
            elif tool_name == "jsp_calculate_kpi":
                return self._jsp_calculate_kpi(arguments)
            elif tool_name == "jsp_draw_gantt":
                return self._jsp_draw_gantt(arguments)
            else:
                return {"success": False, "error": f"Tool not implemented: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _jsp_solve_ga(self, args):
        """使用遗传算法求解JSP"""
        processing_times = args.get("processing_times")
        machine_sequences = args.get("machine_sequences")
        ga_params = args.get("ga_params", {})
        random_seed = args.get("random_seed", 42)

        model = JSPModel(processing_times, machine_sequences)

        config = {
            "population_size": ga_params.get("population_size", 100),
            "max_generations": ga_params.get("max_generations", 300),
            "crossover_rate": ga_params.get("crossover_rate", 0.8),
            "mutation_rate_init": ga_params.get("mutation_rate_init", 0.1),
            "selection_pressure": ga_params.get("selection_pressure", 2.0),
            "elite_ratio": ga_params.get("elite_ratio", 0.05),
            "early_stop_generations": ga_params.get("early_stop_generations", 50),
            "adaptive_mutation": ga_params.get("adaptive_mutation", True),
            "diversity_ratio_threshold": ga_params.get("diversity_ratio_threshold", 0.2),
            "random_seed": random_seed,
            "verbose": False
        }

        ga = GeneticAlgorithm(model, config)
        result = ga.solve()

        return {
            "success": True,
            "result": {
                "makespan": result["makespan"],
                "best_sequence": result["best_sequence"],
                "schedule": result["schedule"],
                "convergence": result["convergence"],
                "final_mutation_rate": result["final_mutation_rate"]
            }
        }

    def _jsp_solve_baseline(self, args):
        """使用基线算法求解JSP"""
        processing_times = args.get("processing_times")
        machine_sequences = args.get("machine_sequences")
        algorithm_type = args.get("algorithm_type", "FCFS")

        model = JSPModel(processing_times, machine_sequences)

        if algorithm_type == "FCFS":
            solver = FCFSSolver(model)
        elif algorithm_type == "SPT":
            solver = SPTSolver(model)
        else:
            return {"success": False, "error": f"Unknown algorithm type: {algorithm_type}"}

        result = solver.solve()

        return {
            "success": True,
            "result": {
                "makespan": result["makespan"],
                "schedule": result["schedule"],
                "algorithm_type": algorithm_type
            }
        }

    def _jsp_calculate_kpi(self, args):
        """计算KPI指标"""
        schedule = args.get("schedule")
        num_machines = args.get("num_machines")
        num_jobs = args.get("num_jobs")
        baseline_makespan = args.get("baseline_makespan")

        calculator = MetricsCalculator()
        result = calculator.calculate_all(schedule, num_machines, num_jobs, baseline_makespan)

        return {
            "success": True,
            "result": result
        }

    def _jsp_draw_gantt(self, args):
        """生成调度甘特图"""
        schedule = args.get("schedule")
        num_machines = args.get("num_machines")
        save_path = args.get("save_path", "./gantt.png")
        title = args.get("title", "JSP调度甘特图")
        show = args.get("show", False)

        visualizer = Visualizer()
        saved_path = visualizer.draw_gantt(schedule, num_machines, save_path, title, show)

        return {
            "success": True,
            "result": {"save_path": saved_path}
        }


def main():
    """MCP 服务器主函数"""
    mcp_server = JSPSolverMCP()

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line.strip())

            if request.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": mcp_server.get_tools()
                }
            elif request.get("method") == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": mcp_server.call_tool(tool_name, arguments)
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -1, "message": "Unknown method"}
                }

            print(json.dumps(response))
            sys.stdout.flush()

        except json.JSONDecodeError:
            continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -2, "message": str(e)}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()