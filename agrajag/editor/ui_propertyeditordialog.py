# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './propertyeditordialog.ui'
#
# Created: Thu Jan 31 15:41:37 2008
#      by: PyQt4 UI code generator 4.3.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_PropertyEditorDialog(object):
    def setupUi(self, PropertyEditorDialog):
        PropertyEditorDialog.setObjectName("PropertyEditorDialog")
        PropertyEditorDialog.resize(QtCore.QSize(QtCore.QRect(0,0,353,429).size()).expandedTo(PropertyEditorDialog.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PropertyEditorDialog.sizePolicy().hasHeightForWidth())
        PropertyEditorDialog.setSizePolicy(sizePolicy)
        PropertyEditorDialog.setMinimumSize(QtCore.QSize(300,400))

        self.layoutWidget = QtGui.QWidget(PropertyEditorDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(0,5,351,421))
        self.layoutWidget.setObjectName("layoutWidget")

        self.hboxlayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.hboxlayout.setObjectName("hboxlayout")

        self.propertyEditor = PropertyEditor(self.layoutWidget)
        self.propertyEditor.setObjectName("propertyEditor")
        self.hboxlayout.addWidget(self.propertyEditor)

        self.buttonBox = QtGui.QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.hboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(PropertyEditorDialog)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),PropertyEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),PropertyEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PropertyEditorDialog)

    def retranslateUi(self, PropertyEditorDialog):
        PropertyEditorDialog.setWindowTitle(QtGui.QApplication.translate("PropertyEditorDialog", "Properties", None, QtGui.QApplication.UnicodeUTF8))

from propertyeditor import PropertyEditor
