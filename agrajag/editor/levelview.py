#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import pickle

from propertyeditordialog import PropertyEditorDialog
from constants import BackgroundItem, EventItem

class AGItem(QGraphicsPixmapItem):
  def __init__(self, pixmap, pos, props):
    QGraphicsPixmapItem.__init__(self, pixmap)
    self.setPos(QPointF(pos))
    self.setToolTip(props['name'])

    self.props = props

  def editProperties(self):
    dlg = PropertyEditorDialog(self.props)
    dlg.exec_()

  def contextMenuEvent(self, event):
    menu = QMenu()
    editProperties = QAction('Edit properties', qApp)
    qApp.connect(editProperties, SIGNAL('triggered()'),
                 self.editProperties)
    menu.addAction(editProperties)
    menu.exec_(event.screenPos())

  def pickledProperties(self):
    return QString(pickle.dumps(self.props))

  def getType(self): return self.props['type']
  type = property(getType)

class AGBackgroundItem(AGItem):
  pass

class AGEventItem(AGItem):
  pass


class LevelView(QGraphicsView):
  def __init__(self, parent=None):
    QGraphicsView.__init__(self, parent)
    self.setBackgroundBrush(QBrush(Qt.CrossPattern))

    self.dragStartPos = None
    self.dragHotSpot = None

    # bez layerow na start, zeby bylo latwiej
    self.newScene(QSize(800, 1000))

  def newScene(self, size):
    self.scene = QGraphicsScene()
    self.scene.setSceneRect(0, 0, size.width(), size.height())
    self.setScene(self.scene)

    self.setMaximumSize(size)

  def snapshot(self):
    image = QImage(self.scene.width(),
                   self.scene.height(),
                   QImage.Format_ARGB32)
    painter = QPainter(image)
    self.scene.render(painter)

    return image

  def placeItem(self, pixmap, pos, props):
    if props['type'] == BackgroundItem:
      item = AGBackgroundItem(pixmap, pos, props)
    elif props['type'] == EventItem:
      item = AGEventItem(pixmap, pos, props)
    self.scene.addItem(item)

  def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton \
    and self.items(event.pos()):
      self.dragStartPos = self.dragHotSpot = event.pos()

  def mouseMoveEvent(self, event):
    if event.buttons() & Qt.LeftButton \
    and self.dragStartPos is not None \
    and event.pos() - self.dragStartPos >= QApplication.startDragDistance():
      item = self.itemAt(self.dragStartPos)
      if not item:
        return
      
      itemData = QByteArray()
      dataStream = QDataStream(itemData, QIODevice.WriteOnly)
      pixmap = item.pixmap()

      dataStream << pixmap << item.pickledProperties()

      mimeData = QMimeData()
      mimeData.setData('image/x-tile', itemData)

      drag = QDrag(self)
      drag.setMimeData(mimeData)
      drag.setPixmap(pixmap)
      
      hs = self.mapToScene(self.dragHotSpot)
      self.dragHotSpot = item.mapFromScene(hs).toPoint()
      drag.setHotSpot(self.dragHotSpot)

      self.scene.removeItem(item)
      self.dragStartPos = None
      drag.start(Qt.MoveAction)

  def dragEnterEvent(self, event):
    if event.mimeData().hasFormat('image/x-tile'):
      event.accept()
    else:
      event.ignore()

  def dragMoveEvent(self, event):
    if event.mimeData().hasFormat('image/x-tile'):
      event.setDropAction(Qt.MoveAction)
      event.accept()
    else:
      event.ignore()

  def dropEvent(self, event):
    if event.mimeData().hasFormat('image/x-tile'):
      tileData = event.mimeData().data('image/x-tile')
      dataStream = QDataStream(tileData, QIODevice.ReadOnly)
      
      pixmap = QPixmap()
      pickledProps = QString()
      dataStream >> pixmap >> pickledProps
      props = pickle.loads(str(pickledProps))

      hotSpot = self.dragHotSpot if self.dragHotSpot else \
                QPoint(pixmap.width() / 2, pixmap.height() / 2)
      self.dragHotSpot = None
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
      self.placeItem(pixmap, self.mapToScene(pos), props)

      event.setDropAction(Qt.MoveAction)
      event.accept()
    else:
      event.ignore()

