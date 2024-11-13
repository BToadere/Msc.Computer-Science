import unittest
from puntos_proximos import distancia_euclidea, lectura_fichero, calculo_distancias_puntos

class UnitTests(unittest.TestCase):
    def test_distancia_euclidea(self):
        self.assertEqual(distancia_euclidea((1,),(2,)), 1)
        self.assertEqual(distancia_euclidea((0,0),(1,1)), 2**(1/2)),
        self.assertRaises(IndexError, distancia_euclidea, (0,0),(1,))

    def test_lectura_fichero(self):
        self.assertEqual(lectura_fichero('coordenadas.txt'), [(3.0, 3.0), (4.0, -1.0), (2.0, 2.0), (-4.0, -1.0), (-2.0, 2.0), (9.0, 1.0), (-8.0, -6.0), (-3.0, 2.0)])
        self.assertRaises(FileNotFoundError, lectura_fichero, ('archivo_innexistente'))

    def test_calculo_distancias_puntos(self):
        self.assertEqual(calculo_distancias_puntos((0,0), [(1,1), (0,0)]), [2**(1/2), 0])
        self.assertIsInstance(calculo_distancias_puntos((0,0), [(1,1), (0,0)]), list)
        self.assertRaises(TypeError, calculo_distancias_puntos)
   
if __name__=='__main__':
   unittest.main()