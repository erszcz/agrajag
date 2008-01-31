#!/usr/bin/env python
#coding: utf-8

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import xml.dom

from ui_editor import Ui_MainWindow
from newleveldialog import NewLevelDialog

from constants import gfx_path, BackgroundItem, EventItem

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

  def load(self, filenames = []):
    if not filenames:
      filenames = QFileDialog.getOpenFileNames(self,
                    self.trUtf8('Load'),
                    './',
                    'Editable files(*.png *.tiff *.jpg *.bmp *.xml)')

    unreadable = []
    for filename in filenames:
      if  not filename.isEmpty() \
      and not self.loadImage(filename) \
      and not self.loadXML(filename):
        unreadable.append(filename)
        
    if unreadable:
      flist = ''
      for s in unreadable:
        flist += '\n' + s
      warn = str('Following files could not be loaded: %s' % flist)
      print warn
      QMessageBox.warning(self,
                          self.trUtf8('Load'),
                          self.trUtf8(warn))

  def loadImage(self, filename):
    newImage = QPixmap()
    if not newImage.load(filename):
      return False
    else:
      props = {}
      props['filename'] = os.path.basename(str(filename))
      props['name'] = props['filename'].rsplit('.', 1)[0]
      props['type'] = BackgroundItem
      self.tileList.addItem(newImage, props)
      return True

  def loadXML(self, filename):
    try:
      # get the props list
      filename = str(filename)
      name = os.path.basename(filename).rsplit('.', 1)[0]
      imported = self.dbm.import_file(filename)
      props = imported['props']

      # craft that list
      del props['editor_enabled']
      props['name'] = name
      props['type'] = EventItem
      k = imported['gfx'].keys()[0]
        # this is the image-resource name from XML
      props['filename'] = imported['gfx'][k]['file']
      
      # get the pixmap
      pixmap = QPixmap()
      if not pixmap.load(os.path.join(gfx_path, props['filename'])):
        return False

      self.tileList.addItem(pixmap, props)

      return True
#    except AttributeError, e:
#      print 'AttributeError:', e.message
#      return False
#    except KeyError, e:
#      print 'KeyError:', e.message
#      return False
    except Exception, e:
#      print 'Exception'
      return False

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

  def saveXML(self, filename = ''):
    if not filename:
      filename = QFileDialog.getSaveFileName(self,
                              self.trUtf8('Save level as XML'),
                              './',
                              'Extensible Markup Language files(*.xml)')
    
    if not filename:
      return
    items = self.levelView.items()
    if not self.writeXML(filename, items):
      warn = 'Could not write file:\n%s' %filename
      QMessageBox.warning(self,
                          self.trUtf8('Save as XML'),
                          self.trUtf8(warn))

  def writeXML(self, filename, items):
    # create the document
    imp = xml.dom.getDOMImplementation()
    doc = imp.createDocument('', 'stage', None)
    root = doc.firstChild
    eventsElement = doc.createElement('events')
    backgroundElement = doc.createElement('background')

    for item in items():
      if item.type == BackgroundItem:
        pass
      elif item.type == EventItem:
        pass
      else:
        pass

    try:
      filename = str(filename)
      # write the file...

      return True
    except IOError, e:
      print 'IOError:', e.message
      return False
