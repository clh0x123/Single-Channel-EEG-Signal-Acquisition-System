#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
串口通信线程模块
负责处理串口数据的接收和发送
"""

import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
import serial

class SerialThread(QThread):
    """串口数据接收线程"""
    data_received = pyqtSignal(bytes)
    connection_error = pyqtSignal(str)
    port_closed = pyqtSignal()
    port_opened = pyqtSignal()
    baudrate = 9600
    timeout = 0.1

    def __init__(self, port_name):
        super().__init__()
        self.port_name = port_name
        self.serial_port = None
        self.running = False
        self.connected = False

    def run(self):
        """线程运行函数"""
        try:
            # 打开串口
            self.serial_port = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            if self.serial_port.is_open:
                self.connected = True
                self.port_opened.emit()
                self.running = True
                
                # 循环接收数据
                while self.running and self.serial_port.is_open:
                    try:
                        if self.serial_port.in_waiting:
                            data = self.serial_port.read(self.serial_port.in_waiting)
                            if data:
                                self.data_received.emit(data)
                        time.sleep(0.01)  # 短暂休眠避免CPU占用过高
                    except serial.SerialException as e:
                        self.connection_error.emit(f"读取错误: {str(e)}")
                        break
            
        except serial.SerialException as e:
            self.connection_error.emit(f"连接错误: {str(e)}")
        finally:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.connected = False
            self.port_closed.emit()

    def stop(self):
        """停止线程"""
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.wait()