from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QAbstractListModel
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QApplication, QDial, QMainWindow
from  SMCControl import SMCCmd
import rooms
from PySide6.QtUiTools import QUiLoader
from tools.iLog import ilog
import sys,os

from enum import Enum
from SMCControl import SMCCmd

basedir = os.path.dirname(__file__)
loader = QUiLoader()
log=ilog('smc.log','smc').get_logger()



try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class ConfControl(Enum):
    VIEW=0
    BROAD=1
    ROLL=2
    MUTE=3
    UNMUTE=4




class MeetingRoom(QAbstractListModel):
    def __init__(self, rooms=None):
        super().__init__()
        self.rooms = rooms or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.rooms[index.row()]['name']
            return text



    def rowCount(self, index):
        return len(self.rooms)



class MainUI(QtCore.QObject):
    def __init__(self):
        super().__init__()

        self.ui = loader.load(
        os.path.join(basedir, "junjuncontrol.ui"), None
    )
        self.ui.setWindowTitle("君君会控")

        self.model=MeetingRoom(rooms.rooms)
        self.ui.participants.setModel(self.model)
        self.confControl=None
        self.viewMute=True
        self.broadMute=True

        self.smc=SMCCmd()


        self.ui.participants.clicked.connect(self.get_participants_id)

        self.ui.viewMute.clicked.connect(lambda x:self.mute_operating(x,ConfControl.VIEW))
        self.ui.broadMute.clicked.connect(lambda x:self.mute_operating(x,ConfControl.BROAD))

        self.ui.viewparticipants.clicked.connect(lambda x:self.conf_oprating(ConfControl.VIEW))
        self.ui.spokesman.clicked.connect(lambda x:self.conf_oprating(ConfControl.ROLL))
        self.ui.broadcaster.clicked.connect(lambda x:self.conf_oprating(ConfControl.BROAD))


        self.ui.show()


    def distribute_cmd(self):
        participant_id=self.get_participants_id()
        if self.confControl==ConfControl.BROAD:
            self.broadMute
            pass
        elif self.confControl==ConfControl.VIEW:
            self.viewMute
            pass
        elif self.confControl==ConfControl.ROLL:
            pass




    def conf_oprating(self,ctl):

        if ctl==ConfControl.ROLL:
            self.confControl=ConfControl.ROLL
        elif ctl==ConfControl.VIEW:
            self.confControl=ConfControl.VIEW
        elif ctl==ConfControl.BROAD:
            self.confControl=ConfControl.BROAD

        log.info(f'conf_oprating:{self.confControl}')

    def mute_operating(self,x,ctl):
        if ctl == ConfControl.VIEW:
            self.viewMute =x
        elif ctl == ConfControl.BROAD:
            self.broadMute = x

        log.info(f'{ctl}:{x}')






    def get_participants_id(self):
        indexes = self.ui.participants.selectedIndexes()

        if indexes:
            index = indexes[0]
            row = index.row()
            return self.model.rooms[row]['id']




def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = MainUI()
    app.exec()

if __name__=='__main__':
    main()