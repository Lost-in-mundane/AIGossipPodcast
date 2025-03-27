from flask import Flask, request, send_file, render_template, jsonify, Response, stream_with_context
from pydub import AudioSegment
import tempfile
import os
import json
from tts_api import SiliconFlowTTS
from multiTTS import DialogueTTS  # 导入对谈模式处理类
from story_converter import StoryConverter
from config import TTS_API_KEY, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

app = Flask(__name__)

# 初始化 TTS 实例
tts = SiliconFlowTTS(api_key=TTS_API_KEY)  # 使用配置文件中的API key
dialogue_tts = DialogueTTS(tts)  # 初始化对谈模式处理器
story_converter = StoryConverter(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    model=OPENAI_MODEL
)  # 使用配置文件中的参数

@app.route('/')
def index():
    return render_template('index.html')

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
        voice = data.get('voice', 'anna')  # 默认使用 anna 音色
        speed = float(data.get('speed', 1.0))  # 默认语速 1.0
        
        if not isinstance(text, str):
            return "'text' 必须是字符串", 400
            
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return "文本内容不能为空", 400
        
        # 创建临时目录存放音频文件
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_segments = []
            
            # 逐行转换文本为语音
            for i, line in enumerate(lines):
                temp_file = os.path.join(temp_dir, f'temp_{i}.wav')
                success = tts.text_to_speech(
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
        host_voice = data.get('host_voice', 'anna')
        guest_voice = data.get('guest_voice', 'alex')
        host_speed = float(data.get('host_speed', 1.0))
        guest_speed = float(data.get('guest_speed', 1.0))
        silence_duration = int(data.get('silence_duration', 500))
        
        # 创建临时目录和文件
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'dialogue_audio.wav')
            
            # 生成对谈音频
            success = dialogue_tts.generate_dialogue_audio(
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
        return str(e), 500

@app.route('/convert_story', methods=['GET', 'POST'])
def convert_story():
    # 处理 GET 请求 - 建立 SSE 连接
    if request.method == 'GET' and request.args.get('stream') == 'true':
        def create_connection():
            # 发送 SSE 连接确认
            yield f"data: {json.dumps({'status': 'connected'})}\n\n"
        
        return Response(stream_with_context(create_connection()), 
                      mimetype='text/event-stream')
    
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
                    prompt = custom_prompt or story_converter.default_prompt
                    full_prompt = f"{prompt}\n\n{story_text}"
                    
                    # 使用流式输出
                    response = story_converter.client.chat.completions.create(
                        model=story_converter.model,
                        messages=[
                            {"role": "system", "content": "你是广播剧本创作专家。"},
                            {"role": "user", "content": full_prompt}
                        ],
                        temperature=0.7,
                        stream=True
                    )
                    
                    # 发送事件开始标记
                    yield f"data: {json.dumps({'status': 'start'})}\n\n"
                    
                    # 流式返回数据
                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            yield f"data: {json.dumps({'content': content})}\n\n"
                    
                    # 发送完成标记
                    yield f"data: {json.dumps({'status': 'done'})}\n\n"
                    
                except Exception as e:
                    # 发送错误消息
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return Response(stream_with_context(generate()), 
                          mimetype='text/event-stream')
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 