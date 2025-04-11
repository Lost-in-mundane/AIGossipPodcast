import requests
import json
from typing import Optional
from config_manager import config_manager

def list_elevenlabs_voices(api_key: Optional[str] = None) -> list:
    """
    获取 ElevenLabs 的所有可用音色列表
    
    Args:
        api_key: ElevenLabs API密钥，如果不提供则从配置中读取
        
    Returns:
        list: 音色信息列表
    """
    if not api_key:
        config = config_manager.get_config()
        api_key = config.API_KEYS.elevenlabs
        print(f"从配置中读取的API密钥: {api_key[:8]}..." if api_key else "未找到API密钥")
        
    if not api_key:
        raise ValueError("未提供 ElevenLabs API 密钥")

    url = "https://api.elevenlabs.io/v2/voices"
    
    headers = {
        "xi-api-key": api_key,
        "Accept": "application/json"
    }
    
    params = {
        "include_total_count": True
    }
    
    try:
        print("正在发送请求到 ElevenLabs API...")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        voices = data.get("voices", [])
        print(f"成功获取到 {len(voices)} 个音色")
        
        # 格式化输出结果
        formatted_voices = []
        for voice in voices:
            voice_info = {
                "voice_id": voice["voice_id"],
                "name": voice["name"],
                "category": voice.get("category", ""),
                "description": voice.get("description", ""),
                "labels": voice.get("labels", {}),
                "settings": voice.get("settings", {})
            }
            formatted_voices.append(voice_info)
            
        return formatted_voices
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        return []

def print_voice_list(voices: list) -> None:
    """
    格式化打印音色列表
    
    Args:
        voices: 音色信息列表
    """
    print("\n=== ElevenLabs 可用音色列表 ===\n")
    
    for i, voice in enumerate(voices, 1):
        print(f"{i}. {voice['name']}")
        print(f"   ID: {voice['voice_id']}")
        print(f"   分类: {voice['category']}")
        if voice['description']:
            print(f"   描述: {voice['description']}")
        
        if voice['labels']:
            print("   标签:")
            for key, value in voice['labels'].items():
                print(f"      - {key}: {value}")
        
        if voice['settings']:
            print("   默认设置:")
            for key, value in voice['settings'].items():
                print(f"      - {key}: {value}")
        
        print()

def main():
    try:
        voices = list_elevenlabs_voices()
        if voices:
            print_voice_list(voices)
            print(f"总计: {len(voices)} 个音色")
        else:
            print("未找到可用音色")
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 