"""
JSP问题模型定义模块
包含JSPModel类，负责模型实例化与约束校验
"""


class JSPModel:
    def __init__(self, processing_times, machine_sequences):
        """
        初始化JSP问题模型
        
        Args:
            processing_times: 二维数组，processing_times[j][k] 为工件j第k道工序的加工时间
            machine_sequences: 二维数组，machine_sequences[j][k] 为工件j第k道工序的机器编号（0-indexed）
        
        Raises:
            ValueError: 输入参数不合法时抛出
        """
        self.processing_times = processing_times
        self.machine_sequences = machine_sequences
        self.num_jobs = len(processing_times)
        self.num_machines = self._infer_num_machines()
        self.validate()

    def _infer_num_machines(self):
        """从机器序列中推断机器数量"""
        if not self.machine_sequences:
            return 0
        max_machine = 0
        for seq in self.machine_sequences:
            if seq:
                current_max = max(seq)
                if current_max > max_machine:
                    max_machine = current_max
        return max_machine + 1

    def validate(self):
        """验证模型参数合法性（工时非负、工序连续、设备有效等）"""
        if not self.processing_times or not self.machine_sequences:
            raise ValueError("processing_times 和 machine_sequences 不能为空")

        if len(self.processing_times) != len(self.machine_sequences):
            raise ValueError(
                f"工件数量不一致: processing_times有{len(self.processing_times)}个工件, "
                f"machine_sequences有{len(self.machine_sequences)}个工件"
            )

        for job_id, (times, machines) in enumerate(
            zip(self.processing_times, self.machine_sequences)
        ):
            if len(times) != len(machines):
                raise ValueError(
                    f"工件{job_id}的工序数量不一致: 加工时间{len(times)}道, 机器序列{len(machines)}道"
                )

            for op_id, (time, machine) in enumerate(zip(times, machines)):
                if time <= 0:
                    raise ValueError(
                        f"工件{job_id}第{op_id}道工序加工时间必须大于0, 当前值: {time}"
                    )
                if machine < 0:
                    raise ValueError(
                        f"工件{job_id}第{op_id}道工序机器编号必须非负, 当前值: {machine}"
                    )

    def get_num_jobs(self):
        """返回工件数量"""
        return self.num_jobs

    def get_num_machines(self):
        """返回机器数量"""
        return self.num_machines

    def get_processing_time(self, job_id, op_id):
        """
        获取指定工件指定工序的加工时间
        
        Args:
            job_id: 工件编号（0-indexed）
            op_id: 工序编号（0-indexed）
        
        Returns:
            float: 加工时间
        """
        return self.processing_times[job_id][op_id]

    def get_machine(self, job_id, op_id):
        """
        获取指定工件指定工序所在的机器编号
        
        Args:
            job_id: 工件编号（0-indexed）
            op_id: 工序编号（0-indexed）
        
        Returns:
            int: 机器编号（0-indexed）
        """
        return self.machine_sequences[job_id][op_id]

    def get_num_operations(self, job_id):
        """
        获取指定工件的工序总数
        
        Args:
            job_id: 工件编号（0-indexed）
        
        Returns:
            int: 工序数量
        """
        return len(self.processing_times[job_id])

    def get_total_operations(self):
        """获取所有工件的工序总数"""
        return sum(self.get_num_operations(j) for j in range(self.num_jobs))