import openai
import json # Import json for potential future use if yielding structured data
import httpx # 导入 httpx
from config import (
    TRANSLATION_OPENAI_API_KEY,
    TRANSLATION_OPENAI_BASE_URL,
    TRANSLATION_OPENAI_MODEL
)

class Translator:
    def __init__(self, api_key=None, base_url=None, model=None):
        # 优先使用传入的参数，否则使用配置文件中的默认值
        self.api_key = api_key or TRANSLATION_OPENAI_API_KEY
        self.base_url = base_url or TRANSLATION_OPENAI_BASE_URL
        self.model = model or TRANSLATION_OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError("未设置 OpenAI API Key")
        
        # 配置HTTP客户端（确保不使用代理）
        async_http_client = httpx.AsyncClient(proxy=None, transport=httpx.AsyncHTTPTransport(retries=1))
        
        # 配置异步 openai 客户端
        try:
            print("正在创建翻译器的 OpenAI 客户端...")
            # 显式传递我们创建的、无代理的httpx客户端
            self.client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=openai.Timeout(
                    connect=30.0,
                    read=300.0,  # 翻译通常比对话生成快，可以用更短的超时
                    write=30.0,
                    pool=30.0
                ),
                http_client=async_http_client # 传递自定义的AsyncClient
            )
            print("翻译器的 OpenAI 客户端创建成功")
        except Exception as e:
            print(f"创建翻译器的 OpenAI 客户端失败: {str(e)}")
            # 如果创建失败，尝试关闭已创建的http客户端
            try:
                import asyncio
                asyncio.run(async_http_client.aclose())
            except Exception:
                pass
            raise
        
        # 翻译系统提示词
        self.system_prompt = """You are a professional translator specializing in translating Chinese conversational scripts into fluent and natural-sounding English. 
Please follow these rules:
1. Maintain the original format, including speaker labels like [主持人] and [嘉宾]
2. Do not translate speaker labels [主持人] and [嘉宾]
3. Keep all rich text markup tags (such as <strong>, [breath], [laughter], etc.)
4. Ensure the accuracy of the content translation while maintaining the natural tone of spoken dialogue
5. According to English conversation habits, appropriately refine the original text into a more native English oral dialogue script for gossip scenes"""

    async def translate_stream(self, text_to_translate: str):
        """
        将中文对话脚本翻译成英文 (流式输出)
        
        Args:
            text_to_translate: 要翻译的中文文本
            
        Yields:
            str: 翻译结果的数据块 (content chunk)
            
        Raises:
            Exception: 如果 OpenAI API 调用失败或其他错误发生
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text_to_translate}
                ],
                temperature=0.7,
                stream=True  # 启用流式输出
            )
            
            async for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content # 直接 yield 内容块
                        
        except Exception as e:
            print(f"Error during OpenAI stream translation: {e}")
            # 让异常向上冒泡，由调用者 (app.py) 处理并发送错误 SSE
            raise # Re-raise the exception

    # 保留非流式方法以备不时之需或用于测试？(可选，暂时注释掉)
    # async def translate(self, text_to_translate: str) -> dict:
    #    ... 