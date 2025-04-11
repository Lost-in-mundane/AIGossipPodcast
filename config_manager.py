from pydantic import BaseModel, Field
from typing import Optional, Dict
import json
import os
from pathlib import Path

# 获取配置文件的绝对路径
CONFIG_FILE = Path(__file__).parent / 'config.json'
print(f"配置文件路径: {CONFIG_FILE}")
print(f"配置文件是否存在: {CONFIG_FILE.exists()}")

# Pydantic 模型定义
class ApiKeysModel(BaseModel):
    # TTS相关API密钥
    elevenlabs: str = ""
    minimax_group_id: str = "1890083205713760296"
    minimax_api_key: str = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLmtbfonrrnlKjmiLdfMjczMTc1NTczMjQwNzAwOTI5IiwiVXNlck5hbWUiOiLmtbfonrrnlKjmiLdfMjczMTc1NTczMjQwNzAwOTI5IiwiQWNjb3VudCI6IiIsIlN1YmplY3RJRCI6IjE4OTAwODMyMDU3MjIxNDg5MDQiLCJQaG9uZSI6IjE5ODAwMzIzNTUwIiwiR3JvdXBJRCI6IjE4OTAwODMyMDU3MTM3NjAyOTYiLCJQYWdlTmFtZSI6IiIsIk1haWwiOiIiLCJDcmVhdGVUaW1lIjoiMjAyNS0wNC0wOCAxNDo0NToyOSIsIlRva2VuVHlwZSI6MSwiaXNzIjoibWluaW1heCJ9.Yt6j5JNvqHXzr80keXVjvU0wgQwqqWyrNnb9CTWeQlUKaeb96xqmy2w-OZEm7n4fNBsvUGX5amNCD75bGl9qJfI01khWEjAzkarSwJ6M_1gUIZOnQRp2nas_pIbmqxmScH8Kp47VVHf4Yadc7O53SUyeYYWZncXX3eJuv8GNcb9DsonZEYttvZPHj6oCibinr3W63hD__tWF9-9bK3uk5TRjoytnHwRWj0uFeHwqEoMfF1FOPlmFrA_tUi7_vBiZ1upbhoTOJ_VL4DF-B2Hv_YMF8It2hPkbB58xn4oGNuNof1tbUXrkCU_Q90PbMtksuDcv4cYoG7vdTqqqtTZ01A"
    aliyun_access_key_id: str = "sk-875aca9095064850a0e2c84d3cc6f5b1"
    aliyun_access_key_secret: Optional[str] = None
    siliconflow_api_key: str = "sk-wfmtuoioaovnoiyvegmvxqacjfxtrbdhnxdejkxoiipfhvef"
    
    # OpenAI相关配置
    openai: str = "sk-JaXkIreIGs3Ci3F3JZkgojqGcKT14JwbwhFA9OsLHE0iEAEd"
    openai_base_url: str = "https://chat.cloudapi.vip/v1"
    openai_model: str = "claude-3-7-sonnet-20250219"
    
    # 翻译专用配置
    translation_openai_api_key: str = "sk-JaXkIreIGs3Ci3F3JZkgojqGcKT14JwbwhFA9OsLHE0iEAEd"
    translation_openai_base_url: str = "https://chat.cloudapi.vip/v1"
    translation_openai_model: str = "claude-3-7-sonnet-20250219"

class ElevenLabsSettingsModel(BaseModel):
    stability: float = Field(0.75, ge=0, le=1)
    similarity_boost: float = Field(0.75, ge=0, le=1)
    speed: float = Field(1.0, ge=0.7, le=1.2)

class DefaultVoicesModel(BaseModel):
    basic: str = "anna"
    dialogue_host: str = "anna"
    dialogue_guest: str = "alex"

class ModelsConfigModel(BaseModel):
    minimax_default_model: str = "speech-02-turbo-preview"
    elevenlabs_default_model: str = "eleven_multilingual_v2"
    elevenlabs_default_voice: str = "21m00Tcm4TlvDq8ikWAM"

class AppConfig(BaseModel):
    API_KEYS: ApiKeysModel = ApiKeysModel()
    DEFAULT_TTS_ENGINE: str = "siliconflow"  # 可选: "siliconflow", "aliyun", "minimax", "elevenlabs"
    DEFAULT_VOICES: DefaultVoicesModel = DefaultVoicesModel()
    ELEVENLABS_SETTINGS: ElevenLabsSettingsModel = ElevenLabsSettingsModel()
    MODELS: ModelsConfigModel = ModelsConfigModel()

class SettingsResponse(BaseModel):
    api_keys_set: Dict[str, bool] = {}
    default_tts_engine: str = "siliconflow"
    default_voices: DefaultVoicesModel = DefaultVoicesModel()
    elevenlabs_settings: ElevenLabsSettingsModel = ElevenLabsSettingsModel()
    models: ModelsConfigModel = ModelsConfigModel()

class ConfigManager:
    _instance = None
    _config: AppConfig = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """从文件加载配置"""
        try:
            if CONFIG_FILE.exists():
                print("正在加载配置文件...")
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    print(f"配置数据: {json.dumps(config_data, indent=2)}")
                    self._config = AppConfig(**config_data)
                print("配置加载完成")
            else:
                print("配置文件不存在，使用默认配置")
                self._config = AppConfig()
                self.save_config()
        except Exception as e:
            print(f"加载配置出错: {e}，使用默认配置")
            self._config = AppConfig()
            self.save_config()

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config.dict(exclude_unset=False), f, indent=4, ensure_ascii=False)
            print("配置已保存")
        except Exception as e:
            print(f"保存配置出错: {e}")
            raise

    def get_config(self) -> AppConfig:
        """获取当前配置"""
        return self._config

    def update_config(self, new_config: AppConfig):
        """更新配置"""
        self._config = new_config
        self.save_config()

    def get_settings_response(self) -> SettingsResponse:
        """获取用于前端显示的设置响应（不包含敏感信息）"""
        api_keys = self._config.API_KEYS.dict()
        api_keys_set = {key: bool(value) for key, value in api_keys.items()}
        
        return SettingsResponse(
            api_keys_set=api_keys_set,
            default_tts_engine=self._config.DEFAULT_TTS_ENGINE,
            default_voices=self._config.DEFAULT_VOICES,
            elevenlabs_settings=self._config.ELEVENLABS_SETTINGS,
            models=self._config.MODELS
        )

# 创建全局配置管理器实例
config_manager = ConfigManager() 