"""
打包脚本 - 使用 PyInstaller 将程序打包成 exe
"""
import subprocess
import sys
import os


def build():
    """执行打包"""
    print("=" * 50)
    print("WindowHack 打包工具")
    print("=" * 50)
    
    # 确保在正确的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("\n正在打包主程序...")
    
    # 打包主程序
    main_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # 打包成单个文件
        "--windowed",          # 不显示控制台窗口
        "--name", "windowhack",
        "--clean",             # 清理临时文件
        "main.py"
    ]
    
    result = subprocess.run(main_cmd)
    if result.returncode != 0:
        print("❌ 主程序打包失败")
        return False
    
    print("\n正在打包安装工具...")
    
    # 打包安装工具
    install_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "install_context_menu",
        "--clean",
        # 安装工具需要控制台，不加 --windowed
        "install_context_menu.py"
    ]
    
    result = subprocess.run(install_cmd)
    if result.returncode != 0:
        print("❌ 安装工具打包失败")
        return False
    
    print("\n" + "=" * 50)
    print("✅ 打包完成!")
    print("=" * 50)
    print(f"\n生成的文件位于: {os.path.join(script_dir, 'dist')}")
    print("  - windowhack.exe          (主程序)")
    print("  - install_context_menu.exe (右键菜单安装工具)")
    print("\n使用方法:")
    print("1. 运行 windowhack.exe 即可使用")
    print("2. 以管理员身份运行 install_context_menu.exe 来添加右键菜单")
    
    return True


if __name__ == "__main__":
    build()
