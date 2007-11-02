#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_new_level import Ui_New_level

class NewLevelDialog(QDialog, Ui_New_level):
  __width = 0
  __height = 0

  def __init__(self, parent=None):
    QDialog.__init__(self, parent)
    Ui_New_level.setupUi(self, self)
    Ui_New_level.retranslateUi(self, self)

  @staticmethod
  def getLevelSize(parent=None):
    nl = NewLevelDialog(parent)
    NewLevelDialog.__width = nl.widthSpinBox.value()
    NewLevelDialog.__height = nl.heightSpinBox.value()

    QObject.connect(nl.widthSpinBox,
                    SIGNAL('valueChanged(int)'),
                    NewLevelDialog.__setWidth)
    QObject.connect(nl.heightSpinBox,
                    SIGNAL('valueChanged(int)'),
                    NewLevelDialog.__setHeight)

    if nl.exec_():
      return QSize(NewLevelDialog.__width,
                   NewLevelDialog.__height)
    else:
      return QSize(0, 0)

  @staticmethod
  def __setWidth(int):
    NewLevelDialog.__width = int
    
  @staticmethod
  def __setHeight(int):
    NewLevelDialog.__height = int

if __name__ == '__main__':
  qapp = QApplication([])
  size = NewLevelDialog.getLevelSize()
  print size.width(), size.height()
