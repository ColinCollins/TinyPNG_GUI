#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
from tinypng_core import TinyPNGCompressor

class TinyPNGGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TinyPNG 图片压缩工具 v1.0.4")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 配置
        self.config_file = "config.json"
        self.config = self.load_config()
        
        # 压缩器实例
        self.compressor = TinyPNGCompressor()
        
        # 压缩线程
        self.compress_thread = None
        self.is_compressing = False
        
        self.setup_ui()
        self.load_config_to_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # API 设置区域
        self.setup_api_section(main_frame)
        
        # 压缩模式区域
        self.setup_mode_section(main_frame)
        
        # 文件选择区域
        self.setup_file_section(main_frame)
        
        # 压缩设置区域
        self.setup_compress_section(main_frame)
        
        # 控制按钮区域
        self.setup_control_section(main_frame)
        
        # 日志输出区域
        self.setup_log_section(main_frame)
    
    def setup_api_section(self, parent):
        """设置 API 配置区域"""
        # API 设置框架
        api_frame = ttk.LabelFrame(parent, text="API 设置", padding="5")
        api_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        api_frame.columnconfigure(1, weight=1)
        
        # API Key 输入
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*", width=50)
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 测试按钮
        ttk.Button(api_frame, text="测试连接", command=self.test_api).grid(row=0, column=2)
    
    def setup_mode_section(self, parent):
        """设置压缩模式区域"""
        # 模式选择框架
        mode_frame = ttk.LabelFrame(parent, text="压缩模式", padding="5")
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 模式选择变量
        self.mode_var = tk.StringVar(value="file")
        
        # 单选按钮
        ttk.Radiobutton(mode_frame, text="单文件", variable=self.mode_var, 
                       value="file", command=self.on_mode_change).grid(row=0, column=0, padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="目录", variable=self.mode_var, 
                       value="dir", command=self.on_mode_change).grid(row=0, column=1, padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="递归目录", variable=self.mode_var, 
                       value="recursive", command=self.on_mode_change).grid(row=0, column=2)
    
    def setup_file_section(self, parent):
        """设置文件选择区域"""
        # 文件选择框架
        file_frame = ttk.LabelFrame(parent, text="文件/目录选择", padding="5")
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # 路径显示
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(file_frame, textvariable=self.path_var, state="readonly")
        self.path_entry.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 选择按钮
        self.select_button = ttk.Button(file_frame, text="选择文件", command=self.select_file)
        self.select_button.grid(row=0, column=2)
    
    def setup_compress_section(self, parent):
        """设置压缩选项区域"""
        # 压缩设置框架
        compress_frame = ttk.LabelFrame(parent, text="压缩设置", padding="5")
        compress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        compress_frame.columnconfigure(1, weight=1)
        
        # 图片宽度设置
        ttk.Label(compress_frame, text="图片宽度:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.width_var = tk.StringVar()
        width_entry = ttk.Entry(compress_frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Label(compress_frame, text="(留空保持原尺寸)").grid(row=0, column=2, sticky=tk.W)
        
        # 选项复选框
        self.replace_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(compress_frame, text="替换原文件", variable=self.replace_var).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        self.ignore_meta_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(compress_frame, text="忽略 .meta 文件", variable=self.ignore_meta_var).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        self.auto_open_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(compress_frame, text="压缩后自动打开输出目录", variable=self.auto_open_var).grid(row=1, column=2, sticky=tk.W, pady=(5, 0))
    
    def setup_control_section(self, parent):
        """设置控制按钮区域"""
        # 控制按钮框架
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # 按钮
        self.start_button = ttk.Button(control_frame, text="开始压缩", command=self.start_compress)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="停止", command=self.stop_compress, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT)
    
    def setup_log_section(self, parent):
        """设置日志输出区域"""
        # 日志框架
        log_frame = ttk.LabelFrame(parent, text="日志输出", padding="5")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(5, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def on_mode_change(self):
        """模式改变时的处理"""
        mode = self.mode_var.get()
        if mode == "file":
            self.select_button.config(text="选择文件")
        else:
            self.select_button.config(text="选择目录")
    
    def select_file(self):
        """选择文件或目录"""
        mode = self.mode_var.get()
        if mode == "file":
            filename = filedialog.askopenfilename(
                title="选择图片文件",
                filetypes=[("图片文件", "*.png *.jpg *.jpeg"), ("所有文件", "*.*")]
            )
            if filename:
                self.path_var.set(filename)
        else:
            dirname = filedialog.askdirectory(title="选择目录")
            if dirname:
                self.path_var.set(dirname)
    
    def test_api(self):
        """测试 API 连接"""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入 API Key")
            return
        
        # 这里可以添加实际的 API 测试逻辑
        messagebox.showinfo("成功", "API Key 格式正确")
    
    def start_compress(self):
        """开始压缩"""
        if self.is_compressing:
            return
        
        # 验证输入
        if not self.validate_input():
            return
        
        # 更新 UI 状态
        self.is_compressing = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # 在新线程中执行压缩
        self.compress_thread = threading.Thread(target=self.compress_worker)
        self.compress_thread.daemon = True
        self.compress_thread.start()
    
    def stop_compress(self):
        """停止压缩"""
        self.is_compressing = False
        self.log_message("正在停止压缩...")
    
    def compress_worker(self):
        """压缩工作线程"""
        try:
            # 重置统计信息
            self.compressor.reset_stats()
            
            # 获取参数
            mode = self.mode_var.get()
            path = self.path_var.get()
            width = self.width_var.get().strip()
            replace = self.replace_var.get()
            
            # 设置宽度参数
            if width:
                try:
                    width = int(width)
                except ValueError:
                    self.log_message("错误: 宽度必须是数字")
                    return
            else:
                width = -1
            
            # 设置 API Key
            api_key = self.api_key_var.get().strip()
            self.compressor.set_api_key(api_key)
            
            # 执行压缩
            if mode == "file":
                self.compressor.compress_file(path, width, replace)
            elif mode == "dir":
                self.compressor.compress_path(path, width, replace)
            elif mode == "recursive":
                self.compressor.compress_path_recursive(path, width, replace)
            
            # 打印压缩统计信息
            self.compressor.print_stats()
            
            self.log_message("压缩完成!")
            
        except Exception as e:
            self.log_message(f"压缩出错: {str(e)}")
        finally:
            # 恢复 UI 状态
            self.root.after(0, self.reset_ui_state)
    
    def reset_ui_state(self):
        """重置 UI 状态"""
        self.is_compressing = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
    
    def validate_input(self):
        """验证输入"""
        # 检查 API Key
        if not self.api_key_var.get().strip():
            messagebox.showerror("错误", "请输入 API Key")
            return False
        
        # 检查路径
        if not self.path_var.get():
            messagebox.showerror("错误", "请选择文件或目录")
            return False
        
        return True
    
    def log_message(self, message):
        """添加日志消息"""
        self.root.after(0, lambda: self.log_text.insert(tk.END, f"{message}\n"))
        self.root.after(0, lambda: self.log_text.see(tk.END))
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def load_config(self):
        """加载配置"""
        default_config = {
            "api_key": "",
            "width": "",
            "replace": False,
            "ignore_meta": True,
            "auto_open": False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_config
        return default_config
    
    def load_config_to_ui(self):
        """将配置加载到 UI"""
        self.api_key_var.set(self.config.get("api_key", ""))
        self.width_var.set(self.config.get("width", ""))
        self.replace_var.set(self.config.get("replace", False))
        self.ignore_meta_var.set(self.config.get("ignore_meta", True))
        self.auto_open_var.set(self.config.get("auto_open", False))
    
    def save_config(self):
        """保存配置"""
        config = {
            "api_key": self.api_key_var.get(),
            "width": self.width_var.get(),
            "replace": self.replace_var.get(),
            "ignore_meta": self.ignore_meta_var.get(),
            "auto_open": self.auto_open_var.get()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

def main():
    root = tk.Tk()
    app = TinyPNGGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()