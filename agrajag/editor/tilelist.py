#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import pickle

class TileListItem(QListWidgetItem):
  BackgroundItem = QListWidgetItem.UserType
  EventItem = QListWidgetItem.UserType + 1

  def __init__(self, props, parent=None):
    '''
    @type  props: C{dict}
    @param props: A dictionary with item properties.

    @type  parent: C{QListWidget}
    @param parent: Parent list item for this widget. Defaults to None.
    '''

    QListWidgetItem.__init__(self, parent)
    self.pixmap = props.pop('pixmap')
    self.setIcon(QIcon(self.pixmap))

    if len(props) == 1:
      props['type'] = TileListItem.BackgroundItem
    else:
      props['type'] = TileListItem.EventItem
      
    self.props = props

    self.setFlags(Qt.ItemIsEnabled |
                  Qt.ItemIsSelectable |
                  Qt.ItemIsDragEnabled)

  def pickledProperties(self):
    return QString(pickle.dumps(self.props))


class TileList(QListWidget):
  #def addTile(self, pixmap, filename):
  #  tileItem = QListWidgetItem(self)
  #  tileItem.setIcon(QIcon(pixmap))
  #  tileItem.setData(Qt.UserRole, QVariant(pixmap))
  #  tileItem.setData(Qt.UserRole + 1, QVariant(filename))
  #  tileItem.setFlags(Qt.ItemIsEnabled | 
  #                    Qt.ItemIsSelectable |
  #                    Qt.ItemIsDragEnabled)
  def addTile(self, props):
    tile = TileListItem(props, self)

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
    pixmap = item.pixmap

    # The data stream supports storing QPixmaps directly. The other
    # properties of an item are stored as a QString containing pickled
    # Python dictionary.
    dataStream << pixmap << item.pickledProperties()

    mimeData = QMimeData()
    mimeData.setData('image/x-tile', itemData)

    drag = QDrag(self)
    drag.setMimeData(mimeData)
    drag.setHotSpot(QPoint(pixmap.width() / 2, pixmap.height() / 2))
    drag.setPixmap(pixmap)

    drag.start(Qt.MoveAction)

#if __name__ == '__main__':
# qapp = QApplication([])
## test 1
# pmap = QPixmap()
# pmap.load('/home/lavrin/work/agrajag/gfx/terrain_new/cliff_cc00.png')
# tl = TileListItem({'pixmap': pmap,
#                    'filename': '/zxc/asd/qwe/asd',
#                    'tpl': ('sa', 'ss', 'zxc'),
#                    'flt': 456.9,
#                    'bl': True,
#                    'nt': 12345})

## test 2
# byteArray = QByteArray()
# inStream = QDataStream(byteArray, QIODevice.WriteOnly)

# data = {QString('one'): QVariant(1.46),
#         QString('two'): QVariant(2),
#         QString('three'): QVariant('zxczc')}
# for x, y in data.items():
#   inStream << x << y
#   print x, y

# outStream = QDataStream(byteArray, QIODevice.ReadOnly)
# while not outStream.atEnd():
#   c = QString()
#   v = QVariant()
#   outStream >> c >> v
#   print c, v
