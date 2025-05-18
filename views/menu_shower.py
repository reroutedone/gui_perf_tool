import tkinter as tk
from tkinter import ttk
import time

class MainView(tk.Frame):
    def __init__(self, parent, controller):
        # 调用父类构造函数，将该 Frame 初始化为 parent 的子容器
        super().__init__(parent)
        self.controller = controller
        self.pack(fill=tk.BOTH, expand=True)  # Pack the main view frame
        
    def main_label(self):
        frame = tk.Frame(self)
        frame.pack(expand=True)
        self.mainlabel = tk.Label(frame, text = '瑞星测试工具', font = (None, 20))
        self.mainlabel.pack(expand=True)

    def show_combo(self):
        # 创建下拉列表
        self.categories = ['扫描测试', '文件监控测试', '文档打开测试']
        self.combo = ttk.Combobox(self, values = self.categories, state = 'readonly', width = 50)
        self.combo.pack(pady = 10)
        self.combo.set("-- 请选择测试项 --")  # 设置默认显示文本
        self.combo.configure(foreground="gray")
        self.content = tk.Frame(self)
        self.content.pack(pady = 5)
        self.combo.bind("<<ComboboxSelected>>", self.on_select)
        return self.content
    
    def clear_frame(self, content):
        self.mainlabel.destroy()
        if content:
            for widget in content.winfo_children():
                widget.destroy()
    # 绑定选择事件
    def on_select(self, event):
        self.clear_frame(self.content)
        selected_value = self.combo.get()
        showers = {
            self.categories[0]:self.show_scan,
            self.categories[1]:self.show_filemon,
            self.categories[2]:self.show_docu
        }
        if selected_value in showers.keys():
            screen = showers[selected_value]()

    def add_placeholder(self, entry, placeholder_text):
        entry.insert(0, placeholder_text)
        entry.config(fg='gray')

        def on_focus_in(event):
            if entry.get() == placeholder_text:
                entry.delete(0, tk.END)
                entry.config(fg='black')

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder_text)
                entry.config(fg='gray')

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def show_screen(self):
        frame = tk.Frame(self)
        frame.pack(side = tk.BOTTOM)
        self.screen = tk.Text(frame, height = 20, wrap = tk.WORD)
        scrollbar = tk.Scrollbar(frame, command = self.screen.yview)
        scrollbar.pack(side = tk.RIGHT, fill=tk.Y)
        self.screen.pack(side = tk.LEFT, fill = tk.BOTH, expand=True)
        self.screen.config(yscrollcommand=scrollbar.set)
        return self.screen

    def show_scan(self):
        pass

    def show_filemon(self):
        pass
    #def 
    def show_docu(self):
        # OFFICE类
        def create_office_section(parent, app_name):
            frame = tk.Frame(parent)
            frame.pack()
            label = tk.Label(frame, text = app_name)
            label.pack(pady = 5)
            docu_dir = tk.Entry(frame, width = 30)
            docu_dir.pack(side = tk.LEFT, padx = (0, 5))
            self.add_placeholder(docu_dir, '请输入文档路径')
            rounds = tk.Entry(frame, width = 5)
            rounds.pack(side = tk.LEFT, padx = (0, 5))
            self.add_placeholder(rounds, '轮数')
            button = tk.Button(frame, text = '执行', command = lambda:self.docu_controller.handle_office_button(docu_dir, rounds))
            button.pack(side = tk.LEFT)
        # WPS
        def create_wps_section(parent):
            frame_wps = tk.Frame(parent)
            frame_wps.pack()
            label = tk.Label(frame_wps, text="WPS(手动操作)")
            label.pack(pady = 5)
            dir_wps = tk.Entry(frame_wps, width = 30)
            dir_wps.pack(side=tk.LEFT, padx=(0, 5))
            self.add_placeholder(dir_wps, "请输入文档路径")
            round_wps = tk.Entry(frame_wps, width = 5)
            round_wps.pack(side=tk.LEFT, padx=(0, 5))
            self.add_placeholder(round_wps, "轮数")
            frame_wps_2 = tk.Frame(self.content)
            frame_wps_2.pack(side = tk.TOP, pady = 5)
            wps_dir = tk.Entry(frame_wps_2, width = 40)
            wps_dir.pack(side = tk.LEFT, padx=(0, 5))
            self.add_placeholder(wps_dir, "请输入WPS程序路径")
            button_wps = tk.Button(frame_wps_2, text = '执行')
            button_wps.pack(side=tk.LEFT, padx=(0, 5))
        # WORD
        create_office_section(self.content, 'WORD')
        # EXCEL
        create_office_section(self.content, 'EXCEL')
        # PPT
        create_office_section(self.content, 'PPT')
        # WPS
        create_wps_section(self.content)