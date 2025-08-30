# 🎙️ AIGossipPodcast - AI 狗血故事播客生成器

> 一个专门用于将八卦、狗血故事转换成生动播客对话的AI工具

**AIGossipPodcast** 是一个基于 AI音频合成服务 的播客生成工具，专注于将各种奇闻异事、情感故事、八卦传闻转化为引人入胜的播客对话。通过大语言模型和多种 TTS 语音合成技术，让任何文字故事都能变成专业级的播客内容。

## ✨ 核心特色

🤖 **AI 剧本转换** - 使用大语言模型将枯燥的文字故事转换为生动的主持人与嘉宾对话脚本  
🎭 **狗血故事专家** - 专门优化处理情感纠纷、奇闻异事、社会八卦等"狗血"内容  
🗣️ **多引擎 TTS** - 支持 SiliconFlow、MiniMax、ElevenLabs、阿里云 CosyVoice 四种语音合成  
🎚️ **对谈模式** - 双音色播客生成，主持人和嘉宾使用不同声音  
🌍 **中英翻译** - 支持中文故事翻译为英文播客脚本  
🎨 **富文本控制** - 支持呼吸声、笑声、语气加强等播客效果  

## 🎯 适用场景

- **情感故事播客** - 将网络热门情感故事转换为播客
- **奇闻异事节目** - 生成都市传说、奇异事件对话
- **八卦娱乐内容** - 制作娱乐圈、社会热点讨论
- **故事电台** - 快速生成故事类电台节目内容

## 🚀 快速开始

### 环境要求

- **Python**: 3.9+ 
- **系统依赖**: FFmpeg (用于音频处理)
- **API 密钥**: 至少配置一个 TTS 服务的 API 密钥

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/你的用户名/AIGossipPodcast.git
cd AIGossipPodcast
```

2. **安装依赖**
```bash
pip install -r requirements.txt

# macOS 用户需要安装 FFmpeg
brew install ffmpeg

# Linux 用户
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL
```

3. **配置 API 密钥**
```bash
# 复制配置模板
cp config.json.example config.json

# 编辑配置文件，填入你的 API 密钥
nano config.json
```

4. **启动服务**
```bash
# 开发模式
python run.py

# 生产模式
uvicorn app:app --host 0.0.0.0 --port 5001
```

5. **访问应用**
- 🌐 **Web 界面**: http://localhost:5001
- 📖 **API 文档**: http://localhost:5001/docs

## ⚙️ API 密钥配置指南

编辑 `config.json` 文件，至少配置一个 TTS 服务：

```json
{
  "API_KEYS": {
    "siliconflow_api_key": "sk-你的密钥",
    "openai": "sk-你的OpenAI密钥",
    "elevenlabs": "你的ElevenLabs密钥",
    "minimax_api_key": "你的MiniMax密钥",
    "aliyun_access_key_id": "你的阿里云密钥"
  },
  "DEFAULT_TTS_ENGINE": "siliconflow"
}
```

### 🔑 API 密钥获取地址

| 服务商 | 获取地址 | 说明 |
|--------|----------|------|
| **SiliconFlow** | https://cloud.siliconflow.cn | 推荐，性价比高 |
| **OpenAI** | https://platform.openai.com | 故事转换必需 |
| **ElevenLabs** | https://elevenlabs.io | 英文语音效果最佳 |
| **MiniMax** | https://www.minimaxi.com | 中文语音自然 |
| **阿里云** | https://dashscope.console.aliyun.com | 国内服务稳定 |

## 🎪 使用指南

### 基础文本转语音

1. 在"基础模式"标签页输入文本
2. 选择 TTS 引擎和音色
3. 调整语速参数
4. 点击"转换"生成音频

### 🎭 狗血故事转播客（核心功能）

1. **准备故事素材**
   ```
   今天要讲一个发生在小区里的奇葩事。我有个邻居，表面上是个温文尔雅的大学教师，
   但是背地里却做着让人意想不到的事情...（故事内容）
   ```

2. **AI 脚本转换**
   - 切换到"故事转换"标签页
   - 粘贴你的故事文本
   - 点击"转换故事"
   - 等待 AI 生成播客对话脚本

3. **生成的脚本示例**
   ```
   [嘉宾]你知道吗，我今天要跟你说个特别离奇的事...[breath]
   [主持人]哦？什么事这么神秘？
   [嘉宾]就是我们小区那个大学老师，表面看着[breath]特别斯文...
   [主持人]<strong>然后呢？</strong>一定有反转吧！[laughter]
   ```

4. **语音合成**
   - 复制生成的脚本到"对谈模式"
   - 为主持人和嘉宾选择不同音色
   - 调整语速和停顿时间
   - 点击"生成对谈"获得最终音频

### 🌍 中英翻译功能

将中文播客脚本翻译为英文：
1. 切换到"翻译"标签页
2. 输入中文对话脚本
3. 点击"翻译脚本"
4. 获得保持格式的英文版本

### 🎛️ 高级音效控制

使用富文本标记增强播客效果：

```
[嘉宾]我跟你说[breath]，这件事简直[noise]太离谱了！
[主持人]<strong>真的假的？</strong>[laughter]快说说！
[嘉宾][sigh]好吧，事情是这样的...[quick_breath]
```

**支持的音效标记**:
- `[breath]` - 呼吸声
- `[laughter]` - 笑声  
- `[sigh]` - 叹息声
- `[noise]` - 噪音
- `<strong>文本</strong>` - 语气加强
- `[quick_breath]` - 快速呼吸

## 🔧 技术架构

- **后端**: FastAPI + Uvicorn
- **前端**: 原生 HTML/CSS/JavaScript
- **AI 模型**: OpenAI GPT 系列
- **语音合成**: 多厂商 TTS API 集成
- **音频处理**: pydub + FFmpeg
- **异步处理**: Server-Sent Events (SSE)

## 📂 项目结构

```
AIGossipPodcast/
├── app.py                 # FastAPI 主应用
├── run.py                 # 启动脚本
├── config_manager.py      # 配置管理
├── story_converter.py     # 故事转换核心逻辑
├── translator.py          # 翻译功能
├── multiTTS.py           # 对谈模式音频生成
├── tts_factory.py        # TTS 工厂模式
├── tts_*.py              # 各 TTS 引擎实现
├── templates/            # 前端模板
├── static/              # 静态资源
├── config.json.example  # 配置模板
└── requirements.txt     # Python 依赖
```

## 🎨 自定义提示词

项目使用专门优化的 AI 提示词（`prompt.md`）来生成播客对话。提示词经过精心调优，专门处理：

- 情感冲突类故事
- 奇闻异事类内容  
- 社会热点八卦
- 人际关系纠纷

你可以根据需要修改提示词来适应特定类型的故事。

## 🐛 常见问题

**Q: 为什么音频生成失败？**  
A: 检查 API 密钥是否正确配置，确保网络连接正常。

**Q: FFmpeg 相关错误怎么解决？**  
A: 确保系统已安装 FFmpeg，macOS 用户使用 `brew install ffmpeg`。

**Q: 支持哪些音频格式？**  
A: 输出支持 WAV 格式，可使用其他工具转换为 MP3。

**Q: 如何提高故事转换质量？**  
A: 输入的故事要有完整情节，包含冲突和反转，长度建议 200-2000 字。

**Q: 能否批量处理多个故事？**  
A: 目前支持单个故事处理，批量功能可通过 API 调用实现。

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 开源协议

本项目采用 MIT 协议开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- OpenAI - 提供强大的 GPT 模型
- 各 TTS 服务商 - SiliconFlow、MiniMax、ElevenLabs、阿里云
- FastAPI - 优秀的 Web 框架
- 所有贡献者和用户

---

**⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！**

**🎙️ 让每个故事都变成精彩的播客！**