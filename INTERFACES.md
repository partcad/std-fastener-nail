# The interfaces of `//pub/std/fastener/nail`

Where a nail goes, which nails go there, which of them go there outdoors, and how a nail is held and struck.
The imperial and the metric nails implement the same ones. The [README](README.md) has the short of it.

## The four ports

<img align=right src="./common/16d.ports.svg" alt="The four ports of a 16d common nail" width="260">

A nail is modelled along Z, point down. `z = 0` is the plane that is flush
with the surface once the nail is driven home: the underside of a flat head,
the top of every other head. Every nail has the same four ports, and, as
everywhere in PartCAD, each one's `+Z` points *into* the nail:

| Port | Interface | Where | `+Z` |
|---|---|---|---|
| `tip` | `nail-point` or `nail-point-outdoor` | the very end of the point, `z = -L` | up the shank |
| `head` | `nail-head` | the middle of the top of the head, drawn at the head's diameter | down the shank |
| `left-grip`, `right-grip` | `nail-grip` | on the shank, on opposite sides | across it, at the axis |

`L` is how far the nail goes in: its length, except for a flat-headed nail
measured overall (a cooler), which loses the thickness of its head.

## Where a nail goes: `nail-target` and `nail-target-outdoor`

A part that a nail is driven into implements a target wherever a nail is
meant to go, with the port on the surface and `+Z` pointing into the
material:

```yaml
implements:
  "//pub/std/fastener/nail:nail-target;width=6,depth=88.9":
    A: [[44.45, 76.2, 88.9], [1, 0, 0], 180]
```

| Parameter | Meaning |
|---|---|
| `width` | The widest nail the place takes, in mm: the diameter of a hole in a metal connector, or the widest nail the wood takes there without being drilled first (6 mm in softwood, under EN 1995-1-1 8.3.1). |
| `depth` | How deep a nail can go, in mm, from the surface: what is behind it before the far side. |
| `drive` | Not set by the target but by the connection: how far the nail has been driven, from its point just touching the surface (0) to `depth`. |

Connecting a nail to a target puts the nail's `tip` on the target's port,
standing ready to be driven - which is where a robot, or a hand, has to put
it. `drive` (in the connection's `toParams`) is how far it then goes in: the
length `L` drives it home.

## The nail's end of it: `nail-point` and `nail-point-outdoor`

A nail implements `nail-point;d=<d>` at its tip, `d` being its shank to the
nearest 0.1 mm - which is finer than ASTM F1667's own tolerance on a shank
of ±0.004 in. That is the whole of what decides where a nail can go, so
every nail of the same wire has the same point, whatever its standard,
style, head or length: an 8d common and a 2.5 in. x 0.131 in. collated
framing nail are the same `nail-point;d=3.3`.

A target of a given `width` takes every point that is not wider. Mating in
PartCAD is by name rather than by range, so this is done by inheritance: a
target that takes 6 mm is a drop-in for the one that takes 5.9 mm, which is
a drop-in for 5.8 mm, and so on down to 0.5 mm. Each of them mates the
point of exactly its own width, so the 6 mm target mates every point from
0.5 to 6 mm through what it inherits, and nothing wider.

A mating is what lets an assembly say only which part a nail goes into and
have PartCAD find the ports.

What tells `pc test` that the nail and the wood are meant to share the space
the nail displaces is the nail itself: its `tip` port says `selfScrew`, because
a nail makes its own hole whatever it is driven into. It is said by the port
rather than by each target's mating so that every connection made through the
point reads it, however the connection was written - one that names the ports
alone (`withPort: tip`, `toPort: A-entry`) looks up no mating at all. The
assembly instruction book has one wording for an end that cuts its own way in,
and puts such a step as "driven in, cutting its own thread".

A mating is not what allows a connection, though. A connection that names the
ports places a nail whether or not its interfaces mate - a bright nail in an
outdoor post included - and since that nail's point makes its own hole too,
`pc test` has no overlap to report about it: check what such a connection
puts where. A connection that names neither the ports nor the interfaces, and
whose two ends have no mating, has nothing to place the nail by: PartCAD warns
that it could not find the peer ports and leaves the nail at the post's origin.

## Outdoor

| Nail implements | `nail-target` (indoor) | `nail-target-outdoor` |
|---|---|---|
| `nail-point` | yes | **no** |
| `nail-point-outdoor` | yes | yes |

An outdoor product needs outdoor nails, and an indoor one takes any nail.
In PartCAD that is two different relations, and each family has the one it
needs:

* `nail-point-outdoor` **inherits** `nail-point`, and so is a drop-in for
  it: everything that takes a generic nail takes an outdoor one.
* `nail-target-outdoor` does **not** inherit `nail-target`. If it did it
  would be a drop-in for it too, and would take whatever `nail-target` takes,
  generic nails included. So the two targets are siblings: both inherit the
  same properties - the port, its outline, the freedom to drive - from the
  abstract `nail-entry`, and each mates only its own kind of point.

A nail is an outdoor nail when it will last outdoors:

* **hot-dip galvanized**: ASTM F1667 (10.1.3) asks for hot-dip galvanizing
  to ASTM A153 Class D "when a heavier coating for exterior use is
  specified", and EN 1995-1-1 takes hot-dip zinc (Z350) in service class 3.
  The `coating` value means the former; or
* made of a metal that needs no coating: stainless steel (`ss-304`,
  `ss-316l`) or copper (`cu-c110`).

Everything else is generic, and that is a deliberately cautious line:

* **Electro-galvanized** says nothing about how much zinc, and EN 1995-1-1
  asks Fe/Zn 25c of a nail outdoors. The parameter cannot tell a nail
  plated that heavily from one plated to Fe/Zn 5.
* **Mechanically galvanized** is in neither standard's exterior clause.
  ASTM F1667 names hot-dip galvanizing for exterior use, and Table 4.1 is
  written for electroplated (ISO 2081) and hot-dip zinc.
* **Aluminium** (`al-6061-t6`, one of the alloys F1667 names) does not rust,
  but EN 14592 covers steel fasteners only, and aluminium is a poor
  neighbour for the copper most wood preservatives are made of.

A finish that does meet service class 3 is one more value of `coating`, and
one more entry in the list in `nail.j2` that makes a nail outdoor. Which of
the two a nail is, is worked out from its `coating` and `material`
parameters, so the same part is either, as asked:

```shell
pc info "//pub/std/fastener/nail/imperial:common/16d"
    # Ports: nail-point;d=4.1
pc info "//pub/std/fastener/nail/imperial:common/16d;coating=hot-dip-galvanized"
    # Ports: nail-point-outdoor;d=4.1
pc info "//pub/std/fastener/nail/metric:flat/3.4x90;material=//pub/std/manufacturing/material/metal:ss-304"
    # Ports: nail-point-outdoor;d=3.4
```

### EN 1995-1-1 Table 4.1: minimum corrosion protection of fasteners

| Fastener | Service class 1 | Service class 2 | Service class 3 |
|---|---|---|---|
| Nails and screws, d ≤ 4 mm | none | Fe/Zn 12c | Fe/Zn 25c |
| Bolts, dowels, nails and screws, d > 4 mm | none | none | Fe/Zn 25c |
| Staples | Fe/Zn 12c | Fe/Zn 12c | stainless steel |

Hot-dip zinc is Z275 for Fe/Zn 12c and Z350 for Fe/Zn 25c; especially
corrosive conditions call for heavier hot-dip coatings or stainless steel.
Service class 1 keeps most softwoods at or below 12 % moisture (a heated
interior), service class 2 at or below 20 % (covered, unheated), and service
class 3 is anything wetter (outdoors). "Outdoor" here is service class 3.
The revised EN 14592 goes further, with categories for the atmosphere
(C1-C5) and for the timber and its treatment (T1-T5); an interface per
category would be inherited the same way `nail-point-outdoor` inherits
`nail-point`.

## Holding: `nail-grip`

A nail is held while it is started by something with two jaws - a parallel
gripper, pliers, a nail holder - that close on its shank from opposite
sides. So the grasp is one interface with two ports: `nail-grip;d=<d>`, `d`
being the shank, with `left-grip` and `right-grip` on its two sides, each
`+Z` pointing at the axis. A tool for it is not a finger but a grip: it
takes both ports at once, and its jaws close to `d`.

The grasp is a quarter of the way down from the head, but never closer to it
than the head is wide (so the hammer's face has room) and never past halfway
(so the point has room).

Every catalogue nail names it as what it is held by - `connect.hold` - so it
is what an assembly's `how.holdWith` defaults to, with the force to hold it
with: 5 N at least, to stand the nail up against the first light taps, and
50 N at most, not to scuff a coating off. `hold` names an interface as it is
written, parameters and all (`nail-grip;d=4.1148` for a 16d common), which a
generated part can do and the metric `nail` part, whose shank is a
parameter, cannot; an assembly holding one names it in `how.holdWith`.

Nothing mates with `nail-grip` yet. A gripper's interface would mate it the
way a target mates a point - by the widest shank its jaws open to.

## Striking: `nail-head`

Where a hammer's face, a nailer's driver or a nail set meets the nail.
`nail-head;d=` is parametrized by the head's diameter, which its port is
drawn at: `head_d`, or twice the shank for a metric `nail` that leaves
`head_d` at 0. A nail names the head it has rather than restating the
outline of a common one, because PartCAD lets only an interface's
`inherits:` restate a boundary, never a part's `implements:`. It mates with
nothing yet either; a driver's interface would mate it the way a target
mates a point.
