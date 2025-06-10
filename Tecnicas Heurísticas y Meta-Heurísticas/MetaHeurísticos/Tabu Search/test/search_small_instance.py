from pathlib import Path
import json

def list_small_instances(base_path: str, limit: int = 10):
    """
    List the smallest JSSP instances sorted by size (jobs × machines)
    Args:
        base_path: Path to JSPLIB directory
        limit: Number of instances to show
    """
    # Load instances file
    inst_file = Path(base_path) / "instances.json"
    with inst_file.open() as f:
        instances = json.load(f)
    
    # Add size metric and sort
    for inst in instances:
        inst['size'] = inst['jobs'] * inst['machines']
    
    sorted_instances = sorted(instances, key=lambda x: x['size'])
    
    # Print results
    print(f"Smallest {limit} instances:")
    print(f"{'Name':<10} {'Jobs':>4} {'Machines':>9} {'Size':>6} {'Optimum':>9}")
    print("-" * 45)
    
    for inst in sorted_instances[:limit]:
        print(f"{inst['name']:<10} {inst['jobs']:>4} {inst['machines']:>9} {inst['size']:>6} {inst['optimum']:>9}")

if __name__ == "__main__":
    base = r"C:\Users\botoa\OneDrive - UNICAN - Estudiantes\_devs_\Tecnicas Heurísticas y Meta-Heurísticas\MetaHeurísticos\Tabu Search\JSPLIB"
    list_small_instances(base)