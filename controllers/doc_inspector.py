import subprocess
import time
import win32gui
import win32con
import psutil
import csv
from datetime import datetime
import argparse
import os
import winreg

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
    },
    'wps': {
        'reg_key': r'SOFTWARE\Kingsoft\Office\6.0\Common',
        'process_name': 'wps.exe',
        'executable': 'wps.exe'
    }
}

def find_install_path(app_type):
    info = APP_CONFIG[app_type]
    try:
        root = winreg.HKEY_LOCAL_MACHINE
        if app_type == 'wps':
            """ with winreg.OpenKey(root, info['reg_key']) as key:
                val, _ = winreg.QueryValueEx(key, None)
                return os.path.join(val, info['executable']) """
            return r'C:\Users\RS\AppData\Local\Kingsoft\WPS Office\12.1.0.20784\office6\wps.exe'
        else:
            with winreg.OpenKey(root, info['reg_key']) as key:
                val, _ = winreg.QueryValueEx(key, None)
                return val
    except Exception as e:
        print(f"[错误] 无法从注册表获取 {app_type} 安装路径: {e}")
        return None

def close_all_windows(process_name):
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                pass

def is_taskbar_window(hwnd):
    """判断窗口是否可见并出现在任务栏（排除加载中窗口）"""
    if not win32gui.IsWindowVisible(hwnd):
        return False
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    return bool(style & win32con.WS_OVERLAPPEDWINDOW)

def find_window_containing(text):
    matches = []

    def callback(hwnd, extra):
        if not is_taskbar_window(hwnd):
            return

        title = win32gui.GetWindowText(hwnd)
        if title.lower().startswith(text.lower()) or title.lower().endswith(text.lower()):
            matches.append(title)

    win32gui.EnumWindows(callback, None)
    return matches

def measure_startup_time(app_type, app_path, doc_path=None, rounds=3, timeout=30):
    process_name = APP_CONFIG[app_type]['process_name']
    filename = os.path.basename(doc_path) if doc_path else ''

    results = []

    for i in range(rounds):
        print(f"\n第 {i+1} 轮测试: 启动 {app_type.upper()}...")
        close_all_windows(process_name)
        time.sleep(2)

        cmd = [app_path]
        #print('cmd = %s' %cmd)
        if doc_path:
            cmd.append(doc_path)

        start_time = time.time()
        print('开始时间: %s' %start_time)
        elapsed = 0
        found = False
        if (app_type != 'wps'):
            proc = subprocess.Popen(cmd, shell=False)
            while elapsed < timeout:
                base_name = os.path.splitext(filename)[0]
                matches = find_window_containing(base_name)
                time.sleep(0.1)
                if matches:
                    print('找到啦！')
                    found = True
                    break
                elapsed = time.time() - start_time

            end_time = time.time()
            print('结束时间: %s' %end_time)
            startup_time = end_time - start_time

            if found:
                print(f"{app_type.upper()} 启动耗时: {startup_time:.2f} 秒")
            else:
                print(f"{app_type.upper()} 启动失败或窗口未检测到，耗时（可能超时）: {startup_time:.2f} 秒")

            results.append(startup_time)
            time.sleep(1)
        else:
            print('当前为wps')
            absolute_doc_path = os.path.abspath(doc_path)
            cmd = [app_path, "/prometheus", "/et", absolute_doc_path]
            proc = subprocess.Popen(cmd, shell=False)
            #time.sleep(1)
            """ # 读取子进程的输出
            output, _ = proc.communicate()

            # 打印输出
            print(output.decode('utf-8')) """
            # WPS特殊处理：等待人工关闭窗口
            print("请手动处理WPS窗口...")
            while elapsed < timeout:
                matches = find_window_containing(filename)
                print(filename)
                if matches:
                    while True:
                        matches = find_window_containing(filename)
                        if not matches:
                            break
                        time.sleep(0.1)
                    break
                else:
                    time.sleep(0.1)
            end_time = time.time()
            startup_time = end_time - start_time
            print(f"WPS 文档处理完成，总耗时: {startup_time:.2f} 秒")
            results.append(startup_time)
    
    if app_type != 'wps':
        close_all_windows(process_name)
    return results

def write_results_to_csv(app_type, results):
    filename = f"{app_type}_startup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['轮次', '启动时间（秒）'])
        for idx, val in enumerate(results, 1):
            writer.writerow([idx, f"{val:.2f}"])
        writer.writerow(['最小', f"{min(results):.2f}"])
        writer.writerow(['平均', f"{sum(results)/len(results):.2f}"])
        writer.writerow(['最大', f"{max(results):.2f}"])
    print(f"\n测试结果已保存到: {filename}")

def main():
    parser = argparse.ArgumentParser(description="WPS/Office 启动时间测试工具")
    parser.add_argument("--type", required=True, choices=['word', 'excel', 'ppt', 'wps'], help="测试目标应用类型")
    parser.add_argument("--file", help="可选：打开的文档路径（推荐带文档提升准确性）")
    parser.add_argument("--rounds", type=int, default=3, help="测试轮数（默认3轮）")
    args = parser.parse_args()

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
    )
    write_results_to_csv(args.type, results)

if __name__ == "__main__":
    main()
