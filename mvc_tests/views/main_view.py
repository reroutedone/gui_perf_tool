# views/main_view.py
import tkinter as tk

class MainView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.text = tk.Text(self)
        self.text.pack()
        self.submit_btn = tk.Button(self, text="提交", command=self.on_submit)
        self.submit_btn.pack()

    def on_submit(self):
        msg = self.text.get("1.0", "end").strip()
        self.controller.handle_text(msg)