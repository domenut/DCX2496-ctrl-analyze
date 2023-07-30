#!/usr/bin/env python3
''' Extension file for "mainDCX.py" MainWindow class. '''



from time import sleep
import threading
import os
import subprocess
import configparser
import pyqtgraph as pg
import numpy as np
from scipy import signal

from PyQt5 import QtWidgets, Qwt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog

import dcx_map as dcx
import shutil

_test=1
pg.setConfigOptions(antialias=True)
np.seterr(over='ignore')
spectrum_data_fifo_name = './spectrum_data.fifo'
spectrum_params_fifo_name = './spectrum_params.fifo'

#IFACE_MAP = 'dcx.Mapper.'
#CHANNELS = ['A', 'B', 'C', 'S', '1', '2', '3', '4', '5', '6']

class ControlLinksMixin():
    ''' Left to Right and Hi pass to low pass locking/linking logic. '''

    def xo_link_lphp_low(self):
        link = self.sender().checkState()
        self.write_ini('Checkbox', self.sender().objectName(), self.sender().checkState())
        if link:
            self.xo_diff_low1 = self.Crossover_hpFreq03.value() - self.Crossover_lpFreq01.value()
            self.xo_diff_low2 = self.Crossover_hpFreq04.value() - self.Crossover_lpFreq02.value()
            self.Crossover_lpFreq01.valueChanged.connect(self.xo_link_lphp_1to3_handler)
            self.Crossover_hpFreq03.valueChanged.connect(self.xo_link_lphp_1to3_handler)
            self.Crossover_lpFreq02.valueChanged.connect(self.xo_link_lphp_2to4_handler)
            self.Crossover_hpFreq04.valueChanged.connect(self.xo_link_lphp_2to4_handler)
        if link == False:
            self.Crossover_lpFreq01.valueChanged.disconnect(self.xo_link_lphp_1to3_handler)
            self.Crossover_hpFreq03.valueChanged.disconnect(self.xo_link_lphp_1to3_handler)
            self.Crossover_lpFreq02.valueChanged.disconnect(self.xo_link_lphp_2to4_handler)
            self.Crossover_hpFreq04.valueChanged.disconnect(self.xo_link_lphp_2to4_handler)

    def xo_link_lphp_high(self):
        link = self.sender().checkState()
        self.write_ini('Checkbox', self.sender().objectName(), self.sender().checkState())
        if link:
            self.xo_diff_hi5 = self.Crossover_lpFreq03.value() - self.Crossover_hpFreq05.value()
            self.xo_diff_hi6 = self.Crossover_lpFreq04.value() - self.Crossover_hpFreq06.value()
            self.Crossover_lpFreq03.valueChanged.connect(self.xo_link_lphp_3to5_handler)
            self.Crossover_hpFreq05.valueChanged.connect(self.xo_link_lphp_3to5_handler)
            self.Crossover_lpFreq04.valueChanged.connect(self.xo_link_lphp_4to6_handler)
            self.Crossover_hpFreq06.valueChanged.connect(self.xo_link_lphp_4to6_handler)
        if link == False:
            self.Crossover_lpFreq03.valueChanged.disconnect(self.xo_link_lphp_3to5_handler)
            self.Crossover_hpFreq05.valueChanged.disconnect(self.xo_link_lphp_3to5_handler)
            self.Crossover_lpFreq04.valueChanged.disconnect(self.xo_link_lphp_4to6_handler)
            self.Crossover_hpFreq06.valueChanged.disconnect(self.xo_link_lphp_4to6_handler)

    def xo_link_lphp_1to3_handler(self):
        if self.xo_lock_enable:
            sender = self.sender()
            if 'lpFreq01' in sender.objectName():
                self.xo_diff_low1 = self.Crossover_hpFreq03.value() - self.Crossover_lpFreq01.value()
            elif 'hpFreq03' in sender.objectName():
                self.Crossover_lpFreq01.setValue(sender.value() - self.xo_diff_low1)

    def xo_link_lphp_2to4_handler(self):
        if self.xo_lock_enable:
            sender = self.sender()
            if 'lpFreq02' in sender.objectName():
                self.xo_diff_low2 = self.Crossover_hpFreq04.value() - self.Crossover_lpFreq02.value()
            elif 'hpFreq04' in sender.objectName():
                self.Crossover_lpFreq02.setValue(sender.value() - self.xo_diff_low2)

    def xo_link_lphp_3to5_handler(self):
        if self.xo_lock_enable:
            sender = self.sender()
            if 'hpFreq05' in sender.objectName():
                self.xo_diff_hi5 = self.Crossover_lpFreq03.value() - self.Crossover_hpFreq05.value()
            elif 'lpFreq03' in sender.objectName():
                self.Crossover_hpFreq05.setValue(sender.value() - self.xo_diff_hi5)

    def xo_link_lphp_4to6_handler(self):
        if self.xo_lock_enable:
            sender = self.sender()
            if self.linkCopy5_6_checkbox.checkState():
                return
            else:
                if 'hpFreq06' in sender.objectName():
                    self.xo_diff_hi6 = self.Crossover_lpFreq04.value() - self.Crossover_hpFreq06.value()
                elif 'lpFreq04' in sender.objectName():
                    self.Crossover_hpFreq06.setValue(sender.value() - self.xo_diff_hi6)

    def xo_hideRightChans(self, hide=None):
        if hide == None:
            hide = self.sender().isChecked()
        else:
            hide = self.xo_hideRightChans_checkbox.isChecked()
            self.write_ini('Checkbox', self.sender().objectName(), self.sender().checkState())
        self._xo_hide_channel('2', hide and self.linkCopy1_2_checkbox.isChecked())
        self._xo_hide_channel('4', hide and self.linkCopy3_4_checkbox.isChecked())
        self._xo_hide_channel('6', hide and self.linkCopy5_6_checkbox.isChecked())

    def _xo_hide_channel(self, right_chan, hide=True):
        xo_frame = getattr(self, 'frame_Crossover0' + right_chan)
        align_frame = getattr(self, 'frame_Align0' + right_chan)
        if hide:
            xo_frame.hide()
            align_frame.hide()
        else:
            xo_frame.show()
            align_frame.show()

    def _xo_connect_to_leftright_mirror(self, left_chan, mirror=True):
        #print('_xo_connect_to_leftright_mirror : ', left_chan)
        
        xo_frame = getattr(self, 'frame_Crossover0' + left_chan)
        align_frame = getattr(self, 'frame_Align0' + left_chan)
        widgets = xo_frame.findChildren(QtWidgets.QWidget)
        widgets.extend(align_frame.findChildren(QtWidgets.QWidget))
        for left_widget in widgets:
            name = left_widget.objectName()
            if name[-2:-1] == '_':
                name = name[:-2]
            val = dcx.get_setting(name)
            if val:
                right_name = name[:-1] + str(int(left_chan) + 1)
                right = getattr(self, right_name)
                right_widget = getattr(self, right_name)
                if mirror == True:
                    if isinstance(left_widget, QtWidgets.QComboBox):
                        right_widget.setCurrentIndex(left_widget.currentIndex())
                        left_widget.currentIndexChanged.connect(self.mirror_stereo_handler)

                    elif isinstance(left_widget, QtWidgets.QCheckBox):
                        right_widget.setCheckState(left_widget.checkState())
                        left_widget.stateChanged.connect(self.mirror_stereo_handler)
                    else:
                        right_widget.setValue(left_widget.value())
                        left_widget.valueChanged.connect(self.mirror_stereo_handler)
                else:
                    if isinstance(left_widget, QtWidgets.QComboBox):
                        left_widget.currentIndexChanged.disconnect(self.mirror_stereo_handler)

                    elif isinstance(left_widget, QtWidgets.QCheckBox):
                        try:
                            right_widget.stateChanged.disconnect(self.mirror_stereo_handler)
                        except:
                            pass
                    else:
                        try:
                            left_widget.valueChanged.disconnect(self.mirror_stereo_handler)
                        except:
                            pass
        #self._xo_hide_channel(str(int(left_chan) + 1), hide=mirror)

    def _chan_tab_connect_to_leftright_mirror(self, left_chan, mirror=True):
        tab = getattr(self, 'tab_ch' + left_chan)
        widgets = tab.findChildren(QtWidgets.QWidget)
        for widget in widgets:
            name = widget.objectName()
            if name[-2:-1] == '_':
                name = name[:-2]
            val = dcx.get_setting(name)
            left_chan = name[-1:]
            if val != None and ('Mute' not in name):
                left = widget
                if left_chan == 'A':
                    right_name = name[:-1] + 'B'
                else:
                    right_name = name[:-1] + str(int(left_chan) + 1)
                if mirror == True:
                    right_widget = getattr(self, right_name)
                    if isinstance(widget, (QtWidgets.QDial, QtWidgets.QSlider)):
                        right_widget.setValue(widget.value())
                        left.valueChanged.connect(self.mirror_stereo_handler)
                        
                    elif isinstance(widget, (Qwt.QwtKnob, Qwt.QwtDial, Qwt.QwtWheel, Qwt.QwtSlider) ):
                        right_widget.setValue( widget.value() )
                        left.valueChanged.connect(self.mirror_stereo_handler)
                        
                    elif isinstance(widget, QtWidgets.QComboBox):
                        right_widget.setCurrentIndex(widget.currentIndex())
                        left.currentIndexChanged.connect(self.mirror_stereo_handler)
                        
                    elif isinstance(widget, QtWidgets.QSpinBox):
                        right_widget.setValue(left.value())
                        left.valueChanged.connect(self.mirror_stereo_handler)
                        
                    elif isinstance(widget, QtWidgets.QPushButton):
                        right_widget.setChecked(left.isChecked())
                        left.toggled.connect(self.mirror_stereo_handler)
                        
                else:
                    if isinstance(widget, (QtWidgets.QDial, QtWidgets.QSlider)):
                        left.valueChanged.disconnect(self.mirror_stereo_handler)
                        
                    elif isinstance(widget, (Qwt.QwtKnob, Qwt.QwtDial, Qwt.QwtWheel, Qwt.QwtSlider) ):
                        left.valueChanged.disconnect(self.mirror_stereo_handler)
                        
                    elif isinstance(widget, QtWidgets.QComboBox):
                        left.currentIndexChanged.disconnect(self.mirror_stereo_handler)
                        
                    elif isinstance(widget, QtWidgets.QSpinBox):
                        left.valueChanged.disconnect(self.mirror_stereo_handler)
                        
                    elif isinstance(widget, QtWidgets.QPushButton):
                        left.toggled.disconnect(self.mirror_stereo_handler)
                    
    def mirror_stereo_handler(self):
        left_widget = self.sender()
        name = left_widget.objectName()
        if name[-2:-1] == '_':
            name = name[:-2]
        channel = name[-1:]
        if channel != 'A':
            name_r = name[:-1] + str(int(channel) + 1)
        else:
            name_r = name[:-1] + 'B'

        right_widget = getattr(self, name_r)

        if isinstance(left_widget, QtWidgets.QComboBox):
            right_widget.setCurrentIndex(left_widget.currentIndex())

        elif isinstance(left_widget, QtWidgets.QCheckBox):
            right_widget.setCheckState(left_widget.checkState())
            
        elif isinstance(left_widget, (Qwt.QwtKnob, Qwt.QwtDial, Qwt.QwtWheel, Qwt.QwtSlider) ):
            right_widget.setValue( left_widget.value() )
            
        elif isinstance(left_widget, QtWidgets.QPushButton ):
            right_widget.setChecked(left_widget.isChecked())
    
        else:
            right_widget.setValue(left_widget.value())

    def mirror_left_to_next(self, left_chan):
        #print('mirror_left_to_next: ', left_chan)
        link = self.sender().isChecked()
        name = self.sender().objectName()
        if 'Mute' in name:
            return
        self.write_ini('Checkbox', self.sender().objectName(), self.sender().checkState())
        if left_chan == 'A' and ('Mute' not in name):
            right_chan = 'B'
            left_tab = getattr(self, 'tab_ch' + left_chan)
            if link:
                self.rename_outputs()
                self._chan_tab_connect_to_leftright_mirror(left_chan, mirror=True)
                self.toggle_tab(right_chan, show=0)
                self.tabWidget.setTabText(0, 'In:AB')
            else:
                right_tab_index = self.tabWidget.indexOf(left_tab) + 1
                self.toggle_tab(right_chan, show=1, new_index=right_tab_index, tab_title='R-')
                self._chan_tab_connect_to_leftright_mirror(left_chan, mirror=False)
                self.tabWidget.setTabText(0, 'In:A')
        else:
            right_chan = str(int(left_chan) + 1)
            if link:
                self.rename_outputs()
                self._chan_tab_connect_to_leftright_mirror(left_chan, mirror=True)
                self.toggle_tab(right_chan, show=0)
                self._xo_connect_to_leftright_mirror(left_chan, mirror=True)
                self.xo_hideRightChans(hide=True)
            else:
                left_tab = getattr(self, 'tab_ch' + left_chan)
                right_tab_index = self.tabWidget.indexOf(left_tab) + 1
                self.toggle_tab(right_chan, show=1, new_index=right_tab_index, tab_title='R-')
                self._chan_tab_connect_to_leftright_mirror(left_chan, mirror=False)
                self._xo_connect_to_leftright_mirror(left_chan, mirror=False)
                self.xo_hideRightChans(hide=False)
            self.rename_outputs()

class CustomAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        places = 0
        strings = []
        for v in values:
            vs = ( 10**v )
            vstr = ("%%0.%df" % places) % vs
            # print(v, ', ', vstr, ', ')
            strings.append(vstr)

        return strings

class CustomGrid():
    def __init__(self, pw):
        pw.plotItem.setAxisItems({'bottom': CustomAxisItem('bottom')})
        grd = pg.GridItem()
        con = 230
        grd.setPen((con,con,con,255))
        grd.setTextPen(None)
        grd.setTickSpacing(x=[1.0,0.2], y=[3.0, 6.0])
        pw.addItem(grd)

class Crosshair():
    def __init__(self, pw):
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        pw.addItem(self.vLine, ignoreBounds=True)
        pw.addItem(self.hLine, ignoreBounds=True)
        self.vb = pw.plotItem.vb
        self.label = pg.TextItem()
        self.label.setPos(3.7,14)
        pw.addItem(self.label)
        self.proxy = pg.SignalProxy(pw.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.pw = pw

    def mouseMoved(self, evt):
        pos = evt[0]
        vr = self.pw.visibleRange()
        mousePoint = self.vb.mapSceneToView(pos)
        # print(mousePoint.x(), ' ', mousePoint.y() )
        self.pw.enableAutoRange('xy', False)
        self.label.setPos(  (vr.x()+(vr.width()*0.8)) , (vr.y()+(vr.height()*1))  )
        self.label.setHtml(
                    "<span style='font-size: 11pt'>{:0.1f}Hz  '\
                     <span style='color: yellow'>{:0.1f}db</span>".format(
                10**mousePoint.x(), mousePoint.y()))

        self.vLine.setPos(mousePoint.x())
        self.hLine.setPos(mousePoint.y())

class PlotsMixin():
    #ref_curve
    ''' Eq and crossover plots code'''

    def init_plots(self):
        self.init_eq_plots()
        self.init_xo_plots()
        
    def init_eq_plots(self):
        ref_colour = '#bfbf5f77'
        #background_colour = '#3a4228ff'
        #background_colour = '#ffffffff'
        background_colour = '#000000ff'
        alpha = 'aa'
        ink = ['#ff0000'+alpha, '#00ff00'+alpha, '#0000ff'+alpha]
        CHANNELS = ['A', 'B', 'C', 'S', '1', '2', '3', '4', '5', '6']
        hz = np.geomspace(2, 24000, 26, dtype=int)
        y = np.zeros(26)
        ink_index = -1
        for channel in CHANNELS:
            plotwin_name = 'plot_' + channel
            try:
                pw = getattr(self, plotwin_name)
                pw.clear()
                pw.showGrid(False, False, alpha=0.6)
                pw.setBackground(background_colour)
                pw.setLogMode(True)
                pw.setXRange(np.log10(20 + 15), np.log10(20000 - 9000))
                pw.setYRange(-16, 16)
                pw.plotItem.vb.setLimits(xMin=1.0, xMax=4.4, yMin=-200, yMax=200)
                setattr(self, plotwin_name +'_', pw.plot(hz, y, pen='#00ccddff', fillLevel=0.0, brush=(50,50,200,60))  )
                self.setup_eq_spectrum_analyzer_plots(plot_window=pw, plotwin_name=plotwin_name, hz_axis=hz, y_axis=y)
                self.setup_eq_graph_markers(plot_window=pw, channel=channel)

                # pw.plotItem.setAxisItems({'bottom': CustomAxisItem('bottom')})
                # grd = pg.GridItem()
                # grd.setPen((255,255,255,127))
                # grd.setTextPen(None)
                # grd.setTickSpacing(x=[1.0,0.2], y=[6.0, 3.0])
                # pw.addItem(grd)

                # Grid
                setattr(self, plotwin_name +'_grid_', CustomGrid(pw) )
                # Crosshairs
                setattr(self, plotwin_name +'_cxh_', Crosshair(pw) )

                if channel.isnumeric():
                    ink_index += int(int(channel) % 2)
                    setattr(self, plotwin_name +'_xo_copy', pw.plot(hz, y, pen=ink[ink_index], fillLevel=None, brush=(50,50,200,60) ) )
                    setattr(self, plotwin_name +'_ref_xo_', pw.plot(hz, y, pen='#dd998899', fillLevel=None, brush=(50,50,200,60)))
            except:
                print('In file: extras.py PlotsMixIn.setup_plots() ... Some balls up ...')

    def init_xo_plots(self):
        ref_colour = '#cfcf6fff'
        #background_colour = '#3a4228ff'
        #background_colour = '#ffffffff'
        background_colour = '#000000ff'
        ink = ['#ff0000ff', '#00ff00ff', '#0000ffff']
        ink_index = -1
        xo_channels = [1, 2, 3, 4, 5, 6]
        hz = np.geomspace(20, 20000, 26, dtype=int)
        y = np.zeros(26)
        plotwin_name = 'plot_xo'
        pw = getattr(self, plotwin_name)
        pw.showGrid(False, False, alpha=1.0)
        pw.setBackground(background_colour)
        pw.setLogMode(True)
        pw.setYRange(-16, 16)
        pw.plotItem.vb.setLimits(xMin=1.0, xMax=4.4, yMin=-200, yMax=200)
        pw.setLabel('bottom', units='hz')
        pw.setLabel('left', units='db')

        self.crosshair = Crosshair(pw)
        custom_grid = CustomGrid(pw)

        for channel in xo_channels:
            ink_index += (channel % 2)
            setattr(self, plotwin_name +'_' + str(channel), pw.plot(hz, y, pen=ink[ink_index], fillLevel=0.0, brush=(50,50,200,30) ))

        setattr(self, 'plot_xo_ref', pw.plot(hz, y, pen=ref_colour, fillLevel=None, brush=(50,50,200,120)))
        setattr(self, 'plot_xo_frozen', pw.plot(hz, y, pen=0.5, fillLevel=None, brush=(50,50,200,120)))

    def setup_eq_graph_markers(self, plot_window, channel='A'):
        mx = [1000,]
        my = [1,]
        #syms=['o', 't', 's', 'd', 'p', 'h', '+', 'x', 'star', 't1', 't2', 't3' ]
        for eq in range(1, 9 + 1):
            # Eq center markers, (shapes)...
            setattr(self, 'eq'+str(eq)+'_'+channel, plot_window.plot(mx, my, pen=None, symbol='o', Brush=(50,50,200,60), symbolSize=6 ) )
            
            # Eq center markers, (eq band numbers)
            setattr(self, 'eq'+str(eq)+'_text_'+ channel, pg.TextItem() )
            this_text = getattr(self, 'eq'+str(eq)+'_text_'+ channel)
            plot_window.addItem(this_text)
            this_text.setPos(0.00, 0.0)

    def render_eq_band_numbers(self, channel='A', band=1, x=3.0, y=0.0, hide=0):
        this_text = getattr(self, 'eq'+str(band)+'_text_'+ channel)
        if not hide:
            this_text.setText( str(band) )
            this_text.setPos( np.log10(x)-0.031, y+2.2)
        else:
            this_text.setText( '' )
        return

    def setup_eq_spectrum_analyzer_plots(self, plot_window, plotwin_name, hz_axis, y_axis):
        #pass
        ref_colour = '#cfcf6fff'
        setattr(self, plotwin_name +'_ref', plot_window.plot(hz_axis, y_axis, pen=ref_colour, fillLevel=None, brush=(50,50,200,120)))
        setattr(self, plotwin_name +'_frozen', plot_window.plot(hz_axis, y_axis, pen=0.5, fillLevel=None, brush=(50,50,200,120)))

    ref_xo_ctrls =[0, 0, 0, 0]
    ref_xo_mem = [ref_xo_ctrls]*6
    
    def xo_ref_visualize(self):
        sender = self.sender()
        p = sender.parent().parent().parent().parent().objectName()
        channel = p[-1:]
        # print('>>: ', p)
        try:
            self.write_ini('RefCrossover', sender.objectName() +'_'+ channel, sender.value() )
        except:
            self.write_ini('RefCrossover', sender.objectName() +'_'+ channel, sender.currentIndex() )

        hz = np.geomspace(20, 20000, 1600, dtype=int)
        magn = [[np.zeros(1600)],[np.zeros(1600)]]


        label_lp = getattr(self, 'Ref_xo_lpLabel')
        label_hp = getattr(self, 'Ref_xo_hpLabel')

        curve = self.Ref_xo_lpCurve.currentText()
        lp_fr_val =  int(self.Ref_xo_lpFreq.value())
        freq = dcx.Mapper.Crossover.hpFreq01.detents(int(lp_fr_val))
        label_lp.setText( str(freq) + 'Hz')
        
        lp_indx  = self.Ref_xo_lpCurve.currentIndex()
        hp_indx  = self.Ref_xo_hpCurve.currentIndex()
        hp_fr_val = int(self.Ref_xo_hpFreq.value())
        
        self.ref_xo_mem[int(channel)-1] = [lp_fr_val, lp_indx, hp_fr_val, hp_indx]

        try:
            order = int(int(curve[-2:])/6)
        except:
            order = 0
        btype = 'low'
        for n in range(0, 2):
            if curve == 'off':
                magn[n] = np.zeros(1600)
            elif curve[0:2] == 'lr':
                numer, denom = signal.butter(order/2, freq, btype, analog=True)
                warr, magn[n], phase = signal.bode((numer,denom), hz)
                magn[n] = magn[n]*2
            elif curve[0:3] == 'but':
                numer, denom = signal.butter(order, freq, btype, analog=True)
                warr, magn[n], phase = signal.bode((numer,denom), hz)
            elif curve[0:3] == 'bes':
                numer, denom = signal.bessel(order, freq, btype, analog=True)
                warr, magn[n], phase = signal.bode((numer,denom), hz)
                
            curve = self.Ref_xo_hpCurve.currentText()
            freq = dcx.Mapper.Crossover.hpFreq01.detents(int(hp_fr_val))
            try:
                order = int(int(curve[-2:])/6)
            except:
                order = 0
            btype = 'high'
        label_hp.setText( str(freq) + 'Hz')

        mag = magn[0] + magn[1]
        this_plot = getattr(self, 'plot_' + channel + '_ref_xo_')
        this_plot.setData(hz, mag)
        
    def xo_visualize(self, channel=None):
        hz = np.geomspace(20, 20000, 1600, dtype=int)
        magn = [[np.zeros(1600)],[np.zeros(1600)]]

        curve = dcx.get_setting('Crossover.lpCurve0' + channel)[1]
        freq = dcx.get_setting('Crossover.lpFreq0' + channel)[1]

        label_lp = getattr(self, 'Crossover_lpFreqLabel0' + channel)
        label_hp = getattr(self, 'Crossover_hpFreqLabel0' + channel)
        edit_box = getattr(self, 'lineEdit_' + channel)
        chan_name = edit_box.text()
        label_lp.setText( str(freq) + 'Hz')

        try:
            label_name = getattr(self, 'Crossover_nameLabel0' + channel)
            label_name.setText(' ['+ chan_name + ']')
        except:
            pass

        try:
            order = int(int(curve[-2:])/6)
        except:
            order = 0
        btype = 'low'
        for n in range(0, 2):
            if curve == 'off':
                magn[n] = np.zeros(1600)
            elif curve[0:2] == 'lr':
                numer, denom = signal.butter(order/2, freq, btype, analog=True)
                warr, magn[n], phase = signal.bode((numer,denom), hz)
                magn[n] = magn[n]*2
            elif curve[0:3] == 'but':
                numer, denom = signal.butter(order, freq, btype, analog=True)
                warr, magn[n], phase = signal.bode((numer,denom), hz)
            elif curve[0:3] == 'bes':
                numer, denom = signal.bessel(order, freq, btype, analog=True)
                warr, magn[n], phase = signal.bode((numer,denom), hz)
            curve = dcx.get_setting('Crossover.hpCurve0' + channel)[1]
            freq = dcx.get_setting('Crossover.hpFreq0' + channel)[1]
            try:
                order = int(int(curve[-2:])/6)
            except:
                order = 0
            btype = 'high'

        label_hp.setText(str(freq) + 'Hz')
        mag = magn[0] + magn[1]
        this_plot = getattr(self, 'plot_xo_' + channel)
        this_plot.setData(hz, mag)
        
        this_plot = getattr(self, 'plot_' + channel + '_xo_copy')
        this_plot.setData(hz, mag)
        
        #pw = getattr(self, 'plot_xo')
        #text = pg.TextItem("test", anchor=(10.0, -6.0))
        #pw.addItem(text)
        #text.setPos(freq, 6.0)

    def eq_visualize(self, channel):
        params = []
        
        eq_bands = getattr(self, 'EqNumber_ch' + channel)  # (live eq's on channel spinBox)
        
        if eq_bands.value() == 0:
            mag2d =  np.zeros(3000)
            this_plot = getattr(self, 'plot_' + channel + '_')
            this_plot.setData(mag2d)
            
            marker = getattr(self, 'eq1_' + channel)
            mx = [20,]
            my = [1,]
            marker.setData(mx, my)
            self.render_eq_band_numbers( channel, band=1, x=0.0, y=0.0, hide=1 )
                
            return
        else:
            pass
        for n in range(1, eq_bands.value() + 1):
            param = []
            params.append(param)

            gain_adr = 'Eq' + str(n) + '.gain' + channel
            gain = dcx.get_setting(gain_adr)[1]
            param.append(gain)

            freq_adr = 'Eq' + str(n) + '.freq' + channel
            freq = dcx.get_setting(freq_adr)[1]
            if freq < 20: freq = 20
            param.append(freq)

            Q_adr = 'Eq' + str(n) + '.Q' + channel
            Q = dcx.get_setting(Q_adr)[1]
            param.append(Q)

            eq_type_adr = 'Eq' + str(n) + '.type' + channel
            eq_type = dcx.get_setting(eq_type_adr)[1]
            param.append(eq_type)

            eq_slope_adr = 'Eq' + str(n) + '.slope' + channel
            eq_slope = dcx.get_setting(eq_slope_adr)[1]
            param.append(eq_slope)
        
            marker = getattr(self, 'eq'+str(n)+'_'+channel)
            mx = [freq,]
            my = [gain,]
            marker.setData(mx, my)
            
            self.render_eq_band_numbers( channel, band=n, x=freq, y=gain, hide=0 )
        bp = lambda f: ((K*(fc/Q)*f))/((f**2) + (fc/Q)*f + (fc**2))
        hp = lambda f: (K*((-f**(2*order)))/((f**(2*order))+(((fc/(2**(1/order)))**(2*order)))))
        lp = lambda f: (K*(((fc/(0.5**(1/order)))**(2*order)+1**(2*order))/(((f**(2*order))+(fc/(0.5**(1/order)))**(2*order)))))
        hz = np.geomspace(2, 24000, 3000, dtype=int)
        for n in range(0, len(params)):
            K, fc, Q, eqtype, eqslope = params[n]
            order = (int(eqslope)/6)
            H = eval(eqtype)
            if 'bp' in eqtype:
                Hs = H(1j*hz)
            else:
                Hs = H(hz)
            if n == 0:
                mag2d = np.abs(Hs)*np.sign(K)
            else:
                mag2d += np.abs(Hs)*np.sign(K)
        this_plot = getattr(self, 'plot_' + channel + '_')
        this_plot.setData(hz, mag2d)
        
        for hidden_eq in range(eq_bands.value()+1, 9+1):
            marker = getattr(self, 'eq'+str(hidden_eq)+'_'+channel)
            mx = [20,]
            my = [1,]
            marker.setData(mx, my)
            self.render_eq_band_numbers( channel, band=(hidden_eq), x=20, y=0, hide=1 )
        
class FilesMixin():
    ''' '''

    def save_set(self, filepath='./Saved_binary/TestSet'):
        dcx.sync_cache_from_dcx()
        shutil.copy(dcx.DUMP_FILE, filepath)

    def load_set(self, filepath='./Saved_binary/TestSet'):
        shutil.copy(filepath, dcx.DUMP_FILE)
        dcx.transmit_set()
        self.update_gui()

        pass

    def read_ini(self, section, key=None, path='settings.ini'):
        config = CaseConfigParser()
        config.read(path) #path of .ini file
        config.optionxform = lambda option: option
        if key == None:
            settings = dict([])
            config.sections()
            for key in config[section]:
                setting = config.get(section, key)
                #print('extras.read_ini:', key, setting)
                settings[key]=setting
            return settings
        else:
            setting = config.get(section, key)
            return setting

    def write_ini(self, section, key, setting, path='settings.ini'):
        from pathlib import Path
        config = configparser.RawConfigParser()
        config.optionxform=str #lambda option: option
        myfile = Path(path)  #Path of .ini file
        config.read(myfile)
        try:
            config.set(section, key, setting) #Updating existing or (create new entry???)
        except:
            config.add_section(section)
            config.set(section, key, setting)
        config.write(myfile.open("w"))
        return

    def save_set_file_handler(self):
        filename = QFileDialog.getSaveFileName(self,
            self.tr("Save setup"), "./Saved_binary",
            self.tr("files (*.dcx)"))[0]
        if filename:
            self.save_set(filepath=filename)

    def load_set_file_handler(self):
        last_tab = 'tab_Crossovers'
        this_tab = getattr(self, last_tab)
        tab_index = self.tabWidget.indexOf(this_tab)
        self.tabWidget.setCurrentIndex(tab_index)

        filename = QFileDialog.getOpenFileName(self,
            self.tr("Load setup"), "./Saved_binary",
            self.tr("files (*.dcx)"))[0]
        if filename:
            self.load_set(filepath=filename)

    def unlock_dcx_channel_links(self):
        self.Setup_outConfig.setCurrentIndex(0)
        self.Setup_outStereoLink.setCurrentIndex(0)
        self.Setup_xoLink.setCurrentIndex(0)
        self.xo_link_Low.setCheckState(0)
        self.xo_link_High.setCheckState(0)

        return

class CaseConfigParser(configparser.SafeConfigParser):
    def optionxform(self, optionstr):
        return optionstr

class SpectrumAnalyserMixin():
    spectrum_analyzer_on = False
    spectrum_data_ready = False
    spectrum_v_shift = 0
    fft_process=None
    noise_gen_process=None
    spectrum_param = ''
    param_ready = False
    param_change_enable = False
    smoothing = True
    smoothing_factor = 1500
    smoothing_poly = 1
    data_collected = np.array([0, 1, 2, 3], ndmin=2)
    y_smooth_data = np.array([0,1,2,3])
    pause = True
    
    def init_spectrum(self): #TODO progress
        self.fft_process= subprocess.Popen( ('./spectrum.out -s 1000'), stdout=subprocess.PIPE, shell=True)
        # self.noise_gen_process= subprocess.Popen( ('./jnoise'), stdout=subprocess.PIPE)
        self.smoothing = self.smoothingFactorSpinBox_S.value()
        self.smoothing_factor = int(self.smoothingFactorSpinBox_S.value())
        sleep(0.1)

        self.spectrum_io_thread = threading.Thread(target=self.start_spectrum_data_loop)
        self.spectrum_io_thread.start()

        self.spectrum_param_io_thread = threading.Thread(target=self.start_spectrum_params_loop)
        self.spectrum_param_io_thread.start()

        self.timer_spectrum_draw = QTimer()
        #self.timer_spectrum_draw = QtCore.QTimer()
        self.timer_spectrum_draw.timeout.connect(self.draw_live_spectrum_plots)
        self.timer_spectrum_draw.start(200)

    def spectrum_power_button_handler(self): #TODO progress...
        sender = self.sender()
        if sender.isChecked():
            try:
                self.pause = True
                self.spectrum_analyzer_on = True
                self.init_spectrum()
                sleep(0.3)
                self.spectrum_init_params()
                sender.setStyleSheet("background-color:rgb( 128 , 0, 0 )")
                sender.setText( "Spectrum ON" )
                self.pause = False
            except:
                sender.setChecked(False)
                sender.setStyleSheet("background-color:rgb( 0, 128, 128 )")
                sender.setText( "error" )
        else:
            sender.setStyleSheet("background-color:rgb( 96, 96, 96 )")
            sender.setText( "Spectrum OFF" )
            self.spectrum_analyzer_on = False
            self.timer_spectrum_draw.stop()
            self.spectrum_io_thread.join()
            os.system(r'pkill -f spectrum.out')
            os.system(r'pkill -f jnoise')
            self.fft_process.wait()
            self.noise_gen_process.wait()

    def spectrum_smoothing_factor_handler(self):
        self.pause = True
        sender = self.sender()
        self.smoothing_factor = int(sender.value())
        self.spectrum_param = 'S' + str(self.smoothing_factor)
        sleep(0.1)
        self.write_ini('Spectrum', sender.objectName(), str(sender.value() ) )
        self.param_ready = True
        self.draw_static_spectrum_plots()
        self.pause = False

    def spectrum_averages_handler(self):
        self.pause = True
        sender = self.sender()
        self.spectrum_param = 'A' + str(sender.value() )
        self.write_ini('Spectrum', sender.objectName(), str(sender.value() ) )
        self.param_ready = True
        sleep(0.1)
        self.pause = False

    def spectrum_exponential_handler(self):
        self.pause = True
        sender = self.sender()
        fac = int(sender.value())
        self.spectrum_param = 'E' + str(fac)
        self.write_ini('Spectrum', sender.objectName(), str(fac) )
        self.param_ready = True
        sleep(0.1)
        self.draw_static_spectrum_plots()
        self.pause = False

    def spectrum_vertical_shift_handler(self):
        sender = self.sender()
        self.spectrum_v_shift = sender.value()
        self.draw_static_spectrum_plots()

    def spectrum_fft_length_handler(self):
        self.pause = True
        sender = self.sender()
        indx = sender.currentIndex()
        fft_len = 2**(indx + 6)
        self.spectrum_param = 'B' + str( fft_len )
        #print('***fft_len_box_handler()***: ', self.spectrum_param)
        self.write_ini('Spectrum', sender.objectName(), str(indx) )
        sleep(0.2)
        self.param_ready = True
        self.pause = False

    def freeze_plot_button_handler(self):
        sender = self.sender()
        frozen_xo_plot = getattr(self, 'plot_xo_frozen')
        try:
            if sender.isChecked():
                frozen_xo_plot.setData(self.data_collected[0:,0], self.data_collected[0:,1] + self.spectrum_v_shift)
                CHANNELS = ['A', 'B', 'C', 'S', '1', '2', '3', '4', '5', '6']
                for ch in CHANNELS:
                    ref_eq_plot = getattr(self, 'plot_' + ch + '_frozen')
                    ref_eq_plot.setData(self.data_collected[0:,0], self.data_collected[0:,1] + self.spectrum_v_shift)
            else:
                frozen_xo_plot.setData(self.data_collected[0:,0], np.zeros(len(self.data_collected[0:,0])))
                CHANNELS = ['A', 'B', 'C', 'S', '1', '2', '3', '4', '5', '6']
                for ch in CHANNELS:
                    ref_eq_plot = getattr(self, 'plot_' + ch + '_frozen')
                    ref_eq_plot.setData(self.data_collected[0:,0], np.zeros(len(self.data_collected[0:,0])))
        except:
            print('No plot to freeze yet...')

    def spectrum_slope_value_handler(self):
        self.pause = True
        sender = self.sender()
        val = (sender.value())
        self.spectrum_param = 's' + str(val)
        self.write_ini('Spectrum', sender.objectName(), str(val) )
        sleep(0.1)
        self.param_ready = True
        self.pause = False

    def spectrum_window_type_handler(self):
        self.pause = True
        sender = self.sender()
        val = sender.currentIndex()
        self.spectrum_param = 'W' + str(val)
        self.write_ini('Spectrum', sender.objectName(), str(val) )
        sleep(0.1)
        self.param_ready = True
        self.pause = False

    def spectrum_reset_averaging_handler(self):
        self.pause = True
        self.spectrum_param = 'R'
        self.param_ready = True
        sleep(0.1)
        self.pause = False

    def spectrum_log_mode_handler(self):
        self.pause = True
        sender = self.sender()
        mode = sender.currentIndex()
        self.spectrum_param = 'l' + str(mode)
        self.param_ready = True
        self.write_ini('Spectrum', sender.objectName(), str(mode) )
        sleep(0.1)
        self.pause = False

    def spectrum_peak_mode_handler(self):
        self.pause = True
        sender = self.sender()
        mode = sender.currentIndex()
        self.spectrum_param = 'P' + str(mode)
        self.param_ready = True
        self.write_ini('Spectrum', sender.objectName(), str(mode) )
        sleep(0.1)
        self.pause = False

    def spectrum_difference_mode_handler(self):
        self.pause = True
        sender = self.sender()
        mode = sender.currentIndex()
        self.spectrum_param = 'D' + str(mode)
        self.write_ini('Spectrum', sender.objectName(), str(mode) )
        sleep(0.1)
        self.param_ready = True
        self.pause = False



    def spectrum_init_params(self):
        sleep(0.1)
        spectrum = self.read_ini('Spectrum')
        params = ''
        for item in spectrum:
            widget = getattr(self, item)
            code = widget.objectName()[-1:]
            val = spectrum[item]
            if(code == 'B'): # fudge for "Block size"
                val = str( 2**( int(val) + 6)  )
            params += code + val + '\n'
        print('msg_code: ', params)
        self.write_param_fifo( params )

            # spectrum[item]







    def draw_live_spectrum_plots(self):
        if(self.pause):return

        if self.spectrum_data_ready:
            # if self.smoothing:
                # y_local = self.y_smooth_data
            # else:
                # y_local = self.data_collected[0:,1]
            ref_xo_plot = getattr(self, 'plot_xo_ref')
            # ref_xo_plot.setData(self.data_collected[0:,0], y_local + self.spectrum_v_shift)
            ref_xo_plot.setData(self.data_collected[0:,0], self.data_collected[0:,1] + self.spectrum_v_shift)
                            
            CHANNELS = ['A', 'B', 'C', 'S', '1', '2', '3', '4', '5', '6']
            for ch in CHANNELS:
                ref_eq_plot = getattr(self, 'plot_' + ch + '_ref')
                # ref_eq_plot.setData(self.data_collected[0:,0], y_local + self.spectrum_v_shift)
                ref_eq_plot.setData(self.data_collected[0:,0], self.data_collected[0:,1] + self.spectrum_v_shift)
                    
            self.spectrum_data_ready = False
        else:
            #print("draw_live_spectrum_plots(): Waiting for data...")
            pass

    def draw_static_spectrum_plots(self):
        if self.spectrum_analyzer_on: return
        # if self.smoothing:
            # y_local = self.y_smooth_data
        # else:
            # y_local = self.data_collected[0:,1]
        ref_xo_plot = getattr(self, 'plot_xo_ref')
        try:
            # ref_xo_plot.setData(self.data_collected[0:,0], self.y_smooth_data + self.spectrum_v_shift)
            ref_xo_plot.setData(self.data_collected[0:,0], self.data_collected[0:,1] + self.spectrum_v_shift)
            CHANNELS = ['A', 'B', 'C', 'S', '1', '2', '3', '4', '5', '6']
            for ch in CHANNELS:
                ref_eq_plot = getattr(self, 'plot_' + ch + '_ref')
                # ref_eq_plot.setData(self.data_collected[0:,0], y_local + self.spectrum_v_shift)
                ref_eq_plot.setData(self.data_collected[0:,0], self.data_collected[0:,1] + self.spectrum_v_shift)
        except:
            pass
            
    def start_spectrum_data_loop(self):
        # Run in separate thread: (self.spectrum_io_thread)...
        print("Analyzer ON")
        while(self.spectrum_analyzer_on):
            if(not self.pause):
                self.data_collected = np.loadtxt(spectrum_data_fifo_name, delimiter=',', dtype=float)
                # self.y_smooth_data = self.data_collected[0:, 1]
                self.spectrum_data_ready=True
        print("Analyzer OFF")
        
    def normalize_spectrum(self, y):
        ylen = len(y)
        #y_local = np.zeros(ylen)
        #y_ave = np.average(y[int(ylen*0.0005):-int(ylen*0.2)])
        #y_ave = np.average(y)
        y_ave = self.smoothing_factor
        y_local = (y / y_ave) 
        return y_local
        
    def smooth_spectrum(self, y): # TODO ? (Done in C++) Use this for static plot?
        # Run in separate thread: (self.spectrum_io_thread)...
         if not self.smoothing:
             return y
         ylen = len(y)
         if ylen < 128:
             return
         y_local = np.zeros(ylen)
         num_splits = 2
         sf = self.smoothing_factor
         if not sf: return
         ord = self.smoothing_factor
         
         first_span = 1
         last_span = sf
         span = np.linspace(first_span, last_span, ylen, endpoint=True)
         n = 0
         for yv in y:
            if n > (ylen - 1): break
            if n >= 8:
                
                span_start = int( n - (span[n]) ) 
                span_end = int( n + (span[n]) )
                if( span_start >= ylen): span_start = ylen - 2
                if( span_end >= ylen): span_end = ylen - 1
                
                span_ave =  np.average( y[span_start:span_end] )

                y_local[n-1:n] = span_ave
            n += 1
         return y_local
        
    def smooth_spectrum_exponential(self, y): # TODO Unused ? (Done in C++)
         if not self.smoothing:
             return
         ylen = len(y)
         if ylen < 128:
             return
         num_splits = 2
         sf = self.smoothing_factor + 1
         #if not sf: return
         ord = self.smoothing_poly + 1
         
         al_start = 1/(sf)
         al_end = al_start/(10000*ord)
         
         #bin_nums = np.geomspace(2, ylen,  num_splits, endpoint=True)
         #alp_fac = np.geomspace(al_start, al_end, ylen, endpoint=True)
         alp_fac = np.linspace(al_start, al_end, ylen, endpoint=True)
        
         ysm =0
         last_ysm = 0
         n = 0
         alph = 1
         
         # st = αxt+(1 – α)st-1 = st-1+ α(xt – st-1)
         
         for yv in y:
             #if n > (ylen - 1): break
             if n >= 2:
                alph = alp_fac[n-1]

                ysm =  alph*yv+(1-alph)*last_ysm ;
                
                self.y_smooth_data[n-1:n] = ysm
                
             last_ysm = ysm

             n += 1
        
    def smooth_spectrum_savgol_split(self, y): # TODO Unused ? (Done in C++)
         if not self.smoothing:
             return
         ylen = len(y)
         if ylen < 128:
             return
         num_splits = 2
         sf = self.smoothing_factor
         if not sf: return
         ord = self.smoothing_poly
         
         bin_nums = np.geomspace((ylen*0.005), ylen,  num_splits, endpoint=True)
         win_lengs = np.geomspace(5, sf,  num_splits)
         last_fr = 0
         n = 0
         for bin in bin_nums:
             if n > (num_splits - 1): break
             if n >= 1:
                fr = int(bin)
                wl = int(win_lengs[n])
                yy = y[last_fr:fr]
                if(wl >= len(yy)):wl = len(yy)-2
                if(wl % 2 == 0):wl +=1  # Assert odd number (for savgol_filter)...
                if(ord >= wl): ord = wl-1
                if(ord < 0): ord = 0
                yhat = signal.savgol_filter(yy, wl, ord)
                self.y_smooth_data[last_fr:fr] = yhat
             last_fr = int(bin)

             n += 1

    def smooth_spectrum_savgol(self, y): # TODO Unused ? (Done in C++)
         if not self.smoothing:
             return
         dln = len(y)
         if dln < 128:
             return

         wl = self.smoothing_factor
         if not wl: return
         ord = self.smoothing_poly 
         if wl <= ord: wl = ord+1
         if(wl % 2 == 0):wl +=1  # Assert odd number (for savgol_filter)...
         yhat = signal.savgol_filter(y, wl, ord)
         self.y_smooth_data = yhat
   
    def start_spectrum_params_loop(self): #TODO FIXME
        # Run in separate thread...
        while(self.spectrum_analyzer_on):
            if self.param_ready:
                self.write_param_fifo(self.spectrum_param)
                print('params_loop: ', self.spectrum_param)
                self.spectrum_param = ''
                self.param_ready = False
                sleep(0.1)
            else:
                #print('params passed... ')
                sleep(0.1)
                pass
                
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




















