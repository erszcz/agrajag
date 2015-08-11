# Introduction #

Stage editor allows to:
  * create graphics backgrounds from tiles
  * place enemies and other objects and set their individual properties
  * edit global properties of game objects


# Background #


# Enemies #

Editor allows to:
  * set positions in which enemies appear
  * set individual properties of enemies, i.e.:
    * mover type and params
    * bonus carried

_**...time of appearance - may be implied by selected position and background scroll-speed with optional shift in time or set explicitly...**_

## Formations ##

Editor allows to place whole formations of enemy ships at once. Every ship in a formation moves along the same trajectory, however initial positions or times of appearance may be different. Properties of each object belonging to a formation may be edited independently.

# Global object properties #

Editor allows to edit xml files which describe game objects of the same type (classes). Editor allows to add/modify/delete:
  * graphics resources
  * audio resources
  * common/default properties

Structure of those files is described in [XMLClassConfig](XMLClassConfig.md).