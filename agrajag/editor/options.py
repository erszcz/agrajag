#!/usr/bin/env python
#coding: utf-8

import os.path as p

here = p.dirname(__file__)

# some paths
gfx_path = p.join(here, '../gfx')
db_path = p.join(here, '../db')
terrain_path = p.join(here, '../gfx/terrain_new')

# display warnings/errors
info_load_error = False  # info about files which couldn't be loaded

# behavoiur
always_snap = True
grid_size = 10
scene_size = 800, 5000
