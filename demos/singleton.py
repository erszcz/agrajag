#!/usr/bin/env python
#coding: utf-8

class Singleton(object):
  __instance = None

  @classmethod
  def singleton(cls):
    if not cls.__instance:
      cls.__instance = cls()
    return cls.__instance

  def __init__(self):
    if self.__class__.__instance:
      raise Exception('singleton instance exists')

class SingletonSubclass(Singleton):
  pass

if __name__ == '__main__':
  s = SingletonSubclass.singleton()
