library("fda.usc")

# Definición de la función y cardinalidad dominio
f <- function(x) x^3 + x^2 + exp(sin(x))

N <- 200

# Selección tipo de ruido
tipo_ruido <- "normal"  # o "uniforme"
set.seed(123) 
if (tipo_ruido == "normal") {
  r <- rnorm(n = N, mean = 0, sd = 0.4)
} else if (tipo_ruido == "uniforme") {
  r <- runif(n = N, min = -0.25, max = 0.25)
}

# Generación datos
x <- seq(0, 2*pi, length.out = N)
y <- f(x)
yr <- y + r

# Definición cardinalidad máxima base
NB_max <- 101
NB_seq <- seq(from = 3, to = NB_max, by = 2)

# Vector para almacenar el error de LOOCV para cada nb
cv_errors <- numeric(length(NB_seq))

# Loop para evaluar cada nb
for (i in seq_along(NB_seq)) {
  nb <- NB_seq[i]
  baseF <- create.fourier.basis(c(0, 2*pi), nbasis = nb)
  
  errors <- numeric(N)
  
  # Leave-One-Out Cross Validation
  for (j in 1:N) {
    x_train <- x[-j]
    y_train <- yr[-j]
    
    fd_obj <- smooth.basis(x_train, y_train, baseF)
    
    y_pred <- eval.fd(x[j], fd_obj$fd)
    
    errors[j] <- (yr[j] - y_pred)^2
  }
  
  cv_errors[i] <- mean(errors)
  cat("nb =", nb, "ECM =", cv_errors[i], "\n")
}

# Selección mejor cardinalidad
best_index <- which.min(cv_errors)
best_nb <- NB_seq[best_index]
cat("La mejor cardinalidad es nb =", best_nb, "con ECM =", cv_errors[best_index], "\n")

# Ajuste final con mejor nb
base_best <- create.fourier.basis(c(0, 2*pi), nbasis = best_nb)
fd_obj_best <- smooth.basis(x, yr, base_best)
y_aprox <- eval.fd(x, fd_obj_best$fd)



# --- Gráfico final ---
plot(x, y, type = "l", col = "black", lwd = 2, ylim = range(c(yr, y_aprox)),
     main = paste("Aproximación con Fourier (nb =", best_nb, ")"),
     xlab = "x", ylab = "f(x)")
points(x, yr, col = "gray", pch = 16, cex = 0.6)
lines(x, y_aprox, col = "red", lwd = 2)
legend("topleft", legend = c("f(x) original", "Datos con ruido", "Aproximación Fourier"),
       col = c("black", "gray", "red"), lwd = c(2, NA, 2), pch = c(NA, 16, NA), pt.cex = 0.8)
