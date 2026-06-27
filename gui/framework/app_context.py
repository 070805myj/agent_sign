import threading
import queue
from datetime import datetime


class AppContext:
    """应用上下文 - 管理共享状态"""

    def __init__(self):
        self.queue = queue.Queue()
        self.is_running = False
        self.current_task = None

        self.ga_result = None
        self.fcfs_result = None
        self.spt_result = None

        self.log_lines = []
        self._last_data = None
        self._needs_refresh = False

        self._root = None

    def set_root(self, root):
        self._root = root

    def log(self, message: str):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"
        self.log_lines.append(line)
        if len(self.log_lines) > 1000:
            self.log_lines = self.log_lines[-1000:]
        self.queue.put(("log", line))

    def set_running(self, running: bool):
        """设置运行状态"""
        self.is_running = running
        if running:
            self.current_task = threading.current_thread().name
        else:
            self.current_task = None

    def needs_refresh(self) -> bool:
        """检查是否需要刷新UI"""
        return self._needs_refresh

    def set_needs_refresh(self, value: bool = True):
        """设置刷新标志"""
        self._needs_refresh = value

    def safe_update(self, callback, *args, **kwargs):
        """线程安全的UI更新方法"""
        if self._root:
            self._root.after(0, lambda: callback(*args, **kwargs))
