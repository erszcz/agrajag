#!/usr/bin/python
#coding: utf-8

import random
import pygame

from clock import Clock

class BackgroundObject(pygame.sprite.Sprite):
  def __init__(self, pos, speed, boundary, *groups):
    pygame.sprite.Sprite.__init__(self, *groups)
    self.rect = pygame.Rect(pos, (0, 0))
    self.speed = speed
    self.boundary = boundary	# wysokosc vieportu w pikselach
    self.clock = Clock()

  def update(self):
    delta_y = round(self.clock.frame_span() * self.speed / 1000)
    self.rect.move_ip(0, delta_y)
    if self.rect.top >= self.boundary:
      self.kill()
      del self

  def left(self):   return self.rect.left
  def right(self):  return self.rect.right
  def top(self):    return self.rect.top
  def bottom(self): return self.rect.bottom

# temp
class BackgroundImage(BackgroundObject):
  def __init__(self, speed, boundary, *groups):
    BackgroundObject.__init__(self, (0, 0), speed, boundary, *groups)

    self.image = pygame.image.load('gfx/terrain/level_template.png').convert_alpha()
    #self.rect = pygame.Rect((0, self.image.get_height() - self.boundary), (0, 0))
    self.rect = pygame.Rect((0, self.boundary - self.image.get_height()), (0, 0))
    self.clock = Clock()

  def update(self):
    delta_y = round(self.clock.frame_span() * self.speed / 1000)
    self.rect.move_ip(0, delta_y)
# end of temp

class DistantStar(BackgroundObject):
  def __init__(self, pos, boundary, *groups):
    BackgroundObject.__init__(self, pos, 80, boundary, *groups)

    self.image = pygame.Surface((1, 1))
    self.image.fill((255, 255, 255))
    self.rect = pygame.Rect(pos, (1, 1))

class CloserStar(BackgroundObject):
  def __init__(self, pos, boundary, *groups):
    BackgroundObject.__init__(self, pos, 120, boundary, *groups)

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
  '''Cluster of small random numer of CloserStar instances positioned randomly each close to one another'''

  def __init__(self, pos, boundary, *groups):
    BackgroundObject.__init__(self, pos, 160, boundary, *groups)

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
  def __init__(self, screen_dims):
    self.dims = screen_dims
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
      self.distant_stars.add(DistantStar((x, y), self.dims[1]))

  def distant_stars_update(self):
    self.distant_stars.update()

    if self.distant_stars.sprites().__len__() < self.distant_count:
      x, y = random.randint(0, self.dims[0]), 0
      self.distant_stars.add(DistantStar((x,y), self.dims[1]))

  def closer_stars_init(self):
    self.closer_stars = pygame.sprite.Group()
    for star in range(self.closer_count):
      x, y = random.randint(0, self.dims[0]),\
             random.randint(0, self.dims[1])
      self.closer_stars.add(CloserStar((x, y), self.dims[1]))

  def closer_stars_update(self):
    self.closer_stars.update()

    if self.closer_stars.sprites().__len__() < self.closer_count:
        x, y = random.randint(0, self.dims[0]), 0
        self.closer_stars.add(CloserStar((x,y), self.dims[1]))

  def closer_star_clusters_init(self):
    self.closer_star_clusters = pygame.sprite.Group()
    for cluster in range(self.closer_cluster_count):
      x, y = random.randint(0, self.dims[0]),\
             random.randint(0, self.dims[1])
      self.closer_star_clusters.add(CloserStarCluster((x, y), self.dims[1]))

  def closer_star_clusters_update(self):
    self.closer_star_clusters.update()

    if self.closer_star_clusters.sprites().__len__() < self.closer_cluster_count:
      x, y = random.randint(0, self.dims[0]), 0
      self.closer_star_clusters.add(CloserStarCluster((x,y), self.dims[1]))

  def update(self):
    self.distant_stars_update()
    self.closer_stars_update()
    self.closer_star_clusters_update()

  def draw(self, surface):
    self.distant_stars.draw(surface)
    self.closer_stars.draw(surface)
    self.closer_star_clusters.draw(surface)
