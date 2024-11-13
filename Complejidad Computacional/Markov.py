import warnings

class algoritmo_de_Markov:
    def __init__(self, reglas, alfabeto=None):
        if alfabeto is None:
            self.alfabeto = set([elem for regla in reglas for elem in regla[:2]])
        else:
            self.alfabeto = set(alfabeto)
        self.reglas = reglas
        self._check_reglas()

    def _check_reglas(self):
        num_regla = 1
        for patron, reemplazo, ind_terminal in self.reglas:
            for i in patron:
                if i not in self.alfabeto:
                    raise ValueError(f"Regla {num_regla}: El símbolo '{i}' no pertenece al alfabeto")
            for j in reemplazo:
                if j not in self.alfabeto and j != '':
                    raise ValueError(f"Regla {num_regla}: El símbolo '{j}' no pertenece al alfabeto")
            num_regla += 1

    def _check_string(self, string):
        for i in string:
            if i not in self.alfabeto:
                raise ValueError(f"String: El símbolo '{i}' no pertenece al alfabeto")

    def exec_string(self, string, longitud_palabra=1000, verbose=False):
        self._check_string(string)

        while True:
            aplicada = False
            for num_regla, (patron, reemplazo, ind_terminal) in enumerate(self.reglas, start=1):
                pos = string.find(patron)
                if pos != -1:
                    string = string[:pos] + reemplazo + string[pos + len(patron):]
                    aplicada = True
                    if verbose:
                        print(f"Estado string: {string}")
                        print(f'Se aplica la regla {num_regla}: "{patron}" -> "{reemplazo}"')
                    if ind_terminal:
                        if verbose:
                            print("Regla terminal aplicada, deteniendo ejecución.")
                        return string  # Si es terminal, termina aquí
                    break  # Reinicia desde la primera regla

            if len(string) > longitud_palabra:
                if verbose:
                    print("La palabra ha llegado al limite")
                break

            if not aplicada:
                # Si no se aplicó ninguna regla en este ciclo, termina la ejecución
                if verbose:
                    print("No se ha podido aplicar ninguna regla más")
                return string

# Diccionario de algoritmos de Markov
algoritmos_markov = {
    # 1. Algoritmo para L = { 0^n 1^n 2^n | n ≥ 1 }
    'igual_cantidad': {
        'alfabeto': "012XYZ",
        'reglas': [
            ("S", "X", False),
            ("1", "Y", False),
            ("2", "Z", False),
            ("XYZ", "", False),
            ("X", "0", False),
            ("Y", "1", False),
            ("Z", "2", False)
        ]
    },
    # 2. Algoritmo para palíndromos sobre {0,1,2}
    'palindromo': {
        'alfabeto': "012ABC",
        'reglas': [
            ("0", "A0", False),
            ("1", "B1", False),
            ("2", "C2", False),
            ("0A", "A", False),
            ("1B", "B", False),
            ("2C", "C", False),
            ("A", "", False),
            ("B", "", False),
            ("C", "", False)
        ]
    },
    # 3. Algoritmo para L = { ww | w ∈ {0,1,2}* }
    'duplicacion': {
        'alfabeto': "012XYZ",
        'reglas': [
            ("0", "X0X", False),
            ("1", "Y1Y", False),
            ("2", "Z2Z", False),
            ("X X", "", False),
            ("Y Y", "", False),
            ("Z Z", "", False),
            ("X", "", False),
            ("Y", "", False),
            ("Z", "", False)
        ]
    },
    # 4. Algoritmo para L = { 0^n 1^n | n ≥ 1 }
    'igual_cantidad_0s_1s': {
        'alfabeto': "01XY",
        'reglas': [
            ("0", "X", False),
            ("1", "Y", False),
            ("XY", "", False),
            ("X", "0", False),
            ("Y", "1", False)
        ]
    }
}

# Agregar el nuevo algoritmo al diccionario
algoritmos_markov['nuevo_algoritmo'] = {
    'alfabeto': 'WBbScCXa',         
    'reglas': [
        ('S', 'abC', False),
        ('S', 'aSBC', False),
        ('CB', 'WB', False),
        ('WB', 'WX', False),
        ('WX', 'BX', False),
        ('BX', 'BC', False),
        ('bB', 'bb', False),
        ('bC', 'bc', False),
        ('cC', 'cc', False)
    ]
}

# Ejemplo de uso
if __name__ == "__main__":
    # Seleccionar el algoritmo que deseas utilizar
    nombre_algoritmo = 'nuevo_algoritmo'  # Cambia esto si deseas probar otro algoritmo

    # Obtener las reglas y el alfabeto del algoritmo seleccionado
    alfabeto = algoritmos_markov[nombre_algoritmo]['alfabeto']
    reglas = algoritmos_markov[nombre_algoritmo]['reglas']

    # Crear una instancia del algoritmo de Markov
    markov = algoritmo_de_Markov(reglas=reglas, alfabeto=alfabeto)

    # Probar con algunas cadenas
    cadenas = ["S", "c", "S", "B"]

    for cadena in cadenas:
        print(f"Probando cadena: {cadena}")
        resultado = markov.exec_string(cadena, verbose=True)
        print(f"Resultado final: {resultado}")
        print("-" * 40)
