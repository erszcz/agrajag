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
  def __init__(self, pixmap, pos, info, props = {}):
    QGraphicsPixmapItem.__init__(self, pixmap)
    # check pos
    x, y, maxX, maxY = pos
    if x < -pixmap.width() + ops.grid_size:
      x += ops.grid_size
    elif x > maxX - ops.grid_size:
      x -= ops.grid_size
    if y < -pixmap.height() + ops.grid_size:
      y += ops.grid_size
    elif y > maxY - ops.grid_size:
      y -= ops.grid_size
    self.setPos(QPointF(x, y))
    self.setToolTip(info['name'])
    self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    self.info = info
    if not props:
      self.props = {'posx': self.scenePos().x(),
                    'posy': self.scenePos().y()}
    else:
      self.props = props
      self.props['posx'] = self.scenePos().x()
      self.props['posy'] = self.scenePos().y()

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

  def itemData(self):
    itemData = QByteArray()
    dataStream = QDataStream(itemData, QIODevice.WriteOnly)
    pixmap = self.pixmap()
    dataStream << pixmap << self.pickledInformation() << self.pickledProperties()
    return itemData

    
class AGBackgroundItem(AGItem):
  pass


class AGEventItem(AGItem):
  def __init__(self, pixmap, pos, info, props = {}):
    AGItem.__init__(self, pixmap, pos, info, props)
    if not props:
      if self.isBonus():
        self.props = {'posx': self.scenePos().x(),
                      'posy': self.scenePos().y(),
                      'time': 0,
                      'bonus_cls_name': self.info['name'],
                      'mover_cls_name': '',
                      'group': ''}
      else:
        self.props = {'posx': self.scenePos().x(),
                      'posy': self.scenePos().y(),
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
    self.setBackgroundBrush(QBrush(QImage(os.path.join(ops.gfx_path, 'grid.png'))))
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
    self.scene = LevelScene()
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
    pos = pos.x(), pos.y(), self.scene.width(), self.scene.height()
    if info['type'] == 'BackgroundItem':
      item = AGBackgroundItem(pixmap, pos, info, props)
    elif info['type'] == 'EventItem':
      item = AGEventItem(pixmap, pos, info, props)
    self.scene.addItem(item)

  def dragEnterEvent(self, event):
    if event.mimeData().hasFormat('agrajag-object') \
    or event.mimeData().hasFormat('agrajag-object-list'):
      event.accept()
    else:
      event.ignore()

  def dragMoveEvent(self, event):
    if event.mimeData().hasFormat('agrajag-object') \
    or event.mimeData().hasFormat('agrajag-object-list'):
      event.setDropAction(Qt.MoveAction)
      event.accept()
    else:
      event.ignore()

  def dropEvent(self, event):
    if event.mimeData().hasFormat('agrajag-object'):
      self.__acceptAgrajagObjectDrop(event)
    elif event.mimeData().hasFormat('agrajag-object-list'):
      self.__acceptAgrajagObjectListDrop(event)
    else:
      event.ignore()

  def __acceptAgrajagObjectDrop(self, event):
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
    if ops.always_snap or event.keyboardModifiers() == Qt.ShiftModifier:
      posX = self.mapToScene(event.pos()).x() - hotSpot.x()
      posY = self.mapToScene(event.pos()).y() - hotSpot.y()
      pos = self.mapFromScene(_snapPos(posX, posY, QPointF))
    else:  # don't snap to grid
      pos = QPoint(event.pos().x() - hotSpot.x(),
                   event.pos().y() - hotSpot.y())
    self.placeItem(pixmap, self.mapToScene(pos), info, props)

    event.setDropAction(Qt.MoveAction)
    event.accept()

  def __acceptAgrajagObjectListDrop(self, event):
    listData = event.mimeData().data('agrajag-object-list')
    listStream = QDataStream(listData, QIODevice.ReadOnly)
    count = QVariant()
    listStream >> count
    count = count.toInt()[0]

    data = QByteArray()

    pixmap = QPixmap()
    pickledInfo = QString()
    pickledProps = QString()

    items = []
    for i in range(count):
      listStream >> data
      stream = QDataStream(data, QIODevice.ReadOnly)
      stream >> pixmap >> pickledInfo >> pickledProps
      info = pickle.loads(str(pickledInfo)) if str(pickledInfo) else {}
      props = pickle.loads(str(pickledProps)) if str(pickledProps) else {}

      items.append((pixmap, info, props))

    deltaX = event.pos().x() - items[0][2]['posx']
    deltaY = event.pos().y() - items[0][2]['posy']
    hotSpot = self.drag.hotSpot()

    for pixmap, info, props in items:
      posX = props['posx'] + deltaX - hotSpot.x()
      posY = props['posy'] + deltaY - hotSpot.y()
      if ops.always_snap or event.keyboardModifiers() == Qt.ShiftModifier:
        pos = _snapPos(posX, posY, QPointF)
      else:
        pos = QPointF(posX, posY)
      self.placeItem(pixmap, pos, info, props)
        
    event.setDropAction(Qt.MoveAction)
    event.accept()


class LevelScene(QGraphicsScene):
  def mousePressEvent(self, event):
    QGraphicsScene.mousePressEvent(self, event)

    self.thisItem = self.itemAt(event.scenePos())

  def mouseMoveEvent(self, event):
    QGraphicsScene.mouseMoveEvent(self, event)

    selected = self.selectedItems()
    pA = QPointF(event.screenPos())
    pB = QPointF(event.buttonDownScreenPos(Qt.LeftButton))
    self.thisItem = self.itemAt(event.buttonDownScenePos(Qt.LeftButton))

    if len(selected) < 1 \
    or QLineF(pA, pB).length() < QApplication.startDragDistance() \
    or not self.thisItem:
      self.thisItem = None
      return
    
    selected.remove(self.thisItem)
    itemData = QByteArray()
    dataStream = QDataStream(itemData, QIODevice.WriteOnly)
    dataStream << QVariant(len(selected) + 1)
    dataStream << self.thisItem.itemData()
    for item in selected:
      dataStream << item.itemData()

    mimeData = QMimeData()
    mimeData.setData('agrajag-object-list', itemData)

    drag = QDrag(self.views()[0])
    drag.setMimeData(mimeData)
#    drag.setHotSpot(QPoint(self.thisItem.pixmap().width() / 2,
#                           self.thisItem.pixmap().height() / 2))
#    drag.setPixmap(self.thisItem.pixmap())
#
    group = self.createItemGroup([self.thisItem] + selected)
    self.image = QImage(group.boundingRect().size().toSize(),
                        QImage.Format_ARGB32)
    painter = QPainter(self.image)
    self.render(painter, QRectF(), group.boundingRect())
    drag.setPixmap(QPixmap.fromImage(self.image))
#
    drag.setHotSpot(group.boundingRect().center().toPoint())
    self.destroyItemGroup(group)

    for item in selected:
      item.hide()
    self.thisItem.hide()
    self.views()[0].drag = drag
    drag.exec_()
    for item in selected:
      self.removeItem(item)
    self.removeItem(self.thisItem)
    self.views()[0].drag = None

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
