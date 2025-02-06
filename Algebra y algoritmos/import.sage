def fin_distinct_degree_descomp(f) -> list:
    R=f.parent()
    F=f.base_ring()
    q=F.cardinality()
    print('q:', q)

    list_g:list=[]
    i: int=0
    x=R([0,1])
    h=x
    while f != 1:
        i+=1
        print(i)
        print('h:', h^q)
        h= (h^q)%f
        print('g:', gcd(h-x,f))
        g=gcd(h-x,f)
        list_g.append(g)
        print('f:', f/g)
        f=f/g
        print(list_g,'---------------',sep='\n')
    return list_g
