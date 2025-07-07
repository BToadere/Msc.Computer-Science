from typing import Dict, List, Tuple, Generator, Set, Union
import copy
from itertools import combinations
from collections import defaultdict
from src.jssp.jssp_model import JSSP_DiGraph, EdgeType

def generate_initial_schedule(instance: JSSP_DiGraph) -> Dict[int, List[int]]:
    """
    Genera un schedule inicial determinista.

    Para cada maquina, ordena las operaciones por su ID y crea una secuencia.
    Esta es una heurística simple para obtener una solucion factible de partida.

    Args:
        instance (JSSP_DiGraph): La instancia del problema.

    Returns:
        Dict[int, List[int]]: Un diccionario que representa el schedule,
        mapeando cada maquina a la lista de operaciones por orden.
    """
    ops_by_machine: Dict[int, List[int]] = {m: [] for m in range(1, instance.n_machines + 1)}

    # Agrupar operaciones por maquina
    for op in instance.operations:
        ops_by_machine[op.machine].append(op.id)
    
    return ops_by_machine

def generate_initial_schedule_bkp(instance: JSSP_DiGraph) -> Dict[int, List[Tuple[int, int]]]:
    """
    Genera un schedule inicial determinista en formato de aristas disyuntivas.

    Para cada máquina, crea una secuencia lineal de operaciones (ordenadas por ID
    para asegurar determinismo) y luego convierte esa secuencia en una lista
    de arcos disyuntivos (u, v) que la representan.

    Este formato de salida es una lista de tuplas (arcos) por máquina, que
    define explícitamente las precedencias en la solución inicial.

    Args:
        instance (JSSP_DiGraph): La instancia del problema.

    Returns:
        Dict[int, List[Tuple[int, int]]]: Un diccionario que mapea cada ID de
        máquina a una lista de tuplas (arcos disyuntivos) que forman una
        secuencia factible.
    """
    ops_by_machine = defaultdict(list)
    for op in instance.operations:
        ops_by_machine[op.machine].append(op.id)

    initial_schedule: Dict[int, List[Tuple[int, int]]] = {}

    for machine_id, op_ids in ops_by_machine.items():
        op_ids.sort()
        arcs = []
        for i in range(len(op_ids) - 1):
            u = op_ids[i]
            v = op_ids[i+1]
            arcs.append((u, v))
        
        initial_schedule[machine_id] = arcs
        
    return initial_schedule

def apply_swap_move_bkp(
    current_schedule: Dict[int, List[Tuple[int, int]]], 
    move: Tuple[int, int]
) -> Dict[int, List[Tuple[int, int]]]:
    """
    Aplica un movimiento de swap a un schedule y devuelve el NUEVO schedule.
    Funciona para operaciones adyacentes y no adyacentes.
    
    Args:
        current_schedule: El schedule actual
        move: Tupla (u, v) a ser invertida a (v, u)
        
    Returns:
        Un nuevo schedule con el movimiento aplicado
    """
    u, v = move
    new_schedule = copy.deepcopy(current_schedule)
    
    for machine, operations in new_schedule.items():
        if (u, v) in operations:
            index = operations.index((u, v))
            operations[index] = (v, u)
            break
    
    return new_schedule

def apply_swap_move(
    current_schedule: Dict[int, List[int]], 
    move: Tuple[int, int]
) -> Dict[int, List[int]]:
    """
    Aplica un movimiento de swap a un schedule y devuelve el NUEVO schedule.
    Funciona para operaciones adyacentes y no adyacentes.
    """
    u, v = move
    # Create a new schedule by dictionary comprehension
    new_schedule = {machine_id: list(ops) for machine_id, ops in current_schedule.items()}
    
    for machine, operations in new_schedule.items():
        for i in range(len(operations) - 1):
            # Check if u and v are adjacent in the current operations list
            if operations[i] == u and operations[i + 1] == v:
                # Swap them
                operations[i], operations[i + 1] = operations[i + 1], operations[i]
                return new_schedule
            elif operations[i] == v and operations[i + 1] == u:
                # Swap them
                operations[i], operations[i + 1] = operations[i + 1], operations[i]
                return new_schedule

def generate_taillard_neighborhood_bkp(
    current_schedule: Dict[int, List[Tuple[int, int]]], 
    instance: JSSP_DiGraph
) -> Generator[Tuple[Tuple[int, int], Dict[int, List[Tuple[int, int]]]]]:
    """
    Genera el vecindario N1 de Taillard, basado en operaciones críticas conectadas por aristas disyuntivas.

    Esta funcion identifica las operaciones en el camino crítico y devuelve pares de operaciones
    adyacentes que estan conectadas por aristas disyuntivas, como posibles movimientos.

    Args:
        current_schedule: El schedule actual
        instance (JSSP_DiGraph): La instancia del problema, que debe haber sido
                                 evaluada con una solucion (`load_solution`).

    Yields:
        Generator: Un generador de tuplas (move, neighbor_schedule) donde:
            - move: Tupla (u, v) que representa operaciones críticas conectadas por una arista disyuntiva
            - neighbor_schedule: El nuevo schedule resultante de aplicar el movimiento
    """
    
    critical_ops = instance.get_critical_operations()
    
    # Examinar todas las aristas disyuntivas en el grafo
    for u, v, edge_data in list(instance.G.edges(data=True)):
        # Verificar si es una arista disyuntiva
        if edge_data.get("type") == "disjunctive":
            # Verificar si ambos nodos estan en el camino crítico
            if u in critical_ops and v in critical_ops:
                # move = (u, v)
                # neighbor_schedule = apply_swap_move(current_schedule, move)
                # yield (move, neighbor_schedule)
                # # print(f"Encontarda arista disyuntiva entre {u} y {v} en el camino crítico.")
                # # Verificar la condicion de tension para confirmar que es un arco crítico
                r_u = instance.r_values[u]
                d_u = instance.G.nodes[u]['duration']
                r_v = instance.r_values[v]
                
                if r_u + d_u == r_v:
                    move = (u, v)
                    neighbor_schedule = apply_swap_move(current_schedule, move)
                    yield (move, neighbor_schedule)
                    
def generate_laarhoven_neighborhood(
    current_schedule: Dict[int, List[int]], 
    instance: JSSP_DiGraph
) -> Generator[Tuple[Tuple[int, int], Dict[int, List[Tuple[int, int]]]]]:
    """
    Genera el vecindario N1 de Taillard, basado en operaciones críticas conectadas por aristas disyuntivas.

    Esta funcion identifica las operaciones en el camino crítico y devuelve pares de operaciones
    adyacentes que estan conectadas por aristas disyuntivas, como posibles movimientos.

    Args:
        current_schedule: El schedule actual
        instance (JSSP_DiGraph): La instancia del problema, que debe haber sido
                                 evaluada con una solucion (`load_solution`).

    Yields:
        Generator: Un generador de tuplas (move, neighbor_schedule) donde:
            - move: Tupla (u, v) que representa operaciones críticas conectadas por una arista disyuntiva
            - neighbor_schedule: El nuevo schedule resultante de aplicar el movimiento
    """
    
    critical_ops = instance.get_critical_operations()
    for machine, operations in current_schedule.items():
        for i in range(len(operations) - 1):
            u = operations[i]
            v = operations[i + 1]
            if u in critical_ops and v in critical_ops:
                # move = (u, v)
                # neighbor_schedule = apply_swap_move(current_schedule, move)
                # yield (move, neighbor_schedule)
                # # print(f"Encontarda arista disyuntiva entre {u} y {v} en el camino crítico.")
                # # Verificar condicion de tension para confirmar que es un arco crítico
                r_u = instance.r_values[u]
                d_u = instance.G.nodes[u]['duration']
                r_v = instance.r_values[v]
                
                if r_u + d_u == r_v:
                    move = (u, v)
                    neighbor_schedule = apply_swap_move(current_schedule, move)
                    yield (move, neighbor_schedule)
