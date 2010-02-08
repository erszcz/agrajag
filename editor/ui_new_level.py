# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_level.ui'
#
# Created: Sun May 18 13:41:04 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_New_level(object):
    def setupUi(self, New_level):
        New_level.setObjectName("New_level")
        New_level.resize(QtCore.QSize(QtCore.QRect(0,0,292,106).size()).expandedTo(New_level.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(New_level.sizePolicy().hasHeightForWidth())
        New_level.setSizePolicy(sizePolicy)
        New_level.setBaseSize(QtCore.QSize(200,100))
        New_level.setModal(True)

        self.gridlayout = QtGui.QGridLayout(New_level)
        self.gridlayout.setObjectName("gridlayout")

        self.label = QtGui.QLabel(New_level)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)

        self.widthSpinBox = QtGui.QSpinBox(New_level)
        self.widthSpinBox.setMinimum(400)
        self.widthSpinBox.setMaximum(2048)
        self.widthSpinBox.setProperty("value",QtCore.QVariant(800))
        self.widthSpinBox.setObjectName("widthSpinBox")
        self.gridlayout.addWidget(self.widthSpinBox,0,1,1,1)

        self.label_2 = QtGui.QLabel(New_level)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,1,0,1,1)

        self.heightSpinBox = QtGui.QSpinBox(New_level)
        self.heightSpinBox.setMinimum(400)
        self.heightSpinBox.setMaximum(999999999)
        self.heightSpinBox.setProperty("value",QtCore.QVariant(5000))
        self.heightSpinBox.setObjectName("heightSpinBox")
        self.gridlayout.addWidget(self.heightSpinBox,1,1,1,1)

        spacerItem = QtGui.QSpacerItem(129,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,2,0,1,1)

        self.buttonBox = QtGui.QDialogButtonBox(New_level)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox,2,1,1,1)

        self.retranslateUi(New_level)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),New_level.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),New_level.reject)
        QtCore.QMetaObject.connectSlotsByName(New_level)

    def retranslateUi(self, New_level):
        New_level.setWindowTitle(QtGui.QApplication.translate("New_level", "New level", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("New_level", "Level width:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("New_level", "Level height:", None, QtGui.QApplication.UnicodeUTF8))

