#!/usr/bin/env python
#coding: utf-8

import sys
import pygame

import logging
log = logging.getLogger('EventManager')

class EventManager(object):
  def __init__(self):
    super(EventManager, self).__init__()
    self.event_handlers = {}
    pygame.event.set_allowed(None)

  def register(self, event_type, handler):
    if event_type in self.event_handlers.keys():
      self.event_handlers[event_type].append(handler)
    else:
      self.event_handlers[event_type] = [handler]
      pygame.event.set_allowed(event_type)

  def unregister(self, event_type, handler):
    try:
      self.event_handlers[event_type].remove(handler)
      handler_count = len(self.event_handlers[event_type])
      log.debug("unregistered handler %s for event type %s" \
            % (handler, pygame.event.event_name(event_type)))
      if handler_count == 0:
        log.debug("event %s blocked" % pygame.event.event_name(event_type))
        pygame.event.set_blocked(event_type)
    except ValueError, e:
      log.debug("Can't unregister %s for event type %s - not registered" \
            % (str(handler), str(event_type)))

  def process(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT: sys.exit()
      if event.type == pygame.KEYDOWN and event.key == pygame.K_q: sys.exit()
      if event.type in self.event_handlers.keys():
        for handler in self.event_handlers[event.type]:
          handler.handle(event)

#interface
#class EventHandler(object):
#  def handle(self, event):
#    pass
