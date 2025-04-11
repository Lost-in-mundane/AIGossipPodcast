import requests
from pathlib import Path
import json
from typing import Literal, Union, Dict, List, Tuple
import os
import base64
from config_manager import config_manager  # 使用新的配置管理器
import re

class MiniMaxTTS:
    """MiniMax T2A V2 API 封装类"""
    
    def __init__(self):
        """初始化 MiniMax TTS 客户端"""
        config = config_manager.get_config()
        self.group_id = config.API_KEYS.minimax_group_id
        self.api_key = config.API_KEYS.minimax_api_key
        self.default_model = config.MODELS.minimax_default_model
        self.base_url = "https://api.minimax.chat/v1/t2a_v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 系统预置音色列表
        self.preset_voices = {
            "male": {
                "male-qn-qingse": "青涩男声",
                "male-qn-jingying": "精英男声",
                "male-qn-badao": "霸道男声",
                "male-qn-daxuesheng": "大学生男声",
                "audiobook_male_1": "男性有声书1",
                "audiobook_male_2": "男性有声书2",
                "presenter_male": "男性主持人",
                "clever_boy": "聪明男孩",
                "cute_boy": "可爱男孩",
                "junlang_nanyou": "俊朗男友",
                "chunzhen_xuedi": "纯真学弟",
                "lengdan_xiongzhang": "冷淡兄长",
                "badao_shaoye": "霸道少爷",
                "tianxin_xiaoling": "甜心小灵",
                "qiaopi_mengmei": "俏皮萌妹",
                "diadia_xuemei": "嗲嗲学妹",
                "danya_xuejie": "淡雅学姐",
                "Santa_Claus": "圣诞老人",
                "Grinch": "格林奇",
                "Rudolph": "鲁道夫",
                "Arnold": "阿诺德",
                "Charming_Santa": "迷人的圣诞老人",
                "Charming_Lady": "迷人女士",
                "Sweet_Girl": "甜心女孩",
                "Cute_Elf": "可爱精灵",
                "Attractive_Girl": "迷人女孩",
                "Serene_Woman": "恬静女士"
            },
            "female": {
                "female-shaonv": "少女音色",
                "female-yujie": "御姐音色",
                "female-chengshu": "成熟女声",
                "female-tianmei": "甜美女声",
                "audiobook_female_1": "女性有声书1",
                "audiobook_female_2": "女性有声书2",
                "presenter_female": "女性主持人",
                "lovely_girl": "可爱女孩",
                "wumei_yujie": "妩媚御姐"
            }
        }
        
        # 支持的模型列表
        self.supported_models = {
            "speech-02-hd-preview": "全新hd音色",
            "speech-02-turbo-preview": "全新turbo音色",
            "speech-01-turbo": "标准音色（快速）"
        }
    
    def _preprocess_text(self, text: str) -> str:
        """
        对文本进行预处理，删除情感标签，保留说话人标签
        
        Args:
            text: 原始文本
            
        Returns:
            str: 处理后的文本
        """
        # 需要删除的情感标签列表
        emotion_tags = [
            'breath', 'noise', 'laughter', 'cough', 'clucking',
            'accent', 'quick_breath', 'hissing', 'sigh', 'lipsmack', 'mm'
        ]
        
        # 删除HTML风格的标签 (如 <laughter>文本</laughter>)
        text = re.sub(r'<[^>]+>', '', text)
        
        # 删除情感标签 [标签名]
        pattern = '|'.join(map(re.escape, emotion_tags))
        text = re.sub(rf'\[({pattern})\]', '', text)
        
        # 删除强调标签 <strong>文本</strong>
        text = re.sub(r'<strong>|</strong>', '', text)
        
        return text
    
    def text_to_speech(
        self,
        text: str,
        output_path: Union[str, Path],
        voice_name: str = "female-chengshu",
        model: str = None,  # 默认使用config中的模型
        response_format: Literal["mp3", "wav", "pcm"] = "mp3",
        speed: float = 1.0,
        gain: float = 0.0,
        stream: bool = False
    ) -> Tuple[bool, str]:
        """
        将文本转换为语音

        Args:
            text: 要转换的文本内容
            output_path: 输出音频文件路径
            voice_name: 音色名称，默认使用 mm_chenyu
            model: 使用的模型，可选 "speech-02-hd-preview"(高清音色) 或 "speech-02-turbo-preview"(高清音色快速) 或 "speech-01-turbo"(标准音色快速)
            response_format: 输出音频格式，MiniMax支持mp3、wav等格式
            speed: 语速，范围 [0.5, 2.0]，默认 1.0
            gain: 音量增益，范围 [0.0, 2.0]，默认 1.0
            stream: 是否使用流式传输，此参数在MiniMax中暂不支持

        Returns:
            tuple: (成功状态, 实际格式)
                - 第一个元素是bool类型，表示转换是否成功
                - 第二个元素是str类型，表示实际的音频格式（'mp3'或'wav'等）
        """
        try:
            # 参数验证和调整
            if not (0.5 <= speed <= 2.0):
                speed = max(0.5, min(speed, 2.0))  # 限制在可接受范围内
            
            # 在MiniMax中gain对应volume参数，转换为可接受的范围
            volume = min(max(gain + 1.0, 0.0), 2.0)
            
            # 确保响应格式是支持的格式
            supported_formats = ["mp3", "wav", "pcm", "flac"]
            if response_format not in supported_formats:
                response_format = "mp3"  # 默认使用mp3
            
            # 确保使用支持的模型
            if model not in self.supported_models:
                model = self.default_model  # 使用默认模型
            
            # 构建请求参数
            payload = {
                "model": model,
                "text": self._preprocess_text(text),
                "stream": False,  # 非流式请求
                "voice_setting": {
                    "voice_id": voice_name,
                    "speed": speed,
                    "vol": volume,
                    "pitch": 0  # 音高，范围[-12, 12]，默认0
                },
                "audio_setting": {
                    "sample_rate": 32000,  # 采样率
                    "bitrate": 128000,     # 比特率
                    "format": response_format,
                    "channel": 1           # 单声道
                }
            }
            
            # 构建完整URL
            url = f"{self.base_url}?GroupId={self.group_id}"
            
            # 发送请求
            response = requests.post(
                url,
                json=payload,
                headers=self.headers
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 检查返回状态
            if result.get('base_resp', {}).get('status_code') != 0:
                error_msg = result.get('base_resp', {}).get('status_msg', '未知错误')
                print(f"API返回错误: {error_msg}")
                return False, ""
            
            # 从响应中提取音频数据
            if "data" in result and "audio" in result["data"]:
                # 将hex编码的音频数据转换为二进制
                audio_data = bytes.fromhex(result["data"]["audio"])
                
                # 写入文件
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(audio_data)
                
                # 获取实际的音频格式
                actual_format = result.get('extra_info', {}).get('audio_format', response_format)
                return True, actual_format
            else:
                print(f"Error: audio data not found in response")
                print(f"Response content: {result}")
                return False, ""
                
        except Exception as e:
            print(f"Error occurred during MiniMax API call: {e}")
            return False, ""
    
    def list_preset_voices(self) -> Dict:
        """列出所有系统预置音色"""
        return self.preset_voices

    def get_voices_for_ui(self) -> List[Dict]:
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