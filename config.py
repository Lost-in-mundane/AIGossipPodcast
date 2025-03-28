import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# OpenAI API配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-JaXkIreIGs3Ci3F3JZkgojqGcKT14JwbwhFA9OsLHE0iEAEd")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://chat.cloudapi.vip/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "claude-3-7-sonnet-20250219-s")

# TTS API配置
TTS_API_KEY = os.getenv("TTS_API_KEY", "sk-wfmtuoioaovnoiyvegmvxqacjfxtrbdhnxdejkxoiipfhvef")

# 阿里云CosyVoice配置
ALIYUN_API_KEY = os.getenv("ALIYUN_API_KEY", "sk-875aca9095064850a0e2c84d3cc6f5b1")
DEFAULT_TTS_ENGINE = os.getenv("DEFAULT_TTS_ENGINE", "siliconflow")

# 如果环境变量不存在，使用默认值，但不提示警告
# 因为我们已经提供了默认值

# 可以在这里添加其他厂商的配置
# 例如：
# AZURE_API_KEY = "your-azure-api-key"
# AZURE_BASE_URL = "https://your-resource.openai.azure.com"
# AZURE_MODEL = "your-deployment-name" 