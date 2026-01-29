import win32gui
import win32process
import win32con
import psutil
import tkinter as tk
from tkinter import ttk
import ctypes


def get_active_window_info(exclude_hwnd=None):
    """获取当前活动窗口信息，可排除指定窗口"""
    hwnd = win32gui.GetForegroundWindow()
    
    # 如果当前窗口是自己，尝试获取下一个窗口
    if exclude_hwnd and hwnd == exclude_hwnd:
        return None
    
    window_title = win32gui.GetWindowText(hwnd)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        process_path = process.exe()
        return {
            "hwnd": hwnd,
            "window_title": window_title,
            "process_name": process_name,
            "pid": pid,
            "process_path": process_path
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


class WindowHackApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WindowHack - 窗口信息查看器")
        self.root.geometry("600x400")
        self.root.minsize(400, 300)
        
        # 保存自己的窗口句柄
        self.root.update_idletasks()
        self.my_hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        
        # 置顶状态
        self.is_topmost = False
        
        self.setup_ui()
        self.setup_update_timer()
    
    def setup_ui(self):
        """设置界面"""
        # 顶部控制栏
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # 置顶按钮
        self.topmost_btn = ttk.Button(
            control_frame, 
            text="📌 置顶窗口", 
            command=self.toggle_topmost
        )
        self.topmost_btn.pack(side=tk.LEFT)
        
        # 置顶状态标签
        self.topmost_label = ttk.Label(control_frame, text="")
        self.topmost_label.pack(side=tk.LEFT, padx=10)
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            control_frame, 
            text="🔄 刷新", 
            command=self.update_info
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # 信息显示区域
        info_frame = ttk.LabelFrame(self.root, text="当前活动窗口信息", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建信息标签
        self.labels = {}
        fields = [
            ("window_title", "窗口标题"),
            ("process_name", "进程名称"),
            ("pid", "进程ID"),
            ("process_path", "程序路径"),
            ("hwnd", "窗口句柄")
        ]
        
        for i, (key, label_text) in enumerate(fields):
            ttk.Label(info_frame, text=f"{label_text}:", font=("微软雅黑", 10, "bold")).grid(
                row=i, column=0, sticky=tk.W, pady=5
            )
            self.labels[key] = ttk.Label(
                info_frame, 
                text="", 
                wraplength=450,
                font=("Consolas", 10)
            )
            self.labels[key].grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
        
        info_frame.columnconfigure(1, weight=1)
        
        # 底部状态栏
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            status_frame, 
            text="提示: 点击其他窗口后，这里会显示该窗口的信息", 
            relief=tk.SUNKEN,
            padding="5"
        )
        self.status_label.pack(fill=tk.X)
    
    def toggle_topmost(self):
        """切换置顶状态"""
        self.is_topmost = not self.is_topmost
        
        if self.is_topmost:
            # 设置窗口置顶但不抢焦点
            self.root.attributes('-topmost', True)
            self.topmost_btn.config(text="📌 取消置顶")
            self.topmost_label.config(text="✅ 已置顶（不影响其他窗口焦点）", foreground="green")
            
            # 使用 Windows API 确保不抢焦点
            # HWND_TOPMOST = -1, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE = 0x0013
            ctypes.windll.user32.SetWindowPos(
                self.my_hwnd, -1, 0, 0, 0, 0, 
                0x0001 | 0x0002 | 0x0010  # SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE
            )
        else:
            self.root.attributes('-topmost', False)
            self.topmost_btn.config(text="📌 置顶窗口")
            self.topmost_label.config(text="")
            
            # 取消置顶
            ctypes.windll.user32.SetWindowPos(
                self.my_hwnd, -2, 0, 0, 0, 0,
                0x0001 | 0x0002 | 0x0010  # SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE
            )
    
    def update_info(self):
        """更新窗口信息"""
        info = get_active_window_info(exclude_hwnd=self.my_hwnd)
        
        if info:
            for key, label in self.labels.items():
                value = info.get(key, "N/A")
                if key == "hwnd":
                    value = f"0x{value:08X}" if isinstance(value, int) else value
                label.config(text=str(value))
            self.status_label.config(text=f"最后更新: 成功获取窗口信息")
        else:
            self.status_label.config(text="提示: 当前焦点在本程序，请点击其他窗口")
    
    def setup_update_timer(self):
        """设置自动更新定时器"""
        def auto_update():
            # 只有当焦点不在自己时才更新
            current_hwnd = win32gui.GetForegroundWindow()
            if current_hwnd != self.my_hwnd:
                self.update_info()
            self.root.after(500, auto_update)  # 每500ms检查一次
        
        auto_update()
    
    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = WindowHackApp()
    app.run()