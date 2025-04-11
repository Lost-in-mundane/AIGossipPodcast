from typing import Union, List, Dict, Optional
from tts_api import SiliconFlowTTS
from aliyun_tts import AliyunCosyVoiceTTS
from minimax_tts import MiniMaxTTS
from elevenlabs_tts import ElevenLabsTTS
from config_manager import config_manager  # 使用新的配置管理器

class TTSFactory:
    """TTS工厂类，负责创建不同的TTS客户端实例"""
    
    @staticmethod
    def create_tts(engine: Optional[str] = None) -> Union[SiliconFlowTTS, AliyunCosyVoiceTTS, MiniMaxTTS, ElevenLabsTTS]:
        """
        创建TTS客户端实例
        
        Args:
            engine: TTS引擎名称，如果不指定则使用默认引擎
            
        Returns:
            TTS客户端实例
        """
        config = config_manager.get_config()
        engine = engine or config.DEFAULT_TTS_ENGINE
        api_keys = config.API_KEYS # 获取 API Keys 配置
        
        if engine == "minimax":
            # MiniMaxTTS 内部会自行读取配置，无需传递参数
            return MiniMaxTTS()
        elif engine == "aliyun":
            # TODO: 实现阿里云TTS客户端
            raise NotImplementedError("阿里云TTS暂未实现")
        elif engine == "elevenlabs":
            # 传递 ElevenLabs API Key (配置正确)
            return ElevenLabsTTS(api_key=api_keys.elevenlabs)
        elif engine == "siliconflow":
            # 传递 SiliconFlow API Key (已修正)
            return SiliconFlowTTS(api_key=api_keys.siliconflow_api_key)
        else:
            raise ValueError(f"不支持的TTS引擎: {engine}")
            
    @staticmethod
    def get_voices_for_ui(engine: str) -> List[Dict]:
        """
        获取指定引擎的音色列表，用于UI显示
        
        Args:
            engine: TTS引擎类型，"siliconflow", "aliyun", "minimax" 或 "elevenlabs"
            
        Returns:
            音色列表，包含id和name
        """
        # 这里创建实例时也需要传递 API Key，否则 get_voices_for_ui 内部可能失败
        tts = TTSFactory.create_tts(engine)
        return tts.get_voices_for_ui() 