#!/usr/bin/python
#coding: utf-8

import pygame
from gfxmanager import GfxManager

"""This module supplies a number of widgets used to form the GUI."""

class Widget(pygame.sprite.Sprite):
  """A base widget object to be inherited from."""

  def __init__(self, pos, *groups):
    pygame.sprite.Sprite.__init__(self, *groups)

    self.pos = pos

  #  self.__focus = False

  #def get_focus(self): return self.__focus
  #def set_focus(self, val): self.__focus = val
  #focus = property(get_focus, set_focus)

class VerticalProgressBar(Widget):
  """
  Vertical progress bar or indicator available in 8 colours.

  @type val: integer
  @ivar val: Property; takes values from C{minimum} to C{maximum}.
      Indicates how much of the bar should be lit.

  @type min: integer
  @ivar min: The minimum value the bar can display. Setting a value
      lower than C{min} will cause an exception to be raised.

  @type max: integer
  @ivar max: The maximum value the bar can display. Setting a value
      higher than C{max} will cause an exception to be raised.

  @type color: string
  @ivar color: Property; allowed values are: 'green', 'cyan', 'blue',
      'magenta', 'red', 'yellow', 'black', 'white'.

  @type length: unsigned integer
  @ivar length: The height of the widget.
  """
  
  def __init__(self, min, max, pos, length, *groups):
    Widget.__init__(self, pos, *groups)
    
    self.gfx = GfxManager().get('StripVertical')

    self.min = min
    self.max = max

    self.__val = 0
    self.__color = 'yellow'

    self.length = length
    self.update()  # initializes self.image and self.rect needed for drawing

  def get_val(self): return self.__val
  def set_val(self, val):
    if val > self.max or val < self.min:
      raise Exception('Value outside range. Supply value between %d and %d.'
                       % (self.min, self.max) )
    else:
      self.__val = val
      self.update()
  val = property(get_val, set_val)

  def get_color(self): return self.__color
  def set_color(self, color):
    colors = 'green', 'cyan', 'blue', 'magenta', \
             'red', 'yellow', 'black', 'white'
    if color not in colors:
      raise Exception('Unsupported color. Choose between: ' + 
                      ', '.join(colors))
    else:
      self.__color = color
  color = property(get_color, set_color)

  def get_strip_img(self):
    """Return an image of a single 'light strip' (i.e. state)."""
    img = pygame.Surface((self.gfx['strip']['w'],
                          self.gfx['strip']['h']),
                         pygame.SRCALPHA,
                         self.gfx['strip']['image'])
    area = self.gfx['strip']['states'][self.__color]['x_off'], \
           self.gfx['strip']['states'][self.__color]['y_off'], \
           self.gfx['strip']['w'], \
           self.gfx['strip']['h']
    img.blit(self.gfx['strip']['image'], (0, 0), area)
    return img

  def update(self):
    """Update the C{image} and C{rect} of the widget."""
    # sprowadzenie wartosci do przedzialu <0, 100>:
    # self.__val * 100. / abs(self.max - self.min)
    tmp_val = round( self.__val * 100. / abs(self.max - self.min) )

    # image
    self.image = pygame.Surface((self.gfx['strip']['w'], self.length),
                                pygame.SRCALPHA,
                                self.gfx['strip']['image'])
    strip_img = self.get_strip_img().convert_alpha(self.image)
    for strip in range(self.length * tmp_val / 400):
      self.image.blit(strip_img, (0, self.length - strip * 4))
    # rect
    self.rect = pygame.Rect(self.pos, (self.gfx['strip']['w'], self.length))
