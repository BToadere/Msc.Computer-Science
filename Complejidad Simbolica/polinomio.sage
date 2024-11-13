
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
    return Polinomios(do_schoolbook(f,g))

def do_schoolbook(f,g):
  n = len(f)
  m = len(g)
  C = [0] * (n+m-1)
  for i in range(n):
    for j in range(m):
        C[i+j] = C[i+j] + f[i]*g[j]
  return C

def do_karatsuba_clase(f,g):
  n0 = len(f)
  n = len(f)
  hago_pop = 0
  if n < 50 :
    return do_schoolbook(f,g)
  if n % 2 == 1:
    f = f+[0]
    g = g+[0]
    n = n+1
    hago_pop=1

  f0 = f[0:n//2]
  f1 = f[n//2:]
  g0 = g[0:n//2]
  g1 = g[n//2:]
  u = do_karatsuba(f0,g0)
  v = do_karatsuba(f1,g1)
  sf = [f0[i]+f1[i] for i in range(n//2)  ]
  sg = [g0[i]+g1[i] for i in range(n//2)  ]
  w = do_karatsuba(sf,sg)
  medio = [ w[i] - u[i] - v[i]  for i in range(len(w))  ]
  C = [0] * (2*n-1)
  for i in range(len(u)):
    C[i] = C[i] + u[i]
    C[n//2+i] = C[n//2+i] + medio[i]
    C[n+i] = C[n+i] + v[i]
  return C[:n0*2-1]

def do_karatsuba(f,g):
  n = len(f)
  n0 = n //2
  n1 = n - n0
  if n < 32 :
    return do_schoolbook(f,g)
  f0 = f[:n0] # tamaño n0
  f1 = f[n0:]  # tamaño n1
  g0 = g[:n0] # tamaño n0
  g1 = g[n0:]  # tamaño n1
  u = do_karatsuba(f0,g0) # tamaño 2*n0-1
  v = do_karatsuba(f1,g1) # tamaño 2*n1-1
  # Usamos f1, g1 como f0+f1,g0+g1 para evitar crear más listas
  # Fijaos que n1 >= n0
  for i in range(n0):
    f1[i] = f1[i]+f0[i]
    g1[i] = g1[i]+g0[i]
  w = do_karatsuba(f1,g1) # tamaño 2*n1-1
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
  C = u +[0] +v
  for i in range(2*n1-1):
    C[n0+i] = C[n0+i] + w[i]
  return C

