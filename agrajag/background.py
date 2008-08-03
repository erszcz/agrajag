#!/usr/bin/python
#coding: utf-8

'''Plain and simple space-style background.
'''

import random
import pygame

from clock import Clock
import application
app = application.app

class BackgroundObject(pygame.sprite.Sprite):
  def __init__(self, pos, speed, *groups):
    pygame.sprite.Sprite.__init__(self, *groups)
    self.rect = pygame.Rect(pos, (0, 0))
    self.speed = speed
    self.clock = Clock()

  def update(self):
    delta_y = round(self.clock.frame_span() * self.speed / 1000)
    self.rect.move_ip(0, delta_y)
    if self.rect.top >= app.screen_height:
      self.kill()
      del self

  def left(self):   return self.rect.left
  def right(self):  return self.rect.right
  def top(self):    return self.rect.top
  def bottom(self): return self.rect.bottom

# temp
class BackgroundImage(BackgroundObject):
  def __init__(self, speed, *groups):
    BackgroundObject.__init__(self, (0, 0), speed, *groups)

    self.image = pygame.image.load('gfx/terrain/example_editor.png').convert_alpha()
    self.rect = pygame.Rect((0, app.screen_height - self.image.get_height()),
                            (0, 0))
    self.clock = Clock()

  def update(self):
    delta_y = round(self.clock.frame_span() * self.speed / 1000)
    self.rect.move_ip(0, delta_y)
# end of temp

class DistantStar(BackgroundObject):
  def __init__(self, pos, *groups):
    BackgroundObject.__init__(self, pos, 80, *groups)

    self.image = pygame.Surface((1, 1))
    self.image.fill((255, 255, 255))
    self.rect = pygame.Rect(pos, (1, 1))

class CloserStar(BackgroundObject):
  def __init__(self, pos, *groups):
    BackgroundObject.__init__(self, pos, 120, *groups)

    self.image = pygame.Surface((3, 3))
    self.image.set_colorkey((0, 0, 0))
    self.image.fill((0, 0, 0))
    self.image.set_at((1, 1), (255, 255, 255))
    color = random.randint(0,2)
    if   color == 0: color = 255, 0, 0
    elif color == 1: color = 0, 200, 0
    elif color == 2: color = 50, 50, 255
    else: print 'CloserStar object init error - color undefined for', color
    for pixel in (1, 0), (0, 1), (1, 2), (2, 1):
      self.image.set_at(pixel, color)
    self.rect = pygame.Rect(pos, (3, 3))

class CloserStarCluster(BackgroundObject):
  '''Cluster of small random number of CloserStar instances positioned randomly each close to one another'''

  def __init__(self, pos, *groups):
    BackgroundObject.__init__(self, pos, 160, *groups)

    count = random.randint(2, 5)
    size = 75

    self.rect = pygame.Rect(pos, (size, size))
    self.image = pygame.Surface((size, size))

    self.image.set_colorkey((0, 0, 0))
    self.image.fill((0, 0, 0))

    for i in range(1, count):
      x = random.randint(1, size - 2)
      y = random.randint(1, size - 2)

      self.image.set_at((1 + x, 1 + y), (255, 255, 255))

      r = random.randint(32, 196);
      b = random.randint(0, 196 - r);
      g = random.randint(0, 196 - r - b);

      for pixel in (1 + x, 0 + y), (0 + x, 1 + y), (1 + x, 2 + y), (2 + x, 1 + y):
        self.image.set_at(pixel, (r, g, b))

class SpaceBackground():
  def __init__(self):
    self.dims = app.screen_size
    self.distant_count = 20
    self.closer_count = 16
    self.closer_cluster_count = 3

    self.distant_stars_init()
    self.closer_stars_init()
    self.closer_star_clusters_init()

  def distant_stars_init(self):
    self.distant_stars = pygame.sprite.Group()
    for star in range(self.distant_count):
      x, y = random.randint(0, self.dims[0]),\
             random.randint(0, self.dims[1])
      self.distant_stars.add(DistantStar((x, y)))

  def distant_stars_update(self):
    self.distant_stars.update()

    if self.distant_stars.sprites().__len__() < self.distant_count:
      x, y = random.randint(0, self.dims[0]), 0
      self.distant_stars.add(DistantStar((x,y)))

  def closer_stars_init(self):
    self.closer_stars = pygame.sprite.Group()
    for star in range(self.closer_count):
      x, y = random.randint(0, self.dims[0]),\
             random.randint(0, self.dims[1])
      self.closer_stars.add(CloserStar((x, y)))

  def closer_stars_update(self):
    self.closer_stars.update()

    if self.closer_stars.sprites().__len__() < self.closer_count:
        x, y = random.randint(0, self.dims[0]), 0
        self.closer_stars.add(CloserStar((x,y)))

  def closer_star_clusters_init(self):
    self.closer_star_clusters = pygame.sprite.Group()
    for cluster in range(self.closer_cluster_count):
      x, y = random.randint(0, self.dims[0]),\
             random.randint(0, self.dims[1])
      self.closer_star_clusters.add(CloserStarCluster((x, y)))

  def closer_star_clusters_update(self):
    self.closer_star_clusters.update()

    if self.closer_star_clusters.sprites().__len__() < self.closer_cluster_count:
      x, y = random.randint(0, self.dims[0]), 0
      self.closer_star_clusters.add(CloserStarCluster((x,y)))

  def clear(self, surface, callback):
    self.distant_stars.clear(surface, callback)
    self.closer_stars.clear(surface, callback)
    self.closer_star_clusters.clear(surface, callback)

  def update(self):
    self.distant_stars_update()
    self.closer_stars_update()
    self.closer_star_clusters_update()

  def draw(self, surface):
    self.distant_stars.draw(surface)
    self.closer_stars.draw(surface)
    self.closer_star_clusters.draw(surface)


class TiledBackground(object):
  '''Provides a scrolling background composed of tiles, which can be
     dynamically created or loaded. Tiles are created just before displaying
     and salvaged when they float out of view.
  '''

  # public
  def __init__(self):
    pass

  def clear(self, surface, callback):
    pass

  def update(self):
    pass

  def draw(self, surface):
    pass

  # private
