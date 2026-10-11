# How `//pub/std/fastener/nail` classifies nails

The words its parameters are written in, the standards they come from, and the rules EN 1995-1-1 makes of them.
The sizes are in [CATALOGUE_imperial.md](CATALOGUE_imperial.md) and [CATALOGUE_metric.md](CATALOGUE_metric.md).

## The classification

| | ASTM F1667, F547, C514 | EN 14592, EN 1995-1-1, EN 10230-1 | Parameter |
|---|---|---|---|
| What | Type I, nails (`NL`) | dowel-type fastener: nail | - |
| Style | Table 1's style identifier | EN 10230-1's head forms; DIN 1151's forms A and B | the part's family |
| Shank | smooth, or mechanically deformed: annular (ring), helical (twisted square wire) | smooth, or "other than smooth" (profiled) | `shank`: `smooth`, `ring`, `screw` |
| Head | flat, flat countersunk, countersunk cupped, brad | head diameter for each wire (EN 10230-1), assumed at least 2d for panels (EN 1995-1-1 8.3.1.3) | `head`: `flat`, `countersunk`, `casing`, `brad`; `head_d` |
| Point | diamond, long diamond, needle, blunt, chisel | - | `point` |
| Finish | bright, cement coated, blued, phosphate, zinc - electro, mechanical (B695 Class 40), hot-dip (A153 Class D for exterior use) | Table 4.1: service class to minimum zinc | `coating` |
| Material | low, medium-low or medium carbon steel; stainless 302, 304, 305 or 316; copper (98 % min.); copper-clad steel; aluminium 2024, 5056 or 6061; brass | carbon or stainless steel | `material` |
| Length | under the head if it is flat, overall otherwise | l | `length`, `measured` |
| Diameter | D, ±0.004 in. from 0.076 in. up | d | `d` |

ASTM F547 is the terminology F1667 defers to; the words in the table are
those of F1667 and of FF-N-105B, the federal specification it replaced.
ASTM C514 is the specification gypsum board is nailed with; the imperial
sizes for it are the gypsum wallboard styles of F1667 (`GWS`, `GWM`).

The rules EN 1995-1-1 makes of that classification, for nails in softwood:

* A nail carries load sideways only with a pointside penetration of at
  least **8d** if it is smooth and **6d** otherwise (8.3.1).
* A nail carries load along its axis only with a pointside penetration of
  at least **12d** if smooth and **8d** otherwise; a smooth nail not for a
  permanent or long-term load, and no nail in end grain (8.3.2).
* The timber is drilled first where its density is above 500 kg/m3 or the
  nail is more than **6 mm** across (8.3.1) - which is why the examples'
  targets are 6 mm wide.

EN 14592 does not list sizes: a manufacturer declares them, along with the
wire's tensile strength, the yield moment, and the withdrawal and head
pull-through parameters. The metric `nail` part is that declaration's
geometry, and the rest is the manufacturer's to state.

## Sources

* ASTM F1667-05, *Standard Specification for Driven Fasteners: Nails,
  Spikes, and Staples*: Table 1 (classification and identification), 4.1
  (part numbers), 6 (materials), 8 (dimensions and tolerances), 10
  (coatings).
* US Federal Specification FF-N-105B, *Nails, Brads, Staples and Spikes:
  Wire, Cut and Wrought* (1971), which F1667 replaced: every imperial
  dimension.
* MiTek, *Nails* product table: the connector nails.
* EN 10230-1, Table 1, as reproduced by globalfastener.com: the metric
  heads. Friedrich Trurnit GmbH, *Drahtstifte DIN 1151*: the metric sizes.
* EN 1995-1-1 (Eurocode 5) Table 4.1 and 8.3, and EN 14592, as reproduced
  by COFORD's *Wood Technology Ireland No. 12: Fasteners - Corrosion
  Resistance* and ITW's *Eurocode 5* guide.
