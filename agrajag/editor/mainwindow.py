#!/usr/bin/env python
#coding: utf-8

import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_editor import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
  def __init__(self, parent=None):
    QMainWindow.__init__(self, parent)
    Ui_MainWindow.setupUi(self, self)

    self.setupActions()

    # temp
    #newerImage = QPixmap()
    #newerImage.load('../gfx/terrain/TEST7B.png')
    #self.scene = QGraphicsScene()
    #self.scene.addPixmap(newerImage)
    #self.levelView.setScene(self.scene)
    #self.levelView.update()
    # koniec temp

  def setupActions(self):
    self.connect(self.actionLoad_tiles,
                 SIGNAL('triggered()'),
                 self.loadTiles)
    self.connect(self.actionAbout_Qt,
                 SIGNAL('triggered()'),
                 qApp.aboutQt)

  def loadTiles(self, filenames = QStringList()):
    if filenames.isEmpty():
      filenames = QFileDialog.getOpenFileNames(self,
                                      self.trUtf8('Load tiles'),
                                      './',
                                      'Image files(*.png *.jpg *.bmp)')

    unreadable = []
    for filename in filenames:
      if not filename.isEmpty():
        newImage = QPixmap()
        if not newImage.load(filename):
          unreadable.append(filename)
        else:
          self.tileList.addTile( newImage,
                                 os.path.basename(str(filename)) )

    if unreadable:
      flist = ''
      for s in unreadable:
        flist += '\n' + s
      warn = str('Following files could not be loaded: %s' % flist)
      print warn, type(warn)
      QMessageBox.warning(self,
                          self.trUtf8('Load tiles'),
                          self.trUtf8(warn))

