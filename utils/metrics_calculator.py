"""
KPI指标计算模块
包含Makespan、总完工时间、平均流程时间、机器利用率等核心指标的计算
"""

import math


class MetricsCalculator:
    def calculate_makespan(self, schedule):
        """
        计算Makespan
        
        Args:
            schedule: 调度方案，包含operations列表
            
        Returns:
            float: Makespan（最大完工时间）
        """
        if not schedule or 'operations' not in schedule:
            return 0.0
        
        operations = schedule['operations']
        if not operations:
            return 0.0
        
        return max(op['end_time'] for op in operations)
    
    def calculate_total_completion_time(self, schedule, num_jobs):
        """
        计算总完工时间
        
        Args:
            schedule: 调度方案，包含operations列表
            num_jobs: 工件数量
            
        Returns:
            float: 所有工件完工时间之和
        """
        if not schedule or 'operations' not in schedule:
            return 0.0
        
        operations = schedule['operations']
        if not operations:
            return 0.0
        
        # 记录每个工件的最后一道工序完工时间
        job_completion_times = {}
        for op in operations:
            job_id = op['job_id']
            end_time = op['end_time']
            if job_id not in job_completion_times or end_time > job_completion_times[job_id]:
                job_completion_times[job_id] = end_time
        
        # 确保所有工件都有完工时间记录
        total = 0.0
        for job_id in range(num_jobs):
            total += job_completion_times.get(job_id, 0.0)
        
        return total
    
    def calculate_avg_flow_time(self, schedule, num_jobs):
        """
        计算平均流程时间
        
        平均流程时间 = 总完工时间 / 工件数量（标准JSP中所有工件到达时间为0）
        
        Args:
            schedule: 调度方案，包含operations列表
            num_jobs: 工件数量
            
        Returns:
            float: 平均流程时间
        """
        if num_jobs <= 0:
            return 0.0
        
        total_completion_time = self.calculate_total_completion_time(schedule, num_jobs)
        return total_completion_time / num_jobs
    
    def calculate_machine_utilization(self, schedule, num_machines, makespan):
        """
        计算机器平均利用率
        
        利用率 = 所有机器的总加工时间 / (机器数量 × Makespan)
        
        Args:
            schedule: 调度方案，包含operations列表
            num_machines: 机器数量
            makespan: Makespan
            
        Returns:
            float: 机器平均利用率（0-1之间）
        """
        if num_machines <= 0 or makespan <= 0:
            return 0.0
        
        if not schedule or 'operations' not in schedule:
            return 0.0
        
        operations = schedule['operations']
        if not operations:
            return 0.0
        
        # 计算每个机器的总加工时间
        machine_total_time = [0.0] * num_machines
        for op in operations:
            machine_id = op['machine_id']
            processing_time = op['end_time'] - op['start_time']
            machine_total_time[machine_id] += processing_time
        
        # 总加工时间
        total_processing_time = sum(machine_total_time)
        
        # 机器平均利用率
        return total_processing_time / (num_machines * makespan)
    
    def calculate_total_idle_time(self, schedule, num_machines, makespan):
        """
        计算机器总空闲时间
        
        总空闲时间 = 机器数量 × Makespan - 所有机器的总加工时间
        
        Args:
            schedule: 调度方案，包含operations列表
            num_machines: 机器数量
            makespan: Makespan
            
        Returns:
            float: 所有机器空闲时间之和
        """
        if num_machines <= 0 or makespan <= 0:
            return 0.0
        
        if not schedule or 'operations' not in schedule:
            return 0.0
        
        operations = schedule['operations']
        if not operations:
            return num_machines * makespan
        
        # 计算每个机器的总加工时间
        machine_total_time = [0.0] * num_machines
        for op in operations:
            machine_id = op['machine_id']
            processing_time = op['end_time'] - op['start_time']
            machine_total_time[machine_id] += processing_time
        
        # 总加工时间
        total_processing_time = sum(machine_total_time)
        
        # 总空闲时间
        return num_machines * makespan - total_processing_time
    
    def calculate_load_variance(self, schedule, num_machines):
        """
        计算机器负载方差（基于总加工时间）
        
        负载方差 = (1/m) × Σ(T_i - T_avg)^2
        
        Args:
            schedule: 调度方案，包含operations列表
            num_machines: 机器数量
            
        Returns:
            float: 机器负载方差
        """
        if num_machines <= 0:
            return 0.0
        
        if not schedule or 'operations' not in schedule:
            return 0.0
        
        operations = schedule['operations']
        if not operations:
            return 0.0
        
        # 计算每个机器的总加工时间
        machine_total_time = [0.0] * num_machines
        for op in operations:
            machine_id = op['machine_id']
            processing_time = op['end_time'] - op['start_time']
            machine_total_time[machine_id] += processing_time
        
        # 计算平均负载
        avg_load = sum(machine_total_time) / num_machines
        
        # 计算方差
        variance = sum((t - avg_load) ** 2 for t in machine_total_time) / num_machines
        
        return variance
    
    def calculate_optimization_rate(self, ga_makespan, baseline_makespan):
        """
        计算优化率（百分比）
        
        优化率 = (基线Makespan - GA Makespan) / 基线Makespan × 100%
        
        Args:
            ga_makespan: GA算法求解的Makespan
            baseline_makespan: 基线算法求解的Makespan
            
        Returns:
            float: 优化率（百分比）
        """
        if baseline_makespan <= 0:
            return 0.0
        
        return (baseline_makespan - ga_makespan) / baseline_makespan * 100.0
    
    def calculate_all(self, schedule, num_machines, num_jobs, baseline_makespan=None):
        """
        计算所有KPI指标，返回完整字典
        
        Args:
            schedule: 调度方案，包含operations列表
            num_machines: 机器数量
            num_jobs: 工件数量
            baseline_makespan: 基线Makespan（可选）
            
        Returns:
            dict: 包含所有KPI指标的字典
        """
        makespan = self.calculate_makespan(schedule)
        total_completion_time = self.calculate_total_completion_time(schedule, num_jobs)
        avg_flow_time = self.calculate_avg_flow_time(schedule, num_jobs)
        machine_utilization = self.calculate_machine_utilization(schedule, num_machines, makespan)
        total_idle_time = self.calculate_total_idle_time(schedule, num_machines, makespan)
        load_variance = self.calculate_load_variance(schedule, num_machines)
        
        result = {
            'makespan': makespan,
            'total_completion_time': total_completion_time,
            'avg_flow_time': avg_flow_time,
            'machine_utilization': machine_utilization,
            'total_idle_time': total_idle_time,
            'load_variance': load_variance,
        }
        
        if baseline_makespan is not None:
            optimization_rate = self.calculate_optimization_rate(makespan, baseline_makespan)
            result['optimization_rate'] = optimization_rate
        
        return result