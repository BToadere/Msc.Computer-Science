#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
PerceptrÃ³n para reconocer imÃ¡genes de cifras. 
"""
import httpimport

analizarpixels=False
proporcionajuste=0.7
# para añadir convolutivasen cada capa '8c5' 8 procesadores de ancho 5
#                             8 procesadores que tienen cada uno 5^2 pesos
ocultos=['4c12', '7c7', '7c5','7c3', 30, 10]
nolineal='ReLU'
funcionfinal='Sigmoid'
inicio='inibase'
algoritmo='Rprop'
velocidad=0.001
# este parametro es para la selecion de puntos para hacer el calculo de gradiente, conviene qeu sea un poco grande
loteajuste=30000
iteraciones=100
fallosval=8
control=None
ajusteveloc=1
regularizacion=0
verejemplo=True

####################################
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
    import inicializacion
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
convol= type(ocultos[0]) is str and 'c' in ocultos[0]
if convol:
        tea=lectura.pasa2d(tea,28)
        tev=lectura.pasa2d(tev,28)
        tep=lectura.pasa2d(tep,28).requires_grad_()
        numvarent=1
    
#definir red
def modula(mod,modulos):
    for n in modulos:
        if mod in dir(n):
            if n is error:
                return error.Errorpropio(mod)
            return getattr(nn,mod)
    return mod
modsactiv=[nn,activaciones]
nolineal=modula(nolineal,modsactiv)
funcionfinal=modula(funcionfinal,modsactiv)
red=tipored.perceptron(numvarent,ocultos,10,nolineal,funcionfinal)
if GPU:
    tea=tea.cuda()
    tsa=tsa.cuda()
    tev=tev.cuda()
    tsv=tsv.cuda()
    tep=tep.cuda()
    tsp=tsp.cuda()
    red=red.cuda()
red(tep)
print(red)
inicializacion.reinicia(red,getattr(inicializacion,inicio))
ajuste.ajustar(red,tea,tsa,tev,tsv,tep,tsp,regiter=registro.clasiter,regfin=registro.clasprueba,algo=getattr(torch.optim,algoritmo),kaj=velocidad,
               numiter=iteraciones,minibatch=loteajuste,decay=regularizacion,
               topeval=fallosval,control=control,funpaso=ajusteveloc)

#Como los resultados son clases discretas, no entramos a los residuos numÃ©ricos. Se supone que la matriz de confusiÃ³n ya nos informa
red.eval()
#Vemos un caso concreto
if verejemplo:
    print('\nEjemplo')
    quien=random.randrange(len(tsp))
    caso=tep[quien].cpu()
    registro.imagen(caso.detach(),'Ejemplo',not convol)
    entrapru=tep[quien]
    entrapru=entrapru.unsqueeze(0)
    dice=red(entrapru)
    print('Red dice',error.clases(dice))

#Las explicaciones se basan en remuestrear. En un espacio de tan alta dimensiÃ³n lleva mucho tiempo
