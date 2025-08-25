#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import shutil
import tinify

class TinyPNGCompressor:
    def __init__(self):
        self.api_key = ""
        self.version = "1.0.4"
        
        # 压缩统计信息
        self.stats = {
            'total_files': 0,
            'compressed_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'original_size': 0,
            'compressed_size': 0,
            'saved_size': 0,
            'compression_ratio': 0.0
        }
        
        # 设置控制台输出编码，解决 PowerShell 中文显示问题
        if sys.platform.startswith('win'):
            import codecs
            # Python 2/3 兼容性处理
            try:
                # Python 3
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
            except AttributeError:
                # Python 2 - 重新编码 stdout 和 stderr
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
    
    def get_file_size(self, file_path):
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def format_file_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_files': 0,
            'compressed_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'original_size': 0,
            'compressed_size': 0,
            'saved_size': 0,
            'compression_ratio': 0.0
        }
    
    def update_stats(self, original_size, compressed_size, success=True):
        """更新统计信息"""
        self.stats['total_files'] += 1
        
        if success:
            self.stats['compressed_files'] += 1
            self.stats['original_size'] += original_size
            self.stats['compressed_size'] += compressed_size
            self.stats['saved_size'] += (original_size - compressed_size)
        else:
            self.stats['failed_files'] += 1
    
    def print_stats(self):
        """打印压缩统计信息"""
        if self.stats['compressed_files'] == 0:
            print("\n=== 压缩统计 ===")
            print("没有成功压缩的文件")
            return
        
        # 计算压缩比例
        if self.stats['original_size'] > 0:
            self.stats['compression_ratio'] = (self.stats['saved_size'] / self.stats['original_size']) * 100
        
        print("\n" + "="*50)
        print("压缩统计报告")
        print("="*50)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"成功压缩: {self.stats['compressed_files']} 个文件")
        print(f"跳过文件: {self.stats['skipped_files']} 个文件")
        print(f"失败文件: {self.stats['failed_files']} 个文件")
        print("-"*50)
        print(f"原始总大小: {self.format_file_size(self.stats['original_size'])}")
        print(f"压缩后大小: {self.format_file_size(self.stats['compressed_size'])}")
        print(f"节省空间: {self.format_file_size(self.stats['saved_size'])}")
        print(f"压缩比例: {self.stats['compression_ratio']:.2f}%")
        print("="*50)
    
    def set_api_key(self, api_key):
        """设置 API Key"""
        self.api_key = api_key
        tinify.key = api_key
    
    def compress_core(self, inputFile, outputFile, img_width, replace=False):
        """压缩的核心逻辑"""
        try:
            # 获取原始文件大小
            original_size = self.get_file_size(inputFile)
            
            source = tinify.from_file(inputFile)
            if img_width != -1:
                resized = source.resize(method="scale", width=img_width)
                resized.to_file(outputFile)
            else:
                source.to_file(outputFile)
            
            # 获取压缩后文件大小
            compressed_size = self.get_file_size(outputFile)
            
            # 更新统计信息
            self.update_stats(original_size, compressed_size, True)
            
            # 如果需要替换原文件
            if replace:
                shutil.move(outputFile, inputFile)
                print(f"已替换原文件: {inputFile}")
                print(f"  原始大小: {self.format_file_size(original_size)} -> 压缩后: {self.format_file_size(compressed_size)}")
            else:
                print(f"压缩完成: {outputFile}")
                print(f"  原始大小: {self.format_file_size(original_size)} -> 压缩后: {self.format_file_size(compressed_size)}")
                
        except Exception as e:
            print(f"压缩失败 {inputFile}: {str(e)}")
            # 更新失败统计
            self.update_stats(0, 0, False)
            raise
    
    def compress_file(self, inputFile, width=-1, replace=False):
        """压缩单个文件"""
        print(f"开始压缩文件: {inputFile}")
        
        if not os.path.isfile(inputFile):
            print(f"文件不存在: {inputFile}")
            return
        
        dirname = os.path.dirname(inputFile)
        basename = os.path.basename(inputFile)
        fileName, fileSuffix = os.path.splitext(basename)
        
        # 忽略 .meta 文件
        if fileSuffix == '.meta':
            print(f"跳过 .meta 文件: {inputFile}")
            self.stats['skipped_files'] += 1
            return
        
        if fileSuffix in ['.png', '.jpg', '.jpeg']:
            if replace:
                # 替换模式：直接压缩到原文件
                self.compress_core(inputFile, inputFile, width, False)
            else:
                # 非替换模式：压缩到 tiny_ 前缀文件
                outputFile = os.path.join(dirname, f"tiny_{basename}")
                self.compress_core(inputFile, outputFile, width, False)
        else:
            print(f"不支持的文件类型: {fileSuffix}")
            self.stats['skipped_files'] += 1
    
    def compress_path(self, path, width=-1, replace=False):
        """压缩目录下的图片（当前层级）"""
        print(f"开始压缩目录: {path}")
        
        if not os.path.isdir(path):
            print(f"目录不存在: {path}")
            return
        
        fromFilePath = path
        toFilePath = os.path.join(path, "tiny")
        
        print(f"源路径: {fromFilePath}")
        print(f"输出路径: {toFilePath}")
        
        for root, dirs, files in os.walk(fromFilePath):
            print(f"处理目录: {root}")
            print(f"子目录: {dirs}")
            print(f"文件: {files}")
            
            for name in files:
                fileName, fileSuffix = os.path.splitext(name)
                # 忽略 .meta 文件
                if fileSuffix == '.meta':
                    continue
                
                if fileSuffix in ['.png', '.jpg', '.jpeg']:
                    toFullPath = toFilePath + root[len(fromFilePath):]
                    toFullName = os.path.join(toFullPath, name)
                    
                    if not os.path.isdir(toFullPath):
                        os.makedirs(toFullPath)
                    
                    inputFile = os.path.join(root, name)
                    self.compress_core(inputFile, toFullName, width, replace)
            
            break  # 仅遍历当前目录
    
    def compress_path_recursive(self, path, width=-1, replace=False):
        """递归压缩目录及其子目录下的图片"""
        print(f"开始递归压缩目录: {path}")
        
        if not os.path.isdir(path):
            print(f"目录不存在: {path}")
            return
        
        fromFilePath = path
        toFilePath = os.path.join(path, "tiny")
        
        print(f"源路径: {fromFilePath}")
        print(f"输出路径: {toFilePath}")
        
        for root, dirs, files in os.walk(fromFilePath):
            print(f"处理目录: {root}")
            print(f"子目录: {dirs}")
            print(f"文件: {files}")
            
            for name in files:
                fileName, fileSuffix = os.path.splitext(name)
                # 忽略 .meta 文件
                if fileSuffix == '.meta':
                    continue
                
                if fileSuffix in ['.png', '.jpg', '.jpeg']:
                    toFullPath = toFilePath + root[len(fromFilePath):]
                    toFullName = os.path.join(toFullPath, name)
                    
                    if not os.path.isdir(toFullPath):
                        os.makedirs(toFullPath)
                    
                    inputFile = os.path.join(root, name)
                    self.compress_core(inputFile, toFullName, width, replace)