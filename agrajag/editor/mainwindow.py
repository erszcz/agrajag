#!/usr/bin/env python
#coding: utf-8

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_editor import Ui_MainWindow
from newleveldialog import NewLevelDialog

from config import gfx_path

class MainWindow(QMainWindow, Ui_MainWindow):
  def __init__(self, dbm, parent=None):
    QMainWindow.__init__(self, parent)
    Ui_MainWindow.setupUi(self, self)
    Ui_MainWindow.retranslateUi(self, self)

    self.setupActions()

    self.dbm = dbm

  def setupActions(self):
    self.connect(self.actionNew_level,
                 SIGNAL('triggered()'),
                 self.newLevel)
    self.connect(self.actionLoad,
                 SIGNAL('triggered()'),
                 #self.loadTiles)
                 self.load)
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

#  def loadTiles(self, filenames = []):
#    if not filenames:
#      filenames = QFileDialog.getOpenFileNames(self,
#                                    self.trUtf8('Load tiles'),
#                                    './',
#                                    'Image files(*.png *.tiff *.jpg *.bmp)')
#
#    unreadable = []
#    for filename in filenames:
#      if not filename.isEmpty():
#        newImage = QPixmap()
#        if not newImage.load(filename):
#          unreadable.append(filename)
#        else:
#          props = {}
#          props['pixmap'] = newImage
#          props['filename'] = os.path.basename(str(filename))
#          self.tileList.addTile(props)
#
#    if unreadable:
#      flist = ''
#      for s in unreadable:
#        flist += '\n' + s
#      warn = str('Following files could not be loaded: %s' % flist)
#      print warn, type(warn)
#      QMessageBox.warning(self,
#                          self.trUtf8('Load tiles'),
#                          self.trUtf8(warn))

  def load(self, filenames = []):
    if not filenames:
      filenames = QFileDialog.getOpenFileNames(self,
                    self.trUtf8('Load tiles'),
                    './',
                    'Editable files(*.png *.tiff *.jpg *.bmp *.xml)')

    unreadable = []
    for filename in filenames:
      if not filename.isEmpty() and \
       not self.loadImage(filename) and \
       not self.loadXML(filename):
        unreadable.append(filename)
        
    if unreadable:
      flist = ''
      for s in unreadable:
        flist += '\n' + s
      warn = str('Following files could not be loaded: %s' % flist)
      print warn
      QMessageBox.warning(self,
                          self.trUtf8('Load tiles'),
                          self.trUtf8(warn))

  def loadImage(self, filename):
    newImage = QPixmap()
    if not newImage.load(filename):
      return False
    else:
      props = {}
      props['pixmap'] = newImage
      props['filename'] = os.path.basename(str(filename))
      props['name'] = props['filename'][:-4]
      self.tileList.addTile(props)
      return True

# finish this
  def loadXML(self, filename):
    print filename
    try:
      self.dbm.import_file(filename)
      name = str(filename)[:-4]
      props = self.dbm.get_editor()[name]['props']
      props['name'] = name
      props['filename'] = self.dbm.get_editor()[name]['gfx']['file']
      del props['editor_enabled']
      pixmap = QPixmap()
      print gfx_path + props['filename']
      if not pixmap.load(os.path.join(gfx_path, props['filename'])):
        return False
      props['pixmap'] = pixmap
      self.tileList.addTile(props)

      return True
    except Exception, e:
      print e
      print 'Exception:', e.message
      return False
#

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
