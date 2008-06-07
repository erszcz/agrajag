#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import ui_propertyeditordialog

class PropertyEditorDialog(QDialog,
  ui_propertyeditordialog.Ui_PropertyEditorDialog):

  def __init__(self, props, parent=None):
    QDialog.__init__(self, parent)
    ui_propertyeditordialog.Ui_PropertyEditorDialog.setupUi(self, self)
    ui_propertyeditordialog.Ui_PropertyEditorDialog.retranslateUi(self, self)

    self.connect(self.buttonBox, SIGNAL('accepted()'),
                 self.propertyEditor.actionCommit_changes.trigger)
    self.connect(self.newButton, SIGNAL('clicked()'),
                 self.propertyEditor.actionNew_property.trigger)
    self.connect(self.deleteButton, SIGNAL('clicked()'),
                 self.propertyEditor.actionDelete_property.trigger)
    self.connect(self.propertyEditor,
                 SIGNAL('actionDelete_propertyEnabled'),
                 self.deleteButton.setEnabled)

    self.propertyEditor.setProperties(props)
