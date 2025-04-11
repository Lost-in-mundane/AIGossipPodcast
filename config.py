# API配置类
class Config:
    # OpenAI API配置
    OPENAI_API_KEY = "sk-JaXkIreIGs3Ci3F3JZkgojqGcKT14JwbwhFA9OsLHE0iEAEd"  # 默认API密钥
    OPENAI_BASE_URL = "https://chat.cloudapi.vip/v1"  # 默认base URL
    OPENAI_MODEL = "claude-3-7-sonnet-20250219"  # 默认模型名称

    # API密钥配置
    API_KEYS = {
        "elevenlabs": "",
        "minimax_group_id": "",
        "minimax_api_key": "",
        "aliyun_access_key_id": "",
        "aliyun_access_key_secret": "",
        "siliconflow_api_key": "",
        "openai": OPENAI_API_KEY,
        "openai_base_url": OPENAI_BASE_URL,
        "openai_model": OPENAI_MODEL
    }

    # 默认TTS引擎
    DEFAULT_TTS_ENGINE = "siliconflow"

    # 默认音色配置
    DEFAULT_VOICES = {
        "basic": "anna",  # 基础模式默认音色
        "dialogue_host": "charles",  # 对话主持人默认音色
        "dialogue_guest": "bella"  # 对话嘉宾默认音色
    }

    # ElevenLabs特定参数
    ELEVENLABS_SETTINGS = {
        "stability": 0.75,
        "similarity_boost": 0.75,
        "speed": 1.0
    }

    @classmethod
    def load_from_json(cls, config_data):
        """从JSON数据加载配置"""
        if not config_data:
            return

        # 更新API密钥
        if "API_KEYS" in config_data:
            cls.API_KEYS.update(config_data["API_KEYS"])
            # 同步更新OpenAI配置
            cls.OPENAI_API_KEY = cls.API_KEYS.get("openai", cls.OPENAI_API_KEY)
            cls.OPENAI_BASE_URL = cls.API_KEYS.get("openai_base_url", cls.OPENAI_BASE_URL)
            cls.OPENAI_MODEL = cls.API_KEYS.get("openai_model", cls.OPENAI_MODEL)

        # 更新其他配置
        if "DEFAULT_TTS_ENGINE" in config_data:
            cls.DEFAULT_TTS_ENGINE = config_data["DEFAULT_TTS_ENGINE"]
        
        if "DEFAULT_VOICES" in config_data:
            cls.DEFAULT_VOICES.update(config_data["DEFAULT_VOICES"])
        
        if "ELEVENLABS_SETTINGS" in config_data:
            cls.ELEVENLABS_SETTINGS.update(config_data["ELEVENLABS_SETTINGS"])

    @classmethod
    def get_settings(cls):
        """获取当前配置"""
        # 检查各API密钥是否已设置
        api_keys_set = {
            "elevenlabs": bool(cls.API_KEYS["elevenlabs"]),
            "minimax_group_id": bool(cls.API_KEYS["minimax_group_id"]),
            "minimax_api_key": bool(cls.API_KEYS["minimax_api_key"]),
            "aliyun_access_key_id": bool(cls.API_KEYS["aliyun_access_key_id"]),
            "aliyun_access_key_secret": bool(cls.API_KEYS["aliyun_access_key_secret"]),
            "siliconflow_api_key": bool(cls.API_KEYS["siliconflow_api_key"]),
            "openai": bool(cls.API_KEYS["openai"]),
            "openai_base_url": bool(cls.API_KEYS["openai_base_url"]),
            "openai_model": bool(cls.API_KEYS["openai_model"])
        }

        return {
            "api_keys_set": api_keys_set,
            "default_tts_engine": cls.DEFAULT_TTS_ENGINE,
            "default_voices": cls.DEFAULT_VOICES,
            "elevenlabs_settings": cls.ELEVENLABS_SETTINGS
        }

# 创建全局配置实例
config = Config()

# TTS API配置
TTS_API_KEY = "sk-wfmtuoioaovnoiyvegmvxqacjfxtrbdhnxdejkxoiipfhvef"

# 阿里云CosyVoice配置
ALIYUN_API_KEY = "sk-875aca9095064850a0e2c84d3cc6f5b1"  # 替换为您的阿里云API密钥

# MiniMax配置
MINIMAX_API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLmtbfonrrnlKjmiLdfMjczMTc1NTczMjQwNzAwOTI5IiwiVXNlck5hbWUiOiLmtbfonrrnlKjmiLdfMjczMTc1NTczMjQwNzAwOTI5IiwiQWNjb3VudCI6IiIsIlN1YmplY3RJRCI6IjE4OTAwODMyMDU3MjIxNDg5MDQiLCJQaG9uZSI6IjE5ODAwMzIzNTUwIiwiR3JvdXBJRCI6IjE4OTAwODMyMDU3MTM3NjAyOTYiLCJQYWdlTmFtZSI6IiIsIk1haWwiOiIiLCJDcmVhdGVUaW1lIjoiMjAyNS0wNC0wOCAxNDo0NToyOSIsIlRva2VuVHlwZSI6MSwiaXNzIjoibWluaW1heCJ9.Yt6j5JNvqHXzr80keXVjvU0wgQwqqWyrNnb9CTWeQlUKaeb96xqmy2w-OZEm7n4fNBsvUGX5amNCD75bGl9qJfI01khWEjAzkarSwJ6M_1gUIZOnQRp2nas_pIbmqxmScH8Kp47VVHf4Yadc7O53SUyeYYWZncXX3eJuv8GNcb9DsonZEYttvZPHj6oCibinr3W63hD__tWF9-9bK3uk5TRjoytnHwRWj0uFeHwqEoMfF1FOPlmFrA_tUi7_vBiZ1upbhoTOJ_VL4DF-B2Hv_YMF8It2hPkbB58xn4oGNuNof1tbUXrkCU_Q90PbMtksuDcv4cYoG7vdTqqqtTZ01A"  # 替换为您的MiniMax API密钥
MINIMAX_GROUP_ID = "1890083205713760296"  # 替换为您的MiniMax Group ID
MINIMAX_DEFAULT_MODEL = "speech-02-turbo-preview"  # 默认使用高清音色

# ElevenLabs配置
ELEVENLABS_API_KEY = ""  # ElevenLabs API Key
# ElevenLabs 配置
ELEVENLABS_DEFAULT_MODEL = "eleven_multilingual_v2"  # 默认模型
ELEVENLABS_DEFAULT_VOICE = "21m00Tcm4TlvDq8ikWAM"  # 默认音色 (Rachel)
# 默认 TTS 引擎
DEFAULT_TTS_ENGINE = "siliconflow"  # 可选: "siliconflow", "aliyun", "minimax", "elevenlabs"

# 翻译专用配置
TRANSLATION_OPENAI_API_KEY = "sk-JaXkIreIGs3Ci3F3JZkgojqGcKT14JwbwhFA9OsLHE0iEAEd"  
TRANSLATION_OPENAI_BASE_URL = "https://chat.cloudapi.vip/v1" 
TRANSLATION_OPENAI_MODEL = "claude-3-7-sonnet-20250219"