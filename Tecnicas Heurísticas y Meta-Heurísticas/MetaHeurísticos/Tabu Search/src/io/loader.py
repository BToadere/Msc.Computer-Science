from pathlib import Path
from typing import List
from src.jssp.jssp_model import Operation, JSSP_DiGraph

def load_from_jsplib(instance_path: str) -> JSSP_DiGraph:
    """
    Lee un archivo de instancia en formato JSPLIB y crea un objeto JSSP_DiGraph.

    El formato esperado es:
    - La primera línea (despues de comentarios) contiene: num_jobs num_machines.
    - Las siguientes `num_jobs` líneas contienen la secuencia de operaciones para cada job.
    - Cada línea de job consiste en pares de (machine_id, duration).

    Args:
        instance_path (str): La ruta al archivo de la instancia (ej. "data/ft06.txt").

    Returns:
        JSSP_DiGraph: Una instancia del modelo del problema, lista para ser usada.
    
    Raises:
        FileNotFoundError: Si la ruta del archivo no es valida.
        ValueError: Si el contenido del archivo no tiene el formato esperado.
    """
    path = Path(instance_path)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontro el archivo de instancia en: {instance_path}")

    with path.open('r') as f:
        lines = [line.strip() for line in f if not line.startswith('#') and line.strip()]

    if not lines:
        raise ValueError("El archivo de instancia esta vacío o solo contiene comentarios.")

    try:
        num_jobs, num_machines = map(int, lines[0].split())
    except (ValueError, IndexError):
        raise ValueError("La primera línea del archivo debe contener 'num_jobs num_machines'.")

    job_lines = lines[1:num_jobs + 1]
    if len(job_lines) != num_jobs:
        raise ValueError(f"Se esperaban {num_jobs} líneas de jobs, pero se encontraron {len(job_lines)}.")
    
    all_operations: List[Operation] = []
    all_jobs: List[List[Operation]] = []
    op_id_counter = 1

    for job_idx, line in enumerate(job_lines):
        parts = list(map(int, line.split()))
        if len(parts) % 2 != 0:
            raise ValueError(f"La línea del job {job_idx + 1} tiene un numero impar de valores.")

        current_job_ops: List[Operation] = []
        for i in range(0, len(parts), 2):
            machine_id, duration = parts[i], parts[i+1]
            
            op = Operation(
                id=op_id_counter,
                job=job_idx + 1,
                machine=machine_id + 1,
                duration=duration
            )
            
            all_operations.append(op)
            current_job_ops.append(op)
            op_id_counter += 1
        
        all_jobs.append(current_job_ops)

    instance_name = path.stem

    return JSSP_DiGraph(
        name=instance_name,
        operations=all_operations,
        jobs=all_jobs
    )

