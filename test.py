import tkinter as tk

"""
自定义带占位符的输入框组件
功能：
1. 在未输入时显示灰色提示文字
2. 获得焦点时自动清除提示文字
3. 失去焦点时若内容为空则恢复提示文字
4. 提供get_value()方法获取真实值（自动过滤占位符状态）
"""
class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="请输入内容", defaultvalue="", color='gray', **kwargs):
        """初始化占位符输入框
        
        参数:
            master: 父容器
            placeholder: 占位符提示文本
            defaultvalue: 当处于占位符状态时返回的默认值
            color: 占位符文本颜色
            **kwargs: 标准Entry组件的其他参数
        """
        super().__init__(master, **kwargs)  # 调用父类构造函数

        # 初始化实例变量
        self.placeholder = placeholder        # 占位符文本
        self.defaultvalue = defaultvalue      # 默认返回值
        self.placeholder_color = color        # 占位符颜色
        self.default_fg_color = self['fg']    # 保存原始文字颜色

        # 绑定焦点事件
        self.bind("<FocusIn>", self._clear_placeholder)   # 获得焦点时清除占位符
        self.bind("<FocusOut>", self._add_placeholder)    # 失去焦点时恢复占位符

        self._add_placeholder()  # 初始添加占位符

    def _clear_placeholder(self, event=None):
        """清除占位符（当获得焦点时调用）"""
        if self._is_placeholder():  # 检查当前是否显示占位符
            self.delete(0, tk.END)  # 清空输入框
            self['fg'] = self.default_fg_color  # 恢复原始文字颜色

    def _add_placeholder(self, event=None):
        """添加占位符（当失去焦点且内容为空时调用）"""
        if not self.get():  # 检查输入框是否为空
            self.insert(0, self.placeholder)  # 插入占位符文本
            self['fg'] = self.placeholder_color  # 设置占位符颜色

    def _is_placeholder(self):
        """检查当前是否处于占位符状态"""
        return self['fg'] == self.placeholder_color and self.get() == self.placeholder

    def get_value(self):
        """获取真实值（自动跳过占位符状态）
        
        返回:
            用户输入的真实值，或默认值（当处于占位符状态时）
        """
        if self._is_placeholder():
            return self.defaultvalue  # 返回预设的默认值
        return self.get()  # 返回用户实际输入
if __name__ == "__main__":
    """组件使用示例"""
    root = tk.Tk()
    # 创建带占位符的输入框
    entry = PlaceholderEntry(
        root, 
        placeholder="请输入用户名", 
        defaultvalue="guest"  # 未输入时返回"guest"
    )
    entry.pack(padx=10, pady=10)  # 布局

    def show_value():
        """按钮回调函数：打印输入框的真实值"""
        print("真实值为：", entry.get_value())  # 获取并打印真实值

    # 创建提交按钮
    tk.Button(root, text="提交", command=show_value).pack(pady=10)

    root.mainloop()  # 启动主事件循环
