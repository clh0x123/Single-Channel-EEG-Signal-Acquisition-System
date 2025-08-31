"""
EEG数据协调器
负责协调频段处理器和绘图组件之间的数据流
"""
from typing import Dict, Any, List, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from collections import deque
import numpy as np

from services.frequency_band_processor import FrequencyBandProcessor
from .data_processor import DataProcessorManager


class EEGDataCoordinator(QObject):
    """EEG数据协调器"""
    
    # 信号定义
    raw_eeg_updated = pyqtSignal(float)  # 原始EEG数据更新
    frequency_bands_updated = pyqtSignal(dict)  # 频段数据更新
    combined_data_updated = pyqtSignal(dict)  # 组合数据更新
    processed_data_available = pyqtSignal(dict)  # 处理后的数据可用信号
    
    def __init__(self, sample_rate: int = 512, buffer_size: int = 1000):
        super().__init__()
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        
        # 初始化处理器
        self.frequency_band_processor = FrequencyBandProcessor(sample_rate)
        self.data_processor_manager = DataProcessorManager()
        
        # 数据缓存
        self.latest_raw_eeg = 0.0
        self.latest_frequency_bands = {}
        self.latest_attention = 0
        self.latest_meditation = 0
        self.latest_signal_quality = 0
        
        # 数据缓冲区
        self.raw_eeg_buffer = deque(maxlen=buffer_size)
        self.eeg_uv_buffer = deque(maxlen=buffer_size)
        
        # 状态变量
        self.is_processing = True
        
        # 处理定时器 - 增加处理频率以提高频段数据更新速度
        self.processing_timer = QTimer(self)
        self.processing_timer.timeout.connect(self.process_buffer_data)
        self.processing_timer.start(100)  # 每100ms处理一次（10Hz）
        
        # 用于累积数据的临时缓冲区
        self.temp_buffer = []
        self.temp_buffer_size = 64  # 每处理64个数据点进行一次频段分析
        
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
            
            # 添加到缓冲区
            self.raw_eeg_buffer.append(eeg_value)
            self.eeg_uv_buffer.append(eeg_value)
            
            # 添加到临时缓冲区用于频段分析
            self.temp_buffer.append(eeg_value)
            
            # 如果临时缓冲区达到指定大小，立即处理频段数据
            if len(self.temp_buffer) >= self.temp_buffer_size:
                self._process_band_data()
            
            # 发射原始EEG数据信号
            self.raw_eeg_updated.emit(eeg_value)
            self.processed_data_available.emit({
                'eeg_raw': eeg_value,
                'eeg_uv': eeg_value
            })
            
            result['raw_eeg'] = eeg_value
        
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
        
    def _process_band_data(self):
        """处理临时缓冲区中的数据以生成频段信息"""
        if not self.is_processing or len(self.temp_buffer) < self.temp_buffer_size:
            return
            
        # 提取临时缓冲区中的数据
        eeg_data = np.array(self.temp_buffer)
        
        # 向频段处理器添加数据
        for value in eeg_data:
            self.frequency_band_processor.add_eeg_data(value)
        
        # 获取最新的频段数据
        band_powers = self.frequency_band_processor.get_latest_frequency_band_data()
        self.latest_frequency_bands = band_powers
        
        # 清空临时缓冲区
        self.temp_buffer = []
        
        # 发送频段数据
        self.frequency_bands_updated.emit(band_powers)
        
        # 发射包含频段信息的数据信号
        self.processed_data_available.emit({
            'frequency_bands': band_powers,
            'eeg_uv': self.eeg_uv_buffer[-1] if self.eeg_uv_buffer else 0
        })
        
    def process_buffer_data(self):
        """处理缓冲区中的数据以生成频段信息 - 作为备用机制"""
        if not self.is_processing:
            return
            
        # 如果临时缓冲区不为空，也进行处理
        if len(self.temp_buffer) > 0:
            self._process_band_data()
            
    def start_processing(self):
        """开始处理数据"""
        self.is_processing = True
        
    def stop_processing(self):
        """停止处理数据"""
        self.is_processing = False
        
    def clear_buffers(self):
        """清空所有数据缓冲区"""
        self.raw_eeg_buffer.clear()
        self.eeg_uv_buffer.clear()
        self.temp_buffer = []
        
    def set_temp_buffer_size(self, size):
        """设置临时缓冲区大小
        
        Args:
            size: 新的缓冲区大小
        """
        self.temp_buffer_size = max(16, min(size, 256))  # 限制在合理范围内
    
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
