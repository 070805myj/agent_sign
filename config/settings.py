"""
GA参数配置模块
所有参数从该文件读取，禁止在核心算法代码中使用魔法数字
"""

GA_CONFIG = {
    "population_size": 100,
    "max_generations": 300,
    "crossover_rate": 0.8,
    "mutation_rate_init": 0.1,
    "selection_pressure": 2.0,
    "elite_ratio": 0.05,
    "early_stop_generations": 50,
    "adaptive_mutation": True,
    "diversity_ratio_threshold": 0.2,
}

GLOBAL_CONFIG = {
    "random_seed": 42,
    "verbose": True,
    "save_results": True,
}

def get_ga_config():
    """获取GA算法参数配置"""
    return GA_CONFIG.copy()

def get_global_config():
    """获取全局参数配置"""
    return GLOBAL_CONFIG.copy()

def set_random_seed(seed):
    """设置全局随机种子"""
    GLOBAL_CONFIG["random_seed"] = seed