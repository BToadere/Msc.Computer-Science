from typing import Dict, List, Tuple, Generator, Set, Union
import copy
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

def apply_swap_move(
    current_schedule: Dict[int, List[int]], 
    move: Tuple[int, int],
    instance: JSSP_DiGraph
) -> Dict[int, List[int]]:
    """
    Aplica un movimiento de swap a un schedule y devuelve el NUEVO schedule.
    Funciona para operaciones adyacentes y no adyacentes.
    """
    u, v = move
    # Create a new schedule by dictionary comprehension
    new_schedule = {machine_id: list(ops) for machine_id, ops in current_schedule.items()}
    
    machine_id = instance.G.nodes[u]['machine']
    seq = new_schedule[machine_id]
    
    idx_u, idx_v = seq.index(u), seq.index(v)
    seq[idx_u], seq[idx_v] = seq[idx_v], seq[idx_u]

    return new_schedule

def generate_taillard_neighborhood(
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
                # yield (u, v)
                # print(f"Encontarda arista disyuntiva entre {u} y {v} en el camino crítico.")
                # Verificar la condicion de tension para confirmar que es un arco crítico
                r_u = instance.r_values[u]
                d_u = instance.G.nodes[u]['duration']
                r_v = instance.r_values[v]
                
                if r_u + d_u == r_v:
                    move = (u, v)
                    neighbor_schedule = apply_swap_move(current_schedule, move, instance)
                    try:
                        instance.load_schedule(neighbor_schedule)
                        yield move, neighbor_schedule
                    except ValueError:
                        print(f"Movimiento {move} genera un ciclo, ignorando.")
                        continue
                    
