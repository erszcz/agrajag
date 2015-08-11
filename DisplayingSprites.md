## Displaying sprites ##

Each class which represents objects shown in the game window **must** be derived from `AGSprite` or its child. This allows every instance to use graphic resources prepared automatically according to an XML configuration file.

Game object may be drawn using zero or more resources. Each resource may contain one or more distinct states in one bitmap (states must be defined in XML config). Sizes of bitmap fragments representing every state are equal.

Image representing game object does not need to be the same size as bitmap fragment representing particular fragment of particular resource. Rectangle used in collision detection does not need to be the same size as image representing game object.

`GfxManager` provides instance of a class representing game object with the following information:
  * named references to graphics resources
  * sizes of state fragments for each resource
  * horizontal and vertical offsets for each state of each resource
  * transparent pixel colorkey

## Positioning object image and collision rectangle ##