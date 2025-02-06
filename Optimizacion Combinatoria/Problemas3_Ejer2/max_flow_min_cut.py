"""
###############################################################################
# Nombre del Archivo   : max_flow_min_cut.py
# Autor                : Bogdan Stefan Toadere
# Fecha de Creación    : 10/12/2024
# Última Modificación  : 11/12/2024
# Descripción          : Implementación del algoritmo de flujo máximo presentado
#                        en 2017 por Alexander Schrijver.
# Observaciones        : Desarrollo con fines pedagógico sin control de errores
#                        y sin optimizar.
# Licencia             : Este código está bajo la licencia CC BY 4.0. 
#                        Se permite usar, compartir y adaptar con atribución. 
#                        Detalles: https://creativecommons.org/licenses/by/4.0/
###############################################################################
"""




from collections import deque

def find_path(Af, s, t):
    """
        Encuentra un camino aumentante de s a t en el grafo residual usando BFS.
        
        Parámetros:
            Af: Grafo residual como lista de adyacencia.
            s: Nodo fuente.
            t: Nodo sumidero.
        
        Retorna:
            path: Lista de nodos que conforman el camino aumentante encontrado.
                Si no hay camino, retorna None.
    """
    visited = set()
    queue = deque([(s, [s])])  # Cola con tuplas (nodo actual, camino acumulado)
    
    while queue:
        current, path = queue.popleft()
        if current == t:
            return path  # Camino encontrado
        for neighbor in Af.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None  # No se encontró camino


def build_residual_graph(A, c, f):
    """
        Construye el grafo residual en formato de lista de adyacencia 
        (para luego poder buscar con mayor facilidad el camino aumentante).
        
        Parámetros:
            A: Lista de arcos (u, v) del grafo original.
            c: Diccionario con capacidades máximas de los arcos, c[(u, v)].
            f: Diccionario con el flujo actual en cada arco, f[(u, v)].
        
        Retorna:
            Af: Grafo residual representado como lista de adyacencia.
    """
    Af = {}
    for (u, v) in A:
        # Arco forward (capacidad residual positiva)
        if f[(u, v)] < c[(u, v)]:
            Af.setdefault(u, []).append(v)
        # Arco backward (flujo positivo existente)
        if f[(u, v)] > 0:
            Af.setdefault(v, []).append(u)
    return Af


def augmenting_flow_step(V, A, c, f, s, t, verbose=False):
    """
        Realiza un paso del algoritmo de Ford-Fulkerson para encontrar y aumentar flujo.
        
        Parámetros:
            V: Lista de nodos.
            A: Lista de arcos (u, v).
            c: Diccionario con capacidades máximas de los arcos.
            f: Diccionario con el flujo actual.
            s: Nodo fuente.
            t: Nodo sumidero.
            verbose: Si es True, imprime detalles del proceso.
        
        Retorna:
            - Si hay un camino aumentante: Diccionario actualizado con el flujo.
            - Si no hay camino aumentante: Lista de arcos en el corte mínimo.
    """
    # Construir el grafo residual
    Af = build_residual_graph(A, c, f)
    if verbose:
        print("Grafo residual Af:", Af)

    # Buscar un camino aumentante
    path = find_path(Af, s, t)

    if path is not None:    # Caso 1
        if verbose:
            print("Camino aumentante encontrado:", path)

        # Determinar la capacidad mínima en el camino (α)
        sigmas = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if (u, v) in A:  # Arco forward
                sigmas.append(c.get((u, v), 0) - f.get((u, v), 0))
            elif (v, u) in A:  # Arco backward
                sigmas.append(f.get((v, u), 0))
        
        alpha = min(sigmas)  # Capacidad máxima que puede añadirse al flujo
        if verbose:
            print("σ:", sigmas)
            print("α:", alpha)

        # Actualizar el flujo en los arcos
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if (u, v) in A:  # Arco forward
                f[(u, v)] += alpha
            elif (v, u) in A:  # Arco backward
                f[(v, u)] -= alpha

        # Retorna el flujo actualizado
        return f

    else:                   # Caso 2
        if verbose:
            print("No existe camino aumentante s-t.")

        # Determinar los nodos alcanzables desde s en el corte mínimo
        U = set()
        queue = deque([s])
        U.add(s)
        while queue:
            u = queue.popleft()
            for v in Af.get(u, []):
                if v not in U:
                    U.add(v)
                    queue.append(v)

        # Generar el corte mínimo
        cut = [(u, v) for (u, v) in A if u in U and v not in U]
        return cut


def maximum_flow_algorithm(V, A, c, s, t, f=None, verbose=False):
    """
        Algoritmo de flujo máximo basado en Ford-Fulkerson.
        
        Parámetros:
            V: Lista de nodos.
            A: Lista de arcos (u, v).
            c: Diccionario con capacidades máximas de los arcos.
            s: Nodo fuente.
            t: Nodo sumidero.
            verbose: Si es True, imprime detalles del proceso.
        
        Retorna:
            - f: Diccionario con el flujo máximo en cada arco.
            - cut: Lista de arcos en el corte mínimo.
            - value_f: Valor total del flujo máximo.
        
        >>> V = [0, 1, 2, 3, 4, 5]
        >>> c = {
        ...     (0, 1): 16, (0, 2): 13,
        ...     (1, 2): 10, (1, 3): 12,
        ...     (2, 1): 4,  (2, 4): 14,
        ...     (3, 2): 9,  (3, 5): 20,
        ...     (4, 3): 7,  (4, 5): 4,
        ... }
        >>> A = list(c.keys())
        >>> s = 0
        >>> t = 5
        >>> f, cut, value_f = maximum_flow_algorithm(V, A, c, s, t, verbose=False)
        >>> value_f
        23
    """
    # Asegurarse de que todos los arcos en A tengan un valor definido en f
    f = f if f else {}
    for a in A:
        if a not in f:
            f[a] = 0  # Inicializar con 0 si no está definido

    
    
    iteration = 0
    while True:
        if verbose:
            print(f"\nIteración {iteration}:")
        
        # Intentar aumentar el flujo
        result = augmenting_flow_step(V, A, c, f, s, t, verbose=verbose)

        if isinstance(result, list):  # Si no hay camino aumentante, devuelve el corte mínimo
            cut = result
            break
        else:
            f = result  # Flujo actualizado
        iteration += 1

    # Calcular el valor del flujo máximo
    value_f = sum(f[(s, v)] for v in V if (s, v) in A)

    if verbose:
        print("\n=== Resultado final ===")
        print("Flujo máximo:", f)
        print("Corte mínimo δ^{out}(U):", cut)
        print("Valor del flujo máximo:", value_f)

    return f, cut, value_f


if __name__ == '__main__':
    # Datos Ejercicio:
    V = ['s', 'a', 'b', 'c', 'd', 'e', 'f', 't']
    
    c = {
        ('s', 'a'): 3, ('s', 'b'): 6, ('s', 'c'): 8, 
        ('a', 'b'): 4, ('a', 'd'): 2, ('a', 'e'): 7,
        ('b', 'd'): 6, ('b', 'e'): 1, ('b', 'f'): 2,
        ('c', 'b'): 4, ('c', 'f'): 4,
        ('d', 'e'): 1, ('d', 't'): 3,
        ('e', 't'): 9, 
        ('f', 'e'): 5, ('f', 't'): 5
    }
    A = list(c.keys())
    
    s = 's'
    t = 't'

    flujo_inicial = {
        ('s', 'a'): 3, ('s', 'b'): 3, ('s', 'c'): 4, 
        ('a', 'b'): 0, ('a', 'd'): 0, ('a', 'e'): 3,
        ('b', 'd'): 3, ('b', 'e'): 0, ('b', 'f'): 0,
        ('c', 'b'): 0, ('c', 'f'): 4,
        ('d', 'e'): 0, ('d', 't'): 3,
        ('e', 't'): 3, 
        ('f', 'e'): 0, ('f', 't'): 4
    }

    

    # Ejecutar el algoritmo
    f, cut, value_f = maximum_flow_algorithm(V, A, c, s, t, verbose=True)

    # print(f, cut,  value_f, sep='\n')
