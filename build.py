#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import subprocess

def build_exe():
    """打包成 exe 文件"""
    try:
        # 检查是否安装了 PyInstaller
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 安装项目依赖
    print("正在安装项目依赖...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 打包命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个文件
        "--windowed",  # 不显示控制台窗口
        "--name=TinyPNG_GUI",  # 可执行文件名
        "--hidden-import=tinify",  # 显式包含 tinify 模块
        "--hidden-import=click",   # 显式包含 click 模块
        "main.py"
    ]
    
    # 执行打包
    subprocess.check_call(cmd)
    print("打包完成！可执行文件在 dist/ 目录中")

if __name__ == "__main__":
    build_exe()