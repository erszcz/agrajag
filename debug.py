#!/usr/bin/env python
#coding: utf-8

import os
import sys

NONE      = 0
INFO      = 10
WARNING   = 20
CRITICAL  = 30
verbosity_level = NONE

def info(msg, **kwargs): pass
def warning(msg, **kwargs): pass
def critical(msg, **kwargs): pass

# clear the log
logfile = file(os.sep.join((os.path.dirname(__file__), 'debug.log')), 'w')
logfile.close()

if __debug__:
  def debug(msg, level, **kwargs):
    if verbosity_level and level >= verbosity_level:
      logfile = file(os.sep.join((os.path.dirname(__file__), 'debug.log')), 'a')
      logs = [sys.stdout, logfile]
      for log in logs:
        log.write(msg + "\n")
        log.writelines(("%s: %s\n" % (x, y) for (x, y) in kwargs.iteritems()))
        log.flush()
      logfile.close()

  def info(msg, **kwargs):
    debug('info: ' + msg, 10, **kwargs)
  def warning(msg, **kwargs):
    debug('warning: ' + msg, 20, **kwargs)
  def critical(msg, **kwargs):
    debug('critical: ' + msg, 30, **kwargs)
