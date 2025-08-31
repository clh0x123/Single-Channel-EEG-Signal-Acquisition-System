"""
频段信号绘图组件
专门用于显示不同频段的EEG信号
"""
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QColor
import pyqtgraph as pg
from collections import deque
from typing import Dict, List, Optional


class FrequencyBandPlotWidget(QWidget):
    """频段信号绘图组件"""
    
    def __init__(self, parent=None, max_points=1000):
        super().__init__(parent)
        self.max_points = max_points
        self.current_time = 0
        
        # 频段配置
        self.frequency_bands = {
            'delta': {'name': 'δ (Delta)', 'color': 'black', 'range': (0.5, 4.0)},
            'theta': {'name': 'θ (Theta)', 'color': 'yellow', 'range': (4.0, 8.0)},
            'alpha_low': {'name': 'α↑ (Alpha上升)', 'color': 'magenta', 'range': (8.0, 10.0)},
            'alpha_high': {'name': 'α↓ (Alpha下降)', 'color': 'darkblue', 'range': (10.0, 13.0)},
            'beta_low': {'name': 'β↑ (Beta上升)', 'color': 'cyan', 'range': (13.0, 20.0)},
            'beta_high': {'name': 'β↓ (Beta下降)', 'color': 'purple', 'range': (20.0, 30.0)},
            'gamma_low': {'name': 'γ↓ (Gamma下降)', 'color': 'darkgreen', 'range': (30.0, 50.0)},
            'gamma_high': {'name': 'γ- (Gamma负)', 'color': 'darkred', 'range': (50.0, 100.0)}
        }
        
        # 数据缓冲区
        self.time_buffer = deque(maxlen=max_points)
        self.band_data_buffers = {band: deque(maxlen=max_points) for band in self.frequency_bands.keys()}
        self.is_paused = False
        
        # 绘图曲线
        self.curves = {}
        
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 创建绘图窗口
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('white')
        self.plot_widget.setLabel('left', 'Amplitude (μV)', color='black', size='10pt')
        self.plot_widget.setLabel('bottom', 'Time (s)', color='black', size='10pt')
        self.plot_widget.setTitle('EEG Frequency Bands', color='black', size='12pt')
        
        # 设置网格
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # 设置Y轴范围
        self.plot_widget.setYRange(-50, 50)
        
        # 创建各频段的绘图曲线
        for band_name, band_info in self.frequency_bands.items():
            color = band_info['color']
            pen = pg.mkPen(color=color, width=1.5)
            self.curves[band_name] = self.plot_widget.plot(pen=pen, name=band_info['name'])
        
        # 添加图例
        legend = self.plot_widget.addLegend()
        for band_name, band_info in self.frequency_bands.items():
            legend.addItem(self.curves[band_name], band_info['name'])
        
        layout.addWidget(self.plot_widget)
        
        # 添加控制面板
        self.setup_control_panel(layout)
        
    def setup_control_panel(self, parent_layout):
        """设置控制面板"""
        control_layout = QHBoxLayout()
        
        # 频段选择下拉框
        self.band_selector = QComboBox()
        self.band_selector.addItem("显示所有频段")
        for band_name, band_info in self.frequency_bands.items():
            self.band_selector.addItem(band_info['name'])
        
        self.band_selector.currentTextChanged.connect(self.on_band_selection_changed)
        
        # 添加标签和控件
        control_layout.addWidget(QLabel("频段选择:"))
        control_layout.addWidget(self.band_selector)
        control_layout.addStretch()
        
        parent_layout.addLayout(control_layout)
        
    def setup_timer(self):
        """设置更新定时器"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        self.update_timer.start(100)  # 10Hz更新频率
        
    def add_frequency_band_data(self, band_data: Dict[str, float]):
        """添加频段数据
        
        Args:
            band_data: 各频段的信号值字典
        """
        self.time_buffer.append(self.current_time)
        self.current_time += 0.01  # 假设采样率为100Hz
        
        # 添加各频段数据
        for band_name, value in band_data.items():
            if band_name in self.band_data_buffers:
                self.band_data_buffers[band_name].append(float(value))
    
    def update_plot(self):
        """更新绘图"""
        if len(self.time_buffer) > 1:
            x_data = list(self.time_buffer)
            
            # 更新各频段的曲线
            for band_name, curve in self.curves.items():
                if band_name in self.band_data_buffers:
                    y_data = list(self.band_data_buffers[band_name])
                    if len(y_data) > 0:
                        curve.setData(x_data[-len(y_data):], y_data)
            
            # 自动调整X轴范围
            if len(x_data) > 0:
                self.plot_widget.setXRange(max(0, x_data[-1] - 10), x_data[-1] + 1)
    
    def on_band_selection_changed(self, selected_text):
        """频段选择改变时的处理"""
        if selected_text == "显示所有频段":
            # 显示所有频段
            for curve in self.curves.values():
                curve.setVisible(True)
        else:
            # 只显示选中的频段
            for band_name, curve in self.curves.items():
                if self.frequency_bands[band_name]['name'] == selected_text:
                    curve.setVisible(True)
                else:
                    curve.setVisible(False)
    
    def clear_plot(self):
        """清空绘图"""
        self.time_buffer.clear()
        for band_data in self.band_data_buffers.values():
            band_data.clear()
        for curve in self.curves.values():
            curve.setData([], [])

    def pause_plot(self):
        """暂停绘图"""
        self.update_timer.stop()
        self.is_paused = True
        
    def resume_plot(self):
        """恢复绘图"""
        self.update_timer.start(100)
        self.is_paused = False
        
    def toggle_pause(self):
        """切换绘图暂停/恢复状态"""
        if self.is_paused:
            self.resume_plot()
        else:
            self.pause_plot()
        self.current_time = 0
        
        # 清空所有曲线
        for curve in self.curves.values():
            curve.setData([], [])
    
    def set_y_range(self, min_val: float, max_val: float):
        """设置Y轴范围"""
        self.plot_widget.setYRange(min_val, max_val)
    
    def pause_plot(self):
        """暂停绘图"""
        self.update_timer.stop()
    
    def resume_plot(self):
        """恢复绘图"""
        self.update_timer.start(100)
    
    def toggle_pause(self):
        """切换绘图暂停/恢复状态"""
        if self.update_timer.isActive():
            self.pause_plot()
        else:
            self.resume_plot()
    
    def get_visible_bands(self) -> List[str]:
        """获取当前可见的频段"""
        visible_bands = []
        for band_name, curve in self.curves.items():
            if curve.isVisible():
                visible_bands.append(band_name)
        return visible_bands
    
    def set_band_visibility(self, band_name: str, visible: bool):
        """设置特定频段的可见性
        
        Args:
            band_name: 频段名称
            visible: 是否可见
        """
        if band_name in self.curves:
            self.curves[band_name].setVisible(visible)
    
    def get_plot_statistics(self) -> Dict[str, Dict[str, float]]:
        """获取绘图统计信息
        
        Returns:
            各频段的统计信息
        """
        stats = {}
        
        for band_name, band_data in self.band_data_buffers.items():
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
