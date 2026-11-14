# SPDX-License-Identifier: LGPL-2.1-or-later
# AddonKit's own tests: the version check and the data files run anywhere;
# records, shapes and fits need FreeCAD and skip without it.
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import addonkit  # noqa: E402
from addonkit import data  # noqa: E402

try:
    if os.environ.get("FREECAD_LIB"):
        sys.path.append(os.environ["FREECAD_LIB"])
    import FreeCAD  # noqa: F401

    HAVE_FC = True
except ImportError:
    HAVE_FC = False


class Version(unittest.TestCase):
    def test_ranges(self):
        self.assertTrue(addonkit.satisfies(">=1.0,<2", "1.4.2"))
        self.assertFalse(addonkit.satisfies(">=1.0,<2", "2.0.0"))
        self.assertFalse(addonkit.satisfies(">=1.1", "1.0.9"))
        self.assertTrue(addonkit.satisfies("==1.0", "1.0.0"))

    def test_require_says_what_to_update(self):
        with self.assertRaises(addonkit.Refused) as c:
            addonkit.require(">=9", "Make")
        self.assertIn("Update AddonKit", c.exception.message)
        self.assertEqual(c.exception.code, "unavailable")

    def test_no_addon_imported(self):
        # The library imports no add-on and nothing of Agent Link's.
        code = "import sys; sys.path.insert(0, %r); import addonkit, addonkit.data; print(sorted(m for m in sys.modules if m.startswith(('agentlink', 'workshop'))))" % ROOT
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(out, "[]")


SCHEMA = {"type": "object", "required": ["d", "source", "date"],
          "properties": {"d": {"type": "number", "minimum": 0}, "source": {"type": "string"}, "date": {"type": "string"}},
          "additionalProperties": False}


def write(folder, name, obj):
    with open(os.path.join(folder, name), "w") as f:
        json.dump(obj, f)


class Data(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.user = tempfile.mkdtemp()
        os.environ["ADDONKIT_OVERRIDES"] = self.user
        write(self.tmp, "t.schema.json", SCHEMA)
        write(self.tmp, "t.json", {"$schema": "t.schema.json", "dataVersion": "1.2.0", "licence": "CC-BY-4.0",
                                   "entries": {"pla": {"d": 1.24, "source": "datasheet", "date": "2026-11-14"},
                                               "petg": {"d": 1.27, "source": "datasheet", "date": "2026-11-14"}}})

    def tearDown(self):
        os.environ.pop("ADDONKIT_OVERRIDES", None)

    def test_load_and_check(self):
        got = data.load(self.tmp, "t")
        self.assertEqual(got["entries"]["pla"]["d"], 1.24)
        self.assertEqual(data.check_folder(self.tmp), [])

    def test_too_new_is_refused(self):
        with self.assertRaises(data.DataError) as c:
            data.load(self.tmp, "t", accepts=">=1.0,<1.2")
        self.assertIn("Update the add-on", c.exception.message)

    def test_user_entries_win_and_are_marked(self):
        os.makedirs(os.path.join(self.user, "mine"))
        write(os.path.join(self.user, "mine"), "t.json", {"entries": {"pla": {"d": 1.3, "date": "2026-11-15"}}})
        got = data.load(self.tmp, "t", package="mine")
        self.assertEqual((got["entries"]["pla"]["d"], got["entries"]["pla"]["source"]), (1.3, "user"))
        self.assertEqual(got["overridden"], ["pla"])

    def test_bad_user_entry_says_which(self):
        os.makedirs(os.path.join(self.user, "mine"))
        write(os.path.join(self.user, "mine"), "t.json", {"entries": {"pla": {"d": -1, "date": "x"}}})
        with self.assertRaises(data.DataError) as c:
            data.load(self.tmp, "t", package="mine")
        self.assertIn("below 0", c.exception.message)

    def test_provenance_is_required(self):
        write(self.tmp, "u.json", {"dataVersion": "1.0.0", "entries": {"x": {"d": 1}}})
        self.assertTrue(any("source and date" in p for p in data.check_folder(self.tmp)))

    def test_side_by_side_versions(self):
        write(self.tmp, "t@1.0.json", {"$schema": "t.schema.json", "dataVersion": "1.0.0",
                                       "entries": {"pla": {"d": 1.2, "source": "old", "date": "2025-01-01"}}})
        self.assertEqual(data.load(self.tmp, "t", tag="1.0")["entries"]["pla"]["d"], 1.2)
        self.assertEqual(data.load(self.tmp, "t", tag="1.1")["entries"]["pla"]["d"], 1.24)

    def test_shipped_data_is_valid(self):
        folder = os.path.join(ROOT, "addonkit", "data")
        if not os.path.isdir(folder):
            self.skipTest("no data files yet")
        self.assertEqual(data.check_folder(folder), [])


class Records(unittest.TestCase):
    def test_meta_only_document(self):
        from addonkit import records

        class Doc:
            Meta = {}

        d = Doc()
        records.write(d, "spec", {"wall": 1.2})
        self.assertEqual(records.read(d, "spec", {}), {"wall": 1.2})


@unittest.skipUnless(HAVE_FC, "FreeCAD is not importable here")
class Fits(unittest.TestCase):
    def test_tables_from_data(self):
        from addonkit import fits

        self.assertEqual(fits.FITS, {"press": 0.0, "snug": 0.1, "slide": 0.2, "free": 0.35})
        self.assertEqual(fits.M["M3"]["clear"], (3.2, 3.4, 3.6))
        self.assertAlmostEqual(fits.size_fit("slide", 8.0, "hole", fits.DEFAULT_CAL), 8.4)


@unittest.skipUnless(HAVE_FC, "FreeCAD is not importable here")
class Shapes(unittest.TestCase):
    def test_round_rect_prism_volume(self):
        from addonkit import geo

        s = geo.prism(0, 0, 20, 10, 0.0, 0, 5)
        self.assertAlmostEqual(s.Volume, 1000.0, delta=1.0)


if __name__ == "__main__":
    unittest.main()
