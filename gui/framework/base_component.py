from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk


class BaseComponent(ABC):
    """Tkinter组件基类"""

    def __init__(self, parent, context):
        self.parent = parent
        self.context = context
        self.frame = None
        self._widgets = {}

    def get_widget(self, key):
        return self._widgets.get(key)

    def set_widget(self, key, widget):
        self._widgets[key] = widget

    @abstractmethod
    def build(self):
        """构建组件UI"""
        pass

    def destroy(self):
        """销毁组件"""
        if self.frame:
            self.frame.destroy()
            self.frame = None
        self._widgets.clear()


class BaseTab(BaseComponent):
    """标签页基类"""

    def __init__(self, parent, context, title):
        super().__init__(parent, context)
        self.title = title

    def build(self):
        self.frame = ttk.Frame(self.parent)
        return self.frame
