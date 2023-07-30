#!/usr/bin/env python3
import sys
#from PyQt5 import QtCore, QtWidgets
from PyQt5 import QtWidgets, Qwt
from PyQt5.QtCore import QTimer

from gui_meters import Ui_MeterDialog
import dcx_map as dcx

CHANNELS = ['A', 'B', 'C', '1', '2', '3', '4', '5', '6']

class Meters(QtWidgets.QDialog, Ui_MeterDialog):
    meters = []
    def __init__(self, *args, obj=None, **kwargs):
        super(Meters, self).__init__(*args, **kwargs)
        self.setupUi(self)
        dcx.port_connect()
        self.tick()
        self.toggle = True
        self.toggle_meters()

    def toggle_meters(self):
        if self.toggle:
            self.hide()
            self.timer.stop()
        else:
            self.show()
            self.timer.start(50)
        self.toggle = not self.toggle

    def read_meter(self):
        levels = dcx.get_live_levels()
        if levels:
            for index in range(0, 9):
                self.meter_input(CHANNELS[index], levels[index])

    def meter_input(self, channel, value):
        meter = getattr(self, 'Meter_' + channel)
        meter.setValue(value)
        #print('metersDCX.meter_input:', value)

    def tick(self):
        self.timer = QTimer()
        #self.timer.singleShot(100, self.read_meter)
        self.timer.timeout.connect(self.read_meter)
        self.timer.start(200)


class MeterUnit(QtWidgets.QFrame, Ui_MeterDialog):
    def __init__(self, *args, obj=None, **kwargs):
        super(MeterUnit, self).__init__(*args, **kwargs)
        self.setupUi(self)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Meters()
    window.show()
    app.exec()
    print('App Exited')
