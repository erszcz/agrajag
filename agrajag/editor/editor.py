#!/usr/bin/env python
#coding: utf-8

import sys
import os
from PyQt4.QtGui import *

from mainwindow import MainWindow

if __name__ == '__main__':
  if os.path.dirname(__file__):
    os.chdir( os.path.dirname(__file__) )

  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()

  sys.exit(app.exec_())
