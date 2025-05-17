import tkinter as tk
from tkinter import ttk
import time

class AutoScrollMessageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("每秒添加一行文本 - 可滚动Message")

        # 创建滚动区域框架
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # 创建 Canvas，用于支持 Message 自由扩展高度
        self.canvas = tk.Canvas(self.frame)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 内容初始化
        self.text_lines = []
        self.add_text_line()

    def add_text_line(self):
        line = time.strftime("时间 %H:%M:%S") + " - 新的一行文本"
        self.text_lines.append(line)

        # 创建新的 Message 控件并添加到 Frame
        message = tk.Message(self.scrollable_frame, text=line, width=500, anchor='w', justify='left')
        message.pack(anchor='w', padx=10, pady=2)

        # 自动滚动到底部
        self.root.after(100, lambda: self.canvas.yview_moveto(1.0))

        # 每秒添加一行
        self.root.after(1000, self.add_text_line)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoScrollMessageApp(root)
    root.mainloop()
