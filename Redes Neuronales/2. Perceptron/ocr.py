#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
PerceptrÃ³n para reconocer imÃ¡genes de cifras. 
"""

analizarpixels=False
proporcionajuste=0.9
modelo='perceptron'
nolineal='Nolin'
funcionfinal='Sigmoid'
ocultos=20
velocidad=0.001
loteajuste=100000
iteraciones=200
verejemplo=False

####################################
import httpimport
with httpimport.remote_repo('https://personales.unican.es/crespoj/redes/redespytorch.zip'):
    import lecturaurl
    import lectura
    import particion
    import tipored
    import ajuste
    import registro
    import torch
    import numpy
    import error
    import random
    from torch import nn
    import activaciones

GPU= torch.cuda.is_available()

datos,datpru=lecturaurl.leemat('mnist_uint8.mat','train_x','train_y','test_x','test_y')

numvarent=len(datos[0])-10
numuestras=len(datos)

#Son 784 pÃ­xels: no podemos analizar cada variable pixel por separado, pero podemos usar su distribucion
frel,vals=lectura.grafica(list(range(numvarent)),datos,False)

#Podemos analizar el conjunto de pÃ­xels
if analizarpixels:
    pixels=datos[:,:-10][:].reshape((-1,1))
    lectura.estadistica(['pixels'],pixels)

    #o bien un par de variables mapeadas
    lectura.mapa(datos[:,:-10],[numpy.mean,numpy.std])

#los pixels son homÃ³geneos entre sÃ­: no los vamos a preprocesar

"""
Cosas que tienes que definir y probar:

Ratio ajuste/validaciÃ³n
NÃºmero de procesadores ocultos
ParÃ¡metros del mÃ©todo de ajuste
Criterio de parada por validaciÃ³n
"""

#Son demasiadas variables para hacer estratificaciÃ³n
tea,tsa,tev,tsv=particion.ajazar(datos,numuestras,proporcionajuste)

tep,tsp=lectura.numpytorch(datpru,10)

def modula(mod):
    if mod in dir(nn):
        return getattr(nn,mod)
    if mod in dir(activaciones):
        return getattr(activaciones,mod)
    return mod

nolineal=modula(nolineal)
funcionfinal=modula(funcionfinal)
#definir red
argums={'lineal':(numvarent,10),'cuasilineal':(numvarent,ocultos,nolineal,10),
        'perceptron':(numvarent,[ocultos],10,nolineal,funcionfinal),
        'lineallineal':(numvarent,10) }
red=getattr(tipored,modelo)(*(argums[modelo]))
notorchs=['lineallineal']
if GPU and modelo not in notorchs:
    tea=tea.cuda()
    tsa=tsa.cuda()
    tev=tev.cuda()
    tsv=tsv.cuda()
    tep=tep.cuda()
    tsp=tsp.cuda()
    red=red.cuda()
if modelo not in notorchs:
    red(tep)
print(red)
_,red,_=ajuste.ajustar(red,tea,tsa,tev,tsv,tep,tsp,regiter=registro.clasiter,regfin=registro.clasprueba,kaj=velocidad,numiter=iteraciones,minibatch=loteajuste)

#Como los resultados son clases discretas, no entramos a los residuos numÃ©ricos. Se supone que la matriz de confusiÃ³n ya nos informa
if modelo not in notorchs:
    red.eval()
#Vemos un caso concreto
if verejemplo:
    print('\nEjemplo')
    quien=random.randrange(len(tsp))
    caso=tep[quien].cpu()
    registro.imagen(caso.detach(),'Ejemplo',True)
    dice=red(tep[quien:quien+1])
    print('Red dice',error.clases(dice))

#Las explicaciones se basan en remuestrear. En un espacio de tan alta dimensiÃ³n lleva mucho tiempo
