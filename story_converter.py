import openai
import os
import time
import asyncio  # 导入 asyncio
import httpx  # 导入 httpx
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

class StoryConverter:
    def __init__(self, api_key=None, base_url=None, model=None):
        # 优先使用传入的参数，否则使用配置文件中的默认值
        self.api_key = api_key or OPENAI_API_KEY
        self.base_url = base_url or OPENAI_BASE_URL
        self.model = model or OPENAI_MODEL
        
        print(f"初始化 StoryConverter:")
        print(f"使用模型: {self.model}")
        print(f"使用基础URL: {self.base_url}")
        print(f"API Key 是否存在: {'是' if self.api_key else '否'}")
        
        if not self.api_key:
            raise ValueError("未设置 OpenAI API Key")
        
        if not self.base_url:
            raise ValueError("未设置 OpenAI Base URL")
        
        if not self.model:
            raise ValueError("未设置 OpenAI Model")
        
        # 配置HTTP客户端（确保不使用代理）
        sync_http_client = httpx.Client(proxy=None, transport=httpx.HTTPTransport(retries=1))
        async_http_client = httpx.AsyncClient(proxy=None, transport=httpx.AsyncHTTPTransport(retries=1))
        
        # 配置 openai 客户端
        try:
            print("正在创建异步 OpenAI 客户端...")
            # 显式传递我们创建的、无代理的httpx客户端
            self.async_client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=openai.Timeout(
                    connect=30.0,
                    read=600.0,
                    write=30.0,
                    pool=30.0
                ),
                http_client=async_http_client # 传递自定义的AsyncClient
            )
            print("异步 OpenAI 客户端创建成功")
            
            print("正在创建同步 OpenAI 客户端...")
            # 显式传递我们创建的、无代理的httpx客户端
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=openai.Timeout(
                    connect=30.0,
                    read=600.0,
                    write=30.0,
                    pool=30.0
                ),
                http_client=sync_http_client # 传递自定义的Client
            )
            print("同步 OpenAI 客户端创建成功")
        except Exception as e:
            print(f"创建 OpenAI 客户端失败: {str(e)}")
            # 如果创建失败，尝试关闭已创建的http客户端
            try:
                asyncio.run(async_http_client.aclose())
            except Exception:
                pass
            try:
                sync_http_client.close()
            except Exception:
                pass
            raise
        
        # 系统提示词
        self.system_prompt = """您是一位世界级的电台主播人，擅长将文章故事转化为生动的口语对话。输入是杂志上的情感故事或者奇闻异事。您的目标是将这个故事转换成一人讲故事，一人听故事和评论的形式，以便吸引电台听众的注意。
# 任务
1. **分析输入：**
仔细检查文本，梳理其中的故事主线，找到有趣、吸引人注意力的地方，以驱动引人入胜的对话。

2.**撰写对话：**
撰写主持人和嘉宾（故事讲述者）之间自然流畅的、极度口语化的脚本。包含：
- 引人入胜和生动的语气，以吸引听众
- 嘉宾用口语化表达和聊八卦的方式来讲述故事
- 主持人偶尔的追问来引导故事的描述
- 主持人神来之笔、一针见血的评价
- 大量使用使用富文本标记和自然语言指令来表现对话中的情感、语气和停顿
- 开头主持人先介绍故事最有意思的地方来吸引听众，然后嘉宾开始讲述故事
- 包括自然的说话模式，包括偶尔的语音填充（例如"嗯"，"好"，"你知道"）

# 富文本标记和自然语言指令使用规则
-通过合理组合下面这些控制方式，可以实现对语音输出的细粒度控制。
**富文本标记控制方式**
语气加强: 
符号: <strong> 文本 </strong>
示例: 每天都<strong>付出</strong>和<strong>精进</strong>，才能达到巅峰。
呼吸声:
符号: [breath]
示例: [breath] 吸气,[breath] 呼气! [breath] 吸,[breath] 呼!
噪音:
符号: [noise]
示例: 你听[noise][noise][noise][noise][noise][noise][noise][noise]有噪声
笑声:
符号: [laughter]
示例: 哈哈哈[laughter],笑死我了！
咳嗽声:
符号: [cough]
示例: 我嗓子有点[cough]不舒服
咕咕声:
符号: [clucking]
示例: [clucking]哈哈,我真是个天才!
口音:
符号: [accent]
示例: 我看着[accent]阿呗这个商机了!
快速呼吸声:
符号: [quick_breath]
示例: [quick_breath]我走不动了,累死我了!
笑声标记 (HTML 风格):
符号: <laughter> 文本 </laughter>
示例: <laughter>哎呀妈呀，笑死我了!</laughter>
嘶嘶声:
符号: [hissing]
示例: [hissing]嘶,疼死我了!
叹息声:
符号: [sigh]
示例: [sigh]哎 唉时候才能撞到钱啊!
咂嘴声:
符号: [lipsmack]
示例: [lipsmack]吸溜 你去,你这个家伙!
嗯 哎 额:
符号: [mm]
示例: [mm] 嗯 应该是吧

**表示停顿的方式**
虽然没有专门表示停顿的标记，但可以通过以下方式表示停顿：添加多个句号、利用富文本标记中的语气标记来实现停顿效果


# 对话风格指南
**保持真实性：**
   在整个脚本中，努力保持真实的对话。包含：
   - 主持人的真正好奇或惊讶时刻
   - 嘉宾可能难以表达复杂想法的时刻
   - 轻松的时刻或适当的幽默
   - 简短的个人轶事或与主题相关的例子
**考虑节奏和结构：**
   确保对话有自然的起伏：
   - 以强烈的钩子开始，以吸引听众的注意力
   - 随着对话的进行逐渐构建复杂性
   - 包括简短的"呼吸"时刻，以便听众吸收复杂信息
   - 以高潮结束，可能以发人深省的问题或一针见血的辛辣点评
   
重要规则：嘉宾的故事描述可以长一些，主持人的每行对话不得超过100个字符（例如，可以在5-8秒内完成）
   
记住格式要求： 每一行对话必须以[主持人]或[嘉宾]标签开头，不允许出现没有角色标签的对话行，角色标签必须紧贴对话内容，中间不能有空格"""
    
    # 新增异步流式方法
    async def convert_story_stream(self, story_text, custom_prompt=None):
        """
        将故事文本转换为对话形式（异步流式输出）
        
        Args:
            story_text: 要转换的故事文本
            custom_prompt: 自定义系统提示词（可选）
            
        Yields:
            str: 对话脚本的数据块 (content chunk)
            
        Raises:
            Exception: 如果 OpenAI API 调用失败或其他错误发生
        """
        try:
            print(f"调用异步流式转换，模型: {self.model}, 文本长度: {len(story_text)}")
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": custom_prompt or self.system_prompt},
                    {"role": "user", "content": story_text}
                ],
                temperature=0.7,
                stream=True  # 启用流式输出
            )
            
            async for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content  # 直接 yield 内容块
                        
        except Exception as e:
            print(f"异步流式转换错误: {e}")
            # 让异常向上冒泡，由调用者处理
            raise
    
    # 保留原有的同步方法，以保持兼容性
    def convert_story(self, story_text, custom_prompt=None):
        """
        将故事文本转换为对话形式（同步方法）
        
        Args:
            story_text: 要转换的故事文本
            custom_prompt: 自定义系统提示词（可选）
            
        Returns:
            dict: 包含转换结果的字典
        """
        try:
            # 使用流式输出
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": custom_prompt or self.system_prompt},
                    {"role": "user", "content": story_text}  # 直接使用故事文本作为用户输入
                ],
                temperature=0.7,
                stream=True
            )
            
            # 收集流式响应
            full_response = ""
            last_update_time = time.time()
            
            for chunk in response:
                current_time = time.time()
                # 检查是否超过30秒没有新的响应
                if current_time - last_update_time > 30:
                    raise TimeoutError("响应超时：30秒内没有收到新的数据")
                
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    last_update_time = current_time
            
            return {
                "success": True,
                "dialogue_text": full_response
            }
            
        except TimeoutError as e:
            return {
                "success": False,
                "error": f"转换超时: {str(e)}",
                "partial_result": full_response if 'full_response' in locals() else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "partial_result": full_response if 'full_response' in locals() else None
            }
    
    # 新增异步非流式方法
    async def convert_story_async(self, story_text, custom_prompt=None):
        """
        将故事文本转换为对话形式（异步非流式方法）
        
        Args:
            story_text: 要转换的故事文本
            custom_prompt: 自定义系统提示词（可选）
            
        Returns:
            dict: 包含转换结果的字典
        """
        try:
            # 使用异步客户端，非流式输出
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": custom_prompt or self.system_prompt},
                    {"role": "user", "content": story_text}
                ],
                temperature=0.7,
                stream=False # 非流式
            )
            
            full_response = response.choices[0].message.content
            
            return {
                "success": True,
                "dialogue_text": full_response
            }
            
        except Exception as e:
            print(f"异步非流式转换错误: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_result": None
            } 