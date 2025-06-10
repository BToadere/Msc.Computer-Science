library("fda.usc")

data(tecator)
names(tecator)
absorp=tecator$absorp.fdata


ind <- 1:165

tt <- absorp[["argvals"]]
y <- tecator$y$Fat[ind]
x <- absorp[ind,]



# Vamos con las derivadas

x.d1 <- fdata.deriv(x, nbasis =19, nderiv=1)
x.d2 <- fdata.deriv(x, nbasis =19, nderiv=2)


plot(x,col=y)
plot(x.d1, col=y)
plot(x.d2, col=y)



# Clasificamos por colores
color =2
colores = 0*y+color
cortes=c(10,20)
for (ic in cortes){
  colores[y>ic]=colores[y>ic]+1
}

plot(x,col=colores)
plot(x.d1, col=colores)
plot(x.d2, col=colores)


rangett <- absorp$rangeval

basis1 <- create.fourier.basis(rangeval = rangett, nbasis=5)
# functional regression scalar response
res.Fou.basis0 <- fregre.basis(x,y,basis.x = basis1)
summary(res.Fou.basis0)


x.test =absorp[-ind,]
y.test=tecator$y$Fat[-ind]


y.pred.Fou.0 = predict(res.Fou.basis0,x.test)

error.Fou.0=(sum((y.test-y.pred.Fou.0)^2))^0.5/length(y.test)
