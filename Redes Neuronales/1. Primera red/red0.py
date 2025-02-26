#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Perceptrón para estimar precio de viviendas. Una capa oculta con 5 procesadores con activación tangente hiperbólica y error cuadrático.
Dependencias: torch, minepy, captum, httpimport
"""
import httpimport

analisisprevio=True
parteazar=0.4
parteajuste=0.7
partevalidacion=0.15
modelo='lineal'
ocultos=4
nolineal='ReLU'
funcionfinal='Sigmoid'
velocidad=0.1
analizaresiduos=False
verejemplos=False

###################################################################################################
with httpimport.remote_repo('https://personales.unican.es/crespoj/redes/redespytorch.zip'):
    import lectura
    import preproceso
    import particion
    import tipored
    import ajuste
    import registro
    import lecturaurl
    from torch import nn
    import activaciones

#Cargamos los datos, todos
datos=lecturaurl.leelistas('practica1/casas.trn.txt')
numentradas=len(datos[0])-1
varnoms=['criminalidad','residencial','industrial','rio','polucion','habitaciones','casas-viejas','distancia-trabajo',
         'autovias','impuestos','ratio-aula','negr@s','pobreza','precio']

#Descripción numérica
if analisisprevio:
    lectura.estadistica(varnoms,datos)

#Descripción gráfica
frel,vals=lectura.grafica(varnoms,datos,analisisprevio)

#Preproceso a distribución normal media 0 varianza 1. Hay otras posibilidades. Mira el fichero preproceso
datot=preproceso.mediavar(datos)

#Conjuntos de ajuste, validación y muestra. Parte al azar y parte por agrupamiento
tea,tsa,tev,tsv,tep,tsp=particion.azaryestrat(datot,parteazar,parteajuste,partevalidacion)

def modula(mod):
    if mod in dir(nn):
        return getattr(nn,mod)
    if mod in dir(activaciones):
        return getattr(activaciones,mod)
    return mod

nolineal=modula(nolineal)
funcionfinal=modula(funcionfinal)
argums={'lineal':(numentradas,1),'cuasilineal':(numentradas,ocultos,1),'perceptron':(numentradas,[ocultos],1,nolineal,funcionfinal)}
red=getattr(tipored,modelo)(*(argums[modelo]))
#).cuda(device)
print(red)
print('\nAjuste')
err,red,_=ajuste.ajustar(red,tea,tsa,tev,tsv,tep,tsp,kaj=velocidad)
print('Error medio cuadrático final en conjunto de prueba',err.item())
red.eval()
tepor=registro.residuos(tep,tsp,red,analizaresiduos)

if verejemplos:
#Vemos un caso concreto
    registro.sacarejemplos(tep,tsp,tepor,varnoms,frel,vals,red,False)

