#!/usr/bin/env python
#coding: utf-8

import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_editor import Ui_MainWindow

from newleveldialog import NewLevelDialog

class MainWindow(QMainWindow, Ui_MainWindow):
  def __init__(self, parent=None):
    QMainWindow.__init__(self, parent)
    Ui_MainWindow.setupUi(self, self)
    Ui_MainWindow.retranslateUi(self, self)

    self.setupActions()

  def setupActions(self):
    self.connect(self.actionNew_level,
                 SIGNAL('triggered()'),
                 self.newLevel)
    self.connect(self.actionLoad_tiles,
                 SIGNAL('triggered()'),
                 self.loadTiles)
    self.connect(self.actionSave_image,
                 SIGNAL('triggered()'),
                 self.saveImage)
    self.connect(self.actionAbout_Qt,
                 SIGNAL('triggered()'),
                 qApp.aboutQt)

    # not implemented
    self.connect(self.actionSave_XML,
                 SIGNAL('triggered()'),
                 self.notImplementedYet)

  def notImplementedYet(self):
    info = 'The feature you requested is not implemented yet.'
    QMessageBox.information(self,
                            self.trUtf8('Feature not implemented'),
                            self.trUtf8(info))

  def newLevel(self):
    size = NewLevelDialog.getLevelSize(self)
    if not size.isEmpty():
      self.levelView.newScene(size)

  def loadTiles(self, filenames = []):
    if not filenames:
      filenames = QFileDialog.getOpenFileNames(self,
                                      self.trUtf8('Load tiles'),
                                      './',
                                      'Image files(*.png *.tiff *.jpg *.bmp)')

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

  def saveImage(self, filename = ''):
    if not filename:
      filename = QFileDialog.getSaveFileName(self,
                                  self.trUtf8('Save level as image'),
                                  './',
                                  'Image files(*.png *.tiff *.jpg *.bmp)')

    if not filename:
      return
    image = self.levelView.snapshot()
    if not image.save(filename):
      QMessageBox.warning(self, self.trUtf8('Save level as image'),
                          self.trUtf8('The file could not be saved.'))
