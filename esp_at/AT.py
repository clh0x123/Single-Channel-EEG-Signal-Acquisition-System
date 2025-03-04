import os
import sys
import serial
from Uart.UartSerial import UartSerial
from PyQt5.QtCore import pyqtSignal, QThread
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))


class AT(QThread):
    # 定义一个信号变量，1个参数
    signalParseCMD = pyqtSignal(object)
    def __init__(self, _baudrate=57600, _port="/dev/ttyUSB0", _bytesize=8, _stopbits="N", _parity=serial.PARITY_NONE):
        super(AT, self).__init__()
        # 调用UartSerial对象
        self.uartObj = UartSerial()
        # 串口设备地址
        self.port = _port
        # 波特率
        self.baudrate = _baudrate
        # 字节大小
        self.bytesize = _bytesize
        # 停止位
        self.stopbits = _stopbits
        # 校验位
        self.parity = _parity
        # 回调函数
        self.uartObj.setCallBack(self.getUartData)

    def initPort(self):
        """用于获取所有可用的串口端口。"""
        return self.uartObj.get_all_port()

    def try_off_port(self, _port, baud):
        """
        关闭指定端口
        :param _port: 串口
        :param baud: 波特率
        :return: True/False
        """
        return self.uartObj.port_close(_port, baud)

    def try_open_port(self, _port, baud):
        """
        用于尝试打开指定端口和波特率的串口
        :param _port: 串口
        :param baud: 波特率
        :return: True/False
        """
        return self.uartObj.try_port_open(_port, baud)

    def is_port_busy(self, _port):
        """
        用于判断指定端口是否处于打开状态
        :param _port:串口
        :return: True/False
        """
        return self.uartObj.is_port_open(_port, 9600)

    def set_rts(self, IsTrue):
        """设置RTS"""
        return self.uartObj.set_rts(IsTrue)

    def set_dts(self, IsTrue):
        """设置DTR"""
        return self.uartObj.set_dts(IsTrue)

    def get_rts(self):
        """获取RTS信号"""
        return self.uartObj.get_rts()

    def get_dts(self):
        """获取DTR信号"""
        return self.uartObj.get_dts()

    def getUartData(self, obj):
        """回调函数，用于接收串口数据。在该函数中，通过判断接收到的数据是否为特定代码，来确定是否发送信号。"""
        # if obj['code'] == self.uartObj.CODE_RECIEVE:
        #     print("length:", obj['length'])
        #     print("data:", obj['data'])
        obj['des'] = '【模块-->MCU】 设置模块为 station 模式成功'
        self.signalParseCMD.emit(obj)

    def set_default_port(self, _port):
        """设置默认串口"""
        self.port = _port

    def set_default_baudrate(self, _baudrate):
        """设置默认波特率"""
        self.baudrate = _baudrate

    def set_default_parity(self, _parity):
        """设置默认校验位"""
        self.parity = _parity
        self.uartObj.set_parity(_parity)

    def set_default_bytesize(self, _bytesize):
        """设置默认字节大小"""
        self.bytesize = _bytesize
        self.uartObj.set_bytesize(_bytesize)

    def set_default_stopbits(self, _stopbits):
        """设置默认停止位"""
        self.stopbits = _stopbits
        self.uartObj.set_stopbits(_stopbits)

    def set_default_at_result_callBack(self, funtion):
        """设置接收数据的回调函数，将信号 signalRecieve 连接到指定的函数上。"""
        self.signalParseCMD.connect(funtion)
