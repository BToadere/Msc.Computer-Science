import networkx as nx
import matplotlib.pyplot as plt
import os
import json
import numpy as np


class JobShopGraph:
    def __init__(self, name, jobs, machines):
        jsplib_path = r"C:\Users\botoa\OneDrive - UNICAN - Estudiantes\_devs_\Tecnicas Heurísticas y Meta-Heurísticas\MetaHeurísticos\Tabu Search\JSPLIB"
        with open(os.path.join(jsplib_path, "instances.json"), "r") as f:
            instances = json.load(f)
        self.jobs = int(jobs)
        self.machines = int(machines)

        instance = next(
            inst for inst in instances
            if inst["name"] == name and inst["jobs"] == jobs and inst["machines"] == machines
        )
        self.optimum = instance["optimum"]
        data_path = os.path.join(jsplib_path, instance["path"])
        self.__parse_instance(data_path)

        # Aquí ahora inicializas tu grafo
        self.graph = nx.DiGraph()
        self.__build_graph()

    def __parse_instance(self, path_absoluto):
        with open(path_absoluto) as f:
            lines = [line for line in f if not line.strip().startswith("#")]
        lines = lines[1:]
        op_id = 1
        data = []
        for line in lines:
            row = list(map(int, line.split()))
            operaciones = [(op_id + i, row[idx], row[idx + 1]) for i, idx in enumerate(range(0, len(row), 2))]
            data.append(operaciones)
            op_id += len(row) // 2
        self.N = op_id-1
        self.data = data

    def __build_graph(self):
        # añadimos los N nodos de las operaciones más el nodo inicial 0 y el nodo final -1
        self.graph.add_nodes_from(range(-1, self.N + 1))

        # Añadir atributos de máquina a los nodos
        for job in self.data:
            for op_id, machine, duration in job:
                self.graph.nodes[op_id]["machine"] = machine
                self.graph.nodes[op_id]["duration"] = duration

        # Añadir aristas de conjuntivas
        for job in self.data:
            self.graph.add_edge(0, job[0][0], weight=0, type="conjuntive")
            self.graph.add_edge(job[-1][0], -1, weight=0, type="conjuntive")
            for operation, _ in enumerate(job[:-1]):
                self.graph.add_edge(job[operation][0], job[operation+1][0], weight=job[operation][2], type="conjuntive")

        # Añadir aristas disyuntivas
        for m in set(nx.get_node_attributes(self.graph, "machine").values()):
            # Para cada máquina
            ops = [n for n, d in self.graph.nodes(data=True) if d.get("machine") == m]
            # Crear conexiones completas entre las operaciones que usan esa máquina
            for i in range(len(ops)):
                for j in range(i+1, len(ops)):
                    self.graph.add_edge(ops[i], ops[j], weight=0, type="disjuntive")
                    self.graph.add_edge(ops[j], ops[i], weight=0, type="disjuntive")


    def show_graph(self):
        import matplotlib.pyplot as plt
        import networkx as nx

        plt.figure(figsize=(8, 5))

        pos = {}
        y_gap = 2  # Espaciado vertical entre máquinas
        x_gap = 1  # Espaciado horizontal entre operaciones

        job_id = 0
        for job in self.data:
            for idx, (op_id, maquina, duracion) in enumerate(job):
                pos[op_id] = (idx * x_gap, -maquina * y_gap)
            job_id += 1

        if pos:
            y_values = [coord[1] for coord in pos.values()]
            center_y = (max(y_values) + min(y_values)) / 2
        else:
            center_y = 0

        if 0 in self.graph.nodes and 0 not in pos:
            pos[0] = (-1.5 * x_gap, center_y)
        if -1 in self.graph.nodes and -1 not in pos:
            pos[-1] = (max(p[0] for p in pos.values()) + 1.5 * x_gap, center_y)

        # Dibujar nodos
        nx.draw_networkx_nodes(self.graph, pos, node_color='skyblue', node_size=1000)

        # Dibujar aristas de trabajo (tipo 'job') normales
        job_edges = [(u, v) for u, v, d in self.graph.edges(data=True) if d.get('type') != 'disjuntive']
        nx.draw_networkx_edges(self.graph, pos, edgelist=job_edges, edge_color='gray', arrows=True)

        # Dibujar aristas de máquina (tipo 'machine') como no dirigidas y punteadas
        machine_edges = [(u, v) for u, v, d in self.graph.edges(data=True) if d.get('type') == 'disjuntive']
        nx.draw_networkx_edges(self.graph, pos, edgelist=machine_edges, style='dotted', edge_color='red', arrows=False)

        # Dibujar etiquetas de nodos
        nx.draw_networkx_labels(self.graph, pos)

        # Dibujar solo etiquetas de aristas tipo 'job'
        job_edge_labels = { (u, v): d['type'] for u, v, d in self.graph.edges(data=True) if d.get('type') != 'disjuntive' }
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=job_edge_labels)

        plt.title("Grafo JSSP (Máquinas punteadas y no dirigidas)")
        plt.axis('off')
        plt.show()









        

    

if __name__ == '__main__':
    print('JSSP')
    # js = JobShopGraph("ft06", 6, 6)
    js = JobShopGraph("bt322", 3, 3)
    print(js.N)
    print(js.data)

    js.show_graph()



