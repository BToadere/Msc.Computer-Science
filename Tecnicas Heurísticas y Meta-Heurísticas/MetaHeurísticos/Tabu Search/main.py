from src.io.loader import load_from_jsplib 
# from src.solver.neighborhood import generate_initial_schedule, generate_taillard_neighborhood, apply_swap_move
from src.solver.tabu_search import do_tabu_search, TabuList, LongTermMemory
from src.solver.neighborhood import generate_initial_schedule, generate_taillard_neighborhood #, generate_insertion_neighborhood, generate_generalized_swap_neighborhood
from src.objectives.functions import makespan
from src.jssp.jssp_model import JSSP_DiGraph

from pathlib import Path
import json

def calculate_lower_bound(instance: JSSP_DiGraph) -> int:
    """
    Calcula una cota inferior simple para el makespan.
    Esta cota se basa en la carga maxima de cualquier maquina (one-machine bound).
    """
    # Justificacion: Ninguna solucion puede ser mejor que el tiempo total de trabajo
    # requerido por la maquina mas ocupada, ya que no hay paralelismo dentro de una maquina.
    workloads = {m: 0 for m in range(1, instance.n_machines + 1)}
    for op in instance.operations:
        workloads[op.machine] += op.duration
    return max(workloads.values())

if __name__ == '__main__':

    base_path = Path(r"C:\Users\botoa\OneDrive - UNICAN - Estudiantes\_devs_\Tecnicas Heurísticas y Meta-Heurísticas\MetaHeurísticos\Tabu Search\JSPLIB")
    
    name = "bt322"
    # name = "ft06" 
    name = "yn2"
    # name = 'ta66'

    instance_file_path = base_path / 'instances' / name
    instance_data_path = base_path / 'instances.json'

    try:
        js = load_from_jsplib(str(instance_file_path))
        with open(instance_data_path) as f:
            data = json.load(f)
        instance_data = next((item for item in data if item["name"] == name), None)

    except (FileNotFoundError, ValueError) as e:
        print(f"Error al cargar la instancia: {e}")

    tabu_list=TabuList(n_jobs=js.n_jobs,n_machines=js.n_machines, n_operations=js.n_operations, p_refresh=0.05, p_length=0.2)
    lt_memory = LongTermMemory(n_operations=js.n_operations)
    max_iter = 10**6
    best_schedule, best_value = do_tabu_search(instance=js,
                                               initial_schedule_func=generate_initial_schedule,
                                               neighborhood_func=generate_taillard_neighborhood,
                                               objective_func=makespan,
                                               stop_criterion_func=lambda k:k>max_iter,
                                               tabu_list=tabu_list,
                                               long_term_memory=lt_memory,
                                               verbose=False
                                               )
    
    print(f"\n\nResultados para la instancia: {name}")
    print(f"-------------------------------------------------")
    print(f"Cota Inferior (carga de maquina): {calculate_lower_bound(js)}")
    print(f"Optimo Teorico Conocido:          {instance_data['optimum']}")
    print(f"Makespan Encontrado por TS:       {best_value}")
    print(f"-------------------------------------------------")

