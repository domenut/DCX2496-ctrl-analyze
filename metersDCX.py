#!/usr/bin/env python3
import sys
from PyQt5 import QtCore, QtWidgets

from gui_meters import Ui_MeterDialog
import dcx_map as dcx

CHANNELS = ['A', 'B', 'C', '1', '2', '3', '4', '5', '6']

class Meters(QtWidgets.QDialog, Ui_MeterDialog):
    meters = []
    def __init__(self, *args, obj=None, **kwargs):
        super(Meters, self).__init__(*args, **kwargs)
        self.setupUi(self)
        dcx.port_connect()
        self.frame.hide()  # Hide the prototype meter
        self.generate_meters()
        self.setup_bar_colours()
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

    def generate_meters(self):
        for channel in CHANNELS:
            target_layout = getattr(self, 'meters_horizontalLayout')
            this_meter = MeterUnit(self)
            this_meter.setNames(channel)
            target_layout.addWidget(this_meter)
            widgets = this_meter.findChildren(QtWidgets.QProgressBar)
            for widget in widgets:
                name = widget.objectName()
                setattr(self, name, self.findChild(QtWidgets.QProgressBar, name))

    def read_meter(self):
        levels = dcx.get_live_levels()
        if levels:
            for index in range(0, 9):
                self.meter_input(CHANNELS[index], levels[index])
        #self.tick()

    def meter_input(self, channel, value):
        meter_1 = getattr(self, 'Meter_1_' + channel)
        meter_2 = getattr(self, 'Meter_2_' + channel)
        meter_3 = getattr(self, 'Meter_3_' + channel)
        meter_4 = getattr(self, 'Meter_4_' + channel)
        limit = getattr(self, 'Limit_' + channel)
        clip = getattr(self, 'Clip_' + channel)
        clip.setValue(value / 6)
        meter_1.setValue(bool(value))
        meter_2.setValue(int(value / 2))
        meter_3.setValue(int(value / 3))
        meter_4.setValue(int(value / 4))
        limit.setValue(int(value / 5))
        #print('metersDCX.meter_input:', value)

    def setup_bar_colours(self):
        for channel in CHANNELS:
            this_limit = getattr(self, 'Limit_' + channel)
            self.colour_bar_orange(this_limit)
            this_clip = getattr(self, 'Clip_' + channel)
            self.colour_bar_red(this_clip)

    def colour_bar_red(self, bar):
        bar.setStyleSheet("QProgressBar::chunk "
                        "{"
                            "background-color: red;"
                        "}")

    def colour_bar_orange(self, bar):
        bar.setStyleSheet("QProgressBar::chunk "
                        "{"
                            "background-color: orange;"
                        "}")

    def tick(self):
        self.timer = QtCore.QTimer()
        #self.timer.singleShot(100, self.read_meter)
        self.timer.timeout.connect(self.read_meter)
        self.timer.start(100)

class MeterUnit(QtWidgets.QFrame, Ui_MeterDialog):
    def __init__(self, *args, obj=None, **kwargs):
        super(MeterUnit, self).__init__(*args, **kwargs)
        self.setupUi(self)

    def setNames(self, channel='0'):
        widgets = self.findChildren(QtWidgets.QWidget)
        for widget in widgets:
            name = widget.objectName() + '_' + channel
            widget.setObjectName(name)
            self.label.setText(channel)
            setattr(self, name, self.findChild(QtWidgets.QProgressBar, name))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Meters()
    window.show()
    app.exec()
    print('App Exited')
