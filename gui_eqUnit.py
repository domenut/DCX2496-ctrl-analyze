# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DCXeqUnit.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
from PyQt5.Qwt import *


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EqFrame(object):
    def setupUi(self, EqFrame):
        EqFrame.setObjectName("EqFrame")
        EqFrame.resize(100, 237)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(EqFrame.sizePolicy().hasHeightForWidth())
        EqFrame.setSizePolicy(sizePolicy)
        EqFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.horizontalLayout = QtWidgets.QHBoxLayout(EqFrame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_7 = QtWidgets.QFrame(EqFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_7.sizePolicy().hasHeightForWidth())
        self.frame_7.setSizePolicy(sizePolicy)
        self.frame_7.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_7)
        self.verticalLayout_7.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout_7.setSpacing(2)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.Eq_band_curve_channel_ = QtWidgets.QComboBox(self.frame_7)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Eq_band_curve_channel_.sizePolicy().hasHeightForWidth())
        self.Eq_band_curve_channel_.setSizePolicy(sizePolicy)
        self.Eq_band_curve_channel_.setMaximumSize(QtCore.QSize(50, 16777215))
        self.Eq_band_curve_channel_.setEditable(False)
        self.Eq_band_curve_channel_.setFrame(False)
        self.Eq_band_curve_channel_.setObjectName("Eq_band_curve_channel_")
        self.verticalLayout_7.addWidget(self.Eq_band_curve_channel_)
        self.label_Eq_band_Q_channel_ = QtWidgets.QLabel(self.frame_7)
        self.label_Eq_band_Q_channel_.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Eq_band_Q_channel_.setObjectName("label_Eq_band_Q_channel_")
        self.verticalLayout_7.addWidget(self.label_Eq_band_Q_channel_)
        self.Eq_band_Q_channel_ = QwtWheel(self.frame_7)
        self.Eq_band_Q_channel_.setMaximum(40.0)
        self.Eq_band_Q_channel_.setObjectName("Eq_band_Q_channel_")
        self.verticalLayout_7.addWidget(self.Eq_band_Q_channel_)
        self.Eq_band_gain_channel_ = QwtSlider(self.frame_7)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Eq_band_gain_channel_.sizePolicy().hasHeightForWidth())
        self.Eq_band_gain_channel_.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.Eq_band_gain_channel_.setFont(font)
        self.Eq_band_gain_channel_.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Eq_band_gain_channel_.setStyleSheet("color: rgb(127, 139, 153);")
        self.Eq_band_gain_channel_.setLowerBound(-15.0)
        self.Eq_band_gain_channel_.setUpperBound(15.0)
        self.Eq_band_gain_channel_.setScaleMaxMajor(6)
        self.Eq_band_gain_channel_.setScaleMaxMinor(5)
        self.Eq_band_gain_channel_.setTotalSteps(300)
        self.Eq_band_gain_channel_.setStepAlignment(True)
        self.Eq_band_gain_channel_.setOrientation(QtCore.Qt.Vertical)
        self.Eq_band_gain_channel_.setScalePosition(QwtSlider.TrailingScale)
        self.Eq_band_gain_channel_.setTrough(True)
        self.Eq_band_gain_channel_.setGroove(False)
        self.Eq_band_gain_channel_.setHandleSize(QtCore.QSize(0, 0))
        self.Eq_band_gain_channel_.setBorderWidth(2)
        self.Eq_band_gain_channel_.setObjectName("Eq_band_gain_channel_")
        self.verticalLayout_7.addWidget(self.Eq_band_gain_channel_)
        self.label_Eq_band_gain_channel_ = QtWidgets.QLabel(self.frame_7)
        self.label_Eq_band_gain_channel_.setObjectName("label_Eq_band_gain_channel_")
        self.verticalLayout_7.addWidget(self.label_Eq_band_gain_channel_)
        self.Eq_band_freq_channel_ = QwtWheel(self.frame_7)
        self.Eq_band_freq_channel_.setOrientation(QtCore.Qt.Horizontal)
        self.Eq_band_freq_channel_.setMaximum(320.0)
        self.Eq_band_freq_channel_.setObjectName("Eq_band_freq_channel_")
        self.verticalLayout_7.addWidget(self.Eq_band_freq_channel_)
        self.label_Eq_band_freq_channel_ = QtWidgets.QLabel(self.frame_7)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_Eq_band_freq_channel_.setFont(font)
        self.label_Eq_band_freq_channel_.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Eq_band_freq_channel_.setObjectName("label_Eq_band_freq_channel_")
        self.verticalLayout_7.addWidget(self.label_Eq_band_freq_channel_)
        self.horizontalLayout.addWidget(self.frame_7)

        self.retranslateUi(EqFrame)
        self.Eq_band_curve_channel_.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(EqFrame)

    def retranslateUi(self, EqFrame):
        _translate = QtCore.QCoreApplication.translate
        EqFrame.setWindowTitle(_translate("EqFrame", "Frame"))
        self.label_Eq_band_Q_channel_.setText(_translate("EqFrame", "Q_val"))
        self.label_Eq_band_gain_channel_.setText(_translate("EqFrame", "gain_val"))
        self.label_Eq_band_freq_channel_.setText(_translate("EqFrame", "frq_val"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EqFrame = QtWidgets.QFrame()
    ui = Ui_EqFrame()
    ui.setupUi(EqFrame)
    EqFrame.show()
    sys.exit(app.exec_())
