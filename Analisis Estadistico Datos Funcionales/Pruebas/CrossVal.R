library("fda.usc")

f <- function(x) sin(x)

N <- 200
tipo_ruido <- "uniforme"  # o "normal"

if (tipo_ruido == "normal") {
  r <- rnorm(n = N, mean = 0, sd = 0.4)
} else if (tipo_ruido == "uniforme") {
  r <- runif(n = N, min = -0.25, max = 0.25)
}


x <- seq(0, 2*pi, length.out = N)
yr <- f(x)+r


NB_max <- 50
NB_seq <- 3:NB_max
colors <- rainbow(NB_max-2)  # colores para las curvas



plot(x, f(x), type = "l", col = "black", lwd = 2, ylim = c(-1.5, 1.5),
     main = "Aproximaciones con bases de Fourier", xlab = "x", ylab = "f(x)")

for (i in seq_along(NB_seq)) {
  nb <- NB_seq[i]
  baseF <- create.fourier.basis(c(0, 2*pi), nbasis = nb)
  fd_obj <- smooth.basis(x, yr, baseF)
  lines(x, eval.fd(x, fd_obj$fd), col = colors[i], lwd = 1.5)
}

legend("topright",
       legend = c("f(x) = sin(x)", paste("nb =", NB_seq)),
       col = c("black", colors),
       lwd = 2,
       bg = "white")
