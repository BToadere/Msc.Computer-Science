from typing import Dict, Tuple
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from src.jssp.jssp_model import JSSP_DiGraph, SOURCE_NODE, SINK_NODE, EdgeType

def draw_jssp_instance(self: JSSP_DiGraph, figsize: Tuple[int, int]=(8, 5)):
        
    def _compute_layout(self) -> Dict[int, Tuple[float, float]]:
        pos: Dict[int, Tuple[float, float]] = {}
        y_gap, x_gap = 2, 1
        for job_id, job_ops in enumerate(self.jobs, start=1):
            for idx, op in enumerate(job_ops):
                pos[op.id] = (idx * x_gap, -job_id * y_gap)
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
    node_labels = {
        n: self.G.nodes[n]['duration']
        for n in self.G.nodes
    }
    # Draw nodes
    nx.draw_networkx_nodes(self.G, pos, node_color='skyblue', node_size=350)
    # Draw edges
    label_pos = {}
    for node, coords in pos.items():
        label_pos[node] = (coords[0] - 0, coords[1] - 0.15)
    
    nx.draw_networkx_labels(self.G, label_pos, labels=node_labels, font_size=8, 
                    horizontalalignment='right', verticalalignment='top',
                    font_color='orange')
    # disyuntivas
    disj = [(u, v) for u, v, d in self.G.edges(data=True)
            if d['type'] == EdgeType.DISJUNCTIVE.value]
    nx.draw_networkx_edges(self.G, pos, edgelist=disj,
                style=(0, (4, 15)), edge_color='blue', width=0.5
            #    ,connectionstyle='arc3,rad=0.2' # Curved edges
                )  
    # conjuntivas
    conj = [(u, v) for u, v, d in self.G.edges(data=True)
        if d['type'] == EdgeType.CONJUNCTIVE.value]
    nx.draw_networkx_edges(self.G, pos, edgelist=conj,
                    edge_color='gray', arrows=True
                #    ,connectionstyle='arc3,rad=0.1' # Curved edges
                    )
    
    nx.draw_networkx_labels(self.G, pos)
    
    # Add legend
    
    legend_elements = [
        Line2D([0], [0], color='gray', lw=1, label='Aristas Conjuntivas'),
        Line2D([0], [0], color='blue', lw=1, linestyle='--', label='Aristas Disyuntivas'),
        Patch(facecolor='skyblue', edgecolor='black', label='ID Operaciones'),
        Patch(facecolor='orange', edgecolor='white', label='Duracion')
    ]
    
    plt.legend(handles=legend_elements, loc='upper center', 
               bbox_to_anchor=(0.5, -0.05), ncol=2)
    
    plt.title(f"Grafo JSSP: {self.name}")
    plt.axis('off')
    plt.tight_layout()
    plt.show()
