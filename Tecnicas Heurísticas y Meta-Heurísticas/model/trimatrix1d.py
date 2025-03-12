import math

class DistanceMatrix:
    def __init__(self, points):
        self.n = len(points)
        self.distances = [0] * (self.n * (self.n - 1) // 2)
        self._compute_distances(points)
    
    def _compute_distances(self, points):
        def euclidean(p1, p2):
            return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        
        index = 0
        for i in range(1, self.n):
            for j in range(i):
                self.distances[index] = euclidean(points[i], points[j])
                index += 1

    def get_distance(self, i, j):
        if i == j:
            return 0
        if i < j:
            i, j = j, i  # Asegurar que siempre accedemos (i > j)
        index = i * (i - 1) // 2 + j
        return self.distances[index]

# Ejemplo de uso:
points = [(0, 1, 2), (1, 4, 6), (2, 7, 8), (3, 2, 3)]
dm = DistanceMatrix([p[1:] for p in points])  # Pasamos solo coordenadas
print(dm.get_distance(1, 3))  # Distancia entre el punto 1 y 3
