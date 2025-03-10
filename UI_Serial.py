# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_Serial.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Serial(object):
    def setupUi(self, Serial):
        Serial.setObjectName("Serial")
        Serial.resize(874, 890)
        self.centralwidget = QtWidgets.QWidget(Serial)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 841, 601))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.groupBox)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.textBrowserShow = QtWidgets.QTextBrowser(self.tab_1)
        self.textBrowserShow.setGeometry(QtCore.QRect(0, 0, 821, 531))
        self.textBrowserShow.setStyleSheet("font: 10pt \"Consolas\";")
        self.textBrowserShow.setObjectName("textBrowserShow")
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.tab_2)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 0, 801, 531))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.plot_table = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.plot_table.setContentsMargins(0, 0, 0, 0)
        self.plot_table.setObjectName("plot_table")
        self.tabWidget.addTab(self.tab_2, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 620, 191, 149))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_3)
        self.formLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.groupBox_3)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.comboBox_port = MyQComBox(self.groupBox_3)
        self.comboBox_port.setEnabled(True)
        self.comboBox_port.setEditable(False)
        self.comboBox_port.setObjectName("comboBox_port")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox_port)
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.comboBox_baud = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_baud.setEnabled(True)
        self.comboBox_baud.setEditable(True)
        self.comboBox_baud.setObjectName("comboBox_baud")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBox_baud)
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.comboBox_Bit = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_Bit.setObjectName("comboBox_Bit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comboBox_Bit)
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.comboBox_check = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_check.setObjectName("comboBox_check")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.comboBox_check)
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.comboBox_stop = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_stop.setObjectName("comboBox_stop")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.comboBox_stop)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(260, 620, 591, 151))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox_4)
        self.layoutWidget.setGeometry(QtCore.QRect(150, 0, 131, 121))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.btSaveLog = QtWidgets.QPushButton(self.layoutWidget)
        self.btSaveLog.setObjectName("btSaveLog")
        self.verticalLayout_2.addWidget(self.btSaveLog)
        self.btClearLog = QtWidgets.QPushButton(self.layoutWidget)
        self.btClearLog.setObjectName("btClearLog")
        self.verticalLayout_2.addWidget(self.btClearLog)
        self.layoutWidget1 = QtWidgets.QWidget(self.groupBox_4)
        self.layoutWidget1.setGeometry(QtCore.QRect(300, 0, 81, 121))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.checkBox_rts = QtWidgets.QCheckBox(self.layoutWidget1)
        self.checkBox_rts.setWhatsThis("")
        self.checkBox_rts.setChecked(False)
        self.checkBox_rts.setObjectName("checkBox_rts")
        self.verticalLayout_3.addWidget(self.checkBox_rts)
        self.checkBox_dtr = QtWidgets.QCheckBox(self.layoutWidget1)
        self.checkBox_dtr.setChecked(False)
        self.checkBox_dtr.setObjectName("checkBox_dtr")
        self.verticalLayout_3.addWidget(self.checkBox_dtr)
        self.layoutWidget2 = QtWidgets.QWidget(self.groupBox_4)
        self.layoutWidget2.setGeometry(QtCore.QRect(10, 0, 131, 121))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget2)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox_show_add_ctrl = QtWidgets.QCheckBox(self.layoutWidget2)
        self.checkBox_show_add_ctrl.setIconSize(QtCore.QSize(16, 16))
        self.checkBox_show_add_ctrl.setObjectName("checkBox_show_add_ctrl")
        self.verticalLayout.addWidget(self.checkBox_show_add_ctrl)
        self.checkBox_show_hex = QtWidgets.QCheckBox(self.layoutWidget2)
        self.checkBox_show_hex.setObjectName("checkBox_show_hex")
        self.verticalLayout.addWidget(self.checkBox_show_hex)
        self.layoutWidget3 = QtWidgets.QWidget(self.groupBox_4)
        self.layoutWidget3.setGeometry(QtCore.QRect(410, 10, 111, 111))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.layoutWidget3)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.bt_open_off_port = QtWidgets.QPushButton(self.layoutWidget3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bt_open_off_port.sizePolicy().hasHeightForWidth())
        self.bt_open_off_port.setSizePolicy(sizePolicy)
        self.bt_open_off_port.setObjectName("bt_open_off_port")
        self.verticalLayout_4.addWidget(self.bt_open_off_port)
        self.bt_checkout_run = QtWidgets.QPushButton(self.layoutWidget3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bt_checkout_run.sizePolicy().hasHeightForWidth())
        self.bt_checkout_run.setSizePolicy(sizePolicy)
        self.bt_checkout_run.setObjectName("bt_checkout_run")
        self.verticalLayout_4.addWidget(self.bt_checkout_run)
        Serial.setCentralWidget(self.centralwidget)

        self.retranslateUi(Serial)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Serial)

    def retranslateUi(self, Serial):
        _translate = QtCore.QCoreApplication.translate
        Serial.setWindowTitle(_translate("Serial", "MainWindow"))
        self.groupBox.setTitle(_translate("Serial", "接收区"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("Serial", "接收数据"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Serial", "图像曲线"))
        self.label.setText(_translate("Serial", "端口号"))
        self.label_2.setText(_translate("Serial", "波特率"))
        self.label_3.setText(_translate("Serial", "数据位"))
        self.label_4.setText(_translate("Serial", "校验位"))
        self.label_5.setText(_translate("Serial", "停止位"))
        self.btSaveLog.setText(_translate("Serial", "保存接收"))
        self.btClearLog.setText(_translate("Serial", "清空接收"))
        self.checkBox_rts.setText(_translate("Serial", "RTS"))
        self.checkBox_dtr.setText(_translate("Serial", "DTR"))
        self.checkBox_show_add_ctrl.setText(_translate("Serial", "自动换行"))
        self.checkBox_show_hex.setText(_translate("Serial", "HEX显示"))
        self.bt_open_off_port.setText(_translate("Serial", "打开串口"))
        self.bt_checkout_run.setText(_translate("Serial", "运行模式"))
from widget.MyQComBox import MyQComBox
