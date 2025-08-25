#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import shutil
import tinify

class TinyPNGCompressor:
    def __init__(self, log_callback=None):
        self.api_key = ""
        self.version = "1.0.4"
        self.log_callback = log_callback  # GUI 日志回调函数
        
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
            if sys.stdout is not None:
                try:
                    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
                except (AttributeError, OSError):
                    pass
            if sys.stderr is not None:
                try:
                    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
                except (AttributeError, OSError):
                    pass
    
    def log(self, message):
        """发送日志消息到 GUI 或控制台"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def get_file_size(self, file_path):
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def get_directory_size(self, directory_path):
        """获取目录总大小（字节）"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        continue
        except OSError:
            pass
        return total_size
    
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
            self.log("\n=== 压缩统计 ===")
            self.log("没有成功压缩的文件")
            return
        
        # 计算压缩比例
        if self.stats['original_size'] > 0:
            self.stats['compression_ratio'] = (self.stats['saved_size'] / self.stats['original_size']) * 100
        
        self.log("\n" + "="*50)
        self.log("压缩统计报告")
        self.log("="*50)
        self.log(f"总文件数: {self.stats['total_files']}")
        self.log(f"成功压缩: {self.stats['compressed_files']} 个文件")
        self.log(f"跳过文件: {self.stats['skipped_files']} 个文件")
        self.log(f"失败文件: {self.stats['failed_files']} 个文件")
        self.log("-"*50)
        self.log(f"原始总大小: {self.format_file_size(self.stats['original_size'])}")
        self.log(f"压缩后大小: {self.format_file_size(self.stats['compressed_size'])}")
        self.log(f"节省空间: {self.format_file_size(self.stats['saved_size'])}")
        self.log(f"压缩比例: {self.stats['compression_ratio']:.2f}%")
        self.log("="*50)
    
    def set_api_key(self, api_key):
        """设置 API Key"""
        self.api_key = api_key
        tinify.key = api_key
        self.log(f"API Key 已设置: {api_key[:10]}...")
        
        # 验证 API Key 格式
        if not api_key or not api_key.strip():
            raise ValueError("API Key 不能为空")
        
        if len(api_key.strip()) < 10:
            raise ValueError("API Key 格式不正确，长度太短")
    
    def test_api_connection(self):
        """测试 API 连接"""
        try:
            if not self.api_key:
                raise ValueError("API Key 未设置")
            
            # 设置 TLS 证书路径（解决 PyInstaller 打包问题）
            self._fix_tls_certificate_issue()
            
            # 尝试获取账户信息来测试连接
            tinify.validate()
            return True, "API 连接成功"
        except tinify.AccountError as e:
            return False, f"API Key 无效: {str(e)}"
        except tinify.ClientError as e:
            return False, f"客户端错误: {str(e)}"
        except tinify.ServerError as e:
            return False, f"服务器错误: {str(e)}"
        except tinify.ConnectionError as e:
            return False, f"网络连接错误: {str(e)}"
        except Exception as e:
            return False, f"未知错误: {str(e)}"
    
    def _fix_tls_certificate_issue(self):
        """修复 TLS 证书问题"""
        try:
            import certifi
            import ssl
            import os
            import sys
            
            # 获取 certifi 的证书路径
            certifi_path = certifi.where()
            
            # 检查证书文件是否存在
            if not os.path.exists(certifi_path):
                # 尝试在 PyInstaller 临时目录中查找
                if getattr(sys, 'frozen', False):
                    # 运行在 PyInstaller 环境中
                    base_path = sys._MEIPASS
                    possible_paths = [
                        os.path.join(base_path, 'certifi', 'cacert.pem'),
                        os.path.join(base_path, 'cacert.pem'),
                        os.path.join(base_path, 'certifi', 'data', 'cacert.pem')
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            certifi_path = path
                            break
            
            # 设置 SSL 上下文
            ssl_context = ssl.create_default_context(cafile=certifi_path)
            
            # 尝试设置 tinify 的 SSL 上下文
            if hasattr(tinify, 'set_ssl_context'):
                tinify.set_ssl_context(ssl_context)
            
            # 设置环境变量
            os.environ['REQUESTS_CA_BUNDLE'] = certifi_path
            os.environ['SSL_CERT_FILE'] = certifi_path
            os.environ['CURL_CA_BUNDLE'] = certifi_path
            
            # 设置 requests 的证书路径
            try:
                import requests
                requests.packages.urllib3.util.ssl_.DEFAULT_CERTS = certifi_path
            except:
                pass
                
        except ImportError:
            # 如果没有 certifi，尝试使用系统默认证书
            try:
                import ssl
                ssl_context = ssl.create_default_context()
                if hasattr(tinify, 'set_ssl_context'):
                    tinify.set_ssl_context(ssl_context)
            except:
                pass
        except Exception as e:
            self.log(f"警告: 无法设置 TLS 证书: {str(e)}")
            # 尝试最后的备用方案
            try:
                import ssl
                ssl_context = ssl._create_unverified_context()
                if hasattr(tinify, 'set_ssl_context'):
                    tinify.set_ssl_context(ssl_context)
            except:
                pass
    
    def diagnose_compression_issue(self, path):
        """诊断压缩问题"""
        issues = []
        
        # 检查 API Key
        if not self.api_key:
            issues.append("❌ API Key 未设置")
        else:
            success, message = self.test_api_connection()
            if not success:
                issues.append(f"❌ API 连接问题: {message}")
            else:
                issues.append("✅ API 连接正常")
        
        # 检查路径
        if not os.path.exists(path):
            issues.append(f"❌ 路径不存在: {path}")
        elif os.path.isfile(path):
            issues.append("✅ 文件存在")
            
            # 检查文件大小
            size = self.get_file_size(path)
            if size == 0:
                issues.append("❌ 文件大小为0")
            else:
                issues.append(f"✅ 文件大小: {self.format_file_size(size)}")
            
            # 检查文件权限
            if not os.access(path, os.R_OK):
                issues.append("❌ 文件无读取权限")
            else:
                issues.append("✅ 文件可读")
            
            # 检查文件扩展名
            _, ext = os.path.splitext(path)
            if ext.lower() not in ['.png', '.jpg', '.jpeg']:
                issues.append(f"❌ 不支持的文件类型: {ext}")
            else:
                issues.append(f"✅ 支持的文件类型: {ext}")
                
        elif os.path.isdir(path):
            issues.append("✅ 目录存在")
            
            # 检查目录权限
            if not os.access(path, os.R_OK):
                issues.append("❌ 目录无读取权限")
            else:
                issues.append("✅ 目录可读")
            
            # 检查目录是否可写（用于创建输出目录）
            if not os.access(path, os.W_OK):
                issues.append("❌ 目录无写入权限")
            else:
                issues.append("✅ 目录可写")
            
            # 统计目录中的图片文件
            image_count = 0
            total_files = 0
            image_files = []
            try:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        total_files += 1
                        _, ext = os.path.splitext(file)
                        if ext.lower() in ['.png', '.jpg', '.jpeg']:
                            image_count += 1
                            # 记录前几个图片文件作为示例
                            if len(image_files) < 5:
                                rel_path = os.path.relpath(os.path.join(root, file), path)
                                image_files.append(rel_path)
                
                # 计算目录总大小
                total_size = self.get_directory_size(path)
                issues.append(f"✅ 目录统计: {image_count} 个图片文件 / {total_files} 个总文件")
                issues.append(f"📊 目录总大小: {self.format_file_size(total_size)}")
                
                if image_count == 0:
                    issues.append("⚠️ 目录中没有找到支持的图片文件")
                else:
                    issues.append(f"📁 图片文件示例: {', '.join(image_files)}")
                    if image_count > 5:
                        issues.append(f"📁 ... 还有 {image_count - 5} 个图片文件")
            except Exception as e:
                issues.append(f"❌ 目录扫描失败: {str(e)}")
        else:
            issues.append(f"❌ 路径既不是文件也不是目录: {path}")
        
        # 检查网络连接和 TLS 证书
        self._check_network_and_tls(issues)
        
        return issues
    
    def compress_core(self, inputFile, outputFile, img_width, replace=False):
        """压缩的核心逻辑（简化版本，基于原始 tinypng.py）"""
        try:
            # 修复 TLS 证书问题
            self._fix_tls_certificate_issue()
            
            # 执行压缩（简化逻辑，直接使用 tinify）
            self.log(f"正在压缩: {inputFile}")
            self.log(f"输出文件: {outputFile}")
            self.log(f"当前 tinify.key: {tinify.key[:10] if tinify.key else 'None'}...")
            
            source = tinify.from_file(inputFile)
            self.log(f"tinify.from_file() 成功")
            
            if img_width != -1:
                self.log(f"调整图片宽度为: {img_width}")
                resized = source.resize(method="scale", width=img_width)
                resized.to_file(outputFile)
            else:
                source.to_file(outputFile)
            
            self.log(f"文件保存成功")
            
            # 获取文件大小用于统计
            original_size = self.get_file_size(inputFile)
            compressed_size = self.get_file_size(outputFile)
            self.update_stats(original_size, compressed_size, True)
            
            # 如果需要替换原文件
            if replace:
                shutil.move(outputFile, inputFile)
                self.log(f"已替换原文件: {inputFile}")
            else:
                self.log(f"压缩完成: {outputFile}")
            
            self.log(f"  原始大小: {self.format_file_size(original_size)} -> 压缩后: {self.format_file_size(compressed_size)}")
                
        except Exception as e:
            error_msg = f"压缩失败: {str(e)}"
            self.log(f"压缩失败 {inputFile}: {error_msg}")
            self.update_stats(0, 0, False)
            raise RuntimeError(error_msg)
    
    def compress_file(self, inputFile, width=-1, replace=False):
        """压缩单个文件（简化版本，基于原始 tinypng.py）"""
        self.log(f"开始压缩文件: {inputFile}")
        
        if not os.path.isfile(inputFile):
            self.log(f"文件不存在: {inputFile}")
            self.stats['skipped_files'] += 1
            return
        
        dirname = os.path.dirname(inputFile)
        basename = os.path.basename(inputFile)
        fileName, fileSuffix = os.path.splitext(basename)
        
        # 忽略 .meta 文件
        if fileSuffix == '.meta':
            self.log(f"跳过 .meta 文件: {inputFile}")
            self.stats['skipped_files'] += 1
            return
        
        if fileSuffix in ['.png', '.jpg', '.jpeg']:
            if replace:
                # 替换模式：先压缩到临时文件，然后替换原文件
                temp_output = os.path.join(dirname, f"temp_{basename}")
                self.compress_core(inputFile, temp_output, width, True)
            else:
                # 非替换模式：压缩到 tiny_ 前缀文件
                outputFile = os.path.join(dirname, f"tiny_{basename}")
                self.compress_core(inputFile, outputFile, width, False)
        else:
            self.log(f"不支持的文件类型: {fileSuffix}")
            self.stats['skipped_files'] += 1
    
    def _process_directory_files(self, path, width, replace, recursive=False):
        """处理目录中的文件（简化版本，基于原始 tinypng.py）"""
        if not os.path.isdir(path):
            self.log(f"目录不存在: {path}")
            return
        
        fromFilePath = path
        
        if replace:
            # 替换模式：直接处理原文件
            self.log(f"替换模式：源路径: {fromFilePath}")
        else:
            # 非替换模式：创建 tiny 子目录
            toFilePath = os.path.join(path, "tiny")
            self.log(f"非替换模式：源路径: {fromFilePath}")
            self.log(f"输出路径: {toFilePath}")
        
        for root, dirs, files in os.walk(fromFilePath):
            self.log(f"处理目录: {root}")
            self.log(f"子目录: {dirs}")
            self.log(f"文件: {files}")
            
            for name in files:
                fileName, fileSuffix = os.path.splitext(name)
                # 忽略 .meta 文件
                if fileSuffix == '.meta':
                    continue
                
                if fileSuffix in ['.png', '.jpg', '.jpeg']:
                    inputFile = os.path.join(root, name)
                    
                    if replace:
                        # 替换模式：先压缩到临时文件，然后替换原文件
                        temp_output = os.path.join(os.path.dirname(inputFile), f"temp_{name}")
                        self.compress_core(inputFile, temp_output, width, True)
                    else:
                        # 非替换模式：压缩到 tiny 子目录
                        toFullPath = toFilePath + root[len(fromFilePath):]
                        toFullName = os.path.join(toFullPath, name)
                        
                        if not os.path.isdir(toFullPath):
                            os.makedirs(toFullPath, exist_ok=True)
                        
                        self.compress_core(inputFile, toFullName, width, False)
            
            if not recursive:
                break  # 仅遍历当前目录
    
    def compress_path(self, path, width=-1, replace=False):
        """压缩目录下的图片（当前层级，简化版本）"""
        self.log(f"开始压缩目录: {path}")
        self._process_directory_files(path, width, replace, recursive=False)
    
    def compress_path_recursive(self, path, width=-1, replace=False):
        """递归压缩目录及其子目录下的图片（简化版本）"""
        self.log(f"开始递归压缩目录: {path}")
        self._process_directory_files(path, width, replace, recursive=True)
    
    def _check_network_and_tls(self, issues):
        """检查网络连接和 TLS 证书（内部方法）"""
        # 检查网络连接
        try:
            import urllib.request
            urllib.request.urlopen('https://api.tinify.com', timeout=5)
            issues.append("✅ 网络连接正常")
        except:
            issues.append("❌ 网络连接失败")
        
        # 检查 TLS 证书
        try:
            import certifi
            certifi_path = certifi.where()
            if os.path.exists(certifi_path):
                issues.append(f"✅ TLS 证书文件存在: {os.path.basename(certifi_path)}")
            else:
                issues.append("❌ TLS 证书文件不存在")
        except ImportError:
            issues.append("❌ certifi 库未安装")
        except Exception as e:
            issues.append(f"❌ TLS 证书检查失败: {str(e)}")