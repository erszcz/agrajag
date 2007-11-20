#coding: utf-8

from math import pi, fabs

def sgn(x):
  """
  Return sgn(x), that is: 1 if x is positive, -1 if x is negative, 0 if
  x is 0.
  """

  try:
    return x / fabs(x)
  except ZeroDivisionError:
    return 0

def deg2rad(deg, normalize = True):
  """
  Convert angle from degrees to radians.

  @type  deg: float
  @param deg: Angle in degrees.

  @type  normalize: bool
  @param normalize: If true translate returned value to [0, 2pi)
  """

  rad = 2 * pi * deg / 360
  return rad if not normalize else normalize_rad(rad)

def rad2deg(rad, normalize = True):
  """
  Convert angle from radians to degrees.

  @type  rad: float
  @param rad: Angle in radians.

  @type  normalize: bool
  @param normalize: If true translate returned value to [0, 360)
  """

  deg = 360 * rad / 2 / pi
  return deg if not normalize else deg % 360

def normalize_rad(rad):
  """
  Return angle in radians translated to [0, 2pi).
  """

  return rad % (2 * pi)
