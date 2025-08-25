# TinyPNG GUI 图片压缩工具

一个基于 TinyPNG API 的图形化图片压缩工具。

## 功能特性

- 🖼️ 支持 PNG、JPG、JPEG 格式图片压缩
- 📁 支持单文件、目录、递归目录压缩
- ⚙️ 可配置图片压缩后的宽度
- 🔄 支持替换原文件或输出到新目录
- 🚫 自动忽略 Unity .meta 文件
- 💾 配置保存和加载
- 📝 实时日志输出

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 打包成 exe

```bash
python build.py
```

## 使用说明

1. 输入 TinyPNG API Key
2. 选择压缩模式（单文件/目录/递归目录）
3. 选择要压缩的文件或目录
4. 配置压缩参数
5. 点击"开始压缩"

## 配置说明

- **API Key**: TinyPNG 的 API 密钥
- **图片宽度**: 压缩后的图片宽度，留空保持原尺寸
- **替换原文件**: 是否用压缩后的文件替换原文件
- **忽略 .meta 文件**: 是否跳过 Unity 的 .meta 文件
- **自动打开输出目录**: 压缩完成后是否自动打开输出目录