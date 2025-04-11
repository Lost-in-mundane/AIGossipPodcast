import re
import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from pydub import AudioSegment
from tts_api import SiliconFlowTTS
from aliyun_tts import AliyunCosyVoiceTTS
from elevenlabs_tts import ElevenLabsTTS

class DialogueTTS:
    """对谈模式TTS处理类"""
    
    def __init__(self, host_tts_client, guest_tts_client):
        """
        初始化对谈模式TTS处理器
        
        Args:
            host_tts_client: 主持人使用的TTS客户端实例
            guest_tts_client: 嘉宾使用的TTS客户端实例
        """
        self.host_tts = host_tts_client
        self.guest_tts = guest_tts_client
        
    def generate_dialogue_audio(
        self,
        dialogue_text: str,
        output_path: str,
        host_voice: str = "anna",
        guest_voice: str = "alex",
        model: str = "FunAudioLLM/CosyVoice2-0.5B",  # Note: This model parameter might become irrelevant or engine-specific
        response_format: str = "wav",
        host_speed: float = 1.0,
        guest_speed: float = 1.0,
        silence_duration: int = 600,  # 静音时长(毫秒)
        host_stability: Optional[float] = None,  # ElevenLabs 参数
        host_similarity_boost: Optional[float] = None,  # ElevenLabs 参数
        guest_stability: Optional[float] = None,  # ElevenLabs 参数
        guest_similarity_boost: Optional[float] = None  # ElevenLabs 参数
    ) -> bool:
        """
        生成对谈音频（逐行生成方式）
        
        Args:
            dialogue_text: 带有角色标记的对谈文本
            output_path: 输出音频文件路径
            host_voice: 主持人音色
            guest_voice: 嘉宾音色
            model: 使用的TTS模型 (可能需要根据引擎调整或忽略)
            response_format: 输出音频格式
            host_speed: 主持人语速
            guest_speed: 嘉宾语速
            silence_duration: 对话之间的静音时长(毫秒)
            host_stability: ElevenLabs 参数
            host_similarity_boost: ElevenLabs 参数
            guest_stability: ElevenLabs 参数
            guest_similarity_boost: ElevenLabs 参数
            
        Returns:
            bool: 是否成功生成音频
        """
        try:
            # 解析对话文本
            parsed_dialogue = self._parse_dialogue(dialogue_text)
            if not parsed_dialogue:
                raise ValueError("无法解析对话文本，请检查格式是否正确")
                
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                audio_segments = []
                prev_role = None
                
                # 为每句对话单独生成音频
                for i, (role, content) in enumerate(parsed_dialogue):
                    temp_file = os.path.join(temp_dir, f'segment_{i}.wav')
                    
                    if role == "主持人":
                        current_tts = self.host_tts
                        voice = host_voice
                        speed = host_speed
                    else: # 嘉宾
                        current_tts = self.guest_tts
                        voice = guest_voice
                        speed = guest_speed
                        
                    # 判断是否需要进行硅基流动TTS的预处理 (根据当前使用的TTS实例)
                    need_preprocess = isinstance(current_tts, SiliconFlowTTS)
                    
                    # 如果是硅基流动TTS，对内容进行预处理
                    if need_preprocess:
                        content = current_tts._preprocess_text(content)
                    
                    # 构建 TTS 参数字典
                    tts_params = {
                        "text": content,
                        "output_path": temp_file,
                        "voice_name": voice,
                        "model": model,
                        "response_format": response_format,
                        "speed": speed
                    }
                    
                    # 添加 ElevenLabs 特定参数
                    if role == "主持人":
                        if host_stability is not None:
                            tts_params["stability"] = host_stability
                        if host_similarity_boost is not None:
                            tts_params["similarity_boost"] = host_similarity_boost
                    else:  # 嘉宾
                        if guest_stability is not None:
                            tts_params["stability"] = guest_stability
                        if guest_similarity_boost is not None:
                            tts_params["similarity_boost"] = guest_similarity_boost
                    
                    try:
                        # --- 修正 ElevenLabs 参数名，并移除不适用的 model 参数 ---
                        if isinstance(current_tts, ElevenLabsTTS):
                            if 'voice_name' in tts_params:
                                tts_params['voice_id'] = tts_params.pop('voice_name')
                            # 如果是 ElevenLabs，移除 model 参数，让 ElevenLabsTTS 内部处理默认值
                            if 'model' in tts_params:
                                tts_params.pop('model') 
                        # --- 修正结束 ---
                        
                        # 使用解包操作符传递参数
                        success = current_tts.text_to_speech(**tts_params)
                        
                        if success:
                            # 读取生成的音频并添加到列表
                            segment = AudioSegment.from_wav(temp_file)
                            segment = segment.normalize() # 音量平衡
                            audio_segments.append((role, segment))
                        else:
                            print(f"生成音频失败: {role}, {content}")
                            audio_segments.append((role, AudioSegment.silent(duration=500)))
                            
                    except Exception as e:
                        print(f"处理片段 '{content}' 时发生错误: {e}")
                        audio_segments.append((role, AudioSegment.silent(duration=500)))
                
                # 拼接所有音频片段
                if not audio_segments:
                    raise ValueError("没有成功生成任何音频片段")
                    
                final_audio = audio_segments[0][1]
                prev_role = audio_segments[0][0]
                
                for role, segment in audio_segments[1:]:
                    pause_duration = silence_duration
                    if role != prev_role:
                        pause_duration += 100
                    
                    silence = AudioSegment.silent(duration=pause_duration)
                    final_audio += silence + segment
                    prev_role = role
                    
                # 导出最终音频
                output_path_obj = Path(output_path) # 使用Path对象
                output_path_obj.parent.mkdir(parents=True, exist_ok=True)
                final_audio.export(output_path_obj, format=response_format)
                
            return True
                
        except Exception as e:
            print(f"生成对谈音频失败: {e}")
            return False
    
    def _parse_dialogue(self, text: str) -> List[Tuple[str, str]]:
        """
        解析对话文本，保留所有特殊标记
        """
        # 使用更精确的正则表达式，只匹配角色标记
        pattern = r'\[(主持人|嘉宾)\]([\s\S]*?)(?=\[主持人\]|\[嘉宾\]|$)'
        matches = re.findall(pattern, text)
        
        dialogue = []
        for role, content in matches:
            # 保留所有特殊标记，只清理首尾空白
            cleaned_content = content.strip()
            if cleaned_content:
                dialogue.append((role, cleaned_content))
        
        return dialogue
    
    def _group_by_speaker(self, dialogue: List[Tuple[str, str]]) -> Tuple[List[str], List[str], List[Tuple[str, int]]]:
        """
        按说话人分组对话
        
        Args:
            dialogue: 解析后的对话列表
            
        Returns:
            Tuple[List[str], List[str], List[Tuple[str, int]]]: 
                主持人台词列表、嘉宾台词列表、原始对话顺序
        """
        host_lines = []
        guest_lines = []
        dialogue_order = []  # 记录原始顺序
        
        for i, (role, content) in enumerate(dialogue):
            if role == "主持人":
                host_lines.append(content)
                dialogue_order.append(("主持人", len(host_lines) - 1))
            else:  # 嘉宾
                guest_lines.append(content)
                dialogue_order.append(("嘉宾", len(guest_lines) - 1))
                
        return host_lines, guest_lines, dialogue_order