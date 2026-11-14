<!-- SPDX-License-Identifier: LGPL-2.1-or-later -->
# AddonKit for FreeCAD

> Not affiliated with or endorsed by the FreeCAD project or the FreeCAD project association (FPA); FreeCAD is the FPA's trademark. Get FreeCAD itself from [freecad.org](https://freecad.org).

A small library other FreeCAD add-ons build on, so none of them copies
another. It adds nothing to FreeCAD's window by itself; the Addon Manager
installs it when an add-on that needs it is installed.

| Module | What |
|---|---|
| `addonkit.records` | Notes kept in the document itself (how each part is made, its spec, materials per body, calibrations): saved with the `.FCStd`, and undo takes them back with the change they belong to. |
| `addonkit.geo` | Shape building and reading on FreeCAD's Part module: rounded prisms, ruled lofts, the thinnest wall, thin runs. |
| `addonkit.fits` | Fits (press, slide, free) and hardware holes for made parts, from the ISO sizes. |
| `addonkit.ccx` | CalculiX's input decks and results, plain Python: meshes, loads, buckling, modes, heat, read back. |
| `addonkit.archive` | Zips to hand on (order packages, library packs): deflated, nothing of the computer in them. |
| `addonkit.sheets` | Drawing sheets as plain Python: paper sizes, view layout, title blocks, written as SVG, DXF and PDF. |
| `addonkit.iso286` | ISO 286 limits of size for the common fits (IT5–IT11; F G H JS holes, f g h js k n p shafts; up to 500 mm). |
| `addonkit.techdraw` | TechDraw helpers: a view's lines waited for when there is no window to run Qt's loop. |
| `addonkit.materials` | Printing filaments (density, stiffness, strength, softening): one table every add-on reads. |
| `addonkit.data` | Versioned, schema-checked data files with your own overrides (below). |
| `addonkit.Refused` | A refusal that says what to do instead. |
| `addonkit.ui` | A parameter dialog and the pieces panels share (GUI only). |

## For add-on developers

```python
import addonkit
addonkit.require(">=1.0,<2", "My add-on")   # refuses with what to update
from addonkit import records, geo, data
```

Declare it in your `package.xml`: `<depend>AddonKit</depend>`. Versions
follow semantic versioning: a change that breaks you bumps the major.

### Data files

Tables live in JSON beside the code, each with its own `dataVersion`, a
schema, and a source and date on every entry. `data.load(folder, name,
accepts=">=1.0,<2", package="my_addon")` reads one, refuses a file too new
for your code, and lays the person's own entries over yours.

**Your own values** go in `~/.config/addonkit/<package>/<name>.json` (or the
folder in `ADDONKIT_OVERRIDES`), in the same shape. Updates never touch
that folder, and your entries win, key by key.

## Requirements

FreeCAD 1.0 or newer. Tested on the newest FreeCAD conda-forge builds, 1.1
and 1.0, on Linux; used on macOS. Windows is expected to work but untested.

## Licence

Code: LGPL-2.1-or-later (`LICENSE`). Data files: CC BY 4.0 (`LICENSE-DATA`).
