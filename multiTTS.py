import re
import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from pydub import AudioSegment
from tts_api import SiliconFlowTTS
from aliyun_tts import AliyunCosyVoiceTTS

class DialogueTTS:
    """对谈模式TTS处理类"""
    
    def __init__(self, tts_client):
        """
        初始化对谈模式TTS处理器
        
        Args:
            tts_client: TTS客户端实例（SiliconFlowTTS或AliyunCosyVoiceTTS）
        """
        self.tts = tts_client
        
    def generate_dialogue_audio(
        self,
        dialogue_text: str,
        output_path: str,
        host_voice: str = "anna",
        guest_voice: str = "alex",
        model: str = "FunAudioLLM/CosyVoice2-0.5B",
        response_format: str = "wav",
        host_speed: float = 1.0,
        guest_speed: float = 1.0,
        tts_engine: str = "siliconflow",  # 新增引擎类型参数
        silence_duration: int = 500  # 静音时长(毫秒)
    ) -> bool:
        """
        生成对谈音频（逐行生成方式）
        
        Args:
            dialogue_text: 带有角色标记的对谈文本
            output_path: 输出音频文件路径
            host_voice: 主持人音色
            guest_voice: 嘉宾音色
            model: 使用的TTS模型
            response_format: 输出音频格式
            host_speed: 主持人语速
            guest_speed: 嘉宾语速
            tts_engine: TTS引擎类型，"siliconflow"或"aliyun"
            silence_duration: 对话之间的静音时长(毫秒)
            
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
                
                # 判断是否需要进行硅基流动TTS的预处理
                need_preprocess = isinstance(self.tts, SiliconFlowTTS) or tts_engine == "siliconflow"
                
                # 为每句对话单独生成音频
                for i, (role, content) in enumerate(parsed_dialogue):
                    temp_file = os.path.join(temp_dir, f'segment_{i}.wav')
                    voice = host_voice if role == "主持人" else guest_voice
                    speed = host_speed if role == "主持人" else guest_speed
                    
                    # 如果是硅基流动TTS，对内容进行预处理
                    if need_preprocess and isinstance(self.tts, SiliconFlowTTS):
                        content = self.tts._preprocess_text(content)
                    
                    try:
                        success = self.tts.text_to_speech(
                            text=content,
                            output_path=temp_file,
                            voice_name=voice,
                            model=model,
                            response_format=response_format,
                            speed=speed
                        )
                        
                        if success:
                            # 读取生成的音频并添加到列表
                            segment = AudioSegment.from_wav(temp_file)
                            
                            # 可选：音量平衡
                            segment = segment.normalize()
                            
                            audio_segments.append((role, segment))
                        else:
                            print(f"生成音频失败: {role}, {content}")
                            # 使用空音频替代失败片段
                            audio_segments.append((role, AudioSegment.silent(duration=500)))
                            
                    except Exception as e:
                        print(f"处理片段错误: {e}")
                        audio_segments.append((role, AudioSegment.silent(duration=500)))
                
                # 拼接所有音频片段
                if not audio_segments:
                    raise ValueError("没有成功生成任何音频片段")
                    
                final_audio = audio_segments[0][1]
                prev_role = audio_segments[0][0]
                
                for role, segment in audio_segments[1:]:
                    # 根据角色转换动态调整静音时长
                    pause_duration = silence_duration
                    if role != prev_role:  # 角色切换时可以稍长一些
                        pause_duration += 100
                    
                    silence = AudioSegment.silent(duration=pause_duration)
                    final_audio += silence + segment
                    prev_role = role
                    
                # 导出最终音频
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                final_audio.export(output_path, format=response_format)
                
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