# controllers/main_controller.py
class MainController:
    def __init__(self, view):
        self.view = view

    def handle_text(self, msg):
        print(f"收到内容：{msg}")
        # 可以添加逻辑处理，比如保存、验证等