# LDtts - 文本转语音工具

这是一个基于多种TTS API的文本转语音工具，支持多行文本处理和音频合并，使用FastAPI构建。

## 功能特点

- 支持多行文本输入
- 自动逐行转换为语音
- 自动合并音频片段
- 支持调整语速和音量
- 支持多种音色选择
- 支持多种音频格式输出
- **支持对谈模式，可生成主持人和嘉宾的对话形式音频**
- **支持故事转换为对话脚本**
- **支持将中文对话翻译为英文**
- **支持多种TTS引擎：Silicon Flow、阿里云CosyVoice、MiniMax**

## 安装依赖

```bash
pip install -r requirements.txt
# 或者手动安装主要依赖
pip install fastapi uvicorn jinja2 pydub openai requests python-multipart
```

## 使用方法

### 启动服务器

```bash
# 使用启动脚本
python run.py

# 或者直接使用uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 5000
```

### 访问和API文档

- 网页界面：打开浏览器访问 `http://localhost:5000`
- API文档：访问 `http://localhost:5000/docs` 或 `http://localhost:5000/redoc`

### 基础模式

1. 设置 API Key：
   - 在 `config.py` 中配置各种TTS引擎的API密钥
   - 默认使用Silicon Flow TTS API

2. 在文本框中输入要转换的文本，选择TTS引擎、音色和语速，点击"转换"按钮

### 对谈模式

对谈模式可以生成两个人物之间交替对话的音频，适合制作播客、访谈等内容。

1. 文本格式：
   - 使用`[主持人]`和`[嘉宾]`标记不同角色的对话
   - 例如：`[主持人]欢迎来到今天的节目。[嘉宾]谢谢邀请，很高兴来到这里。`

2. 使用方法：
   - 在对谈模式输入框中输入带有角色标记的文本
   - 为每个角色选择不同的音色和TTS引擎
   - 点击"生成对谈"按钮

### 故事转换模式

将文章或故事自动转换为主持人和嘉宾的对话形式。

1. 输入一段故事或文章
2. 点击"转换故事"按钮
3. 系统会利用大语言模型将文章转换为对谈脚本

### 翻译功能

将中文对话脚本翻译成英文，保持对话格式。

1. 输入中文对话脚本
2. 点击"翻译"按钮
3. 系统会返回翻译后的英文对话脚本

## 技术栈

- FastAPI：高性能异步Web框架
- Uvicorn：ASGI服务器
- Jinja2：模板引擎
- OpenAI API：用于故事转换和翻译
- 多种TTS API：用于语音合成

## 注意事项

- 请确保已安装 ffmpeg
- API Key 请妥善保管，不要泄露
- 对谈模式中，建议为不同角色选择差异明显的音色，增强区分度
- 流式API处理会保持长连接，请确保网络稳定 

# ElevenLabs 音色列表

本项目支持以下 ElevenLabs 音色:

## 可用音色

1. **Mark** (ID: UgBBYS2sOqTuMpoF3BR0)
   - 分类：专业版（professional）
   - 描述：自然对话的年轻成年人声音，非常适合对话 AI
   - 特点：
     - 口音：美式英语
     - 风格：随意
     - 年龄：年轻
     - 性别：男性
     - 用途：对话场景

2. **Rachel** (ID: 21m00Tcm4TlvDq8ikWAM)
   - 分类：预制版（premade）
   - 特点：
     - 口音：美式英语
     - 风格：平静
     - 年龄：年轻
     - 性别：女性
     - 用途：叙述

3. **Drew** (ID: 29vD33N1CtxCmqQRPOHJ)
   - 分类：预制版（premade）
   - 特点：
     - 口音：美式英语
     - 风格：全面
     - 年龄：中年
     - 性别：男性
     - 用途：新闻播报

4. **Clyde** (ID: 2EiwWnXFnvU5JabPnv8n)
   - 分类：预制版（premade）
   - 特点：
     - 口音：美式英语
     - 风格：战争老兵
     - 年龄：中年
     - 性别：男性
     - 用途：角色扮演

5. **Paul** (ID: 5Q0t7uMcjvnagumLfvZi)
   - 分类：预制版（premade）
   - 特点：
     - 口音：美式英语
     - 风格：权威
     - 年龄：中年
     - 性别：男性
     - 用途：新闻播报

6. **Aria** (ID: 9BWtsMINqrJLrRacOk9x)
   - 分类：预制版（premade）
   - 特点：
     - 口音：美式英语
     - 风格：富有表现力
     - 年龄：中年
     - 性别：女性
     - 用途：社交媒体

7. **Domi** (ID: AZnzlk1XvdvUeBnXmlld)
   - 分类：预制版（premade）
   - 特点：
     - 口音：美式英语
     - 风格：有力
     - 年龄：年轻
     - 性别：女性
     - 用途：叙述

8. **Dave** (ID: CYw3kZ02Hs0563khs1Fj)
   - 分类：预制版（premade）
   - 特点：
     - 口音：英式英语
     - 风格：对话式
     - 年龄：年轻
     - 性别：男性
     - 用途：角色扮演

9. **Roger** (ID: CwhRBWXzGAHq8TQ4Fs17)
   - 分类：预制版（premade）
   - 特点：
     - 口音：美式英语
     - 风格：自信
     - 年龄：中年
     - 性别：男性
     - 用途：社交媒体

10. **Fin** (ID: D38z5RcWu1voky8WS1ja)
    - 分类：预制版（premade）
    - 特点：
      - 口音：爱尔兰英语
      - 风格：水手
      - 年龄：老年
      - 性别：男性
      - 用途：角色扮演

## 音色参数说明

每个音色都支持以下参数调整：

1. **语音稳定性 (stability)**
   - 范围：0-1
   - 默认值：0.75
   - 说明：值越高，语音越稳定但可能情感表现越单调

2. **音色相似度 (similarity_boost)**
   - 范围：0-1
   - 默认值：0.75
   - 说明：值越高，越接近原始音色，但可能不够稳定

3. **语速 (speed)**
   - 范围：0.7-1.2
   - 默认值：1.0
   - 说明：1.0 为正常语速

sk_0aeef3355c3cbf53d9ba16503931bc0b34bcd5bc8f1d05da