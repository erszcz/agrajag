# Introduction #

The game is divided into several stages. Each stage has its own scenario which details when and where player encounters her enemies (and possibly bonuses). Each stage definition is contained in a separate file. Those files must follow specific syntax described below.

# Stage definition syntax #

Example:

```
<events>
  <spawn
    time='0'
    x='50'
    y='50'
    object_cls_name=''
    object_base_cls_name='Enemy'
    mover_cls_name='LinearPlayerTargetingMover'
    bonus_cls_name='RechargeBonus'>
      <mover_param name='vertical_div' value='0.3' type='float' />
      <bonus_param name='power' value='10' type='int' />
      <group name='enemies' />
  </spawn>
</events>
```

All events are included in the main `<events>` node. At this moment there is only one type of event node - the `<spawn>` node.

The `<spawn>` node has the following obligatory attributes:

  * `time` - spawn time in miliseconds
  * `x` - horizontal position of spawned object (exact meaning of this value depends on the  object that is spawned)
  * `y` - vertical position of spawned object (see above)
  * `object_cls_name` - name of the class to instantiate

The `<spawn>` node has the following optional attributes:
  * `object_base_cls_name` - name of 'base' class which determines what arguments will be passed to object constructor by object spawner - those arguments must be defined in `<object_param>` nodes (see below)
    * `Projectile`
      * `dir` - approximate direction (in radians) in which the projectile is shoot (this should be used but in some cases may be ignored by projectile's mover)
      * `collision_group` - name of the group containing objects that projectile collides with
    * `Bonus` - params depend on bonus class
    * no attribute - no params are or required and none will be used if provided
    * other value - error will be raised
  * `mover_cls_name` - if set spawner will try to set object's mover after creating the object itself, mover may be parametrised with `<mover_param>` nodes (see below)
  * `bonus_cls_name` - if set spawner will try to set bonus held by the object, this bonus may be parametrised with `<bonus_param>` nodes (see below)

Following nodes may be contained by the `<spawn>` node:

  * `group` - name of the group to add created object to
  * `object_param` - used in conjunction with `object_base_cls_name` attribute
  * `mover_param` - used in conjunction with `mover_cls_name` attribute
  * `bonus_param` - used in conjunction with `bonus_cls_name` attribute

Multiple nodes of each type may be used.


Note that it is easily possible to create stage definition that despite of being syntactically correct will cause spawner to crash. This for example may happen when:

  * trying to set mover for object which has fixed mover
  * trying to set bonus for object which is not instance of `BonusHolder`'s subclass