#!/usr/bin/python
#coding: utf-8

import os
import pygame

class GroupManager:
  content = {}

  def add(self, name):
    """
    Create new C{pygame.sprite.Group} and store reference pointing to it.
    Return that reference.
    
    @type  name: string
    @param name: Name of the group to be created.
    """

    GroupManager.content[name] = pygame.sprite.Group()
    return GroupManager.content[name]

  def get(self, name):
    """
    Return reference to a group or None if group does not exist.
    
    @type  name: string
    @param name: Name of the group to be returned.
    """

    if GroupManager.content.has_key(name):
      return GroupManager.content[name]

    return None
    
