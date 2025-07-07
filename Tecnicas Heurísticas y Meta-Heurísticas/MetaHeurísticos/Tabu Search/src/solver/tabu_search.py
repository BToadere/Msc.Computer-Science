from src.jssp.jssp_model import JSSP_DiGraph
from typing import Callable, Tuple
from collections import defaultdict

import random


class TabuList:
    """
    Implementa una lista tabu dinamica y autocontenida segun Taillard (1994).
    - Usa la interpretacion estandar: swap(u,v) prohíbe el movimiento inverso (v,u).
    - Gestiona automaticamente el refresco del rango de la tenencia tabu.
    """
    def __init__(self, n_jobs: int, n_machines: int, n_operations: int, p_refresh: float = 0.05, p_length: float = 0.2):
        self.n = n_jobs
        self.m = n_machines
        self.N = n_operations
        self.p_refresh = p_refresh
        self.p_length = p_length

        # Diccionario que mapea op_id -> iteracion hasta la que es tabu.
        self.tabu_until = defaultdict(int)
        
        # Inicializamos los parametros de tenencia por primera vez.
        self._update_tenure_range()

    def _update_tenure_range(self):
        """
        Metodo privado para (re)calcular L_base, L_min, L_max y el intervalo de refresco.
        Esta funcion se llama al inicio y periodicamente durante la busqueda.
        """
        # Usamos la formula simple como base. Puedes cambiarla por la compleja si quieres.
        self.L_base = round((self.n + self.m) / 2)
        self.L_min = int((1.0 - self.p_length) * self.L_base)
        self.L_max = int((1.0 + self.p_length) * self.L_base)
        
        if self.L_min < 1: self.L_min = 1
        if self.L_max < self.L_min: self.L_max = self.L_min
            
        # Calculamos el numero de iteraciones hasta el proximo refresco.
        self.refresh_interval = int(self.L_max * (1.0 + self.p_refresh))
        self.iter_since_last_change = 0 # Reseteamos el contador
        

    def push(self, move: Tuple[int, int], current_iteration: int):
        """
        Registra un movimiento como tabu y comprueba si es necesario refrescar la tenencia.
        """
        u, v = move
        tenure = random.randint(self.L_min, self.L_max)
        # cierto acoplamiento con el movmiento swap
        self.tabu_until[(v,u)] = current_iteration + tenure

        self.iter_since_last_change += 1
        if self.iter_since_last_change >= self.refresh_interval:
            self._update_tenure_range()

    def is_tabu(self, move: Tuple[int, int], current_iteration: int) -> bool:
        """
        Comprueba si un movimiento esta actualmente prohibido.

        Args:
            move (Tuple[int, int]): El movimiento (u, v) a evaluar.
            current_iteration (int): El numero de la iteracion actual (k).

        Returns:
            bool: True si el movimiento es tabu, False en caso contrario.
        """
        
        return current_iteration < self.tabu_until[move]

    def __repr__(self):

        output = ["TabuList Status:"]
        output.append(f"  Tenure range: [{self.L_min}, {self.L_max}], Base: {self.L_base}")
        output.append(f"  Refresh: {self.iter_since_last_change}/{self.refresh_interval} iterations")
        
        # Show active tabu moves
        if self.tabu_until:
           output.append(f"  {dict(self.tabu_until)}")
        else:
            output.append("  No active tabu moves")
            
        return "\n".join(output)
    


class LongTermMemory:
    def __init__(self, n_operations: int):
        self.freq = defaultdict(int)       # f(b): frecuencia con la que b ha sido retrasada
        self.N = n_operations              # numero total de operaciones
        self.P = 0.0                       # penalizacion dinamica
        self.delta_max = 0               # Δ_k^max
        self.prev_value = None         # value anterior

    def push(self, mov: Tuple[int, int], current_Cmax:int):

        self._update_frequency(mov)
        self._update_delta(current_Cmax)
        

    def _update_frequency(self, mov: Tuple[int,int]):
        """
        Si b ha sido desplazada hacia atras en su maquina respecto a su posicion anterior,
        se incrementa f(b).
        """
        self.freq[mov] += 1

    def _update_delta(self, current_value: int):
        """
        Calcula el incremento de value desde la solucion anterior
        y actualiza delta_max si el incremento es mayor al observado hasta ahora.
        """
        if self.prev_value is not None:
            delta = current_value - self.prev_value
            if delta > self.delta_max:
                self.delta_max = delta
                self._update_P()
        self.prev_value = current_value  # actualizar siempre

    def _update_P(self):
        self.P = 0.5 * self.delta_max * (self.N)**(0.5)

    def get_penalty(self, mov: Tuple[int, int]) -> float:
        """
        Devuelve la penalizacion asociada a empujar hacia atras a b.
        """
        return self.P * self.freq[mov]

    def __repr__(self):
        output = ["LongTermMemory Status:"]
        output.append(f"  Frequency: {dict(self.freq)}")
        output.append(f"  Delta max: {self.delta_max}, P: {self.P}")
        output.append(f"  Previous value: {self.prev_value}")
        return "\n".join(output)    




def do_tabu_search(
    instance: JSSP_DiGraph, 
    initial_schedule_func: Callable, 
    neighborhood_func: Callable,
    objective_func: Callable,
    stop_criterion_func: Callable, 
    tabu_list: TabuList, 
    long_term_memory: LongTermMemory,
    verbose: bool = False
):
    # 1. Solucion Inicial
    current_schedule = initial_schedule_func(instance)
    instance.load_schedule(current_schedule)
    current_value = objective_func(instance)
    
    best_schedule = current_schedule
    best_value = current_value
    
    # Inicializar memoria a largo plazo
    long_term_memory.prev_value = current_value
    
    k = 0
    if verbose:
        print(f"Iteracion {k:4}: Valor inicial = {best_value}")

    while not stop_criterion_func(k):
        if verbose:
            print(f"\n--- Iteracion {k:4} ---")
        k += 1
        
        # Generar vecinos desde la solucion actual (la instancia ya esta evaluada)
        best_neighbor_move: Tuple[int, int] = None
        best_neighbor_value = float('inf')
        best_neighbor_eval = float('inf')

        for move, neighbor_schedule in neighborhood_func(current_schedule,instance):
            # Carga la solución
            try:
                instance.load_schedule(neighbor_schedule)
            except ValueError:
                continue
            
            if verbose:
                print(f"Evaluando movimiento: {move}")
            neighbor_value = objective_func(instance)
            
            # Criterio Tabu y de Aspiracion
            if tabu_list.is_tabu(move, k) and neighbor_value >= best_value:
                if verbose:
                    print(f"Movimiento {move} es tabu. Valor vecino: {neighbor_value} (actual: {current_value}) (best: {best_value})")
                continue

            # Aplicacion Memoria a Largo Plazo
            penalty = long_term_memory.get_penalty(move)
            neighbor_evaluation = neighbor_value + penalty

            if neighbor_evaluation < best_neighbor_eval:
                best_neighbor_eval = neighbor_evaluation
                best_neighbor_value = neighbor_value
                best_neighbor_move = move
                best_neighbor_schedule = neighbor_schedule

        if best_neighbor_move is None:
            print("Busqueda estancada: no se encontraron movimientos validos. Terminando.")
            break

        # 5. Mover a la siguiente solucion
        current_schedule = best_neighbor_schedule
        current_value = best_neighbor_value
        instance.load_schedule(current_schedule)
        
        # Actualizar mejor solucion global
        if current_value < best_value:
            best_schedule = current_schedule
            best_value = current_value
            if verbose:
                print(f"Iteracion {k:8}: ¡NUEVO MEJOR! -> {best_value} aplicando {best_neighbor_move}")
        
        # 6. Actualizar Memorias
        tabu_list.push(move=best_neighbor_move, current_iteration=k)
        long_term_memory.push(best_neighbor_move, current_value)
        
        if verbose:
            print(tabu_list)
            print(long_term_memory)
        if k % 50 == 0:
            print(f"Iteracion {k:4}: value actual = {current_value} (Mejor global = {best_value})")

    if verbose:
        print(f"\n--- Busqueda Tabu Finalizada en {k} itraciones ---")
        print(f"Mejor value encontrado: {best_value}")
    return best_schedule, best_value
