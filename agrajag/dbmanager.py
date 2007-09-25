#!/usr/bin/python
#coding: utf-8

import os
import pygame
import xml.dom.minidom

'''
This class is responsible for importing game content configuration.
'''

class DBManager:
  content = {}

  def import_db(self, dir):
    '''Imports all files from specified directory and puts contents in static variable C{DBManager.content}'''

    if not dir:
      raise Exception('DBManager error: no drectory specified')
    
    files = os.listdir(dir)
    for f in files:
      ff = os.path.join(dir, f)
      if os.path.isfile(ff):
        DBManager.content[f.rsplit('.', 1)[0]] = self.import_file(ff)

  def import_file(self, filepath):
    '''Imports contents of a single file and returns them as a dictionary'''

    dom = xml.dom.minidom.parse(filepath)
    dom_gfx = dom.getElementsByTagName('content')[0]. \
                  getElementsByTagName('gfx')[0]. \
                  getElementsByTagName('resource');

    dom_properties = dom.getElementsByTagName('content')[0]. \
                         getElementsByTagName('properties')[0]. \
                         getElementsByTagName('prop');

    gfx = {}
    for dom_resource in dom_gfx:
      name = dom_resource.getAttribute('name')

      gfx[name] = {}
      gfx[name]['file'] = dom_resource.getAttribute('file')
      gfx[name]['state_w'] = (int)(dom_resource.getAttribute('state_w'))
      gfx[name]['state_h'] = (int)(dom_resource.getAttribute('state_h'))
      gfx[name]['states'] = {}

      dom_states = dom_resource.getElementsByTagName('state')
      for dom_state in dom_states:
        state_name = dom_state.getAttribute('name')
        
        off = { 'x_off' : (int)(dom_state.getAttribute('x_off')), 'y_off' : (int)(dom_state.getAttribute('y_off')) }
        
        gfx[name]['states'][state_name] = off


    props = {}
    for p in dom_properties:
      name = p.getAttribute('name')
      type = p.getAttribute('type')

      props[name] = p.getAttribute('value')

      if (type and type == 'int'):
        props[name] = (int)(props[name])
    
    return { 'gfx' : gfx, 'props' : props }

  def get(self, class_name = None):
    '''Returns config for a specific class or for all classes if no classname is given'''

    return DBManager.content[class_name] if class_name else DBManager.content
    
