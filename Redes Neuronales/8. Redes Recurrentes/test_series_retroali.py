#!/usr/bin/python3
import httpimport

analisisprevio=False
#
preproc='rango1'
#
horiz=4
#
tipo='RealimTrans'


# capocul=4
naten = 2
nocul=50#[20,15,15,12,10]

activsal='Identity'
nolineal='Tanh'
#
algoajuste='Adam'
funerror='MSE'
limit=500
velocidad=0.001
#
analizaresiduos=False
#################

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

variables=lecturaurl.leevarsmat('realimentadas/parana3.mat')

for v in variables:
    if v[0]=='_':
       continue
    globals()[v]=variables[v][:,0]

if analisisprevio:
    temporal.graftemp1(y2) #comÃ©ntalo despuÃ©s

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
for c in cambio[0]:
	tramo=tcom[cp:c-(horiz-1)]
	itati=torch.tensor([dicitat[t][0] for t in tramo],dtype=torch.float).reshape((-1,1))
	corrien=torch.tensor([diccp[t][0] for t in tramo],dtype=torch.float).reshape((-1,1))
	entradas.append(torch.hstack((itati,corrien)))
	salid.append(torch.tensor([diccp[t][0] for t in tcom[cp+horiz:c+1]],dtype=torch.float).reshape((-1,1)))
	cp=c
entval=entradas.pop()
salval=salid.pop()
tramop=tcom[cp:-horiz]
itatip=torch.tensor([dicitat[t][0] for t in tramop],dtype=torch.float).reshape((-1,1))
corrienp=torch.tensor([diccp[t][0] for t in tramop],dtype=torch.float).reshape((-1,1))
entp=torch.hstack((itatip,corrienp))
salp=torch.tensor([diccp[t][0] for t in tcom[cp+horiz:]],dtype=torch.float).reshape((-1,1))
itatipr,corrienpr,_=preproceso.recupera(itatip.numpy(),corrienp.numpy(),corrienp.numpy())
if analisisprevio:
    temporal.graftemp2(itatipr.numpy().squeeze(),corrienpr.numpy().squeeze()) #comÃ©ntalo despuÃ©s
def modula(mod,modulos):
    for n in modulos:
        if mod in dir(n):
            return getattr(n,mod)
    return mod
modsactiv=[nn,activaciones]
nolin=modula(nolineal,modsactiv)
funcionfinal=modula(activsal,modsactiv)
if tipo=='Realimicror':
    argstipo=[2,capocul,nocul,1]
elif tipo=='Realimoc':
    argstipo=[2,capocul,nocul,1,True,nolineal.lower()]
elif tipo=='Realimsal':
    argstipo=[2,nocul,1,nolin,funcionfinal]
elif tipo=='RealimTrans':
    argstipo=[2,1,naten,nocul,funcionfinal]
red=getattr(tipored,tipo)(*argstipo)
#red=tipored.Realimoc(2,capocul,nocul,1,serie=True,fun='relu')
#red=tipored.Realimsal(2, [20,10],1,activ=nn.LeakyReLU,activsal=nn.LeakyReLU)
#red=tipored.Realimicror(1,capocul,nocul,1,)
#red=tipored.RealimTrans(2,1,naten,nocul,activsal)
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


#Analizar la red es retorcido cuando las entradas no son de la misma longitud
    

red.eval()
with torch.no_grad():
        #mask = get_tgt_mask(1).cuda()
        salred=red(entp)#.cuda(),y)
        #print(salred.shape)
        #Para realimsal
        entreal,salreal,salredreal=preproceso.recupera(entp,salp,salred)
        pyplot.plot(salreal,label='Real')
        pyplot.plot(salredreal,label='Red')
        pyplot.legend()
        pyplot.show()

        #Las explicaciones van a depender de la realimentaciÃ³n y no son fÃ¡ciles de ver
        
#Analizar los residuos
if analizaresiduos:
    registro.grafresid(salreal,salredreal)
