#Conjunto de datos de crecimiento
install.packages("fda.usc")
library("fda.usc")

data("growth")
growth

View(growth)

growth$hgtm
growth$hgtf
growth$age

growth
length(growth$age)
dim(growth$hgtm)
dim(growth$hgtf)


#Datos tecator
data(tecator)
tecator

tecator$absorp.fdata

plot(tecator$absorp.fdata,type = "o")
plot(tecator$absorp.fdata,col = "black")

tecator$y$Fat #Contenido en grasa
tecator$y$Water #Contenido en agua
tecator$y$Protein #Contenido en proteina


#Datos aemet
data(aemet)

View(aemet)

summary(aemet)

#Contiene medias por día de temperaturas entre 1980-2009 de 73 estaciones
#meteorológicas distribuidas por todo el país.
aemet$temp

plot(aemet$temp)
plot(aemet$wind.speed)
plot(aemet$logprec)







#Introducción a crear bases de funciones.
baseF <- create.fourier.basis(c(0,2*pi),nbasis = 3)

baseF$names

oldpar <- par(no.readonly = TRUE)
plot(baseF)

baseS <- create.bspline.basis(c(0,1),nbasis = 3,norder = 3)

baseS$names

olpar <- par(no.readonly = TRUE)
plot(baseS)

baseS <- create.bspline.basis(c(0,10),nbasis = 12,norder = 3)
baseS <- create.bspline.basis(c(0,10),nbasis = 12,norder = 10)

olpar <- par(no.readonly = TRUE)
plot(baseS)

#Ejemplo de juguete

x <- seq(0,2*pi,by = 0.1)
y <- sin(x)
plot(x,y,type = "l",lty = 2,xlim = c(0,2*pi),ylim = c(-1,1))
par(new = TRUE)
par(mfrow = c(1,1))

basis <- create.bspline.basis(c(0,2*pi),5,2)
fd_obj <- smooth.basis(x,y,basis)

plot(fd_obj)

eval.fd(3,fd_obj$fd) #Evalua el objeto funcional que hemos creado al suavizar
#nuestros datos con una base de splines.

basis <- create.bspline.basis(c(0,2*pi),6,3)
fd_obj <- smooth.basis(x,y,basis)

plot(x,y,type = "l",lty = 2,xlim = c(0,2*pi),ylim = c(-1,1))
par(new = TRUE)
plot(fd_obj)


basis <- create.bspline.basis(c(0,2*pi),7,4)
fd_obj <- smooth.basis(x,y,basis)

plot(x,y,type = "l",lty = 2,xlim = c(0,2*pi),ylim = c(-1,1))
par(new = T)
plot(fd_obj)




#Representar tecator
install.packages("fda.usc")
library("fda.usc")

data(tecator)
tecator

tecator$absorp.fdata

plot(tecator$absorp.fdata,type = "o")
plot(tecator$absorp.fdata,col = "black")

tecator$y$Fat #Contenido en grasa
tecator$y$Water #Contenido en agua
tecator$y$Protein #Contenido en proteina





#Queremos ver la relación de las curvas en función de su contenido en grasa.
Fat20 <- ifelse(y$Fat<20,2,4)#2 rojo y 4 azul
plot(absorp,col=Fat20)

Water55 <- ifelse(y$Water < 55,1,3) #1 negro y 3 verde
plot(absorp,col=Water55)

Protein15 <- ifelse(y$Protein < 15,1,3)
plot(absorp,col=Protein15)
#
#¡¡¡No se distingue!!! Hay que idear otra cosa...
#

#Representar growth
#El número de funciones de la base de splines viene dado por:
#number of basis functions = order + number of interior knots

data("growth")
growth

growth$hgtm
growth$hgtf
growth$age

growth
length(growth$age)
dim(growth$hgtm)
dim(growth$hgtf)

#Altura de los chicos
for(i in 1:dim(growth$hgtm)[2]){
  plot(growth$age,growth$hgtm[,i],ylim=c(min(growth$hgtm),max(growth$hgtm)),
       type = "l")
  par(new = T)
}

#Altura de las chicas
for(i in 1:dim(growth$hgtf)[2]){
  plot(growth$age,growth$hgtf[,i],ylim=c(min(growth$hgtf),max(growth$hgtf)),
       type = "l")
  par(new = T)
}

#Altura conjunta (chicas en rojo y chicos en azul)
for(i in 1:dim(growth$hgtm)[2]){
  plot(growth$age,growth$hgtm[,i],ylim=c(min(growth$hgtf),max(growth$hgtm)),
       type = "l",col="blue")
  par(new = T)
}
for(i in 1:dim(growth$hgtf)[2]){
  plot(growth$age,growth$hgtf[,i],ylim=c(min(growth$hgtf),max(growth$hgtm)),
       type = "l",col="red")
  par(new = T)
}


#Representar AEMET
data(aemet)

View(aemet)

summary(aemet)

#Contiene medias por día de temperaturas entre 1980-2009 de 73 estaciones
#meteorológicas distribuidas por todo el país.
aemet$temp

plot(aemet$temp)
plot(aemet$wind.speed)
plot(aemet$logprec)


temp.fd <- fdata2fd(aemet$temp,type.basis = "bspline",nbasis = 7)
plot(temp.fd)

par(mfrow = c(1, 2))
plot(temp.fd)
plot(aemet$temp)

temp.fd.fourier <- fdata2fd(aemet$temp,type.basis = "fourier",nbasis = 7)
par(mfrow = c(1, 3))
plot(temp.fd.fourier)
plot(temp.fd)
plot(aemet$temp)

##############################################################################
install.packages("fda.usc")
library("fda.usc")
data(tecator)

absorp <- tecator$absorp.fdata
y <- tecator$y

Fat20 <- ifelse(y$Fat<20,2,4)
plot(absorp,col=Fat20)

#Calculamos la primera derivada usando splines.
absorp.d1 <- fdata.deriv(absorp,nderiv = 1,method = "bspline") 
plot(absorp.d1,col=Fat20)

par(mfrow = c(1, 2))

##########
library(fda.usc)
data(tecator)
names(tecator)
fat<-tecator$y$Fat
x<-tecator$absorp.fdata

# Aproximamos las curvas por splines hasta el orden 9 y el 41
x0_9<-fdata.deriv(tecator$absorp.fdata,nderiv=0,nbasis=9)
x0_41<-fdata.deriv(tecator$absorp.fdata,nderiv=0,nbasis=41)

x0_9 #Observamos que la clase ha cambiado a "fdata".

# Lo mismo con las segundas derivadas.
x2_9<-fdata.deriv(tecator$absorp.fdata,nderiv=2,nbasis=9)
x2_41<-fdata.deriv(tecator$absorp.fdata,nderiv=2,nbasis=41)

# Hacemos cortes en los contenidos de grasa
Corte.1=25
Corte.2=15

datos=tecator$absorp.fdata
ondas=datos$argvals
# Los números están elegidos para que al representar las curvas, las bajas en grasa salgan verdes
# las altas en rojo y en amarillo las intermedias
y<-ifelse(fat<Corte.1,7,2) 
y[fat<Corte.2]=rep(3,length(y[fat<Corte.2]))
#y<-factor(y)
table(y)

# Las curvas originales y las curvas cuyo contenido en grasa tenemos 
# que averiguar son:
plot(x,col=y,type="l",lty=1)
legend("topleft", legend = c(paste("fat >",Corte.1,"%"),paste("fat","intermediate        "),paste("fat <",Corte.2,"%")),col=c(2,7,3),lwd=3,cex=0.5)

elijo.curvas=c(99,  76, 205)
for (i in 1:length(elijo.curvas)){
  lines(x$argvals,x$data[elijo.curvas[i],],lwd=3)#,col=y[elijo.curvas[i]])
}

# Las dibujamos aproximadas hasta el orden 9
plot(x0_9,col=y,type="l",lty=1,main="Spectometric curves. Aproximadas hasta el orden 9")
legend("topleft", legend = c(paste("fat >",Corte.1,"%"),paste("fat","intermediate"),paste("fat <",Corte.2,"%")),col=c(2,7,3),lwd=3,cex=1)
for (i in 1:length(elijo.curvas)){
  lines(x0_9$argvals,x$data[elijo.curvas[i],],lwd=3)#,col=y[elijo.curvas[i]])
}


# Las dibujamos aproximadas hasta el orden 41:
plot(x,col=y,type="l",lty=1,main="Spectometric curves")
legend("topleft", legend = c(paste("fat >",Corte.1,"%"),paste("fat","intermediate        "),paste("fat <",Corte.2,"%")),col=c(2,7,3),lwd=3,cex=1)

elijo.curvas=c(99,  76, 205)
for (i in 1:length(elijo.curvas)){
  lines(x$argvals,x$data[elijo.curvas[i],],lwd=3)#,col=y[elijo.curvas[i]])
}

par(mfrow = c(1,1))

#Dibujamos las curvas elegidas e indicamos sus respectivos contenidos en grasa
plot(x,col="white",type="l",lty=1,main="Spectometric curves")
legend("topleft", legend = c(paste("fat >",Corte.1,"%"),paste("fat","intermediate        "),paste("fat <",Corte.2,"%")),col=c(2,7,3),lwd=3,cex=1)
for (i in 1:length(elijo.curvas)){
  lines(x$argvals,x$data[elijo.curvas[i],],lwd=2,col=y[elijo.curvas[i]])
}
text(x$argvals[90],x$data[elijo.curvas[1],90]+.15,paste("fat=",fat[elijo.curvas[1]]),cex=1,col="magenta")
text(x$argvals[90],x$data[elijo.curvas[2],90]+.1,paste("fat=",fat[elijo.curvas[2]]),cex=1,col="magenta")
text(x$argvals[80],x$data[elijo.curvas[3],80]-.1,paste("fat=",fat[elijo.curvas[3]]),cex=1,col="magenta")


# Dibujamos juntas las segundas derivadas de las curvas.

par(mfrow=c(1,2))
plot(x2_9,col=y,type="l",lty=1,main="2nd derivada. Aproximadas orden 9")
legend("topleft", legend = c(paste("fat >",Corte.1,"%"),paste("fat","intermediate        "),paste("fat <",Corte.2,"%")),col=c(2,7,3),lwd=3,cex=.5)

for (i in 1:length(elijo.curvas)){
  lines(x2_9$argvals,x2_9$data[elijo.curvas[i],],lwd=2)
}

plot(x2_41,col=y,type="l",lty=1,main="2nd derivada. Aproximadas orden 41")
legend("topleft", legend = c(paste("fat >",Corte.1,"%"),paste("fat","intermediate        "),paste("fat <",Corte.2,"%")),col=c(2,7,3),lwd=3,cex=.5)

for (i in 1:length(elijo.curvas)){
  lines(x2_41$argvals,x2_41$data[elijo.curvas[i],],lwd=2)
}
par(mfrow=c(1,1))



plot(x2_41,col="blue",type="l",lty=1,main="Aproximaciones segunda derivada")
lines(x2_9,col="red",type="l",lty=1)

legend("topleft", legend = c("Orden 9","Orden 41"),col=c("red","blue"),lwd=3,cex=1)

#########
#Datos del AEMET
data(aemet)
argvals <- aemet$temp$argvals
datos <- aemet$temp$data
plot(data,xlim = c(0,365),ylim = c(-2,30),type = "l")

par(mfrow = c(1,1))
for(i in 1:73){
  plot(aemet$temp$data[i,],type="l",xlim = c(0,365),ylim = c(-2,30))
  par(new=TRUE)
}

#Vamos a dibujar las curvas con temperatura media más alta en rojo
indices <- c(34,35,55:60)

par(new=T)
for(i in indices){
  plot(aemet$temp$data[i,],type = "l",xlim = c(0,365),ylim = c(-2,30),col = "red")
  par(new =T)
}

#Suaviazamos las curvas

temp.fd <- fdata2fd(aemet$temp, type.basis= "splines", nbasis= 41)
canarySmooth <- temp.fd[indices]

plot(temp.fd,col="black",lty=1)
lines(canarySmooth,col="red",type="l",lty=1)
