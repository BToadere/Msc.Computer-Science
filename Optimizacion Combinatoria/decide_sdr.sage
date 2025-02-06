def naive_decide_sdr_in_family(fam: list[list]) -> None:
    """
    Finds an SDR (System of Distinct Representatives) in a family of sets using the matching theorem 
    for bipartite graphs. The function builds:
    - `U`, the set of all distinct elements present in the subsets of the family.
    - `W`, the set of all subsets in the family.

    Then, it checks if there exists a complete matching between `U` and `W`, where edges represent 
    the membership relationship between elements of `U` and subsets of `W`.

    Args:
        fam (list of lists): A family of sets, where each set is represented as a list of elements.

    Prints:
        If no perfect matching exists, it displays:
            - The subset `s` that violates the condition.
            - Its neighbors `ns` and their respective cardinalities.
        If a perfect matching exists, it indicates that the matching is valid.

    Returns:
        None

    Examples:
        sage: naive_find_sdr_in_family([['a','d'],['a','c'],['b','c'],['c','d']])
        By König's theorem, a perfect matching exists.

        sage: naive_find_sdr_in_family([[1,2,3,4,5,6],[1,3,4],[1,4,7],[2,3,5,6],[3,4,7],[1,3,4,7],[1,3,7]])
        By König's theorem, no perfect matching exists:
        The subset s (#s=3): {2, 5, 6}
        Has 2 neighbors:
        {2, 3, 5, 6}
        {1, 2, 3, 4, 5, 6}
        """
    # Create the universal set U
    U = Set([elem for sublist in fam for elem in sublist])

    # Create a set of sets W from the family
    W = Set(Set(sublist) for sublist in fam)

    # Generate all subsets of U
    S = U.subsets()

    # Iterate over all subsets in S
    for s in S:
        # Build the set of neighbors of s
        #ns = Set()  # Inicializar conjunto vacío de vecinos de s
        #for element in s:
        #    for w in W:
        #        if element in w:  # Verificar si el elemento pertenece al subconjunto w
        #            ns = ns.union(Set([w]))  # Unión de conjuntos

        ns = Set(w for w in W if any(element in w for element in s))
        scard = s.cardinality()
        nscard = ns.cardinality()

        # Check the matching condition
        if scard > nscard:
            print("By König's theorem, no perfect matching exists:")
            print(f"The subset s (#s={scard}): {s}")
            print(f"Has {nscard} neighbors:")
            print(*ns, sep='\n')
            return

    # Successful case
    print("By König's theorem, a perfect matching exists.")
