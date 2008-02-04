#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_propertyeditordialog import Ui_PropertyEditorDialog

from newpropertydialog import NewPropertyDialog

class PropertyEditorDialog(QDialog, Ui_PropertyEditorDialog):
  def __init__(self, props, parent=None):
    QDialog.__init__(self, parent)
    Ui_PropertyEditorDialog.setupUi(self, self)
    Ui_PropertyEditorDialog.retranslateUi(self, self)
    
    self.connect(self.buttonBox, SIGNAL('accepted()'),
                 self.propertyEditor.commitChanges)
    self.connect(self.newButton, SIGNAL('clicked()'),
                 self.__addProperty)
    self.connect(self.deleteButton, SIGNAL('clicked()'),
                 self.propertyEditor.deleteCurrentProperty)

    self.propertyEditor.initProperties(props)

  # slot
  def __addProperty(self):
    npd = NewPropertyDialog(self.propertyEditor)
    npd.exec_()
