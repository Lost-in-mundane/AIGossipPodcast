import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer, ResultCallback, AudioFormat
from pathlib import Path
import tempfile
import io
from typing import Literal, Union, Dict
from pydub import AudioSegment

class AliyunCosyVoiceTTS:
    """阿里云 CosyVoice TTS API 封装类"""
    
    def __init__(self, api_key: str):
        """
        初始化 TTS 客户端
        
        Args:
            api_key: 阿里云API密钥
        """
        dashscope.api_key = api_key
        
        # 阿里云音色列表
        self.preset_voices = {
            "male": {
                "longcheng_v2": "中文，阳光男声",
                "longwan_v2": "中文，稳重男声",
                "longshu_v2": "中文，书籍朗读男声"
            },
            "female": {
                "longhua_v2": "中文，清新女声",
                "loongbella_v2": "中文，欢快女声",
                "longxiaochun_v2": "中文+英文，沉稳男声",
                "longxiaoxia_v2": "中文，温柔女声"
            }
        }
        
        # 默认参数
        self.model = "cosyvoice-v2"  # 使用2.0版本以获得更好的语气词处理
        
    def _get_audio_format(self, format_str: str) -> AudioFormat:
        """将格式字符串转换为AudioFormat枚举值"""
        format_map = {
            # WAV格式，选择22.05kHz采样率作为默认WAV格式
            "wav": AudioFormat.WAV_22050HZ_MONO_16BIT,
            
            # MP3格式，选择22.05kHz采样率、256kbps作为默认MP3格式
            "mp3": AudioFormat.MP3_22050HZ_MONO_256KBPS,
            
            # PCM格式，选择22.05kHz采样率作为默认PCM格式
            "pcm": AudioFormat.PCM_22050HZ_MONO_16BIT
        }
        return format_map.get(format_str, AudioFormat.WAV_22050HZ_MONO_16BIT)  # 默认使用22.05kHz WAV格式
        
    def text_to_speech(
        self,
        text: str,
        output_path: Union[str, Path],
        voice_name: str = "longxiaochun_v2",
        model: str = None,  # 此参数与SiliconFlowTTS兼容，但在阿里云中不同含义
        response_format: Literal["mp3", "wav", "pcm"] = "wav",  # 移除不支持的opus格式
        speed: float = 1.0,  # 为了保持接口兼容性，参数名仍使用speed
        gain: float = 0.0,  # 为了保持接口兼容性，参数名仍使用gain
        stream: bool = False
    ) -> tuple[bool, str]:
        """
        将文本转换为语音

        Args:
            text: 要转换的文本内容
            output_path: 输出音频文件路径
            voice_name: 音色名称，直接使用阿里云音色
            model: 兼容参数，在阿里云中忽略
            response_format: 输出音频格式，支持mp3、wav等格式
            speed: 语速，范围 [0.5, 2.0]，默认 1.0
            gain: 音量增益，转换为volume参数 [0-100]
            stream: 是否使用流式传输，此参数在阿里云中不适用

        Returns:
            tuple: (成功状态, 实际格式)
                - 第一个元素是bool类型，表示转换是否成功
                - 第二个元素是str类型，表示实际的音频格式（'mp3'或'wav'等）
        """
        try:
            # 参数验证和调整
            if not (0.5 <= speed <= 2.0):
                speed = max(0.5, min(speed, 2.0))  # 限制在阿里云支持范围内
            
            # 将gain转换为volume (0-100)
            volume = int(min(max((gain + 1.0) * 50, 0), 100))
            
            # 获取正确的音频格式
            audio_format = self._get_audio_format(response_format)
                
            # 实例化合成器
            synthesizer = SpeechSynthesizer(
                model=self.model, 
                voice=voice_name,
                format=audio_format,  # 使用AudioFormat枚举值
                speech_rate=speed,        # 语速参数
                volume=volume     # 音量参
            )
            
            # 调用同步API
            audio_data = synthesizer.call(text)
            
            # 写入文件
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            return True, response_format
            
        except Exception as e:
            print(f"Error occurred during Aliyun API call: {e}")
            return False, ""
    
    def list_preset_voices(self) -> Dict:
        """列出所有系统预置音色"""
        return self.preset_voices

    def get_voices_for_ui(self) -> Dict:
        """获取用于UI展示的音色列表"""
        voices = []
        
        # 合并男声和女声列表
        for gender, voice_dict in self.preset_voices.items():
            for voice_id, description in voice_dict.items():
                voices.append({
                    "id": voice_id,
                    "name": f"{voice_id} ({description})"
                })
        
        return voices 