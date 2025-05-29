# docu_controller.py
import subprocess
import time
import win32gui
import win32con
import psutil
import csv
from datetime import datetime
import os
import winreg
import threading
import queue
from views.scr_view import log

class DocuController:
    
    APP_CONFIG = {
        'word': {
            'reg_key': r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\WINWORD.EXE',
            'process_name': 'WINWORD.EXE'
        },
        'excel': {
            'reg_key': r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\EXCEL.EXE',
            'process_name': 'EXCEL.EXE'
        },
        'ppt': {
            'reg_key': r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\POWERPNT.EXE',
            'process_name': 'POWERPNT.EXE'
        }
    }
    def __init__(self, view):
        self.view = view

    # 使用scr_view的旧log()方法，暂时废除
    """ def scrprint(self, text):
        self.view.scr.log(f"\n{text}") """

    # 使用示例
    # 获取office部分输入
    def handle_office_button(self, docu_dir, rounds, app_name):
        docu_dir = docu_dir.get()
        rounds = int(rounds.get())
        self.handle_word_test(docu_dir, rounds, app_name)
    # 获取WPS部分输入
    def handle_wps_button(self, docu_dir, rounds, wps_dir):
        docu_dir = docu_dir.get()
        rounds = int(rounds.get())
        wps_dir = wps_dir.get()
        self.handle_wps_test(
            docu_dir = docu_dir, 
            rounds = rounds, 
            wps_dir = wps_dir
        )

    # 主要文档测试逻辑
    def find_install_path(self, app_type):
        info = self.APP_CONFIG[app_type]
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            if app_type == 'wps':
                return r'C:\Users\reroutedone\AppData\Local\Kingsoft\WPS Office\12.1.0.20784\office6\wps.exe'
            else:
                with winreg.OpenKey(root, info['reg_key']) as key:
                    val, _ = winreg.QueryValueEx(key, None)
                    return val
        except Exception as e:
            log(f"[错误] 无法从注册表获取 {app_type} 安装路径: {e}")
            return None
    def close_all_windows(self, process_name):
        for proc in psutil.process_iter(attrs=['name']):
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except Exception:
                    pass

    def is_taskbar_window(self, hwnd):
        """判断窗口是否可见并出现在任务栏（排除加载中窗口）"""
        if not win32gui.IsWindowVisible(hwnd):
            return False
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        return bool(style & win32con.WS_OVERLAPPEDWINDOW)

    def find_window_containing(self, text):
        matches = []

        def callback(hwnd, extra):
            if not self.is_taskbar_window(hwnd):
                return

            title = win32gui.GetWindowText(hwnd)
            if title.lower().startswith(text.lower()) or title.lower().endswith(text.lower()):
                matches.append(title)

        win32gui.EnumWindows(callback, None)
        return matches

    def _measure_startup_time_thread(self, app_type, app_path, rounds, doc_path, result_queue, timeout=30):
        if app_type != 'wps':
            process_name = self.APP_CONFIG[app_type]['process_name']
        else:
            process_name = 'wps.exe'
        filename = os.path.basename(doc_path) if doc_path else ''

        results = []
        for i in range(rounds):
            log(f"\n第 {i+1} 轮测试: 启动 {app_type.upper()}...")
            self.close_all_windows(process_name)
            time.sleep(2)

            cmd = [app_path]
            if doc_path:
                cmd.append(doc_path)

            start_time = time.time()
            log('开始时间: %s' %start_time)
            elapsed = 0
            found = False
            if (app_type != 'wps'):
                proc = subprocess.Popen(cmd, shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
                while elapsed < timeout:
                    base_name = os.path.splitext(filename)[0]
                    matches = self.find_window_containing(base_name)
                    time.sleep(0.1)
                    if matches:
                        found = True
                        break
                    elapsed = time.time() - start_time

                end_time = time.time()
                log('结束时间: %s' %end_time)
                startup_time = end_time - start_time

                if found:
                    log(f"{app_type.upper()} 启动耗时: {startup_time:.2f} 秒")
                else:
                    log(f"{app_type.upper()} 启动失败或窗口未检测到，耗时（可能超时）: {startup_time:.2f} 秒")

                results.append(startup_time)
                time.sleep(1)
            else:
                log('当前为wps')
                absolute_doc_path = os.path.abspath(doc_path)
                cmd = [app_path, "/prometheus", "/et", absolute_doc_path]
                proc = subprocess.Popen(cmd, shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
                #time.sleep(1)
                # WPS特殊处理：等待人工关闭窗口
                log("请手动处理WPS窗口...")
                while elapsed < timeout:
                    matches = self.find_window_containing(filename)
                    if matches:
                        while True:
                            matches = self.find_window_containing(filename)
                            if not matches:
                                break
                            time.sleep(0.1)
                        break
                    else:
                        time.sleep(0.1)
                end_time = time.time()
                log('结束时间: %s' %end_time)
                startup_time = end_time - start_time
                log(f"{app_type.upper()} 启动耗时: {startup_time:.2f} 秒")
                results.append(startup_time)
        
        if app_type != 'wps':
            self.close_all_windows(process_name)
        result_queue.put(results)
        
    def measure_startup_time(self, app_type, app_path, rounds, doc_path, callback=None, timeout=30):
        """异步测量启动时间"""
        result_queue = queue.Queue()
        thread = threading.Thread(
            target=self._measure_startup_time_thread,
            args=(app_type, app_path, rounds, doc_path, result_queue, timeout),
            daemon=True
        )
        thread.start()
        
        if callback:
            def check_result():
                try:
                    results = result_queue.get_nowait()
                    callback(results)
                except queue.Empty:
                    self.view.after(100, check_result)
            check_result()
    """ def write_results_to_csv(app_type, results):
        filename = f"{app_type}_startup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['轮次', '启动时间（秒）'])
            for idx, val in enumerate(results, 1):
                writer.writerow([idx, f"{val:.2f}"])
            writer.writerow(['最小', f"{min(results):.2f}"])
            writer.writerow(['平均', f"{sum(results)/len(results):.2f}"])
            writer.writerow(['最大', f"{max(results):.2f}"])
        print(f"\n测试结果已保存到: {filename}") """
    
    """ def handle_office_test(self, doc_path, rounds):
        # 实现OFFICE文档测试逻辑
        
        
        app_path = find_install_path(args.type)
        if (not app_path or not os.path.exists (app_path)) and args.type != 'wps':
            print(args.type)
            print(f"[错误] 无法找到 {args.type} 的启动程序: {app_path}")
            return

        if args.file and not os.path.exists(args.file):
            print(f"[错误] 指定文档不存在: {args.file}")
            return

        results = measure_startup_time(
            app_type=args.type,
            app_path=app_path,
            doc_path=args.file,
            rounds=args.rounds
        ) """
        #write_results_to_csv(args.type, results)
    def handle_wps_test(self, docu_dir, rounds, wps_dir):
        # 实现WPS文档测试逻辑
        if (not wps_dir or not os.path.exists (wps_dir)):
            log(f"[错误] 无法找到 WPS 的启动程序: {wps_dir}")
            return
        if docu_dir and not os.path.exists(docu_dir):
            log(f"[错误] 指定文档不存在: {docu_dir}")
            return
        results = self.measure_startup_time(
            app_type = 'wps',
            app_path = wps_dir,
            doc_path = docu_dir,
            rounds = rounds
        )
        #write_results_to_csv('wps', results)
