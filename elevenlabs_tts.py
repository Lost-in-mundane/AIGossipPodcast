import requests
from pathlib import Path
from typing import Literal, Union, Dict, List, Tuple
import tempfile
import os
from pydub import AudioSegment
from config_manager import config_manager

class ElevenLabsTTS:
    """ElevenLabs TTS API 封装类"""
    
    def __init__(self, api_key: str):
        """初始化 ElevenLabs TTS 客户端"""
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # --- 新增：加载默认模型 ID --- 
        config = config_manager.get_config()
        self.default_model_id = config.MODELS.elevenlabs_default_model
        # --- 新增结束 ---
        
        # 预置音色列表
        self.preset_voices = [
            {'id': 'UgBBYS2sOqTuMpoF3BR0', 'name': 'Mark - 自然对话'},
            {'id': '21m00Tcm4TlvDq8ikWAM', 'name': 'Rachel - 平静叙述'},
            {'id': '29vD33N1CtxCmqQRPOHJ', 'name': 'Drew - 新闻播报'},
            {'id': '2EiwWnXFnvU5JabPnv8n', 'name': 'Clyde - 战争老兵'},
            {'id': '5Q0t7uMcjvnagumLfvZi', 'name': 'Paul - 权威播报'},
            {'id': '9BWtsMINqrJLrRacOk9x', 'name': 'Aria - 表现力强'},
            {'id': 'AZnzlk1XvdvUeBnXmlld', 'name': 'Domi - 有力叙述'},
            {'id': 'CYw3kZ02Hs0563khs1Fj', 'name': 'Dave - 英式对话'},
            {'id': 'CwhRBWXzGAHq8TQ4Fs17', 'name': 'Roger - 自信社交'},
            {'id': 'D38z5RcWu1voky8WS1ja', 'name': 'Fin - 爱尔兰水手'}
        ]

    def _map_format(self, format_str: str) -> str:
        """将通用格式映射到 ElevenLabs 支持的格式 - 始终请求 MP3"""
        # 忽略 format_str，总是请求 MP3，后续再转换
        return "mp3_44100_128"

    def text_to_speech(
        self,
        text: str,
        output_path: Union[str, Path],
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        model_id: str = None,
        response_format: Literal["mp3", "wav", "pcm"] = "mp3",
        stability: float = 0.75,
        similarity_boost: float = 0.75,
        speed: float = 1.0,
        stream: bool = False
    ) -> Tuple[bool, str]:
        """
        将文本转换为语音
        (修改：增加 model_id 验证和回退逻辑)
        """
        try:
            stability = max(0.0, min(1.0, stability))
            similarity_boost = max(0.0, min(1.0, similarity_boost))
            speed = max(0.7, min(1.2, speed))
            
            # --- 新增：验证并确定使用的模型 ID --- 
            # 如果传入的 model_id 无效 (None 或空字符串)，则使用类初始化时加载的默认 ID
            effective_model_id = model_id if model_id else self.default_model_id 
            # 可以在此添加更复杂的验证逻辑，例如检查 model_id 是否在已知列表中
            # --- 新增结束 ---
            
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            eleven_api_format = self._map_format("mp3")
            params = {
                "output_format": eleven_api_format
            }
            
            payload = {
                "text": text,
                "model_id": effective_model_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "speed": speed
                }
            }
            
            response = requests.post(
                url,
                json=payload,
                params=params,
                headers=self.headers,
                stream=True
            )

            if response.status_code == 200:
                # --- 修改：先写入临时 MP3，再转换为目标格式 --- 
                temp_mp3_fd, temp_mp3_path = tempfile.mkstemp(suffix=".mp3")
                try:
                    with os.fdopen(temp_mp3_fd, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # 使用 pydub 加载 MP3
                    audio = AudioSegment.from_mp3(temp_mp3_path)
                    
                    # 导出为最终请求的格式 (wav 或 mp3)
                    final_output_format = response_format if response_format in ["wav", "mp3"] else "wav" # 默认转为 wav
                    output_path_obj = Path(output_path)
                    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
                    audio.export(output_path_obj, format=final_output_format)
                    
                    return True, final_output_format # 返回实际输出的格式
                finally:
                    os.remove(temp_mp3_path) # 清理临时文件
                # --- 修改结束 ---
            else:
                print(f"ElevenLabs API Error ({response.status_code}): {response.text}")
                return False, ""

        except Exception as e:
            print(f"Error occurred during ElevenLabs API call: {e}")
            return False, ""

    def list_preset_voices(self) -> List[Dict]:
        """列出预设的常用音色"""
        return self.preset_voices

    def get_voices_for_ui(self) -> List[Dict]:
        """获取用于UI展示的音色列表"""
        return self.list_preset_voices() 