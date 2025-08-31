"""
组合EEG绘图组件
将原始EEG信号和频段信号整合在一张图中显示
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QColor
import pyqtgraph as pg
import numpy as np
from collections import deque


class CombinedEEGPlotWidget(QWidget):
    """组合EEG绘图组件"""
    
    # 信号定义
    data_updated = pyqtSignal(dict)  # 数据更新信号
    
    def __init__(self, parent=None, max_points=5000):
        super().__init__(parent)
        self.max_points = max_points
        
        # 原始EEG数据缓冲区
        self.raw_eeg_buffer = deque(maxlen=max_points)
        self.raw_time_buffer = deque(maxlen=max_points)

        # 缓冲区大小设置
        self.MAX_BAND_BUFFER_SIZE = max_points  # 频段数据缓冲区与原始EEG数据缓冲区大小相同
        
        
        # 频段配置
        self.frequency_bands = {
        'raw': {'name': 'raw', 'color': 'red', 'range': (0, 100)},
        'delta': {'name': 'δ', 'color': 'black', 'range': (0.5, 4.0)},
        'alpha_low': {'name': 'α↑', 'color': 'magenta', 'range': (8.0, 10.0)},
        'alpha_high': {'name': 'α↓', 'color': 'darkblue', 'range': (10.0, 13.0)},
        'beta_low': {'name': 'β↑', 'color': 'cyan', 'range': (13.0, 20.0)},
        'beta_high': {'name': 'β↓', 'color': 'purple', 'range': (20.0, 30.0)},
        'gamma_low': {'name': 'γ↓', 'color': 'darkgreen', 'range': (30.0, 50.0)},
        'gamma_high': {'name': 'γ-', 'color': 'darkred', 'range': (50.0, 100.0)},
        'theta': {'name': 'θ', 'color': 'yellow', 'range': (4.0, 8.0)}
    }

        # 确保频段数据缓冲区与原始EEG数据缓冲区大小相同
        self.MAX_BAND_BUFFER_SIZE = max_points
        
        # 频段数据缓冲区
        self.band_time_buffers = {band: deque(maxlen=max_points) for band in self.frequency_bands.keys()}
        self.band_data_buffers = {band: deque(maxlen=max_points) for band in self.frequency_bands.keys()}
        
        # 绘图窗口和曲线
        self.plot_widgets = {}
        self.curves = {}
        
        # 状态变量
        self.current_time = 0
        self.is_paused = False
        
        # 采样率设置
        self.sample_rate = 512  # 默认512Hz
        self.time_increment = 1.0 / self.sample_rate
        
        # 可见性控制
        self.band_visibility = {band: True for band in self.frequency_bands.keys()}
        
        self.setup_ui()
        self.setup_timer()
        self.setup_connections()
        
    def set_sample_rate(self, sample_rate):
        """设置采样率
        
        Args:
            sample_rate: 新的采样率值
        """
        self.sample_rate = sample_rate
        self.time_increment = 1.0 / self.sample_rate
        
    def setup_ui(self):
        """设置UI界面 - 按照图片中的样式精确设计"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 设置背景颜色
        bg_color = '#d9d9d9'  # 浅灰色背景
        plot_bg_color = '#ffffff'  # 白色绘图区域背景
        
        # 排列频段
        display_order = ['raw', 'delta', 'alpha_low', 'alpha_high', 'beta_low', 'beta_high', 'gamma_low', 'gamma_high', 'theta']
        
        # 为每个频段创建单独的绘图窗口
        for band_name in display_order:
            if band_name not in self.frequency_bands:
                continue
                
            band_info = self.frequency_bands[band_name]
            
            # 创建包含绘图窗口和标签的容器
            plot_container = QWidget()
            plot_container.setStyleSheet(f"background-color: {bg_color};")
            plot_container_layout = QHBoxLayout(plot_container)
            plot_container_layout.setContentsMargins(0, 0, 0, 0)
            plot_container_layout.setSpacing(0)
            
            # 添加频段名称标签，右侧对齐
            band_label = QLabel(band_info['name'])
            band_label.setStyleSheet("color: black; font-weight: bold; font-size: 12pt; padding-right: 10px;")
            band_label.setFixedWidth(60)  # 增加标签宽度以确保显示完全
            band_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            plot_container_layout.addWidget(band_label)
            
            # 创建绘图窗口
            plot_widget = pg.PlotWidget()
            plot_widget.setBackground(plot_bg_color)
            
            # 设置无边框样式
            plot_widget.setStyleSheet("border: none;")
            
            # 移除坐标轴标签和标题
            plot_widget.hideAxis('left')
            plot_widget.hideAxis('bottom')
            plot_widget.setTitle('')
            
            # 禁用网格
            plot_widget.showGrid(x=False, y=False)
            
            # 设置Y轴范围 - 按照图片样式设置
            if band_name == 'raw':
                plot_widget.setYRange(-100, 100)
            else:
                plot_widget.setYRange(-50, 50)
            
            # 创建曲线，设置合适的线宽
            color = band_info['color']
            line_width = 2.0 if band_name == 'raw' else 1.5
            pen = pg.mkPen(color=color, width=line_width, cosmetic=True)
            curve = plot_widget.plot(pen=pen)
            
            # 存储绘图窗口和曲线
            self.plot_widgets[band_name] = plot_widget
            self.curves[band_name] = curve
            
            # 添加绘图窗口到容器，占用大部分空间
            plot_container_layout.addWidget(plot_widget, 1)
            
            # 添加容器到主布局
            layout.addWidget(plot_container)
            
            # 添加分割线（除了最后一个）
            if band_name != display_order[-1]:
                separator = QWidget()
                separator.setStyleSheet("background-color: #b0b0b0;")
                separator.setFixedHeight(1)
                layout.addWidget(separator)
        
    def setup_timer(self):
        """设置更新定时器"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        self.update_timer.start(30)  # 约33Hz更新频率，提高响应速度
        
    def setup_connections(self):
        """设置信号连接"""
        # 连接数据更新信号
        self.data_updated.connect(self.process_data_update)
        # 连接数据更新信号到自动缩放方法
        self.data_updated.connect(self.on_data_updated)
        
    def update_raw_eeg(self, eeg_value):
        """更新原始EEG数据
        
        Args:
            eeg_value: 新的EEG值
        """
        if self.is_paused:
            return

        # 更新当前时间
        self.current_time += self.time_increment

        # 添加原始EEG数据
        self.raw_eeg_buffer.append(float(eeg_value))
        self.raw_time_buffer.append(self.current_time)

    def process_data_update(self, data: dict):
        """处理数据更新
        
        Args:
            data: 更新的数据字典
        """
        if not data or self.is_paused:
            return
            
        # 更新当前时间
        self.current_time += self.time_increment
        
        
        # 更新原始EEG数据
        if 'eeg_raw' in data:
            eeg_value = data['eeg_raw']
            self.raw_eeg_buffer.append(float(eeg_value))
            self.raw_time_buffer.append(self.current_time)
        
        # 更新频段信号
        if 'frequency_bands' in data:
            band_data = data['frequency_bands']
            for band_name, value in band_data.items():
                if band_name in self.band_data_buffers:
                    # 频段数据添加逻辑
                    # 根据TGAM数据流格式说明，原始EEG数据1秒有512个点，而频段数据只有1个点
                    # 所以我们只需要添加一个点，而不是与原始数据相同数量的点
                    self.band_data_buffers[band_name].append(float(value))
                    self.band_time_buffers[band_name].append(self.current_time)
                    
                    # 维护缓冲区大小，确保不会占用过多内存
                    if len(self.band_data_buffers[band_name]) > self.MAX_BAND_BUFFER_SIZE:
                        self.band_data_buffers[band_name].pop(0)
                        self.band_time_buffers[band_name].pop(0)
        
        
    def update_frequency_bands(self, band_data: dict):
        """更新频段信号数据
        
        Args:
            band_data: 频段信号数据字典
        """
        if not self.is_paused:
            # 频段数据应该与最近的原始EEG数据时间戳同步
            if self.raw_time_buffer:
                current_time = self.raw_time_buffer[-1]
            else:
                current_time = self.current_time
                self.current_time += self.time_increment
            
            for band_name, value in band_data.items():
                if band_name in self.band_data_buffers:
                    # 将频段数据添加到缓冲区，使用与原始EEG相同的时间戳
                    self.band_data_buffers[band_name].append(float(value))
                    self.band_time_buffers[band_name].append(current_time)
                    
                    # 维护缓冲区大小，确保不会占用过多内存
                    if len(self.band_data_buffers[band_name]) > self.MAX_BAND_BUFFER_SIZE:
                        self.band_data_buffers[band_name].pop(0)
                        self.band_time_buffers[band_name].pop(0)
        
    def update_plot(self):
        """更新所有绘图"""
        if self.is_paused:
            return

        # 更新原始EEG曲线
        if 'raw' in self.curves and len(self.raw_eeg_buffer) > 1:
            # 获取原始EEG数据和时间戳
            raw_time = list(self.raw_time_buffer)
            raw_data = list(self.raw_eeg_buffer)

            # 更新曲线
            self.curves['raw'].setData(raw_time, raw_data)

            # 同步X轴范围
            if len(raw_time) > 0:
                self.plot_widgets['raw'].setXRange(raw_time[0], raw_time[-1] + 1)

        # 更新各频段的曲线
        for band_name in self.frequency_bands.keys():
            if band_name != 'raw' and len(self.band_data_buffers[band_name]) > 1:
                # 获取频段数据和时间戳
                band_time = list(self.band_time_buffers[band_name])
                band_data = list(self.band_data_buffers[band_name])
                
                # 更新曲线
                self.curves[band_name].setData(band_time, band_data)
                
                # 同步X轴范围
                if len(band_time) > 0:
                    self.plot_widgets[band_name].setXRange(band_time[0], band_time[-1] + 1)
        
    def clear_all_plots(self):
        """清空所有图表"""
        # 清空原始EEG数据缓冲区
        self.raw_eeg_buffer.clear()
        self.raw_time_buffer.clear()

        # 清空所有频段数据缓冲区
        for band_name in self.frequency_bands.keys():
            if band_name in self.band_time_buffers:
                self.band_time_buffers[band_name].clear()
                self.band_data_buffers[band_name].clear()
        
        # 清除所有曲线数据
        for curve in self.curves.values():
            curve.setData([], [])
            

        
    def set_band_visibility(self, band_name, visible):
        """设置特定频段的可见性
        
        Args:
            band_name: 频段名称
            visible: 是否可见
        """
        if band_name in self.band_visibility:
            self.band_visibility[band_name] = visible
            if not visible and band_name in self.curves:
                self.curves[band_name].setData([], [])
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
        
    
        return self.is_paused

    def toggle_pause_all(self):
        """切换所有图表的暂停/继续状态
        
        Returns:
            bool: 切换后的暂停状态
        """
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
        
    def set_y_range(self, min_val: float, max_val: float, band_name=None):
        """设置图表的Y轴范围
        
        Args:
            min_val: 最小值
            max_val: 最大值
            band_name: 可选，指定要设置的频段名称，None表示设置所有频段
        """
        if band_name:
            if band_name in self.plot_widgets:
                self.plot_widgets[band_name].setYRange(min_val, max_val)
        else:
            for plot_widget in self.plot_widgets.values():
                plot_widget.setYRange(min_val, max_val)

    def auto_scale_y(self, band_name=None, scale_factor=1.1):
        """自动调整Y轴范围以适应数据
        
        Args:
            band_name: 可选，指定要调整的频段名称，None表示调整所有频段
            scale_factor: 缩放因子，默认为1.2，值越大波形显示越宽松
        """
        if band_name:
            if band_name in self.band_data_buffers and self.band_data_buffers[band_name]:
                data = list(self.band_data_buffers[band_name])
                min_val = min(data) * scale_factor
                max_val = max(data) * scale_factor
                # 确保Y轴范围包含0点，使波形居中显示
                min_val = min(min_val, 0)
                max_val = max(max_val, 0)
                self.plot_widgets[band_name].setYRange(min_val, max_val)
        else:
            # 调整所有频段
            for band in self.band_data_buffers:
                if band in self.plot_widgets and self.band_data_buffers[band]:
                    data = list(self.band_data_buffers[band])
                    min_val = min(data) * scale_factor
                    max_val = max(data) * scale_factor
                    # 确保Y轴范围包含0点，使波形居中显示
                    min_val = min(min_val, 0)
                    max_val = max(max_val, 0)
                    self.plot_widgets[band].setYRange(min_val, max_val)

    def on_data_updated(self):
        """数据更新后自动调用的方法"""
        # 每收到一定量的数据后自动缩放一次
        # 检查任意一个频段的数据长度
        any_band_has_data = any(len(buffer) > 0 for buffer in self.band_data_buffers.values())
        if any_band_has_data and len(next(iter(self.band_data_buffers.values()))) % 100 == 0:
            self.auto_scale_y()
        
    def set_max_points(self, max_points: int):
        """设置最大数据点数
        
        Args:
            max_points: 最大点数
        """
        # 验证输入值
        if not isinstance(max_points, int) or max_points <= 0:
            raise ValueError("max_points必须是正整数")
            
        self.max_points = max_points
        
        # 更新所有频段的缓冲区大小
        for band_name in self.frequency_bands.keys():
            if band_name in self.band_time_buffers:
                self.band_time_buffers[band_name] = deque(list(self.band_time_buffers[band_name]), maxlen=max_points)
                self.band_data_buffers[band_name] = deque(list(self.band_data_buffers[band_name]), maxlen=max_points)
