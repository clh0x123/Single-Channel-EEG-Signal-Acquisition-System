import os
import numpy as np

def remove_extension(file_path):
    """
    去除文件后缀名
    :param file_path:文件路径
    :return: 去除后缀后的文件路径
    """
    file_dir = os.path.dirname(file_path)  # 获取文件所在的目录路径
    file_name = os.path.basename(file_path)  # 获取文件名（包含后缀名）
    file_name_without_extension = os.path.splitext(file_name)[0]  # 去除后缀名
    return os.path.join(file_dir, file_name_without_extension)

def extract_rawdata(data_stream):
    """
    :param data_stream:接收到的串口数据流
    :return: 原始数据的ndarray
    """
    rawdata_list = []
    data_list = data_stream.split()  # 将数据流按空格分割为列表
    for i in range(len(data_list) - 6):  # 遍历数据流中的每个小数据包
        if data_list[i:i+4] == ['AA', '04', '80', '02']:
            xxHigh = int(data_list[i+4], 16)  # 将xxHigh转换为十进制数值
            xxLow = int(data_list[i+5], 16)  # 将xxLow转换为十进制数值
            xxCheckSum = int(data_list[i+6], 16)  # 将xxCheckSum转换为十进制数值
            checksum = ((0x80 + 0x02 + xxHigh + xxLow) ^ 0xFFFFFFFF) & 0xFF  # 计算校验和
            if xxCheckSum == checksum:  # 校验和正确
                rawdata = (xxHigh << 8) | xxLow  # 计算rawdata
                if rawdata > 32768:
                    rawdata -= 65536
                rawdata_list.append(rawdata)  # 将rawdata添加到列表中
    return np.array(rawdata_list)