#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TGAM数据流解析器
用于解析TGAM芯片发送的脑电数据
"""

from typing import List, Dict, Any
import logging


class TGAMDataStreamParser:
    """TGAM数据流解析器
    负责解析TGAM芯片发送的原始数据流，提取各种脑电参数
    """
    
    def __init__(self):
        """初始化解析器"""
        # 解析状态
        self.state = 0  # 0: 寻找包头, 1: 寻找包长度, 2: 接收数据
        self.payload_length = 0
        self.payload_data = []
        self.checksum = 0
        
        # 包头标记
        self.HEADER_BYTE = 0xAA
        
        # 数据类型
        self.RAW_VALUE = 0x80
        self.POOR_SIGNAL = 0x02
        self.ATTENTION = 0x04
        self.MEDITATION = 0x05
        self.BLINK = 0x16
        self.EEG_POWER = 0x83
        
        # 解析结果
        self.parsed_data_list = []
    
    def parse_stream(self, data: bytes) -> List[Dict[str, Any]]:
        """解析数据流
        
        Args:
            data: 原始二进制数据
        
        Returns:
            解析后的数据列表
        """
        self.parsed_data_list = []
        
        for byte in data:
            self._parse_byte(byte)
        
        return self.parsed_data_list
    
    def _parse_byte(self, byte: int):
        """解析单个字节
        
        Args:
            byte: 当前解析的字节
        """
        if self.state == 0:
            # 寻找第一个包头字节
            if byte == self.HEADER_BYTE:
                self.state = 1
        elif self.state == 1:
            # 寻找第二个包头字节
            if byte == self.HEADER_BYTE:
                self.state = 2
            else:
                self.state = 0  # 重置状态
        elif self.state == 2:
            # 接收包长度
            self.payload_length = byte
            self.payload_data = []
            self.checksum = 0
            self.state = 3
        elif self.state == 3:
            # 接收有效载荷数据
            self.payload_data.append(byte)
            self.checksum += byte
            
            if len(self.payload_data) == self.payload_length:
                self.state = 4
        elif self.state == 4:
            # 接收校验和
            calculated_checksum = (~self.checksum) & 0xFF
            
            if byte == calculated_checksum:
                # 校验和正确，解析数据包
                self._parse_payload(self.payload_data)
            else:
                logging.warning(f"校验和错误: 期望 {calculated_checksum}, 实际 {byte}")
            
            self.state = 0  # 重置状态
    
    def _parse_payload(self, payload: List[int]):
        """解析数据包有效载荷
        
        Args:
            payload: 有效载荷数据
        """
        if not payload:
            return
        
        index = 0
        while index < len(payload):
            data_type = payload[index]
            index += 1
            
            if data_type == self.RAW_VALUE and index + 2 <= len(payload):
                # 解析原始脑电值
                raw_value = (payload[index] << 8) | payload[index + 1]
                index += 2
                
                # 转换为有符号整数
                if raw_value > 32767:
                    raw_value -= 65536
                
                # 转换为微伏值 (根据TGAM规格)
                eeg_uv = raw_value * 0.516
                
                self.parsed_data_list.append({
                    'type': 'raw_eeg',
                    'raw_value': raw_value,
                    'eeg_uv': eeg_uv
                })
                
            elif data_type == self.POOR_SIGNAL and index < len(payload):
                # 解析信号质量
                signal_quality = payload[index]
                index += 1
                
                self.parsed_data_list.append({
                    'type': 'signal_quality',
                    'signal_quality': signal_quality
                })
                
            elif data_type == self.ATTENTION and index < len(payload):
                # 解析注意力值
                attention = payload[index]
                index += 1
                
                self.parsed_data_list.append({
                    'type': 'attention',
                    'attention': attention
                })
                
            elif data_type == self.MEDITATION and index < len(payload):
                # 解析冥想值
                meditation = payload[index]
                index += 1
                
                self.parsed_data_list.append({
                    'type': 'meditation',
                    'meditation': meditation
                })
                
            elif data_type == self.BLINK and index < len(payload):
                # 解析眨眼强度
                blink_strength = payload[index]
                index += 1
                
                self.parsed_data_list.append({
                    'type': 'blink',
                    'blink_strength': blink_strength
                })
                
            elif data_type == self.EEG_POWER and index + 25 <= len(payload):
                # 解析EEG功率谱数据
                power_data_length = payload[index]
                index += 1
                
                if power_data_length == 24 and index + 24 <= len(payload):
                    # EEG功率谱包含8个频段，每个频段3字节
                    eeg_power = []
                    for i in range(8):
                        power_value = (payload[index] << 16) | (payload[index + 1] << 8) | payload[index + 2]
                        eeg_power.append(power_value)
                        index += 3
                    
                    self.parsed_data_list.append({
                        'type': 'eeg_power',
                        'eeg_power': eeg_power
                    })
                else:
                    # 数据长度不正确，跳过
                    index += power_data_length
            else:
                # 未知数据类型或数据不完整，跳过
                logging.warning(f"未知数据类型: {data_type} 或数据不完整")
                break
    
    def clear_buffer(self):
        """清空解析缓冲区"""
        self.state = 0
        self.payload_length = 0
        self.payload_data = []
        self.checksum = 0
        self.parsed_data_list = []


# 简单的测试函数
if __name__ == "__main__":
    parser = TGAMDataStreamParser()
    
    # 模拟一个简单的数据包
    test_data = bytes([0xAA, 0xAA, 0x04, 0x80, 0x02, 0x01, 0x02, 0x79])  # 原始数据
    
    parsed_data = parser.parse_stream(test_data)
    print(f"解析结果: {parsed_data}")