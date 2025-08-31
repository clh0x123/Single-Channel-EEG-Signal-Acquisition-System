"""
EEG频段信号处理器
负责将原始EEG信号分解为不同频段的信号
"""
import numpy as np
from scipy import signal
from collections import deque
from typing import Dict, Any, List, Tuple


class FrequencyBandProcessor:
    """EEG频段信号处理器"""
    
    def __init__(self, sample_rate: int = 512, buffer_size: int = 1000):
        """初始化频段处理器
        
        Args:
            sample_rate: 采样率，默认512Hz
            buffer_size: 缓冲区大小
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        
        # 定义频段范围 (Hz)
        self.frequency_bands = {
            'delta': (0.5, 4.0),      # Delta波: 0.5-4Hz
            'theta': (4.0, 8.0),      # Theta波: 4-8Hz
            'alpha_low': (8.0, 10.0), # 低频Alpha: 8-10Hz
            'alpha_high': (10.0, 13.0), # 高频Alpha: 10-13Hz
            'beta_low': (13.0, 20.0),   # 低频Beta: 13-20Hz
            'beta_high': (20.0, 30.0),  # 高频Beta: 20-30Hz
            'gamma_low': (30.0, 50.0),  # 低频Gamma: 30-50Hz
            'gamma_high': (50.0, 100.0) # 高频Gamma: 50-100Hz
        }
        
        # 数据缓冲区
        self.raw_eeg_buffer = deque(maxlen=buffer_size)
        self.filtered_signals = {band: deque(maxlen=buffer_size) for band in self.frequency_bands.keys()}
        
        # 滤波器缓存
        self.filters = {}
        self._create_filters()
        
    def _create_filters(self):
        """创建各频段的带通滤波器"""
        for band_name, (low_freq, high_freq) in self.frequency_bands.items():
            # 设计Butterworth带通滤波器
            nyquist = self.sample_rate / 2
            low_norm = low_freq / nyquist
            high_norm = high_freq / nyquist
            
            # 确保频率在有效范围内
            low_norm = max(0.001, min(low_norm, 0.99))
            high_norm = max(0.001, min(high_norm, 0.99))
            
            if low_norm < high_norm:
                try:
                    b, a = signal.butter(4, [low_norm, high_norm], btype='band')
                    self.filters[band_name] = (b, a)
                except ValueError:
                    # 如果滤波器设计失败，使用简单的移动平均
                    self.filters[band_name] = None
            else:
                self.filters[band_name] = None
    
    def add_eeg_data(self, eeg_value: float):
        """添加EEG数据点
        
        Args:
            eeg_value: EEG信号值 (μV)
        """
        self.raw_eeg_buffer.append(eeg_value)
        
        # 当缓冲区有足够数据时进行滤波
        if len(self.raw_eeg_buffer) >= 64:  # 至少需要64个点进行有效滤波
            self._process_frequency_bands()
    
    def _process_frequency_bands(self):
        """处理频段信号"""
        if len(self.raw_eeg_buffer) < 64:
            return
            
        # 转换为numpy数组
        eeg_data = np.array(list(self.raw_eeg_buffer))
        
        # 对每个频段进行滤波
        for band_name, (low_freq, high_freq) in self.frequency_bands.items():
            filtered_signal = self._filter_signal(eeg_data, band_name)
            
            # 取最新的滤波结果
            if filtered_signal is not None and len(filtered_signal) > 0:
                self.filtered_signals[band_name].append(filtered_signal[-1])
            else:
                # 如果没有滤波结果，使用原始信号
                self.filtered_signals[band_name].append(eeg_data[-1])
    
    def _filter_signal(self, eeg_data: np.ndarray, band_name: str) -> np.ndarray:
        """对信号进行滤波
        
        Args:
            eeg_data: 原始EEG数据
            band_name: 频段名称
            
        Returns:
            滤波后的信号
        """
        if band_name not in self.filters or self.filters[band_name] is None:
            # 如果没有滤波器，使用简单的移动平均
            return self._simple_moving_average(eeg_data, 8)
        
        try:
            b, a = self.filters[band_name]
            filtered = signal.filtfilt(b, a, eeg_data)
            return filtered
        except (ValueError, RuntimeError):
            # 滤波失败时使用移动平均
            return self._simple_moving_average(eeg_data, 8)
    
    def _simple_moving_average(self, data: np.ndarray, window_size: int) -> np.ndarray:
        """简单的移动平均滤波
        
        Args:
            data: 输入数据
            window_size: 窗口大小
            
        Returns:
            滤波后的数据
        """
        if len(data) < window_size:
            return data
        
        result = np.convolve(data, np.ones(window_size)/window_size, mode='same')
        return result
    
    def get_frequency_band_data(self) -> Dict[str, List[float]]:
        """获取所有频段的信号数据
        
        Returns:
            各频段的信号数据字典
        """
        return {band: list(data) for band, data in self.filtered_signals.items()}
    
    def get_latest_frequency_band_data(self) -> Dict[str, float]:
        """获取最新的频段信号数据
        
        Returns:
            各频段的最新信号值
        """
        return {band: data[-1] if data else 0.0 for band, data in self.filtered_signals.items()}
    
    def get_raw_eeg_data(self) -> List[float]:
        """获取原始EEG数据
        
        Returns:
            原始EEG信号数据
        """
        return list(self.raw_eeg_buffer)
    
    def clear_buffers(self):
        """清空所有数据缓冲区"""
        self.raw_eeg_buffer.clear()
        for band_data in self.filtered_signals.values():
            band_data.clear()
    
    def get_signal_statistics(self) -> Dict[str, Dict[str, float]]:
        """获取各频段信号的统计信息
        
        Returns:
            各频段信号的统计信息
        """
        stats = {}
        
        for band_name, band_data in self.filtered_signals.items():
            if len(band_data) > 0:
                data_array = np.array(list(band_data))
                stats[band_name] = {
                    'mean': float(np.mean(data_array)),
                    'std': float(np.std(data_array)),
                    'max': float(np.max(data_array)),
                    'min': float(np.min(data_array)),
                    'latest': float(data_array[-1])
                }
            else:
                stats[band_name] = {
                    'mean': 0.0, 'std': 0.0, 'max': 0.0, 'min': 0.0, 'latest': 0.0
                }
        
        return stats
