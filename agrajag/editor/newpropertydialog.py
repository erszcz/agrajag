#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_newpropertydialog import Ui_NewPropertyDialog

import propertyeditor

class Type:
  Integer = 0
  Double  = 1
  Bool    = 2
  Tuple   = 3
  String  = 4

  @classmethod
  def pythonic(cls, type):
    if   type == cls.Integer:
      out = int
    elif type == cls.Double:
      out = float
    elif type == cls.Bool:
      out = bool
    elif type == cls.Tuple:
      out = tuple
    elif type == cls.String:
      out = str
    return out

class NewPropertyDialog(QDialog, Ui_NewPropertyDialog):
  def __init__(self, parent):
    QDialog.__init__(self, parent)
    Ui_NewPropertyDialog.setupUi(self, self)
    Ui_NewPropertyDialog.retranslateUi(self, self)

    self.propertyEditor = parent

    self.typeButtonGroup = QButtonGroup(self)
    self.typeButtonGroup.addButton(self.intTypeButton, Type.Integer)
    self.typeButtonGroup.addButton(self.doubleTypeButton, Type.Double)
    self.typeButtonGroup.addButton(self.boolTypeButton, Type.Bool)
    self.typeButtonGroup.addButton(self.tupleTypeButton, Type.Tuple)
    self.typeButtonGroup.addButton(self.strTypeButton, Type.String)
    
    self.connect(self.typeButtonGroup, SIGNAL('buttonClicked(int)'),
                 self.enableSelectedEditor)

    self.editors = {Type.Bool: self.boolCheckBox, \
                    Type.Double: self.doubleSpinBox, \
                    Type.Integer: self.intSpinBox, \
                    Type.String: self.strLineEdit, \
                    Type.Tuple: self.tupleLineEdit}

    self.connect(self.buttonBox, SIGNAL('accepted()'),
                 self.__addProperty)

  # slot
  def enableSelectedEditor(self, id):
    for x in self.editors.values():
      x.setEnabled(False)
    self.editors[id].setEnabled(True)

  # slot
  def __addProperty(self):
    key = str(self.keyLineEdit.text())
    if not key:
      text = str(self.keyLabel.text())
      self.keyLabel.setText('<span style="color: red">%s</span>' % text)
      return
    type = Type.pythonic(self.typeButtonGroup.checkedId())

    cnv = propertyeditor.PropertyTableRow
    if   type == int:
      value = self.intSpinBox.value()
    elif type == float:
      value = self.doubleSpinBox.value()
    elif type == bool:
      value = cnv.convertBool(self.boolCheckBox.checkState())
    elif type == tuple or type == list:
      value = cnv.convertTuple(self.tupleLineEdit.text())
    elif type == str or type == unicode:
      value = cnv.convertString(self.strLineEdit.text())

    self.propertyEditor.addProperty(key, value)
    # this is rooted out from this dialog's behaviour in designer
    # file, so I add it here
    self.accept()
