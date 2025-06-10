install.packages("HSAUR")
library("HSAUR")

#Cargamos el conjunto de datos sobre la final olímpica de Seúl 1988 del
#Heptathlon.
Hep <- heptathlon

View(Hep)
summary(Hep)
head(Hep)

#Para que todos los "scores" apunten en la misma dirección
Hep$hurdles = max(Hep$hurdles) - Hep$hurdles
Hep$run200m = max(Hep$run200m) - Hep$run200m
Hep$run800m = max(Hep$run800m) - Hep$run800m

#Cogemos todas las variable smenos la 8 pm es el resutado
HepS <- Hep[,-8]

#Matriz de covarianzas. Observamos que la variable "Javelin" no está correlada
#con las demás. Observamos, por ejemplo, la relación que hay entre las variables
#"Hurdles" y "LongJump".
cor(HepS)

#Dibujamos las variables por pares. Observamos la columna de "Javelin".
#Nos sirve para plotear a pares
pairs(HepS, main = "Scatterplot de todas las pruebas del Heptathlon",
      col = "blue")

#Si trabajamos sin escalar los datos, los resultados de la prueba de 800m
#son números mayores que las demás pruebas, por lo que obtendría un peso
#desproporcionado.
#Utilizamos la función "prcomp" e indicamos que escale los datos.
hep_PCA <- prcomp(HepS,scale = TRUE)
print(hep_PCA)
summary(hep_PCA)

#Mostramos los coeficientes de las variables originales de la primera 
#componente. Observamos que esta componente representa un poco todas las 
#disciplinas, salvo el lanzamiento de jabalina.
#El signo de los coeficientes no es importante aquí. Pensamos en los números
#en valor absoluto, ya que esta teoría se construye para explicar la mayor
#cantidad de varianza posible.
hep_PCA$rotation[,1]

#El siguiente comando nos muestra el "score" de las 25 competidoras en la
#primera componente. Observamos que las que tienen el score más alto son...
#el oro, la plata y el bronce, en orden. Claro... esta componente representa 
#un poco todas las habilidades ateléticas, exceptuando la jabalina. Es el valor
#de y_1 para todas las atletas
predict(hep_PCA)[,1]

# Esto es lo mismo pero quitando lso nombres
scoresPC1 <- rep(0,25)
for(i in 1:25){
  scoresPC1[i] <- predict(hep_PCA)[,1][[i]]
}

#Si calculamos el coeficiente de correlación entre el "score" de las 25 
#atletas en la PC1 y el resultado de la prueba, el resultado es 
#aproximadamente -0.99.
cor(scoresPC1,heptathlon$score)

#Esto significa que explicamos gran cantidad de la varianza relevante con 
#nuestra primera componente.
plot(scoresPC1,heptathlon$score)

summary(hep_PCA)
plot(hep_PCA)
plot(hep_PCA,type = "lines")


#Observamos los coeficientes de la segunda componente principal. Se puede
#observar que tiene coeficiente marcadamente negativo en la variable "Javelin"
#por lo que esta componente, lo que mide sobretodo, es la habilidad en el
#lanzamiento de Jabalina. También influyen, en menor medida, el lanzamiento
#de peso y los 200m.
hep_PCA$rotation[,2]

#Observamos que Jackie Joyner-Kersee es la mejor, seguida de John y Behmer
#(las atletas de la RDA que quedaron plata y bronce). Observamos también que 
#Choubenkova es peor en líneas generales que estas, pero es mejor que ellas
#en lanzamiento de jabalina. Por otro lado, la belga Hautenauve es peor que el 
#resto, en líneas generales. Sobretodo, en jabalina, que es la peor, por eso 
#obtiene el mayor "score" en la PC2 (eje Y).
biplot(hep_PCA,col = c("gray","steelblue"),cex = c(0.5,1.3))
