#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from newpropertydialog import NewPropertyDialog

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
    self.setupActions()
    self.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.setSelectionMode(QAbstractItemView.SingleSelection)
    self.connect(self, SIGNAL('currentItemChanged(QTableWidgetItem *, QTableWidgetItem *)'),
                 self.updateActions)
    
    self.setColumnCount(2)
    self.setHorizontalHeaderLabels([self.trUtf8('Property'),
                                    self.trUtf8('Value')])

    self.reset({})

  def setupActions(self):
    self.actionNew_property = QAction('New property', self)
    self.connect(self.actionNew_property, SIGNAL('triggered()'),
                 self.newProperty)
    
    self.actionDelete_property = QAction('Delete', self)
    self.connect(self.actionDelete_property, SIGNAL('triggered()'),
                 self.deleteProperty)

    self.actionCommit_changes = QAction('Commit changes', self)
    self.connect(self.actionCommit_changes, SIGNAL('triggered()'),
                 self.commitChanges)

  def updateActions(self, currentItem, previousItem):
    text = str(currentItem.text())
    if text == 'posx' or text == 'posy':
      self.actionDelete_property.setEnabled(False)
      self.emit(SIGNAL('actionDelete_propertyEnabled'), False)
    else:
      self.actionDelete_property.setEnabled(True)
      self.emit(SIGNAL('actionDelete_propertyEnabled'), True)

  def reset(self, props):
    self.adjusters = {}
    self.initialProps = props
    self.props = self.initialProps.copy()

    for x, y in self.props.items():
      self.addProperty(x, type(y), y, False)
    self.sortItems(0)

  # slot
  def commitChanges(self):
    '''
    Commit all the changes user has made (i.e. apply them to
    the original dictionary storing the properties).
    '''
    self.initialProps.clear()
    self.initialProps.update(self.props)

  # slot
  def addProperty(self, key, type, value, sort=True):
    # item with key name
    keyItem = QTableWidgetItem(key)
    if key != 'posx' and key != 'posy':
      keyItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
    else:
      keyItem.setFlags(Qt.ItemIsSelectable)

    # item with value editor
    valItem = self.__getEditor(key, type, value)
    if key == 'posx' or key == 'posy':
      valItem.setEnabled(False)
    
    # increase row number
    index = self.rowCount()
    self.setRowCount(index + 1)

    # set proper items
    self.setItem(index, 0, keyItem)
    self.setCellWidget(index, 1, valItem)
    valItem.show()
    if sort:  # sort if necessary
      self.sortItems(0)

    # add to the dictionary
    self.props[key] = value
  
  # slot
  def newProperty(self):
    npd = NewPropertyDialog(self)
    npd.exec_()

  # slot
  def deleteProperty(self, item=None):
    if item == None:
      item = self.currentItem()
      
    # remove the corresponding adjuster
    key = str(item.text())
    del self.adjusters[key]

    # remove item's row
    self.removeRow(self.row(item))

    del self.props[key]

  def __getEditor(self, key, type, value):
    print 'key:', key, 'type:', type, 'val:', value
    if   type == int:
      editor = QSpinBox()
      editor.setRange(-10000, 10000)
      editor.setValue(value)
      self.adjusters[key] = PropertyAdjuster(key, self)
      self.connect(editor, SIGNAL('valueChanged(int)'),
                   self.adjusters[key].adjustNumber)
    elif type == float:
      editor = QDoubleSpinBox()
      editor.setRange(-10000.0, 10000.0)
      editor.setValue(value)
      self.adjusters[key] = PropertyAdjuster(key, self)
      self.connect(editor, SIGNAL('valueChanged(double)'),
                   self.adjusters[key].adjustNumber)
    elif type == bool:
      editor = QCheckBox()
      editor.setTristate(False)
      f = lambda x: 2 if x else 0
      editor.setCheckState(Qt.CheckState(f(value)))
      self.adjusters[key] = PropertyAdjuster(key, self)
      self.connect(editor, SIGNAL('stateChanged(int)'),
                   self.adjusters[key].adjustBool)
    elif type == tuple or type == list:
      editor = QLineEdit()
      editor.setText(', '.join(list(value)))
      self.adjusters[key] = PropertyAdjuster(key, self)
      self.connect(editor, SIGNAL('textChanged(QString)'),
                   self.adjusters[key].adjustTuple)
    elif type == str or type == unicode:
      editor = QLineEdit()
      editor.setText(value)
      self.adjusters[key] = PropertyAdjuster(key, self)
      self.connect(editor, SIGNAL('textChanged(QString)'),
                   self.adjusters[key].adjustString)
    else:
      raise Exception('Editor for type: %s undefined.' % type)

    return editor
