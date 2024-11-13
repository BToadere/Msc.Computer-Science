from collections import deque

class evaluador():
    def __init__(s, operacion):
        s.cola = deque(operacion.split())
        s.operadores = deque()
        s.operandos = deque()
        s.precendencia = ['*', '/', '+', '-', '(', ')']

    def es_binario(s, operador):
        if operador in s.precendencia[0:-2]:
            return True
        else:
            return False
        
    def evaluador(s):
        
        while s.cola[-1]:

            ele = s.cola.pop()
            if ele[0] == '(':
                s.operadores.append(ele)
            
            elif ele[1] == 'operando':
                s.operandos.append(ele)

            elif s.precendencia.index(ele[0]) <= s.precendencia.index(s.operador[-1][0]):
                up_operador=s.operador.pop()
                if up_operador == '(' and ele[0] != ')':
                    print('Error en la sintaxis del cálculo')
                elif up_operador == '(' and ele[0] == ')':
                    pass
                else:
                    s.operar()
                    
            elif s.precendencia.index(ele[0]) > s.precendencia.index(s.operador[-1][0]):
                s.operadores.append(ele)
            
            elif not s.operador[-1]:
                print(f'El resultado es: {s.operandos.pop()[0]}')
            
            else:
                print('Error en la sintaxis del cálculo')

        return

