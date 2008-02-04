# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './newpropertydialog.ui'
#
# Created: Mon Feb  4 18:19:18 2008
#      by: PyQt4 UI code generator 4.3.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_NewPropertyDialog(object):
    def setupUi(self, NewPropertyDialog):
        NewPropertyDialog.setObjectName("NewPropertyDialog")
        NewPropertyDialog.resize(QtCore.QSize(QtCore.QRect(0,0,296,263).size()).expandedTo(NewPropertyDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(NewPropertyDialog)
        self.gridlayout.setObjectName("gridlayout")

        self.keyLabel = QtGui.QLabel(NewPropertyDialog)
        self.keyLabel.setObjectName("keyLabel")
        self.gridlayout.addWidget(self.keyLabel,0,0,1,1)

        self.keyLineEdit = QtGui.QLineEdit(NewPropertyDialog)
        self.keyLineEdit.setObjectName("keyLineEdit")
        self.gridlayout.addWidget(self.keyLineEdit,0,1,1,2)

        self.tyoeLabel = QtGui.QLabel(NewPropertyDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tyoeLabel.sizePolicy().hasHeightForWidth())
        self.tyoeLabel.setSizePolicy(sizePolicy)
        self.tyoeLabel.setObjectName("tyoeLabel")
        self.gridlayout.addWidget(self.tyoeLabel,1,0,1,1)

        self.valueLabel = QtGui.QLabel(NewPropertyDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.valueLabel.sizePolicy().hasHeightForWidth())
        self.valueLabel.setSizePolicy(sizePolicy)
        self.valueLabel.setObjectName("valueLabel")
        self.gridlayout.addWidget(self.valueLabel,1,2,1,1)

        self.boolTypeButton = QtGui.QRadioButton(NewPropertyDialog)
        self.boolTypeButton.setObjectName("boolTypeButton")
        self.gridlayout.addWidget(self.boolTypeButton,2,0,1,2)

        self.boolCheckBox = QtGui.QCheckBox(NewPropertyDialog)
        self.boolCheckBox.setEnabled(False)
        self.boolCheckBox.setObjectName("boolCheckBox")
        self.gridlayout.addWidget(self.boolCheckBox,2,2,1,1)

        self.doubleTypeButton = QtGui.QRadioButton(NewPropertyDialog)
        self.doubleTypeButton.setObjectName("doubleTypeButton")
        self.gridlayout.addWidget(self.doubleTypeButton,3,0,1,2)

        self.doubleSpinBox = QtGui.QDoubleSpinBox(NewPropertyDialog)
        self.doubleSpinBox.setEnabled(False)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.gridlayout.addWidget(self.doubleSpinBox,3,2,1,1)

        self.intTypeButton = QtGui.QRadioButton(NewPropertyDialog)
        self.intTypeButton.setObjectName("intTypeButton")
        self.gridlayout.addWidget(self.intTypeButton,4,0,1,2)

        self.intSpinBox = QtGui.QSpinBox(NewPropertyDialog)
        self.intSpinBox.setEnabled(False)
        self.intSpinBox.setObjectName("intSpinBox")
        self.gridlayout.addWidget(self.intSpinBox,4,2,1,1)

        self.strTypeButton = QtGui.QRadioButton(NewPropertyDialog)
        self.strTypeButton.setObjectName("strTypeButton")
        self.gridlayout.addWidget(self.strTypeButton,5,0,1,2)

        self.strLineEdit = QtGui.QLineEdit(NewPropertyDialog)
        self.strLineEdit.setEnabled(False)
        self.strLineEdit.setObjectName("strLineEdit")
        self.gridlayout.addWidget(self.strLineEdit,5,2,1,1)

        self.tupleTypeButton = QtGui.QRadioButton(NewPropertyDialog)
        self.tupleTypeButton.setObjectName("tupleTypeButton")
        self.gridlayout.addWidget(self.tupleTypeButton,6,0,1,2)

        self.tupleLineEdit = QtGui.QLineEdit(NewPropertyDialog)
        self.tupleLineEdit.setEnabled(False)
        self.tupleLineEdit.setObjectName("tupleLineEdit")
        self.gridlayout.addWidget(self.tupleLineEdit,6,2,1,1)

        self.buttonBox = QtGui.QDialogButtonBox(NewPropertyDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox,7,0,1,3)

        self.retranslateUi(NewPropertyDialog)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),NewPropertyDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NewPropertyDialog)

    def retranslateUi(self, NewPropertyDialog):
        NewPropertyDialog.setWindowTitle(QtGui.QApplication.translate("NewPropertyDialog", "New property", None, QtGui.QApplication.UnicodeUTF8))
        self.keyLabel.setText(QtGui.QApplication.translate("NewPropertyDialog", "Property name:", None, QtGui.QApplication.UnicodeUTF8))
        self.tyoeLabel.setText(QtGui.QApplication.translate("NewPropertyDialog", "Type:", None, QtGui.QApplication.UnicodeUTF8))
        self.valueLabel.setText(QtGui.QApplication.translate("NewPropertyDialog", "Value:", None, QtGui.QApplication.UnicodeUTF8))
        self.boolTypeButton.setText(QtGui.QApplication.translate("NewPropertyDialog", "Boolean", None, QtGui.QApplication.UnicodeUTF8))
        self.boolCheckBox.setText(QtGui.QApplication.translate("NewPropertyDialog", "True/False", None, QtGui.QApplication.UnicodeUTF8))
        self.doubleTypeButton.setText(QtGui.QApplication.translate("NewPropertyDialog", "Double", None, QtGui.QApplication.UnicodeUTF8))
        self.intTypeButton.setText(QtGui.QApplication.translate("NewPropertyDialog", "Integer", None, QtGui.QApplication.UnicodeUTF8))
        self.strTypeButton.setText(QtGui.QApplication.translate("NewPropertyDialog", "String", None, QtGui.QApplication.UnicodeUTF8))
        self.tupleTypeButton.setText(QtGui.QApplication.translate("NewPropertyDialog", "Tuple (string list)", None, QtGui.QApplication.UnicodeUTF8))

