"""
贪婪解码器模块
采用左移贪婪解码法，将染色体序列转换为实际工序开工/完工时间表
"""


class GreedyDecoder:
    def decode(self, sequence, model):
        """
        左移贪婪解码
        
        将工序序列（染色体）转换为调度方案，保证满足所有约束：
        1. 工序顺序约束：同一工件的工序必须按顺序执行
        2. 机器独占约束：同一机器同一时刻只能加工一个工序
        
        Args:
            sequence: 工序序列（染色体），list[int]，每个元素为工件编号
            model: JSPModel实例
        
        Returns:
            dict: {
                'makespan': float,
                'operations': list[dict],  # 每个元素包含job_id, op_id, machine_id, start_time, end_time
                'machine_end_times': list[float]
            }
        """
        num_jobs = model.get_num_jobs()
        num_machines = model.get_num_machines()
        
        # 初始化各机器的可用时间
        machine_available_time = [0.0] * num_machines
        
        # 初始化各工件的下一道工序索引
        job_next_op = [0] * num_jobs
        
        # 用数组记录每个工件上一道工序的完工时间，避免O(n²)查找
        job_end_times = [0.0] * num_jobs
        
        # 存储工序调度结果
        operations = []
        
        # 按染色体顺序依次处理每个基因（工件编号）
        for job_id in sequence:
            op_id = job_next_op[job_id]
            machine_id = model.get_machine(job_id, op_id)
            processing_time = model.get_processing_time(job_id, op_id)
            
            # 计算最早开工时间：取机器可用时间和工件前道工序完工时间的较大值
            if op_id == 0:
                earliest_start = machine_available_time[machine_id]
            else:
                earliest_start = max(machine_available_time[machine_id], job_end_times[job_id])
            
            # 计算完工时间
            end_time = earliest_start + processing_time
            
            # 更新机器可用时间
            machine_available_time[machine_id] = end_time
            
            # 更新工件上一道工序完工时间
            job_end_times[job_id] = end_time
            
            # 更新工件的下一道工序索引
            job_next_op[job_id] += 1
            
            # 记录工序信息
            operations.append({
                'job_id': job_id,
                'op_id': op_id,
                'machine_id': machine_id,
                'start_time': earliest_start,
                'end_time': end_time,
            })
        
        # Makespan为所有机器完工时间的最大值
        makespan = max(machine_available_time)
        
        return {
            'makespan': makespan,
            'operations': operations,
            'machine_end_times': machine_available_time,
        }