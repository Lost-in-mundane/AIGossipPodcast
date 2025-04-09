from flask import Flask, request, send_file, render_template, jsonify, Response, stream_with_context
from pydub import AudioSegment
import tempfile
import os
import json
from tts_factory import TTSFactory
from multiTTS import DialogueTTS  # 导入对谈模式处理类
from story_converter import StoryConverter
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, DEFAULT_TTS_ENGINE
import time

app = Flask(__name__)

# 初始化默认 TTS 实例
tts = TTSFactory.create_tts(DEFAULT_TTS_ENGINE)
# dialogue_tts = DialogueTTS(tts)  # 不再需要全局初始化，在路由中动态创建
story_converter = StoryConverter(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    model=OPENAI_MODEL
)  # 使用配置文件中的参数

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """获取指定TTS引擎的音色列表"""
    engine = request.args.get('engine', DEFAULT_TTS_ENGINE)
    voices = TTSFactory.get_voices_for_ui(engine)
    return jsonify(voices)

@app.route('/convert', methods=['POST'])
def convert():
    try:
        # 获取文本内容
        if not request.is_json:
            return "请求必须是 JSON 格式", 400
            
        data = request.get_json()
        if not data or 'text' not in data:
            return "请求必须包含 'text' 字段", 400
            
        text = data['text']
        voice = data.get('voice', 'anna')  # 默认根据引擎不同自动选择默认音色
        speed = float(data.get('speed', 1.0))  # 默认语速 1.0
        tts_engine = data.get('tts_engine', DEFAULT_TTS_ENGINE)  # 获取TTS引擎选择
        
        if not isinstance(text, str):
            return "'text' 必须是字符串", 400
            
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return "文本内容不能为空", 400
        
        # 创建临时目录存放音频文件
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_segments = []
            
            # 创建相应的TTS客户端
            current_tts = TTSFactory.create_tts(tts_engine)
            
            # 逐行转换文本为语音
            for i, line in enumerate(lines):
                temp_file = os.path.join(temp_dir, f'temp_{i}.wav')
                success = current_tts.text_to_speech(
                    text=line,
                    output_path=temp_file,
                    voice_name=voice,
                    speed=speed,
                    response_format="wav"  # 使用 wav 格式便于合并
                )
                
                if not success:
                    raise Exception(f"转换失败：{line}")
                
                # 读取音频文件并添加到列表
                audio_segment = AudioSegment.from_wav(temp_file)
                audio_segments.append(audio_segment)
            
            # 在每段之间添加 0.5 秒的静音
            silence = AudioSegment.silent(duration=500)
            final_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                final_audio += silence + segment
            
            # 导出合并后的音频到临时文件
            output_path = os.path.join(temp_dir, 'final_output.wav')
            final_audio.export(output_path, format="wav")
            
            # 返回音频文件
            return send_file(
                output_path,
                mimetype="audio/wav",
                as_attachment=True,
                download_name="combined_audio.wav"
            )
            
    except Exception as e:
        return str(e), 500

@app.route('/convert_dialogue', methods=['POST'])
def convert_dialogue():
    """对谈模式音频生成接口"""
    try:
        # 获取请求数据
        if not request.is_json:
            return "请求必须是 JSON 格式", 400
            
        data = request.get_json()
        if not data or 'dialogue_text' not in data:
            return "请求必须包含 'dialogue_text' 字段", 400
            
        # 获取参数
        dialogue_text = data['dialogue_text']
        host_voice = data.get('host_voice', 'anna') # Default voice might need to be engine-specific
        guest_voice = data.get('guest_voice', 'alex') # Default voice might need to be engine-specific
        host_speed = float(data.get('host_speed', 1.0))
        guest_speed = float(data.get('guest_speed', 1.0))
        silence_duration = int(data.get('silence_duration', 600)) # Increased default silence
        host_tts_engine = data.get('host_tts_engine', DEFAULT_TTS_ENGINE)  # 主持人TTS引擎
        guest_tts_engine = data.get('guest_tts_engine', DEFAULT_TTS_ENGINE) # 嘉宾TTS引擎
        
        # 创建相应的TTS客户端实例
        host_tts = TTSFactory.create_tts(host_tts_engine)
        guest_tts = TTSFactory.create_tts(guest_tts_engine)
        
        # 初始化对谈处理器，传入两个不同的TTS实例
        current_dialogue_tts = DialogueTTS(host_tts, guest_tts)
        
        # 创建临时目录和文件
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'dialogue_audio.wav')
            
            # 生成对谈音频 (不再需要传递 tts_engine)
            success = current_dialogue_tts.generate_dialogue_audio(
                dialogue_text=dialogue_text,
                output_path=output_path,
                host_voice=host_voice,
                guest_voice=guest_voice,
                host_speed=host_speed,
                guest_speed=guest_speed,
                silence_duration=silence_duration
            )
            
            if not success:
                raise Exception("生成对谈音频失败")
                
            # 返回音频文件
            return send_file(
                output_path,
                mimetype="audio/wav",
                as_attachment=True,
                download_name="dialogue_audio.wav"
            )
            
    except Exception as e:
        print(f"Error in convert_dialogue: {str(e)}") # 添加更详细的错误日志
        return str(e), 500

@app.route('/convert_story', methods=['GET', 'POST'])
def convert_story():
    # 处理 GET 请求 - 建立 SSE 连接
    if request.method == 'GET' and request.args.get('stream') == 'true':
        def create_connection():
            try:
                # 发送 SSE 连接确认
                yield f"data: {json.dumps({'status': 'connected'})}\n\n"
                
                # 保持连接活跃
                while True:
                    time.sleep(1)
                    yield f"data: {json.dumps({'status': 'heartbeat'})}\n\n"
            except GeneratorExit:
                print("SSE connection closed by client")
        
        return Response(
            stream_with_context(create_connection()), 
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
    
    # 处理 POST 请求 - 实际处理转换请求
    try:
        data = request.get_json()
        story_text = data['story_text']
        custom_prompt = data.get('custom_prompt')
        use_stream = data.get('use_stream', True)  # 默认使用流式输出
        
        if not use_stream:
            # 非流式模式
            result = story_converter.convert_story(
                story_text=story_text,
                custom_prompt=custom_prompt
            )
            return jsonify(result)
        else:
            # 流式模式 - 返回 Server-Sent Events
            def generate():
                try:
                    print("开始创建 OpenAI 请求...")  # 调试日志
                    response = story_converter.client.chat.completions.create(
                        model=story_converter.model,
                        messages=[
                            {"role": "system", "content": custom_prompt or story_converter.system_prompt},
                            {"role": "user", "content": story_text}
                        ],
                        temperature=0.7,
                        stream=True
                    )
                    print("OpenAI 请求创建成功，开始处理流式响应...")  # 调试日志
                    
                    yield f"data: {json.dumps({'status': 'start'})}\n\n"
                    
                    for chunk in response:
                        print(f"收到数据块: {chunk}")  # 调试日志
                        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            print(f"提取的内容: {content}")  # 调试日志
                            if content.strip():  # 确保内容不是空白
                                print(f"发送内容到前端: {content}")  # 调试日志
                                yield f"data: {json.dumps({'content': content})}\n\n"
                    
                    print("数据流处理完成，发送完成标记...")  # 调试日志
                    yield f"data: {json.dumps({'status': 'done'})}\n\n"
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"发生错误: {error_msg}")  # 调试日志
                    print(f"错误详情: ", e)  # 调试日志
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
            
            return Response(
                stream_with_context(generate()), 
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'
                }
            )
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error in story conversion: {error_msg}")
        return jsonify({"success": False, "error": error_msg})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 