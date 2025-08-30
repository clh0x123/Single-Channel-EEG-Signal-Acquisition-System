import random
import time
import threading

class TGAMSimulator:
    
    def __init__(self, port="COM2", baudrate=57600, serial_manager=None):
        """
        TGAM 模拟器
        :param port: 串口名称（当不提供serial_manager时使用）
        :param baudrate: TGAM 默认波特率 57600
        :param serial_manager: 已存在的SerialManager实例，用于共享串口连接
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.raw_counter = 0
        self.running = False
        self.thread = None
        self.serial_manager = serial_manager  # 共享的串口管理器

    def _checksum(self, data_bytes):
        """计算校验和 (sum of payload, 取反, 取低8位)"""
        return (~sum(data_bytes)) & 0xFF

    def generate_raw_packet(self):
        """生成一个小包 (raw data)"""
        raw_value = random.randint(-2048, 2047)  # 模拟脑电原始数据
        if raw_value < 0:
            raw_value = 65536 + raw_value
        xxHigh = (raw_value >> 8) & 0xFF
        xxLow = raw_value & 0xFF

        # 正确的payload格式：数据类型 + 数据
        payload = [0x80, xxHigh, xxLow]
        payload_len = len(payload)
        checksum = self._checksum(payload)
        packet = bytes([0xAA, 0xAA, payload_len] + payload + [checksum])
        return packet

    def generate_big_packet(self):
        """生成一个大包 (Signal + EEG Power + Attention + Meditation)"""
        signal = random.randint(0, 200)  # 信号强度
        attention = random.randint(0, 100)
        meditation = random.randint(0, 100)

        # EEG Power 8 组，每组 3 字节 (24 bytes)
        eeg_power = []
        for _ in range(8):
            val = random.randint(1000, 100000)
            eeg_power += [(val >> 16) & 0xFF, (val >> 8) & 0xFF, val & 0xFF]

        payload = []
        payload += [0x02, signal]  # Signal
        payload += [0x83, 24] + eeg_power  # EEG Power
        payload += [0x04, attention]  # Attention
        payload += [0x05, meditation]  # Meditation

        payload_len = len(payload)
        header = [0xAA, 0xAA, payload_len]
        checksum = self._checksum(payload)
        packet = bytes(header + payload + [checksum])
        return packet

    def _stream_loop(self):
        """数据流循环，在单独线程中运行"""
        try:
            while self.running:
                    if not self.ser or not self.ser.is_open:
                        break
                     
                    # 确保串口参数已设置
                    if not hasattr(self.ser, 'port') or not self.ser.port:
                        print("错误: 串口参数未设置")
                        break
                     
                    # 输出 512 个小包
                    for _ in range(512):
                        if not self.running or not self.ser or not self.ser.is_open:
                            break
                        raw_packet = self.generate_raw_packet()
                        if self.serial_manager and self.serial_manager.serial_port:
                            self.serial_manager.serial_port.write(raw_packet)
                        else:
                            self.ser.write(raw_packet)
                        time.sleep(1/512)  # 控制频率 ~512Hz
                     
                    if not self.running or not self.ser or not self.ser.is_open:
                        break
                          
                    # 输出一个大包
                    big_packet = self.generate_big_packet()
                    if self.serial_manager and self.serial_manager.serial_port:
                        self.serial_manager.serial_port.write(big_packet)
                    else:
                        self.ser.write(big_packet)
                    # 给下游解析留一点时间
                    time.sleep(0.01)
        except Exception as e:
            print(f"数据流错误: {e}")
        finally:
            self.close()

    def start(self):
        """启动模拟数据流"""
        if self.running:
            return False

        try:
            # 实际串口模式
                try:
                    if self.serial_manager and self.serial_manager.is_connected():
                        # 使用共享的串口管理器
                        self.ser = self.serial_manager.serial_port
                        # 确保端口参数已设置
                        self.ser.port = self.serial_manager.port_name
                        print(f"使用共享串口连接: {self.serial_manager.port_name}")
                    else:
                        # 回退到自己打开串口
                        print(f"没有共享串口连接，尝试自己打开: {self.port}")
                        import serial
                        self.ser = serial.Serial()
                        self.ser.port = self.port
                        self.ser.baudrate = self.baudrate
                        self.ser.timeout = 1
                        self.ser.open()
                        
                        if not self.ser.is_open:
                            return False

                    self.running = True
                    # 创建并启动线程
                    self.thread = threading.Thread(target=self._stream_loop)
                    self.thread.daemon = True
                    self.thread.start()
                    return True
                except Exception as e:
                    error_msg = f"启动失败: {e}"
                    print(error_msg)
                    # 提供更友好的错误提示
                    if "PermissionError" in str(e) or "拒绝访问" in str(e):
                        print(f"请确认端口 {self.port} 未被其他程序占用，或尝试使用虚拟模式")
                    self.close()
                    return False
        except Exception as e:
            print(f"启动失败: {e}")
            self.close()
            return False

    def stop(self):
        """停止模拟数据流"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.close()
        return True

    def close(self):
        """关闭串口"""
        # 如果使用的是共享的串口管理器，不要关闭串口
        if self.ser and self.ser.is_open and not self.serial_manager:
            try:
                self.ser.close()
            except Exception as e:
                print(f"关闭串口错误: {e}")
        self.ser = None

if __name__ == "__main__":
    sim = TGAMSimulator(port="COM1", baudrate=57600)
    print("TGAM 模拟数据流开始发送...")
    sim.start()
    try:
        # 运行100秒后停止
        time.sleep(100)
    except KeyboardInterrupt:
        print("用户中断")
    finally:
        sim.stop()
        print("发送结束")
