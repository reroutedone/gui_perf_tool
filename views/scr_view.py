import tkinter as tk

# 闭包封装状态
def create_logger():
    _screen = None
    
    def set_screen(screen_widget):
        nonlocal _screen
        _screen = screen_widget
    
    def log(text):
        if _screen:
            _screen.insert(tk.END, f"\n{text}")
            _screen.see(tk.END)
        else:
            print(f"[LOG] {text}")
    
    return set_screen, log

# 创建日志函数
set_global_screen, log = create_logger()

class ScrView:
    def __init__(self, screen_widget=None):
        self.screen = screen_widget if screen_widget else tk.Text()
        set_global_screen(self.screen)  # 设置全局screen