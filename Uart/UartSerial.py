import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject
import time
from PyQt5.QtCore import pyqtSignal, QThread


# 参考 https://blog.csdn.net/windowsyun/article/details/80001488
# https://www.jb51.net/article/163876.htm PyQt5重写QComboBox的鼠标点击事件方法


class UartRecieveThread(QThread):

    def __init__(self, run):
        super(UartRecieveThread, self).__init__()
        self.runfun = run

    def run(self):
        self.runfun()


class UartSerial(QObject):
    # 定义一个信号变量，1个参数
    signalRecieve = pyqtSignal(object)
    # 信号接受， 信号断开
    CODE_RECIEVE, CODE_DISCONNECT = 0, 1

    def __init__(self):
        super(UartSerial, self).__init__()
        self.mThread = UartRecieveThread(self.data_receive)  # 创建线程
        self.mSerial = serial.Serial()
        self.data_num_received = 0

    def init(self, _port="/dev/ttyUSB0", _baudrate=57600, _bytesize=8, _stopbits="N", _parity=serial.PARITY_NONE):
        self.mSerial.port = _port
        self.mSerial.baudrate = _baudrate
        self.mSerial.bytesize = _bytesize
        self.mSerial.stopbits = _stopbits
        self.mSerial.parity = _parity
        self.data_num_received = 0

    def is_port_open(self, _port_name, _baudrate):
        try:
            self.mSerial.port = _port_name
            self.mSerial.baudrate = _baudrate
            return not self.mSerial.isOpen()
        except Exception:
            return False

    # 关闭串口
    def port_close(self, _port_name, _baudrate):
        self.mSerial.port = _port_name
        self.mSerial.baudrate = _baudrate
        try:
            self.mSerial.close()
        except:
            return False
        self.mThread.quit()
        return True

    # 串口检测
    def get_all_port(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.port_list_name = []
        port_list = list(serial.tools.list_ports.comports())
        i = 0

        if len(port_list) <= 0:
            return []
        else:
            for port in port_list:
                i = i + 1
                self.port_list_name.append(port[0])

        return self.port_list_name

    # 打开串口
    def try_port_open(self, _port, _baudrate=57600):
        self.mSerial.port = _port
        self.mSerial.baudrate = _baudrate
        try:
            self.mSerial.open()
        except:
            return False
        if not self.mThread.isRunning():
            self.mThread.start()
        return True

    def set_rts(self, IsTrue):
        self.mSerial.setRTS(IsTrue)

    def set_dts(self, IsTrue):
        self.mSerial.setDTR(IsTrue)

    def get_rts(self):
        return self.mSerial.rts

    def get_dts(self):
        return self.mSerial.dtr

    def set_bytesize(self, _bytesize):
        self.mSerial.bytesize = _bytesize

    def set_parity(self, _parity):
        self.mSerial.parity = _parity

    def set_stopbits(self, _stopbits):
        self.mSerial.stopbits = _stopbits

    # 接收数据
    def data_receive(self):
        while True:
            data = {}
            try:
                num = self.mSerial.inWaiting()
            except:
                self.mSerial.close()
                data['code'] = self.CODE_DISCONNECT
                data['data'] = 0
                data['length'] = 0
                self.signalRecieve.emit(data)
                return None
            if num > 0:
                if self.mSerial.isOpen():
                    buff = self.mSerial.read(num)
                    data['code'] = self.CODE_RECIEVE
                    data['data'] = buff
                    data['length'] = len(buff)
                    self.signalRecieve.emit(data)
            time.sleep(0.1)

    def setCallBack(self, funtion):
        self.signalRecieve.connect(funtion)




