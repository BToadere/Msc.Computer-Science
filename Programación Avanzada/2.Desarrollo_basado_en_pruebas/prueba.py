import unittest
from desarrollo_basado_en_pruebas import romanum
class UnitTests(unittest.TestCase):
   def test_romanum(self):
      self.assertEqual(romanum('X'), 10)
      self.assertEqual(romanum('LX'), 60)
      self.assertRaises(KeyError, romanum, ('Z'))
      self.assertEqual(romanum(''), 0)
      self.assertRaises(TypeError, romanum)
if __name__=='__main__':
   unittest.main()