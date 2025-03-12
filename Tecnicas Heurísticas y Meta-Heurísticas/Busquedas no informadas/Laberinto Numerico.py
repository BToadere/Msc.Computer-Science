from collections import deque
import heapq


class Casilla(tuple):
    def __new__(cls, i, j, valor, ancestro=None, marcado=False):
        """
        Método para controlar la generación de instancias.
        """
        instance = super().__new__(cls, (i, j))
        instance.valor = valor
        instance.ancestro = ancestro
        instance.marcado = marcado
        instance.coste = float('inf')  # Inicialmente infinito
        return instance

    def __str__(self):
        return f"Casilla({self.i},{self.j})"

    @property
    def i(self):
        return self[0]

    @property
    def j(self):
        return self[1]

    def linaje(self):
        """
            Complejidad: O(n^2)
        """
        linaje = deque()
        while self:                         # n^2 iteraciones     
            linaje.appendleft(self)             # 1 extraccion cola
            self = self.ancestro                # 1 asignacion
        return linaje                       # 2*n^2 operaciones totales

class Tablero:
    def __init__(self, N, T):
        self.N = N-1
        self.T = T
        self.tracker = {}

    def obtener_casilla(self, i, j, ancestro=None):
        if (i, j) in self.tracker:
            casilla = self.tracker[(i, j)]
            return casilla

        valor = self.T[i][j]
        casilla = Casilla(i, j, valor, ancestro)
        self.tracker[(i, j)] = casilla
        return casilla

    def movimientos_posibles(self, c):
        """
            Complejidad: O(1)
        """
        mov_posibles = deque()
        desplazamientos = [(0, -c.valor), (c.valor, 0), (0, c.valor), (-c.valor, 0)]    # 8 asignaciones

        for di, dj in desplazamientos:                                                  # 4 iteraciones
            ni, nj = c.i + di, c.j + dj                                                     # 2 sumas y 2 asignaciones
            if 0 <= ni <= self.N and 0 <= nj <= self.N:                                     # 4 comparaciones
                mov_posibles.append(self.obtener_casilla(ni, nj, ancestro=c))               # 1 escritura cola
                                                                                        # 36 operaciones bucle
        return mov_posibles                                                             # 42 operaciones totales

    def posicion_inicial(self):
        return self.obtener_casilla(0, 0)

    def posicion_meta(self):
        return (self.N, self.N)

def buscar_solucion(tab, tipo='DFS', verbose=False):
    """
        Complejidad: O(n^2)
    """
    if verbose:
        print(f"\n+ Buscando solucion con {tipo}.")
    tab.tracker = {}
    cola = deque()
    cola.append(tab.posicion_inicial())                                             # 1 escritura cola
    iteraciones = 0                                                                 # 1 asignacion
 
    while cola:                                                                     # n^2 iteraciones
        iteraciones += 1                                                                # 2 operaciones
        if tipo == 'DFS':
            nodo = cola.pop()                                                           # 1 extraccion cola
        elif tipo == 'BFS':                                                             # o
            nodo = cola.popleft()                                                       # 1 extraccion pila
        else:
            raise ValueError("Tipo de busqueda no soportado.[DFS, BFS]")
        
        if verbose:
            print(f"\nVisitando: {nodo},    Ancestro: {nodo.ancestro}")

        if not nodo.marcado:                                                            # 1 comparacion
            nodo.marcado = True                                                         # 1 asignacion
            sucesores = tab.movimientos_posibles(nodo)                                  # 36 operaciones
            if verbose:
                print(f"  Generando sucesores: {sucesores}")
            cola.extend(sucesores)                                                      # 4 escritura cola

        if nodo == tab.posicion_meta():                                                 # 1 comparacion
            if verbose:
                print("\nMeta alcanzada.")
            return nodo.linaje(), iteraciones                                       # 2 + n^2 + n^2*46 operaciones totales
        
    if verbose:
        print("\nNo se encontro solucion.")
    return 'NULL', iteraciones

def buscar_dijkstra(tab, verbose=False):
    """
        Complejidad: O(n^2+n^4*log(n))
    """
    if verbose:
        print("\n+ Buscando solucion con Dijkstra.")
    tab.tracker = {}
    inicio = tab.posicion_inicial()                                                     
    inicio.coste = 0                                                                        # 1 asignacion
    iteraciones = 0                                                                         # 1 asignacion                

    cola = []
    heapq.heappush(cola, (inicio.coste, inicio))                                            # 1 escritura cola prioridad

    while cola:                                                                             # n^2 iteraciones
        iteraciones += 1                                                                        # 2 operaciones
        coste_actual, nodo = heapq.heappop(cola)                                                # 1 extraccion 
        
        if verbose:
            print(f"\nVisitando: {nodo}, coste={coste_actual},  Ancestro: {nodo.ancestro}")
        
        if not nodo.marcado:                                                                    # 1 comparacion
            nodo.marcado = True                                                                 # 1 asignacion
            for sucesor in tab.movimientos_posibles(nodo):                                      # 4 iteraciones
                nuevo_coste = nodo.coste + 1                                                        # 1 suma
                if nuevo_coste < sucesor.coste:                                                     # 1 comparacion
                    sucesor.coste = nuevo_coste                                                     # 1 asignacion
                    sucesor.ancestro = nodo                                                         # 1 asignacion
                    heapq.heappush(cola, (sucesor.coste, sucesor))                                  # 1 escritura cola prioridad
                    if verbose:                                                                 # 4*(4 + 2*n^2*log(n)) operaciones
                        print(f"  Sucesor: {sucesor},   Coste {sucesor.coste}")

        if nodo == tab.posicion_meta():                                                         # 1 comparacion                                              
            if verbose:
                print("\nMeta alcanzada.")
            return nodo.linaje(), iteraciones                                               # 3 + n^2 + n^2*(21 + 8*n^2*log(n)) operaciones totales
        
    if verbose:
        print("\nNo se encontro solucion.")
    return 'NULL', iteraciones

def visualizar_camino(tab, camino):
    """
        Complejidad: O(n^2)
    """
    tabla = [[0]*(tab.N+1) for _ in range(tab.N+1)]                                         # n^2 operaciones

    for paso, iteracion in enumerate(camino,1):                                             # n^2 iteraciones
        tabla[iteracion.i][iteracion.j]=paso                                                    # 3 operaciones
                                                                                            # 3*n^2
    return tabla                                                                            # 4*n^2 operaciones totales

if __name__ == '__main__':
    VERBOSE = False
    N = 4
    T = [
        [2, 3, 3, 2],
        [2, 1, 1, 1],
        [3, 2, 2, 2],
        [2, 2, 2, 0]
    ]
    tab3 = Tablero(N, T)

    dfs, iter_dfs = buscar_solucion(tab3, tipo='DFS', verbose=VERBOSE)
    print('DFS      ', dfs)
    print('Iteraciones DFS:', iter_dfs)
    tdfs = visualizar_camino(tab3, dfs)
    for f in tdfs: print(f)

    bfs, iter_bfs = buscar_solucion(tab3, tipo='BFS', verbose=VERBOSE)
    print('BFS      ', bfs)
    print('Iteraciones BFS:', iter_bfs)
    tbfs = visualizar_camino(tab3, bfs)
    for f in tbfs: print(f)

    dij, iter_dij = buscar_dijkstra(tab3, verbose=VERBOSE)
    print('Dijkstra ', dij)
    print('Iteraciones Dijkstra:', iter_dij)
    tdij = visualizar_camino(tab3, dij)
    for f in tdij: print(f)


