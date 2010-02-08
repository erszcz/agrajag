#!/usr/bin/env python
#coding: utf-8

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_editor import Ui_MainWindow
from newleveldialog import NewLevelDialog

import formation as f
import propertyeditor as pe
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

    self.__cachedIndex = 0
    self.__lastType = ''

    self.setWindowTitle (self.trUtf8('Formations toolbar'))
    self.actionToggleView = self.toggleViewAction()

    self.__wdgactions = {}

    # formations combobox
    self.formationLabel = QLabel(self.trUtf8('Formation:'))
    self.formationLabel.setIndent(5)
    self.__wdgactions[self.formationLabel] = self.addWidget(self.formationLabel)
    self.formationCombo = QComboBox(self)
    self.formationCombo.addItems(f.formations)
    self.__wdgactions[self.formationCombo] = self.addWidget(self.formationCombo)

    # item count
    label = QLabel(self.trUtf8('Ship count:'))
    label.setIndent(5)
    self.__wdgactions[label] = self.addWidget(label)
    self.count = QSpinBox(self)
    self.count.setRange(1, 20)
    self.count.setValue(5)
    self.__wdgactions[self.count] = self.addWidget(self.count)

    # mover preselection
    label = QLabel(self.trUtf8('Mover:'))
    label.setIndent(5)
    self.__wdgactions[label] = self.addWidget(label)
    self.moverCombo = QComboBox(self)
    self.moverCombo.addItems(['NoMover'] + pe.mover_params.keys())
    self.__wdgactions[self.moverCombo] = self.addWidget(self.moverCombo)

    # mover param
    self.__setupParamWidgets()

    self.__setupActions()
    self.__setupConnections()

    self.__currentFormationChanged(0)

  def __setupActions(self):
    pass

  def __setupConnections(self):
    self.connect(self.formationCombo, SIGNAL('currentIndexChanged(int)'),
                 self.__currentFormationChanged)
    self.connect(self.moverCombo, SIGNAL('currentIndexChanged(int)'),
                 self.__updateParamWidgets)

  def __setupParamWidgets(self):
    self.paramLabels = {}
    self.paramSpins = {}
    for mover, params in pe.mover_params.items():
      for param in params.keys():
        labelText = str(self.trUtf8('Mover parameter (%s):'))
        paramKey = ':'.join((mover, param))
        paramWdg = self.paramLabels[paramKey] = QLabel(labelText % param)
        paramWdg.setIndent(5)
        self.__wdgactions[paramWdg] = self.addWidget(paramWdg)
        QAction.setVisible(self.__wdgactions[paramWdg], False)

        if type(params[param]) == int:
          paramWdg = self.paramSpins[paramKey] = QSpinBox()
        elif type(params[param]) == float:
          paramWdg = self.paramSpins[paramKey] = QDoubleSpinBox()
        else:
          raise Exception('undefined parameter type %s' % type(params[param]))
        paramWdg.setRange(-1000000, 1000000)
        paramWdg.setValue(params[param])
        self.__wdgactions[paramWdg] = self.addWidget(paramWdg)
        QAction.setVisible(self.__wdgactions[paramWdg], False)

  def __updateParamWidgets(self):
    mover = str(self.moverCombo.currentText())
    for item in self.paramLabels:
      QAction.setVisible(self.__wdgactions[self.paramLabels[item]], False)
    for item in self.paramSpins:
      QAction.setVisible(self.__wdgactions[self.paramSpins[item]], False)
    if pe.mover_params.has_key(mover):
      for param in pe.mover_params[mover]:
        QAction.setVisible(self.__wdgactions[self.paramLabels[':'.join((mover, param))]], True)
        QAction.setVisible(self.__wdgactions[self.paramSpins[':'.join((mover, param))]], True)
        self.paramLabels[':'.join((mover, param))].setEnabled(True)
        self.paramSpins[':'.join((mover, param))].setEnabled(True)

  def __currentFormationChanged(self, index):
    if index == 0:
      for x in self.findChildren(QWidget, QString()):
        x.setEnabled(False)
      self.formationLabel.setEnabled(True)
      self.formationCombo.setEnabled(True)
      for x in self.formationCombo.findChildren(QWidget, QString()):
        x.setEnabled(True)
    else:
      for x in self.findChildren(QWidget, QString()):
        x.setEnabled(True)
        for y in x.findChildren(QWidget, QString()):
          y.setEnabled(True)

    if self.formationCombo.currentIndex() != -1 and self.__lastType == 'EventItem':
      self.__cachedIndex = index

  def sendFormation(self):
    mover = str(self.moverCombo.currentText())
    if mover != 'NoMover':
      params = {}
      for param in self.paramSpins.keys():
        if param.startswith(mover):
          params[param] = self.paramSpins[param].value()
      args = {'count': self.count.value(),
              'mover': mover,
              'mover_params': params}
    else:
      args = {'count': self.count.value(),
              'mover': ''}
    self.emit(SIGNAL('sendFormation(const QString&, PyQt_PyObject)'),
              self.formationCombo.currentText(), args)

  def adjustSettings(self, type):
    self.__lastType = type
    if type == 'BackgroundItem':
      self.formationCombo.setCurrentIndex(0)
      self.setEnabled(False)
    elif type == 'EventItem':
      self.setEnabled(True)
      self.__currentFormationChanged(self.__cachedIndex)
      self.formationCombo.setCurrentIndex(self.__cachedIndex)
    else:
      raise Exception('unknown item type: %s' % type)

  def contextMenuEvent(self, event):
    pass

  def formation(self):
    return self.formationCombo.currentText()


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
    self.menuOptions.addAction(self.toolbar.actionToggleView)
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
    self.connect(self.tileList, SIGNAL('requestFormation'),
                 self.toolbar.sendFormation)

    self.connect(self.toolbar,
                 SIGNAL('sendFormation(const QString&, PyQt_PyObject)'),
                 self.tileList.setFormation)

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
      and not self.loadImage(filename, update=False) \
      and not self.loadXML(filename, update=False):
        unreadable.append(filename)
    self.tileList.updateItems()
        
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

  def loadImage(self, filename, update=True):
    newImage = QPixmap()
    if not newImage.load(filename):
      return False
    else:
      info = {}
      info['pixmap'] = os.path.basename(str(filename))
      info['pixmap_size'] = newImage.width(), newImage.height()
      info['name'] = info['pixmap'].rsplit('.', 1)[0]
      info['type'] = 'BackgroundItem'
      self.tileList.addItem(newImage, info, update)
      return True

  def loadXML(self, filename, update=True):
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

      self.tileList.addItem(pixmap, info, update)

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
