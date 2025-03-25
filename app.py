from flask import Flask, request, send_file, render_template
from pydub import AudioSegment
import tempfile
import os
from tts_api import SiliconFlowTTS
from multiTTS import DialogueTTS  # 导入对谈模式处理类

app = Flask(__name__)

# 初始化 TTS 实例
tts = SiliconFlowTTS(api_key="sk-wfmtuoioaovnoiyvegmvxqacjfxtrbdhnxdejkxoiipfhvef")  # 替换成您的 API key
dialogue_tts = DialogueTTS(tts)  # 初始化对谈模式处理器

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
        speed = float(data.get('speed', 1.0))
        gain = float(data.get('gain', 0.0))
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
                speed=speed,
                gain=gain,
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

if __name__ == '__main__':
    app.run(debug=True, port=5000) 