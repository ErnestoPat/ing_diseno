# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 12:41:28 2025

@author: Ernesto Patiño A
"""

# shear_lag_analysis.py
from typing import Dict, Any

def calcular_factor_u(
    seccion_props: Dict[str, float],
    connection_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calcula el factor de reducción por cortante diferido (U) según los casos
    de la Tabla D3.1 del AISC 360-22.

    Esta función es una 'caja negra' que traduce la lógica detallada del
    script U.m.

    Args:
        seccion_props (dict): Propiedades geométricas del perfil.
            - 'tipo': "W", "L", "WT", etc.
            - 'd': Peralte (in).
            - 'bf': Ancho del patín (in).
            - 'x_bar': Ubicación del centroide (in).

        connection_details (dict): Detalles de la conexión.
            - 'elementos_conectados': Lista, ej. ['patin', 'alma'], ['solo_patin'].
            - 'L': Longitud de la conexión (in).
            - 'num_tornillos_linea': Número de tornillos en la línea de carga.

    Returns:
        dict: Un diccionario con el valor de U, el estado, el caso de la norma
              utilizado y un mensaje de diagnóstico.
    """
    resultado = {
        "valor_calculado_U": None,
        "status": "Error",
        "referencia_norma": "AISC 360-22, Tabla D3.1",
        "mensaje": "No se pudo determinar un caso aplicable."
    }

    try:
        elementos = connection_details.get('elementos_conectados', ['patin', 'alma'])
        L = connection_details.get('L', 0)
        x_bar = seccion_props.get('x_bar', 0)
        tipo = seccion_props.get('tipo', '')
        bf = seccion_props.get('bf', 0)
        d = seccion_props.get('d', 0)
        num_tornillos = connection_details.get('num_tornillos_linea', 0)
        
        U = 1.0
        caso_aplicado = "Caso 1: Todos los elementos conectados."

        if 'solo_patin' in elementos or 'solo_alma' in elementos:
            # Caso 2: Conexión longitudinal a través de elementos que no son la totalidad de la sección
            if L > 0 and x_bar > 0:
                U = 1 - (x_bar / L)
                caso_aplicado = f"Caso 2: U = 1 - (x_bar/L) = 1 - ({x_bar:.2f}/{L:.2f})"
            else:
                # Casos 7 y 8 (Alternativos para conexiones atornilladas)
                if tipo in ['W', 'M', 'S', 'HP'] and num_tornillos >= 3:
                    if 'solo_patin' in elementos:
                        caso_aplicado = "Caso 7 (Alternativo): Conexión al patín"
                        U = 0.90 if bf >= (2/3 * d) else 0.85
                    elif 'solo_alma' in elementos:
                        caso_aplicado = "Caso 7 (Alternativo): Conexión al alma"
                        U = 0.70
                elif tipo == 'L' and num_tornillos >= 4:
                     caso_aplicado = "Caso 8 (Alternativo): Ángulo simple"
                     U = 0.80
                elif tipo == 'L' and num_tornillos < 4:
                     caso_aplicado = "Caso 8 (Alternativo): Ángulo simple"
                     U = 0.60
                else: # Otros perfiles como WT, C
                    U = 0.85 # Un valor conservador si no se puede calcular
                    caso_aplicado = "Caso genérico/conservador"
        
        # El valor de U no puede ser mayor a 1.0
        U = min(U, 1.0)
        
        resultado["valor_calculado_U"] = U
        resultado["status"] = "Exitoso"
        resultado["mensaje"] = f"Cálculo de U completado. {caso_aplicado}"

    except Exception as e:
        resultado["mensaje"] = f"Error inesperado durante el cálculo de U: {e}"

    return resultado