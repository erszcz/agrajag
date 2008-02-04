# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './propertyeditordialog.ui'
#
# Created: Sun Feb  3 18:20:52 2008
#      by: PyQt4 UI code generator 4.3.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_PropertyEditorDialog(object):
    def setupUi(self, PropertyEditorDialog):
        PropertyEditorDialog.setObjectName("PropertyEditorDialog")
        PropertyEditorDialog.resize(QtCore.QSize(QtCore.QRect(0,0,360,401).size()).expandedTo(PropertyEditorDialog.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PropertyEditorDialog.sizePolicy().hasHeightForWidth())
        PropertyEditorDialog.setSizePolicy(sizePolicy)
        PropertyEditorDialog.setMinimumSize(QtCore.QSize(300,400))

        self.gridlayout = QtGui.QGridLayout(PropertyEditorDialog)
        self.gridlayout.setObjectName("gridlayout")

        self.propertyEditor = PropertyEditor(PropertyEditorDialog)
        self.propertyEditor.setObjectName("propertyEditor")
        self.gridlayout.addWidget(self.propertyEditor,0,0,4,1)

        self.newButton = QtGui.QPushButton(PropertyEditorDialog)
        self.newButton.setObjectName("newButton")
        self.gridlayout.addWidget(self.newButton,0,1,1,1)

        self.deleteButton = QtGui.QPushButton(PropertyEditorDialog)
        self.deleteButton.setObjectName("deleteButton")
        self.gridlayout.addWidget(self.deleteButton,1,1,1,1)

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem,2,1,1,1)

        self.buttonBox = QtGui.QDialogButtonBox(PropertyEditorDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox,3,1,1,1)

        self.retranslateUi(PropertyEditorDialog)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),PropertyEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),PropertyEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PropertyEditorDialog)

    def retranslateUi(self, PropertyEditorDialog):
        PropertyEditorDialog.setWindowTitle(QtGui.QApplication.translate("PropertyEditorDialog", "Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.newButton.setText(QtGui.QApplication.translate("PropertyEditorDialog", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteButton.setText(QtGui.QApplication.translate("PropertyEditorDialog", "Delete", None, QtGui.QApplication.UnicodeUTF8))

from propertyeditor import PropertyEditor
