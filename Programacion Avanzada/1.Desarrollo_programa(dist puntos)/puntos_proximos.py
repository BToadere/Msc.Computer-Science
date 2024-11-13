from math import sqrt


# Definición la funcion para el calculo de distancias
def distancia_euclidea(punto1, punto2):
    distancia = 0
    for i in range(len(punto1)):
        distancia += (punto1[i]-punto2[i])**2
    distancia = sqrt(distancia)
    return distancia

def lectura_fichero(file):
    # Lectura fichero de datos
    file=open(file, 'r')
    coordenadas = []
    for line in file:
        valor_float = [float(ele) for ele in line.strip().split(' ') ]
        coordenadas.append(tuple(valor_float))
    file.close()
    return coordenadas

def calculo_distancias_puntos(centro, coordenadas):
    # Calculo distancias
    distancias = []
    for punto in coordenadas:
        distancias.append(distancia_euclidea(centro, punto))

    return distancias


if __name__ == '__main__':
    # Declaración listas
    puntos_proximos = []

    coordenadas = lectura_fichero('coordenadas.txt')

    # Tratamiento centro (input)
    centro_brut = input('Coordenadas centro (formato: x y): ')
    centro = tuple([float(ele) for ele in centro_brut.split(' ')])
    
    distancias = calculo_distancias_puntos(centro, coordenadas)
    distancia_minima = min(distancias)

    # Discriminación putnos próximos
    for pos, distancia in enumerate(distancias):
        if distancia <= 2*distancia_minima:
            puntos_proximos.append(coordenadas[pos])

    #print('centr:', centro)
    #print('coordenadas:', coordenadas)
    #print('distancias:', distancias)
    #print('2*distancia minima:', 2*distancia_minima)
    print('Los puntos proximos son los siguientes:', puntos_proximos)