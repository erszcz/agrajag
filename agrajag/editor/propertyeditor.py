#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from newpropertydialog import NewPropertyDialog


prop_opts = {# option selectible props
             'object_cls_name': ['EnemyInterceptor', 'MidgetBeamShip'],
             'mover_cls_name':  ['RandomMover', 'ZigZagMover', 'CircularMover',
                                 'LinearMover', 'LinearPlayerTargetingMover',
                                 'SeekingMover'],
             'bonus_cls_name':  ['RechargeBonus', 'SuperShieldBonus',
                                 'ShieldUpgradeBonus'],
             'group':           ['enemies', 'ship', 'enemy_projectiles',
                                 'player_projectiles', 'beams', 'explosions',
                                 'shields', 'bonuses'],
             # primitive type props
             'posx': int,
             'posy': int,
             'time': int
            }
select_only_props = 'group', 'mover_cls_name', \
                    'bonus_cls_name', 'object_cls_name'
primitive_type_props = 'posx', 'posy', 'time'

# mover/bonus-type: {param_one: default_value, param_two: default_value...}
mover_params = {'RandomMover':   {'period': 130},
                'ZigZagMover':   {'radius': 80},
                'CircularMover': {'radius': 80},
                'LinearMover':   {'dir': 0},
                'LinearPlayerTargetingMover': {'vertical_div': 0.3},
                'SeekingMover':  {}
               }
bonus_params = {'RechargeBonus': {'power': 10},
                'SuperShieldBonus': {},
                'ShieldUpgradeBonus': {}
               }
object_params = {'EnemyInterceptor': {},
                 'MidgetBeamShip': {}
                }
# translator: class name -> object type (i.e.: mover, object, bonus)
cls2type = {}
for cls in mover_params.keys() + bonus_params.keys() + object_params.keys():
  if cls in prop_opts['object_cls_name']:
    cls2type[cls] = 'object_cls_name'
  elif cls in prop_opts['mover_cls_name']:
    cls2type[cls] = 'mover_cls_name'
  elif cls in prop_opts['bonus_cls_name']:
    cls2type[cls] = 'bonus_cls_name'


class PropertyTableRow(QObject):
  def __init__(self, key, value, parent, childProperties={}):
    QObject.__init__(self, parent)
    self.parent = parent
    self.key = key
    
    # child props management
    if childProperties:
      self.__oldChoice = childProperties.keys()[0].split(':')[0]
    else:
      self.__oldChoice = ''
    self.initChildProperties(childProperties)

    self.labelItem = QTableWidgetItem(key)  # labelItem.text = key
    self.labelItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
    self.editorItem, setter, value = self.__getEditor(key, value)


    # add widgets to parent
    index = parent.rowCount() - 1
    parent.setItem(index, 0, self.labelItem)
    parent.setCellWidget(index, 1, self.editorItem)
    setter(value)
    self.parent.sortItems(0)

  def initChildProperties(self, properties):
    self.__childProperties = []
    for child, value in properties.items():
      self.parent.addProperty(child, value)
      self.__childProperties.append(child)

  def deleteChildProperties(self):
    for child in self.__childProperties:
      self.parent.deleteProperty(key = child)
    self.__childProperties = []

  # slot
  def updateChildProperties(self, choice):
    choice = str(choice)
    if self.__oldChoice != choice:
      self.__oldChoice = choice

      # purge old child properties
      self.deleteChildProperties()

      # create new child properties
      type = cls2type[choice].split('_')[0]
      for child, value in eval(type + '_params')[choice].items():
        self.parent.addProperty(':'.join((choice, child)), value)
        self.__childProperties.append(':'.join((choice, child)))

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

  def adjustNumber(self, value):
    self.parent.props[self.key] = value

  def adjustBool(self, value):
    self.parent.props[self.key] = self.convertBool(value)

  def adjustTuple(self, value):
    self.parent.props[self.key] = self.convertTuple(value)

  def adjustString(self, value):
    self.parent.props[self.key] = self.convertString(value)

  def __getEditor(self, key, value):
    vtype = type(value)
    if key in select_only_props:
      editor = QComboBox()
      editor.addItems(prop_opts[key])
      editor.setEditable(True)
      editor.setValidator(QRegExpValidator(QRegExp('\S*'), self))
      setter = editor.setEditText
      self.connect(editor, SIGNAL('editTextChanged(QString)'),
                   self.adjustString)

      if key == 'object_cls_name':
        editor.setEnabled(False)
        self.labelItem.setFlags(Qt.ItemIsSelectable)

      if key in ('object_cls_name', 'mover_cls_name', 'bonus_cls_name'):
        self.connect(editor, SIGNAL('editTextChanged(QString)'),
                     self.updateChildProperties)
    else:
      if   vtype == int:
        editor = QSpinBox()
        setter = editor.setValue
        self.connect(editor, SIGNAL('valueChanged(int)'),
                     self.adjustNumber)
      elif vtype == float:
        editor = QDoubleSpinBox()
        setter = editor.setValue
        self.connect(editor, SIGNAL('valueChanged(double)'),
                     self.adjustNumber)
      elif vtype == bool:
        editor = QCheckBox()
        editor.setTristate(False)
        f = lambda x: 2 if x else 0
        setter = editor.setCheckState
        value = Qt.CheckState(f(value))
        self.connect(editor, SIGNAL('stateChanged(int)'),
                     self.adjustBool)
      elif vtype == tuple or vtype == list:
        editor = QLineEdit()
        setter = editor.setText
        value = ', '.join(list(value))
        self.connect(editor, SIGNAL('textChanged(QString)'),
                     self.adjustTuple)
      elif vtype == str or vtype == unicode:
        editor = QLineEdit()
        setter = editor.setText
        self.connect(editor, SIGNAL('textChanged(QString)'),
                     self.adjustString)

      if key == 'posx':
        editor.setEnabled(False)
        self.labelItem.setFlags(Qt.ItemIsSelectable)
        editor.setRange(-1024, 1024)
      elif key == 'posy':
        editor.setEnabled(False)
        self.labelItem.setFlags(Qt.ItemIsSelectable)
        editor.setRange(-1024, 1000000000)
      elif key == 'time':
        editor.setMinimum(0)
      # object/mover/bonus parameters
      elif key.split(':')[-1] == 'period':
        editor.setRange(0, 1000000000)
      elif key.split(':')[-1] == 'radius':
        editor.setRange(0, 512)
      elif key.split(':')[-1] == 'dir':
        editor.setRange(0, 359)
      elif key.split(':')[-1] == 'vertical_div':
        editor.setRange(0.0, 6.28)
      elif key.split(':')[-1] == 'power':
        editor.setRange(0, 1000000000)

    return editor, setter, value


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
    self.setMinimumWidth(230)
    self.setHorizontalHeaderLabels([self.trUtf8('Property'),
                                    self.trUtf8('Value')])

    self.autoApplyChanges = False
    #self.setProperties({})
    self.reset()

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

  def setFromItem(self, item=None):
    if item:
      self.setProperties(item.props)
    else:
      self.setProperties({})

  def reset(self):
    self.setRowCount(0)
    self.rows = {}
    self.props = {}

  def setProperties(self, props):
    if not props:  # no props, not setting anything
      self.setEnabled(False)
      self.reset()
      return
    
    self.setEnabled(True)
    self.reset()
    if self.autoApplyChanges:
      self.props = props
    else:
      self.initialProps = props
      self.props = props.copy()

    initTree = {}
    for key in sorted(props.keys(), reverse=True):
      if key[0].islower(): initTree[key] = {}
      elif key[0].isupper():
        type = cls2type[key.split(':')[0]]
        initTree[type][key] = props[key]
      else:
        raise Exception('Undefined property: %s' % key)

    for key in initTree.keys():
      self.addProperty(key, props[key], initTree[key])

  # slot
  def commitChanges(self):
    '''
    Commit all the changes user has made (i.e. apply them to
    the original dictionary storing the properties).
    '''
    if self.autoApplyChanges:
      return
    self.initialProps.clear()
    self.initialProps.update(self.props)

  # slot
  def addProperty(self, key, value, childProperties={}):
    # increase row number
    index = self.rowCount()
    self.setRowCount(index + 1)
    
    self.rows[key] = PropertyTableRow(key, value, self, childProperties)

    # add to the dictionary
    self.props[key] = value
  
  # slot
  def newProperty(self):
    npd = NewPropertyDialog(self)
    npd.exec_()

  # slot
  def deleteProperty(self, item=None, key=None):
    if item == None and key == None:
      item = self.currentItem()

    if not key:
      key = str(item.text())
    if not item:
      key = str(key)
      item = self.rows[key].labelItem

    # remove item's row
    self.removeRow(self.row(item))
    self.rows[key].deleteChildProperties()
    del self.rows[key]

    del self.props[key]

  def contextMenuEvent(self, event):
    menu = QMenu()
    menu.addAction(self.actionNew_property)
    menu.addAction(self.actionDelete_property)
    menu.addAction(self.actionCommit_changes)
    menu.exec_(event.globalPos())

