import os
import requests
import argparse
import base64
from pathlib import Path

def encode_audio_to_base64(audio_file_path):
    """将音频文件转换为base64编码"""
    with open(audio_file_path, 'rb') as audio_file:
        audio_content = audio_file.read()
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        # 获取文件扩展名
        file_ext = Path(audio_file_path).suffix.lstrip('.')
        return f"data:audio/{file_ext};base64,{audio_base64}"

def upload_voice_file(api_key, audio_file_path, custom_name, text_content, model="FunAudioLLM/CosyVoice2-0.5B"):
    """通过文件方式上传音色"""
    url = "https://api.siliconflow.cn/v1/uploads/audio/voice"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"音频文件不存在: {audio_file_path}")
    
    files = {
        "file": open(audio_file_path, "rb")
    }
    
    data = {
        "model": model,
        "customName": custom_name,
        "text": text_content
    }
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()  # 检查响应状态
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"上传失败: {str(e)}")
        return None
    finally:
        files["file"].close()

def upload_voice_base64(api_key, audio_file_path, custom_name, text_content, model="FunAudioLLM/CosyVoice2-0.5B"):
    """通过base64编码方式上传音色"""
    url = "https://api.siliconflow.cn/v1/uploads/audio/voice"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"音频文件不存在: {audio_file_path}")
    
    audio_base64 = encode_audio_to_base64(audio_file_path)
    
    data = {
        "model": model,
        "customName": custom_name,
        "audio": audio_base64,
        "text": text_content
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # 检查响应状态
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"上传失败: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='上传用户音色到SiliconFlow平台')
    parser.add_argument('--api-key', required=True, help='SiliconFlow API密钥')
    parser.add_argument('--audio-file', required=True, help='音频文件路径')
    parser.add_argument('--name', required=True, help='自定义音色名称')
    parser.add_argument('--text', required=True, help='音频对应的文字内容')
    parser.add_argument('--model', default='FunAudioLLM/CosyVoice2-0.5B', help='模型名称')
    parser.add_argument('--method', choices=['file', 'base64'], default='file', help='上传方式：file或base64')
    
    args = parser.parse_args()
    
    if args.method == 'file':
        result = upload_voice_file(args.api_key, args.audio_file, args.name, args.text, args.model)
    else:
        result = upload_voice_base64(args.api_key, args.audio_file, args.name, args.text, args.model)
    
    if result:
        print("上传成功！")
        print(f"音色URI: {result.get('uri')}")
    else:
        print("上传失败！")

if __name__ == "__main__":
    main() 