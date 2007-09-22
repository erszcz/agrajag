#!/usr/bin/python
#coding: utf-8

import os
import pygame

class GfxManager(dict):
  def __init__(self, gfx_ind_or_dir = None):
    if not gfx_ind_or_dir:
      print 'GfxManager error: no graphics index file or drectory specified'
      return

    if os.path.isdir(gfx_ind_or_dir):
      files = os.listdir(gfx_ind_or_dir)
      for f in files:
        ff = os.path.join(gfx_ind_or_dir, f)
        if os.path.isfile(ff):
          self[f.rsplit('.', 1)[0]] = pygame.image.load(ff).convert_alpha()
    elif os.path.isfile(gfx_ind_or_dir):
      ind = file(gfx_ind_or_dir, 'r')
      for line in ind:
        if not line[0] == '#':
          field, img = line.split()
          self[field] = pygame.image.load(img).convert_alpha()
    else:
      print 'GfxManager unexpected error: unrecognized gfx_ind_or_dir'

