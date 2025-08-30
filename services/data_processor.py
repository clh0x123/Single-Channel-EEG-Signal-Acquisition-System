#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据处理模块
负责处理和分析EEG数据
"""

from typing import Dict, Any, List
from collections import deque
import numpy as np
import time
from abc import ABC, abstractmethod


class IDataProcessor(ABC):
    """数据处理器接口"""
    
    @abstractmethod
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理数据
        
        Args:
            data: 输入数据
        
        Returns:
            处理后的数据
        """
        pass
    
    @abstractmethod
    def get_processed_data(self) -> Dict[str, Any]:
        """获取处理后的数据
        
        Returns:
            处理后的数据
        """
        pass
    
    @abstractmethod
    def clear_buffer(self):
        """清空数据缓冲区"""
        pass


class RawEEGProcessor(IDataProcessor):
    """原始EEG数据处理器"""
    
    def __init__(self, max_buffer_size=1000):
        """初始化原始EEG数据处理器
        
        Args:
            max_buffer_size: 最大缓冲区大小
        """
        self.max_buffer_size = max_buffer_size
        self.eeg_buffer = deque(maxlen=max_buffer_size)
        self.timestamp_buffer = deque(maxlen=max_buffer_size)
        
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理原始EEG数据
        
        Args:
            data: 包含'eeg_uv'的原始数据
        
        Returns:
            处理后的数据
        """
        if 'eeg_uv' in data:
            self.eeg_buffer.append(data['eeg_uv'])
            self.timestamp_buffer.append(time.time())
            
            return {
                'type': 'processed_eeg',
                'eeg_uv': data['eeg_uv'],
                'timestamp': time.time()
            }
        return {}
    
    def get_processed_data(self) -> Dict[str, Any]:
        """获取处理后的EEG数据
        
        Returns:
            包含统计信息的处理后数据
        """
        if not self.eeg_buffer:
            return {}
        
        eeg_data = list(self.eeg_buffer)
        
        return {
            'mean': np.mean(eeg_data) if eeg_data else 0,
            'std': np.std(eeg_data) if eeg_data else 0,
            'max': np.max(eeg_data) if eeg_data else 0,
            'min': np.min(eeg_data) if eeg_data else 0,
            'latest': eeg_data[-1] if eeg_data else 0
        }
    
    def clear_buffer(self):
        """清空EEG数据缓冲区"""
        self.eeg_buffer.clear()
        self.timestamp_buffer.clear()


class SignalQualityProcessor(IDataProcessor):
    """信号质量处理器"""
    
    def __init__(self):
        """初始化信号质量处理器"""
        self.latest_signal_quality = 0
        
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理信号质量数据
        
        Args:
            data: 包含'signal_quality'的原始数据
        
        Returns:
            处理后的数据
        """
        if 'signal_quality' in data:
            self.latest_signal_quality = data['signal_quality']
            
            # 评估信号质量
            quality_level = '优秀' if self.latest_signal_quality < 10 else \
                           '良好' if self.latest_signal_quality < 20 else \
                           '一般' if self.latest_signal_quality < 40 else \
                           '较差' if self.latest_signal_quality < 70 else '极差'
            
            return {
                'type': 'signal_quality',
                'signal_quality': self.latest_signal_quality,
                'quality_level': quality_level,
                'timestamp': time.time()
            }
        return {}
    
    def get_processed_data(self) -> Dict[str, Any]:
        """获取处理后的信号质量数据
        
        Returns:
            处理后的信号质量数据
        """
        return {
            'signal_quality': self.latest_signal_quality
        }
    
    def clear_buffer(self):
        """清空信号质量缓冲区"""
        self.latest_signal_quality = 0


class AttentionMeditationProcessor(IDataProcessor):
    """注意力和冥想值处理器"""
    
    def __init__(self):
        """初始化注意力和冥想值处理器"""
        self.latest_attention = 0
        self.latest_meditation = 0
        
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理注意力和冥想值数据
        
        Args:
            data: 包含'attention'或'meditation'的原始数据
        
        Returns:
            处理后的数据
        """
        result = {'timestamp': time.time()}
        
        if 'attention' in data:
            self.latest_attention = data['attention']
            result['attention'] = self.latest_attention
            result['type'] = 'attention'
        
        if 'meditation' in data:
            self.latest_meditation = data['meditation']
            result['meditation'] = self.latest_meditation
            result['type'] = 'meditation' if 'type' not in result else 'both'
        
        return result if 'type' in result else {}
    
    def get_processed_data(self) -> Dict[str, Any]:
        """获取处理后的注意力和冥想值数据
        
        Returns:
            处理后的注意力和冥想值数据
        """
        return {
            'attention': self.latest_attention,
            'meditation': self.latest_meditation
        }
    
    def clear_buffer(self):
        """清空注意力和冥想值缓冲区"""
        self.latest_attention = 0
        self.latest_meditation = 0


class EEGPowerProcessor(IDataProcessor):
    """EEG功率谱处理器"""
    
    def __init__(self):
        """初始化EEG功率谱处理器"""
        self.band_names = ['delta', 'theta', 'low_alpha', 'high_alpha', 
                           'low_beta', 'high_beta', 'low_gamma', 'high_gamma']
        self.latest_power_data = {name: 0 for name in self.band_names}
        
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理EEG功率谱数据
        
        Args:
            data: 包含'eeg_power'的原始数据
        
        Returns:
            处理后的数据
        """
        if 'eeg_power' in data and len(data['eeg_power']) == 8:
            # 更新最新功率数据
            for i, name in enumerate(self.band_names):
                self.latest_power_data[name] = data['eeg_power'][i]
            
            # 计算相对功率
            total_power = sum(self.latest_power_data.values())
            relative_power = {name: value / total_power if total_power > 0 else 0 
                             for name, value in self.latest_power_data.items()}
            
            return {
                'type': 'eeg_power',
                'eeg_power': data['eeg_power'],
                'absolute_power': self.latest_power_data,
                'relative_power': relative_power,
                'timestamp': time.time()
            }
        return {}
    
    def get_processed_data(self) -> Dict[str, Any]:
        """获取处理后的EEG功率谱数据
        
        Returns:
            处理后的EEG功率谱数据
        """
        return self.latest_power_data
    
    def clear_buffer(self):
        """清空EEG功率谱缓冲区"""
        self.latest_power_data = {name: 0 for name in self.band_names}


class DataProcessorManager:
    """数据处理器管理器
    管理多个数据处理器，根据数据类型分发数据
    """
    
    def __init__(self):
        """初始化数据处理器管理器"""
        self.processors = {
            'raw_eeg': RawEEGProcessor(),
            'signal_quality': SignalQualityProcessor(),
            'attention': AttentionMeditationProcessor(),
            'meditation': AttentionMeditationProcessor(),
            'eeg_power': EEGPowerProcessor()
        }
    
    def process_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理数据
        
        Args:
            data: 输入数据
        
        Returns:
            处理后的数据列表
        """
        results = []
        
        if 'type' in data and data['type'] in self.processors:
            processor = self.processors[data['type']]
            result = processor.process_data(data)
            if result:
                results.append(result)
        
        return results
    
    def get_all_processed_data(self) -> Dict[str, Any]:
        """获取所有处理后的数据
        
        Returns:
            所有处理后的数据
        """
        all_data = {}
        
        for processor_type, processor in self.processors.items():
            all_data[processor_type] = processor.get_processed_data()
        
        return all_data
    
    def clear_all_buffers(self):
        """清空所有处理器的缓冲区"""
        for processor in self.processors.values():
            processor.clear_buffer()


# 简单的测试函数
if __name__ == "__main__":
    manager = DataProcessorManager()
    
    # 测试数据处理
    test_data = {
        'type': 'raw_eeg',
        'eeg_uv': 50.5
    }
    
    processed_data = manager.process_data(test_data)
    print(f"处理后的数据: {processed_data}")
    
    all_data = manager.get_all_processed_data()
    print(f"所有处理后的数据: {all_data}")