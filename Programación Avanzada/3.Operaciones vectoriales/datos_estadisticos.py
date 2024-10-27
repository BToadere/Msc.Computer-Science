import numpy as np

def cen_med_mediana_moda():
    datos= np.loadtxt('datos_estadisticos.txt')

    centro = (np.max(datos)+np.min(datos))/2
    media = np.mean(datos)
    mediana = np.median(datos)

    value, border = np.histogram(datos, bins='auto')

    pos_moda = np.argmax(value)
    moda = (border[pos_moda]+border[pos_moda])/2

    print(f"centro: {centro}")
    print(f"media: {media}")
    print(f"mediana: {mediana}")
    print(f"moda: {moda}")

    return np.array((centro, media, mediana, moda))


if __name__=='__main__':
    cen_med_mediana_moda()