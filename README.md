# hexarena

Game-agnostic hex-grid primitives shared across hex-based wargames
([orge](../orge) — Steve Jackson's *Ogre*; [melee](../melee) — *The Fantasy
Trip: Melee*). It carries **no game rules** — no terrain, units, facing, or
scenarios — only the math those games build on, so each game stays the single
source of truth for its own rules while the geometry/dice/pathfinding code lives
in exactly one place.

## What's in it

| Module | Responsibility |
|---|---|
| `hexarena.hex` | `Hex(col, row)` value type and `HexLayout` — offset↔cube conversion, `distance`, `neighbors`, `neighbor`, `direction_to`, `line` (line-of-sight). Supports flat-top and pointy-top, odd/even offset. |
| `hexarena.dice` | `Dice` — injectable d6 source; scripted queue for deterministic tests, seeded random fallback. `roll`, `roll_n`, `total`, `feed`. |
| `hexarena.pathfinding` | `reachable()` — generic Dijkstra with caller-supplied `neighbors_fn`, `cost_fn`, `must_stop_fn`, and `blocked` set. Returns `Reach` (cost + path reconstruction). |
| `hexarena.layout` | Pixel geometry for SVG/Canvas rendering — `hex_center`, `hex_corners`, `layout`. Flat and pointy orientations. |

## Why it exists

Ogre and Melee are both hex games but share almost nothing at the rules level
(Ogre resolves combat on an odds-based CRT; Melee rolls 3d6 under adjusted DX).
What they *do* share is the substrate: hex coordinate math, an injectable dice
source for deterministic tests, terrain-aware reachability, and the trig that
turns a hex into screen pixels. That substrate is here, once.

## Install (local, editable)

```bash
pip install -e .          # from this directory
# or, from a consumer project:
pip install -e ../hexarena
```

## Test

```bash
pytest
```
