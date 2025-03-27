import openai
import os
import time
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

class StoryConverter:
    def __init__(self, api_key=None, base_url=None, model=None):
        # 优先使用传入的参数，否则使用配置文件中的默认值
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or OPENAI_API_KEY
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL") or OPENAI_BASE_URL
        self.model = model or os.environ.get("OPENAI_MODEL") or OPENAI_MODEL
        
        # 配置openai客户端
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=60.0  # 增加超时时间
        )
        
        self.default_prompt = """
将故事转换为[主持人]和[嘉宾]的对谈形式。遵循以下规则：

1. 格式要求：
- 每一行对话必须以[主持人]或[嘉宾]标签开头
- 不允许出现没有角色标签的对话行
- 角色标签必须紧贴对话内容，中间不能有空格

2. 角色分工：
- 主持人负责叙述、追问和点评
- 嘉宾负责讲述故事细节和回应

3. 标记使用：
- 适当使用[breath]表示停顿
- 使用<strong></strong>标记强调内容
- 保持段落简短，适合有声播放

示例格式：
[主持人]欢迎来到今天的节目。
[嘉宾]谢谢主持人的邀请。[breath]今天我想分享一个特别的故事。
[主持人]<strong>太好了</strong>，我们都很期待。
"""
    
    def convert_story(self, story_text, custom_prompt=None):
        try:
            prompt = custom_prompt or self.default_prompt
            full_prompt = f"{prompt}\n\n{story_text}"
            
            # 使用流式输出
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是广播剧本创作专家。"},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                stream=True  # 启用流式输出
            )
            
            # 收集流式响应
            full_response = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
            return {
                "success": True,
                "dialogue_text": full_response
            }
        except Exception as e:
            return {"success": False, "error": str(e)} 