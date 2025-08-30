#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
串口管理模块
遵循SOLID原则，负责处理所有串口相关的功能
"""

import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
import serial
from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE
from serial import STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
import serial.tools.list_ports
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
from .tgam_parser import TGAMDataStreamParser
from .data_processor import DataProcessorManager


class ISerialPort(ABC):
    """串口接口"""
    
    @abstractmethod
    def open(self) -> bool:
        """打开串口"""
        pass
    
    @abstractmethod
    def close(self):
        """关闭串口"""
        pass
    
    @abstractmethod
    def is_open(self) -> bool:
        """检查串口是否打开"""
        pass
    
    @abstractmethod
    def read(self, size: int = 1) -> bytes:
        """读取数据"""
        pass
    
    @abstractmethod
    def write(self, data: bytes) -> int:
        """写入数据"""
        pass
    
    @abstractmethod
    def in_waiting(self) -> int:
        """获取等待读取的字节数"""
        pass


class SerialPortWrapper(ISerialPort):
    """串口包装器"""
    
    def __init__(self, port_name: str, baudrate: int = 9600, **kwargs):
        self.port_name = port_name
        self.baudrate = baudrate
        self.serial_params = kwargs
        self.serial_port: Optional[serial.Serial] = None
    
    def open(self) -> bool:
        """打开串口"""
        try:
            self.serial_port = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                **self.serial_params
            )
            return self.serial_port.is_open
        except Exception as e:
            print(f"打开串口失败: {e}")
            return False
    
    def close(self):
        """关闭串口"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
    
    def is_open(self) -> bool:
        """检查串口是否打开"""
        return self.serial_port is not None and self.serial_port.is_open
    
    def read(self, size: int = 1) -> bytes:
        """读取数据"""
        if self.serial_port and self.serial_port.is_open:
            return self.serial_port.read(size)
        return b''
    
    def write(self, data: bytes) -> int:
        """写入数据"""
        if self.serial_port and self.serial_port.is_open:
            return self.serial_port.write(data)
        return 0
    
    def in_waiting(self) -> int:
        """获取等待读取的字节数"""
        if self.serial_port and self.serial_port.is_open:
            return self.serial_port.in_waiting
        return 0


class IPortEnumerator(ABC):
    """端口枚举器接口"""
    
    @abstractmethod
    def enumerate_ports(self) -> List[str]:
        """枚举可用端口"""
        pass


class StandardPortEnumerator(IPortEnumerator):
    """标准端口枚举器"""
    
    def enumerate_ports(self) -> List[str]:
        """使用标准方法枚举端口"""
        try:
            ports_info = serial.tools.list_ports.comports()
            return [port.device for port in ports_info]
        except Exception as e:
            print(f"标准方法获取串口失败: {e}")
            return []


class WindowsPortEnumerator(IPortEnumerator):
    """Windows端口枚举器"""
    
    def enumerate_ports(self) -> List[str]:
        """在Windows下枚举常见串口"""
        available_ports = []
        
        # 检查前20个COM端口
        for i in range(1, 21):
            port_name = f'COM{i}'
            try:
                test_serial = serial.Serial(port_name, timeout=0.1)
                test_serial.close()
                available_ports.append(port_name)
            except (OSError, serial.SerialException):
                pass
        
        return available_ports


class SerialManager(QThread):
    """串口管理类，遵循SOLID原则"""
    
    # 信号定义
    data_received = pyqtSignal(bytes)
    parsed_data_received = pyqtSignal(dict)
    connection_error = pyqtSignal(str)
    port_closed = pyqtSignal()
    port_opened = pyqtSignal()
    port_list_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # 依赖注入
        self.port_enumerators = [
            StandardPortEnumerator(),
            WindowsPortEnumerator()
        ]
        
        # 串口相关
        self.serial_port: Optional[ISerialPort] = None
        self.running = False
        self.connected = False
        self.port_name = ""
        self.baudrate = 9600
        self.timeout = 0.1
        self.ports = []
        
        # 数据解析和处理
        self.data_parser = TGAMDataStreamParser()
        self.data_processor = DataProcessorManager()
    
    def update_port_list(self):
        """更新可用串口列表"""
        try:
            self.ports = []
            
            # 尝试不同的端口枚举器
            for enumerator in self.port_enumerators:
                try:
                    ports = enumerator.enumerate_ports()
                    if ports:
                        self.ports = ports
                        print(f"使用 {enumerator.__class__.__name__} 找到串口: {ports}")
                        break
                except Exception as e:
                    print(f"{enumerator.__class__.__name__} 失败: {e}")
                    continue
            
            if not self.ports:
                print("未找到任何可用串口")
            
            self.port_list_updated.emit()
            return self.ports
            
        except Exception as e:
            error_msg = f"获取串口列表失败: {str(e)}"
            print(error_msg)
            self.connection_error.emit(error_msg)
            return []
    
    def set_port(self, port_name: str):
        """设置串口名称"""
        self.port_name = port_name
    
    def set_baudrate(self, baudrate: int):
        """设置波特率"""
        self.baudrate = baudrate
    
    def set_serial_params(self, **kwargs):
        """设置串口参数"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def open_serial(self) -> bool:
        """打开串口"""
        if not self.port_name:
            self.connection_error.emit("请选择一个串口")
            return False
        
        try:
            # 关闭已打开的串口
            if self.serial_port and self.serial_port.is_open():
                self.serial_port.close()
                time.sleep(0.1)
            
            # 检查串口是否存在
            available_ports = self.update_port_list()
            if self.port_name not in available_ports:
                self.connection_error.emit(f"串口 {self.port_name} 不存在或不可用")
                return False
            
            # 创建串口包装器
            serial_params = {
                'timeout': self.timeout,
                'write_timeout': 1.0,
                'inter_byte_timeout': None
            }
            
            # 添加可选参数
            if hasattr(self, 'databits'):
                serial_params['bytesize'] = self.databits
            if hasattr(self, 'parity'):
                parity_map = {
                    'none': PARITY_NONE,
                'even': PARITY_EVEN,
                'odd': PARITY_ODD,
                'mark': PARITY_MARK,
                'space': PARITY_SPACE
                }
                serial_params['parity'] = parity_map.get(self.parity.lower(), PARITY_NONE)
            
            if hasattr(self, 'stopbits'):
                stopbits_map = {
                    1: STOPBITS_ONE,
                    1.5: STOPBITS_ONE_POINT_FIVE,
                    2: STOPBITS_TWO
                }
                serial_params['stopbits'] = stopbits_map.get(self.stopbits, STOPBITS_ONE)
            
            # 流控制参数
            if hasattr(self, 'flowcontrol'):
                if self.flowcontrol.lower() == 'hardware':
                    serial_params['rtscts'] = True
                    serial_params['xonxoff'] = False
                elif self.flowcontrol.lower() == 'software':
                    serial_params['rtscts'] = False
                    serial_params['xonxoff'] = True
                else:
                    serial_params['rtscts'] = False
                    serial_params['xonxoff'] = False
            
            print(f"尝试打开串口: {self.port_name}, 波特率: {self.baudrate}")
            
            # 创建串口包装器
            self.serial_port = SerialPortWrapper(self.port_name, self.baudrate, **serial_params)
            
            # 重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if self.serial_port.open():
                        break
                    elif attempt < max_retries - 1:
                        print(f"第{attempt + 1}次尝试失败，等待后重试")
                        time.sleep(0.5)
                        continue
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"第{attempt + 1}次尝试失败: {e}")
                        time.sleep(0.5)
                        continue
                    else:
                        raise e
            
            if self.serial_port and self.serial_port.is_open():
                self.connected = True
                self.port_opened.emit()
                self.running = True
                self.start()
                print(f"串口 {self.port_name} 打开成功")
                return True
            else:
                self.connection_error.emit("串口打开失败")
                return False
                
        except Exception as e:
            error_msg = self._get_friendly_error_message(str(e))
            print(f"串口连接错误: {error_msg}")
            self.connection_error.emit(error_msg)
            return False
    
    def _get_friendly_error_message(self, error_str: str) -> str:
        """将系统错误转换为用户友好的错误信息"""
        if "信号灯超时" in error_str or "timeout" in error_str.lower():
            return "串口连接超时，可能是蓝牙设备连接不稳定"
        elif "拒绝访问" in error_str or "permission" in error_str.lower():
            return "串口被其他程序占用或需要管理员权限"
        elif "不存在" in error_str or "not exist" in error_str.lower():
            return "串口设备不存在或已断开连接"
        elif "正在使用" in error_str or "in use" in error_str.lower():
            return "串口正在被其他程序使用"
        else:
            return f"串口连接错误: {error_str}"
    
    def close_serial(self):
        """关闭串口"""
        self.running = False
        if self.serial_port and self.serial_port.is_open():
            self.serial_port.close()
        self.connected = False
        self.port_closed.emit()
    
    def run(self):
        """线程运行函数"""
        if not self.serial_port or not self.serial_port.is_open():
            return
        
        try:
            # 循环接收数据
            while self.running and self.serial_port.is_open():
                try:
                    if self.serial_port.in_waiting():
                        data = self.serial_port.read(self.serial_port.in_waiting())
                        if data:
                            # 发送原始数据信号
                            self.data_received.emit(data)
                            
                            # 解析数据
                            parsed_data_list = self.data_parser.parse_stream(data)
                            
                            # 处理解析后的数据
                            for parsed_data in parsed_data_list:
                                # 发送解析后的数据信号
                                self.parsed_data_received.emit(parsed_data)
                                
                                # 处理数据
                                processed_results = self.data_processor.process_data(parsed_data)
                                
                                # 这里可以发送处理后的数据信号
                                # self.processed_data_received.emit(processed_results)
                    
                    time.sleep(0.01)  # 短暂休眠避免CPU占用过高
                    
                except Exception as e:
                    self.connection_error.emit(f"读取错误: {str(e)}")
                    break
                    
        finally:
            if self.serial_port and self.serial_port.is_open():
                self.serial_port.close()
            self.connected = False
            self.port_closed.emit()
    
    def is_connected(self) -> bool:
        """检查串口是否连接"""
        return self.connected
    
    def get_port_name(self) -> str:
        """获取当前串口名称"""
        return self.port_name
    
    def get_baudrate(self) -> int:
        """获取当前波特率"""
        return self.baudrate
    
    def get_processed_data(self) -> Dict[str, Any]:
        """获取处理后的数据"""
        return self.data_processor.get_all_processed_data()
    
    def clear_data_buffers(self):
        """清空数据缓冲区"""
        self.data_processor.clear_all_buffers()
        self.data_parser.clear_buffer()
    
    def __del__(self):
        """析构函数，确保关闭串口"""
        try:
            if hasattr(self, 'serial_port') and self.serial_port and self.serial_port.is_open():
                self.serial_port.close()
            self.running = False
        except Exception:
            pass
