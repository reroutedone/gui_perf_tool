# docu_controller.py
import tkinter as tk
class DocuController:
    def __init__(self, view):
        self.view = view
        self.view.screen.insert(tk.END, 'TEST')
        # 获取office部分输入
    def handle_office_button(self, docu_dir, rounds):
        docu_dir = docu_dir.get()
        rounds = rounds.get()
        self.handle_word_test(docu_dir, rounds)
    def handle_word_test(self, doc_path, rounds):
        # 实现WORD文档测试逻辑
        formatted_text = "%s %s" % (doc_path, rounds)
        self.view.screen.insert(tk.END, formatted_text)
        
    def handle_excel_test(self, doc_path, rounds):
        # 实现EXCEL文档测试逻辑
        pass
        
    def handle_ppt_test(self, doc_path, rounds):
        # 实现PPT文档测试逻辑
        pass
        
    def handle_wps_test(self, doc_path, wps_path, rounds):
        # 实现WPS文档测试逻辑
        pass
