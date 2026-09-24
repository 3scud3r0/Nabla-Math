from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from nablamath.orbits import earth_circular_orbit
from nablamath.orbit_svg import write_earth_orbit_svg


class VisualizationTests(unittest.TestCase):
    def test_svg_parses_and_contains_scaled_orbit(self):
        with tempfile.TemporaryDirectory() as directory:
            output = write_earth_orbit_svg(earth_circular_orbit(400_000),
                                           Path(directory) / "orbit.svg")
            root = ET.parse(output).getroot()
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            ellipse = root.find("{http://www.w3.org/2000/svg}ellipse")
            self.assertEqual(ellipse.attrib["rx"], ellipse.attrib["ry"])
            circles = root.findall("{http://www.w3.org/2000/svg}circle")
            self.assertLess(float(circles[0].attrib["r"]), float(ellipse.attrib["rx"]))
            self.assertIn("Não inclui inclinação", output.read_text(encoding="utf-8"))
