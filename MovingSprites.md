# Introduction #

Most of game objects including player's ship have the ability to move in space. Some objects have constant velocity (speed and direction) but most of them do not (especially enemy ships). There are several ways to determine position of the object in subsequent moments including using parametrised curves or dynamics simulation.

Agrajag uses standard pygame coordinate system with origin in top left corner of the viewport.

# Object properties #

Each game object that has to be drawn on the screen is derived from `pygame.Sprite` (indirectly; directly they are derived from `AGSprite` implementing a number of useful features) meaning that it needs at lest two attributes in order to be drawn, i.e.:

```
  .rect
  .image
```

pygame.Rect contains information on position of an object's top left corner and its linear dimensions. In most cases using position of the object's top left corner as object's position is not appropriate and position of object's center would be more suitable.

To allow that, two additional properties are defined:

```
  .pos
  .align
```

`pos` is a tuple or a list containing current position of arbitrary object's point (i.e. center of explosion).
`align` is a name or a tuple of names of properties that may be used to position `pygame.Rect` (i.e. 'center' or ('centerx', 'top'))

```
  .max_speed
```


Using single rectangular area for collision detection is not sufficient for more complex shapes and some objects may need to be represented by multiple rectangles.

# Movement of player's ship #

In case of player's ship, direction is determined by keys pressed. Ship movement does not occur when no keys are pressed.

_**... zdecydowac czy ruchy statku maja sie odbywac w ten sam sposob, co pozostalych obiektow (w praktyce: metody fly\_xxx ustalalyby kierunek, a update\_position() robilo swoje) czy tak jak jest teraz ...**_

# Complex movement #

Objects of different kinds and different objects of the same type (i.e. enemy ships of particular type) must have the ability to move in different ways.

This is achieved by assigning movement controllers to game objects. Controller may be assigned in the moment of creation of an object or after that moment. Different types of controllers produce different object movements (i.e. zig-zaging or going round in circles). Instances of controller of particular type may be parametrised so that moves produced by each instance varies (i.e. small or big radius).


# Implementation #

```
class AGSprite
```

```
  max_speed
```

Maximal linear speed in pixels per iteration (class attribute)

```
  rect
```

`pygame.Rect` containing information on object's position and area used to detect collisions

```
  mover
```

Reference to movement controller (which may be not set)

```
  update_position()
```

Updates object's position (only if object has movement controller).

```
class Mover
```

Base class for all movement controllers.

```
class LinearMover
```

```
class RandomMover
```

```
class CircularMover
```

```
class ZigZagMover
```