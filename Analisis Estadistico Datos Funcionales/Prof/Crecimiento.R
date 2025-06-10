#  -----------------------------------------------------------------------
#                            Growth Data Analyses
#  -----------------------------------------------------------------------
#
#                          Overview of the analyses
#
#  These analyses are intended to illustrate the analysis of nonperiod data
#  where a spline basis is the logical choice.  These analyses complement
#  the daily weather data in that sense.
#
#  The growth data have the additional feature of being essentially
#  monotonic or, to say the same thing in another way, have an essentially
#  positive first derivative or velocity.  This requires monotone smoothing.
#  Moreover, most of the interpretability of the growth data comes from
#  inspecting the acceleration of the height curves, so that great emphasis
#  is placed here on getting a good sensible and stable acceleration
#  estimate.
#
#  Finally, a large prortion of the variation in the growth curve data is 
#  due to phase variation, mainly through the variation in the timing of the
#  pubertal growth spurt.  Registration therefore plays a major role and is
#  especially illustrated here.
#
#  Most of the analyses are carried out on the Berkeley growth data, which
#  have the advantage of being freely distributable, whereas as more recent
#  and larger data bases require special permission from the agencies that
#  are responsible for them.  Not much is lost, however, since the quality
#  of the Berkeley data are quite comparable to those of other datasets.
#  The primary analyses are the monotone smoothing of the data.  The right
#  smoothing level is taken as known, and was determined by other analyses
#  in the Matlab language.  The monotone smoothing function used here
#  requires the use of low-level code in C and C++, but even with that help,
#  computation times are substantially longer than in Matlab.
#  Following monotone smoothing, the growth data are registered, an
#  essential step because of the large variation in the timing of the
#  pubertal growth spurt.  The pubertal growth spurts are aligned using
#  landmark registration, and the land-mark registered curves are then
#  registered using continuous registration.
#  The final analysis is of a set of data on a single boy where the
#  measurements are taken every three days or so, rather than twice a year.
#  These data show that growth is rather more complex than the traditional
#  data could have revealed.
#  -----------------------------------------------------------------------
#                           Berkeley Growth Data
#  -----------------------------------------------------------------------
#  Last modified 2008.06.21;  previously modified 21 March 2006
###
### 0.  Access the data (available in the 'fda' package)
###
library(fda)
attach(growth)
(nage <- length(age))
(ncasem <- ncol(hgtm))
(ncasef <- ncol(hgtf))
(ageRng <- range(age))
agefine <- seq(ageRng[1],ageRng[2],length=101)
###
### 1.  Smooth the data (ignore monotonicity) --------------
### Se ignora la monotonia para simplificar el proceso de suavización
#  This smooth uses the usual smoothing methods to smooth the data,
#  but is not guaranteed to produce a monotone fit.  This may not
#  matter much for the estimate of the height function, but it can
#  have much more serious consequences for the velocity and
#  accelerations.  See the monotone smoothing method below for a
#  better solution, but one with a much heavier calculation overhead.

#  -----------  Create fd objects   ----------------------------
#  A B-spline basis with knots at age values and order 6 is used
#
# A single call to smooth.basisPar would give us a cubic spline.  
# However, to get a smooth image of acceleration,
# we need a quintic spline (degree 5, order 6) 
hgtm = growth$hgtm
hgtf = growth$hgtf
age = growth$age
rng = range(age)
knots  <- growth$age
norder <- 6
nbasis <- length(knots) + norder - 2 # Esto es una formula que se establece en la teroia de splines
hgtbasis <- create.bspline.basis(range(knots), nbasis, norder, knots)


# Penalización 4 derivada, la penalizamos porqeu penalizamos el cambio de 
# curbatura en la aceleración que es la segunda derivada
Lfdobj<-4
lambda <- 1e-2
growfdPar <- fdPar(hgtbasis, Lfdobj, lamda)
# Need 'hgtm', 'hgtf', e.g., from attach(growth)
# Proceso de suavizado, ejex      ejey        funcion a minimizar
hgtmfd <- smooth.basis(growth$age, growth$hgtm, growfdPar)
hgtmfd <- smooth.basis(growth$age, growth$hgtm, growfdPar)$fd
hgtffd <- smooth.basis(growth$age, growth$hgtf, growfdPar)$fd

#  Calculo de la aproximacion por B-splines a las curvas iniciales y de sus velocidades y aceleraciones
#  Males:
hgtmfit <- eval.fd(age,     hgtmfd) # comando para evaluar (hará falta en el crossvalidation)
hgtmhat <- eval.fd(agefine, hgtmfd) # evaluamos el linespace creado por nosotros
velmhat <- eval.fd(agefine, hgtmfd, 1) # evalua la primera derivada
accmhat <- eval.fd(agefine, hgtmfd, 2) 
childrenm <- 1:ncasem
# Females:
hgtffit <- eval.fd(age,     hgtffd)
hgtfhat <- eval.fd(agefine, hgtffd)
velfhat <- eval.fd(agefine, hgtffd, 1)
accfhat <- eval.fd(agefine, hgtffd, 2)
childrenf <- 1:ncasef #Número de niños de la muestra

# Dibujo de las aproximaciones a las curvas iniciales por splines:
plot(age, hgtm[,1], ylim=c(60,200),col="white",
     xlab="Edad", ylab="Altura", main="Alturas. Por sexos")
# Añade leyenda
legend("topleft",legend=c("chicos","chicas"),col=c(2,4),lwd=1,cex=1)
# Dibuja las graficas
for (i in childrenm){
  lines(agefine, hgtmhat[,i], col=2,pch=1)#Nos fijamos que en el eje x están 
  #los x gorro y en el eje y las aproximaciones suavizando con la muestra
}
for (i in childrenf) {
  lines(agefine, hgtfhat[,i], col=4)
}

# Dibujo de una muestra de lo anterior (5 de cada)
plot(age, hgtm[,1], ylim=c(60,200),col="white",
     xlab="Edad", ylab="Altura", main="Alturas. Por sexos. Muestras elegidas al azar")
legend("topleft",legend=c("chicos","chicas"),col=c(2,4),lwd=3)
for (i in sample(childrenm,5)){
  lines(agefine, hgtmhat[,i], col=2,pch=1)
}
for (i in sample(childrenf,5)) {
  lines(agefine, hgtfhat[,i], col=4)
}

#Dibujo de las derivadas (calculadas sobre los splines)
plot(age, hgtm[,1], ylim=c(-1,20),xlab="Edad", ylab="Speed", main="Velocidad de crecimiento. Por sexos",col="white")
legend("topright",legend=c("chicos","chicas"),col=c(2,4),lwd=3)
abline(h=0, lty=2)
for (i in childrenm){
  lines(agefine, velmhat[,i], col=2)
}
for (i in childrenf) {
  lines(agefine, velfhat[,i], col=4)
}

# Dibujo de una muestra de lo anterior (6 de cada)
plot(age, hgtm[,1], ylim=c(-1.5,20),xlab="Years", ylab="Speed", main="Velocidad de crecimiento. Por sexos. Muestra al azar",col="white")
legend("topright",legend=c("chicos","chicas"),col=c(2,4),lwd=3)
abline(h=0, lty=2)
for (i in c(18,sample(childrenm,5))){
  lines(agefine, velmhat[,i], col=2)
}
for (i in c(9,47,sample(childrenf,4))){#sample(childrenf,5)) {
  lines(agefine, velfhat[,i], col=4);abline(h=0, lty=2)
}


#Dibujo de las segundas derivadas (tambien calculadas sobre los splines)
plot(agefine, accmhat[,1], type="l", ylim=c(-6,6),
     xlab="Edad", ylab="Acceleration", main="Aceleracion del crecimiento. Por sexos",col="white")
legend("topright",legend=c("chicos","chicas"),col=c(2,4),lwd=3)
abline(h=0, lty=2)
for (i in childrenm){
  lines(agefine, accmhat[,i], col=2)
}
for (i in childrenf) {
  lines(agefine, accfhat[,i], col=4)
}

# Dibujo de una muestra de lo anterior (6 de cada)
plot(agefine, accmhat[,1], type="l", ylim=c(-6,6),
     xlab="Edad", ylab="Aceleracion", main="Aceleracion del crecimiento. Por sexos",col="white")
legend("topright",legend=c("chicos","chicas"),col=c(2,4),lwd=3)
abline(h=0, lty=2)
for (i in sample(childrenm,6)){
  lines(agefine, accmhat[,i], col=2)
}
for (i in sample(childrenf,6)) {
  lines(agefine, accfhat[,i], col=4)
}

