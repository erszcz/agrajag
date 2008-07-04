#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import pickle
import os.path

import propertyeditor
import propertyeditordialog

import options as ops

class AGItem(QGraphicsPixmapItem):
  def __init__(self, pixmap, info):
    QGraphicsPixmapItem.__init__(self, pixmap)

    self.setToolTip(info['name'])
    self.setFlag(QGraphicsItem.ItemIsSelectable, True)
    self.setFlag(QGraphicsItem.ItemIsMovable, True)

    self.info = info
    self._props = {}

  def __getProps(self):
    self._props['posx'] = self.scenePos().x()
    self._props['posy'] = self.scenePos().y()
    return self._props
  props = property(__getProps)

  def adjustPos(self):
    pos = self.scenePos()
    self.setPos(*_snapPos(pos.x(), pos.y()))

  def editProperties(self):
    dlg = propertyeditordialog.PropertyEditorDialog(self.props)
    dlg.exec_()

  def standardise(self):
    others = self.scene().selectedItems()
    others.remove(self)
    for item in others:
      item._props = self._props.copy()

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

    standardiseGroup = QAction('Standardise group', qApp)
    selected = self.scene().selectedItems()
    if len(selected) > 1:
      standardiseGroup.setEnabled(True)

      pattern = selected[0].info['name']
      for item in selected:
        if item.info['name'] != pattern:
          standardiseGroup.setEnabled(False)
    else:
      standardiseGroup.setEnabled(False)
    qApp.connect(standardiseGroup, SIGNAL('triggered()'),
                 self.standardise)
    menu.addAction(standardiseGroup)

    menu.exec_(event.screenPos())

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

    
class AGBackgroundItem(AGItem):
  pass


class AGEventItem(AGItem):
  def __init__(self, pixmap, info):
    AGItem.__init__(self, pixmap, info)
    if self.isBonus():
      self._props = {'time': 0,
                     'bonus_cls_name': self.info['name'],
                     'mover_cls_name': '',
                     'group': ''}
    else:
      self._props = {'time': 0,
                     'object_cls_name': self.info['name'],
                     'mover_cls_name': '',
                     'bonus_cls_name': '',
                     'group': ''}

  def isBonus(self):
    return True if self.info['name'].find('Bonus') != -1 else False

  @staticmethod
  def fromSkeleton(skeleton):
    pixmap = QPixmap(os.path.join(ops.gfx_path, skeleton.info['pixmap']))
    item = AGEventItem(pixmap, skeleton.info)
    if skeleton.mover:
      item._props['mover_cls_name'] = skeleton.mover
    return item


class LevelView(QGraphicsView):
  def __init__(self, parent=None):
    QGraphicsView.__init__(self, parent)
    self.setBackgroundBrush(QBrush(QImage(os.path.join(ops.gfx_path, 'grid.png'))))
    self.setInteractive(True)
    self.setDragMode(QGraphicsView.RubberBandDrag)

    self.newScene(QSize(*ops.scene_size))

  def newScene(self, size):
    if type(self.scene) == QObject:
      self.disconnect(self.scene, SIGNAL('selectionChanged()'))
    self.scene = LevelScene()
    self.scene.setSceneRect(0, 0, size.width(), size.height())
    self.setScene(self.scene)
    self.scene.view = self

    self.setMaximumSize(size)
    self.ensureVisible(0, 0, 1, 1)
    
    self.connect(self.scene, SIGNAL('itemSelected(QGraphicsItem)'),
                 self,       SIGNAL('itemSelected(QGraphicsItem)'))
    self.emit(SIGNAL('sceneSize'), int(self.scene.width()),
                                   int(self.scene.height()))

  def snapshot(self):
    image = QImage(self.scene.width(),
                   self.scene.height(),
                   QImage.Format_ARGB32)
    painter = QPainter(image)
    self.scene.render(painter)

    return image

  def createItem(self, pixmap, pos, info):
    if info['type'] == 'BackgroundItem':
      item = AGBackgroundItem(pixmap, info)
    elif info['type'] == 'EventItem':
      item = AGEventItem(pixmap, info)
    self.placeItem(item, pos)

  def placeItem(self, item, pos):
    item.setPos(pos)
    self.connect(self.scene, SIGNAL('changed(const QList<QRectF>&)'),
                 item.adjustPos)
    self.scene.addItem(item)

  def mouseMoveEvent(self, event):
    QGraphicsView.mouseMoveEvent(self, event)
    pos = self.mapToScene(event.pos())
    self.emit(SIGNAL('mouseAt'), int(pos.x()), int(pos.y()))

  def dragEnterEvent(self, event):
    if event.mimeData().hasFormat('agrajag-object') \
    or event.mimeData().hasFormat('agrajag-formation'):
      event.accept()
    else:
      event.ignore()

  def dragMoveEvent(self, event):
    if event.mimeData().hasFormat('agrajag-object') \
    or event.mimeData().hasFormat('agrajag-formation'):
      event.setDropAction(Qt.MoveAction)
      event.accept()
    else:
      event.ignore()

  def dropEvent(self, event):
    if event.mimeData().hasFormat('agrajag-object'):
      self.__acceptAgrajagObjectDrop(event)
    elif event.mimeData().hasFormat('agrajag-formation'):
      self.__acceptFormationDrop(event)
    else:
      event.ignore()

  def __acceptAgrajagObjectDrop(self, event):
    tileData = event.mimeData().data('agrajag-object')
    dataStream = QDataStream(tileData, QIODevice.ReadOnly)
    
    pixmap = QPixmap()
    pickledinfo = QString()
    dataStream >> pixmap >> pickledinfo
    info = pickle.loads(str(pickledinfo))

    hotSpot = QPoint(pixmap.width() / 2, pixmap.height() / 2)
    # check whether to snap or not when dropping
    if ops.always_snap or event.keyboardModifiers() == Qt.ShiftModifier:
      posX = self.mapToScene(event.pos()).x() - hotSpot.x()
      posY = self.mapToScene(event.pos()).y() - hotSpot.y()
      pos = self.mapFromScene(_snapPos(posX, posY, QPointF))
    else:  # don't snap to grid
      pos = QPoint(event.pos().x() - hotSpot.x(),
                   event.pos().y() - hotSpot.y())
    self.createItem(pixmap, self.mapToScene(pos), info)

    event.setDropAction(Qt.MoveAction)
    event.accept()

  def __acceptFormationDrop(self, event):
    data = event.mimeData().data('agrajag-formation')
    
    formation = pickle.loads(data)
    for skel, pos in formation:
      posF = QPointF(event.pos() + pos)
      self.placeItem(AGEventItem.fromSkeleton(skel), posF)

    event.setDropAction(Qt.MoveAction)
    event.accept()


class LevelScene(QGraphicsScene):
  def __init__(self):
    QGraphicsScene.__init__(self)

    self.connect(self, SIGNAL('selectionChanged()'),
                 self.__handleSelection)
    self.connect(self, SIGNAL('changed(const QList<QRectF>&)'),
                 self.__handleSelection)
  
  def __handleSelection(self):
    items = self.selectedItems()
    if len(items) == 1:
      self.emit(SIGNAL('itemSelected(QGraphicsItem)'), items[0])
    else:
      self.emit(SIGNAL('itemSelected(QGraphicsItem)'), QGraphicsPixmapItem())


def _snapPos(x, y, rtype=None):
  gridSize = ops.grid_size
  offsetX = x % gridSize
  offsetY = y % gridSize
  snapX = x - offsetX
  snapY = y - offsetY
  x = snapX if offsetX < gridSize/2 else snapX + gridSize
  y = snapY if offsetY < gridSize/2 else snapY + gridSize

  if rtype:
    return rtype(x, y)
  else:
    return x, y
