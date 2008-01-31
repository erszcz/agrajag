#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from constants import BackgroundItem, EventItem

class PropertyAdjuster:
  def __init__(self, propKey, parent):
    self.propKey = propKey
    self.parent = parent

  def adjustNumber(self, value):
    self.parent.props[self.propKey] = value

  def adjustBool(self, value):
    self.parent.props[self.propKey] = bool(value)

  def adjustTuple(self, value):
    value = str(value)
    value = value.replace(' ', '')
    self.parent.props[self.propKey] = tuple(value.split(','))

  def adjustString(self, value):
    value = str(value)
    self.parent.props[self.propKey] = value

class PropertyEditor(QTableWidget):
  '''Class suited to view and allow for adjustment of event properties.'''
  
  def __init__(self, parent=None):
    QTableWidget.__init__(self, parent)
    
    self.setColumnCount(2)
    self.setHorizontalHeaderLabels([self.trUtf8('Property'),
                                    self.trUtf8('Value')])

    self.adjusters = []

  def initProperties(self, props):
    self.propsOriginal = props
    self.props = self.propsOriginal.copy()

    propKeys = self.props.keys()
    propKeys.sort()
    self.setRowCount(len(propKeys))
    for x in propKeys:
      self.initProperty(propKeys.index(x), x, self.props[x])

  def initProperty(self, index, propKey, propValue):
    if   type(propValue) == int:
      cellWidget = QSpinBox()
      cellWidget.setValue(propValue)
      self.adjusters.append(PropertyAdjuster(propKey, self))
      self.connect(cellWidget, SIGNAL('valueChanged(int)'),
                   self.adjusters[-1].adjustNumber)
    elif type(propValue) == float:
      cellWidget = QDoubleSpinBox()
      cellWidget.setValue(propValue)
      self.adjusters.append(PropertyAdjuster(propKey, self))
      self.connect(cellWidget, SIGNAL('valueChanged(double)'),
                   self.adjusters[-1].adjustNumber)
    elif type(propValue) == bool:
      cellWidget = QCheckBox()
      cellWidget.setTristate(False)
      f = lambda x: 2 if x else 0
      cellWidget.setCheckState(Qt.CheckState(f(propValue)))
      self.adjusters.append(PropertyAdjuster(propKey, self))
      self.connect(cellWidget, SIGNAL('stateChanged(int)'),
                   self.adjusters[-1].adjustBool)
    elif type(propValue) == tuple or type(propValue) == list:
      cellWidget = QLineEdit()
      cellWidget.setText(', '.join(list(propValue)))
      self.adjusters.append(PropertyAdjuster(propKey, self))
      self.connect(cellWidget, SIGNAL('textChanged(QString)'),
                   self.adjusters[-1].adjustTuple)
    elif type(propValue) == str or type(propValue) == unicode:
      cellWidget = QLineEdit()
      cellWidget.setText(propValue)
      self.adjusters.append(PropertyAdjuster(propKey, self))
      self.connect(cellWidget, SIGNAL('textChanged(QString)'),
                   self.adjusters[-1].adjustString)
    
    self.setItem(index, 0, QTableWidgetItem(propKey.title()))
    self.setCellWidget(index, 1, cellWidget)

