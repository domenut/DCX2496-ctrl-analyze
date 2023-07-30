#!/usr/bin/env python3

import sys
from PyQt5 import QtWidgets, Qwt
from PyQt5.QtCore import QTimer
from time import sleep
import dcx_map as dcx
from gui_dcx import Ui_MainWindow
from gui_eqUnit import Ui_EqFrame
from dcx_extras import PlotsMixin, ControlLinksMixin, FilesMixin, SpectrumAnalyserMixin
from dcx_meters import Meters
from time import sleep

''' !!WIP!! ENTRY POINT,  Application to control the dcx2496 Audio Xover, via rs232 com (version:0)
    author-email for bugs, errors etc.: chriscomdotcom@gmail.com
'''

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, Ui_EqFrame, ControlLinksMixin, PlotsMixin, FilesMixin, SpectrumAnalyserMixin):
    def __init__(self, *args, obj=None, **kwargs): # FIXME
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.timer = QTimer()
        self.timer.singleShot(500, self.initiate_gui)
        
        
        # Testing...

    def initiate_gui(self): # FIXME
        self.populate_ports_combobox()
        last_port = self.read_ini('Port', 'last')
        dcx.PORT_NAME = last_port
        self.xo_lock_enable = True
        
        self.rename_eq_controls()
        self.init_plots()
        dcx.comlink_write_enabled = False
        dcx.sync_cache_from_dcx() # TODO (uncomment)
        self.show_last_tab()
        self.meters = Meters(self)
        self.wire_option_widgets_to_targets()
        self.wire_dcx_control_widgets_to_targets()
        self.show_last_ui_config()
        # #self.mute_all(False)
        self.Gain_ch1.valueChanged.connect(self.remote_gain_control2)
        self.Gain_ch3.valueChanged.connect(self.remote_gain_control2)
        self.Gain_ch5.valueChanged.connect(self.remote_gain_control2)
        self.Mid_gain_remote.setValue(self.Gain_ch3.value())
        self.Hi_gain_remote.setValue(self.Gain_ch5.value())
        self.Low_gain_remote.valueChanged.connect(self.remote_gain_control)
        self.Mid_gain_remote.valueChanged.connect(self.remote_gain_control)
        self.Hi_gain_remote.valueChanged.connect(self.remote_gain_control)
        self.rtsButton.toggled.connect(self.rs232auxlines)
        self.dtrButton.toggled.connect(self.rs232auxlines)
        self.comPort.currentIndexChanged.connect(self.change_port)
        self.wire_spectrum_analyzer_widgets_to_targets()
        dcx.comlink_write_enabled = True

    def DEBUG_HOVER(self):
        sender = self.sender()
        print('DEBUG_HOVER: ', sender.objectName())

    def rename_eq_controls(self):
        containers = ['frame_Eqs_chA', 
                      'frame_Eqs_chB', 'frame_Eqs_chC', 'frame_Eqs_chS',
                      'frame_Eqs_ch1', 'frame_Eqs_ch2', 'frame_Eqs_ch3', 
                      'frame_Eqs_ch4', 'frame_Eqs_ch5', 'frame_Eqs_ch6' 
                      ]
        for cont in containers:
            container = getattr(self, cont)
            widgets = container.findChildren(QtWidgets.QWidget)
            channel = cont[-1:]
            for widget in widgets:
                old_name = widget.objectName()
                name = old_name
                if 'frame_Eq' not in name:
                    eq_band = widget.parent().objectName()[8:9]
                    if name[-11:-2] == '_channel_':
                        name = name[:-2]
                    elif name[-10:-1] == '_channel_':
                        name = name[:-1]
                    name = name.replace('_channel_', channel)
                    name = name.replace('_band', eq_band )
                    setattr(self, name,  self.findChild(QtWidgets.QWidget, old_name ))
                    widget.setObjectName(name)
  
    def populate_ports_combobox(self):
        ports = dcx.comPorts()
        for port in ports:
            name = port.name
            self.comPort.addItem(name)
        last_port = self.read_ini('Port', 'last')
        self.comPort.setCurrentText(last_port)
        dcx.PORT_NAME = self.comPort.currentText()
        dcx.port_connect()

    def change_port(self):
        self.write_ini('Port', 'last', self.comPort.currentText())
        dcx.PORT_NAME = self.comPort.currentText()
        dcx.port_connect()
                
    def rs232auxlines(self):
        #self.tick()
        sender = self.sender()
        print(':', sender.objectName()[:3], ':', sender.isChecked())
        if 'rts' in sender.objectName():
            dcx.set_rts_line(sender.isChecked())
        elif 'dtr' in sender.objectName():
            dcx.set_dtr_line(sender.isChecked())

    def remote_gain_control(self):
        sender = self.sender()
        if 'Hi_gain_remote' in sender.objectName():
            self.Gain_ch5.setValue((sender.value()))
            self.Gain_ch6.setValue((sender.value()))

        if 'Mid_gain_remote' in sender.objectName():
            self.Gain_ch3.setValue((sender.value()))
            self.Gain_ch4.setValue((sender.value()))

        if 'Low_gain_remote' in sender.objectName():
            self.Gain_ch1.setValue((sender.value()))
            self.Gain_ch2.setValue((sender.value()))

    def remote_gain_control2(self):
        sender = self.sender()
        if 'ch1' in sender.objectName():
            self.Low_gain_remote.setValue(sender.value())

        if 'ch3' in sender.objectName():
            self.Mid_gain_remote.setValue(sender.value())

        if 'ch5' in sender.objectName():
            self.Hi_gain_remote.setValue(sender.value())

    def mute_all(self, mute=None):
        if mute == None:
            toggle = int(self.sender().isChecked())
        else:
            toggle = int(mute)
        names = [
            'Mute_ch1',
            'Mute_ch2',
            'Mute_ch3',
            'Mute_ch4',
            'Mute_ch5',
            'Mute_ch6',
            'Mute_chA',
            'Mute_chB',
            'Mute_chC',
            'Mute_chS', ]
        for n in range(0, len(names)):
            button = getattr(self, names[n])
            button.setChecked(toggle)
            dcx.set_setting(names[n], toggle)

    def mute_inputs(self, mute=None):
        if mute == None:
            toggle = int(self.sender().isChecked())
        else:
            toggle = int(mute)
        names = [
            'Mute_chA',
            'Mute_chB',
            'Mute_chC',
            'Mute_chS', ]
        for n in range(0, len(names)):
            button = getattr(self, names[n])
            button.setChecked(toggle)
            dcx.set_setting(names[n], toggle)

    def mute_outputs(self, mute=None):
        if mute == None:
            toggle = int(self.sender().isChecked())
        else:
            toggle = int(mute)
        names = [
            'Mute_ch1',
            'Mute_ch2',
            'Mute_ch3',
            'Mute_ch4',
            'Mute_ch5',
            'Mute_ch6', ]
        for n in range(0, len(names)):
            button = getattr(self, names[n])
            button.setChecked(toggle)
            dcx.set_setting(names[n], toggle)

    def rename_outputs(self):
        sender = self.sender()
        if sender and 'lineEdit' in sender.objectName():  # Rename one channel, based on user text edit.
            new_name = sender.text()
            channel = sender.objectName()[-1:]
            self.write_ini('OutputNames', channel, new_name)
            this_tab = getattr(self, 'tab_ch' + channel)
            tab_index = self.tabWidget.indexOf(this_tab)
            self.tabWidget.setTabText(tab_index, new_name)
            xo_label = getattr(self, 'Crossover_nameLabel0' + channel)
            xo_label.setText(new_name)
        else:                                              # Setup from settings.ini
            for channel in range(1, 6 + 1, 1):
                this_tab = getattr(self, 'tab_ch' + str(channel))
                tab_index = self.tabWidget.indexOf(this_tab)
                name = self.read_ini('OutputNames', str(channel))
                edit_box = getattr(self, 'lineEdit_' + str(channel))
                edit_box.setText(name)
                self.tabWidget.setTabText(tab_index, name)
                xo_label = getattr(self, 'Crossover_nameLabel0' + str(channel) )
                xo_label.setText(name)

    def set_uncontrolled_defaults(self):
        '''set-up all parameters that arent controled by gui, So the gui works as intended. '''
        params = [
            ['Setup.outConfig', 2],
            ['Limit.sw01', 0],
            ['Limit.sw02', 0],
            ['Limit.sw03', 0],
            ['Limit.sw04', 0],
            ['Limit.sw05', 0],
            ['Limit.sw06', 0],
            ['DelaySw.chA', 0],
            ['DelaySw.chB', 0],
            ['DelaySw.chC', 0],
            ['DelaySw.chS', 0],
            ]
        for n in range(0, len(params)):
            dcx.set_setting(params[n][0], params[n][1])

    def move_option_frame(self, channel):
        # on tab change, options panel is moved to new tab.(saves multiplicity of connections)
        if 'Crossovers' in channel:
            target_layout = getattr(self, 'xo_link_verticalLayout')
            target_layout.addWidget(self.frame_options)
        elif 'ch' in channel:
            target_layout = getattr(self, 'plot' + channel[-1:] + '_horizontalLayout')
            target_layout.addWidget(self.frame_options)

    def move_remote_crossover_frame(self, channel):
        if 'chS' in channel:
            return
        elif 'ch' in channel:
            self.frame_Ref_Crossover.hide()
            target_layout = getattr(self, 'horizontalLayout_' + channel[-1:] + '_' + channel[-1:] )
            target_layout.addWidget(self.frame_remote)
            sleep(0.1)
            if channel[-1:].isnumeric():

                for i in reversed(range(self.remoteXoLayout.count())):
                    # self.remoteXoLayout.itemAt(i).widget().setParent(None)
                    ctrl = self.remoteXoLayout.itemAt(i).widget()
                    ch = ctrl.objectName()[-1:]
                    self.xoLayout.insertWidget(int(ch), ctrl)

                this_ch_xo = getattr(self, 'frame_Crossover0' + channel[-1:]  )
                self.remoteXoLayout.addWidget(this_ch_xo)

                ch = int(channel[-1:])
                self.frame_Ref_Crossover.show()
                self.block_signals_ref_xo(block=True)
                try:
                    mem = self.read_ini('RefCrossover', 'Ref_xo_hpFreq_' + str(ch) )
                    self.Ref_xo_hpFreq.setValue(float(mem))
                    mem = self.read_ini('RefCrossover', 'Ref_xo_hpCurve_' + str(ch) )
                    self.Ref_xo_hpCurve.setCurrentIndex(int(mem))
                    mem = self.read_ini('RefCrossover', 'Ref_xo_lpCurve_' + str(ch) )
                    self.Ref_xo_lpCurve.setCurrentIndex(int(mem))
                    mem = self.read_ini('RefCrossover', 'Ref_xo_lpFreq_' + str(ch) )
                    self.Ref_xo_lpFreq.setValue(float(mem))
                    v = float(mem)
                except:
                    self.Ref_xo_lpFreq.setValue(self.ref_xo_mem[ch-1][0])
                    self.Ref_xo_hpFreq.setValue(self.ref_xo_mem[ch-1][2])
                    self.Ref_xo_lpCurve.setCurrentIndex(self.ref_xo_mem[ch-1][1])
                    self.Ref_xo_hpCurve.setCurrentIndex(self.ref_xo_mem[ch-1][3])
                    v = self.ref_xo_mem[ch-1][0]

                self.block_signals_ref_xo(block=False)
                # nudge a control, to update labels...
                self.Ref_xo_lpFreq.setValue(v-1)
                self.Ref_xo_lpFreq.setValue(v+1)
                self.Ref_xo_lpFreq.setValue(v)
                # print('v: ', v, '  type: ', type(v))

    def move_remote_gain_frame(self, channel):
        if 'Crossovers' in channel:
            return
            # target_layout = getattr(self, 'xo_link_verticalLayout')
            # target_layout.addWidget(self.remote_gain_frame)
        elif 'ch' in channel:
            ch = channel[-1:]
            target_layout = getattr(self, 'gain' + ch + '_verticalLayout')
            target_layout.insertWidget(2, self.remote_gain_frame)

            if ch == '5' or ch == '6':
                self.remoteGain_5.hide()
            else:
                self.remoteGain_5.show()
            if ch == '3' or ch == '4':
                self.remoteGain_3.hide()
            else:
                self.remoteGain_3.show()
            if ch == '1' or ch == '2':
                self.remoteGain_1.hide()
            else:
                self.remoteGain_1.show()
                
    def block_signals_ref_xo(self, block=True):
        self.Ref_xo_hpFreq.blockSignals(block)
        self.Ref_xo_lpFreq.blockSignals(block)
        self.Ref_xo_hpCurve.blockSignals(block)
        self.Ref_xo_lpCurve.blockSignals(block)
    
    def tab_changed(self):
        sender = self.sender()
        tab_name = sender.currentWidget().objectName()
        self.write_ini('Tab', 'last', tab_name)
        self.move_option_frame(sender.currentWidget().objectName())
        self.move_remote_crossover_frame(sender.currentWidget().objectName())
        self.move_remote_gain_frame(sender.currentWidget().objectName())
        if 'Crossovers' in tab_name:
            for ch in range(0, 6):
                ctrl = getattr(self, 'frame_Crossover0' + str(ch+1) )
                self.xoLayout.insertWidget(ch, ctrl)
        return

    def show_last_tab(self):
        # Show last viewed tab...
        last_tab = self.read_ini('Tab', 'last')
        this_tab = getattr(self, last_tab)
        tab_index = self.tabWidget.indexOf(this_tab)
        self.tabWidget.setCurrentIndex(tab_index)






    def show_last_ui_config(self):
        self.rename_outputs()
        # Set checkboxes (non hardware) to last used state.
        checkboxes = self.read_ini('Checkbox')
        for box in checkboxes:
            ui_box = getattr(self, box)
            ui_box.setCheckState(int(checkboxes[box]))

        spectrum = self.read_ini('Spectrum')
        for item in spectrum:
            widget = getattr(self, item)
            if isinstance(widget, QtWidgets.QComboBox):
                widget.setCurrentIndex( int(spectrum[item]) )
            elif isinstance(widget, QtWidgets.QSpinBox):
                widget.setValue( int(spectrum[item]) )
            elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                widget.setValue( float(spectrum[item]) )








    def toggle_tab(self, channel, show=0, new_index=None, tab_title=None):
        this_tab = getattr(self, 'tab_ch' + channel)
        tab_index = self.tabWidget.indexOf(this_tab)
        input_chans = set(['B', 'C', 'S'])
        if input_chans.issuperset(channel):
            tab_title = 'in:' + channel
            if channel == 'S' and self.Setup_inSumSelect.currentIndex() != 0:
                tab_title += 'um'
            if show:
                self.tabWidget.insertTab(new_index, this_tab, tab_title)
            else:
                self.tabWidget.removeTab(tab_index)
            return
        if show:
            self.tabWidget.insertTab(new_index, this_tab, tab_title)
        else:
            self.tabWidget.removeTab(tab_index)
        return

    def update_gui(self):
        dcx.comlink_write_enabled = False
        self.xo_lock_enable = False
        dcx.port_connect()
        dcx.sync_cache_from_dcx()
        self.wire_dcx_control_widgets_to_targets(update=True)
        self.xo_lock_enable = True
        dcx.comlink_write_enabled = True

    def button_handler(self):
        sender = self.sender()
        name = sender.objectName()
        #print('button_handler:' + sender.objectName() )
        dcx.set_setting(name, sender.isChecked())
        val = dcx.get_setting(name)
        if 'Mute' not in name:
            sender.setText(str(val[1]))
        else:
            #sender.setChecked(val[1])
            pass
   
    def gain_val_control_handler(self, _widget=None):
        sender = self.sender()
        try:
            name = sender.objectName()
            if name[-2:-1] == '_':
                name = name[:-2]

            dcx.set_setting(name, sender.value())

            try:  # Populates label values on knob adjustment.
                val = dcx.get_setting(name)[1]
                label = getattr(self, 'label_' + name)
                label.setText(str(val) + 'db')
                label = getattr(self, 'label_' + name + '_2')
                label.setText(str(val) + 'db')
            except:
                pass
        except:  # Populates label values on app start.
            try:
                name = _widget.objectName()
                if name[-2:-1] == '_':
                    name = name[:-2]
                #print('label_updateStart:', name)
                val = dcx.get_setting(name)[1]
                label = getattr(self, 'label_' + name)
                label.setText(str(val) + 'db')
                label = getattr(self, 'label_' + name + '_2')
                label.setText(str(val) + 'db')
            except:
                pass

    def eq_bands_spinBox_handler(self): # TODO FIXME
        sender = self.sender()
        channel = sender.objectName()[-1:]
        this_frame = getattr(self, 'frame_Eqs_ch' + channel)
        widgets = this_frame.children()
        if sender.value() == 0:
            dcx.set_setting('EqSwitch.ch' + channel, 0)
        else:
            dcx.set_setting('EqSwitch.ch' + channel, 1)
            dcx.set_settings(['EqIndex.ch' + channel, sender.value() - 1], ['EqNumber.ch' + channel, sender.value() - 1])
        band = []
        for widget in widgets:
            if 'frame_Eq' in widget.objectName():
                band.append(widget)
        for n in range(0, len(band)):
            if sender.value() - 1 >= n:
                band[n].show()
                # band[n].move(9-n, 0)
            else:
                band[n].hide()
        self.eq_visualize(channel)

    def eq_val_control_handler(self, _widget=None):
        sender = self.sender()
        try:  # Handler section
            name = sender.objectName()
            #print('eq_val_control_handler: ', name, '  ', sender.value() )
            dcx.set_setting(name, sender.value())
            channel = sender.objectName()[-1:]
            self.eq_visualize(channel)
            widgets = sender.parent().findChildren(QtWidgets.QWidget)
            for widget in widgets:
                if 'label' in widget.objectName():
                    if sender.objectName() in widget.objectName():
                        if 'freq' in widget.objectName():
                            prefix = ''
                            suffix = 'Hz'
                        elif 'gain' in widget.objectName():
                            #print('eq_val_control_handler: ' + widget.objectName() )
                            prefix = ''
                            suffix = 'db'
                        elif 'Q' in widget.objectName():
                            prefix = 'Q:'
                            suffix = '     [' + name[2:3] + ']'
                        widget.setText(prefix + str(dcx.get_setting(name.replace('_', '.'))[1]) + suffix)
        except:  # Startup section.
            try:
                name = _widget.objectName()
            except:
                return
            widgets = _widget.parent().findChildren(QtWidgets.QWidget)
            for widget in widgets:
                if _widget:
                    if 'label' in widget.objectName():
                        if _widget.objectName() in widget.objectName():
                            if 'freq' in _widget.objectName():
                                prefix = ''
                                suffix = 'Hz'
                            elif 'gain' in widget.objectName():
                                prefix = ''
                                suffix = 'db'
                            elif 'Q' in widget.objectName():
                                prefix = 'Q:'
                                suffix = '     [' + name[2:3] + ']'
                            widget.setText(prefix + str(dcx.get_setting(name.replace('_', '.'))[1]) + suffix)

    def eq_index_handler(self):
        sender = self.sender()
        try:
            dcx.set_setting(sender.objectName(), sender.currentIndex())
            channel = sender.objectName()[-1:]
            self.eq_visualize(channel)
        except:
            print('mainDCX: eq_index_handler()[X]:', sender.objectName())
    
    def eq_bypass_handler(self):
        sender = self.sender()
        channel = sender.objectName()[-1:]
        index = sender.objectName()[2:3]
        print('eq_bypass_handler, chan: ' + channel + '  Index: ' + index)
        print()
        
    def xo_index_handler(self):
        sender = self.sender()
        try:
            dcx.set_setting(sender.objectName(), sender.currentIndex())
            channel = sender.objectName()[-1:]
        except:
            print('mainDCX: xo_index_handler():', sender)
        self.xo_visualize(channel)

    def xo_val_control_handler(self):
        sender = self.sender()
        # print('info: xo_val_control_handler, sender=', sender.objectName())s
        try:
            dcx.set_setting(sender.objectName(), sender.value())
            channel = sender.objectName()[-1:]
            self.xo_visualize(channel)
            # print('info: xo_val_control_handler, sender=', sender)
        except:
            print('info: xo_val_control_handler, sender=', sender)
            pass

    def index_handler(self):
        sender = self.sender()
        index = sender.currentIndex()
        dcx.set_setting(sender.objectName(), index)
        if 'Config' in sender.objectName():
            chans = ['1', '2', '3', '4', '5', '6']
            for chan in chans:
                dcx.set_setting('Mute.ch' + chan, 0)

    def insum_index_handler(self):
        sender = self.sender()
        index = sender.currentIndex()
        dcx.set_setting(sender.objectName(), index)
        if index == 0:
            self.toggle_tab('S', show=0)
            new_text = self.tabWidget.tabText(0).replace('-Sum', '')
            self.tabWidget.setTabText(0, new_text)
        elif index > 0:
            if self.Setup_inStereoLink.currentIndex != 2:
                aux1_tab = getattr(self, 'tab_ch1')
                tab_index = self.tabWidget.indexOf(aux1_tab)
                new_indx = tab_index - 1
                self.toggle_tab('S', show=1, new_index=new_indx)
                if 'Sum' not in self.tabWidget.tabText(0) and self.Setup_inStereoLink.currentIndex() == 3:
                    new_text = self.tabWidget.tabText(0) + '-Sum'
                    self.tabWidget.setTabText(0, new_text)

    def hide_show_c_handler(self):
        sender = self.sender()
        self.write_ini('Checkbox', self.sender().objectName(), self.sender().checkState())
        c_tab = getattr(self, 'tab_chC')
        tab_index = self.tabWidget.indexOf(getattr(self, 'tab_chB'))
        if tab_index <= 0: tab_index = 0
        print('>> ', tab_index)
        if sender.isChecked():
            self.tabWidget.removeTab(tab_index+1)
        else:
            self.tabWidget.insertTab(tab_index+1, c_tab, 'In:C')

    def linkCopyA_B_handler(self):
        self.Setup_inStereoLink.setCurrentIndex(0)
        self.mirror_left_to_next('A')

    def instereolink_index_handler(self):
        sender = self.sender()
        index = sender.currentIndex()
        dcx.set_setting(sender.objectName(), index)
        if index:
            self.linkCopyA_B_checkbox.setChecked(0)
            self.hide_c_checkbox.setChecked(0)
        if index == 1:
            self.tabWidget.setTabText(0, 'in:A-B')
            self.toggle_tab('B', show=0)
            self.toggle_tab('C', show=1, new_index=1)
            if dcx.get_setting('Setup_inSumSelect')[0] != 0:
                aux1_tab = getattr(self, 'tab_ch1')
                tab_index = self.tabWidget.indexOf(aux1_tab)
                new_indx = tab_index - 1
                self.toggle_tab('S', show=1, new_index=new_indx)
        elif index == 2:
            self.tabWidget.setTabText(0, 'in:A-B-C')
            self.toggle_tab('B', show=0)
            self.toggle_tab('C', show=0)
            if dcx.get_setting('Setup_inSumSelect')[0] != 0:
                aux1_tab = getattr(self, 'tab_ch1')
                tab_index = self.tabWidget.indexOf(aux1_tab)
                new_indx = tab_index - 1
                self.toggle_tab('S', show=1, new_index=new_indx)
        elif index == 3:
            if dcx.get_setting('Setup_inSumSelect')[0] != 0:
                self.tabWidget.setTabText(0, 'in:A-B-C-Sum')
            else:
                self.tabWidget.setTabText(0, 'in:A-B-C')
            self.toggle_tab('B', show=0)
            self.toggle_tab('C', show=0)
            self.toggle_tab('S', show=0)
        elif index == 0:
            self.tabWidget.setTabText(0, 'in:A')
            self.toggle_tab('B', show=1, new_index=1)
            self.toggle_tab('C', show=1, new_index=2)
            if dcx.get_setting('Setup_inSumSelect')[0] != 0:
                aux1_tab = getattr(self, 'tab_ch1')
                tab_index = self.tabWidget.indexOf(aux1_tab)
                new_indx = tab_index - 1
                self.toggle_tab('S', show=1, new_index=new_indx)

    def align_val_control_handler(self, _widget=None):
        try:
            sender = self.sender()
            name = sender.objectName()
        except:
            sender = _widget
            name = sender.objectName()
        try:
            dcx.set_setting(name, sender.value())
            val = dcx.get_setting(name)
            self.label_update(name, val[1])
            if 'delay' in name:
                if val[0] == 0:
                    dcx.set_setting(('DelaySw.ch' + name[-1:]), 0)
                else:
                    dcx.set_setting(('DelaySw.ch' + name[-1:]), 1)
        except:
            pass

    def label_update(self, name, value):
        label = getattr(self, 'label_' + name)
        if 'delay' in name:
            ms = round(value * 0.00291, 2)
            label.setText('delay:' + str(value) + 'mm   ' + str(ms) + 'ms')
        elif 'phase' in name:
            label.setText('phase:' + str(value) + '°')

    def checkbox_handler(self):
        sender = self.sender()
        if sender.checkState():
            val = 1
        else:
            val = 0
        dcx.set_setting(sender.objectName(), val)
        #print(sender.objectName)
        #lock_chans = set(['3', '5'])
        #if lock_chans.issuperset(sender.objectName()[-1:]):
            #print('checkbox_handler:', sender.objectName()[-1:] )
            #r_chan = sender.objectName()[:-1] + str(int(sender.objectName()[-1:]) + 1)
            #dcx.set_setting(r_chan, val)

    def balance_control_handler(self):
        print('balance_control_handler(): UNUSED FUNCTION')
        sender = self.sender()
        l_bal = sender.value()
        r_bal = l_bal
        
        self.balance.setValue(l_bal)
        self.balance_2.setValue(l_bal)
        self.balance_3.setValue(l_bal)
        self.balance_4.setValue(l_bal)
        self.balance_5.setValue(l_bal)
        self.balance_6.setValue(l_bal)
        self.balance_7.setValue(l_bal)
        self.balance_8.setValue(l_bal)
        self.balance_9.setValue(l_bal)
        
        l_gain_dial = self.Gain_chA.value()
        r_gain_dial = self.Gain_chB.value()
        
        l_gain = dcx.get_setting('Gain.chA')[1]
        r_gain = dcx.get_setting('Gain.chB')[1]
        
        #print('balance_control_handler r: ', (r_gain) )
        
        dcx.set_setting('Gain.chA', l_gain_dial-l_bal)
        dcx.set_setting('Gain.chB', r_gain_dial+r_bal)

    def wire_option_widgets_to_targets(self):
        self.muteInsButton.toggled.connect(self.mute_inputs)
        self.muteOutsButton.toggled.connect(self.mute_outputs)
        self.updateGuiButton.pressed.connect(self.update_gui)
        self.tabWidget.currentChanged.connect(self.tab_changed)
        self.saveSetButton.pressed.connect(self.save_set_file_handler)
        self.loadSetButton.pressed.connect(self.load_set_file_handler)
        self.metersButton.pressed.connect(self.meters.toggle_meters)
        self.xo_link_Low.stateChanged.connect(self.xo_link_lphp_low)
        self.xo_link_High.stateChanged.connect(self.xo_link_lphp_high)
        self.linkCopy1_2_checkbox.stateChanged.connect(lambda: self.mirror_left_to_next('1'))
        self.linkCopy3_4_checkbox.stateChanged.connect(lambda: self.mirror_left_to_next('3'))
        self.linkCopy5_6_checkbox.stateChanged.connect(lambda: self.mirror_left_to_next('5'))
        self.xo_hideRightChans_checkbox.stateChanged.connect(self.xo_hideRightChans)
        # self.linkCopyA_B_checkbox.stateChanged.connect(lambda: self.mirror_left_to_next('A'))
        self.linkCopyA_B_checkbox.stateChanged.connect(self.linkCopyA_B_handler)
        self.hide_c_checkbox.stateChanged.connect(self.hide_show_c_handler)

    def wire_spectrum_analyzer_widgets_to_targets(self):#TODO
        self.spectrumPowerButton.toggled.connect(self.spectrum_power_button_handler)
        self.smoothingFactorSpinBox_S.valueChanged.connect(self.spectrum_smoothing_factor_handler)
        self.meanAveragesSpinBox_A.valueChanged.connect(self.spectrum_averages_handler)
        self.expAverageSpinBox_E.valueChanged.connect(self.spectrum_exponential_handler)
        self.spectrumVShift.valueChanged.connect(self.spectrum_vertical_shift_handler)
        self.blockLengthComboBox_B.currentIndexChanged.connect(self.spectrum_fft_length_handler)
        self.spectrumFreezePlotButton.toggled.connect(self.freeze_plot_button_handler)
        self.slopeSpinBox_s.valueChanged.connect(self.spectrum_slope_value_handler)
        self.windowTypeComboBox_W.currentIndexChanged.connect(self.spectrum_window_type_handler)
        self.resetAveragingButton_R.pressed.connect(self.spectrum_reset_averaging_handler)
        self.logModeComboBox_l.currentIndexChanged.connect(self.spectrum_log_mode_handler)
        self.peakHoldModeComboBox_P.currentIndexChanged.connect(self.spectrum_peak_mode_handler)
        self.diffModeComboBox_D.currentIndexChanged.connect(self.spectrum_difference_mode_handler)


        self.Ref_xo_hpFreq.valueChanged.connect(self.xo_ref_visualize)
        self.Ref_xo_lpFreq.valueChanged.connect(self.xo_ref_visualize)
        self.Ref_xo_hpCurve.currentIndexChanged.connect(self.xo_ref_visualize)
        self.Ref_xo_lpCurve.currentIndexChanged.connect(self.xo_ref_visualize)
        
    def wire_dcx_control_widgets_to_targets(self, update=False):
        widgets = self.findChildren(QtWidgets.QWidget)
        
        for widget in widgets:                
            name = widget.objectName()
            if name[-2:-1] == '_':
                name = name[:-2]
            val = dcx.get_setting(name)
            channel = name[-1:]  
            if val: # if hardware setting exists + reply not  None
                if isinstance(widget, QtWidgets.QComboBox):
                    if update == False:
                        self.wire_combobox(widget, name, val, channel)

                elif isinstance(widget, (QtWidgets.QDial, QtWidgets.QSlider)):
                    self.wire_slider(widget, name, val, channel)

                elif isinstance(widget, (Qwt.QwtKnob, Qwt.QwtDial, Qwt.QwtWheel, Qwt.QwtSlider) ):
                    self.wire_slider(widget, name, val, channel)                    

                elif isinstance(widget, QtWidgets.QSpinBox):
                    self.wire_spinbox(widget, name, val, channel)

                elif isinstance(widget, QtWidgets.QCheckBox):
                    self.wire_checkbox(widget, name, val, channel)

                elif isinstance(widget, QtWidgets.QPushButton):
                    self.wire_pushbutton(widget, name, val, channel)
            else:  # for non 'dcx_map' controls
                if isinstance(widget, QtWidgets.QLineEdit):
                    if 'lineEdit' in name:
                        widget.editingFinished.connect(self.rename_outputs)
                elif isinstance(widget, QtWidgets.QPushButton):
                    if 'bypass' in name:
                        widget.pressed.connect(self.eq_bypass_handler)
                # elif isinstance(widget, (Qwt.QwtKnob, Qwt.QwtDial, Qwt.QwtWheel, Qwt.QwtSlider) ):
                    # if 'xoRemote' in name:
                        # widget.valueChanged.connect(self.xo_remote_handler)
                    # if 'balance' in name:
                        # widget.valueChanged.connect(self.balance_control_handler)

    def wire_combobox(self, widget, name, val, channel):
        if widget.count() == 0:
            self.populate_combobox(widget)
        widget.setCurrentIndex(val[0])
        if 'Crossover' in name or 'Align' in name:
            self.xo_visualize(channel)
            widget.currentIndexChanged.connect(self.xo_index_handler)
        elif 'Eq' in name:
            setattr(self, name, self.findChild(QtWidgets.QComboBox, name))
            widget.currentIndexChanged.connect(self.eq_index_handler)
        elif 'inStereoLink' in name:
            widget.currentIndexChanged.connect(self.instereolink_index_handler)
            # widget.setCurrentIndex(0)
            # widget.setCurrentIndex(1)
            widget.setCurrentIndex(val[0])
        elif 'inSumSelect' in name:
            widget.setCurrentIndex(1)
            # widget.setCurrentIndex(2)
            widget.currentIndexChanged.connect(self.insum_index_handler)
            widget.setCurrentIndex(val[0])
        else:
            widget.currentIndexChanged.connect(self.index_handler)

    def wire_slider(self, widget, name, val, channel):
        if 'Gain' in name:
            widget.setValue(val[1])
            widget.valueChanged.connect(self.gain_val_control_handler)

            try:  # Populates label values on knob adjustment.
                val = dcx.get_setting(name)[1]
                label = getattr(self, 'label_' + name)
                label.setText(str(val) + 'db')
                label = getattr(self, 'label_' + name + '_2')
                label.setText(str(val) + 'db')
            except:
                pass
            
        elif 'Eq' in name:
            if 'freq' in name:
                value = val[0]
            elif '_Q' in name:
                value = val[0]
            else:
                value = val[1]
            widget.valueChanged.connect(self.eq_val_control_handler)
            widget.setValue((value))
        elif 'Crossover' in name:
            widget.setValue(val[0])
            widget.valueChanged.connect(self.xo_val_control_handler)
        elif 'Align' in name:
            self.label_update(name, val[1])
            widget.setValue(val[0])
            widget.valueChanged.connect(self.align_val_control_handler)
            #self.align_val_control_handler(_widget=widget)

    def wire_spinbox(self, widget, name, val, channel): # TODO FIXME
        if 'EqNum' in name:
            sw_val = dcx.get_setting('EqSwitch.ch' + channel)[0]
            widget.valueChanged.connect(self.eq_bands_spinBox_handler)
            widget.setValue(val[0] + sw_val + 1)
            widget.setValue(val[0] + sw_val)
            #self.eq_visualize(channel)  FIXME
        else:
            widget.setValue(val[0])
            widget.valueChanged.connect(self.spinBox_handler)

    def wire_checkbox(self, widget, name, val, channel):
        #print('wire_checkbox'+ name)
        if val[0]:
            widget.setCheckState(2)
        else:
            widget.setCheckState(0)
        widget.stateChanged.connect(self.checkbox_handler)

    def wire_pushbutton(self, widget, name, val, channel):
        #print('wire pushbutton'+ name)
        #widget.pressed.connect(self.button_handler)
        widget.toggled.connect(self.button_handler)
        val = dcx.get_setting(widget.objectName())
        if 'Mute' not in name:
            widget.setText(val[1])
            print('Mute not in name: ', name)
        else:
            widget.setChecked(val[1])

    def populate_combobox(self, widget):
        try:
            control = eval('dcx.Mapper.' + widget.objectName().replace('_', '.'))
            list1 = control.detents()
            for itm in list1:
                widget.addItem(str(itm))
        except:
            if 'Eq' and 'curve' in widget.objectName():
                list1 = dcx.eqCurveEnum()
                for itm in list1:
                    widget.addItem(str(itm))
                    
    def tick(self):
        self.timer = QtCore.QTimer()
        self.timer.singleShot(2, self.initiate_gui)
        #self.timer.timeout.connect(self.initiate_gui)
        #self.timer.start(1000)
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
    import os
    # os.system(r'pkill -f jnoise')
    os.system("pkill -f spectrum.out")
    os.system("pkill -f mainDCX.py")
    print('App Exited')
    # dcx.sync_cache_from_dcx()
    
    
    
    
