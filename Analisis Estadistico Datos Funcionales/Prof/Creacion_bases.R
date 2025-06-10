library("fda.usc")

baseF <- create.fourier.basis(c(0,2*pi), nbasis = 3)

baseF$names

data(tecator)
tecator
