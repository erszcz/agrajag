#!/usr/bin/python
#coding: utf-8

import os
import pygame
import xml.dom.minidom

from xmlmanager import XMLManager


class StageManager(XMLManager):
  """
  This class is responsible for importing game stages schedule.
  """

  content = {}

  def import_stages(self, dir):
    """
    Import all files from specified directory and put contents in static
    variable C{StageManager.content}
    """

    if not dir:
      raise Exception('StageManager error: no drectory specified')
    
    files = os.listdir(dir)
    for f in files:
      ff = os.path.join(dir, f)
      if os.path.isfile(ff):
        try:
          stage = self.import_file(ff)
        except xml.parsers.expat.ExpatError:
          print "Error parsing file %s" % ff
          raise 

        StageManager.content[f.rsplit('.', 1)[0]] = stage

  def import_file(self, filepath):
    """
    Import contents of a single file and returns them as a dictionary.
    """

    dom = xml.dom.minidom.parse(filepath)
    dom_events = dom.getElementsByTagName('events')[0].childNodes

    spawn = {}
    for dom_event in dom_events:
      if dom_event.nodeType != xml.dom.minidom.Node.ELEMENT_NODE:
        continue

      if dom_event.nodeName == 'spawn':
        time = int(dom_event.getAttribute('time'))
        s = {
            'time' : time, 
            'x' : int(dom_event.getAttribute('x')), 
            'y' : int(dom_event.getAttribute('y')), 
            'object_cls_name' : dom_event.getAttribute('object_cls_name'),
            'mover_cls_name' : dom_event.getAttribute('mover_cls_name'),
            'bonus_cls_name' : dom_event.getAttribute('bonus_cls_name')
            }

        dom_groups = dom_event.getElementsByTagName('group')

        s['object_params'] = self.get_props(dom_event, 'object_param')
        s['mover_params'] = self.get_props(dom_event, 'mover_param')
        s['bonus_params'] = self.get_props(dom_event, 'bonus_param')

        s['groups'] = {}
        for dom_g in dom_groups:
          s['groups'][dom_g.getAttribute('name')] = True


        if not spawn.has_key(time):
          spawn[time] = []

        spawn[time].append(s)

    return {'spawn' : spawn}

  def get(self):
    """
    Return contents for all stages.
    """

    return StageManager.content
    
