# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DCXmeters.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
from PyQt5.Qwt import *


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MeterDialog(object):
    def setupUi(self, MeterDialog):
        MeterDialog.setObjectName("MeterDialog")
        MeterDialog.resize(272, 203)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MeterDialog.sizePolicy().hasHeightForWidth())
        MeterDialog.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtWidgets.QHBoxLayout(MeterDialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_A = QtWidgets.QFrame(MeterDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_A.sizePolicy().hasHeightForWidth())
        self.frame_A.setSizePolicy(sizePolicy)
        self.frame_A.setMaximumSize(QtCore.QSize(20, 16777215))
        self.frame_A.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_A.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_A.setObjectName("frame_A")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_A)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.Meter_A = QwtThermo(self.frame_A)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Meter_A.sizePolicy().hasHeightForWidth())
        self.Meter_A.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.Meter_A.setFont(font)
        self.Meter_A.setStyleSheet("color: rgb(190, 126, 95);")
        self.Meter_A.setLowerBound(0.0)
        self.Meter_A.setUpperBound(6.0)
        self.Meter_A.setScaleMaxMajor(0)
        self.Meter_A.setScaleMaxMinor(19)
        self.Meter_A.setScaleStepSize(0.0)
        self.Meter_A.setScalePosition(QwtThermo.LeadingScale)
        self.Meter_A.setOriginMode(QwtThermo.OriginMinimum)
        self.Meter_A.setAlarmLevel(5.0)
        self.Meter_A.setOrigin(0.0)
        self.Meter_A.setBorderWidth(2)
        self.Meter_A.setPipeWidth(10)
        self.Meter_A.setProperty("value", -1.0)
        self.Meter_A.setObjectName("Meter_A")
        self.verticalLayout.addWidget(self.Meter_A)
        self.label_A = QtWidgets.QLabel(self.frame_A)
        self.label_A.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_A.setFont(font)
        self.label_A.setTextFormat(QtCore.Qt.PlainText)
        self.label_A.setAlignment(QtCore.Qt.AlignCenter)
        self.label_A.setObjectName("label_A")
        self.verticalLayout.addWidget(self.label_A)
        self.horizontalLayout.addWidget(self.frame_A)
        self.frame_B = QtWidgets.QFrame(MeterDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_B.sizePolicy().hasHeightForWidth())
        self.frame_B.setSizePolicy(sizePolicy)
        self.frame_B.setMaximumSize(QtCore.QSize(20, 16777215))
        self.frame_B.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_B.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_B.setObjectName("frame_B")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_B)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Meter_B = QwtThermo(self.frame_B)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Meter_B.sizePolicy().hasHeightForWidth())
        self.Meter_B.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.Meter_B.setFont(font)
        self.Meter_B.setStyleSheet("color: rgb(190, 126, 95);")
        self.Meter_B.setLowerBound(0.0)
        self.Meter_B.setUpperBound(6.0)
        self.Meter_B.setScaleMaxMajor(0)
        self.Meter_B.setScaleMaxMinor(19)
        self.Meter_B.setScaleStepSize(0.0)
        self.Meter_B.setScalePosition(QwtThermo.LeadingScale)
        self.Meter_B.setOriginMode(QwtThermo.OriginMinimum)
        self.Meter_B.setAlarmLevel(5.0)
        self.Meter_B.setOrigin(0.0)
        self.Meter_B.setBorderWidth(2)
        self.Meter_B.setPipeWidth(10)
        self.Meter_B.setProperty("value", -1.0)
        self.Meter_B.setObjectName("Meter_B")
        self.verticalLayout_2.addWidget(self.Meter_B)
        self.label_B = QtWidgets.QLabel(self.frame_B)
        self.label_B.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_B.setFont(font)
        self.label_B.setTextFormat(QtCore.Qt.PlainText)
        self.label_B.setAlignment(QtCore.Qt.AlignCenter)
        self.label_B.setObjectName("label_B")
        self.verticalLayout_2.addWidget(self.label_B)
        self.horizontalLayout.addWidget(self.frame_B)
        self.frame_C = QtWidgets.QFrame(MeterDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_C.sizePolicy().hasHeightForWidth())
        self.frame_C.setSizePolicy(sizePolicy)
        self.frame_C.setMaximumSize(QtCore.QSize(20, 16777215))
        self.frame_C.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_C.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_C.setObjectName("frame_C")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_C)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.Meter_C = QwtThermo(self.frame_C)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Meter_C.sizePolicy().hasHeightForWidth())
        self.Meter_C.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.Meter_C.setFont(font)
        self.Meter_C.setStyleSheet("color: rgb(190, 126, 95);")
        self.Meter_C.setLowerBound(0.0)
        self.Meter_C.setUpperBound(6.0)
        self.Meter_C.setScaleMaxMajor(0)
        self.Meter_C.setScaleMaxMinor(19)
        self.Meter_C.setScaleStepSize(0.0)
        self.Meter_C.setScalePosition(QwtThermo.LeadingScale)
        self.Meter_C.setOriginMode(QwtThermo.OriginMinimum)
        self.Meter_C.setAlarmLevel(5.0)
        self.Meter_C.setOrigin(0.0)
        self.Meter_C.setBorderWidth(2)
        self.Meter_C.setPipeWidth(10)
        self.Meter_C.setProperty("value", -1.0)
        self.Meter_C.setObjectName("Meter_C")
        self.verticalLayout_3.addWidget(self.Meter_C)
        self.label_C = QtWidgets.QLabel(self.frame_C)
        self.label_C.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_C.setFont(font)
        self.label_C.setTextFormat(QtCore.Qt.PlainText)
        self.label_C.setAlignment(QtCore.Qt.AlignCenter)
        self.label_C.setObjectName("label_C")
        self.verticalLayout_3.addWidget(self.label_C)
        self.horizontalLayout.addWidget(self.frame_C)
        self.frame_1 = QtWidgets.QFrame(MeterDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_1.sizePolicy().hasHeightForWidth())
        self.frame_1.setSizePolicy(sizePolicy)
        self.frame_1.setMaximumSize(QtCore.QSize(20, 16777215))
        self.frame_1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_1.setObjectName("frame_1")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_1)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.Meter_1 = QwtThermo(self.frame_1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Meter_1.sizePolicy().hasHeightForWidth())
        self.Meter_1.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.Meter_1.setFont(font)
        self.Meter_1.setStyleSheet("color: rgb(170, 0, 0);")
        self.Meter_1.setLowerBound(0.0)
        self.Meter_1.setUpperBound(6.0)
        self.Meter_1.setScaleMaxMajor(0)
        self.Meter_1.setScaleMaxMinor(19)
        self.Meter_1.setScaleStepSize(0.0)
        self.Meter_1.setScalePosition(QwtThermo.LeadingScale)
        self.Meter_1.setOriginMode(QwtThermo.OriginMinimum)
        self.Meter_1.setAlarmLevel(5.0)
        self.Meter_1.setOrigin(0.0)
        self.Meter_1.setBorderWidth(2)
        self.Meter_1.setPipeWidth(10)
        self.Meter_1.setProperty("value", -1.0)
        self.Meter_1.setObjectName("Meter_1")
        self.verticalLayout_4.addWidget(self.Meter_1)
        self.label_1 = QtWidgets.QLabel(self.frame_1)
        self.label_1.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_1.setFont(font)
        self.label_1.setStyleSheet("color: rgb(255, 0, 0);")
        self.label_1.setTextFormat(QtCore.Qt.PlainText)
        self.label_1.setAlignment(QtCore.Qt.AlignCenter)
        self.label_1.setObjectName("label_1")
        self.verticalLayout_4.addWidget(self.label_1)
        self.horizontalLayout.addWidget(self.frame_1)
        self.frame_2 = QtWidgets.QFrame(MeterDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMaximumSize(QtCore.QSize(20, 16777215))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.Meter_2 = QwtThermo(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Meter_2.sizePolicy().hasHeightForWidth())
        self.Meter_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.Meter_2.setFont(font)
        self.Meter_2.setStyleSheet("color: rgb(170, 0, 0);")
        self.Meter_2.setLowerBound(0.0)
        self.Meter_2.setUpperBound(6.0)
        self.Meter_2.setScaleMaxMajor(0)
        self.Meter_2.setScaleMaxMinor(19)
        self.Meter_2.setScaleStepSize(0.0)
        self.Meter_2.setScalePosition(QwtThermo.LeadingScale)
        self.Meter_2.setOriginMode(QwtThermo.OriginMinimum)
        self.Meter_2.setAlarmLevel(5.0)
        self.Meter_2.setOrigin(0.0)
        self.Meter_2.setBorderWidth(2)
        self.Meter_2.setPipeWidth(10)
        self.Meter_2.setProperty("value", -1.0)
        self.Meter_2.setObjectName("Meter_2")
        self.verticalLayout_5.addWidget(self.Meter_2)
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color: rgb(255, 0, 0);")
        self.label_2.setTextFormat(QtCore.Qt.PlainText)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_5.addWidget(self.label_2)
        self.horizontalLayout.addWidget(self.frame_2)
        self.frame_3 = QtWidgets.QFrame(MeterDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setMaximumSize(QtCore.QSize(20, 16777215))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.Meter_3 = QwtThermo(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Meter_3.sizePolicy().hasHeightForWidth())
        self.Meter_3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.Meter_3.setFont(font)
        self.Meter_3.setStyleSheet("color: rgb(0, 170, 0);")
        self.Meter_3.setLowerBound(0.0)
        self.Meter_3.setUpperBound(6.0)
        self.Meter_3.setScaleMaxMajor(0)
        self.Meter_3.setScaleMaxMinor(19)
        self.Meter_3.setScaleStepSize(0.0)
        self.Meter_3.setScalePosition(QwtThermo.LeadingScale)
        self.Meter_3.setOriginMode(QwtThermo.OriginMinimum)
        self.Meter_3.setAlarmLevel(5.0)
        self.Meter_3.setOrigin(0.0)
        self.Meter_3.setBorderWidth(2)
        self.Meter_3.setPipeWidth(10)
        self.Meter_3.setProperty("value", -1.0)
        self.Meter_3.setObjectName("Meter_3")
        self.verticalLayout_6.addWidget(self.Meter_3)
        self.label_3 = QtWidgets.QLabel(self.frame_3)
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("color: rgb(0, 255, 0);")
        self.label_3.setTextFormat(QtCore.Qt.PlainText)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_6.addWidget(self.label_3)
        self.horizontalLayout.addWidget(self.frame_3)
        self.frame_4 = QtWidgets.QFrame(MeterDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy)
        self.frame_4.setMaximumSize(QtCore.QSize(20, 16777215))
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.Meter_4 = QwtThermo(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Meter_4.sizePolicy().hasHeightForWidth())
        self.Meter_4.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.Meter_4.setFont(font)
        self.Meter_4.setStyleSheet("color: rgb(0, 170, 0);")
        self.Meter_4.setLowerBound(0.0)
        self.Meter_4.setUpperBound(6.0)
        self.Meter_4.setScaleMaxMajor(0)
        self.Meter_4.setScaleMaxMinor(19)
        self.Meter_4.setScaleStepSize(0.0)
        self.Meter_4.setScalePosition(QwtThermo.LeadingScale)
        self.Meter_4.setOriginMode(QwtThermo.OriginMinimum)
        self.Meter_4.setAlarmLevel(5.0)
        self.Meter_4.setOrigin(0.0)
        self.Meter_4.setBorderWidth(2)
        self.Meter_4.setPipeWidth(10)
        self.Meter_4.setProperty("value", -1.0)
        self.Meter_4.setObjectName("Meter_4")
        self.verticalLayout_7.addWidget(self.Meter_4)
        self.label_4 = QtWidgets.QLabel(self.frame_4)
        self.label_4.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet("color: rgb(0, 255, 0);")
        self.label_4.setTextFormat(QtCore.Qt.PlainText)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_7.addWidget(self.label_4)
        self.horizontalLayout.addWidget(self.frame_4)
        self.frame_5 = QtWidgets.QFrame(MeterDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy)
        self.frame_5.setMaximumSize(QtCore.QSize(20, 16777215))
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_5.setObjectName("frame_5")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.frame_5)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.Meter_5 = QwtThermo(self.frame_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Meter_5.sizePolicy().hasHeightForWidth())
        self.Meter_5.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.Meter_5.setFont(font)
        self.Meter_5.setStyleSheet("color: rgb(0, 0, 207);")
        self.Meter_5.setLowerBound(0.0)
        self.Meter_5.setUpperBound(6.0)
        self.Meter_5.setScaleMaxMajor(0)
        self.Meter_5.setScaleMaxMinor(19)
        self.Meter_5.setScaleStepSize(0.0)
        self.Meter_5.setScalePosition(QwtThermo.LeadingScale)
        self.Meter_5.setOriginMode(QwtThermo.OriginMinimum)
        self.Meter_5.setAlarmLevel(5.0)
        self.Meter_5.setOrigin(0.0)
        self.Meter_5.setBorderWidth(2)
        self.Meter_5.setPipeWidth(10)
        self.Meter_5.setProperty("value", -1.0)
        self.Meter_5.setObjectName("Meter_5")
        self.verticalLayout_8.addWidget(self.Meter_5)
        self.label_5 = QtWidgets.QLabel(self.frame_5)
        self.label_5.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_5.setFont(font)
        self.label_5.setStyleSheet("color: rgb(0, 0, 255);")
        self.label_5.setTextFormat(QtCore.Qt.PlainText)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_8.addWidget(self.label_5)
        self.horizontalLayout.addWidget(self.frame_5)
        self.frame_6 = QtWidgets.QFrame(MeterDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy)
        self.frame_6.setMaximumSize(QtCore.QSize(20, 16777215))
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_6.setObjectName("frame_6")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.frame_6)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.Meter_6 = QwtThermo(self.frame_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Meter_6.sizePolicy().hasHeightForWidth())
        self.Meter_6.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.Meter_6.setFont(font)
        self.Meter_6.setStyleSheet("color: rgb(0, 0, 207);")
        self.Meter_6.setLowerBound(0.0)
        self.Meter_6.setUpperBound(6.0)
        self.Meter_6.setScaleMaxMajor(0)
        self.Meter_6.setScaleMaxMinor(19)
        self.Meter_6.setScaleStepSize(0.0)
        self.Meter_6.setScalePosition(QwtThermo.LeadingScale)
        self.Meter_6.setOriginMode(QwtThermo.OriginMinimum)
        self.Meter_6.setAlarmLevel(5.0)
        self.Meter_6.setOrigin(0.0)
        self.Meter_6.setBorderWidth(2)
        self.Meter_6.setPipeWidth(10)
        self.Meter_6.setProperty("value", -1.0)
        self.Meter_6.setObjectName("Meter_6")
        self.verticalLayout_9.addWidget(self.Meter_6)
        self.label_6 = QtWidgets.QLabel(self.frame_6)
        self.label_6.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_6.setFont(font)
        self.label_6.setStyleSheet("color: rgb(0, 0, 255);")
        self.label_6.setTextFormat(QtCore.Qt.PlainText)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_9.addWidget(self.label_6)
        self.horizontalLayout.addWidget(self.frame_6)

        self.retranslateUi(MeterDialog)
        QtCore.QMetaObject.connectSlotsByName(MeterDialog)

    def retranslateUi(self, MeterDialog):
        _translate = QtCore.QCoreApplication.translate
        MeterDialog.setWindowTitle(_translate("MeterDialog", "Levels"))
        self.label_A.setText(_translate("MeterDialog", "A"))
        self.label_B.setText(_translate("MeterDialog", "B"))
        self.label_C.setText(_translate("MeterDialog", "C"))
        self.label_1.setText(_translate("MeterDialog", "1"))
        self.label_2.setText(_translate("MeterDialog", "2"))
        self.label_3.setText(_translate("MeterDialog", "3"))
        self.label_4.setText(_translate("MeterDialog", "4"))
        self.label_5.setText(_translate("MeterDialog", "5"))
        self.label_6.setText(_translate("MeterDialog", "6"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MeterDialog = QtWidgets.QDialog()
    ui = Ui_MeterDialog()
    ui.setupUi(MeterDialog)
    MeterDialog.show()
    sys.exit(app.exec_())