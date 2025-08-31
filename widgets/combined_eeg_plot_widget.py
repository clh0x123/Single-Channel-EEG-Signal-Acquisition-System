"""
组合EEG绘图组件
将原始EEG信号和频段信号整合在一张图中显示
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from collections import deque


class CombinedEEGPlotWidget(QWidget):
    """组合EEG绘图组件"""
    
    # 信号定义
    data_updated = pyqtSignal(dict)  # 数据更新信号
    
    def __init__(self, parent=None, max_points=1000):
        super().__init__(parent)
        self.max_points = max_points
        
        # 数据缓冲区
        self.time_buffer = deque(maxlen=max_points)
        self.raw_eeg_buffer = deque(maxlen=max_points)
        
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
        
        # 频段数据缓冲区
        self.band_data_buffers = {band: deque(maxlen=max_points) for band in self.frequency_bands.keys()}
        
        # 绘图曲线
        self.raw_eeg_curve = None
        self.band_curves = {}
        
        # 状态变量
        self.current_time = 0
        self.is_paused = False
        
        # 可见性控制
        self.raw_eeg_visible = True
        self.band_visibility = {band: True for band in self.frequency_bands.keys()}
        
        self.setup_ui()
        self.setup_timer()
        self.setup_connections()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 创建绘图窗口
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('white')
        self.plot_widget.setLabel('left', 'Amplitude (μV)', color='black', size='12pt')
        self.plot_widget.setLabel('bottom', 'Time (s)', color='black', size='12pt')
        self.plot_widget.setTitle('EEG信号与频段分析', color='black', size='14pt')
        
        # 设置网格
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # 设置Y轴范围
        self.plot_widget.setYRange(-100, 100)
        
        # 创建原始EEG信号曲线
        self.raw_eeg_curve = self.plot_widget.plot(pen=pg.mkPen(color='red', width=2), name='raw (原始EEG信号)')
        
        # 创建各频段的绘图曲线
        for band_name, band_info in self.frequency_bands.items():
            color = band_info['color']
            pen = pg.mkPen(color=color, width=1.5)
            self.band_curves[band_name] = self.plot_widget.plot(pen=pen, name=band_info['name'])
        
        # 添加图例
        legend = self.plot_widget.addLegend()
        legend.addItem(self.raw_eeg_curve, 'raw (原始EEG信号)')
        for band_name, band_info in self.frequency_bands.items():
            legend.addItem(self.band_curves[band_name], band_info['name'])
        
        layout.addWidget(self.plot_widget)
        
        # 控制按钮
        self.setup_control_buttons(layout)
        
    def setup_control_buttons(self, parent_layout):
        """设置控制按钮"""
        # 移除了重复的按钮，将由主窗口统一控制
        pass
        
    def setup_timer(self):
        """设置更新定时器"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        self.update_timer.start(50)  # 20Hz更新频率
        
    def setup_connections(self):
        """设置信号连接"""
        # 连接数据更新信号
        self.data_updated.connect(self.process_data_update)
        
    def process_data_update(self, data: dict):
        """处理数据更新
        
        Args:
            data: 更新的数据字典
        """
        if not data or self.is_paused:
            return
            
        # 更新原始EEG信号
        if 'eeg_uv' in data:
            self.raw_eeg_buffer.append(float(data['eeg_uv']))
            self.time_buffer.append(self.current_time)
            self.current_time += 0.01  # 假设采样率为100Hz
        
        # 更新频段信号
        if 'frequency_bands' in data:
            band_data = data['frequency_bands']
            for band_name, value in band_data.items():
                if band_name in self.band_data_buffers:
                    self.band_data_buffers[band_name].append(float(value))
    
    def update_raw_eeg(self, eeg_value: float):
        """更新原始EEG信号
        
        Args:
            eeg_value: EEG信号值
        """
        if not self.is_paused:
            self.raw_eeg_buffer.append(float(eeg_value))
            self.time_buffer.append(self.current_time)
            self.current_time += 0.01  # 假设采样率为100Hz
        
    def update_frequency_bands(self, band_data: dict):
        """更新频段信号数据
        
        Args:
            band_data: 频段信号数据字典
        """
        if not self.is_paused:
            for band_name, value in band_data.items():
                if band_name in self.band_data_buffers:
                    self.band_data_buffers[band_name].append(float(value))
        
    def update_plot(self):
        """更新绘图"""
        if len(self.time_buffer) < 2:
            return
            
        x_data = list(self.time_buffer)
        
        # 更新原始EEG信号曲线
        if len(self.raw_eeg_buffer) > 0 and self.raw_eeg_visible:
            self.raw_eeg_curve.setData(x_data[-len(self.raw_eeg_buffer):], list(self.raw_eeg_buffer))
        elif not self.raw_eeg_visible:
            self.raw_eeg_curve.setData([], [])
        
        # 更新各频段的曲线
        for band_name, curve in self.band_curves.items():
            if band_name in self.band_data_buffers and self.band_visibility.get(band_name, True):
                y_data = list(self.band_data_buffers[band_name])
                if len(y_data) > 0:
                    curve.setData(x_data[-len(y_data):], y_data)
            elif band_name in self.band_visibility and not self.band_visibility[band_name]:
                curve.setData([], [])
        
        # 自动调整X轴范围
        self.plot_widget.setXRange(max(0, x_data[-1] - 10), x_data[-1] + 1)
        
    def clear_all_plots(self):
        """清空所有图表"""
        self.time_buffer.clear()
        self.raw_eeg_buffer.clear()
        for band_data in self.band_data_buffers.values():
            band_data.clear()
        
        self.raw_eeg_curve.setData([], [])
        for curve in self.band_curves.values():
            curve.setData([], [])

    def set_raw_eeg_visibility(self, visible):
        """设置原始EEG信号的可见性
        
        Args:
            visible: 是否可见
        """
        self.raw_eeg_visible = visible
        if not visible:
            self.raw_eeg_curve.setData([], [])
        self.update_plot()

    def set_band_visibility(self, band_name, visible):
        """设置特定频段的可见性
        
        Args:
            band_name: 频段名称
            visible: 是否可见
        """
        if band_name in self.band_visibility:
            self.band_visibility[band_name] = visible
            if not visible and band_name in self.band_curves:
                self.band_curves[band_name].setData([], [])
            self.update_plot()

    def get_band_names(self):
        """获取所有频段名称
        
        Returns:
            频段名称列表
        """
        return list(self.frequency_bands.keys())

    def get_band_info(self, band_name):
        """获取特定频段的信息
        
        Args:
            band_name: 频段名称
        
        Returns:
            频段信息字典
        """
        return self.frequency_bands.get(band_name, {})
        
    def toggle_pause_all(self):
        """切换所有图表的暂停/恢复状态"""
        self.is_paused = not self.is_paused
        return self.is_paused
    
    def get_plot_statistics(self) -> dict:
        """获取所有图表的统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            'raw_eeg': {},
            'frequency_bands': {}
        }
        
        # 获取原始EEG的统计信息
        if self.raw_eeg_buffer:
            raw_array = list(self.raw_eeg_buffer)
            stats['raw_eeg'] = {
                'data_points': len(raw_array),
                'latest_value': raw_array[-1] if raw_array else 0.0
            }
        
        # 获取频段信号的统计信息
        for band_name, buffer in self.band_data_buffers.items():
            if buffer:
                band_array = list(buffer)
                stats['frequency_bands'][band_name] = {
                    'data_points': len(band_array),
                    'latest_value': band_array[-1] if band_array else 0.0
                }
        
        return stats
        
    def set_y_range(self, min_val: float, max_val: float):
        """设置图表的Y轴范围
        
        Args:
            min_val: 最小值
            max_val: 最大值
        """
        self.plot_widget.setYRange(min_val, max_val)
        
    def set_max_points(self, max_points: int):
        """设置最大数据点数
        
        Args:
            max_points: 最大点数
        """
        self.max_points = max_points
        # 注意：这里需要重新创建子组件来应用新的max_points
        # 或者添加方法来动态调整缓冲区大小
