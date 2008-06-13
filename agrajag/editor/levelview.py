#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import pickle
import os.path

import propertyeditor
import propertyeditordialog

import options

class AGItem(QGraphicsPixmapItem):
  def __init__(self, pixmap, pos, info, props = {}):
    QGraphicsPixmapItem.__init__(self, pixmap)
    self.setPos(QPointF(pos))
    self.setToolTip(info['name'])
    self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    self.info = info
    if not props:
      self.props = {'posx': self.mapToScene(0, 0).x(),
                    'posy': self.mapToScene(0, 0).y()}
    else:
      self.props = props
      self.props['posx'] = self.mapToScene(0, 0).x()
      self.props['posy'] = self.mapToScene(0, 0).y()

    self.dragStartPos = None

  def editProperties(self):
    dlg = propertyeditordialog.PropertyEditorDialog(self.props)
    if dlg.exec_():
      self.setPos(self.props['posx'], self.props['posy'])

  def contextMenuEvent(self, event):
    menu = QMenu()
    editProperties = QAction('Edit properties', qApp)
    qApp.connect(editProperties, SIGNAL('triggered()'),
                 self.editProperties)
    menu.addAction(editProperties)

    #>>
    dumpInformation = QAction('Dump information', qApp)
    qApp.connect(dumpInformation, SIGNAL('triggered()'),
                 self.debugDump)
    menu.addAction(dumpInformation)
    #<<

    menu.exec_(event.screenPos())

  def pickledInformation(self):
    return QString(pickle.dumps(self.info))

  def pickledProperties(self):
    return QString(pickle.dumps(self.props))

  # temp
  def debugDump(self):
    print '## %s\n# info:' % str(self)
    for x, y in sorted(self.info.items()):
      print '%s: %s' % (x, str(y))
    print '# props:'
    for x, y in sorted(self.props.items()):
      print '%s: %s' % (x, str(y))
    print
  #<<

  def mousePressEvent(self, event):
    QGraphicsItem.mousePressEvent(self, event)  # to have the default behaviour
    if event.button() == Qt.LeftButton:
      self.dragStartPos = event.pos()

  def mouseMoveEvent(self, event):
    QGraphicsItem.mouseMoveEvent(self, event)  # to have the default behaviour
    if event.buttons() & Qt.LeftButton \
    and self.dragStartPos is not None \
    and event.pos() - self.dragStartPos >= QApplication.startDragDistance():
      itemData = QByteArray()
      dataStream = QDataStream(itemData, QIODevice.WriteOnly)
      pixmap = self.pixmap()

      dataStream << pixmap << self.pickledInformation() << self.pickledProperties()

      mimeData = QMimeData()
      mimeData.setData('agrajag-object', itemData)

      drag = QDrag(self.scene().views()[0])
      drag.setMimeData(mimeData)
      drag.setPixmap(pixmap)
      
      drag.setHotSpot(self.dragStartPos.toPoint())
      self.dragStartPos = None
      self.scene().views()[0].drag = drag
      self.hide()
      drag.exec_(Qt.MoveAction)
      self.scene().views()[0].drag = None
      self.scene().removeItem(self)

class AGBackgroundItem(AGItem):
  pass

class AGEventItem(AGItem):
  def __init__(self, pixmap, pos, info, props = {}):
    AGItem.__init__(self, pixmap, pos, info, props)
    if not props:
      if self.isBonus():
        self.props = {'posx': self.mapToScene(0, 0).x(),
                      'posy': self.mapToScene(0, 0).y(),
                      'time': 0,
                      'bonus_cls_name': self.info['name'],
                      'mover_cls_name': '',
                      'group': ''}
      else:
        self.props = {'posx': self.mapToScene(0, 0).x(),
                      'posy': self.mapToScene(0, 0).y(),
                      'time': 0,
                      'object_cls_name': self.info['name'],
                      'mover_cls_name': '',
                      'bonus_cls_name': '',
                      'group': ''}

  def isBonus(self):
    return True if self.info['name'].find('Bonus') != -1 else False

class LevelView(QGraphicsView):
  def __init__(self, parent=None):
    QGraphicsView.__init__(self, parent)
    self.setBackgroundBrush(QBrush(QImage(os.path.join(options.gfx_path, 'grid.png'))))
    self.setInteractive(True)
    self.setDragMode(QGraphicsView.RubberBandDrag)

    self.drag = None

    # bez layerow na start, zeby bylo latwiej
    self.newScene(QSize(800, 1000))

  # signal
  def __itemsSelected(self):
    items = self.scene.selectedItems()
    if len(items) == 1:
      self.emit(SIGNAL('itemSelected(QGraphicsItem)'), items[0])
    else:
      self.emit(SIGNAL('itemDeselected'))

  def newScene(self, size):
    if type(self.scene) == QObject:
      self.disconnect(self.scene, SIGNAL('selectionChanged()'))
    self.scene = QGraphicsScene()
    self.scene.setSceneRect(0, 0, size.width(), size.height())
    self.setScene(self.scene)

    self.setMaximumSize(size)
    self.ensureVisible(0, 0, 1, 1)
    
    self.connect(self.scene, SIGNAL('selectionChanged()'),
                 self.__itemsSelected)

  def snapshot(self):
    image = QImage(self.scene.width(),
                   self.scene.height(),
                   QImage.Format_ARGB32)
    painter = QPainter(image)
    self.scene.render(painter)

    return image

  def placeItem(self, pixmap, pos, info, props = {}):
    if info['type'] == 'BackgroundItem':
      item = AGBackgroundItem(pixmap, pos, info, props)
    elif info['type'] == 'EventItem':
      item = AGEventItem(pixmap, pos, info, props)
    self.scene.addItem(item)


  def dragEnterEvent(self, event):
    if event.mimeData().hasFormat('agrajag-object'):
      event.accept()
    else:
      event.ignore()

  def dragMoveEvent(self, event):
    if event.mimeData().hasFormat('agrajag-object'):
      event.setDropAction(Qt.MoveAction)
      event.accept()
    else:
      event.ignore()

  def dropEvent(self, event):
    if event.mimeData().hasFormat('agrajag-object'):
      tileData = event.mimeData().data('agrajag-object')
      dataStream = QDataStream(tileData, QIODevice.ReadOnly)
      
      pixmap = QPixmap()
      pickledinfo = QString()
      pickledprops = QString()
      dataStream >> pixmap >> pickledinfo >> pickledprops
      info = pickle.loads(str(pickledinfo))
      pickledprops = str(pickledprops)
      props = pickle.loads(pickledprops) if pickledprops else {}

      if self.drag:
        hotSpot = self.drag.hotSpot()
      else:
        hotSpot = QPoint(pixmap.width() / 2, pixmap.height() / 2)
      # check whether to snap or not when dropping
      if event.keyboardModifiers() == Qt.ShiftModifier:
        # snap to grid
        posX = self.mapToScene(event.pos()).x() - hotSpot.x()
        posY = self.mapToScene(event.pos()).y() - hotSpot.y()
        gridSize = 20

        offsetX = posX % gridSize
        offsetY = posY % gridSize
        snapX = posX - offsetX
        snapY = posY - offsetY
        posX = snapX if offsetX <= gridSize/2 else snapX + gridSize
        posY = snapY if offsetY <= gridSize/2 else snapY + gridSize
        pos = self.mapFromScene(QPointF(posX, posY))
      else:
        # don't snap to grid
        pos = QPoint(event.pos().x() - hotSpot.x(),
                     event.pos().y() - hotSpot.y())
      self.placeItem(pixmap, self.mapToScene(pos), info, props)

      event.setDropAction(Qt.MoveAction)
      event.accept()
    else:
      event.ignore()

