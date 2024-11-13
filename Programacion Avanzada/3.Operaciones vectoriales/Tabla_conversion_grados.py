import numpy as np
import pandas as pd

#  Tabla de conversion de grados a radiades de 0 a 360 el salto de grados se lo pregunto al usuario y hay qeu utilizar el arange

def conversion_grados_rad(vector):
    factor_conversion = np.pi/180
    return vector * factor_conversion

def line_space(step):
    return np.linspace(0,100,step)

if __name__ == '__main__':
    paso = float(input('Salto de grados en la tabla: '))
    v_grados = np.arange(start=0,  stop=360, step=paso)
    v_grados = v_grados.reshape(1,len(v_grados))

    v_radianes = conversion_grados_rad(v_grados)

    tabla_brut = np.concatenate((v_grados, v_radianes), axis=0).T
    print(tabla_brut)
    
    tabla_fina = pd.DataFrame(columns=['Grados', 'Radianes'], data= tabla_brut)
    print(tabla_fina.to_string())