#!/usr/bin/env python3

#import sys
#from PyQt5.QtWidgets import QApplication, QDialog
#from PyQt5 import QtCore, QtWidgets
#from gui_dcx import Ui_MainWindow
#app = QApplication(sys.argv)
#window = QtWidgets.QMainWindow()
#ui = Ui_MainWindow()
#ui.setupUi(window)
#window.show()
#sys.exit(app.exec_())


import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5 import QtCore, QtWidgets
from gui_eqUnit import Ui_EqFrame
app = QApplication(sys.argv)
window = QtWidgets.QFrame()
ui = Ui_EqFrame()
ui.setupUi(window)
window.show()
sys.exit(app.exec_())

