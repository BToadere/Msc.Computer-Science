#-----------------------------------------------------------------------------
# FUNCIÓN: k-Means Podado Imparcial (Impartial Trimmed k-Means)
#-----------------------------------------------------------------------------
# OBJETIVO:
#   Agrupa datos funcionales (o multivariantes) según la distancia empleada
#   en 'k' clústeres, descartando (podando) una proporción 'alfa' de las 
#   observaciones más atípicas. Los centroides son siempre observaciones reales.
#
# PARÁMETROS:
#   - data: Un data frame o matrix donde cada fila es una observación.
#   - k: El número de clústeres deseado.
#   - alfa: La proporción de datos a podar (ej: 0.1 para el 10%).
#   - max_iteraciones: Número máximo de ciclos para evitar bucles infinitos.
#
# RETORNA:
#   Una lista con la asignación de clústeres, los centroides, los
#   índices de los datos podados y un resumen de los tamaños.
#-----------------------------------------------------------------------------

itkmeans <- function(data, k, alfa, max_iteraciones = 1000) {
  
  # Sub-función auxiliar para calcular la matrizz de distancias (En etse caso euclideas)
  matrix_d_2 <- function(conjunto_a, conjunto_b) {
    matrix_a <- as.matrix(conjunto_a)
    matrix_b <- as.matrix(conjunto_b)
    
    # (a-b)^2 = a^2 + b^2 - 2ab
    norma_a <- rowSums(matrix_a^2)
    norma_b <- rowSums(matrix_b^2)
    
    dist_cuadrado <- matrix(norma_a, nrow = nrow(matrix_a), ncol = nrow(matrix_b)) + 
      matrix(norma_b, nrow = nrow(matrix_a), ncol = nrow(matrix_b), byrow = TRUE) - 
      2 * tcrossprod(matrix_a, matrix_b)
    
    # Aseguramos que no haya valores negativos por errores de precisión numérica
    return(pmax(dist_cuadrado, 0))
  }
  
  num_observaciones <- nrow(data)
  num_a_podar <- floor(alfa * num_observaciones)
  
  # # Fijamos una semilla
  # set.seed(111)
  
  # Elegimos 'k' centroides iniciales de forma aleatoria de entre los datos
  indices_centroides_actuales <- sample(1:num_observaciones, k)
  
  # Vector para guardar la asignación de grupo de cada observación (0 si no está asignado)
  grupos <- rep(0, num_observaciones)
  
  for (i in 1:max_iteraciones) {
    
    indices_centroides_antiguos <- indices_centroides_actuales
    datos_centroides <- data[indices_centroides_actuales, , drop = FALSE]
    
    # Parte de Trimming
    # Calculamos la distancia de cada punto a todos los centroides
    distancias_a_centroides <- matrix_d_2(data, datos_centroides)
    
    # Para cada punto, encontramos su distancia al centroide MÁS CERCANO
    distancias_minimas <- apply(distancias_a_centroides, 1, min)
    
    # Identificamos las observaciones que tienen la mayor distancia mínima
    if (num_a_podar > 0) {
      umbral_poda <- sort(distancias_minimas, decreasing = TRUE)[num_a_podar]
      indices_podados <- which(distancias_minimas >= umbral_poda)[1:num_a_podar]
    } else {
      indices_podados <- integer(0)
    }
    
    # Las observaciones con las que trabajaremos son las no podadas
    indices_no_podados <- setdiff(1:num_observaciones, indices_podados)
    
    # Parte de ASIGNACIÓN 
    nuevos_grupos <- rep(0, num_observaciones)
    if (length(indices_no_podados) > 0) {
      # Asignamos cada observación no podada al clúster de su centroide más cercano
      asignaciones <- apply(distancias_a_centroides[indices_no_podados, , drop = FALSE], 1, which.min)
      nuevos_grupos[indices_no_podados] <- asignaciones
    }
    grupos <- nuevos_grupos
    
    # Parte de ACTUALIZACIÓN de Centroides
    indices_nuevos_centroides <- integer(k)
    for (j in 1:k) {
      # Identificamos los miembros de cada grupo
      miembros_del_grupo_idx <- which(grupos == j)
      
      ### Manejo de ERROR: Clústeres vacíos.
      # Para evitar que el calculo de distancias de error por un cluster vacio 
      # le asignamos como centroide uno de los puntos más lejanos y pasamos al siguiente clúster.
      if (length(miembros_del_grupo_idx) == 0) {
        indices_nuevos_centroides[j] <- order(distancias_minimas, decreasing = TRUE)[j]
        next
      }
      
      # El nuevo centroide es el MEDOIDE: la observación que minimiza la suma
      # de distancias a las demás observaciones DENTRO de su clúster
      distancias_intra_grupo <- matrix_d_2(data[miembros_del_grupo_idx, , drop = FALSE], 
                                           data[miembros_del_grupo_idx, , drop = FALSE])
      suma_distancias <- rowSums(distancias_intra_grupo)
      indice_local_medoide <- which.min(suma_distancias)
      
      # Guardamos el índice global del nuevo centroide
      indices_nuevos_centroides[j] <- miembros_del_grupo_idx[indice_local_medoide]
    }
    indices_centroides_actuales <- indices_nuevos_centroides
    
    # Comprobación de Convergencia
    if (all(sort(indices_centroides_actuales) == sort(indices_centroides_antiguos))) {
      cat(paste("Convergencia alcanzada en la iteración", i, "\n"))
      break
    }
    if (i == max_iteraciones) {
      cat("Se ha alcanzado el número máximo de iteraciones.\n")
    }
  }
  
  return(list(
    cluster = grupos,
    centers = data[indices_centroides_actuales, , drop = FALSE],
    trimmed = indices_podados,
    size = table(grupos[grupos != 0]),
    trimmed_size = length(indices_podados)
  ))
}


# Cargar Datos y Definir Parámetros
library(fda.usc)
data(tecator)
absorp_matrix <- tecator$absorp$data

k_clusters <- 7
alfa_trim <- 0.08


# Ejecución y Análisis de Resultados
cat(paste("\nEjecutando ITkM implementado con k =", k_clusters, "y alpha =", alfa_trim, "...\n"))
itkm_result <- itkmeans(data = absorp_matrix, k = k_clusters, alfa = alfa_trim)

# Resumen numérico
cat("Tamaño de los clústeres:\n"); print(itkm_result$size)
cat(paste("Número de observaciones podadas:", itkm_result$trimmed_size, "\n"))

# Definición de una paleta de colores para los gráficos
cluster_colors <- hcl.colors(k_clusters, palette = "Zissou 1")
if (k_clusters > length(cluster_colors)) {
  warning(paste("k es mayor que la paleta de colores definida. Se reciclarán los colores."))
  cluster_colors <- rep(cluster_colors, length.out = k_clusters)
}


#--- Visualización de Resultados ----

# Gráfica base con todas las observaciones en gris.
plot(tecator$absorp, 
     col = "grey80",
     lty = 1,
     main=paste("Resultado de ITkM (k=", k_clusters, ", alpha=", alfa_trim, ")", sep=""),
     xlab="Longitud de onda (nm)",
     ylab="Absorbancia")

# Superponer cada clúster
for (j in 1:k_clusters) {
  cluster_indices <- which(itkm_result$cluster == j)
  if (length(cluster_indices) > 0) {
    lines(tecator$absorp[cluster_indices], col = cluster_colors[j], lty = 1)
  }
}

# Superponer los datos podados
if (length(itkm_result$trimmed) > 0) {
  lines(tecator$absorp[itkm_result$trimmed], col="black", lty=2, lwd=2)
}

# Superponer los CENTROIDES
centroides_fdata <- fdata(itkm_result$centers, argvals = tecator$absorp$argvals)
lines(centroides_fdata, col = "brown", lwd = 3, lty = 3)


# Crear una leyenda
legend_text <- c(
  paste0("Clúster y Centroide ", 1:k_clusters),
  paste0("Datos Podados (", alfa_trim * 100, "%)")
)
legend_colors <- c(
  cluster_colors,
  "black"
)
legend_lty <- c(
  rep(1, k_clusters),
  2
)
legend_lwd <- c(
  rep(1.5, k_clusters), # Grosor para miembros del clúster
  2                     # Grosor para datos podados
)

legend("topleft", 
       legend = legend_text,
       col = legend_colors, 
       lty = legend_lty,
       lwd = legend_lwd,
       bty = "n",
       cex = 0.8)
