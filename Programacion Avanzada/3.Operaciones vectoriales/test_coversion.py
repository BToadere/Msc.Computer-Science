import unittest
import numpy as np
from Tabla_conversion_grados import conversion_grados_rad, line_space

class test_conversion_grados(unittest.TestCase):
    def test_conversion_grados_rad(self):
        self.assertEqual(conversion_grados_rad(180), np.pi)
        self.assertRaises(TypeError, conversion_grados_rad)
        self.assertRaises(TypeError, conversion_grados_rad, ((90)), ([90]))
        self.assertEqual(conversion_grados_rad((90)), np.pi/2)

    def test_line_space(self):
        self.assertEqual(line_space(2), np.linspace(0,100,2))



if __name__=='__main__':
    print(
        # conversion_grados_rad(180)
          )
    unittest.main()
    # conversion_grados_rad()
