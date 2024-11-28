class Polinomios :

  def __init__(self, L):
    self.coeffs = copy(L) #---- PROBLEMAS, argumentos por referencia.
    self.limpia()
    self.len = len(self.coeffs)
    self.grado = self.len - 1

  def limpia(self):
    while self.coeffs and self.coeffs[-1] == 0:
      self.coeffs.pop()

  def __repr__(self):
    return self.coeffs.__repr__()

  def __add__(self,other):
    s = max(self.len,other.len)
    L1 = self.coeffs + [0]*(s-self.len)
    L2 = other.coeffs + [0]*(s-other.len)
    return Polinomios([ L1[i] + L2[i] for i in range(s) ])

  def __add2__(self,other):
    s = min(self.len,other.len)
    C = [self.coeffs[i] + other.coeffs[i] for i in range(s) ]
    if self.len < other.len:
      return Polinomios (C + other.coeffs[s:])
    else:
      return Polinomios (C + self.coeffs[s:])

  def __neg__(self):
    return Polinomios ([- F for F in self.coeffs])

  def __sub__(self,other):
    return self + (-other)

  def __eq__(self,other):
    return self.coeffs == other.coeffs

  def __mul__(self,other):
    if not self.coeffs or not other.coeffs:
      return Polinomios([])
    return Polinomios(do_schoolbook(self,other))

def do_schoolbook(f,g):
  n = len(f)
  m = len(g)
  C = [anillo(0)] * (n+m-1)
  for i in range(n):
    for j in range(m):
        C[i+j] = C[i+j] + f[i]*g[j]
  return C

def do_karatsuba(f,g, K_threshold=8):
  n = len(f)
  n0 = n //2
  n1 = n - n0
  if n < K_threshold:
    return do_schoolbook(f,g)
  f0 = f[:n0] # tamaño n0
  f1 = f[n0:]  # tamaño n1
  g0 = g[:n0] # tamaño n0
  g1 = g[n0:]  # tamaño n1
  u = do_karatsuba(f0,g0, K_threshold) # tamaño 2*n0-1
  v = do_karatsuba(f1,g1, K_threshold) # tamaño 2*n1-1
  # Usamos f1, g1 como f0+f1,g0+g1 para evitar crear más listas
  # Fijaos que n1 >= n0
  for i in range(n0):
    f1[i] = f1[i]+f0[i]
    g1[i] = g1[i]+g0[i]
  w = do_karatsuba(f1,g1, K_threshold) # tamaño 2*n1-1
  # resto u y v a w, el problema es que los tamaños pueden ser distintos
  for i in range(2*n0-1):
    w[i] = w[i] - u[i] - v[i]
  for i in range(2*n0-1,2*n1-1):
    w[i] = w[i] - v[i]
  #C = [0] * (2*n-1)
  #for i in range(2*n0-1):
  #  C[i] = C[i] + u[i]
  #  C[n0+i] = C[n0+i] + w[i]
  #  C[2*n0+i] = C[2*n0+i] + v[i]
  #for i in range(2*n0-1,2*n1-1):
  #  C[n0+i] = C[n0+i] + w[i]
  #  C[2*n0+i] = C[2*n0+i] + v[i]
  #
  # u contiene los monomios de 0 a 2*n0-2
  # v contiene los monomios de 2*n0 a 2*n-1
  # solo nos falta el monomio 2*n0-1
  # podemos usarlo para evitar sumas en C
  C = u +[anillo(0)] +v
  for i in range(2*n1-1):
    C[n0+i] = C[n0+i] + w[i]
  return C

def do_karatsuba_different_size(left: list, right: list, K_threshold: int=8) -> list:
    """
    Multiplicación de dos polinomios de diferente grado, usando una
    estrategia de división del polinómio mayor en partes de tamaño
    del polinomio menor. Así, poder aplicar do_karatsuba a las partes.

    INPUT:

    - ``left``  -- representación de polinomio como lista
    - ``right`` -- representación de polinomio como lista
    - ``K_threshold`` -- Entero, se usa como criterio para usar la 
    multiplicación de la escuela si el el grado de alguno de los 
    polinómios es menor que él.

    TESTS:

    sage: do_karatsuba_different_size([anillo(1), anillo(2)], [anillo(3), anillo(4)])  # Grados iguales
    [3, 10, 8]

    sage: do_karatsuba_different_size([anillo(1), anillo(2), anillo(3)], [anillo(4), anillo(5)])  # n > m
    [4, 13, 22, 15]

    sage: do_karatsuba_different_size([anillo(3), anillo(4)], [anillo(1), anillo(2), anillo(3)])  # n < m
    [3, 10, 17, 12]

    sage: do_karatsuba_different_size([], [anillo(1), anillo(2), anillo(3)])  # Caso vacío
    []

    sage: do_karatsuba_different_size([anillo(1)], [anillo(1), anillo(2), anillo(3)])  # Caso n = 1
    [1, 2, 3]

    sage: do_karatsuba_different_size([anillo(1), anillo(2), anillo(3)], [anillo(1)])  # Caso m = 1
    [1, 2, 3]

    sage: do_karatsuba_different_size([anillo(1), anillo(2), anillo(3)], [anillo(4), anillo(5)], K_threshold=1)  # Caso K_threshold bajo
    [4, 13, 22, 15]

    """
    n: int= len(left); m: int= len(right)
    if n == 0 or m == 0:
        return []
    if n == 1:
        c = left[0]
        return [c*a for a in right]
    if m == 1:
        c = right[0]
        return [a*c for a in left] # beware of noncommutative rings
    
    if n <= K_threshold or m <= K_threshold or K_threshold==1 or K_threshold==2:
        return do_schoolbook(left, right)
    if n == m:
        return do_karatsuba(left, right, K_threshold)
    if n > m:
        # left is the bigger list
        # n is the bigger number
        q = n // m
        r = n % m
        output = do_karatsuba(left[:m], right, K_threshold)
        for i in range(1, q): #from 1 <= i < q:
            mi = m*i
            carry = do_karatsuba(left[mi:mi+m], right, K_threshold)
            for j in range(m-1):
                output[mi+j] = output[mi+j] + carry[j]
            output.extend(carry[m-1:])
        if r:
            mi = m*q
            carry = do_karatsuba_different_size(left[mi:], right, K_threshold)
            for j in range (m-1):
                output[mi+j] = output[mi+j] + carry[j]
            output.extend(carry[m-1:])
        return output
    else:
        # n < m, I need to repeat the code due to the case
        # of noncommutative rings.
        q = m // n
        r = m % n
        output = do_karatsuba(left, right[:n], K_threshold)
        for i in range(1,q): #from 1 <= i < q:
            mi = n*i
            carry = do_karatsuba(left, right[mi:mi+n], K_threshold)
            for j in range(n-1):
                output[mi+j] = output[mi+j] + carry[j]
            output.extend(carry[n-1:])
        if r:
            mi = n*q
            carry = do_karatsuba_different_size(left, right[mi:], K_threshold)
            for j in range(n-1):
                output[mi+j] = output[mi+j] + carry[j]
            output.extend(carry[n-1:])
        return output


NUM_SUMA = 0
NUM_PRODUCTO = 0

class anillo:
    def __init__(self, valor):
        self.valor = valor

    def __repr__(self):
        return repr(self.valor)

    def __add__(self, otro):
        global NUM_SUMA 
        NUM_SUMA = NUM_SUMA + 1
        return anillo(self.valor + otro.valor)

    def __sub__(self,otro):
        global NUM_SUMA 
        NUM_SUMA = NUM_SUMA + 1
        return anillo(self.valor - otro.valor)

    def __mul__(self, otro):
        global NUM_PRODUCTO
        NUM_PRODUCTO = NUM_PRODUCTO + 1
        return anillo(self.valor * otro.valor)
