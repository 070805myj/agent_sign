"""
基线算法模块
包含FCFS（先来先服务）和SPT（最短加工时间优先）两种基线调度算法
"""

import heapq


class FCFSSolver:
    def __init__(self, model):
        """
        初始化串行FCFS求解器
        
        Args:
            model: JSPModel实例
        """
        self.model = model

    def solve(self):
        """
        执行串行FCFS算法
        
        所有工件默认0时刻到达，按ID升序排序，必须完整加工完当前工件的全部工序
        前一个工件完全完工后，才开启下一个工件加工
        
        Returns:
            dict: {
                'makespan': float,
                'schedule': dict  # 同decoder返回格式
            }
        """
        num_jobs = self.model.get_num_jobs()
        num_machines = self.model.get_num_machines()
        
        # 初始化各机器的可用时间
        machine_available_time = [0.0] * num_machines
        
        # 存储工序调度结果
        operations = []
        
        # 按工件ID升序处理每个工件
        for job_id in range(num_jobs):
            num_ops = self.model.get_num_operations(job_id)
            
            # 完整加工当前工件的全部工序（严格遵循工艺顺序）
            for op_id in range(num_ops):
                machine_id = self.model.get_machine(job_id, op_id)
                processing_time = self.model.get_processing_time(job_id, op_id)
                
                # 计算最早开工时间
                if op_id == 0:
                    earliest_start = machine_available_time[machine_id]
                else:
                    # 查找该工件前一道工序的完工时间
                    prev_op_end = 0.0
                    for op in operations:
                        if op['job_id'] == job_id and op['op_id'] == op_id - 1:
                            prev_op_end = op['end_time']
                            break
                    earliest_start = max(machine_available_time[machine_id], prev_op_end)
                
                # 计算完工时间
                end_time = earliest_start + processing_time
                
                # 更新机器可用时间
                machine_available_time[machine_id] = end_time
                
                # 记录工序信息
                operations.append({
                    'job_id': job_id,
                    'op_id': op_id,
                    'machine_id': machine_id,
                    'start_time': earliest_start,
                    'end_time': end_time,
                })
        
        makespan = max(machine_available_time)
        
        return {
            'makespan': makespan,
            'schedule': {
                'makespan': makespan,
                'operations': operations,
                'machine_end_times': machine_available_time,
            },
        }


class SPTSolver:
    def __init__(self, model):
        """
        初始化事件驱动SPT求解器
        
        Args:
            model: JSPModel实例
        """
        self.model = model

    def solve(self):
        """
        执行事件驱动SPT算法
        
        采用全局时间推进 + 最小堆事件驱动机制，仅在设备完工事件触发时为该设备分配工序
        
        Returns:
            dict: {
                'makespan': float,
                'schedule': dict
            }
        """
        num_jobs = self.model.get_num_jobs()
        num_machines = self.model.get_num_machines()
        
        # 初始化各机器的可用时间
        machine_available_time = [0.0] * num_machines
        
        # 记录每个工件的下一道待安排工序索引
        job_next_op = [0] * num_jobs
        
        # 记录每个工件最后一道已安排工序的完工时间
        job_last_end_time = [0.0] * num_jobs
        
        # 存储工序调度结果
        operations = []
        
        # 记录已安排的工序数量
        scheduled_ops = 0
        total_ops = self.model.get_total_operations()
        
        while scheduled_ops < total_ops:
            # 收集所有就绪工序（前驱工序已完成）
            ready_ops = []
            for job_id in range(num_jobs):
                op_id = job_next_op[job_id]
                if op_id < self.model.get_num_operations(job_id):
                    if job_last_end_time[job_id] == 0 or op_id > 0:
                        ready_ops.append((job_id, op_id))
            
            # 找到最早可用的机器
            min_machine_time = float('inf')
            for m_id in range(num_machines):
                if machine_available_time[m_id] < min_machine_time:
                    min_machine_time = machine_available_time[m_id]
            
            # 从就绪工序中选择可以在当前最早可用机器上加工的工序
            available_ops = []
            for job_id, op_id in ready_ops:
                machine_id = self.model.get_machine(job_id, op_id)
                if machine_available_time[machine_id] == min_machine_time:
                    processing_time = self.model.get_processing_time(job_id, op_id)
                    available_ops.append((processing_time, job_id, op_id, machine_id))
            
            if not available_ops:
                # 推进时间到最早就绪的工序所需的机器可用时间
                min_next_time = float('inf')
                for job_id, op_id in ready_ops:
                    machine_id = self.model.get_machine(job_id, op_id)
                    time_needed = machine_available_time[machine_id]
                    if time_needed < min_next_time:
                        min_next_time = time_needed
                
                if min_next_time != float('inf'):
                    for m_id in range(num_machines):
                        if machine_available_time[m_id] < min_next_time:
                            machine_available_time[m_id] = min_next_time
                    continue
                else:
                    break
            
            # 按SPT规则选择工时最短的工序
            available_ops.sort(key=lambda x: (x[0], x[1], x[2]))
            processing_time, job_id, op_id, machine_id = available_ops[0]
            
            # 计算开始时间和完工时间
            start_time = max(machine_available_time[machine_id], job_last_end_time[job_id])
            end_time = start_time + processing_time
            
            # 更新机器可用时间
            machine_available_time[machine_id] = end_time
            
            # 更新工件状态
            job_next_op[job_id] += 1
            job_last_end_time[job_id] = end_time
            
            # 记录工序信息
            operations.append({
                'job_id': job_id,
                'op_id': op_id,
                'machine_id': machine_id,
                'start_time': start_time,
                'end_time': end_time,
            })
            
            # 更新已安排工序数量
            scheduled_ops += 1
        
        makespan = max(machine_available_time)
        
        return {
            'makespan': makespan,
            'schedule': {
                'makespan': makespan,
                'operations': operations,
                'machine_end_times': machine_available_time,
            },
        }