#!/usr/bin/python
#coding: utf-8

import pygame

class Clock(object):
  """
  This class grants objects information about the flow of time.
  It is mainly used to globally access the length of the last frame.
  It is a wrapper for C{pygame.time.Clock}.

  @type __frame_span: unsigned integer
  @cvar __frame_span: Length of the last game frame in miliseconds.

  @type __total_time: unsigned integer
  @cvar __total_time: Total time elapsed since game start in miliseconds.

  @type readonly: boolean
  @ivar readonly: Determines whether the instance may actually
      alter the game clock. Defaults to True.
  """

  __frame_span = 0
  __total_time = 0
  __clock = pygame.time.Clock()

  def __init__(self, readonly=True):
    """
    @type  readonly: boolean
    @param readonly: Determines whether the instance may actually
        alter the game clock. Defaults to True.
    """
    self.readonly = readonly

  def tick(self, fps = 0):
    """
    Tick the game clock (if instance type allows it).

    @type  fps: unsigned integer
    @param fps: Describes the number to which the framerate is capped.
    """
    if self.readonly:
      raise Exception('Instance not allowed to alter the game clock.')
    else:
      Clock.__frame_span = Clock.__clock.tick(fps)
      Clock.__total_time += Clock.__frame_span

      return Clock.__frame_span

  @staticmethod
  def get_rawtime():
    return Clock.__clock.get_rawtime()

  @staticmethod
  def frame_span():
    return Clock.__frame_span

  @staticmethod
  def get_fps():
    return Clock.__clock.get_fps()
