"""
遗传算法模块
实现基于IPOX交叉和工件块移位变异的改进遗传算法
"""

import random
import math

from core.decoder import GreedyDecoder


class GeneticAlgorithm:
    def __init__(self, model, config):
        """
        初始化遗传算法
        
        Args:
            model: JSPModel实例
            config: 参数字典，包含population_size, max_generations, crossover_rate,
                    mutation_rate_init, selection_pressure, elite_ratio,
                    early_stop_generations, adaptive_mutation, diversity_ratio_threshold,
                    random_seed等
        """
        self.model = model
        self.config = config
        self.decoder = GreedyDecoder()
        
        # 初始化随机种子
        random_seed = config.get("random_seed", 42)
        random.seed(random_seed)
        
        # 算法参数
        self.population_size = config.get("population_size", 100)
        self.max_generations = config.get("max_generations", 300)
        self.crossover_rate = config.get("crossover_rate", 0.8)
        self.mutation_rate = config.get("mutation_rate_init", 0.1)
        self.mutation_rate_init = self.mutation_rate
        self.selection_pressure = config.get("selection_pressure", 2.0)
        self.elite_ratio = config.get("elite_ratio", 0.05)
        self.early_stop_generations = config.get("early_stop_generations", 50)
        self.adaptive_mutation = config.get("adaptive_mutation", True)
        self.diversity_ratio_threshold = config.get("diversity_ratio_threshold", 0.2)
        
        # 状态变量
        self.population = []
        self.fitness_values = []
        self.convergence = []
        self.best_makespan = float('inf')
        self.best_sequence = None
        self._fitness_cache = {}
        
        # 自适应变异相关变量
        self.baseline_std = None
        self.stagnant_generations = 0
        self.last_best_makespan = float('inf')
    
    def _generate_initial_sequence(self):
        """
        生成合法的初始染色体序列
        
        Returns:
            list[int]: 工序序列，每个元素为工件编号
        """
        num_jobs = self.model.get_num_jobs()
        sequence = []
        
        # 为每个工件添加其工序数目的基因
        for job_id in range(num_jobs):
            num_ops = self.model.get_num_operations(job_id)
            sequence.extend([job_id] * num_ops)
        
        # 随机打乱序列
        random.shuffle(sequence)
        return sequence
    
    def _initialize_population(self):
        """初始化种群"""
        self.population = [
            self._generate_initial_sequence()
            for _ in range(self.population_size)
        ]
    
    def _calculate_fitness(self, sequence):
        """
        计算适应度值（带缓存）
        
        Args:
            sequence: 工序序列
            
        Returns:
            float: 适应度值（Makespan的倒数）
        """
        # 使用元组作为缓存键
        seq_key = tuple(sequence)
        if seq_key in self._fitness_cache:
            return self._fitness_cache[seq_key]
        
        result = self.decoder.decode(sequence, self.model)
        makespan = result['makespan']
        fitness = 1.0 / makespan
        self._fitness_cache[seq_key] = fitness
        return fitness
    
    def _evaluate_population(self):
        """评估种群中所有个体的适应度"""
        self.fitness_values = [
            self._calculate_fitness(seq)
            for seq in self.population
        ]
    
    def _select_parents(self):
        """
        截断选择：按适应度降序排序，选择前T个个体作为父代池
        
        Returns:
            list[list[int]]: 父代池
        """
        # 按适应度降序排序
        sorted_indices = sorted(
            range(self.population_size),
            key=lambda i: -self.fitness_values[i]
        )
        
        # 计算截断比例
        truncation_ratio = 1.0 / self.selection_pressure
        
        # 选择前T个个体
        num_parents = max(2, int(self.population_size * truncation_ratio))
        parent_indices = sorted_indices[:num_parents]
        
        return [self.population[i] for i in parent_indices]
    
    def _ipox_crossover(self, parent1, parent2):
        """
        IPOX交叉算子（Improved Precedence Preserving Crossover）
        
        Args:
            parent1: 父代1的染色体序列
            parent2: 父代2的染色体序列
            
        Returns:
            tuple: (子代1, 子代2)
        """
        num_jobs = self.model.get_num_jobs()
        
        # 随机将工件划分为两个互不相交的子集G1、G2
        jobs = list(range(num_jobs))
        random.shuffle(jobs)
        split_idx = num_jobs // 2
        G1 = set(jobs[:split_idx])
        G2 = set(jobs[split_idx:])
        
        # 生成子代1：保留父代1中属于G1的基因，填充父代2中属于G2的基因
        child1 = []
        # 记录父代2中G2基因的出现顺序
        g2_from_p2 = [gene for gene in parent2 if gene in G2]
        g2_idx = 0
        
        for gene in parent1:
            if gene in G1:
                child1.append(gene)
            else:
                child1.append(g2_from_p2[g2_idx])
                g2_idx += 1
        
        # 生成子代2：保留父代2中属于G2的基因，填充父代1中属于G1的基因
        child2 = []
        # 记录父代1中G1基因的出现顺序
        g1_from_p1 = [gene for gene in parent1 if gene in G1]
        g1_idx = 0
        
        for gene in parent2:
            if gene in G2:
                child2.append(gene)
            else:
                child2.append(g1_from_p1[g1_idx])
                g1_idx += 1
        
        return child1, child2
    
    def _job_block_shift_mutation(self, sequence):
        """
        工件块移位变异
        
        Args:
            sequence: 原始染色体序列
            
        Returns:
            list[int]: 变异后的染色体序列
        """
        num_jobs = self.model.get_num_jobs()
        
        # 随机选择一个工件
        job_id = random.randint(0, num_jobs - 1)
        
        # 从原染色体中移除所有属于工件j的基因，保留原有相对顺序
        remaining = []
        job_block = []
        for gene in sequence:
            if gene == job_id:
                job_block.append(gene)
            else:
                remaining.append(gene)
        
        # 随机选择插入位置（共剩余长度+1个可选位置）
        insert_pos = random.randint(0, len(remaining))
        
        # 将工件块插入到选定位置
        new_sequence = remaining[:insert_pos] + job_block + remaining[insert_pos:]
        
        return new_sequence
    
    def _calculate_diversity(self):
        """
        计算种群多样性（适应度标准差）
        
        Returns:
            float: 适应度标准差
        """
        if len(self.fitness_values) < 2:
            return 0.0
        
        mean_fitness = sum(self.fitness_values) / len(self.fitness_values)
        variance = sum((f - mean_fitness) ** 2 for f in self.fitness_values) / len(self.fitness_values)
        return math.sqrt(variance)
    
    def _update_adaptive_mutation_rate(self, generation):
        """
        更新自适应变异率
        
        Args:
            generation: 当前代数
        """
        if not self.adaptive_mutation:
            return
        
        # 计算当前种群适应度标准差
        current_std = self._calculate_diversity()
        
        # 前10代收集基线标准差
        if generation <= 10:
            if self.baseline_std is None:
                self.baseline_std = [current_std]
            else:
                self.baseline_std.append(current_std)
            return
        
        # 取前10代标准差的中位数作为基准
        if generation == 11:
            self.baseline_std = sorted(self.baseline_std)
            self.baseline_std = self.baseline_std[len(self.baseline_std) // 2]
        
        # 检查是否需要提升变异率
        if current_std < self.diversity_ratio_threshold * self.baseline_std:
            self.stagnant_generations += 1
        else:
            self.stagnant_generations = 0
        
        # 检查最优解是否停滞
        current_best = max(self.fitness_values)
        if abs(current_best - self.last_best_makespan) < 1e-10:
            self.stagnant_generations += 1
        else:
            self.last_best_makespan = current_best
            self.stagnant_generations = 0
        
        # 触发条件：连续20代多样性低于阈值 或 最优解连续early_stop_generations代无更新
        if self.stagnant_generations >= 20 or self.stagnant_generations >= self.early_stop_generations:
            self.mutation_rate = min(0.5, self.mutation_rate * 1.5)
            self.stagnant_generations = 0
        
        # 回落机制：多样性恢复后指数衰减
        if current_std > 1.5 * self.diversity_ratio_threshold * self.baseline_std:
            self.mutation_rate = max(self.mutation_rate_init, self.mutation_rate * 0.99)
    
    def _reproduce(self, parents):
        """
        繁殖：交叉和变异
        
        Args:
            parents: 父代池
            
        Returns:
            list[list[int]]: 新一代种群（不含精英个体）
        """
        new_population = []
        num_parents = len(parents)
        
        # 计算精英数量
        num_elites = max(1, int(self.population_size * self.elite_ratio))
        num_offspring = self.population_size - num_elites
        
        # 生成子代
        while len(new_population) < num_offspring:
            # 随机选择两个父代
            parent1 = parents[random.randint(0, num_parents - 1)]
            parent2 = parents[random.randint(0, num_parents - 1)]
            
            # 交叉
            if random.random() < self.crossover_rate:
                child1, child2 = self._ipox_crossover(parent1, parent2)
            else:
                child1, child2 = parent1[:], parent2[:]
            
            # 变异
            if random.random() < self.mutation_rate:
                child1 = self._job_block_shift_mutation(child1)
            if random.random() < self.mutation_rate:
                child2 = self._job_block_shift_mutation(child2)
            
            new_population.append(child1)
            if len(new_population) < num_offspring:
                new_population.append(child2)
        
        return new_population
    
    def _elitism(self):
        """
        精英保留：选择适应度最高的个体直接保留到下一代
        
        Returns:
            list[list[int]]: 精英个体列表
        """
        num_elites = max(1, int(self.population_size * self.elite_ratio))
        
        # 按适应度降序排序
        sorted_indices = sorted(
            range(self.population_size),
            key=lambda i: -self.fitness_values[i]
        )
        
        # 返回精英个体
        return [self.population[i][:] for i in sorted_indices[:num_elites]]
    
    def solve(self):
        """
        执行遗传算法求解
        
        Returns:
            dict: {
                'makespan': float,
                'best_sequence': list[int],
                'schedule': dict,         # 同decoder返回格式
                'convergence': list[float],  # 每代最优Makespan
                'final_population': list,
                'final_mutation_rate': float
            }
        """
        verbose = self.config.get("verbose", True)
        
        # 初始化种群
        self._initialize_population()
        
        # 评估初始种群
        self._evaluate_population()
        
        # 记录初始最优解
        best_idx = max(range(self.population_size), key=lambda i: self.fitness_values[i])
        self.best_makespan = 1.0 / self.fitness_values[best_idx]
        self.best_sequence = self.population[best_idx][:]
        self.last_best_makespan = self.fitness_values[best_idx]
        
        if verbose:
            print(f"初始种群最优Makespan: {self.best_makespan:.2f}")
        
        # 记录收敛曲线
        self.convergence = [self.best_makespan]
        
        # 迭代进化
        no_improve_count = 0
        for generation in range(1, self.max_generations + 1):
            # 更新自适应变异率
            self._update_adaptive_mutation_rate(generation)
            
            # 选择父代
            parents = self._select_parents()
            
            # 繁殖（交叉+变异）
            offspring = self._reproduce(parents)
            
            # 精英保留
            elites = self._elitism()
            
            # 组合新种群
            self.population = elites + offspring
            
            # 评估新种群
            self._evaluate_population()
            
            # 更新最优解
            best_idx = max(range(self.population_size), key=lambda i: self.fitness_values[i])
            current_best_makespan = 1.0 / self.fitness_values[best_idx]
            current_best_sequence = self.population[best_idx][:]
            
            # 记录收敛曲线
            self.convergence.append(current_best_makespan)
            
            # 检查最优解是否更新
            if current_best_makespan < self.best_makespan:
                self.best_makespan = current_best_makespan
                self.best_sequence = current_best_sequence
                no_improve_count = 0
                
                if verbose:
                    print(f"第{generation}代: Makespan = {self.best_makespan:.2f}")
            else:
                no_improve_count += 1
            
            # 早停检查
            if no_improve_count >= self.early_stop_generations:
                if verbose:
                    print(f"第{generation}代: 连续{self.early_stop_generations}代无改进，触发早停")
                break
        
        # 解码最优解
        best_schedule = self.decoder.decode(self.best_sequence, self.model)
        
        if verbose:
            print(f"最终最优Makespan: {self.best_makespan:.2f}")
        
        return {
            'makespan': self.best_makespan,
            'best_sequence': self.best_sequence,
            'schedule': best_schedule,
            'convergence': self.convergence,
            'final_population': self.population,
            'final_mutation_rate': self.mutation_rate,
        }

    # 在 GeneticAlgorithm 类中添加此方法
    def solve_with_progress(self, log_callback, progress_queue):
        """
        带进度回调的求解方法，用于GUI界面

        参数:
            log_callback: 日志回调函数 log(message)
            progress_queue: 进度队列，放入 ("progress", percent)
        """
        self._initialize_population()
        self._evaluate_population()

        best_idx = max(range(self.population_size), key=lambda i: self.fitness_values[i])
        self.best_makespan = 1.0 / self.fitness_values[best_idx]
        self.best_sequence = self.population[best_idx][:]
        self.convergence = [self.best_makespan]
        no_improve_count = 0

        for generation in range(1, self.max_generations + 1):
            self._update_adaptive_mutation_rate(generation)
            parents = self._select_parents()
            offspring = self._reproduce(parents)
            elites = self._elitism()
            self.population = elites + offspring
            self._evaluate_population()

            best_idx = max(range(self.population_size), key=lambda i: self.fitness_values[i])
            current_best_makespan = 1.0 / self.fitness_values[best_idx]
            current_best_sequence = self.population[best_idx][:]
            self.convergence.append(current_best_makespan)

            if current_best_makespan < self.best_makespan:
                self.best_makespan = current_best_makespan
                self.best_sequence = current_best_sequence
                no_improve_count = 0
                log_callback(f"Gen {generation}: Makespan = {self.best_makespan:.2f}")
            else:
                no_improve_count += 1

            progress = int(generation / self.max_generations * 100)
            progress_queue.put(("progress", progress))

            if no_improve_count >= self.early_stop_generations:
                log_callback(f"Gen {generation}: Early stop after {self.early_stop_generations} generations")
                break

        best_schedule = self.decoder.decode(self.best_sequence, self.model)
        return {
            'makespan': self.best_makespan,
            'best_sequence': self.best_sequence,
            'schedule': best_schedule,
            'convergence': self.convergence,
            'final_mutation_rate': self.mutation_rate,
        }