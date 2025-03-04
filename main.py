from PyQt5.QtGui import QIcon, QTextCursor
from esp_at.AT import AT
from datetime import datetime
from UI_Serial import Ui_Serial
import time
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from utils.data_creator import Data_Creator
from utils.util import extract_rawdata
import pyqtgraph as pg
from pyqtgraph import DateAxisItem
import codecs
import numpy as np

DEFAULT_BAUD_ARRAY = ('4800', '74880', '9600', '57600', '115200', '576000', '921600',)
GET_PORT_ARRAY = []
# 串口输出数据（定义全局变量）
data = []


class Pyqt5_Serial(QMainWindow, Ui_Serial):
    """继承QMainWindow，Ui_Serial两个类，并调用AT类 """
    def __init__(self):
        super().__init__()
        # 设置ui
        self.setupUi(self)
        # 调用AT类
        self.mATObj = AT()
        # 初始化
        self.init()
        # 初始化绘图界面
        self.init_plot_table()
        # 初始化接收数据
        self.data = np.full(1, None)
        # 设定定时器
        self.timer = pg.QtCore.QTimer()
        # 定时器信号绑定 update_plot 函数
        self.timer.timeout.connect(self.update_plot)
        # 定时器间隔500ms
        self.timer.start(500)

    def init(self):
        """初始化"""
        self.comboBox_baud.clear()
        # for item in DEFAULT_BAUD_ARRAY:
        self.comboBox_baud.addItems(DEFAULT_BAUD_ARRAY)
        self.comboBox_baud.setCurrentIndex(3)
        # 数据位
        self.comboBox_Bit.addItem('8')
        self.comboBox_Bit.addItem('7')
        self.comboBox_Bit.addItem('6')
        self.comboBox_Bit.addItem('5')

        # 停止位
        self.comboBox_stop.addItem('1')
        self.comboBox_stop.addItem('1.5')
        self.comboBox_stop.addItem('2')

        # 校验位 'N', 'E', 'O', 'M', 'S'
        self.comboBox_check.addItem('N')
        self.comboBox_check.addItem('O')
        self.comboBox_check.addItem('M')
        self.comboBox_check.addItem('E')
        self.comboBox_check.addItem('S')

        self.mATObj.set_dts(False)
        self.mATObj.set_rts(False)
        self.textBrowserShow.setStyleSheet("font: 11pt \"Consolas\";")
        self.refreshPort()
        # 点击按钮，打开串口
        self.bt_open_off_port.clicked.connect(self.onClickOpenOffPort)
        # 点击按钮，刷新串口
        self.comboBox_port.popupAboutToBeShown.connect(self.refreshPort)
        #  rts
        self.checkBox_rts.stateChanged.connect(self.OnClickRTS)
        #  dts
        self.checkBox_dtr.stateChanged.connect(self.OnClickDTR)
        #  Clear Log
        self.btClearLog.clicked.connect(self.OnClickClearLog)
        # save Log
        self.btSaveLog.clicked.connect(self.OnClickSaveLog)
        # 运行模式
        self.bt_checkout_run.clicked.connect(self.OnClickCheckOutRun)
        # 面板可操作
        self.checkoutPortStatus(True)

    def init_plot_table(self):
        """初始化绘图界面"""
        pg.setConfigOptions(leftButtonPan=True, antialias=True)
        pg.setConfigOption('background', 'w')  # 初始的背景(白)
        # 添加 PlotWidget 控件
        self.pw = pg.PlotWidget()
        # 设置标题
        self.pw.setTitle("脑电图信号", color='k', size='12pt')
        # 设置该控件尺寸和相对位置
        self.pw.setGeometry(QtCore.QRect(25, 25, 550, 550))
        # 设置网格
        self.pw.showGrid(x=True, y=True)
        # 设置上下左右的label
        self.pw.setYRange(-15, 20, padding=0)

        # 创建一个DateAxisItem对象作为x轴
        axis = DateAxisItem()
        # 设置x轴的位置为y=0的位置
        axis.setPos(0, 0)

        # 将x轴设置为绘图区域的底部轴
        self.pw.setAxisItems({'bottom': axis})

        self.plot_item = self.pw.getPlotItem()
        self.curve = self.plot_item.plot(pen=pg.mkPen('b', width=2))
        self.plot_table.addWidget(self.pw)

    def update_plot(self):
        """更新绘图界面，若没有串口信号，则绘制y=0的直线"""
        self.curve.getViewBox().enableAutoRange()
        self.curve.getViewBox().setAutoVisible()
        if self.data.any() == None:
            self.data = np.zeros(30)
            self.data[:-1] = self.data[1:]
        self.curve.setData(self.data)

    def OnClickCheckOutRun(self):
        """运行模式"""
        self.mATObj.set_rts(True)
        self.mATObj.set_dts(False)

        time.sleep(0.1)
        self.mATObj.set_dts(True)
        self.checkBox_rts.setChecked(True)
        self.checkBox_dtr.setChecked(True)

    def OnClickClearLog(self):
        """清空数据接收界面"""
        self.textBrowserShow.clear()

    def OnClickSaveLog(self):
        """保存数据"""
        global data

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(None, "保存文件", "", "dat Files (*.dat)")  # 弹出文件保存对话框

        if file_path:  # 如果选择了保存路径
            # 创建EEG数据结构
            eeg_data = np.concatenate(data)

            DC = Data_Creator(file_path, len(eeg_data))
            DC.create_dat(eeg_data)
            DC.create_txt(eeg_data)

    def OnClickRTS(self, state):
        """RTS流控"""
        if state == QtCore.Qt.Unchecked:
            self.mATObj.set_rts(False)
        elif state == QtCore.Qt.Checked:
            self.mATObj.set_rts(True)

    def OnClickDTR(self, state):
        """DTR流控"""
        if state == QtCore.Qt.Unchecked:
            self.mATObj.set_dts(False)
        elif state == QtCore.Qt.Checked:
            self.mATObj.set_dts(True)

    def refreshPort(self):
        """刷新串口"""
        _ports = self.mATObj.initPort()
        # print(_ports)
        self.comboBox_port.clear()
        GET_PORT_ARRAY.clear()
        if len(_ports) == 0:
            self.comboBox_port.addItem('')
        else:
            for item in _ports:
                self.comboBox_port.addItem(item)
                GET_PORT_ARRAY.append(item)


    def onClickOpenOffPort(self):
        """打开/关闭串口"""
        if len(GET_PORT_ARRAY) == 0:
            QMessageBox.critical(self, '错误信息', '请选择串口')
        else:
            baud = DEFAULT_BAUD_ARRAY[self.comboBox_baud.currentIndex()]
            port = GET_PORT_ARRAY[self.comboBox_port.currentIndex()]
            str = self.bt_open_off_port.text()
            bitIndex = self.comboBox_Bit.currentText()
            if str == '关闭串口':
                if self.mATObj.try_off_port(port, baud):
                    # 设置打开串口参数
                    self.mATObj.set_default_parity(self.comboBox_check.currentText())
                    self.mATObj.set_default_stopbits(float(self.comboBox_stop.currentText()))
                    self.mATObj.set_default_port(port)
                    self.mATObj.set_default_bytesize(int(bitIndex))
                    self.mATObj.set_default_baudrate(baud)
                    self.bt_open_off_port.setText('打开串口')
                    self.checkoutPortStatus(True)
                else:
                    QMessageBox.critical(self, '错误信息', '串口被占用或已拔开，无法打开')
            if str == '打开串口':
                if self.mATObj.try_open_port(port, baud):
                    self.checkoutPortStatus(False)
                    self.bt_open_off_port.setText('关闭串口')
                else:
                    QMessageBox.critical(self, '错误信息', '串口被占用或已拔开，无法打开')

    def checkoutPortStatus(self, isShow):
        """检查串口状态"""
        self.comboBox_baud.setEnabled(isShow)
        self.comboBox_Bit.setEnabled(isShow)
        self.comboBox_check.setEnabled(isShow)
        self.comboBox_stop.setEnabled(isShow)
        self.comboBox_port.setEnabled(isShow)

    def closeEvent(self, event):
        """关闭ui窗口"""
        print('closeEvent')

def xh_utf8_error_handler(err):
    start = err.start
    end = err.end
    return ("".join(["<%02X>"% err.object[i] for i in range(start,end)]),end)

codecs.register_error('xh_replace', xh_utf8_error_handler)


def at_callback_handler(obj):
    """
    当接受到串口信号时将调用此函数
    :param obj: 串口信号
    :return:
    """
    global data
    if obj['code'] == 1:
        if ui.bt_open_off_port.text() != '打开串口':
            QMessageBox.critical(ui, '错误信息', '串口异常断开！')
            # 面板可操作
            ui.checkoutPortStatus(True)
            ui.bt_open_off_port.setText('打开串口')
            ui.refreshPort()
    else:
        data = []
        buff = (obj['data'])
        now_time = datetime.now()  # 获取当前时间
        new_time = now_time.strftime('[%H:%M:%S]:')  # 打印需要的信息,依次是年月日,时分秒,注意字母大小写
        if ui.checkBox_show_hex.checkState():
            out_s = ''
            for i in range(0, len(buff)):
                out_s = out_s + '{:02X}'.format(buff[i]) + ' '
            raw_data = extract_rawdata(out_s)
            data.append(raw_data)
            ui.data = raw_data
            if ui.checkBox_show_add_ctrl.checkState():
                ui.textBrowserShow.append(new_time + out_s)
            else:
                ui.textBrowserShow.insertPlainText(out_s)
            ui.textBrowserShow.moveCursor(QTextCursor.End)

        else:
            try:
                if ui.checkBox_show_add_ctrl.checkState():
                    ui.textBrowserShow.append(new_time + buff.decode('utf-8', errors='xh_replace'))
                else:
                    ui.textBrowserShow.insertPlainText(buff.decode('utf-8', errors='xh_replace'))
                ui.textBrowserShow.moveCursor(QTextCursor.End)
            except:
                # 乱码显示
                pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("brain.ico"))
    ui = Pyqt5_Serial()

    # 禁止拉伸窗口大小
    # MainWindow.setFixedSize(MainWindow.width(), MainWindow.height())
    # # !!!修复DesignerQT5自定义QWidget时候，window不会设置调用setCentralWidget设置在中心
    ui.setCentralWidget(ui.centralwidget)
    # # 设置电脑键盘回调
    dk = app.desktop()

    # 设置回调函数
    ui.mATObj.set_default_at_result_callBack(at_callback_handler)

    # 居中显示
    ui.move((int)(dk.width() / 2 - ui.width() / 2), (int)(dk.height() / 2 - ui.height() / 2))
    _translate = QtCore.QCoreApplication.translate
    ui.setWindowTitle(_translate("Serial", "串口调试助手"))
    ui.show()
    ui.refreshPort()

    sys.exit(app.exec_())
