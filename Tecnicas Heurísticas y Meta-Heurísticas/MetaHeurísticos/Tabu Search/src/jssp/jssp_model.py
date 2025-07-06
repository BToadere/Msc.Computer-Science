import networkx as nx
from itertools import combinations
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

# Constantes y Estructuras de Datos Fundamentales

SOURCE_NODE = 0
SINK_NODE = -1

class EdgeType(Enum):
    """Define los tipos de aristas en el grafo disyuntivo."""
    CONJUNCTIVE = "conjunctive"
    DISJUNCTIVE = "disjunctive"

@dataclass
class Operation:
    """Representa una unica operacion con sus atributos."""
    id: int
    job: int
    machine: int
    duration: int

#  Clase Principal del Modelo JSSP 

class JSSP_DiGraph:
    """
    Representa el problema JSSP mediante un grafo disyuntivo.
    
    Esta clase encapsula la estructura del problema (operaciones, jobs, maquinas)
    y proporciona la funcionalidad para evaluar una solucion completa (un schedule).
    """

    def __init__(self, name: str, operations: List[Operation], jobs: List[List[Operation]]):
        """
        Constructor del modelo. Recibe los datos del problema ya procesados.
        
        Args:
            name (str): Nombre de la instancia (ej. "ft06").
            operations (List[Operation]): Lista plana de todas las operaciones.
            jobs (List[List[Operation]]): Lista de jobs, donde cada job es una lista de sus operaciones.
        """
        self.name = name
        self.operations = operations
        self.n_operations = len(operations)
        self.jobs = jobs
        self.n_jobs = len(jobs)
        self.n_machines = len({op.machine for op in operations})
        
        self.G = nx.DiGraph()
        self._build_base_graph()

        self.r_values: Dict[int, int] = {}
        self.q_values: Dict[int, int] = {}

    def _build_base_graph(self):
        """
        Construye el grafo base con nodos y aristas CONJUNTIVAS.
        Las aristas disyuntivas se añadiran al cargar una solucion específica.
        """
        # 1. Añadir todos los nodos al grafo
        self.G.add_node(SOURCE_NODE, duration=0, critical=True)
        self.G.add_node(SINK_NODE, duration=0, critical=True)
        for op in self.operations:
            self.G.add_node(op.id, machine=op.machine, duration=op.duration, job=op.job, critical=False)

        # 2. Añadir aristas conjuntivas (secuencia de operaciones de cada job)
        for job_ops in self.jobs:
            # Conectar source a la primera operacion del job
            self.G.add_edge(SOURCE_NODE, job_ops[0].id, type=EdgeType.CONJUNCTIVE.value)
            # Conectar operaciones consecutivas del mismo job
            for i in range(len(job_ops) - 1):
                self.G.add_edge(job_ops[i].id, job_ops[i+1].id, type=EdgeType.CONJUNCTIVE.value)
            # Conectar la ultima operacion del job al sink
            self.G.add_edge(job_ops[-1].id, SINK_NODE, type=EdgeType.CONJUNCTIVE.value)

        aux_dict = {}
        for op in self.operations:
            machine = op.machine
            if machine not in aux_dict:
                aux_dict[machine] = []
            aux_dict[machine].append(op.id)

        self._disjunctive_edges = {}
        for key, values in aux_dict.items():
            pairs = []
            # Todas las combinaciones de 2 elementos
            for a, b in combinations(values, 2):
                pairs.append((a, b))
                pairs.append((b, a))  # inverso
            self._disjunctive_edges[key] = pairs


    def load_schedule(self, schedule: Dict[int, List[int]]):
        """
        Configura el grafo para representar una solucion completa y la evalua.
        Este es el punto de entrada principal para analizar un schedule.

        Args:
            machine_schedule: Un diccionario {machine_id: [op1, op2, ...]} que define
                              el orden de las operaciones en cada maquina.
        
        Raises:
            ValueError: Si el schedule proporcionado crea un ciclo en el grafo.
        """
        self.current_schedule = schedule
        initial_arcs = {}
        for machine, seq in schedule.items():
            arcs = []
            for i in range(len(seq) - 1):
                arcs.append((seq[i], seq[i+1]))
            initial_arcs[machine] = arcs

        for machine, arcs in initial_arcs.items():
            for arc in arcs:
                if arc not in self._disjunctive_edges[machine]:
                    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Error: El arco {arc} no es valido para la maquina {machine} !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # 1. Limpiar las aristas disyuntivas de la solucion anterior
        edges_to_remove = [
            (u, v) for u, v, d in self.G.edges(data=True) 
            if d.get("type") == EdgeType.DISJUNCTIVE.value
        ]
        self.G.remove_edges_from(edges_to_remove)
        # 2. Añadir las nuevas aristas disyuntivas del schedule
        for machine, schedule_arcs in initial_arcs.items():
            for u, v in schedule_arcs:
                self.G.add_edge(u, v, type=EdgeType.DISJUNCTIVE.value)
        
        # 3. Validar que la solucion es factible (no tiene ciclos)
        if not nx.is_directed_acyclic_graph(self.G):
            raise ValueError(f"El schedule proporcionado es infactible ({schedule}).")

        # 4. Evaluar el estado del grafo con la nueva solucion
        self._compute_r()
        self._compute_q()
        self._mark_critical_operations()

    # def PJ(self, n_i: int) -> int:
    #     """
    #     Predecesor inmediato de la operacion n_i en su mismo job (arista conjuntiva).
    #     Devuelve SOURCE_NODE si n_i es la primera operacion del job.
    #     """
    #     preds = set(
    #         u for u in self.G.predecessors(n_i)
    #         if self.G[u][n_i]['type'] == EdgeType.CONJUNCTIVE.value
    #     )
    #     return preds

    # def SJ(self, n_i: int) -> int:
    #     """
    #     Sucesor inmediato de la operacion n_i en su mismo job (arista conjuntiva).
    #     Devuelve SINK_NODE si n_i es la ultima operacion del job.
    #     """
    #     succs = set(
    #         v for v in self.G.successors(n_i)
    #         if self.G[n_i][v]['type'] == EdgeType.CONJUNCTIVE.value
    #     )
    #     return succs

    # def PM(self, n_i: int) -> int:
    #     """
    #     Predecesor inmediato de la operacion n_i en la misma maquina (arista disyuntiva orientada).
    #     Devuelve SOURCE_NODE si n_i es la primera operacion en esa maquina.
    #     """
    #     preds = set(
    #         u for u in self.G.predecessors(n_i)
    #         if self.G[u][n_i]['type'] == EdgeType.DISJUNCTIVE.value
    #     )
    #     return preds

    # def SM(self, n_i: int) -> int:
    #     """
    #     Sucesor inmediato de la operacion n_i en la misma maquina (arista disyuntiva orientada).
    #     Devuelve SINK_NODE si n_i es la ultima operacion en esa maquina.
    #     """
    #     succs = set(
    #         v for v in self.G.successors(n_i)
    #         if self.G[n_i][v]['type'] == EdgeType.DISJUNCTIVE.value
    #     )
    #     return succs

    def _compute_r(self):
        """
        Calcula r_i para cada nodo i (camino mas largo desde el source).
        """
        self.r_values = {node: 0 for node in self.G.nodes}

        for i in nx.topological_sort(self.G):
            if i == SOURCE_NODE:
                continue
            
            max_pred_completion_time = max(
                (self.r_values[k] + self.G.nodes[k]['duration'] for k in self.G.predecessors(i))
            )
            self.r_values[i] = max_pred_completion_time
        
    def _compute_q(self):
        """
        Calcula q_i para cada nodo i (camino mas largo desde i hasta el sink).
        """
        self.q_values = {node: self.G.nodes[node]['duration'] for node in self.G.nodes}

        for i in reversed(list(nx.topological_sort(self.G))):
            if i == SINK_NODE:
                continue

            max_succ_q_value = max(
                (self.q_values[k] for k in self.G.successors(i))
            )
            self.q_values[i] += max_succ_q_value

    def _mark_critical_operations(self):
        """Marca las operaciones que pertenecen a un camino crítico."""
        # El makespan es el tiempo de inicio del nodo SINK.
        makespan = self.r_values.get(SINK_NODE)

        for op_id in self.G.nodes:
            if op_id in (SOURCE_NODE, SINK_NODE): 
                continue
        
            # Una operacion es crítica si r_i + q_i es igual al makespan total.
            is_critical = (self.r_values[op_id] + self.q_values[op_id] == makespan)
            self.G.nodes[op_id]['critical'] = is_critical
    
    def get_critical_operations(self) -> List[int]:
        """Devuelve una lista de las operaciones críticas de la solucion actual."""
        return {n:d for n, d in self.G.nodes(data=True) if d.get("critical") == True}



    # #  Metodos de Ayuda y Depuracion 

    def __repr__(self):
        """Return a string representation of the JSSP problem for debugging."""
        problem_info = (
            f"JSSP_DiGraph('{self.name}')\n"
            f"  Jobs: {self.n_jobs}\n"
            f"  Machines: {self.n_machines}\n"
            f"  Operations: {len(self.operations)}\n"
            f"  Graph: {self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges\n"
        )
        
        # Add information about operations
        problem_info += "  Operation details:\n"
        for job_id, job_ops in enumerate(self.jobs):
            problem_info += f"    Job {job_id}: "
            problem_info += " -> ".join([f"(M{op.machine}:{op.duration})" for op in job_ops])
            problem_info += "\n"
        
        # Add machine sequences based on disjunctive edges
        problem_info += "  Machine sequences:\n"
        for machine in range(self.n_machines):
            machine_ops = [op.id for op in self.operations if op.machine == machine]
            if not machine_ops:
                continue
            
            # Build sequence using disjunctive edges
            sequence = []
            edges = [(u, v) for u, v, d in self.G.edges(data=True) 
                if d.get("type") == EdgeType.DISJUNCTIVE.value and 
                u in machine_ops and v in machine_ops]
            
            if edges:
            # Find the first operation (one with no disjunctive predecessors)
                first_op = next((op for op in machine_ops 
                    if not any(v == op for u, v in edges)), machine_ops[0])
            
                sequence = [first_op]
                while len(sequence) < len(machine_ops):
                    for u, v in edges:
                        if u == sequence[-1] and v not in sequence:
                            sequence.append(v)
                            break
                
                # Format the sequence
                problem_info += f"    Machine {machine}: "
                op_details = []
                for op_id in sequence:
                    job_id = self.G.nodes[op_id].get('job')
                    duration = self.G.nodes[op_id].get('duration')
                    op_details.append(f"(J{job_id}:{duration})")
                problem_info += " -> ".join(op_details)
                problem_info += "\n"
            else:
                problem_info += f"    Machine {machine}: No sequence defined\n"
        
        # Add information about machine total durations
        machine_durations = {}
        for op in self.operations:
            machine_durations[op.machine] = machine_durations.get(op.machine, 0) + op.duration
        
        problem_info += "  Machine workloads:\n"
        for machine, duration in sorted(machine_durations.items()):
            problem_info += f"    Machine {machine}: {duration} time units\n"
        
        makespan = self.r_values.get(SINK_NODE, None)
        if makespan is not None:
            problem_info += f"  Current makespan: {makespan}\n"
            critical_ops = len(self.get_critical_operations())
            problem_info += f"  Critical operations: {critical_ops}\n"
        
        return problem_info