from fastapi import FastAPI, Request, Response, HTTPException, Depends, File, UploadFile, Body
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, AsyncGenerator
from starlette.background import BackgroundTask

from pydub import AudioSegment
import tempfile
import os
import json
import time
import asyncio
from pathlib import Path

from tts_factory import TTSFactory
from multiTTS import DialogueTTS
from story_converter import StoryConverter
from translator import Translator
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, DEFAULT_TTS_ENGINE

# 创建 FastAPI 应用
app = FastAPI(
    title="LDtts - 语音生成平台",
    description="一个基于多种语音引擎的文本到语音转换服务",
    version="1.0.0"
)

# CORS 设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置静态文件和模板
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化默认 TTS 实例和故事转换器
story_converter = StoryConverter(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    model=OPENAI_MODEL
)

# Pydantic 模型定义
class TextToSpeechRequest(BaseModel):
    text: str
    voice: str = "anna"
    speed: float = 1.0
    tts_engine: str = DEFAULT_TTS_ENGINE

    @validator('speed')
    def validate_speed(cls, v):
        if not (0.25 <= v <= 4.0):
            raise ValueError("语速必须在 0.25 到 4.0 之间")
        return v

class DialogueRequest(BaseModel):
    dialogue_text: str
    host_voice: str = "anna"
    guest_voice: str = "alex"
    host_speed: float = 1.0
    guest_speed: float = 1.0
    silence_duration: int = 600
    host_tts_engine: str = DEFAULT_TTS_ENGINE
    guest_tts_engine: str = DEFAULT_TTS_ENGINE

    @validator('host_speed', 'guest_speed')
    def validate_speed(cls, v):
        if not (0.25 <= v <= 4.0):
            raise ValueError("语速必须在 0.25 到 4.0 之间")
        return v

class StoryRequest(BaseModel):
    story_text: str
    custom_prompt: Optional[str] = None
    use_stream: bool = True

class TranslationRequest(BaseModel):
    text_to_translate: str

# 路由定义
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """返回首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/voices")
async def get_voices(engine: str = DEFAULT_TTS_ENGINE):
    """获取指定TTS引擎的音色列表"""
    voices = TTSFactory.get_voices_for_ui(engine)
    return voices

@app.post("/convert")
async def convert(request: TextToSpeechRequest):
    """将文本转换为语音"""
    try:
        lines = [line.strip() for line in request.text.split('\n') if line.strip()]
        if not lines:
            raise HTTPException(status_code=400, detail="文本内容不能为空")
        
        # 创建命名临时文件
        temp_final = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_final.close()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_segments = []
            current_tts = TTSFactory.create_tts(request.tts_engine)
            
            for i, line in enumerate(lines):
                temp_file = os.path.join(temp_dir, f'temp_{i}.wav')
                success = current_tts.text_to_speech(
                    text=line,
                    output_path=temp_file,
                    voice_name=request.voice,
                    speed=request.speed,
                    response_format="wav"
                )
                
                if not success:
                    os.unlink(temp_final.name)  # 清理临时文件
                    raise HTTPException(status_code=500, detail=f"转换失败：{line}")
                
                audio_segment = AudioSegment.from_wav(temp_file)
                audio_segments.append(audio_segment)
            
            silence = AudioSegment.silent(duration=500)
            final_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                final_audio += silence + segment
            
            final_audio.export(temp_final.name, format="wav")
            
        return FileResponse(
            path=temp_final.name,
            media_type="audio/wav",
            filename="combined_audio.wav",
            background=BackgroundTask(os.unlink, temp_final.name)
        )
            
    except Exception as e:
        if 'temp_final' in locals():
            os.unlink(temp_final.name)  # 确保出错时也清理临时文件
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert_dialogue")
async def convert_dialogue(request: DialogueRequest):
    """对谈模式音频生成接口"""
    try:
        host_tts = TTSFactory.create_tts(request.host_tts_engine)
        guest_tts = TTSFactory.create_tts(request.guest_tts_engine)
        dialogue_tts = DialogueTTS(host_tts, guest_tts)
        
        # 创建命名临时文件
        temp_final = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_final.close()
        
        success = dialogue_tts.generate_dialogue_audio(
            dialogue_text=request.dialogue_text,
            output_path=temp_final.name,
            host_voice=request.host_voice,
            guest_voice=request.guest_voice,
            host_speed=request.host_speed,
            guest_speed=request.guest_speed,
            silence_duration=request.silence_duration
        )
        
        if not success:
            os.unlink(temp_final.name)
            raise HTTPException(status_code=500, detail="生成对谈音频失败")
            
        return FileResponse(
            path=temp_final.name,
            media_type="audio/wav",
            filename="dialogue_audio.wav",
            background=BackgroundTask(os.unlink, temp_final.name)
        )
            
    except Exception as e:
        if 'temp_final' in locals():
            os.unlink(temp_final.name)
        print(f"Error in convert_dialogue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# SSE连接端点
@app.get("/convert_story")
async def convert_story_connection():
    """建立Server-Sent Events连接"""
    
    async def event_generator():
        try:
            # 发送连接确认
            yield f"data: {json.dumps({'status': 'connected'})}\n\n"
            
            # 保持连接活跃
            while True:
                await asyncio.sleep(1)
                yield f"data: {json.dumps({'status': 'heartbeat'})}\n\n"
        except asyncio.CancelledError:
            print("SSE connection closed")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

# 故事转换处理端点
@app.post("/convert_story")
async def convert_story_process(request: StoryRequest):
    """处理故事转换请求"""
    try:
        if not request.use_stream:
            # 非流式模式
            result = await story_converter.convert_story_async(
                story_text=request.story_text,
                custom_prompt=request.custom_prompt
            )
            return result
        else:
            # 流式模式
            async def generate():
                try:
                    print("开始流式对话转换...")
                    
                    yield f"data: {json.dumps({'status': 'start'})}\n\n"
                    
                    async for content in story_converter.convert_story_stream(
                        story_text=request.story_text,
                        custom_prompt=request.custom_prompt
                    ):
                        if content.strip():
                            yield f"data: {json.dumps({'content': content})}\n\n"
                    
                    print("数据流处理完成，发送完成标记...")
                    yield f"data: {json.dumps({'status': 'done'})}\n\n"
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"发生错误: {error_msg}")
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'
                }
            )
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error in story conversion: {error_msg}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": error_msg}
        )

@app.post("/translate_script")
async def translate_script_stream(request: TranslationRequest):
    """将中文对话脚本翻译成英文 (流式 SSE)"""
    if not request.text_to_translate:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "'text_to_translate' 字段不能为空"}
        )

    async def generate_translation():
        try:
            translator = Translator()
            print("TRANSLATE STREAM: Yielding start event")
            yield f"data: {json.dumps({'status': 'start'})}\n\n" 

            chunk_count = 0
            async for content_chunk in translator.translate_stream(request.text_to_translate):
                chunk_count += 1
                print(f"TRANSLATE STREAM: Received chunk {chunk_count}: {content_chunk[:50]}...")
                yield f"data: {json.dumps({'content': content_chunk})}\n\n"

            print(f"TRANSLATE STREAM: Finished loop after {chunk_count} chunks. Yielding done event.")
            yield f"data: {json.dumps({'status': 'done'})}\n\n" 

        except Exception as e:
            error_msg = str(e)
            print(f"Error during streaming translation: {error_msg}")
            yield f"data: {json.dumps({'error': error_msg})}\n\n"

    return StreamingResponse(
        generate_translation(),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True) 