"""
可视化模块
包含甘特图、收敛曲线、对比柱状图的绘制功能
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.weight'] = 'normal'


class Visualizer:
    def draw_gantt(self, schedule, num_machines, save_path, title="JSP调度甘特图", show=False):
        """
        绘制调度甘特图，按机器分行，不同工件不同颜色
        
        Args:
            schedule: 调度方案，包含operations列表
            num_machines: 机器数量
            save_path: 保存路径
            title: 图表标题
            show: 是否显示图表
            
        Returns:
            str: 保存路径
        """
        if not schedule or 'operations' not in schedule:
            raise ValueError("调度方案为空")
        
        operations = schedule['operations']
        if not operations:
            raise ValueError("调度方案中无工序信息")
        
        # 定义颜色映射（为不同工件分配不同颜色）
        colors = plt.cm.tab20.colors

        # 统计工件数量，决定是否显示文字标注
        unique_jobs = sorted(set(op['job_id'] for op in operations))
        num_jobs = len(unique_jobs)
        show_text = num_jobs <= 15  # 工件数超过15时不显示文字标注，避免遮挡

        # 创建图形
        fig, ax = plt.subplots(figsize=(14, max(6, 0.6 * num_machines)))

        # 按机器分组工序
        machine_ops = [[] for _ in range(num_machines)]
        for op in operations:
            machine_ops[op['machine_id']].append(op)

        # 绘制每个机器的工序条
        for machine_id, ops in enumerate(machine_ops):
            # 按开始时间排序
            ops.sort(key=lambda x: x['start_time'])

            for op in ops:
                start_time = op['start_time']
                duration = op['end_time'] - op['start_time']
                job_id = op['job_id']

                # 创建矩形补丁
                rect = patches.Rectangle(
                    (start_time, machine_id - 0.3),
                    duration,
                    0.6,
                    facecolor=colors[job_id % len(colors)],
                    edgecolor='black',
                    linewidth=0.5
                )
                ax.add_patch(rect)

                # 在矩形中央添加文字标注（仅当工件数较少时）
                if show_text:
                    center_x = start_time + duration / 2
                    center_y = machine_id
                    ax.text(
                        center_x,
                        center_y,
                        f"J{job_id+1}O{op['op_id']+1}",
                        ha='center',
                        va='center',
                        fontsize=7,
                        color='white' if duration > 3 else 'black'
                    )

        # 设置坐标轴
        makespan = max(op['end_time'] for op in operations)
        ax.set_xlim(0, makespan * 1.05)
        ax.set_ylim(-0.5, num_machines - 0.5)

        # 设置Y轴标签（机器编号）
        ax.set_yticks(range(num_machines))
        ax.set_yticklabels([f"机器{i+1}" for i in range(num_machines)])

        # 设置标题和标签
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel("时间", fontsize=12)
        ax.set_ylabel("机器", fontsize=12)

        # 添加网格
        ax.grid(True, axis='x', linestyle='--', alpha=0.7)

        # 添加图例 - 多列显示避免遮挡
        handles = []
        for job_id in unique_jobs:
            handle = plt.Line2D(
                [0], [0],
                color=colors[job_id % len(colors)],
                linewidth=6,
                label=f"工件{job_id+1}"
            )
            handles.append(handle)
        # 工件数多时使用多列图例，放在图表下方
        ncol = min(num_jobs, 10) if num_jobs > 10 else num_jobs
        ax.legend(handles=handles, loc='upper center',
                  bbox_to_anchor=(0.5, -0.08 - 0.02 * (num_machines > 20)),
                  ncol=ncol, fontsize=8, frameon=True)
        
        # 保存图片
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        # 显示图表（可选）
        if show:
            plt.show()
        
        plt.close()
        
        return save_path
    
    def draw_convergence(self, convergence, save_path, title="收敛曲线", show=False):
        """
        绘制GA迭代收敛曲线，横轴为代数，纵轴为Makespan
        
        Args:
            convergence: 每代最优Makespan列表
            save_path: 保存路径
            title: 图表标题
            show: 是否显示图表
            
        Returns:
            str: 保存路径
        """
        if not convergence:
            raise ValueError("收敛数据为空")
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 绘制收敛曲线
        ax.plot(
            range(len(convergence)),
            convergence,
            marker='o',
            markersize=3,
            linewidth=2,
            color='#1f77b4',
            label='最优Makespan'
        )
        
        # 设置标题和标签
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel("迭代代数", fontsize=12)
        ax.set_ylabel("Makespan", fontsize=12)
        
        # 添加网格
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # 添加图例
        ax.legend()
        
        # 保存图片
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        # 显示图表（可选）
        if show:
            plt.show()
        
        plt.close()
        
        return save_path
    
    def draw_comparison_bar(self, ga_makespan, fcfs_makespan, spt_makespan,
                            save_path, title="调度方案对比", show=False):
        """
        绘制三种算法Makespan对比柱状图
        
        Args:
            ga_makespan: GA算法的Makespan
            fcfs_makespan: FCFS算法的Makespan
            spt_makespan: SPT算法的Makespan
            save_path: 保存路径
            title: 图表标题
            show: 是否显示图表
            
        Returns:
            str: 保存路径
        """
        # 数据
        algorithms = ['FCFS', 'SPT', 'GA']
        makespans = [fcfs_makespan, spt_makespan, ga_makespan]
        
        # 颜色设置
        colors = ['#ff7f0e', '#2ca02c', '#1f77b4']
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 绘制柱状图
        bars = ax.bar(algorithms, makespans, color=colors, edgecolor='black', linewidth=1)
        
        # 在每个柱子上方标注数值
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f'{height:.1f}',
                ha='center',
                va='bottom',
                fontsize=10,
                fontweight='bold'
            )
        
        # 设置标题和标签
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel("Makespan", fontsize=12)
        
        # 添加网格
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # 保存图片
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        # 显示图表（可选）
        if show:
            plt.show()
        
        plt.close()
        
        return save_path