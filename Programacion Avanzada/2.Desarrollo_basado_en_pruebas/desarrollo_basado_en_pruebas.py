def romanum(textorom):
    valores={'M':1000,'D':500,'C':100, 'L':50, 'X': 10, 'V': 5, 'I': 1}
    num=0
    for letra in textorom:
      num+=valores[letra]
    return num

if __name__=='__main__':
   romanum('Z')