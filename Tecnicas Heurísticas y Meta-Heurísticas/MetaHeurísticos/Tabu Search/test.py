from src.io.loader import load_from_jsplib 
from src.io.drawer import draw_jssp_instance
from src.solver.neighborhood import generate_initial_schedule, generate_taillard_neighborhood, apply_swap_move
from src.jssp.jssp_model import JSSP_DiGraph, SOURCE_NODE, SINK_NODE

from pathlib import Path

if __name__ == "__main__":
    base_path = Path(r"C:\Users\botoa\OneDrive - UNICAN - Estudiantes\_devs_\Tecnicas Heurísticas y Meta-Heurísticas\MetaHeurísticos\Tabu Search\JSPLIB")
    
    name = "bt322" 
    # name = "ft06" 
    # name = "la01"

    instance_file_path = base_path / 'instances' / name
    instance_data_path = base_path / 'instances.json'

    try:
        js = load_from_jsplib(str(instance_file_path)) # Es buena practica pasar el string de la ruta

    except (FileNotFoundError, ValueError) as e:
        print(f"Error al cargar la instancia: {e}")

    initial_schedule = generate_initial_schedule(js)
    js.load_schedule(initial_schedule)


    print(js)

    print(js.r_values, js.q_values, js.get_critical_operations() , sep='\n')
    draw_jssp_instance(js)



