#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class LevelView(QGraphicsView):
  def __init__(self, parent=None):
    QGraphicsView.__init__(self, parent)
    self.setBackgroundBrush(QBrush(Qt.CrossPattern))

    self.dragStartPos = None

    # bez layerow na start, zeby bylo latwiej
    self.newScene(QSize(800, 1000))
      # teraz zastanawialem sie co zrobic, zeby mi tego cham nie centrowal

  def newScene(self, size):
    self.scene = QGraphicsScene()
    self.scene.setSceneRect(0, 0, size.width(), size.height())
    self.setScene(self.scene)

    self.setMaximumSize(size)

  def placeTile(self, pixmap, pos):
    graphicsItem = QGraphicsPixmapItem(pixmap)
    graphicsItem.setOffset(QPointF(pos))
    self.scene.addItem(graphicsItem)

  def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton \
    and self.items(event.pos()):
      self.dragStartPos = event.pos()

  def mouseMoveEvent(self, event):
    if event.buttons() & Qt.LeftButton \
    and self.dragStartPos is not None \
    and event.pos() - self.dragStartPos >= QApplication.startDragDistance():
      item = self.itemAt(self.dragStartPos)
      
      itemData = QByteArray()
      dataStream = QDataStream(itemData, QIODevice.WriteOnly)
      pixmap = item.pixmap()

      dataStream << pixmap  # << filename  # pozniej trzeba bedzie dodac

      mimeData = QMimeData()
      mimeData.setData('image/x-tile', itemData)

      drag = QDrag(self)
      drag.setMimeData(mimeData)
      drag.setHotSpot(QPoint(pixmap.width() / 2, pixmap.height() / 2))
      drag.setPixmap(pixmap)

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
      filename = QString()
      dataStream >> pixmap >> filename

      hotSpot = QPoint(pixmap.width() / 2, pixmap.height() / 2)
      pos = QPoint(event.pos().x() - hotSpot.x(),
                   event.pos().y() - hotSpot.y())
      self.placeTile(pixmap, self.mapToScene(pos))

      event.setDropAction(Qt.MoveAction)
      event.accept()
    else:
      event.ignore()

