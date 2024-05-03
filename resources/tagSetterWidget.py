## New Tag name setter (Custom Widget)
import sys
from PyQt5 import QtCore, QtWidgets, uic
from tagSetterWidgetUI import Ui_Dialog

class tagSetterWidget(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        # uic.loadUi("tagSetterWidget.ui", self)

        # Show without borders
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # Set accpet / reject call
        self.acceptButton.clicked.connect(lambda x: self.accept())
        self.rejectButton.clicked.connect(lambda x: self.reject())


# Main
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = tagSetterWidget()
    widget.show()
    result = widget.exec_()