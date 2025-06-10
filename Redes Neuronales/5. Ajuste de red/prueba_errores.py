#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
PerceptrÃ³n para estimar precio de viviendas. Una capa oculta con 5 procesadores con activaciÃ³n tangente hiperbÃ³lica.
"""
import httpimport

analisisprevio=False
############
parteazar=0.5
parteajuste=0.75
partevalidacion=0.1
proceso='rango1'
################
modelo='perceptron'
ocultos=25
nolineal='Tanh'
funcionfinal='Identity'
###################
funerror='SmoothL1'
inicio='inibase'

algoritmo='LBFGS'
velocidad=0.01
control=None
ajusteveloc=1
iteraciones=100
############
estimacion='particion'
numpruebas=10
todofinal=None
###################
analizaresiduos=True
analizared=False
verejemplos=False
################
cogered=None
reajusta=False
guardared=None
recorta=None
cuantorecorte=0
###################################################################################################
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
    import error
    from torch import nn
    import activaciones
    import inicializacion
    import math
    import copy
    from matplotlib import pyplot
    import statistics

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

#Preproceso a distribuciÃ³n normal media 0 varianza 1
datot=getattr(preproceso,proceso)(datos)

if estimacion =='bootstrap':
    #ParticiÃƒÂ³n para bootstrap
    gener,tep,tsp=particion.generazarremuest(datot,parteajuste+partevalidacion)
if estimacion=='cruzada':
    #ParticiÃƒÂ³n para validaciÃƒÂ³n cruzada
    gener=iter(particion.genervalcruz(datot,numpruebas))

def modula(mod,modulos):
    for n in modulos:
        if mod in dir(n):
            if n is error:
                return error.Errorpropio(mod)
            return getattr(n,mod)
    return mod
modsactiv=[nn,activaciones]
nolineal=modula(nolineal,modsactiv)
funcionfinal=modula(funcionfinal,modsactiv)
if cogered is None:
    argums={'lineal':(numentradas,1),'cuasilineal':(numentradas,ocultos,1),'perceptron':(numentradas,[ocultos],1,nolineal,funcionfinal)}
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

presens={'MSE':math.sqrt,'L1':abs,'SmoothL1':abs}
def module(mod):
    global presenerror
    if mod+'Loss' in dir(nn):
        m= getattr(nn,mod+'Loss')()
        presenerror=presens[mod]
        return m
    if mod in dir(error):
            m=error.ErrorPropio(mod)
            presenerror=m.presen
            return m
    return m()

if cogered is None or reajusta:
    print('\nAjuste')
    ferr=module(funerror)
    errorps=[]
    erroras=[]
    diferror=[]
    errmin=1000
    for _ in range(numpruebas):
        if estimacion in ['particion','particiÃ³n']:
        #Conjuntos de ajuste, validaciÃ³n y muestra. Parte al azar y parte por agrupamiento
            tea,tsa,tev,tsv,tep,tsp=particion.azaryestrat(datot,parteazar,parteajuste,partevalidacion)
        else:
            if estimacion=='bootstrap':
                    teav,tsav=next(iter(gener))
            if estimacion=='cruzada':
                tep,tsp,teav,tsav=next(gener)
            tea,tsa,tev,tsv,_,_=particion.torchazar(teav.detach(),tsav.detach(),parteajuste/(parteajuste+partevalidacion),partevalidacion/(parteajuste+partevalidacion))
        inicializacion.reinicia(red,getattr(inicializacion,inicio))
        err,red,erraj=ajuste.ajustar(red,tea.requires_grad_(),tsa,tev,tsv,tep,tsp,kaj=velocidad,error=ferr,
                                     algo=getattr(torch.optim,algoritmo),control=control,
                                 numiter=iteraciones,funpaso=ajusteveloc,muestraerror=presenerror) 
        errorps.append(err.item())
        erroras.append(erraj)
        diferror.append(err.item()-erraj)
        if err.item()<errmin:
            errmin=err.item()
            registro.guardared(red,'tempytorch')

red=registro.cogered('tempytorch')
if numpruebas>1:
    pyplot.hist(errorps)
    pyplot.show()

if todofinal is not None:
    finaj=getattr(statistics,todofinal)(erroras)
    inicializacion.reinicia(red,getattr(inicializacion,inicio))
    tea,tsa=lectura.septorch(datot)
    red,erraj=ajuste.ajustar(red,tea.requires_grad_(),tsa,None,None,None,None,kaj=velocidad,error=ferr,algo=getattr(torch.optim,algoritmo),control=control,
                                 numiter=iteraciones,funpaso=ajusteveloc,muestraerror=presenerror,limerr=finaj)
    print('EstimaciÃ³n de error de generalizacion',erraj+getattr(statistics,todofinal)(diferror))
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