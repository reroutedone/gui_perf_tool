# main.py
import tkinter as tk
import views.menu_shower as msh
import controllers.docu_controller as dcon
import controllers.main_controller as mcon

root = tk.Tk()
root.title('瑞星windows客户端测试工具')
root.geometry('400x600')
view = msh.MainView(root, None)
controller = mcon.MainController(view)
view.controller = controller

# 构建界面组件 - 按照以下顺序初始化UI元素
view.show_combo()
view.main_label()
view.show_screen()

# 初始化文档控制器(必须在show_screen之后)
docu_controller = dcon.DocuController(view)
view.docu_controller = docu_controller

if __name__ == '__main__':
    root.mainloop()
 