#!/usr/bin/python
#coding: utf-8

"""
This module contains base definitions needed by different modules.
"""

from dbmanager import DBManager


class AGObject:
  """
  Base class for all game objects.
  """

  def __init__(self):
    """
    """

    pass

  def _setattrs(self, params, values):
    """
    Setup instance attributes. 
    
    This is an auxiliary method that will set value of instance attribute if its
    name exists in C{params} and C{values} (as a key). All attributes
    whose names exist in C{params} should have default values. If there is
    no default value for attribute which does not have value defined in
    C{values} an exception is raised.

    @type  params: string, list or tuple
    @param params: Names of allowed parameters - if string, names should be 
    comma-separated

    @type  values: dict
    @param values: Dictionary containing instance attribute values
    """

    if type(params) not in (str, list, tuple):
      raise TypeError("attribute 'params' must be a string, a list or a tuple")

    if type(values) is not dict:
      raise TypeError("attribute 'values' must be a dict")

    if type(params) is str:
      params = params.split(',')
      params = map(lambda s: s.strip(), params)

    for name in params:
      if name in values.keys():
        setattr(self, name, values[name])
      elif not hasattr(self, name): 
        v = "%s.%s does not have any value defined" % \
            (self.__class__.__name__, name)
        raise ValueError(v)

