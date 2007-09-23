#!/usr/bin/python
#coding: utf-8

import os
import pygame
import xml.dom.minidom


class DBManager(dict):
  def __init__(self, dir):
    if not dir:
      raise Exception('DBManager error: no drectory specified')

    files = os.listdir(dir)
    for f in files:
      ff = os.path.join(dir, f)
      self[f.rsplit('.', 1)[0]] = self.import_file(ff)

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
    for resource in dom_gfx:
      name = resource.getAttribute('name')

      gfx[name] = {}
      gfx[name]['file'] = resource.getAttribute('file')

    props = {}
    for p in dom_properties:
      name = p.getAttribute('name')
      props[name] = p.getAttribute('value')
    
    return { 'gfx' : gfx, 'props' : props }

    
