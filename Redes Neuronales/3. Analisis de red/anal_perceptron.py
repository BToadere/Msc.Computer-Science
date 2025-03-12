#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
PerceptrÃ³n para estimar precio de viviendas. Una capa oculta con 5 procesadores con activaciÃ³n tangente hiperbÃ³lica y error cuadrÃ¡tico.
"""
analisisprevio=False
parteazar=0.4
parteajuste=0.7
partevalidacion=0.15
modelo='perceptron'
ocultos=30
nolineal='Tanh'
funcionfinal='Identity'
velocidad=0.002
analizaresiduos=False
analizared=False
verejemplos=False
cogered='ANALISIS_RED_GRANDE'
reajusta=True
guardared=None
recorta='procesador'
cuantorecorte=3
###################################################################################################
import httpimport
with httpimport.remote_repo('https://personales.unican.es/crespoj/redes/redespytorch.zip'):
    import lectura
    import lecturaurl
    import preproceso
    import particion
    import tipored
    import ajuste
    import registro
    import random
    import analizar
    from torch.nn.utils import prune
    import torch
    from torch import nn
    import activaciones

#Cargamos los datos, todos
datos=lecturaurl.leelistas('practica1/casas.trn.txt')
numentradas=len(datos[0])-1
varnoms=['criminalidad','residencial','industrial',
         'rio','polucion','habitaciones',
         'casas-viejas','distancia-trabajo','autovias',
         'impuestos','ratio-aula','negr@s',
         'pobreza','precio']

#DescripciÃ³n numÃ©rica
if analisisprevio:
    lectura.estadistica(varnoms,datos)

#DescripciÃ³n grÃ¡fica
frel,vals=lectura.grafica(varnoms,datos,analisisprevio)

#Preproceso a distribuciÃ³n normal media 0 varianza 1
datot=preproceso.rango1(datos)


#Conjuntos de ajuste, validaciÃ³n y muestra. Parte al azar y parte por agrupamiento
tea,tsa,tev,tsv,tep,tsp=particion.azaryestrat(datot,parteazar,parteajuste,partevalidacion)

if cogered is None:
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
else:
    red=registro.cogered(cogered)
    if recorta=='pesoscapa':
        for capa in red.modules():
            if isinstance(capa, torch.nn.Conv2d) or isinstance(capa, torch.nn.Linear):
                    prune.l1_unstructured(capa,name='weight',amount=cuantorecorte) 
                    prune.remove(capa,'weight') # si quieres borrar definitivamente los originales
    elif recorta=='pesosglobal':
        parametros=[]     
        for capa in red.modules():
                if isinstance(capa, torch.nn.Conv2d) or isinstance(capa, torch.nn.Linear):
                        parametros.append((capa,'weight'))     
        prune.global_unstructured(parametros,pruning_method=prune.L1Unstructured,amount=cuantorecorte)
    elif recorta=='procesadores':
        for capa in red.modules():
                try:
                    if len(capa.weight)>cuantorecorte:# no vas a quitar  si sÃ³lo hay uno
                        prune.ln_structured(capa,name='weight',amount=cuantorecorte,n=2,dim=0)
                except:
                    pass
print(red)

if cogered is None or reajusta:
    print('\nAjuste')
    err,red,_=ajuste.ajustar(red,tea,tsa,tev,tsv,tep,tsp,kaj=velocidad) 
    print('Error medio cuadrÃ¡tico final en conjunto de prueba',err.item())
if guardared is not None:
    registro.guardared(red,guardared)

tepor=registro.residuos(tep,tsp,red,analizaresiduos)

if analizared:
    input("AnÃ¡lisis globales")
    #Analizar la red
    analizar.analisis(red,tep,tsp,False)


if verejemplos:
#Vemos un caso concreto
    registro.sacarejemplos(tep,tsp,tepor,varnoms,frel,vals,red)