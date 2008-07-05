#!/usr/bin/env python
#coding: utf-8

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_editor import Ui_MainWindow
from newleveldialog import NewLevelDialog

import formation as f
import xmlwriter as xw

import options

class InfoWindow(QDialog):
  def __init__(self, short, long='', parent=None):
    QDialog.__init__(self, parent)
    self.setModal(True)
    self.setMinimumWidth(500)
    layout = QVBoxLayout(self)
    
    shortLabel = QLabel(short, self)
    layout.addWidget(shortLabel)
    if long:
      longText = QTextEdit(long)
      layout.addWidget(longText)
      longText.setLineWrapMode(QTextEdit.NoWrap)
    button = QPushButton('&OK')
    layout.addWidget(button)
    self.connect(button, SIGNAL('clicked()'),
                 self, SLOT('accept()'))

  @staticmethod
  def info(short, long='', parent=None):
    dlg = InfoWindow(short, long, parent)
    dlg.exec_()


class FormationToolbar(QToolBar):
  def __init__(self, parent=None):
    QToolBar.__init__(self, parent)

    # formations combobox
    self.addWidget(QLabel(self.trUtf8('Formation:')))

    self.combo = QComboBox(self)
    self.combo.addItems(f.formations)
    self.addWidget(self.combo)

    # item count
    self.addWidget(QLabel(self.trUtf8('Ship count:')))

    self.count = QSpinBox(self)
    self.count.setRange(1, 20)
    self.count.setValue(5)
    self.addWidget(self.count)

    self.__setupActions()
    self.__setupConnections()

    self.__cachedIndex = 0
    self.__lastType = ''

  def __setupActions(self):
    self.actionShowHide = QAction(self.trUtf8('Formation toolbar'), qApp)
    self.actionShowHide.setCheckable(True)
    self.actionShowHide.setChecked(True)
    self.connect(self.actionShowHide, SIGNAL('toggled(bool)'),
                 self.setVisible)

  def __setupConnections(self):
    self.connect(self.combo, SIGNAL('currentIndexChanged(int)'),
                 self.__cacheIndex)

  def __cacheIndex(self, index):
    if self.combo.currentIndex() != -1 and self.__lastType == 'EventItem':
      self.__cachedIndex = index

  def adjustSettings(self, type):
    self.__lastType = type
    if type == 'BackgroundItem':
      self.combo.setCurrentIndex(0)
      self.setEnabled(False)
    elif type == 'EventItem':
      self.setEnabled(True)
      # shite without that, but why?
      for x in self.findChildren(QWidget, QString()):
        x.setEnabled(True)
      #
      self.combo.setCurrentIndex(self.__cachedIndex)
    else:
      raise Exception('unknown item type: %s' % type)

  def contextMenuEvent(self, event):
    pass

  def formation(self):
    return self.combo.currentText()


class MainWindow(QMainWindow, Ui_MainWindow):
  def __init__(self, dbm, parent=None):
    QMainWindow.__init__(self, parent)
    Ui_MainWindow.setupUi(self, self)
    Ui_MainWindow.retranslateUi(self, self)
 
    # statusbar
    self.statusbar = QStatusBar(self)
    self.dimensionsLabel = QLabel('Dim: %s x %s' % options.scene_size)
    self.positionLabel = QLabel('Pos: 0, 0')
    self.statusbar.addPermanentWidget(self.positionLabel)
    self.statusbar.addPermanentWidget(self.dimensionsLabel)
    self.setStatusBar(self.statusbar)

    # toolbar
    self.toolbar = FormationToolbar(self)
    self.addToolBar(self.toolbar)
    self.menuOptions.addAction(self.toolbar.actionShowHide)
    self.menubar.contextMenuEvent = lambda: 0

    # property editor
    self.propEd.autoApplyChanges = True
    self.menuOptions.addAction(self.propEd.actionShowHide)

    self.__setupConnections()
    self.__setupActions()

    self.dbm = dbm

  # slot
  def __updateMousePosition(self, x, y):
    self.positionLabel.setText('Pos: %s, %s' % (x, y))

  def __updateSceneDimensions(self, x, y):
    self.dimensionsLabel.setText('Dim: %s x %s' % (x, y))

  def __setupConnections(self):
    self.connect(self.levelView, SIGNAL('itemSelected(QGraphicsItem)'),
                 self.propEd.setFromItem)
    self.connect(self.levelView, SIGNAL('itemDeselected'),
                 self.propEd.setFromItem)
    self.connect(self.levelView, SIGNAL('mouseAt'),
                 self.__updateMousePosition)
    self.connect(self.levelView, SIGNAL('sceneSize'),
                 self.__updateSceneDimensions)

    self.connect(self.tileList, SIGNAL('itemSelected(PyQt_PyObject)'),
                 self.toolbar.adjustSettings)

  def __setupActions(self):
    self.connect(self.actionNew_level,
                 SIGNAL('triggered()'),
                 self.newLevel)
    self.connect(self.actionLoad,
                 SIGNAL('triggered()'),
                 self.load)
    self.connect(self.actionLoad_all,
                 SIGNAL('triggered()'),
                 self.loadAll)
    self.connect(self.actionSave_image,
                 SIGNAL('triggered()'),
                 self.saveImage)
    self.connect(self.actionAbout_Qt,
                 SIGNAL('triggered()'),
                 qApp.aboutQt)
    self.connect(self.actionSave_XML,
                 SIGNAL('triggered()'),
                 self.saveXML)

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
      if not filename.isEmpty() \
      and not self.loadImage(filename) \
      and not self.loadXML(filename):
        unreadable.append(filename)
        
    if unreadable and options.info_load_error:
      flist = ''
      for s in unreadable:
        flist += s + '<br />'
      InfoWindow.info(self.trUtf8('Following files could not be loaded:'),
                      flist, self)
#      warn = str('Following files could not be loaded: %s' % flist)
#      print warn

  def loadAll(self):
    files = [QString(os.path.join(options.terrain_path, f))
             for f in os.listdir(options.terrain_path)]
    files.extend([QString(os.path.join(options.db_path, f))
                  for f in os.listdir(options.db_path)])
    self.load(files)

  def loadImage(self, filename):
    newImage = QPixmap()
    if not newImage.load(filename):
      return False
    else:
      info = {}
      info['pixmap'] = os.path.basename(str(filename))
      info['pixmap_size'] = newImage.width(), newImage.height()
      info['name'] = info['pixmap'].rsplit('.', 1)[0]
      info['type'] = 'BackgroundItem'
      self.tileList.addItem(newImage, info)
      return True

  def loadXML(self, filename):
    try:
      # get the info list
      filename = str(filename)
      name = os.path.basename(filename).rsplit('.', 1)[0]
      imported = self.dbm.import_file(filename)
      info = imported['props']

      # craft that list
      del info['editor_enabled']
      info['name'] = name
      info['type'] = 'EventItem'
      k = imported['gfx'].keys()[0]
        # this is the image-resource name from XML
      info['pixmap'] = imported['gfx'][k]['file']
      
      # get the pixmap
      pixmap = QPixmap()
      if not pixmap.load(os.path.join(options.gfx_path, info['pixmap'])):
        return False
      info['pixmap_size'] = pixmap.width(), pixmap.height()

      self.tileList.addItem(pixmap, info)

      return True
#    except AttributeError, e:
#      print 'AttributeError:', e.message
#      return False
#    except KeyError, e:
#      print 'KeyError:', e.message
#      return False
    except Exception, e:
#      print 'Exception:', e.message
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
    if filename.indexOf('.') == -1:
      filename.append('.png')
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
    if not filename.endsWith('.xml'):
      filename.append('.xml')
    if not xw.XMLWriter.writeEventsFile(filename, self.levelView.scene):
      warn = 'Could not write file:\n%s' %filename
      QMessageBox.warning(self,
                          self.trUtf8('Save as XML'),
                          self.trUtf8(warn))
