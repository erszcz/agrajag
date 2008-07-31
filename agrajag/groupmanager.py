#!/usr/bin/python
#coding: utf-8

'''Management of sprite groups.
'''

import os
import pygame

class GroupManager:
  content = {}

  def add(self, name, cls_name = 'Group'):
    """
    Create new C{pygame.sprite.Group} and store reference pointing to it.
    Return that reference.
    
    @type  name: string
    @param name: Name of the group to be created.
    """

    cls = eval('pygame.sprite.' + cls_name)

    GroupManager.content[name] = cls()
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
  
  @classmethod
  def reset(cls):
    '''Delete all groups and their content.
    '''
    cls.content = {}

  def __getitem__(self, x):
    return self.get(x)
