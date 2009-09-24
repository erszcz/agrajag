#!/usr/bin/env python
#coding: utf-8

class Singleton(object):
  _instance = None

  @classmethod
  def singleton(cls, *args):
    if not cls._instance:
      cls._instance = cls(*args)
    return cls._instance

  def __init__(self, *args):
    if self.__class__._instance:
      raise Exception('singleton instance exists')
    self.__class__._instance = self


if __name__ == '__main__':
  class A(Singleton):
    def __init__(self):
      super(A, self).__init__()
      self.asd = 'qwe'
  
  class B(A):
    pass

  b = B.singleton()
  print b.asd
