import flet as ft
import time
import numpy as np

def funcion_activacion(x):
    return 1 if x >= 0 else 0

def entrenar_neurona(X, y, page, epoca, valor_x1, valor_x2, valor_w1, valor_w2, valor_baias, valor_y, tasa_aprendizaje=0.1, epocas=100):
    n_caracteristicas = X.shape[1]
    pesos = np.zeros(n_caracteristicas)
    bias = 0

    for ep in range(epocas):
        epoca.value = f"Epoca: {ep}"
        pesos_actualizados = False  # Reiniciar en cada época

        for i in range(X.shape[0]):
            # Actualizar los valores en pantalla
            valor_x1.value = str(X[i][0])
            valor_x2.value = str(X[i][1])
            valor_w1.value = f"* {pesos[0]:.2f}"
            valor_w2.value = f"* {pesos[1]:.2f}"
            valor_baias.value = f"Bias: {bias:.2f}"
            
            z = np.dot(pesos, X[i]) + bias
            y_pred = funcion_activacion(z)
            error = y[i] - y_pred

            if error != 0:  # Actualizar pesos solo si hay error
                pesos += tasa_aprendizaje * error * X[i]
                bias += tasa_aprendizaje * error
                pesos_actualizados = True
                page.update()

            valor_y.value = str(y_pred)
            page.update()
            time.sleep(0.7)

        if not pesos_actualizados:  # Si no hubo actualizaciones, convergió
            epoca.value = "Convergencia alcanzada"
            page.update()
            break

    return pesos, bias

# Datos de entrada para compuerta lógica AND
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 0, 0, 1])

def predecir(input_1, input_2, pesos, bias):
    X_input = np.array([input_1, input_2])
    z = np.dot(pesos, X_input) + bias
    return funcion_activacion(z)

def main(page: ft.Page):
    imagen_neurona = ft.Image(src="neurona.png", width=700, height=700)
    epoca = ft.Text(value="Epoca: ", left=40, top=30, size=30)
    valor_x1 = ft.Text(value="0", left=50, top=190, size=30)
    valor_w1 = ft.Text(value="* 0", left=75, top=190, size=30)
    valor_x2 = ft.Text(value="0", left=210, top=185, size=30)
    valor_w2 = ft.Text(value="* 0", left=235, top=185, size=30)
    valor_baias = ft.Text(value="Bias: 0", left=240, top=270, size=25)
    valor_y = ft.Text(value="0", left=600, top=170, size=30)
    boton_entrenar = ft.ElevatedButton("Entrenar", left=600, top=40)
    input_1 = ft.TextField(hint_text="Input 1")
    input_2 = ft.TextField(hint_text="Input 2")
    boton_predecir = ft.ElevatedButton("Predecir")
    valor_prediccion = ft.Text(value="Predicción: 0", size=30)

    stack_control = ft.Stack([
        imagen_neurona,
        boton_entrenar,
        epoca,
        valor_x1,
        valor_w1,
        valor_x2,
        valor_w2,
        valor_baias,
        valor_y
    ])
    
    row_prediccion = ft.Row(controls=[input_1, input_2, boton_predecir])
    page.add(stack_control, row_prediccion, valor_prediccion)

    # Variables para almacenar los pesos y el bias entrenados
    pesos_entrenados = None
    bias_entrenado = None

    def entrenar(event):
        nonlocal pesos_entrenados, bias_entrenado
        pesos_entrenados, bias_entrenado = entrenar_neurona(
            X, y, page, epoca, valor_x1, valor_x2, valor_w1, valor_w2, valor_baias, valor_y
        )

    def predecir_funcion(event):
        if pesos_entrenados is not None and bias_entrenado is not None:
            input_1_val = int(input_1.value)
            input_2_val = int(input_2.value)
            pred = predecir(input_1_val, input_2_val, pesos_entrenados, bias_entrenado)
            valor_prediccion.value = f"Predicción: {pred}"
            page.update()

    boton_entrenar.on_click = entrenar
    boton_predecir.on_click = predecir_funcion

ft.app(target=main)
