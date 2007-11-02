#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class TileList(QListWidget):
  def addTile(self, pixmap, filename):
    tileItem = QListWidgetItem(self)
    tileItem.setIcon(QIcon(pixmap))
    tileItem.setData(Qt.UserRole, QVariant(pixmap))
    tileItem.setData(Qt.UserRole + 1, QVariant(filename))
    tileItem.setFlags(Qt.ItemIsEnabled | 
                      Qt.ItemIsSelectable |
                      Qt.ItemIsDragEnabled)

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
      event.setDropAction(Qt.MoveAction)
      event.accept()
    else:
      event.ignore()

  def startDrag(self, supportedActions):
    item = self.currentItem()

    itemData = QByteArray()
    dataStream = QDataStream(itemData, QIODevice.WriteOnly)
    pixmap = QPixmap(item.data(Qt.UserRole))
    filename = item.data(Qt.UserRole + 1).toString()

    dataStream << pixmap << filename

    mimeData = QMimeData()
    mimeData.setData('image/x-tile', itemData)

    drag = QDrag(self)
    drag.setMimeData(mimeData)
    drag.setHotSpot(QPoint(pixmap.width() / 2, pixmap.height() / 2))
    drag.setPixmap(pixmap)

    drag.start(Qt.MoveAction)

