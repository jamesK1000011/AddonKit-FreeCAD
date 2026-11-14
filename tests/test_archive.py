# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from addonkit import archive  # noqa: E402


class Zip(unittest.TestCase):
    def test_names_modes_and_sources(self):
        d = tempfile.mkdtemp()
        src = os.path.join(d, "a.gbr")
        with open(src, "w") as f:
            f.write("G04*")
        out = archive.write_zip(os.path.join(d, "o.zip"), [("/x\\a.gbr", src), ("b.txt", b"bytes"), ("c.md", "text")])
        with zipfile.ZipFile(out) as z:
            self.assertEqual(z.namelist(), ["x/a.gbr", "b.txt", "c.md"])
            self.assertEqual(z.read("x/a.gbr"), b"G04*")
            self.assertEqual(z.read("c.md"), b"text")
            self.assertEqual(z.getinfo("b.txt").external_attr >> 16, 0o644)
            self.assertEqual(z.getinfo("b.txt").compress_type, zipfile.ZIP_DEFLATED)


if __name__ == "__main__":
    unittest.main()
