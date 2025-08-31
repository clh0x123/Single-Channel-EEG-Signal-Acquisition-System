"""
实时绘图组件
用于显示EEG信号的实时波形
"""
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, pyqtSignal
import pyqtgraph as pg
from collections import deque


class RealtimePlotWidget(QWidget):
    """实时绘图组件"""
    
    def __init__(self, parent=None, max_points=1000):
        super().__init__(parent)
        self.max_points = max_points
        self.data_buffer = deque(maxlen=max_points)
        self.time_buffer = deque(maxlen=max_points)
        self.current_time = 0
        self.is_paused = False
        
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 创建绘图窗口
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('white')
        self.plot_widget.setLabel('left', 'Amplitude (μV)', color='black', size='12pt')
        self.plot_widget.setLabel('bottom', 'Time (s)', color='black', size='12pt')
        self.plot_widget.setTitle('EEG Signal Real-time Plot', color='black', size='14pt')
        
        # 设置网格
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # 创建绘图曲线
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='blue', width=2))
        
        # 设置Y轴范围
        self.plot_widget.setYRange(-100, 100)
        
        layout.addWidget(self.plot_widget)
        
    def setup_timer(self):
        """设置更新定时器"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        self.update_timer.start(50)  # 20Hz更新频率
        
    def add_data_point(self, value):
        """添加数据点"""
        self.data_buffer.append(float(value))
        self.time_buffer.append(self.current_time)
        self.current_time += 0.01  # 假设采样率为100Hz
        
    def update_plot(self):
        """更新绘图"""
        if len(self.data_buffer) > 1:
            x_data = list(self.time_buffer)
            y_data = list(self.data_buffer)
            self.curve.setData(x_data, y_data)
            
            # 自动调整X轴范围
            if len(x_data) > 0:
                self.plot_widget.setXRange(max(0, x_data[-1] - 10), x_data[-1] + 1)
    
    def clear_plot(self):
        """清空绘图"""
        self.data_buffer.clear()
        self.time_buffer.clear()
        self.current_time = 0
        self.curve.setData([], [])
        
    def set_y_range(self, min_val, max_val):
        """设置Y轴范围"""
        self.plot_widget.setYRange(min_val, max_val)
        
    def pause_plot(self):
        """暂停绘图"""
        self.update_timer.stop()
        self.is_paused = True
        
    def resume_plot(self):
        """恢复绘图"""
        self.update_timer.start(50)
        self.is_paused = False
        
    def toggle_pause(self):
        """切换绘图暂停/恢复状态"""
        if self.is_paused:
            self.resume_plot()
        else:
            self.pause_plot()
    
    def update_data(self, data):
        """更新数据
        从SerialManager接收解析后的数据并添加到绘图中
        
        Args:
            data: 解析后的数据字典
        """
        # 确保数据是有效的
        if data is None:
            return
            
        # 检查数据类型
        data_type = data.get('type', 'unknown')
        
        # 根据数据类型处理
        if data_type in ['eeg', 'raw_eeg'] and 'eeg_uv' in data:
            # 添加EEG数据点
            self.add_data_point(data['eeg_uv'])
        elif data_type == 'signal_quality' and 'quality' in data:
            # 可以在这里添加信号质量的显示逻辑
            pass
        elif data_type in ['attention', 'meditation'] and data_type in data:
            # 可以在这里添加注意力/冥想值的显示逻辑
            pass
        elif 'eeg_uv' in data:
            # 兼容旧的数据格式
            self.add_data_point(data['eeg_uv'])
        elif data_type == 'raw_eeg' and isinstance(data, (int, float)):
            # 直接处理原始EEG数值
            self.add_data_point(data)