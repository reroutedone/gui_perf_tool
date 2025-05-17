# main.py
import tkinter as tk
from views.main_view import MainView
from controllers.main_controller import MainController

root = tk.Tk()
view = MainView(root, None)
controller = MainController(view)
view.controller = controller
view.pack()
root.mainloop()