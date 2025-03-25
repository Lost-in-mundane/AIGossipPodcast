import requests
from pathlib import Path
import base64
from typing import Literal, Optional, Union
import os

class SiliconFlowTTS:
    """硅基流动 TTS API 封装类"""
    
    def __init__(self, api_key: str):
        """
        初始化 TTS 客户端
        
        Args:
            api_key: 从 https://cloud.siliconflow.cn/account/ak 获取的 API 密钥
        """
        self.base_url = "https://api.siliconflow.cn/v1/audio/speech"
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 系统预置音色列表
        self.preset_voices = {
            "male": {
                "alex": "沉稳男声",
                "benjamin": "低沉男声",
                "charles": "磁性男声",
                "david": "欢快男声"
            },
            "female": {
                "anna": "沉稳女声",
                "bella": "激情女声",
                "claire": "温柔女声",
                "diana": "欢快女声"
            }
        }
    
    def text_to_speech(
        self,
        text: str,
        output_path: Union[str, Path],
        voice_name: str = "anna",
        model: str = "FunAudioLLM/CosyVoice2-0.5B",
        response_format: Literal["mp3", "wav", "pcm", "opus"] = "wav",
        speed: float = 1.0,
        gain: float = 0.0,
        stream: bool = False
    ) -> bool:
        """
        将文本转换为语音

        Args:
            text: 要转换的文本内容
            output_path: 输出音频文件路径
            voice_name: 音色名称，默认使用 anna（沉稳女声）
            model: 使用的模型，默认使用 CosyVoice2-0.5B
            response_format: 输出音频格式，支持 mp3、wav、pcm、opus
            speed: 语速，范围 [0.25, 4.0]，默认 1.0
            gain: 音量增益(dB)，范围 [-10, 10]，默认 0.0
            stream: 是否使用流式传输，默认 False

        Returns:
            bool: 转换是否成功
        """
        # 参数验证
        if not (0.25 <= speed <= 4.0):
            raise ValueError("speed must be between 0.25 and 4.0")
        if not (-10 <= gain <= 10):
            raise ValueError("gain must be between -10 and 10")
            
        # 构建完整的语音名称
        full_voice_name = f"{model}:{voice_name}"
        
        # 构建请求参数
        payload = {
            "model": model,
            "voice": full_voice_name,
            "input": text,
            "response_format": response_format,
            "stream": stream,
            "speed": speed,
            "gain": gain
        }

        try:
            # 发送请求
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                stream=stream
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 将响应内容写入文件
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if stream:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            else:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                    
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during API call: {e}")
            if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'text'):
                print(f"API response: {e.response.text}")
            return False
            
    def list_preset_voices(self):
        """列出所有系统预置音色"""
        return self.preset_voices

