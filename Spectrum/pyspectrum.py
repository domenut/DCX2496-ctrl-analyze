#!/usr/bin/env python3

import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import struct


import threading

#from scipy.fftpack import fft
import sys
import os
import subprocess
import time

np.set_printoptions(threshold=sys.maxsize, precision=2, suppress=True)

ShowWindow = True
fifo_name = './spectrum_data.fifo'


app = pg.mkQApp("CMD-PLOT©")
win = pg.GraphicsLayoutWidget(show=ShowWindow, title="Basic plotting examples")
win.resize(620, 580)
win.setWindowTitle('CMDPLOT ! ©/™/®')
pg.setConfigOptions(antialias=True)
#app.sigMouseClicked.connect(mouse_clicked)
#win.clickAccepted

p0 = win.addPlot(title="Time series")
p0.setLogMode(x=None, y=None)
p0.showGrid(x=True, y=True, alpha=0.5)
p0.enableAutoRange('xy', False)
curve_chA = p0.plot(pen='g')
curve_chA.setAlpha(0.6, False)
#curve_chA.setFftMode(True)
win.nextRow()

p0.hide()

p1 = win.addPlot(title="Frquency bins")
# p1.setLogMode(x=True, y=True)
p1.setLogMode(x=True, y=None)
p1.showGrid(x=True, y=True, alpha=10)
# p1.enableAutoRange('xy', False)
curve_sig = p1.plot( pen='g')
curve_sig.setAlpha(0.6, False)
curve_ref = p1.plot(pen='y')
curve_ref.setAlpha(0.2, False)


class Crosshair():
    def __init__(self, pw, domain):
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        pw.addItem(self.vLine, ignoreBounds=True)
        pw.addItem(self.hLine, ignoreBounds=True)

        self.vb = pw.vb
        self.domain = domain

        self.label = pg.TextItem()
        self.vb.addItem(self.label)
        self.label.setPos( 0.5, 0.5 )

        self.proxy = pg.SignalProxy(pw.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.pw = pw

    def mouseMoved(self, evt):
        pos = evt[0]
        vr = self.pw.viewRect()
        mousePoint = self.vb.mapSceneToView(pos)
        self.vLine.setPos(mousePoint.x())
        self.hLine.setPos(mousePoint.y())
        self.label.setPos(  (vr.x()+(vr.width()*0.7)) , (vr.y()+(vr.height()*1))  )

        if( self.domain == 'freq' ):
            self.pw.enableAutoRange('xy', False)
            self.label.setHtml(
                        "<span style='font-size: 11pt'>{:0.1f}Hz  '\
                        <span style='color: yellow'>{:0.1f}db</span>".format(
                    10**mousePoint.x(), mousePoint.y()))
        elif( self.domain == 'time' ):
            self.label.setHtml(
                        "<span style='font-size: 11pt'>{:0.1f}  '\
                        <span style='color: yellow'>{:0.1f}</span>".format(
                    10**mousePoint.x(), mousePoint.y()))


# crosshair0 = Crosshair(p0, 'time')
crosshair1 = Crosshair(p1, 'freq')

toggle = 1
def mouseClicked():
    global toggle
    if (toggle):
        p0.hide()
        toggle = 0
    else:
        p0.show()
        toggle = 1

    print('clicked plot 0x')
    #exit()
    #print('clicked plot 0x{:x}, event: {}'.format(id(self), mouseClickEvent))

p1.scene().sigMouseClicked.connect(mouseClicked)

def messageSubprocess(message):
    fdo = open(fifo_name, 'w')
    fdo.write(message)
    fdo.close()

ptr = 0
lt = 0.0
data_ready = 0

def get_data():
    global data_collected, ptr, lt, data_ready
    # ptr += 1
    try:
        data_collected = np.loadtxt(fifo_name, delimiter=',', dtype=float)
        data_ready = 1;
        # print(data_collected[1:,1:2])
        # print(ptr, time.time() - lt)
        # lt = time.time()

    except:
        print("data_collected error")
        print("data_collected error")


timer = QtCore.QTimer()
def update():
    global curve_sig, data, ptr, p1, curve_ref, p0, data_collected, data_ready
    # ptr = ptr + 1

    if(data_ready):
    # if(1):
        data_ready = 0
        try:
            curve_sig.setData(data_collected[0:,0], data_collected[0:,1])
            curve_ref.setData(data_collected[0:,0], data_collected[0:,2])
            # curve_chA.setData(data_collected[0:,0], data_collected[0:,3])
            curve_chA.setData(y = data_collected[0:,3])
            # p1.enableAutoRange('xy', False)

        except:
            print("Update: No Data?")
            time.sleep(0.1)
    else:
        pass
        # print("Waiting for data...")

    # if ptr > 10:
        # timer.stop()
        # pg.exit()
        # print('Exceded')
        # pass
#            p1.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted


def start_data_loop():
    while(True):
        time.sleep(0.01)
        get_data()

data_thread = threading.Thread(target=start_data_loop)
data_thread.start()


timer.timeout.connect(update)
timer.start(100)


def write_param_fifo(self, param): # TODO FIXME
        if param == '':
            pass
        else:
            try:
                print('write_param_fifo():', param)
                fifo = open(spectrum_params_fifo_name, "w")
                # fifo.write(param + '\n')
                fifo.writelines(param)
                fifo.flush()
                fifo.close()
                sleep(0.25)
            except:
                print('*****write_param_fifo():Exception*****', param)






#x2 = np.linspace(-100, 100, 1000)
#data2 = np.sin(x2) / x2
#lr = pg.LinearRegionItem([400, 700])
#lr.setZValue(-10)




def main():
    data_collected = np.loadtxt(fifo_name, delimiter=',', dtype=float)
    print("#####")
    #print( data_collected[0:8,0] )
    #print( data_collected[0:,1] )
    print( data_collected )
    print("-----")

if __name__ == '__main__':
    pg.exec()
    os.system(r'pkill -f pyspectrum.py')
    #while(1):
        #main()

#   mainDCX|spectrum.out|jnoise|pyspectrum.py












