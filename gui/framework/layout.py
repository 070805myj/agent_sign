import tkinter as tk
from tkinter import ttk


def create_section_header(parent, text, **pack_options):
    """创建分节标题"""
    label = ttk.Label(parent, text=text, font=('Arial', 10, 'bold'))
    label.pack(**pack_options)
    return label


def create_labeled_input(parent, label_text, input_type='text', **kwargs):
    """创建带标签的输入框"""
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=label_text).pack(side=tk.LEFT, padx=5)

    if input_type == 'int':
        var = tk.IntVar(value=kwargs.get('default', 0))
        entry = ttk.Entry(frame, textvariable=var, width=kwargs.get('width', 10))
    elif input_type == 'float':
        var = tk.DoubleVar(value=kwargs.get('default', 0.0))
        entry = ttk.Entry(frame, textvariable=var, width=kwargs.get('width', 10))
    else:
        var = tk.StringVar(value=kwargs.get('default', ''))
        entry = ttk.Entry(frame, textvariable=var, width=kwargs.get('width', 20))

    entry.pack(side=tk.LEFT, padx=5)
    frame.pack(**kwargs.get('pack', {'padx': 10, 'pady': 2, 'fill': tk.X}))

    return frame, var, entry


def create_button(parent, text, command, **kwargs):
    """创建按钮"""
    btn = ttk.Button(parent, text=text, command=command, **kwargs)
    btn.pack(**kwargs.get('pack', {'padx': 5, 'pady': 5}))
    return btn


def create_scrolled_text(parent, height=10, **kwargs):
    """创建滚动文本框"""
    text_frame = ttk.Frame(parent)
    text_widget = tk.Text(text_frame, height=height, width=kwargs.get('width', 60),
                          font=('Consolas', 9), wrap=tk.WORD)
    scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)

    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_frame.pack(**kwargs.get('pack', {'padx': 5, 'pady': 5, 'fill': tk.BOTH, 'expand': True}))

    return text_frame, text_widget
