#!/usr/bin/python3

analisisprevio=False
#
preproc='rango1'
# Esto es para redecir el nivel del rio en 5 dias
horiz=5
# Cuanto sinstantes previos cargamos. Tendria sentido usar un año por el tema de los ciclos naturales, 
# sin emabrgo... Cunato va a afectar el caudal de hace 6 meses a 5 dias vista
# Se peude clasificar como:
# Un ocmponentes estacional (tener una foto a grandes rasgos, como una interpolacion de fourier grande)
# Un componente local (analifar las fluctiuaciones a nivel local, el ruido qeu podria tener)
# La memoria hace referencia a la ocmponnete local
memoria=10
tipo='perceptron'
ocultos=[4]
activsal='ReLU'
nolineal='Nolin'
#
algoajuste='Adam'
funerror='MSE'
# iteraciones maximas
limit=200
velocidad=0.001
#
analizaresiduos=True
#################

import httpimport
with httpimport.remote_repo('https://personales.unican.es/crespoj/redes/redespytorch.zip'):
    import torch
    from torch import nn
    import random
    import numpy
    import tipored
    import ajuste
    import registro
    import activaciones
    from torch.nn.utils.rnn import pack_sequence
    import analizar
    import error as funerr
    import scipy.io as sio
    # import temporal
    import preproceso
    from matplotlib import pyplot
    import inicializacion
    import lecturaurl
    import math
    from scipy.linalg import toeplitz

variables=lecturaurl.leevarsmat('realimentadas/parana3.mat')

for v in variables:
    if v[0]=='_':
       continue
    globals()[v]=variables[v][:,0]

if analisisprevio:
    temporal.graftemp1(y2)

ycp=getattr(preproceso,preproc)(numpy.concatenate((y1,y2)).reshape(-1,1))
tcorr=numpy.concatenate((t1,t2))
diccp=dict(zip(tcorr,ycp))
titat=numpy.concatenate((titati1,titati2,titati3,titati4,titati5,titati6))
xitat=preproceso.procesa(numpy.concatenate((x1,x2,x3,x4,x5,x6)).reshape(-1,1))
dicitat=dict(zip(titat,xitat))
tcom=numpy.array(list(set(tcorr) & set(titat)))
dif=tcom[1:]-tcom[:-1]
cambio=numpy.nonzero(dif-1)
tramos=[]
entradas=[]
salid=[]
cp=0
tramop=tcom[cp:-horiz]
itatip=torch.tensor([dicitat[t][0] for t in tramop],dtype=torch.float).reshape((-1,1))
corrienp=torch.tensor([diccp[t][0] for t in tramop],dtype=torch.float).reshape((-1,1))
itatipr,corrienpr,_=preproceso.recupera(itatip.numpy(),corrienp.numpy(),corrienp.numpy())
if analisisprevio:
    temporal.graftemp2(itatipr.numpy().squeeze(),corrienpr.numpy().squeeze())
    quit()

def generaret(dic,tramo,memoria):
	int=numpy.array([dic[t][0] for t in tramo]).reshape((-1,1))
	return torch.tensor(toeplitz(int)[memoria-1:,:memoria],dtype=torch.float)
    
for c in cambio[0]:
	tramo=tcom[cp:c-(horiz-1)]
	itatiret=generaret(dicitat,tramo,memoria)
	corrienret=generaret(diccp,tramo,memoria)
	entradas.append(torch.hstack((itatiret,corrienret)))
	salid.append(torch.tensor([diccp[t][0] for t in tcom[cp+horiz:c+1]],dtype=torch.float).reshape((-1,1))[memoria-1:])
	cp=c
entval=entradas.pop()
salval=salid.pop()
itatiretp=generaret(dicitat,tramop,memoria)
corrienretp=generaret(diccp,tramop,memoria)
entp=torch.hstack((itatiretp,corrienretp))
salp=torch.tensor([diccp[t][0] for t in tramop],dtype=torch.float).reshape((-1,1))[memoria-1:]
def modula(mod,modulos):
    for n in modulos:
        if mod in dir(n):
            return getattr(n,mod)
    return mod
modsactiv=[nn,activaciones]
nolin=modula(nolineal,modsactiv)
funcionfinal=modula(activsal,modsactiv)
numentradas=memoria*2
argums={'lineal':(numentradas,1),'cuasilineal':(numentradas,ocultos,1),'perceptron':(numentradas,ocultos,1,nolin,funcionfinal)}
red=getattr(tipored,tipo)(*(argums[tipo]))
aj=getattr(torch.optim,algoajuste)(red.parameters(),lr=velocidad)#,weight_decay=0.002)
#contaj=torch.optim.lr_scheduler.MultiplicativeLR(aj,lr_lambda= lambda paso: 0.99 if mederr/len(ent)>2 else 0.95)
topeval=3
nfall=0
evprev=1e99
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

print('\nAjuste')
error=module(funerror)
inicializacion.reinicia(red,inicializacion.inixu)
for it in range(limit):
    mederr=0
    for ent, sal in zip(entradas,salid):
        red.zero_grad()
        #mask = get_tgt_mask(1).cuda()
        salred = red(ent)#,sal)
        #salred = salred.permute(1, 2, 0)      
        eaj = error(salred, sal)
        eaj.backward()
        #torch.nn.utils.clip_grad_norm_(red.parameters(), 0.25)
        aj.step()
        mederr+=eaj.item()
    #contaj.step()
    print(it,mederr/len(ent))
    salrv=red(entval)
    ev=error(salrv,salval).item()
    if ev>evprev:
        nfall+=1
        if nfall>topeval:
            break
        else:
            evprev=ev



red.eval()
with torch.no_grad():
        salred=red(entp)#.cuda(),y)
        entreal,salreal,salredreal=preproceso.recupera(entp,salp,salred)
        pyplot.plot(salreal,label='Real')
        pyplot.plot(salredreal,label='Red')
        pyplot.legend()
        pyplot.show()

        #Las explicaciones van a depender de la realimentaciÃ³n y no son fÃ¡ciles de ver
        
#Analizar los residuos
if analizaresiduos:
    registro.grafresid(salreal,salredreal)
