"""
Windows 11 右键菜单注册脚本
需要以管理员权限运行
"""
import winreg
import os
import sys
import ctypes


def is_admin():
    """检查是否有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def elevate_if_needed():
    """如无管理员权限则触发 UAC 提权并退出当前进程"""
    if is_admin():
        return True

    if getattr(sys, 'frozen', False):
        exe = sys.executable
        params = " ".join(f'"{arg}"' for arg in sys.argv[1:])
    else:
        exe = sys.executable
        script = os.path.abspath(__file__)
        params = " ".join([f'"{script}"'] + [f'"{arg}"' for arg in sys.argv[1:]])

    result = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        exe,
        params,
        None,
        1,
    )

    if result <= 32:
        print("❌ 无法获取管理员权限或已取消")
        return False

    sys.exit(0)


def get_exe_path():
    """获取 wintracker.exe 文件路径"""
    # 如果是打包后的 exe，查找同目录下的 wintracker.exe
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        exe_path = os.path.join(exe_dir, "wintracker.exe")
        if os.path.exists(exe_path):
            return exe_path
    
    # 开发环境下，查找 dist 目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(script_dir, "dist", "wintracker.exe")
    
    if os.path.exists(exe_path):
        return exe_path
    
    return None


def install_context_menu():
    """安装右键菜单项"""
    exe_path = get_exe_path()
    
    if not exe_path:
        print("错误: 找不到 wintracker.exe")
        print("请先运行打包命令生成 exe 文件:")
        print("  uv run pyinstaller --onefile --windowed --name wintracker main.py")
        return False
    
    print(f"使用的 exe 路径: {exe_path}")
    
    try:
        # Windows 11 使用新的右键菜单系统
        # 需要在 HKEY_CLASSES_ROOT\*\shell 下添加
        
        # # 为所有文件添加右键菜单
        # key_path = r"*\shell\wintracker"
        
        # # 创建主键
        # key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
        # winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "查看窗口信息 (wintracker)")
        # winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, exe_path)
        # winreg.CloseKey(key)
        
        # # 创建 command 子键
        # cmd_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path + r"\command")
        # winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'"{exe_path}"')
        # winreg.CloseKey(cmd_key)
        
        # # 为目录添加右键菜单
        # dir_key_path = r"Directory\shell\wintracker"
        
        # key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, dir_key_path)
        # winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "查看窗口信息 (wintracker)")
        # winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, exe_path)
        # winreg.CloseKey(key)
        
        # cmd_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, dir_key_path + r"\command")
        # winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'"{exe_path}"')
        # winreg.CloseKey(cmd_key)
        
        # 为目录背景添加右键菜单
        bg_key_path = r"Directory\Background\shell\wintracker"
        
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, bg_key_path)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "查看窗口信息 (wintracker)")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        
        cmd_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, bg_key_path + r"\command")
        winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(cmd_key)
        
        # 为桌面添加右键菜单
        desktop_key_path = r"DesktopBackground\shell\wintracker"
        
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, desktop_key_path)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "查看窗口信息 (wintracker)")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        
        cmd_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, desktop_key_path + r"\command")
        winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(cmd_key)
        
        print("✅ 右键菜单安装成功!")
        print("\n注意: Windows 11 默认显示简化右键菜单")
        print("你可能需要点击 '显示更多选项' 才能看到 wintracker")
        print("或者按住 Shift 键再右键点击")
        return True
        
    except PermissionError:
        print("❌ 权限不足，请以管理员身份运行此脚本")
        return False
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return False


def uninstall_context_menu():
    """卸载右键菜单项"""
    try:
        paths = [
            # r"*\shell\wintracker",
            # r"Directory\shell\wintracker",
            r"Directory\Background\shell\wintracker",
            r"DesktopBackground\shell\wintracker",
        ]
        
        for path in paths:
            try:
                # 先删除 command 子键
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, path + r"\command")
            except FileNotFoundError:
                pass
            
            try:
                # 再删除主键
                winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, path)
            except FileNotFoundError:
                pass
        
        print("✅ 右键菜单已卸载")
        return True
        
    except PermissionError:
        print("❌ 权限不足，请以管理员身份运行此脚本")
        return False
    except Exception as e:
        print(f"❌ 卸载失败: {e}")
        return False


def main():
    print("=" * 50)
    print("wintracker 右键菜单安装工具")
    print("=" * 50)
    
    if not elevate_if_needed():
        input("\n按回车键退出...")
        return
    
    print("\n请选择操作:")
    print("1. 安装右键菜单")
    print("2. 卸载右键菜单")
    print("3. 退出")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        install_context_menu()
    elif choice == "2":
        uninstall_context_menu()
    else:
        print("已退出")
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
