import random
import numpy as np
import time

class Distance_Matrix_L:
    def __init__(self, points):
        self.n = len(points)
        self.matrix = [[] for _ in range(self.n)]  # Lista de listas (triangular inferior)
        self._compute_distances(points)
    
    def _compute_distances(self, points):
        """Calcula la matriz triangular de distancias usando NumPy para vectorización."""
        coords = np.array([(p[1], p[2]) for p in points])  # Extraemos coordenadas (x, y)
        
        for i in range(1, self.n):  # Empezamos desde la segunda fila
            # Calculamos la distancia a todos los puntos anteriores
            diffs = coords[i] - coords[:i]  
            distances = np.sqrt(np.sum(diffs**2, axis=1))  # Distancia euclidiana
            self.matrix[i] = distances.tolist()  # Guardamos la fila triangular
    
    def get_distance(self, i, j):
        """Obtiene la distancia entre los nodos i y j. Se asume que i, j están en base 1."""
        if i == j:
            return 0
        if i > j:
            return self.matrix[i][j]  # Acceso directo en la triangular
        else:
            return self.matrix[j][i]  # Simetría: d(i, j) = d(j, i)
    
    def __str__(self):
        """Representación matricial de la matriz triangular."""
        output = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                if j > i:
                    row.append("   ")  # Espacios vacíos para mantener formato
                elif i == j:
                    row.append("--")  # Representa la diagonal principal
                else:
                    row.append(f"{self.get_distance(i+1, j+1):.2f}")
            output.append(" ".join(row))
        return "\n".join(output)


def parse_tsp_file(file_path):
    metadata = {}
    nodes = []
    is_node_section = False
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("COMMENT"):
                continue

            if line == "NODE_COORD_SECTION":
                is_node_section = True
                continue
            
            if is_node_section:
                parts = line.split()
                if len(parts) == 3:
                    node_id, x, y = map(float, parts)
                    nodes.append((int(node_id), x, y))
            else:
                key_value = line.split(":")
                if len(key_value) == 2:
                    key_aux, value_aux = key_value
                    key, value = key_aux.strip(), value_aux.strip()
                    metadata[key.strip()] = value.strip()
    
    return metadata, nodes


def vecindario_aleatorio(estado=None):
    ciudades = list(range(int(metadata['DIMENSION'])))
    random.shuffle(ciudades)
    return [ciudades]

def vecindario_2opt(estado):
    n = len(estado)
    for i in range(n - 1):
        for j in range(i + 2, n):
            vecino = estado[:i+1] + estado[i+1:j][::-1] + estado[j:]
            yield vecino


def vecindario_2opt_rand(tour):
    n = len(tour)
    indices = list(range(n - 1))
    random.shuffle(indices)
    
    for i in indices:
        j_indices = list(range(i + 1, n))
        random.shuffle(j_indices)
        
        for j in j_indices:
            yield tour[:i] + tour[i:j+1][::-1] + tour[j+1:]

def vecindario_2opt_rand_lim(estado, max_vecinos=100):
    n = len(estado)
    indices = list(range(n - 1))
    random.shuffle(indices)  # Desordena los índices para exploración aleatoria
    
    vecinos_generados = 0
    for i in indices:
        j_indices = list(range(i + 2, n))
        random.shuffle(j_indices)
        for j in j_indices:
            if vecinos_generados >= max_vecinos:
                return
            yield estado[:i] + estado[i:j+1][::-1] + estado[j+1:]
            vecinos_generados += 1

def vecindario_3opt(estado):
    n = len(estado)
    for i in range(n - 2):
        for j in range(i + 2, n - 1):
            for k in range(j + 2, n):
                nuevo = estado[:i+1] + estado[i+1:j][::-1] + estado[j:k][::-1] + estado[k:]
                yield nuevo

def vecindario_swap(estado):
    n = len(estado)
    for i in range(n-1):    
        for j in range(i+1,n):
            vecino = estado[:]
            vecino[i], vecino[j] = vecino[j], vecino[i]
            yield vecino

def two_opt_neighborhood(tour):
    """
    Generate the 2-opt neighborhood for a given tour.

    :param tour: A list of integers representing the tour (cities).
    :yield: A new tour with a 2-opt swap applied.
    """
    n = len(tour)
    for i in sorted(list(range(0, n - 1)), key= lambda _ : random.random()):  # i starts from 1 to avoid the first city
        for j in sorted(list(range(i + 1, n )), key= lambda _ : random.random()):  # j starts from i + 1 to ensure we don't swap the same edge
            # Create a new tour with the 2-opt swap
            #print(f"{i}--{j}")
            new_tour = tour[:i] + tour[i:j+1][::-1] + tour[j+1:]
            yield new_tour



def perturbacion(solucion):
    n = len(solucion)
    i, j = sorted(random.sample(range(n), 2))
    segmento = solucion[i:j+1]
    random.shuffle(segmento)
    return solucion[:i] + segmento + solucion[j+1:]

def perturbacion_double_bridge(solucion):
    n = len(solucion)
    # Selecciona 4 puntos de corte (evitando la posición 0 para preservar el inicio fijo si se desea)
    pos = sorted(random.sample(range(1, n), 4))
    a, b, c, d = pos
    # Reconecta los segmentos: [0, a] + [c, d] + [b, c] + [a, b] + [d, n]
    return solucion[:a] + solucion[c:d] + solucion[b:c] + solucion[a:b] + solucion[d:]



def funcion_objetivo(solucion, matriz_d):
    return sum([matriz_d.get_distance(solucion[i],solucion[i+1]) for i in range(len(solucion)-1)]) + matriz_d.get_distance(solucion[-1],solucion[0])


def do_simulated_annealing_raw(generar_ruta_inicial, matriz_d, t_max, t_min, max_iter, n_sin_mejora, deca=0.9, vecindario=None, distribucion=None):
    actual = generar_ruta_inicial()[0]
    mejor_solucion = actual
    mejor_valor = funcion_objetivo(actual, matriz_d)
    
    T = t_max
    no_mejora = 0

    for i in range(max_iter):
        valor_actual = funcion_objetivo(actual, matriz_d)
        if valor_actual < mejor_valor:
            mejor_solucion = actual
            mejor_valor = valor_actual
            no_mejora = 0 
        else:
            no_mejora += 1  
        print(f'{i:5}. Temp: {T:11.5f} - Obj: {valor_actual:21.16f} - Sin mejora: {no_mejora}/{n_sin_mejora}')
        
        for vecino in vecindario(actual):
            delta = funcion_objetivo(vecino, matriz_d) - valor_actual
            if delta <= 0:
                actual = vecino
                break
            else:
                if random.random() < distribucion(delta, T): 
                    actual = vecino
                    break

        T = deca * T
        
        # **Criterios de parada**
        if no_mejora >= n_sin_mejora or T < t_min:
            break

    return mejor_solucion, mejor_valor



def do_simulated_annealing(actual, matriz_d, t_max, t_min, max_iter, n_sin_mejora, deca=0.9, vecindario=None, distribucion=None, mejor_ils=0, verbose=False):
    mejor_solucion = actual
    mejor_valor = funcion_objetivo(actual, matriz_d)
    
    T = t_max
    no_mejora = 0
    no_progresa = 0
    flag=False
    max_nomejora = 0
    n_sin_mejora_bkp = n_sin_mejora
    for i in range(max_iter):
        valor_actual = funcion_objetivo(actual, matriz_d)
        if mejor_valor < mejor_ils:
            mejor_ils=mejor_valor
        print(f'{i:6}. Temp: {T:11.5f} - Obj: {valor_actual:21.16f} - Sin mejora: {no_mejora}/{n_sin_mejora}  ({max_nomejora}) - Mejor: {mejor_ils}')
        
        error = (valor_actual-mejor_valor)/mejor_valor
            
        if error<0.009:
            no_progresa+=1
            if no_progresa > n_sin_mejora//4:
                flag = True
        
        if error < -0.009:
            no_progresa = 0
            n_sin_mejora = n_sin_mejora_bkp
            flag=False
        
        if valor_actual < mejor_valor:
            if flag:
                n_sin_mejora = n_sin_mejora//2
            mejor_solucion = actual
            mejor_valor = valor_actual
            if no_mejora>max_nomejora:
                max_nomejora=no_mejora
            no_mejora = 0 
        else:
            no_mejora += 1  
        
        

        for vecino in vecindario(actual):
            delta = funcion_objetivo(vecino, matriz_d) - valor_actual
            if delta <= 0:
                actual = vecino
                break
            else:
                if random.random() < distribucion(delta, T): 
                    actual = vecino
                    break

        T = deca * T
        
        # **Criterios de parada**
        if no_mejora >= n_sin_mejora or T < t_min:
            break

    return mejor_solucion, mejor_valor


def do_iterated_local_search(generar_ruta_inicial, matriz_d, max_iter_ils, perturbacion, 
                             t_max, t_min, max_iter, n_sin_mejora, deca, vecindario, distribucion):
    actual = generar_ruta_inicial()[0]
    actual_cost = funcion_objetivo(actual, matriz_d)
    best_sol, best_cost = actual, actual_cost
    t_max_perturb = .5  # Por ejemplo, 10 veces menor
    for i in range(max_iter_ils):
        mejor_local, mejor_local_cost = do_simulated_annealing(actual, 
                                                               matriz_d,
                                                               t_max=t_max,
                                                               t_min=t_max_perturb/10,
                                                               max_iter=int(max_iter*0.8),
                                                               n_sin_mejora=n_sin_mejora,
                                                               deca=deca,
                                                               vecindario=vecindario,
                                                               distribucion=distribucion,
                                                               mejor_ils=best_cost,
                                                               verbose=True)
        # 2. Perturbación fuerte
        perturbada = perturbacion_double_bridge(mejor_local)
        
        # 3. SA intensivo: reiniciamos la temperatura a un valor menor para explotar localmente
        
        nueva_solucion, nueva_cost = do_simulated_annealing(perturbada, 
                                                            matriz_d,
                                                            t_max=t_max_perturb,
                                                            t_min=t_min,
                                                            max_iter=max_iter,
                                                            n_sin_mejora=n_sin_mejora,
                                                            deca=deca,
                                                            vecindario=vecindario,
                                                            distribucion=distribucion,
                                                            mejor_ils=best_cost,
                                                            verbose=True)
        # 4. Criterio de aceptación
        if nueva_cost < best_cost:
            best_sol, best_cost = nueva_solucion, nueva_cost

        actual, actual_cost = best_sol, best_cost
        print(f'ILS: {i:5} - Obj: {actual_cost:21.16f}')
    return best_sol, best_cost





if __name__ == "__main__":
    a = "data/xqf131.tsp"
    b = "data/dj38.tsp"
    c = "data/ar9152.tsp"

    metadata, nodes = parse_tsp_file(a)
    matriz_d = Distance_Matrix_L(nodes)

    DO_ITERATED_LOCAL_SEARCH = True

    # Iniciar temporizador
    start_time = time.time()

    if DO_ITERATED_LOCAL_SEARCH:
        solucion, coste = do_iterated_local_search(
            generar_ruta_inicial=vecindario_aleatorio,
            matriz_d=matriz_d, 
            max_iter_ils=3,
            perturbacion=perturbacion_double_bridge,
            t_max=3,
            t_min=0.0001,
            max_iter=20000,
            n_sin_mejora=2500,
            deca=0.9998,
            vecindario=vecindario_2opt_rand,
            distribucion=lambda delta, T: np.exp(-delta/T)
        )
    else:
        solucion, coste = do_simulated_annealing(
            actual=vecindario_aleatorio()[0],
            matriz_d=matriz_d, 
            t_max=10**1, 
            t_min=0, 
            max_iter=10**6,
            n_sin_mejora=4000,
            deca=0.99995, 
            vecindario=vecindario_2opt_rand, 
            distribucion=lambda delta, T: np.exp(-delta/T),
            verbose=True
        )

    # Detener temporizador
    end_time = time.time()
    
    # Calcular tiempo total
    elapsed_time = end_time - start_time

    # Imprimir resultados
    print('Solución')
    print(solucion, coste, sep='\n')
    print(f"\nTiempo de ejecucion: {elapsed_time/60:.5f} minutos")

