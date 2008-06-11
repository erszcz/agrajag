#!/usr/bin/env python
#coding: utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import xml.etree.ElementTree as ETree
import xml.dom.minidom as minidom

import levelview as lv
import propertyeditor as pe

class XMLWriter:
  '''
  Object writes XML describing stage files.
  It is done by converting their internal editor representation
  to markup and writing it to disk.
  '''

  @classmethod
  def writeEventsFile(cls, filename, scene):
    '''Write down QScene's events to stage file.'''
    try:
      file = open(filename, 'w')
      doc = cls.sceneToXML(scene)
      doc.writexml(file, indent='', addindent='  ', newl='\n')
      file.close()
    except Exception, e:
      print e
      print e.message
      print 'Couldn\'t write %s.' % filename
      return False
    return True

  @staticmethod
  def sceneToXML(scene):
    root = ETree.Element('events')
    for item in scene.items():
      if type(item) == lv.AGBackgroundItem:
        print 'AGBackgroundItem', type(item)
      elif type(item) == lv.AGEventItem:
        attrs = {'x': str(int(item.props['posx'])),
                 'y': str(int(item.props['posy'])),
                 'time': str(item.props['time']),
                 'bonus_cls_name': item.props['bonus_cls_name'],
                 'mover_cls_name': item.props['mover_cls_name']
                }
        if not item.isBonus():
          attrs['object_cls_name'] = item.props['object_cls_name']
        spawnElement = ETree.SubElement(root, 'spawn', attrs)

        mcn = item.props['mover_cls_name']
        bcn = item.props['bonus_cls_name']
        cpSeq = [(mcn, 'mover_param'), (bcn, 'bonus_param')]
          #(1) (class name, param name)-pair sequence
        if not item.isBonus():
          ocn = item.props['object_cls_name']
          cpSeq.append((ocn, 'object_param'))
        for cn, pn in cpSeq:  # jump over sequence from (1)
          # cn - class name, pn - param name
          if getattr(pe, pn + 's').has_key(cn) and getattr(pe, pn + 's')[cn]:
            name = getattr(pe, pn + 's')[cn].keys()[0]
            value = item.props[':'.join((cn, name))]
            t = lambda x: x[7:x.rindex('\'')]  # "<type 'int'>" -> "int"
            param_attrs = {'name': name,
                           'value': str(value),
                           'type': t(str(type(value)))
                          }
            ETree.SubElement(spawnElement, pn, param_attrs)
        ETree.SubElement(spawnElement, 'group', {'name': item.props['group']})
      else:
        print 'XMLWriter error: unknown item type (%s)' % str(type(item))

    doc = minidom.parseString(ETree.tostring(root, 'utf-8'))
    return doc
