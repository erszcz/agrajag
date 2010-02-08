#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import propertyeditor as pe

import options as ops


formations = ['NoFormation',
              'LineFormation']


class AGEventItemSkeleton:
  def __init__(self, info):
    self.info = info

    self.mover = ''
    self.mover_params = {}


class Formation:
  '''Stores informations about relative item positions.'''

  def __init__(self, info, count, mover='', mover_params={}):
    # item is a dict sotring at least 'pixmap' and dict 'info'
    self._info = info
    self._count = count

    self.setMover(mover, mover_params)

    self._cache = []
    self._nodes = []

    self._calculateSpacing()
    self._layout()

  def __len__(self):
    return self._count

  def __iter__(self):
    if self._cache:
      for x in range(self._count):
        yield self._cache[x], self._nodes[x]
    else:
      for x in range(self._count):
        item = AGEventItemSkeleton(self._info)
        if self.mover:
          item.mover = self.mover
        if self.mover_params:
          item.mover_params = self.mover_params
        self._cache.append(item)
        yield item, self._nodes[x]

  def _calculateSpacing(self):
    '''
    Get the optimal distance between nodes on which the items are placed
    from the item size and grid snap distance.

    This function initialises a number of different instance variables,
    depending on the formation type. Formation subclass must provide any
    needed vars here and stick to their use (probably only in _layout method).
    '''
    pass

  def _layout(self):
    '''Setup the node positions.'''
    pass

  def setMover(self, mover, params={}):
    if mover and mover not in pe.mover_params.keys():
      raise ValueError('unknown mover type: %s' % mover)
    self.mover = mover
    self.mover_params = params


class LineFormation(Formation):
  def _calculateSpacing(self):
    self._hspace = (self._info['pixmap_size'][0] / ops.grid_size + 1) \
                  * ops.grid_size
  
  def _layout(self):
    nodes = []
    for x in range(self._count):
      nodes.append(QPointF(x * self._hspace, 0))
    x = QPolygonF(nodes).boundingRect().center().x() \
        + self._info['pixmap_size'][1] / 2
    center = QPointF(x, self._info['pixmap_size'][1] / 2)
    for x in nodes:
      self._nodes.append((x - center).toPoint())
