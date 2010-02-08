#!/usr/bin/python
#coding: utf-8

'''Management and conversion to on-screen colour pallette of graphics.
'''

import os
import pygame

class GfxManager:
  content = {}

  def import_gfx(self, conf, gfx_dir):
    if not gfx_dir:
      raise Exception('GfxManager error: no graphics drectory specified')
  
    for class_name in conf:
      GfxManager.content[class_name] = {}

      gfx = conf[class_name]['gfx']
      for res in gfx:
        f = os.path.join(gfx_dir, gfx[res]['file'])

        size = gfx[res]['state_w'], gfx[res]['state_h']
        GfxManager.content[class_name][res] = {
            'image' : pygame.image.load(f).convert_alpha(),
            'states' : gfx[res]['states'],
            'w' : size[0],
            'h' : size[1],
            'size' : size 
          }

  def get(self, class_name = None):
    '''Returns gfx for a specific class or for all classes if no classname is given'''

    return GfxManager.content[class_name] if class_name else GfxManager.content
