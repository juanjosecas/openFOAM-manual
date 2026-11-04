"""Pruebas matematicas independientes del solver."""
import importlib.util
import math
import unittest
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location(
 "ray",Path(__file__).with_name("trazar.py"))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestRayos(unittest.TestCase):
 def test_snell(self):
  d=[.5,0,-math.sqrt(.75)]
  refl,trans=mod.snell(d,[0,0,1],1,1.333)
  self.assertAlmostEqual(trans[0],.5/1.333)
  self.assertGreater(refl[2],0)
 def test_rit(self):
  d=[math.sin(math.radians(60)),0,-math.cos(math.radians(60))]
  self.assertIsNone(mod.snell(d,[0,0,1],1.333,1)[1])
 def test_plano(self):
  h=np.full(mod.NX,.03)
  ramas,p,n=mod.rayos(h)
  self.assertEqual(len(ramas),3)
  self.assertAlmostEqual(p[2],.03,places=5)
  self.assertAlmostEqual(n[2],1,places=6)
 def test_altura(self):
  pts=np.array([(x,.0005,z) for x in mod.X
                for z in (np.arange(mod.NZ)+.5)*mod.DZ])
  h=mod.altura(pts,(pts[:,2]<.03).astype(float))
  self.assertTrue(np.allclose(h,.03))

if __name__=="__main__":
 unittest.main()
