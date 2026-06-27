import tkinter as tk
from tkinter import ttk, messagebox
from gui.framework import BaseTab, create_section_header
from gui.i18n import t, set_language, get_language
from gui.settings import Settings


class SettingsTab(BaseTab):
    """设置标签页"""

    def __init__(self, parent, context):
        super().__init__(parent, context, t("settings"))
        self.settings = Settings()

    def _save_settings(self):
        self.settings.set_language(self.language_var.get())
        self.settings.set_font_size(int(self.font_size_var.get()))
        self.settings.save()
        messagebox.showinfo("Settings", t("settings_saved"))
        set_language(self.language_var.get())
        self.context.set_needs_refresh(True)

    def build(self):
        frame = super().build()
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 语言设置
        create_section_header(frame, t("language"))
        lang_frame = ttk.Frame(frame)
        self.language_var = tk.StringVar(value=self.settings.get_language())
        ttk.Radiobutton(lang_frame, text="English", variable=self.language_var, value="en").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(lang_frame, text="中文", variable=self.language_var, value="zh").pack(side=tk.LEFT, padx=10)
        lang_frame.pack(pady=10)

        # 字体大小设置
        create_section_header(frame, t("font_size"))
        font_frame = ttk.Frame(frame)
        ttk.Label(font_frame, text=t("font_size")).pack(side=tk.LEFT, padx=5)
        self.font_size_var = tk.IntVar(value=self.settings.get_font_size())
        font_sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20]
        ttk.Combobox(font_frame, textvariable=self.font_size_var, values=font_sizes, width=5).pack(side=tk.LEFT, padx=5)
        font_frame.pack(pady=10)

        # 保存按钮
        ttk.Button(frame, text="Save Settings", command=self._save_settings).pack(pady=20)

        # 提示信息
        ttk.Label(frame, text=t("font_size_tip"), foreground="gray").pack(pady=10)

        return frame
