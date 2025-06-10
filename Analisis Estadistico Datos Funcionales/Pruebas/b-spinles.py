import numpy as np
import matplotlib.pyplot as plt


def cox_de_boor_recursive(t_param, i_basis_idx, k_order, knots_vector, memo_cache):
    """
    Calcula el valor de la función base B-spline B_{i,k}(t) usando la recursión de Cox-de Boor.
    Esta es la implementación central y simplificada.

    Args:
        t_param (float): El valor del parámetro 't' donde se evalúa la función base.
        i_basis_idx (int): Índice de la función base (y del primer nodo t_i relevante).
                           Corresponde al 'i' en B_{i,k}.
        k_order (int): El orden 'k' de la B-spline (grado p = k-1).
        knots_vector (np.array): El vector de nodos completo.
        memo_cache (dict): Diccionario para memoización. Clave: (i_basis_idx, k_order_actual).
    
    Returns:
        float: El valor de B_{i_basis_idx, k_order}(t_param).
    """

    
    if (i_basis_idx, k_order) in memo_cache:
        return memo_cache[(i_basis_idx, k_order)]

    if k_order == 1:
        
        knot_i = knots_vector[i_basis_idx]
        
        
        if i_basis_idx + 1 < len(knots_vector):
            knot_i_plus_1 = knots_vector[i_basis_idx + 1]
            
            if knot_i <= t_param < knot_i_plus_1:
                result = 1.0

            elif t_param == knot_i_plus_1 and knot_i_plus_1 == knots_vector[-1] and knot_i <= t_param:
                 result = 1.0
            else:
                result = 0.0
        else:
            result = 0.0 
        
        memo_cache[(i_basis_idx, k_order)] = result
        return result

    term1_value = 0.0
    
    if (i_basis_idx + k_order - 1) < len(knots_vector) and i_basis_idx < len(knots_vector):
        denominator1 = knots_vector[i_basis_idx + k_order - 1] - knots_vector[i_basis_idx]
        if denominator1 != 0: 
            coeff1 = (t_param - knots_vector[i_basis_idx]) / denominator1
            term1_value = coeff1 * cox_de_boor_recursive(t_param, i_basis_idx, k_order - 1, knots_vector, memo_cache)

    term2_value = 0.0
    
    if (i_basis_idx + k_order) < len(knots_vector) and (i_basis_idx + 1) < len(knots_vector):
        denominator2 = knots_vector[i_basis_idx + k_order] - knots_vector[i_basis_idx + 1]
        if denominator2 != 0: 
            coeff2 = (knots_vector[i_basis_idx + k_order] - t_param) / denominator2
            
            term2_value = coeff2 * cox_de_boor_recursive(t_param, i_basis_idx + 1, k_order - 1, knots_vector, memo_cache)
    
    final_result = term1_value + term2_value
    memo_cache[(i_basis_idx, k_order)] = final_result
    return final_result

def generate_simple_knots(num_total_basis_fns, spline_degree, t_min=0.0, t_max=1.0):
    """
    Genera un vector de nodos "abierto" (clamped) simple para visualización.
    Longitud del vector de nodos = num_total_basis_fns + order.
    """
    spline_order = spline_degree + 1
    
    if num_total_basis_fns < spline_order:
        if num_total_basis_fns == spline_order: 
             return np.concatenate((np.full(spline_order, t_min), np.full(spline_order, t_max)))
        else: 
              
            knot_vector_len = num_total_basis_fns + spline_order
            return np.array([t_min]* (knot_vector_len // 2) + [t_max]*(knot_vector_len - knot_vector_len // 2) )

    
    num_internal_segments_plus_endpoints = num_total_basis_fns - spline_order + 2
    
    if num_internal_segments_plus_endpoints < 2: 
        internal_knot_values_for_linspace = np.array([]) 
    else:
        internal_knot_values_for_linspace = np.linspace(t_min, t_max, num_internal_segments_plus_endpoints)
    
    knots = np.concatenate((
        np.full(spline_order, t_min), 
        internal_knot_values_for_linspace[1:-1], 
        np.full(spline_order, t_max)  
    ))
    
    return knots


if __name__ == "__main__":
    
    grado_p = 1       
    orden_k = grado_p + 1 

    K_num_funciones_base = 4 

    t_inicio = 0.0
    t_fin = 3.0 

    nodos = generate_simple_knots(K_num_funciones_base, grado_p, t_inicio, t_fin)
    
    print(f"Grado p = {grado_p}, Orden k = {orden_k}")
    print(f"Número de funciones base K = {K_num_funciones_base}")
    print(f"Vector de Nodos (longitud {len(nodos)}): {np.round(nodos, 2)}")

    
    t_puntos_evaluacion = np.linspace(t_inicio, t_fin, 200)

    plt.figure(figsize=(10, 6))
    plt.title(f'Funciones Base B-spline (Grado {grado_p}, K={K_num_funciones_base}) - Implementación KISS')

    for i_indice_base in range(K_num_funciones_base): 
        valores_base_actual = []
        for t_val in t_puntos_evaluacion:
            cache_memoizacion = {} 
                                   
                                   
            valor = cox_de_boor_recursive(t_val, i_indice_base, orden_k, nodos, cache_memoizacion)
            valores_base_actual.append(valor)
        
        plt.plot(t_puntos_evaluacion, valores_base_actual, label=f'$B_{{{i_indice_base},{orden_k}}}(t)$')

    
    unique_knots_plot = sorted(list(set(np.round(nodos,3))))
    for knot_val_plot in unique_knots_plot:
        if t_inicio <= knot_val_plot <= t_fin:
            plt.axvline(knot_val_plot, color='gray', linestyle=':', linewidth=0.7, alpha=0.8)
            
    plt.xlabel('Parámetro t')
    plt.ylabel('Valor de la función base')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.ylim(-0.1, 1.1) 
    plt.show()

    
    suma_bases = np.zeros_like(t_puntos_evaluacion)
    for i_indice_base in range(K_num_funciones_base):
        for idx_t, t_val in enumerate(t_puntos_evaluacion):
            cache_memoizacion = {}
            suma_bases[idx_t] += cox_de_boor_recursive(t_val, i_indice_base, orden_k, nodos, cache_memoizacion)
            
    
    all_bases_values_for_sum = np.zeros((len(t_puntos_evaluacion), K_num_funciones_base))
    for i_idx_base in range(K_num_funciones_base):
        for t_idx, t_v in enumerate(t_puntos_evaluacion):
            memo = {}
            all_bases_values_for_sum[t_idx, i_idx_base] = cox_de_boor_recursive(t_v, i_idx_base, orden_k, nodos, memo)
    
    sum_of_bases_plot = np.sum(all_bases_values_for_sum, axis=1)

    plt.figure(figsize=(10, 5))
    plt.plot(t_puntos_evaluacion, sum_of_bases_plot, label='$\\sum B_{i,k}(t)$')
    plt.title('Verificación de la Partición de la Unidad (KISS)')
    plt.xlabel('t')
    plt.ylabel('Suma de las funciones base')
    plt.ylim(-0.1, 1.5)
    plt.axhline(1.0, color='red', linestyle=':', label='Valor esperado = 1.0')
    for knot_val_plot in unique_knots_plot:
        if t_inicio <= knot_val_plot <= t_fin:
            plt.axvline(knot_val_plot, color='gray', linestyle=':', linewidth=0.7, alpha=0.8)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()