import multiprocessing
import numpy as np
import time


# # Output código
#
# Número de procesadores: 8
# Calculo en Serie:
#  Población: 100000
#  Anchos: 4
#  Tiempo ejec: 3.9815497398376465 s
# Calculo en Paralelo:
#  Población: 100000
#  Anchos:16
#  Tiempo ejec: 5.961965560913086 s




def parzen_estim(muestra_x, punto_x, ancho):
    cuenta = 0
    for muestra in muestra_x:
        dif = np.abs((punto_x - muestra) / ancho)
        if np.all(dif<0.5):
             cuenta += 1
    return (ancho, (cuenta / muestra_x.shape[0]) / (ancho**len(punto_x)))


def serie(poblacion, x, anchos):
    return [parzen_estim(poblacion, x, a) for a in anchos]

def paralelo(procesos, poblacion, x, anchos):
    
    argumentos = [[poblacion, x, a] for a in anchos]
    proceso_paralelizacion = multiprocessing.Pool(procesos)
    result = proceso_paralelizacion.starmap(parzen_estim, argumentos)
    result.sort(key=lambda x: x[0])
    return result





if __name__ == '__main__':
    num_procs = multiprocessing.cpu_count()
    print(f'Número de procesadores: {num_procs}')   
    
    mu = 0
    sigma = 1
    poblacion = np.random.normal(mu,sigma,100000)
    x=[np.array([1])]
    anchos_serie=[np.array([x]) for x in range(1,5)]
    anchos_paralelo=[np.array([x]) for x in range(1,17)]
    
    t0 =time.time()
    var = serie(poblacion, x, anchos_serie)
    tf=time.time()
    print(f'Calculo en Serie:\n Población: {len(poblacion)}\n Anchos: {len(anchos_serie)}\n Tiempo ejec: {tf-t0} s')

    t0 =time.time()
    var = paralelo(num_procs,poblacion, x, anchos_paralelo)
    tf=time.time()
    print(f'Calculo en Paralelo:\n Población: {len(poblacion)}\n Anchos:{len(anchos_paralelo)}\n Tiempo ejec: {tf-t0} s')