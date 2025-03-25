# LDtts - 文本转语音工具

这是一个基于 Silicon Flow TTS API 的文本转语音工具，支持多行文本处理和音频合并。

## 功能特点

- 支持多行文本输入
- 自动逐行转换为语音
- 自动合并音频片段
- 支持调整语速和音量
- 支持多种音色选择
- 支持多种音频格式输出

## 安装依赖

```bash
pip install flask pydub requests
conda install ffmpeg  # 或使用其他方式安装 ffmpeg
```

## 使用方法

1. 设置 API Key：
   - 在 `app.py` 中替换 `your_api_key_here` 为您的 Silicon Flow API Key
   - 或设置环境变量 `SILICON_FLOW_API_KEY`

2. 运行服务器：
```bash
python app.py
```

3. 访问网页界面：
   - 打开浏览器访问 `http://localhost:5000`
   - 在文本框中输入要转换的文本
   - 点击"转换"按钮
   - 等待处理完成后自动下载音频文件

## 注意事项

- 请确保已安装 ffmpeg
- API Key 请妥善保管，不要泄露
- 建议使用 Chrome 或 Firefox 浏览器 