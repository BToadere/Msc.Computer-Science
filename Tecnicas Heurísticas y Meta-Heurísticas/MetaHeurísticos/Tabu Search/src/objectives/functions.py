from src.jssp.jssp_model import JSSP_DiGraph, SINK_NODE

def makespan(instance: JSSP_DiGraph) -> int:
    """
    Calcula el makespan (C_max) de una solucion.

    El makespan es el tiempo de finalizacion de la ultima operacion, que corresponde
    al camino mas largo desde el nodo SOURCE hasta el nodo SINK en el grafo disyuntivo.

    Args:
        instance (JSSP_DiGraph): Una instancia del problema que ya ha sido evaluada.

    Returns:
        int: El valor del makespan.
    
    Raises:
        KeyError: Si la instancia no ha sido evaluada y los valores `r_values` no existen.
    """
    if not instance.r_values:
        raise ValueError("La instancia debe ser evaluada con una solucion antes de calcular el makespan.")
    
    # El makespan es simplemente el valor r del nodo SINK.
    return instance.r_values[SINK_NODE]

