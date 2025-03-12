import random
import numpy as np
import multiprocessing as mp

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



def vecindario_aleatorio(actual=None):
    ciudades = list(range(int(metadata['DIMENSION'])))
    random.shuffle(ciudades)
    return [ciudades]

def distancia(a,b):
    return ((nodes[a-1][1]-nodes[b-1][1])**2+(nodes[a-1][2]-nodes[b-1][2])**2)**(1/2)

def funcion_objetivo(solucion):
    # suma = 0
    # for i in range(len(solucion)-1):
    #     suma += 
    # suma += distancia(solucion[-1],solucion[0])
    suma = sum([distancia(solucion[i],solucion[i+1]) for i in range(len(solucion)-1)]) + distancia(solucion[-1],solucion[0])

    return suma

def vecindario_2opt(estado):
    for i in range(len(estado)):
        for j in range(i+3,len(estado)):
            parte_1 = estado[:i+1]
            parte_2 = estado[i+1:j]
            parte_3 = estado[j:]
            parte_2.reverse()
            vecino = parte_1 + parte_2 + parte_3
            yield vecino

def vecindario_swap(estado):
    for i in range(len(estado)):    
        for j in range(i+1,len(estado)):
            vecino = estado[:]
            vecino[i], vecino[j] = vecino[j], vecino[i]
            yield vecino

def do_simulated_annealing(generar_ruta_inicial, t_max, t_min, max_iter, deca = 0.9, vecindario = None, distribucion = None, verbose = False):
    actual = list(range(1,39))#generar_ruta_inicial()[0]
    T=t_max
    n=0
    for _ in range(max_iter):
        for vecino in vecindario(actual):
            n+=1
            delta = funcion_objetivo(vecino) - funcion_objetivo(actual)
            if delta <= 0:
                actual = vecino
                break
            else:
                if random.random() < distribucion(delta, T): 
                    actual = vecino
                    break
        T = deca*T
        if verbose:
            print(f'Temp: {T:.5f} - {funcion_objetivo(actual)}')
    return actual




if __name__ == "__main__":

    a = "data/xqf131.tsp"
    b = "data/dj38.tsp"

    metadata, nodes = parse_tsp_file(b)

    d=distancia(0,1)
    # print(d)
    # sol = list(range(1,39))
    # print('sol', sol)
    # print(funcion_objetivo(sol))
    solucion = do_simulated_annealing(generar_ruta_inicial= vecindario_aleatorio, 
                    t_max=10000, 
                    t_min=0.001, 
                    max_iter=10000, 
                    deca = 0.95, 
                    vecindario = vecindario_2opt, 
                    distribucion = lambda delta, T: np.exp(-delta/T),
                    verbose=True)
    
    f_solucion = funcion_objetivo(solucion)
        


# def parallel_simulated_annealing(n_processes, generar_ruta_inicial, t_max, t_min, max_iter, deca=0.9, vecindario=None, distribucion=None):
#     """Ejecuta múltiples instancias de recocido simulado en paralelo."""
    
#     with mp.Pool(processes=n_processes) as pool:
#         results = pool.starmap(do_simulated_annealing, [
#             (generar_ruta_inicial, t_max, t_min, max_iter, deca, vecindario, distribucion, False)
#             for _ in range(n_processes)
#         ])
    
#     return results

# if __name__ == "__main__":
#     n_processes = 8 # Número de procesos en paralelo
#     puntos_path = "data/xqf131.tsp"
#     argentina = "data/ar9152.tsp"
#     metadata, nodes = parse_tsp_file(puntos_path)
    
#     resultados = parallel_simulated_annealing(
#         n_processes=n_processes,
#         generar_ruta_inicial=vecindario_aleatorio,  # Función de ejemplo
#         t_max=100,
#         t_min=0.1,
#         max_iter=100,
#         deca=0.9,
#         vecindario=vecindario_2opt,
#         distribucion=lambda delta, T: np.exp(delta/T)
#     )

#     print("Resultados finales:", resultados)

