from pathlib import Path
import json
import networkx as nx
import matplotlib.pyplot as plt
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Generator


SOURCE_NODE = 0
SINK_NODE   = -1

class EdgeType(Enum):
    CONJ = "conjunctive"
    DISJ = "disjunctive"

@dataclass
class Operation:
    id: int
    job: int
    machine: int
    duration: int

class JSSP_DiGraph:

    def draw(self, figsize=(8, 5)):
        def _compute_layout(self) -> Dict[int, Tuple[float, float]]:
            pos: Dict[int, Tuple[float, float]] = {}
            y_gap, x_gap = 2, 1
            # respetar distribución original: idx por operación, -máquina en y
            for job_id, job_ops in enumerate(self.jobs, start=1):
                for idx, op in enumerate(job_ops):
                    pos[op.id] = (idx * x_gap, -job_id * y_gap)
            # centro en y para source y sink
            if pos:
                ys = [y for _, y in pos.values()]
                center_y = (max(ys) + min(ys)) / 2
            else:
                center_y = 0
            min_x = min(x for x, _ in pos.values())
            max_x = max(x for x, _ in pos.values())
            pos[SOURCE_NODE] = (min_x - 1.5 * x_gap, center_y)
            pos[SINK_NODE]   = (max_x + 1.5 * x_gap, center_y)
            return pos
        pos = _compute_layout(self)
        
        plt.figure(figsize=figsize)
        nx.draw_networkx_nodes(self.G, pos, node_color='skyblue', node_size=350)
        # disyuntivas
        disj = [(u, v) for u, v, d in self.G.edges(data=True)
                if d['type'] == EdgeType.DISJ.value]
        nx.draw_networkx_edges(self.G, pos, edgelist=disj,
                       style=(0, (4, 15)), edge_color='blue', width=0.5)
        # conjuntivas
        conj = [(u, v) for u, v, d in self.G.edges(data=True)
                if d['type'] == EdgeType.CONJ.value]
        nx.draw_networkx_edges(self.G, pos, edgelist=conj,
                               edge_color='gray', arrows=True)
        # # Añadir pesos a las aristas
        # edge_labels = {(u, v): self.G.nodes[u]['duration'] for u, v, d in self.G.edges(data=True)
        #                if self.G.nodes[u]['duration']}
        # nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels)
        
        nx.draw_networkx_labels(self.G, pos)
        plt.title(f"Grafo JSSP: {self.name}")
        plt.axis('off')
        plt.show()

    def print_attributes(self):
        print("JobShopGraph Attributes:")
        print(f"Name: {self.name}")
        print(f"Number of Jobs: {self.n_jobs}")
        print(f"Number of Machines: {self.n_machines}")
        print(f"Base Path: {self.base_path}")
        print(f"Total Operations: {self.total_ops}")
        print("Operations:")
        for op in self.operations:
            print(f"  Operation ID: {op.id}, Job ID: {op.job}, Machine: {op.machine}, Duration: {op.duration}")
        print("Jobs:")
        for job_id, job_ops in enumerate(self.jobs, start=1):
            print(f"  Job {job_id}: {[op.id for op in job_ops]}")
        print("Graph Nodes:")
        print(self.G.nodes(data=True))
        print("Graph Edges:")
        print(self.G.edges(data=True))
        print("Disjunctive Arcs:")
        for machine, arcs in self.disjunctive_arcs.items():
            print(f"  Machine {machine}: {arcs}")
    
    def __init__(self, name: str, jobs: int, machines: int, base_path: str):
        self.name       = name
        self.n_jobs     = jobs
        self.n_machines = machines
        self.base_path  = Path(base_path)
        
        self.operations: List[Operation] = []
        self.jobs: List[List[Operation]] = []
        self._load_instance()
        
        self.G = nx.DiGraph()
        self.disjunctive_arcs: Dict[int, List[Tuple[int, int]]]
        self._build_graph()

    def _load_instance(self):
        inst_file = self.base_path / "instances.json"
        with inst_file.open() as f:
            instances = json.load(f)
        inst = next(i for i in instances
                    if i["name"] == self.name
                    and i["jobs"] == self.n_jobs
                    and i["machines"] == self.n_machines)
        path_txt = self.base_path / inst["path"]
        self.optimum = inst["optimum"]
        with path_txt.open() as f:
            lines = [L for L in f if not L.startswith("#")][1:]
        op_id = 0
        for job_id, line in enumerate(lines, start=1):
            datos = list(map(int, line.split()))
            job_ops: List[Operation] = []
            for k in range(0, len(datos), 2):
                op_id += 1
                op = Operation(
                    id=op_id,
                    job=job_id,
                    machine=datos[k],
                    duration=datos[k+1]
                )
                self.operations.append(op)
                job_ops.append(op)
            self.jobs.append(job_ops)
        self.total_ops = op_id

    def _build_graph(self):

        def _add_nodes(self):
            self.G.add_node(SOURCE_NODE, machine=None, duration=0, job=None, critical=False)
            self.G.add_node(SINK_NODE,   machine=None, duration=0, job=None, critical=False)
            for op in self.operations:
                self.G.add_node(op.id, machine=op.machine, duration=op.duration, job=op.job, critical=False)

        def _add_conjunctive_edges(self):
            for job_ops in self.jobs:
                # source -> primera
                self.G.add_edge(SOURCE_NODE, job_ops[0].id,
                                type=EdgeType.CONJ.value)
                # secuencia
                for a, b in zip(job_ops, job_ops[1:]):
                    self.G.add_edge(a.id, b.id,
                                    type=EdgeType.CONJ.value)
                # última -> sink
                self.G.add_edge(job_ops[-1].id, SINK_NODE,
                                type=EdgeType.CONJ.value)


        def _add_disjunctive_edges(self):
            """Guardar disyuntivas agrupadas por máquina."""
            self.disjunctive_arcs = {}
            by_machine: List[Tuple[int, int]] = {}
            for op in self.operations:
                by_machine.setdefault(op.machine, []).append(op.id)
            for machine, ops in by_machine.items():
                self.disjunctive_arcs[machine] = []
                for i in range(len(ops)):
                    for j in range(i+1, len(ops)):
                        u, v = ops[i], ops[j]
                        self.disjunctive_arcs[machine].extend([(u, v),(v,u)])


        _add_nodes(self)
        _add_conjunctive_edges(self)
        _add_disjunctive_edges(self)

    def function(self) -> int:
        return self.r_values[SINK_NODE]
    
    def load_disjunctive_arcs(self, disjunctive_dict: Dict[int, List[Tuple[int, int]]]) -> None:
        """
        Evalúa una solución añadiendo aristas disyuntivas al grafo según el diccionario dado
        Args:
            disjunctive_dict: Diccionario que mapea máquinas a lista de tuplas (u,v) de aristas dirigidas
        """
        # Primero limpiamos las aristas disyuntivas existentes
        edges_to_remove = [(u, v) for u, v, d in self.G.edges(data=True)
                        if d.get('type') == EdgeType.DISJ.value]
        self.G.remove_edges_from(edges_to_remove)
        
        # Añadimos las nuevas aristas disyuntivas
        for machine, arcs in disjunctive_dict.items():
            for u, v in arcs:
                self.G.add_edge(u, v, 
                            type=EdgeType.DISJ.value)
        

        # Verificamos que el grafo resultante es acíclico
        if not nx.is_directed_acyclic_graph(self.G):
            print("❌ Solución no factible: el grafo tiene ciclos.")

        self.compute_r()
        self.compute_q()
        self.mark_critical_operations()
    
    def PJ(self, n_i: int) -> int:
        """
        Predecesor inmediato de la operación n_i en su mismo job (arista conjuntiva).
        Devuelve SOURCE_NODE si n_i es la primera operación del job.
        """
        preds = set(
            u for u in self.G.predecessors(n_i)
            if self.G[u][n_i]['type'] == EdgeType.CONJ.value
        )
        return preds

    def SJ(self, n_i: int) -> int:
        """
        Sucesor inmediato de la operación n_i en su mismo job (arista conjuntiva).
        Devuelve SINK_NODE si n_i es la última operación del job.
        """
        succs = set(
            v for v in self.G.successors(n_i)
            if self.G[n_i][v]['type'] == EdgeType.CONJ.value
        )
        return succs

    def PM(self, n_i: int) -> int:
        """
        Predecesor inmediato de la operación n_i en la misma máquina (arista disyuntiva orientada).
        Devuelve SOURCE_NODE si n_i es la primera operación en esa máquina.
        """
        preds = set(
            u for u in self.G.predecessors(n_i)
            if self.G[u][n_i]['type'] == EdgeType.DISJ.value
        )
        return preds

    def SM(self, n_i: int) -> int:
        """
        Sucesor inmediato de la operación n_i en la misma máquina (arista disyuntiva orientada).
        Devuelve SINK_NODE si n_i es la última operación en esa máquina.
        """
        succs = set(
            v for v in self.G.successors(n_i)
            if self.G[n_i][v]['type'] == EdgeType.DISJ.value
        )
        return succs

    def compute_r(self) -> Dict[int, int]:
        """
        Calcula r_i para cada nodo i:
        r[source] = 0
        r_i = max(r[PJ(i)] + d[PJ(i)], r[PM(i)] + d[PM(i)])
        """
        r = {n: 0 for n in self.G.nodes()}
        for i in nx.topological_sort(self.G):
            preds = self.PJ(i).union(self.PM(i))
            if not preds:
                continue
            r[i] = max(r[j] + self.G.nodes[j]['duration'] for j in preds)
        self.r_values = r

    def compute_q(self) -> Dict[int, int]:
        """
        Calcula q_i para cada nodo i:
        q[sink] = 0
        q_i = d[i] + max(q[SJ(i)], q[SM(i)])
        """
        q = {n: 0 for n in self.G.nodes()}
        for i in reversed(list(nx.topological_sort(self.G))):
            sucs = self.SM(i).union(self.SJ(i))
            if not sucs:
                continue
            q[i] = max(q[j] for j in sucs) + self.G.nodes[i]['duration']
        self.q_values = q

    def mark_critical_operations(self) -> List[int]:
        """Devuelve una lista de IDs de operaciones críticas"""
        for node_id in self.G.nodes:
            if node_id in (SOURCE_NODE, SINK_NODE):
                continue
            if self.r_values[node_id] + self.q_values[node_id] == self.r_values[SINK_NODE]:
                self.G.nodes[node_id]["critical"] = True

    def load_neighbor(self, vecino:Tuple[int, int]):
        """
        Invierte una arista disyuntiva (a → b) a (b → a).
        Precondición: la arista (a, b) debe existir y ser disyuntiva.
        """
        a,b =vecino

        if not self.G.has_edge(a, b):
            raise ValueError(f"No existe la arista ({a}, {b}) en el grafo.")
        if self.G[a][b]['type'] != EdgeType.DISJ.value:
            raise ValueError(f"La arista ({a}, {b}) no es disyuntiva.")

        # Eliminar (a → b)
        self.G.remove_edge(a, b)

        # Añadir (b → a) con los mismos atributos
        self.G.add_edge(b, a, type=EdgeType.DISJ.value)
        self.draw()
        # Recompute all values
        self.compute_r()
        self.compute_q()
        self.mark_critical_operations()

    def _compute_neighbor(self, a: int, b: int):
        """
        Calcula r' y q' para las operaciones a y b tras invertir (a → b).
        Asume que el grafo ya ha sido modificado (ya está (b → a)).
        """
        r = self.r_values.copy()
        q = self.q_values.copy()
        d = lambda i: self.G.nodes[i]['duration']

        # Recalcular r_b'
        pred_job_b = next(iter(self.PJ(b)), SOURCE_NODE)
        pred_mach_b = next(iter(self.PM(b)), SOURCE_NODE)
        r[b] = max(r[pred_job_b] + d(pred_job_b),
                r[pred_mach_b] + d(pred_mach_b))

        # r_a' depende de r_b'
        pred_job_a = next(iter(self.PJ(a)), SOURCE_NODE)
        r[a] = max(r[b] + d(b),
                r[pred_job_a] + d(pred_job_a))

        # Recalcular q_a'
        succ_job_a = next(iter(self.SJ(a)), SINK_NODE)
        succ_mach_a = next(iter(self.SM(a)), SINK_NODE)
        q[a] = max(q[succ_job_a], q[succ_mach_a]) + d(a)

        # q_b' depende de q_a'
        succ_job_b = next(iter(self.SJ(b)), SINK_NODE)
        q[b] = max(q[a], q[succ_job_b]) + d(b)

        self.r_values[a] = r[a]
        self.r_values[b] = r[b]
        self.q_values[a] = q[a]
        self.q_values[b] = q[b]


        


def generate_initial_machine_orders(self) -> Dict[int, List[Tuple[int, int]]]:
    """
    Genera un diccionario con las aristas disyuntivas filtradas.
    Solo incluye las tuplas (u, v) donde u < v para cada máquina.
    """
    machine_orders = {
        machine: [(u, v) for u, v in arcs if u < v]
        for machine, arcs in self.disjunctive_arcs.items()
    }
    return machine_orders

def generate_neighborhood(self) -> Generator[Tuple[int, int], None, None]:
    """
    Genera un vecindario de pares de operaciones críticas que son 
    sucesivas en la misma máquina (conectadas por aristas disyuntivas).
    
    Returns:
        Generador de tuplas (u, v) donde u y v son operaciones críticas en la misma máquina,
        y v es el sucesor inmediato de u en la máquina.
    """
    
    # Para cada operación excepto source y sink
    for u in self.G.nodes():
        if u in (SINK_NODE, SOURCE_NODE):
            continue
        
        # Si u es crítica
        if self.G.nodes[u]['critical']:
            # Obtener sucesores en la misma máquina
            successors = self.SM(u)
            # Para cada sucesor
            for v in successors: 
                # Si v también es crítica
                if self.G.nodes[v]['critical']:
                    yield (u, v)


def generate_neighborhood2(self) -> Generator[Tuple[int, int], None, None]:
    """
    Vecindario Taillard: por cada máquina, reconstruye su orden actual
    y genera swaps sólo entre operaciones críticas adyacentes.
    """
    # 1. Recoger todas las operaciones críticas
    critical_ops = {
        i for i, d in self.G.nodes(data=True)
        if d.get('critical', False)
    }

    # 2. Por cada máquina m
    for m, disj_arcs in self.disjunctive_arcs.items():
        # 2.1 Construir el subgrafo H_m con sólo nodos de m y sus aristas disyuntivas
        H = nx.DiGraph()
        # nodos que corren en m
        nodes_m = [i for i, d in self.G.nodes(data=True) if d['machine'] == m]
        H.add_nodes_from(nodes_m)
        H.add_edges_from(disj_arcs)

        # 2.2 Orden topológico = secuencia actual en m
        try:
            seq = list(nx.topological_sort(H))
        except nx.NetworkXUnfeasible:
            # si hubiera ciclos algo va muy mal
            continue

        # 3. Sólo swaps entre vecinos críticos en esa secuencia
        for u, v in zip(seq, seq[1:]):
            if u in critical_ops and v in critical_ops:
                yield (u, v)


if __name__ == "__main__":
    base = r"C:\Users\botoa\OneDrive - UNICAN - Estudiantes\_devs_\Tecnicas Heurísticas y Meta-Heurísticas\MetaHeurísticos\Tabu Search\JSPLIB"
    js = JSSP_DiGraph("bt322", 3, 3, base)
    # js = JSSP_DiGraph("ft06", 6, 6, base)
    # js = JSSP_DiGraph("la01", 10, 5, base)

    sol = generate_initial_machine_orders(js)
    print('sol:', sol)
    js.load_disjunctive_arcs(sol)

    # for i in range(-1, len(js.operations)+1):
    #     print(f"Operacion: {i}")
    #     p=js.PJ(i)
    #     print('PJ:', p)
    #     p=js.SJ(i)
    #     print('SJ:', p)
    #     p=js.PM(i)
    #     print('PM:', p)
    #     p=js.SM(i)
    #     print('SM:', p)
    

    # r= js.compute_r()
    # print(f"r: {r}")
    # q= js.compute_q()
    # print(f"q: {q}")

    # c_max = js.compute_makespan()
    # print(f"C_max: {c_max}")

    # for (i, r_v), q_v in zip(r.items(),q.values()):
    #     s=r_v+q_v
    #     if s != c_max:
    #         print("ojo con", i)


    # critical_op = js.find_critical_operations()
    # print(len(critical_op), critical_op)
    # Calcular y mostrar el grado de todos los vértices del grafo
    # degrees = {node: js.G.degree(node) for node in js.G.nodes()}
    # print("Grados de los vértices:")
    # for node, degree in degrees.items():
    #     print(f"  Nodo {node}: Grado {degree}")

    # js.draw()


