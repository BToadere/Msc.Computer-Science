from collections import deque, defaultdict
from jssp_model import *
import random
import math


class TabuList(deque):
    def __init__(self, n_jobs: int, n_machines: int, p_refresh: float=0.05, p_length:float=0.2):
        super().__init__()
        self.n = n_jobs
        self.m = n_machines

        # Valor base L
        self.L_base = self.compute_L()
        self.L_min = int((1-p_length) * self.L_base)
        self.L_max = round((1+p_length) * self.L_base)

        self.current_length = self.L_base
        self.iter_since_last_change = 0
        self.refresh_interval = int(p_refresh * self.L_max)

    def compute_L(self) -> int:
        return round((self.n+self.m)/2)

    def push(self, move):
        self.append(move)
        if len(self) > self.current_length:
            self.popleft()

        self.iter_since_last_change += 1
        if self.iter_since_last_change >= self.refresh_interval:
            self.current_length = random.randint(self.L_min, self.L_max)
            self.iter_since_last_change = 0

    def is_tabu(self, move) -> bool:
        return move in self


class LongTermMemory:
    def __init__(self, n_operations: int):
        self.freq = defaultdict(int)       # f(b): frecuencia con la que b ha sido retrasada
        self.N = n_operations              # número total de operaciones
        self.P = 0.0                       # penalización dinámica
        self.delta_max = 0               # Δ_k^max
        self.prev_makespan = None         # makespan anterior

    def push(self, mov: Tuple[int, int], current_Cmax:int):

        self.update_frequency(mov)
        self.update_delta(current_Cmax)
        

    def update_frequency(self, mov: Tuple[int,int]):
        """
        Si b ha sido desplazada hacia atrás en su máquina respecto a su posición anterior,
        se incrementa f(b).
        """
        self.freq[mov[1]] += 1

    def update_delta(self, current_makespan: int):
        """
        Calcula el incremento de makespan desde la solución anterior
        y actualiza delta_max si el incremento es mayor al observado hasta ahora.
        """
        if self.prev_makespan is not None:
            delta = current_makespan - self.prev_makespan
            if delta > self.delta_max:
                self.delta_max = delta
                self.update_P()
        self.prev_makespan = current_makespan  # actualizar siempre

    def update_P(self):
        self.P = 0.5 * self.delta_max * math.sqrt(self.N)

    def get_penalty(self, mov: Tuple[int, int]) -> float:
        """
        Devuelve la penalización asociada a empujar hacia atrás a b.
        """
        return self.P * self.freq[mov[1]]


def do_tabu_search(instance, gen_solucion_ini, gen_vecinos, criterio_parada, tabu, memoria):
    
    instance.load_disjunctive_arcs(gen_solucion_ini(instance))
    s = instance.G
    fs = instance.function()
    s_best = s
    fs_best = fs
    k=0
    
    while not criterio_parada(k):
        k+=1
        m_best = None
        v_best = None
        fv_best = float('inf')
        print(f'{k:10}. Vecino: {fv_best:4} - Global: {fs_best:4}')
        for m in gen_vecinos(instance):
            instance.load_neighbor(m)
            v = instance.G
            fv = instance.function()
            print('fv', fv)
            # Cond tabu y cond aspiracion
            if m in tabu and fv > fs_best:
                continue
            
            if fv < fv_best:
                v_best = v
                fv_best = fv
                m_best = m

        if v_best is None:
            print('saltó')
            break  # no hay movimiento válido

        s = v_best
        fs = fv_best
    
        if fs < fs_best:
            s_best = s
            fs_best = fs

        tabu.push(m_best)
    
    return s_best, fs_best




if __name__ == '__main__':
    base = r"C:\Users\botoa\OneDrive - UNICAN - Estudiantes\_devs_\Tecnicas Heurísticas y Meta-Heurísticas\MetaHeurísticos\Tabu Search\JSPLIB"
    js = JSSP_DiGraph("bt322", 3, 3, base)
    js = JSSP_DiGraph("ft06", 6, 6, base)

    tabu=TabuList(n_jobs=js.n_jobs, n_machines=js.n_machines)
    ltmemory = LongTermMemory(n_operations=len(js.operations))

    s, fs = do_tabu_search(instance=js,
                           gen_solucion_ini=generate_initial_machine_orders, 
                           gen_vecinos=generate_neighborhood, 
                           criterio_parada=lambda k:k>10**4,
                           tabu=tabu,
                           memoria=ltmemory
                           )
    
    print('Sol', s, 'Val', fs)
    
