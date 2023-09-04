from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QApplication, QDial, QMainWindow
from  SMCControl import SMCCmd

from PySide6.QtUiTools import QUiLoader

import sys,os

basedir = os.path.dirname(__file__)
loader = QUiLoader()

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class MainUI(QtCore.QObject):
    def __init__(self):
        super().__init__()

        self.ui = loader.load(
        os.path.join(basedir, "junjuncontrol.ui"), None
    )
        self.ui.setWindowTitle("君君会控")
        self.ui.show()






def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = MainUI()
    app.exec()

if __name__=='__main__':
    main()