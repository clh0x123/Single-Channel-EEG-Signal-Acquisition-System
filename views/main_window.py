import os
import sys
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QSizePolicy)
from services.serial_manager import SerialManager
from services.tgam_simulator import TGAMSimulator
from widgets.realtime_plot_widget import RealtimePlotWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 加载UI文件
        ui_file = os.path.join(os.path.dirname(__file__), 'main_window.ui')
        uic.loadUi(ui_file, self)
        
        # 初始化接收端串口管理器
        self.receiver_serial_manager = SerialManager()
        self.receiver_serial_manager.data_received.connect(self.on_raw_data_received)
        self.receiver_serial_manager.parsed_data_received.connect(self.on_parsed_data_received)
        self.receiver_serial_manager.connection_error.connect(self.on_connection_error)
        
        # 初始化TGAM串口管理器
        self.tgam_serial_manager = SerialManager()
        
        # 初始化TGAM模拟器
        self.tgam_simulator = TGAMSimulator(serial_manager=self.tgam_serial_manager)
        
        # 设置选项卡界面
        self.create_tabbed_interface()
        
        # 设置默认值
        self.setup_default_values()
        
        # 连接信号和槽
        self.connect_signals()
        
        # 自动刷新串口列表
        self.refresh_receiver_ports()
        self.refresh_tgam_ports()
        
        # 初始化状态
        self.update_status()
        
        # 启动定时器更新状态
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)
    
    def create_tabbed_interface(self):
        """设置选项卡界面"""
        # 使用UI文件中已有的tabWidget
        self.tab_widget = self.tabWidget
        
        # 获取UI中已有的串口设置选项卡
        self.serial_tab = self.serialTab
        
        # 获取绘图选项卡
        self.plot_tab = self.plotTab
        
        # 创建绘图控件
        self.plot_widget = RealtimePlotWidget(self.plot_tab)
        # 设置控件大小策略为扩展，使其能填满可用空间
        self.plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 设置图表标题
        self.plot_widget.plot_widget.setTitle("脑电图信号", color='k', size='12pt')
        # 设置网格
        self.plot_widget.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        # 设置Y轴范围
        self.plot_widget.set_y_range(-100, 100)
        
        # 创建控制按钮布局
        control_layout = QHBoxLayout()
        
        self.clearPlotButton = QPushButton("清除绘图")
        self.clearPlotButton.clicked.connect(self.plot_widget.clear_plot)
        
        self.yRangeButton = QPushButton("调整Y轴范围")
        self.yRangeButton.clicked.connect(self.adjust_y_range)
        
        self.savePlotButton = QPushButton("保存图像")
        self.savePlotButton.clicked.connect(self.save_plot_image)
        
        # 添加到控制面板
        control_layout.addWidget(self.clearPlotButton)
        control_layout.addWidget(self.yRangeButton)
        control_layout.addWidget(self.savePlotButton)
        
        # 创建暂停按钮并添加到控制面板
        self.pauseButton = QPushButton("开始")
        self.pauseButton.clicked.connect(self.toggle_plot_and_simulation)
        control_layout.addWidget(self.pauseButton)
        
        # 初始状态设置为暂停
        self.plot_widget.pause_plot()
        
        # 使用plot_tab现有的布局
        plot_tab_layout = self.plot_tab.layout()

        # 确保plot_tab使用扩展大小策略
        self.plot_tab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if plot_tab_layout is None:
            # 创建新布局
            plot_tab_layout = QVBoxLayout(self.plot_tab)
        else:
            # 清空现有布局中的所有项
            while plot_tab_layout.count() > 0:
                item = plot_tab_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.hide()  # 隐藏而不是删除，以防后续需要
                elif item.layout() is not None:
                    sub_layout = item.layout()
                    while sub_layout.count() > 0:
                        sub_item = sub_layout.takeAt(0)
                        sub_widget = sub_item.widget()
                        if sub_widget is not None:
                            sub_widget.hide()

        # 添加绘图控件和控制布局
        plot_tab_layout.addWidget(self.plot_widget)
        plot_tab_layout.addLayout(control_layout)

        # 设置拉伸因子，让绘图控件占满大部分空间
        plot_tab_layout.setStretch(0, 100)
        plot_tab_layout.setStretch(1, 1)
    
    def setup_default_values(self):
        """设置默认值"""
        # 设置默认波特率
        self.baudrateCombo.setCurrentText("9600")
        self.tgamBaudrateCombo.setCurrentText("9600")
        
        # 设置默认数据位
        self.databitsCombo.setCurrentText("8")
        self.tgamDatabitsCombo.setCurrentText("8")
        
        # 设置默认校验位
        self.parityCombo.setCurrentText("None")
        self.tgamParityCombo.setCurrentText("None")
        
        # 设置默认停止位
        self.stopbitsCombo.setCurrentText("1")
        self.tgamStopbitsCombo.setCurrentText("1")
        
        # 设置默认流控
        self.flowcontrolCombo.setCurrentText("None")
        
        # 设置默认显示格式
        self.asciiRadio.setCurrentText("Hex")
        
        # 设置默认选项
        self.autoWrapCheck.setChecked(True)
        self.showTimeCheck.setChecked(True)
    
    def connect_signals(self):
        """连接信号和槽"""
        # 串口控制按钮
        self.openCloseButton.clicked.connect(self.toggle_receiver_port)
        self.refreshButton.clicked.connect(self.refresh_receiver_ports)
        self.clearButton.clicked.connect(self.clear_receive_area)
        
        # TGAM控制按钮
        self.tgamOpenCloseButton.clicked.connect(self.toggle_tgam_port)
        self.tgamRefreshButton.clicked.connect(self.refresh_tgam_ports)
        self.startSimButton.clicked.connect(self.start_tgam_simulation)
        self.stopSimButton.clicked.connect(self.stop_tgam_simulation)
        
        # 显示设置
        self.asciiRadio.currentTextChanged.connect(self.on_display_format_changed)
        self.autoWrapCheck.toggled.connect(self.on_auto_wrap_changed)
        self.showTimeCheck.toggled.connect(self.on_show_time_changed)
        
        # 将TGAM串口管理器的解析数据信号连接到绘图组件
        self.tgam_serial_manager.parsed_data_received.connect(self.plot_widget.update_data)
        self.receiver_serial_manager.parsed_data_received.connect(self.plot_widget.update_data)
    
    def refresh_receiver_ports(self):
        """刷新接收端端口列表"""
        ports = self.receiver_serial_manager.update_port_list()
        self.portCombo.clear()
        self.portCombo.addItems(ports)
    
    def refresh_tgam_ports(self):
        """刷新TGAM端口列表"""
        ports = self.tgam_serial_manager.update_port_list()
        self.tgamPortCombo.clear()
        self.tgamPortCombo.addItems(ports)
    
    def toggle_plot_and_simulation(self):
        """同时切换绘图和TGAM模拟的暂停/恢复状态"""
        # 切换绘图状态
        self.plot_widget.toggle_pause()

        # 更新按钮文本
        if self.plot_widget.is_paused:
            self.pauseButton.setText("开始")
            # 停止模拟
            if hasattr(self, 'tgam_simulator') and self.tgam_simulator.running:
                self.stop_tgam_simulation()
        else:
            self.pauseButton.setText("暂停")
            # 启动模拟
            if hasattr(self, 'tgam_simulator') and not self.tgam_simulator.running:
                self.start_tgam_simulation()
    
    def toggle_receiver_port(self):
        """切换接收端串口状态"""
        if not self.receiver_serial_manager.is_connected():
            # 打开串口
            port = self.portCombo.currentText()
            baudrate = int(self.baudrateCombo.currentText())
            databits = int(self.databitsCombo.currentText())
            parity = self.parityCombo.currentText()
            stopbits = float(self.stopbitsCombo.currentText())
            flowcontrol = self.flowcontrolCombo.currentText()
            
            # 设置串口参数
            self.receiver_serial_manager.set_port(port)
            self.receiver_serial_manager.set_baudrate(baudrate)
            self.receiver_serial_manager.databits = databits
            self.receiver_serial_manager.parity = parity
            self.receiver_serial_manager.stopbits = stopbits
            self.receiver_serial_manager.flowcontrol = flowcontrol
            
            if self.receiver_serial_manager.open_serial():
                self.openCloseButton.setText("关闭串口")
                self.update_status()
            else:
                self.receiveText.append("打开串口失败")
        else:
            # 关闭串口
            self.receiver_serial_manager.close_serial()
            self.openCloseButton.setText("打开串口")
            self.update_status()
    
    def toggle_tgam_port(self):
        """切换TGAM串口状态"""
        if not self.tgam_serial_manager.is_connected():
            # 打开TGAM串口
            port = self.tgamPortCombo.currentText()
            baudrate = int(self.tgamBaudrateCombo.currentText())
            databits = int(self.tgamDatabitsCombo.currentText())
            parity = self.tgamParityCombo.currentText()
            stopbits = float(self.tgamStopbitsCombo.currentText())
            
            # 设置串口参数
            self.tgam_serial_manager.set_port(port)
            self.tgam_serial_manager.set_baudrate(baudrate)
            self.tgam_serial_manager.databits = databits
            self.tgam_serial_manager.parity = parity
            self.tgam_serial_manager.stopbits = stopbits
            
            # TGAM默认不使用流控
            self.tgam_serial_manager.flowcontrol = "None"
            
            if self.tgam_serial_manager.open_serial():
                self.tgamOpenCloseButton.setText("关闭TGAM串口")
                self.tgamStatusLabel.setText("TGAM串口状态: 打开")
                self.tgamStatusLabel.setStyleSheet("color: green;")
                # 更新TGAM模拟器的参数
                self.tgam_simulator.port = port
                self.tgam_simulator.baudrate = baudrate
            else:
                self.receiveText.append("打开TGAM串口失败")
        else:
            # 关闭TGAM串口
            self.tgam_serial_manager.close_serial()
            self.tgamOpenCloseButton.setText("打开TGAM串口")
            self.tgamStatusLabel.setText("TGAM串口状态: 关闭")
            self.tgamStatusLabel.setStyleSheet("color: red;")
    
    def start_tgam_simulation(self):
        """开始TGAM模拟"""
        if self.tgam_serial_manager.is_connected():
            if self.tgam_simulator.start():
                self.startSimButton.setEnabled(False)
                self.stopSimButton.setEnabled(True)
                self.receiveText.append("开始TGAM模拟")
            else:
                self.receiveText.append("TGAM模拟启动失败")
        else:
            self.receiveText.append("请先打开TGAM串口")
    
    def stop_tgam_simulation(self):
        """停止TGAM模拟"""
        self.tgam_simulator.stop()
        self.startSimButton.setEnabled(True)
        self.stopSimButton.setEnabled(False)
        self.receiveText.append("停止TGAM模拟")
    
    def clear_receive_area(self):
        """清空接收区"""
        self.receiveText.clear()
    
    def on_display_format_changed(self, format_type):
        """显示格式改变"""
        # 这里可以添加格式转换逻辑
        pass
    
    def on_auto_wrap_changed(self, checked):
        """自动换行设置改变"""
        if checked:
            self.receiveText.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.receiveText.setLineWrapMode(QTextEdit.NoWrap)
    
    def on_show_time_changed(self, checked):
        """显示时间设置改变"""
        # 这里可以添加时间显示逻辑
        pass
    
    def on_raw_data_received(self, data):
        """接收原始数据"""
        if self.showTimeCheck.isChecked():
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            data_str = f"[{timestamp}] {data}"
        else:
            data_str = data
        
        if self.asciiRadio.currentText() == "Hex":
            # 转换为十六进制显示
            hex_data = ' '.join([f"{b:02X}" for b in data])
            self.receiveText.append(hex_data)
        else:
            # ASCII显示
            try:
                ascii_data = data.decode('ascii', errors='replace')
                self.receiveText.append(ascii_data)
            except:
                self.receiveText.append(str(data))
        
        # 自动滚动到底部
        self.receiveText.ensureCursorVisible()
    
    def on_parsed_data_received(self, parsed_data):
        """接收解析后的数据"""
        # 确保数据是有效的
        if parsed_data is None:
            print("接收到空数据")
            return
            
        # 提取数据类型和EEG值
        data_type = parsed_data.get('type', 'eeg')
        print(f"接收到数据类型: {data_type}")
        
        # 确保数据包含eeg_uv字段
        if 'eeg_uv' not in parsed_data:
            print("数据中不包含eeg_uv字段")
            # 尝试从其他字段提取或计算EEG值
            # 这里可以添加适当的错误处理或日志记录
            return
        
        print(f"接收到EEG数据: {parsed_data['eeg_uv']}")
        # 将数据传递给绘图组件
        self.plot_widget.update_data(parsed_data)
    
    def on_connection_error(self, error_msg):
        """处理连接错误"""
        self.receiveText.append(f"错误: {error_msg}")
    
    def update_status(self):
        """更新状态显示"""
        # 更新接收端串口状态
        if self.receiver_serial_manager.is_connected():
            self.statusLabel.setText("接收端串口状态: 打开")
            self.statusLabel.setStyleSheet("color: green;")
        else:
            self.statusLabel.setText("接收端串口状态: 关闭")
            self.statusLabel.setStyleSheet("color: red;")
        
        # 更新TGAM串口状态
        if self.tgam_serial_manager.is_connected():
            self.tgamStatusLabel.setText("TGAM串口状态: 打开")
            self.tgamStatusLabel.setStyleSheet("color: green;")
        else:
            self.tgamStatusLabel.setText("TGAM串口状态: 关闭")
            self.tgamStatusLabel.setStyleSheet("color: red;")
        
        # 更新接收统计
        # 由于serial_manager.py中没有get_received_bytes方法，这里简单处理
        received_bytes = len(self.receiveText.toPlainText())
        self.receivedStatsLabel.setText(f"接收字节: {received_bytes}")
    
    def adjust_y_range(self):
        """调整Y轴范围"""
        from PyQt5.QtWidgets import QInputDialog
        min_val, ok1 = QInputDialog.getDouble(self, "调整Y轴范围", "最小值 (μV):", -100, -1000, 1000)
        if ok1:
            max_val, ok2 = QInputDialog.getDouble(self, "调整Y轴范围", "最大值 (μV):", 100, -1000, 1000)
            if ok2:
                self.plot_widget.set_y_range(min_val, max_val)
    
    def save_plot_image(self):
        """保存绘图图像"""
        from PyQt5.QtWidgets import QFileDialog

        # 获取文件名
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图像", "eeg_plot.png", "PNG Files (*.png);;All Files (*)"
        )
        
        if file_path:
            # 捕获绘图区域的图像
            pixmap = self.plot_widget.plot_widget.grab()
            pixmap.save(file_path)
            self.receiveText.append(f"图像已保存到: {file_path}")
    
    def closeEvent(self, event):
        """关闭事件"""
        # 关闭串口
        self.receiver_serial_manager.close_serial()
        self.tgam_serial_manager.close_serial()
        if hasattr(self.tgam_simulator, 'close_serial'):
            self.tgam_simulator.close_serial()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()