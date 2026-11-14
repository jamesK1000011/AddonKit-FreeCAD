# SPDX-License-Identifier: LGPL-2.1-or-later
"""AddonKit for FreeCAD: what FreeCAD add-ons share, so none copies another.

- records: notes kept in the document itself (setups, specs, materials per
  body, calibrations), saved with the .FCStd and taken back by undo
- geo: shape building and reading on FreeCAD's Part module
- fits: fits and hardware holes for made parts
- data: versioned, schema-checked data files with the person's overrides
- Refused: a refusal that says what to do instead
- ui (GUI only): a parameter dialog and the pieces panels share

Plain Python on FreeCAD; no add-on here imports any other add-on.
Depend on it with a version range: addonkit.require(">=1.0,<2").
"""

VERSION = "1.1.0"


class Refused(ValueError):
    """A request an add-on will not carry out, with what to do instead.
    code: invalid_input, not_found, invalid_state, unavailable."""

    def __init__(self, message, code="invalid_input"):
        super().__init__(message)
        self.code = code
        self.message = message


def _parse(v):
    return tuple(int(x) for x in v.split("."))


def satisfies(spec, version=VERSION):
    """True when version meets every clause of spec (">=1.0,<2")."""
    have = _parse(version)
    for clause in (c.strip() for c in spec.split(",") if c.strip()):
        for op in (">=", "<=", "==", ">", "<"):
            if clause.startswith(op):
                want = _parse(clause[len(op):].strip())
                n = max(len(have), len(want))
                a, b = have + (0,) * (n - len(have)), want + (0,) * (n - len(want))
                ok = {">=": a >= b, "<=": a <= b, "==": a == b, ">": a > b, "<": a < b}[op]
                if not ok:
                    return False
                break
        else:
            raise ValueError(f"version clause {clause!r}: use >=, <=, ==, > or <")
    return True


def require(spec, who="This add-on"):
    """Refuse, saying what to update, when AddonKit's version is outside spec."""
    if not satisfies(spec):
        raise Refused(f"{who} needs AddonKit {spec}; this is {VERSION}. Update AddonKit for FreeCAD (Addon Manager, or the add-on's own updater).", "unavailable")
    return VERSION
