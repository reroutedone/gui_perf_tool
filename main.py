import tkinter as tk
import views.menu_shower as msh
#import controllers.doc_inspector as dinsp
import controllers.main_controller as mcon

root = tk.Tk()
root.title('瑞星windows客户端测试工具')
root.geometry('400x600')
view = msh.MainView(root, None)
controller = mcon.MainController(view)
view.controller = controller

view.show_combo()



if __name__ == '__main__':
    root.mainloop()
