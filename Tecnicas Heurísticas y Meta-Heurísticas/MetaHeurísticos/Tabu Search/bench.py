from jssp_model import *


def test(js):
    sol = generate_initial_machine_orders(js)
    js.load_disjunctive_arcs(sol)
    # js.draw()
    print("INICIO", js.G.edges)
    crit = [(op,js.G.nodes[op]) for op in js.G.nodes if js.G.nodes[op]["critical"]]
    print("OP. CRITICAS", *crit)

    for m in generate_neighborhood2(js):
        print('M', m)
        js.load_neighbor(m)
        print(js.G.edges)
        print(js.__dict__)




if __name__ == "__main__":
    base = r"C:\Users\botoa\OneDrive - UNICAN - Estudiantes\_devs_\Tecnicas Heurísticas y Meta-Heurísticas\MetaHeurísticos\Tabu Search\JSPLIB"
    js = JSSP_DiGraph("bt322", 3, 3, base)
    # js = JSSP_DiGraph("ft06", 6, 6, base)
    # js = JSSP_DiGraph("la01", 10, 5, base)

    

    test(js)
    # sol = generate_initial_machine_orders(js)
    # print('sol:', sol)
    # load_disjunctive_arcs(js, sol)




    # for i in range(1, len(js.operations)+1):
    #     p=js.PJ(i)
    #     if len(p) !=1:print('pj:', p)
    #     p=js.SJ(i)
    #     if len(p) !=1:print('Sj:', p)
    #     p=js.PM(i)
    #     if len(p) !=1:print('pM:', p)
    #     p=js.PM(i)
    #     if len(p) !=1:print('pM:', p)
    
    # print('se termino el for')

    # # Calcular y mostrar el grado de todos los vértices del grafo
    # degrees = {node: js.G.degree(node) for node in js.G.nodes()}
    # print("Grados de los vértices:")
    # for node, degree in degrees.items():
    #     print(f"  Nodo {node}: Grado {degree}")
    # # r_val=js.compute_r()
    # # print(r_val)
    # # print(list(nx.topological_sort(js.G)))
    
    # # MK=js.compute_makespan()
    # # print('MakeSpan:', MK)
    # print(f"Opti: {js.optimum}")
    # js.draw()
