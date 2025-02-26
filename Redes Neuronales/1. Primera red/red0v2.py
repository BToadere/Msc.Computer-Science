#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
PerceptrÃ³n para estimar precio de viviendas. Una capa oculta con 5 procesadores con activaciÃ³n tangente hiperbÃ³lica y error cuadrÃ¡tico.
Dependencias: torch, sklearn, captum, httpimport
"""
import httpimport


analisisprevio=False

parteazar=0.5
parteajuste=0.75
partevalidacion=0.1

modelo='perceptron'

ocultos=40
nolineal='Nolin'
# Ojo si esta acotada o no esta acotada
funcionfinal='Identity'
velocidad=0.05


analizaresiduos=False
verejemplos=True


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

#DescripciÃ³n numÃ©rica
if analisisprevio:
    lectura.estadistica(varnoms,datos)

#DescripciÃ³n grÃ¡fica
frel,vals=lectura.grafica(varnoms,datos,analisisprevio)

#Preproceso. Hay otras posibilidades. Mira el fichero preproceso
datot=preproceso.rango1(datos)

#Conjuntos de ajuste, validaciÃ³n y muestra. Parte al azar y parte por agrupamiento
tea,tsa,tev,tsv,tep,tsp=particion.azaryestrat(datot,parteazar,parteajuste,partevalidacion)

def modula(mod):
    if mod in dir(nn):
        return getattr(nn,mod)
    if mod in dir(activaciones):
        return getattr(activaciones,mod)
    return mod

nolineal=modula(nolineal)
funcionfinal=modula(funcionfinal)
argums={'lineal':(numentradas,1),'cuasilineal':(numentradas,ocultos,nolineal,1),'perceptron':(numentradas,[ocultos],1,nolineal,funcionfinal),
        'lineallineal':(numentradas,1),'linealgen':(numentradas,ocultos,1)}
red=getattr(tipored,modelo)(*(argums[modelo]))
#).cuda(device)
print(red)
print('\nAjuste')
err,red,_=ajuste.ajustar(red,tea,tsa,tev,tsv,tep,tsp,kaj=velocidad)
print('Error medio cuadrÃ¡tico final en conjunto de prueba',err)
red.eval()
tepor=registro.residuos(tep,tsp,red,analizaresiduos)

if verejemplos:
#Vemos un caso concreto
    registro.sacarejemplos(tep,tsp,tepor,varnoms,frel,vals,red,False)
