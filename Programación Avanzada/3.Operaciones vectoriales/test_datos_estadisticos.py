import unittest
import numpy as np
from datos_estadisticos import cen_med_mediana_moda

class test_datos_esatdisticos(unittest.TestCase):
    def test_cen_med_mediana_moda(self):
        self.assertEqual(tuple(cen_med_mediana_moda()),np.array(11.,  9.,  8.,  2.))


if __name__=='__main__':
    # print(cen_med_mediana_moda)
    unittest.main()

