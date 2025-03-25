import re
import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from pydub import AudioSegment
from tts_api import SiliconFlowTTS

class DialogueTTS:
    """对谈模式TTS处理类"""
    
    def __init__(self, tts_client: SiliconFlowTTS):
        """
        初始化对谈模式TTS处理器
        
        Args:
            tts_client: SiliconFlowTTS客户端实例
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
        speed: float = 1.0,
        gain: float = 0.0,
        silence_duration: int = 500  # 静音时长(毫秒)
    ) -> bool:
        """
        生成对谈音频
        
        Args:
            dialogue_text: 带有角色标记的对谈文本
            output_path: 输出音频文件路径
            host_voice: 主持人音色
            guest_voice: 嘉宾音色
            model: 使用的TTS模型
            response_format: 输出音频格式
            speed: 语速
            gain: 音量增益
            silence_duration: 对话之间的静音时长(毫秒)
            
        Returns:
            bool: 是否成功生成音频
        """
        try:
            # 解析对话文本
            parsed_dialogue = self._parse_dialogue(dialogue_text)
            if not parsed_dialogue:
                raise ValueError("无法解析对话文本，请检查格式是否正确")
                
            # 按角色分组文本
            host_lines, guest_lines, dialogue_order = self._group_by_speaker(parsed_dialogue)
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 生成主持人音频
                host_audio_path = os.path.join(temp_dir, "host.wav")
                host_text = "。".join(host_lines)
                if host_text:
                    success = self.tts.text_to_speech(
                        text=host_text,
                        output_path=host_audio_path,
                        voice_name=host_voice,
                        model=model,
                        response_format=response_format,
                        speed=speed,
                        gain=gain
                    )
                    if not success:
                        raise Exception("生成主持人音频失败")
                
                # 生成嘉宾音频
                guest_audio_path = os.path.join(temp_dir, "guest.wav")
                guest_text = "。".join(guest_lines)
                if guest_text:
                    success = self.tts.text_to_speech(
                        text=guest_text,
                        output_path=guest_audio_path,
                        voice_name=guest_voice,
                        model=model,
                        response_format=response_format,
                        speed=speed,
                        gain=gain
                    )
                    if not success:
                        raise Exception("生成嘉宾音频失败")
                
                # 根据音频长度估算每句话的时长
                host_audio = AudioSegment.from_wav(host_audio_path) if host_lines else None
                guest_audio = AudioSegment.from_wav(guest_audio_path) if guest_lines else None
                
                # 创建静音片段
                silence = AudioSegment.silent(duration=silence_duration)
                
                # 切分并拼接音频
                final_audio = self._assemble_dialogue_audio(
                    host_audio=host_audio,
                    guest_audio=guest_audio,
                    host_lines=host_lines,
                    guest_lines=guest_lines,
                    dialogue_order=dialogue_order,
                    silence=silence
                )
                
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
    
    def _assemble_dialogue_audio(
        self,
        host_audio: Optional[AudioSegment],
        guest_audio: Optional[AudioSegment],
        host_lines: List[str],
        guest_lines: List[str],
        dialogue_order: List[Tuple[str, int]],
        silence: AudioSegment
    ) -> AudioSegment:
        """
        组装对话音频
        
        Args:
            host_audio: 主持人完整音频
            guest_audio: 嘉宾完整音频
            host_lines: 主持人台词列表
            guest_lines: 嘉宾台词列表
            dialogue_order: 原始对话顺序
            silence: 静音片段
            
        Returns:
            AudioSegment: 最终组装的音频
        """
        # 空音频片段作为起点
        final_audio = AudioSegment.empty()
        
        # 如果任一角色没有台词，直接返回另一角色的音频
        if not host_lines and guest_audio:
            return guest_audio
        if not guest_lines and host_audio:
            return host_audio
            
        # 计算每句话的近似时长
        host_char_count = [len(line) for line in host_lines]
        guest_char_count = [len(line) for line in guest_lines]
        
        host_total_chars = sum(host_char_count) if host_char_count else 0
        guest_total_chars = sum(guest_char_count) if guest_char_count else 0
        
        host_duration = len(host_audio) if host_audio else 0
        guest_duration = len(guest_audio) if guest_audio else 0
        
        # 计算每句话的起始位置（基于字符数比例）
        host_positions = [0]
        for i in range(1, len(host_lines)):
            ratio = sum(host_char_count[:i]) / host_total_chars if host_total_chars > 0 else 0
            host_positions.append(int(ratio * host_duration))
        host_positions.append(host_duration)
        
        guest_positions = [0]
        for i in range(1, len(guest_lines)):
            ratio = sum(guest_char_count[:i]) / guest_total_chars if guest_total_chars > 0 else 0
            guest_positions.append(int(ratio * guest_duration))
        guest_positions.append(guest_duration)
        
        # 按原始顺序拼接
        for speaker, index in dialogue_order:
            if speaker == "主持人" and host_audio:
                start = host_positions[index]
                end = host_positions[index + 1]
                final_audio += host_audio[start:end] + silence
            elif speaker == "嘉宾" and guest_audio:
                start = guest_positions[index]
                end = guest_positions[index + 1]
                final_audio += guest_audio[start:end] + silence
                
        return final_audio 