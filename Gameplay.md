# Combat #

Combat is the most important part of the game.

Basic assumptions:
  * player ship collides only with enemy projectiles
  * enemy ships collide only with player projectiles

## Player ##

### Defence ###

Player ship as well as enemy ships have two basic types of defensive means - _armour_ and _shield_. This distinction is important because different kinds of weapons may have different impact on shield and different on armour (i.e. particular weapon may be good against shields and weak against armour and vice-versa).

Ship armour value depends on its _hull_ type and installed _equipment_ (see **Gear** below). Ship does not have any shields by default but may have them installed as additional equipment.

Shields fall into two categories:
  * _manual_ - which have to be triggered by the player
  * _automatic_ - which are triggered automatically before a hit occurs but may also be triggered by the player

Shields are characterised by two values:
  * _current energy level_ - amount of damage the shield can absorb at this moment
  * _maximum energy level_ - maximal amount of damage shield can absorb in one hit

Shield energy is used very slowly when the shield is working. Shield energy is also used to deflect projectiles. Amount of energy used depends on projectile type.
When shield is not working its energy is being recharged. Recharge speed depends on the _reactor_ installed (see **Gear** below).

Automatic shield is also characterised by _critical speed_ value - shield is triggered **only** by projectiles moving with speed lesser than this value. No shield is automatically triggered by weapons that hit instantly (but if shield was triggered manually it protects the ship).

Armour is characterised by two similar values:
  * _current armour level_ - amount of damage the armour can absorb at this moment
  * _maximum armour level_ - maximal amount of damage armour can absorb in one hit

When a hit occurs damage is absorbed by the shield in the first place (assuming the shield is working). If the damage is not absorbed completely by the shield, remaining damage has to be absorbed by the armour.

Armour can be repaired during combat if the ship is equipped with _autorepair kit_.

If armour level drops to zero or less the ship is destroyed and the game ends unless the ship is equipped with an _escape pod_.

Ships may possibly be additionally equipped with other types of defensive means beside armour and shield.


### Offence ###

Weapons can be categorized as follows depending on how they shoot:
  * instant weapons which hit instantly
  * projectile weapons which fire projectiles moving with finite speed

Alternatively, they can be categorized depending on what they shoot:
  * energy weapons which consume energy
  * ammo weapons which fire ammo pieces

Only one weapon can be selected at a time.

_**Idea:** allow firing more than one weapon at once (depending on hull type/weapon slots/?)_

Every weapon is characterized by _cooldown_, that is minimal time between shots.

Beam weapons are characterized by three additional parameters:
  * maximal energy
  * current energy
  * energy needed for one shot

Because of that beam weapons are somewhat similar to shields. Energy of beam weapons can also be recharged by the reactor.

Ammo weapons are characterized by two parameters:
  * ammo storage capacity
  * current number of ammo pieces

It is assumed that ammo weapons always fire one piece of ammo even if in reality more than one projectile appears.

Instant ammo weapons are very rare, most of instant weapons are energy weapons.

Every ship is by default equipped with a single projectile energy weapon having low energy requirements. This makes it unlikely that player ship runs completely out of ammo.


### Hulls ###

Ship hull is its most important part. It determines ship's:
  * maximum speed
  * base armour level
  * number of slots for different types of weapons and additional equipment
  * base cargo space which is used to collect certain bonuses

There are several types of hull slots:
  * weapon slots
  * armour slots which allow to increase maximum armour level
  * shield slots
  * reactor slots
  * escape pod slots
  * general purpose slots

At least one reactor slot needs to be filled in order for the ship to run. Reactors provide energy that powers ship hull, shields, energy weapons and certain other equipment.

### Bonuses ###

There are several types of bonuses that can be collected and used immediately during combat.  These bonuses do not consume cargo space. These include:
  * cash
  * energy - restores shield and/or beam weapons energy
  * ammunition of particular type - can be collected only if ship has free storage for it
  * supergear - powerful items that temporarily replace ship's gear

There are also bonuses that can not be used immediately, they have to be installed in a dock. Collecting those requires cargo space. These include:
  * weapons and additional equipment

_**At this time all bonuses can be collected and used immediatelly.**_

_To avoid situation in which player ship is equipped with so many weapons that switching between them is not comfortable, maximal number of weapons is introduced. Picking new weapon when that number is achieved will replace oldest carried weapon. It is level designer's responsibility to place better weapons further in the game._


## Enemies ##

Player comes across several types of enemy units: air units, ground units and naval units.

**This should probably be moved to technical documentation:** Technically there is not much difference between those units. There are no constrains on where ground and naval units could move, they just need to be placed in correct positions. The only difference is that
ground and naval units are rendered below/before air units.


### Defence ###

Enemy ships may be equipped with similiar defensive means that player ship, however there are some differences.

Shields:
  * enemy ship may be equipped with a shield
  * enemy ships should not be equipped with manual shields as those would be useless

Armours:
  * enemy ship may be equipped with an armour

Reactors:
  * enemy ship may be equipped with a reactor

Two ships of the same type may be equipped differently. Enemy ships may possibly use other equipment.


### Offence ###

Enemy ships use the same weapons that player ship uses. Some weapons may be forbidden for enemies or player.

Most enemies move over predefined trajectories and shoot constantly as fast as their weapon allows that. Some enemies try to position themselves in front of the player ship and shoot only if they are close enough.


### Bonuses ###

Enemies do not collect bonuses, but may carry them. If enemy carrying a bonus is destroyed, the bonus appears and may be collected by player ship.


# Stages #



# Gear #

## Hulls ##

## Weapons ##

### Projectile Energy Weapons ###

**Mini Blaster**

  * very small projectile
  * low damage
  * low energy consumption
  * medium cooldown

**Blaster Mk I, II**

  * small projectile
  * medium damage
  * medium energy consumption
  * medium cooldown

**Dual Blaster Mk I, II**

  * medium projectile
  * medium/high damage
  * medium/high energy consumption
  * medium cooldown

**Scatter Blaster**

  * medium scattering projectile
  * medium damage
  * medium energy consumption
  * medium cooldown

**Heavy Scatter Blaster**

  * big scattering projectile
  * high damage
  * high energy consumption
  * medium cooldown

**Wave Blaster**

  * very big projectile
  * very high damage
  * high energy consumption
  * high cooldown


### Instant Energy Weapons ###

Instant energy weapons should have slightly higher energy consumption rates than projectile energy weapons with similiar damage.

**Basic Beamer**

  * narrow beam
  * medium damage
  * medium energy consumption
  * low/medium cooldown

**Rapid Beamer**

  * narrow beam
  * medium damage
  * medium energy consumption
  * very low cooldown

**Multi Beamer**

  * multiple narrow beams fired in different directions
  * high damage
  * high energy consumption
  * medium cooldown

_**At this time drawing slanting beams could be quite troublesome thus this weapon will not be implemented in first release.**_

### Projectile Ammo Weapons ###

**Mini Cannon**

  * very small projectile
  * low damage
  * medium cooldown
  * manual targeting

**Auto Cannon**

  * very small projectile
  * low damage
  * low/medium cooldown
  * auto targeting (wide arc)

**Multi Cannon**

  * multiple small projectile
  * medium damage
  * medium cooldown
  * manual targeting

**Seeker Cannon**

  * small seeking projectile
  * medium damage
  * low/medium cooldown
  * manual targeting

**Heavy Cannon**

  * big scattering projectile
  * very high damage
  * medium/high cooldown
  * manual targeting


### Instant Ammo Weapons ###


## Armour extensions ##

## Shields ##

### Basic Shield ###

  * manual
  * medium energy capacity
  * medium/high energy consumption

### Basic Reflective Shield ###

  * manual
  * medium energy capacity
  * medium/high energy consumption
  * fires low damage projectile when struck

### Medium Shield ###

  * manual
  * medium/high energy capacity
  * low/medium energy consumption

### Medium Reflective Shield ###

  * manual
  * medium/high energy capacity
  * low/medium energy consumption
  * fires medium damage projectile when struck

### Advanced Shield ###

  * auto
  * high energy capacity
  * low energy consumption

### Advanced Reflective Shield ###

  * auto
  * high energy capacity
  * low energy consumption
  * fires small random number of high damage projectiles when struck

## Reactors ##

## Escape pods ##

## Other ##

**Targeting Device**

Produces line of light which helps in targeting especially with beam weapons.


**Armour Repair Kit Mk I, II**

Constantly repairs damaged armour (if equipped) and hull. Needs energy.


### Radars ###

Radars allow player to see parameters of enemy ships. Better radars allow player to see more details.


# Bonuses #

## Recharge bonus ##

Recharges ship's energy weapons, shields and possibly other energy consuming gear.

## Refill bonus ##

Refills ship's ammo weapons with ammo.

_Simplification: at this time it is assumed that all weapons use identical ammo._

## Supershield bonus ##

Replaces current shield by a supershield (which is better than any other shield in the game) for a limited time. After that time or when the shield energy is depleted previously used shield is restored.

## Weapon bonus ##

Equips player ship with a weapon. If ship already carries
maximal allowed number of weapons, oldest weapon is replaced by the one
provided by bonus. It is level designer's responsibility to place better
weapons further in the game.

## Shield bonus ##

Equips player ship with a shield. If ship already carries a shield that shield is replaced. New shield comes with full energy. It is level designer's responsibility to place better shields further in the game.

## Shield upgrade bonus ##

Replaces player ship's shield with a better one. New shield comes with full energy.