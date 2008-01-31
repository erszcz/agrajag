#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_propertyeditordialog import Ui_PropertyEditorDialog

class PropertyEditorDialog(QDialog, Ui_PropertyEditorDialog):
  def __init__(self, props, parent=None):
    QDialog.__init__(self, parent)
    Ui_PropertyEditorDialog.setupUi(self, self)
    Ui_PropertyEditorDialog.retranslateUi(self, self)
    
    self.connect(self.buttonBox, SIGNAL("accepted()"), self.accept_)

    self.propertyEditor.initProperties(props)

  def accept_(self):
    self.propertyEditor.propsOriginal.update(self.propertyEditor.props)

