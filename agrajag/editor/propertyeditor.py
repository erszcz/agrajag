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
    self.parent.props[self.propKey] = self.convertBool(value)

  def adjustTuple(self, value):
    self.parent.props[self.propKey] = self.convertTuple(value)

  def adjustString(self, value):
    self.parent.props[self.propKey] = self.convertString(value)

  # converters
  @staticmethod
  def convertBool(value):
    return bool(value)

  @staticmethod
  def convertTuple(value):
    value = str(value)
    value = value.replace(' ', '')
    return tuple(value.split(','))

  @staticmethod
  def convertString(value):
    return str(value)

class PropertyEditor(QTableWidget):
  '''
  Class suited to view and allow for adjustment
  of event/item properties.
  '''
  
  def __init__(self, parent=None):
    QTableWidget.__init__(self, parent)
    
    self.setColumnCount(2)
    self.setHorizontalHeaderLabels([self.trUtf8('Property'),
                                    self.trUtf8('Value')])

    self.adjusters = []
    self.initProperties({})

  def initProperties(self, props):
    self.propsOriginal = props
    self.props = self.propsOriginal.copy()

    for x, y in self.props.items():
      self.newProperty(x, type(y), y, False)
    self.sortItems(0)

  # slot
  def commitChanges(self):
    '''
    Commit all the changes user has made (i.e. apply them to
    the original dictionary storing the properties).
    '''
    self.propsOriginal.clear()
    self.propsOriginal.update(self.props)

  # slot
  def newProperty(self, key, type, value, sort=True):
    # item with key name
    keyItem = QTableWidgetItem(key)
    keyItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    # item with value editor
    valItem = self.__getEditor(key, type, value)
    
    # increase row number
    index = self.rowCount()
    self.setRowCount(index + 1)

    # set proper items
    self.setItem(index, 0, keyItem)
    self.setCellWidget(index, 1, valItem)
    if sort:  # sort if necessary
      self.sortItems(0)

    # add to the dictionary
    self.props[key] = value

  # slot
  def deleteCurrentProperty(self):
    # remove the corresponding adjuster
    self.adjusters.sort(key=lambda obj: 1 if obj.propKey == propKey else 0)
    self.adjusters.pop()

    # remove item's row
    self.removeRow(self.currentRow())

    del self.props[propKey]

  def __getEditor(self, key, type, value):
    if   type == int:
      editor = QSpinBox()
      editor.setValue(value)
      self.adjusters.append(PropertyAdjuster(key, self))
      self.connect(editor, SIGNAL('valueChanged(int)'),
                   self.adjusters[-1].adjustNumber)
    elif type == float:
      editor = QDoubleSpinBox()
      editor.setValue(value)
      self.adjusters.append(PropertyAdjuster(key, self))
      self.connect(editor, SIGNAL('valueChanged(double)'),
                   self.adjusters[-1].adjustNumber)
    elif type == bool:
      editor = QCheckBox()
      editor.setTristate(False)
      f = lambda x: 2 if x else 0
      editor.setCheckState(Qt.CheckState(f(value)))
      self.adjusters.append(PropertyAdjuster(key, self))
      self.connect(editor, SIGNAL('stateChanged(int)'),
                   self.adjusters[-1].adjustBool)
    elif type == tuple or type == list:
      editor = QLineEdit()
      editor.setText(', '.join(list(value)))
      self.adjusters.append(PropertyAdjuster(key, self))
      self.connect(editor, SIGNAL('textChanged(QString)'),
                   self.adjusters[-1].adjustTuple)
    elif type == str or type == unicode:
      editor = QLineEdit()
      editor.setText(value)
      self.adjusters.append(PropertyAdjuster(key, self))
      self.connect(editor, SIGNAL('textChanged(QString)'),
                   self.adjusters[-1].adjustString)
    else:
      raise Exception('Editor for type: %s undefined.' % type)

    return editor
