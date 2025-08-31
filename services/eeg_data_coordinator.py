"""
EEG数据协调器
负责协调频段处理器和绘图组件之间的数据流
"""
from typing import Dict, Any, List, Optional
from PyQt5.QtCore import QObject, pyqtSignal

from .frequency_band_processor import FrequencyBandProcessor
from .data_processor import DataProcessorManager


class EEGDataCoordinator(QObject):
    """EEG数据协调器"""
    
    # 信号定义
    raw_eeg_updated = pyqtSignal(float)  # 原始EEG数据更新
    frequency_bands_updated = pyqtSignal(dict)  # 频段数据更新
    combined_data_updated = pyqtSignal(dict)  # 组合数据更新
    
    def __init__(self, sample_rate: int = 512, buffer_size: int = 1000):
        super().__init__()
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        
        # 初始化处理器
        self.frequency_band_processor = FrequencyBandProcessor(sample_rate, buffer_size)
        self.data_processor_manager = DataProcessorManager()
        
        # 数据缓存
        self.latest_raw_eeg = 0.0
        self.latest_frequency_bands = {}
        self.latest_attention = 0
        self.latest_meditation = 0
        self.latest_signal_quality = 0
        
    def process_eeg_data(self, eeg_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理EEG数据
        
        Args:
            eeg_data: 原始EEG数据
            
        Returns:
            处理后的数据字典
        """
        result = {
            'timestamp': eeg_data.get('timestamp', 0),
            'type': 'combined_eeg_data'
        }
        
        # 处理原始EEG数据
        if 'eeg_uv' in eeg_data:
            eeg_value = float(eeg_data['eeg_uv'])
            self.latest_raw_eeg = eeg_value
            
            # 发送原始EEG信号
            self.raw_eeg_updated.emit(eeg_value)
            
            # 添加到频段处理器
            self.frequency_band_processor.add_eeg_data(eeg_value)
            
            # 获取频段数据
            frequency_bands = self.frequency_band_processor.get_latest_frequency_band_data()
            self.latest_frequency_bands = frequency_bands
            
            # 发送频段数据
            self.frequency_bands_updated.emit(frequency_bands)
            
            result['raw_eeg'] = eeg_value
            result['frequency_bands'] = frequency_bands
        
        # 处理其他类型的数据
        if 'attention' in eeg_data:
            self.latest_attention = eeg_data['attention']
            result['attention'] = self.latest_attention
            
        if 'meditation' in eeg_data:
            self.latest_meditation = eeg_data['meditation']
            result['meditation'] = eeg_data['meditation']
            
        if 'signal_quality' in eeg_data:
            self.latest_signal_quality = eeg_data['signal_quality']
            result['signal_quality'] = eeg_data['signal_quality']
        
        # 使用数据处理器管理器处理数据
        processed_results = self.data_processor_manager.process_data(eeg_data)
        for processed_data in processed_results:
            result.update(processed_data)
        
        # 发送组合数据
        self.combined_data_updated.emit(result)
        
        return result
    
    def get_latest_raw_eeg(self) -> float:
        """获取最新的原始EEG数据
        
        Returns:
            最新的EEG值
        """
        return self.latest_raw_eeg
    
    def get_latest_frequency_bands(self) -> Dict[str, float]:
        """获取最新的频段数据
        
        Returns:
            各频段的最新值
        """
        return self.latest_frequency_bands.copy()
    
    def get_frequency_band_history(self, band_name: str, max_points: Optional[int] = None) -> List[float]:
        """获取指定频段的历史数据
        
        Args:
            band_name: 频段名称
            max_points: 最大点数，None表示全部
            
        Returns:
            频段历史数据
        """
        all_band_data = self.frequency_band_processor.get_frequency_band_data()
        if band_name in all_band_data:
            data = all_band_data[band_name]
            if max_points is not None:
                return data[-max_points:] if len(data) > max_points else data
            return data
        return []
    
    def get_all_frequency_band_history(self) -> Dict[str, List[float]]:
        """获取所有频段的历史数据
        
        Returns:
            所有频段的历史数据
        """
        return self.frequency_band_processor.get_frequency_band_data()
    
    def get_signal_statistics(self) -> Dict[str, Any]:
        """获取信号统计信息
        
        Returns:
            信号统计信息
        """
        stats = {
            'raw_eeg': {
                'latest': self.latest_raw_eeg,
                'buffer_size': len(self.frequency_band_processor.get_raw_eeg_data())
            },
            'frequency_bands': self.frequency_band_processor.get_signal_statistics(),
            'attention': self.latest_attention,
            'meditation': self.latest_meditation,
            'signal_quality': self.latest_signal_quality
        }
        
        return stats
    
    def clear_all_data(self):
        """清空所有数据"""
        self.frequency_band_processor.clear_buffers()
        self.data_processor_manager.clear_all_buffers()
        
        # 重置最新值
        self.latest_raw_eeg = 0.0
        self.latest_frequency_bands = {}
        self.latest_attention = 0
        self.latest_meditation = 0
        self.latest_signal_quality = 0
    
    def set_sample_rate(self, sample_rate: int):
        """设置采样率
        
        Args:
            sample_rate: 新的采样率
        """
        if sample_rate != self.sample_rate:
            self.sample_rate = sample_rate
            # 重新创建频段处理器
            self.frequency_band_processor = FrequencyBandProcessor(sample_rate, self.buffer_size)
    
    def set_buffer_size(self, buffer_size: int):
        """设置缓冲区大小
        
        Args:
            buffer_size: 新的缓冲区大小
        """
        if buffer_size != self.buffer_size:
            self.buffer_size = buffer_size
            # 重新创建频段处理器
            self.frequency_band_processor = FrequencyBandProcessor(self.sample_rate, buffer_size)
    
    def get_available_frequency_bands(self) -> List[str]:
        """获取可用的频段列表
        
        Returns:
            频段名称列表
        """
        return list(self.frequency_band_processor.frequency_bands.keys())
    
    def get_frequency_band_info(self) -> Dict[str, Dict[str, Any]]:
        """获取频段信息
        
        Returns:
            频段信息字典
        """
        return self.frequency_band_processor.frequency_bands.copy()
