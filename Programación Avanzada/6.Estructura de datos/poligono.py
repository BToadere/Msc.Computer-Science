import numpy as np

class vertice():
    def __init__(s, valor):
        s.valor = valor
        s.anterior = None
        s.posterior = None

    def listavalores(s):
        lista =[s.valor]
        s_aux=s
        while(s_aux.posterior):
            s_aux = s_aux.posterior
            lista.append(s_aux.valor)
        
        return lista

class Poligono():

    def __init__(poli, lista_vertices):  
        
        poli.vert_inicial = lista_vertices[0]
        poli.vert_final = lista_vertices[-1]

        poli.vertices = vertice(lista_vertices[0])
        aux = poli.vertices
        
        for i in range(1, len(lista_vertices)):
            vert = vertice(lista_vertices[i])
            aux.posterior = vert
            vert.anterior = aux
            aux = vert
        return
    
    def perimetro(poli):
        result = 0
        vert = poli.vertices
        while vert.posterior:
            pto_act = np.array(vert.valor)
            pto_pos = np.array(vert.posterior.valor)
            result += np.sqrt(np.sum((pto_pos-pto_act)**2))
            vert = vert.posterior

        pto_final = np.array(vert.valor)
        pto_inicial = np.array(poli.vertices.valor)
        result += np.sqrt(np.sum((pto_final-pto_inicial)**2))

        return result
    
    def borrar(poli, valor):
        vert = poli.vertices
        while True:
            # verti_anterior = vert.anterior
            if vert.valor == valor:
                vert.anterior.posterior = vert.posterior
                vert.posterior.anterior = vert.anterior
                break
            elif not vert.posterior:
                print(f'El valor qeu se quiere eliminar {valor} no existe')
                break
            else:
                vert = vert.posterior
        return
    


if __name__ == '__main__':
    li=[(0,0),(0,1),(1,1),(1,0)]
    poli = Poligono(li)
    poli.borrar((1,4))
    print(poli.vertices.listavalores())
    print(poli.perimetro())