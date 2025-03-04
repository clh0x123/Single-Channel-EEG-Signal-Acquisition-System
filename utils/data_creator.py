import random
import os

import numpy as np

from utils.util import remove_extension
from datetime import datetime


class Data_Creator:
    def __init__(self, file_name, len_data, num_channel=1):
        self.file_path = remove_extension(file_name)
        self.len_data = len_data
        self.file_name = os.path.basename(self.file_path)
        self.num_channel = num_channel
        self.channel_names = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2',
                 'F7', 'F8', 'T7', 'T8', 'P7', 'P8', 'Fz', 'Cz', 'Pz', 'FC1',
                 'FC2', 'CP1', 'CP2', 'FC5', 'FC6', 'CP5', 'CP6', 'TP9', 'TP10',
                 'Eog', 'Ekg1', 'Ekg2']

    def create_dat(self, data):
        """
        :param data: 原始数据
        :return: 保存.dat文件
        """
        data.tofile(self.file_path + '.dat')
        print("生成.dat文件成功！")

    def create_txt(self, data):
        """
        :param data: 原始数据
        :return: 保存.txt文件
        """
        np.savetxt(self.file_path + '.txt', data, fmt='%.2f')
        print("生成.txt文件成功！")

    def create_vmrk(self, num_markers=17):
        """
        :param num_markers: markers数量
        :return: 保存.vmrk文件
        """
        with open(self.file_path + '.vmrk', 'w') as file:
            file.write("Brain Vision Data Exchange Marker File, Version 1.0\n")
            file.write("; Data created from history path: BrainVision_Dataformat_01/Raw Data\n")
            file.write("; The channel numbers are related to the channels in the exported file.\n\n")
            file.write("[Common Infos]\n")
            file.write(f"DataFile={self.file_name}.dat\n\n")
            file.write("[Marker Infos]\n")
            file.write("; Each entry: Mk<Marker number>=<Type>,<Description>,<Position in data points>,\n")
            file.write("; <Size in data points>, <Channel number (0 = marker is related to all channels)>,\n")
            file.write("; <Date (YYYYMMDDhhmmssuuuuuu)>\n")
            file.write("; Fields are delimited by commas, some fields might be omitted (empty).\n")
            file.write("; Commas in type or description text are coded as \"\\1\".\n")

            for i in range(1, num_markers + 1):
                position = random.randint(1, 2048)  # 随机选择位置（1-2048之间）
                size = 1  # 固定大小为1
                channel_number = 0  # 固定通道为0
                # 获取当前时间
                current_time = datetime.now()
                date = current_time.strftime("%Y%m%d%H%M%S")

                if i == 1:
                    marker_type = "New Segment"
                    file.write(f"Mk{i}={marker_type},,1,1,0,{date}\n")
                else:
                    marker_type = "Stimulus"
                    description = f"S  {random.randint(1, 4)}"  # 随机选择描述
                    file.write(f"Mk{i}={marker_type},{description},{position},{size},{channel_number}\n")

        print("生成.vmrk文件成功！")

    def create_vhdr(self):
        """
        :return: 生成vhdr文件
        """
        random.shuffle(self.channel_names)

        # 生成随机的Coordinates
        coordinates = []
        for i in range(1, self.num_channel+1):
            radius = random.randint(0, 1)
            theta = random.randint(-180, 180)
            phi = random.randint(-90, 90)
            coordinates.append(f"Ch{i}={radius},{theta},{phi}")

        # 生成随机的.vhdr文件内容
        vhdr_content = [
            "Brain Vision Data Exchange Header File Version 1.0",
            "; Data created from history path: BrainVision_Dataformat_01/Raw Data",
            "",
            "[Common Infos]",
            f"DataFile={self.file_name}.dat",
            f"MarkerFile={self.file_name}.vmrk",
            "DataFormat=BINARY",
            "; Data orientation: VECTORIZED=ch1,pt1, ch1,pt2..., MULTIPLEXED=ch1,pt1, ch2,pt1 ...",
            "DataOrientation=MULTIPLEXED",
            "DataType=TIMEDOMAIN",
            f"NumberOfChannels={self.num_channel}",
            f"DataPoints={self.len_data}",
            "; Sampling interval in microseconds if time domain (convert to Hertz:",
            "; 1000000 / SamplingInterval) or in Hertz if frequency domain:",
            "SamplingInterval=5000",
            "",
            "[Binary Infos]",
            "BinaryFormat=IEEE_FLOAT_32",
            "",
            "[Channel Infos]",
            "; Each entry: Ch<Channel number>=<Name>,<Reference channel name>,",
            "; <Resolution in microvolts>,<Future extensions..",
            "; Fields are delimited by commas, some fields might be omitted (empty).",
            "; Commas in channel names are coded as \"\\1\"."
        ]

        # 添加随机生成的Channel信息
        for i, channel_name in enumerate(self.channel_names[:self.num_channel]):
            vhdr_content.append(f"Ch{i + 1}={channel_name},,")

        # 添加Coordinates信息
        vhdr_content.append("\n[Coordinates]")
        for coordinate in coordinates:
            vhdr_content.append(coordinate)

        # 将生成的内容写入.vhdr文件
        with open(self.file_path + '.vhdr', 'w') as file:
            for line in vhdr_content:
                file.write(line + "\n")
        print("生成.vhdr文件成功！")
