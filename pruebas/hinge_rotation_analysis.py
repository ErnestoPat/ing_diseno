# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 12:50:41 2025

@author: Ernesto Patiño A
"""

# hinge_rotation_analysis.py
from typing import Dict, Any

def calcular_momento_rotacion(
    seccion_props: Dict[str, float],
    material_props: Dict[str, float],
    beam_params: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calcula los puntos clave de la curva Momento-Rotación para un segmento de
    viga (rótula plástica), basado en fórmulas empíricas para perfiles tipo W.

    Args:
        seccion_props (dict): Propiedades geométricas del perfil.
            - 'd', 'bf', 'tf', 'tw': Dimensiones de la sección (in).
            - 'Ix', 'Zx', 'Sx': Propiedades de la sección (in^4, in^3, in^3).

        material_props (dict): Propiedades del material.
            - 'E': Módulo de elasticidad (ksi).
            - 'Fy': Esfuerzo de fluencia (ksi).

        beam_params (dict): Parámetros del segmento de viga.
            - 'L': Longitud del segmento o viga (in).

    Returns:
        dict: Un diccionario con los resultados, incluyendo los puntos
              característicos de la curva Momento vs. Rotación.
    """
    resultado = {
        "status": "Error",
        "mensaje": "",
        "puntos_curva": None
    }
    try:
        # --- 1. Extraer datos de entrada ---
        d, bf, tf, tw = seccion_props['d'], seccion_props['bf'], seccion_props['tf'], seccion_props['tw']
        Ix, Zx, Sx = seccion_props['Ix'], seccion_props['Zx'], seccion_props['Sx']
        E, Fy = material_props['E'], material_props['Fy']
        L = beam_params['L']
        
        # --- 2. Calcular Momentos Característicos ---
        My = Fy * Sx
        Mp = Fy * Zx
        
        # --- 3. Calcular Rotaciones Caracterísitcas (basado en fórmulas empíricas) ---
        h = d - 2 * tf
        
        # Parámetros adimensionales
        h_tw = h / tw if tw > 0 else 0
        bf_2tf = bf / (2 * tf) if tf > 0 else 0
        L_d = L / d if d > 0 else 0
        
        # Conversiones para fórmulas empíricas (pueden requerir ajuste)
        d_533 = (d * 25.4) / 533
        Fy_355 = (Fy * 6.895) / 355
        
        # Rotación en la fluencia
        theta_y = (My * L) / (6 * E * Ix) if E * Ix > 0 else 0

        # Rotación plástica y de plastificación completa (capping)
        # Estas fórmulas son altamente empíricas y específicas del paper/código de origen
        if d <= 21: # Condición del script original
            theta_p = (0.0865 * (h_tw)**-0.365) * ((bf_2tf)**-0.14) * \
                      ((d_533)**-0.721) * ((Fy_355)**-0.23) * ((L_d)**0.34)
            
            theta_pc = (5.63 * (h_tw)**-0.565) * ((bf_2tf)**-0.781) * \
                       ((d_533)**-0.583) * ((Fy_355)**-0.652) * ((L_d)**1.49)
        else: # d > 21
            theta_p = (0.0544 * (h_tw)**-0.456) * ((bf_2tf)**-0.09) * \
                      ((d_533)**-0.892) * ((Fy_355)**-0.384) * ((L_d)**0.641)

            theta_pc = (2.26 * (h_tw)**-0.53) * ((bf_2tf)**-0.613) * \
                       ((d_533)**-0.12) * ((Fy_355)**-0.511) * ((L_d)**1.14)
        
        # --- 4. Ensamblar los puntos de la curva ---
        # (Momento, Rotación)
        puntos = {
            "punto_origen": (0, 0),
            "punto_fluencia": (My, theta_y),
            "punto_plastico": (Mp, theta_p),
            "punto_capping": (Mp, theta_pc) # Asumiendo que el capping ocurre a Mp
        }
        
        resultado["status"] = "Exitoso"
        resultado["mensaje"] = "Cálculo de Momento-Rotación completado."
        resultado["puntos_curva"] = puntos
        
    except KeyError as e:
        resultado["mensaje"] = f"Error: Falta la propiedad requerida: {e}."
    except Exception as e:
        resultado["mensaje"] = f"Error inesperado en el análisis: {e}."

    return resultado