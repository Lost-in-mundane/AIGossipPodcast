from typing import Union, List, Dict
from tts_api import SiliconFlowTTS
from aliyun_tts import AliyunCosyVoiceTTS
from minimax_tts import MiniMaxTTS
from config import TTS_API_KEY, ALIYUN_API_KEY, MINIMAX_API_KEY, MINIMAX_GROUP_ID, DEFAULT_TTS_ENGINE

class TTSFactory:
    """TTS工厂类，负责创建不同的TTS客户端实例"""
    
    @staticmethod
    def create_tts(engine: str = None) -> Union[SiliconFlowTTS, AliyunCosyVoiceTTS, MiniMaxTTS]:
        """
        创建TTS客户端实例
        
        Args:
            engine: TTS引擎类型，可选值: "siliconflow", "aliyun", "minimax"。默认使用配置中设置的引擎。
            
        Returns:
            TTS客户端实例，兼容相同的接口
        """
        # 如果未指定引擎，使用默认引擎
        engine = engine or DEFAULT_TTS_ENGINE
        
        if engine == "aliyun":
            return AliyunCosyVoiceTTS(api_key=ALIYUN_API_KEY)
        elif engine == "minimax":
            return MiniMaxTTS(api_key=MINIMAX_API_KEY)
        else:  # 默认使用硅基流动
            return SiliconFlowTTS(api_key=TTS_API_KEY)
            
    @staticmethod
    def get_voices_for_ui(engine: str) -> List[Dict]:
        """
        获取指定引擎的音色列表，用于UI显示
        
        Args:
            engine: TTS引擎类型，"siliconflow", "aliyun" 或 "minimax"
            
        Returns:
            音色列表，包含id和name
        """
        tts = TTSFactory.create_tts(engine)
        return tts.get_voices_for_ui() 