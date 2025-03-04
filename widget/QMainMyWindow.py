from PyQt5.QtWidgets import QMainWindow


class QMainMyWindow(QMainWindow):

    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        print('closeEvent')
