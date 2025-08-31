import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from views.main_window import MainWindow
from PyQt5.QtGui import QIcon


def main():
    """主函数"""
    # 设置高DPI相关环境变量
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"
    
    # 启用高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("brain.ico"))
    app.setApplicationName("单通道EEG信号采集系统")
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()