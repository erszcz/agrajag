#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import pickle

import formation as f
import mainwindow as mw


class TileListItem(QListWidgetItem):
  def __init__(self, pixmap, info, parent=None):
    '''
    @type  info: C{dict}
    @param info: A dictionary with item properties.

    @type  parent: C{QListWidget}
    @param parent: Parent list item for this widget. Defaults to None.
    '''

    QListWidgetItem.__init__(self, parent)
    self.pixmap = pixmap
    self.setIcon(QIcon(self.pixmap))
    self.setToolTip(info['name'])

    self.info = info

    self.setFlags(Qt.ItemIsEnabled |
                  Qt.ItemIsSelectable |
                  Qt.ItemIsDragEnabled)

  def pickledInfo(self):
    return QString(pickle.dumps(self.info))


class TileList(QListWidget):
  def __init__(self, parent = None):
    QListWidget.__init__(self, parent)

    self.__items = []

    self.formation = {}

    self.connect(self, SIGNAL('currentItemChanged(QListWidgetItem *, QListWidgetItem *)'),
                 self.__currentItemChanged)

  # slot
  def __currentItemChanged(self, item):
    if item.info['type'] in ['BackgroundItem', 'EventItem']:
      self.emit(SIGNAL('itemSelected(PyQt_PyObject)'), item.info['type'])
    else:
      raise Exception('unknown item type: %s' % item.info['type'])

  def addItem(self, pixmap, info, update=True):
    # hardly elaborate...
    tile = {'pixmap': pixmap,
            'info': info}
    self.__items.append(tile)
    self.updateItems()

  def updateItems(self):
    self.clear()
    self.__items.sort(key=lambda x: x['info']['name'].lower())
    for x in self.__items:
      QListWidget.addItem(self, TileListItem(x['pixmap'], x['info'], self))

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
      event.setDropAction(Qt.MoveAction)
      event.accept()
    else:
      event.ignore()

  def startDrag(self, supportedActions):
    for widget in qApp.topLevelWidgets():
      if isinstance(widget, mw.MainWindow):
        main = widget
    formation = main.toolbar.formation()
    if formation == 'NoFormation':
      self.__startItemDrag()
    else:
      self.__startFormationDrag(formation)

  def __startItemDrag(self):
    item = self.currentItem()

    itemData = QByteArray()
    dataStream = QDataStream(itemData, QIODevice.WriteOnly)
    pixmap = item.pixmap

    dataStream << pixmap << item.pickledInfo()

    mimeData = QMimeData()
    mimeData.setData('agrajag-object', itemData)

    drag = QDrag(self)
    drag.setMimeData(mimeData)
    drag.setHotSpot(QPoint(pixmap.width() / 2, pixmap.height() / 2))
    drag.setPixmap(pixmap)

    drag.start(Qt.MoveAction)

  def __startFormationDrag(self, frmCls):
    item = self.currentItem()

    self.emit(SIGNAL('requestFormation'))
    formation = eval('f.' + self.formation['type'])(item.info,
                                                    **self.formation['args'])
    data = pickle.dumps(formation)

    mdata = QMimeData()
    mdata.setData('agrajag-formation', data)

    drag = QDrag(self)
    drag.setMimeData(mdata)
    drag.setHotSpot(QPoint(item.pixmap.width() / 2,
                           item.pixmap.height() / 2))
    drag.setPixmap(item.pixmap)

    drag.exec_(Qt.MoveAction)

  def setFormation(self, formation, args):
    self.formation = {'type': str(formation),
                      'args': args}

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
