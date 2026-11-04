import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rayos import trazar, s

class TestSnell(unittest.TestCase):
    def test_normal(self):
        r = trazar(angulo=0)
        self.assertAlmostEqual(r["angulo_refractado"], 0)
    def test_snell(self):
        r = trazar(angulo=35)
        self.assertAlmostEqual(r["n1"]*math.sin(math.radians(r["angulo"])),
            r["n2"]*math.sin(math.radians(r["angulo_refractado"])), places=12)
    def test_rit(self):
        r = trazar(angulo=60, n1=1.333, n2=1.0003, desde="abajo")
        self.assertTrue(r["rit"])
        self.assertEqual(len(r["segmentos"]), 2)
    def test_azimut(self):
        r = trazar(angulo=30, azimut=90)
        choque = r["segmentos"][0][2]
        self.assertAlmostEqual(choque[0], 0, places=12)
        self.assertAlmostEqual(s(choque, 90), choque[1])
    def test_abajo(self):
        r = trazar(desde="abajo")
        self.assertLess(r["segmentos"][0][1][2], 0)
        self.assertGreater(r["segmentos"][-1][2][2], 0)
    def test_parametros(self):
        with self.assertRaises(ValueError):
            trazar(angulo=90)
        with self.assertRaises(ValueError):
            trazar(n2=0)

if __name__ == "__main__":
    unittest.main()
