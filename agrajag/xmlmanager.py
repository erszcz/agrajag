#!/usr/bin/python
#coding: utf-8

'''Backend for XML processing managers.
'''

import os
import pygame
import xml.dom.minidom


class XMLManager:
  """
  This class is intended to be base class for other classes that do XML
  processing. This class provides some quite specialized DOM access methods.
  """

  def get_props(self, node, prop_name):
    """
    Return dictionary containing values of C{prop_name} "prop-nodes" 
    contained in C{node}. Prop-node is a node that has a 'name', 'value' and
    optionally 'type' attributes. If type is present value is converted
    accordingly, otherwise it is returned as a string.

    If there are no prop-nodes in C{node} empty dictionary is returned.
    """

    props = {}
    dom_props = node.getElementsByTagName(prop_name)
    for p in dom_props:
      name = p.getAttribute('name')
      type = p.getAttribute('type')

      props[name] = p.getAttribute('value')

      if (type):
        if type == 'int':
          props[name] = int(props[name])
        elif type == 'float':
          props[name] = float(props[name])
        elif type == 'bool':
          props[name] = bool(int(props[name]))
        elif type == 'tuple':
          props[name] = map(lambda x: x.strip(), props[name].split(','))

    return props
    
