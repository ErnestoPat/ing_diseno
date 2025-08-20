# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 13:01:13 2025

@author: Ernesto Patiño A
"""

# serviceability_analysis.py
import math
from typing import Dict, Any

def calcular_deflexion_angulos(
    seccion_props: Dict[str, float],
    material_props: Dict[str, float],
    beam_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calcula las deflexiones para una viga de perfil angular simplemente apoyada
    y sometida a una carga uniformemente distribuida.

    Verifica las deflexiones contra los límites comunes del AISC. El cálculo
    considera la flexión biaxial que ocurre debido a que los ejes principales
    no coinciden con los ejes geométricos.

    Args:
        seccion_props (dict): Propiedades geométricas del perfil angular.
            - 'Ix', 'Iy': Momentos de inercia sobre ejes geométricos (in^4).
            - 'Iz', 'Iw': Momentos de inercia sobre ejes principales (in^4).
            - 'tan_alpha': Tangente del ángulo de los ejes principales.

        material_props (dict): Propiedades del material ('E').

        beam_params (dict): Parámetros de la viga y cargas.
            - 'L': Longitud de la viga (in).
            - 'w_dead': Carga muerta uniformemente distribuida (kip/in).
            - 'w_live': Carga viva uniformemente distribuida (kip/in).
            - 'limite_viva': Límite para deflexión por carga viva (ej. 360 para L/360).
            - 'limite_total': Límite para deflexión por carga total (ej. 240 para L/240).

    Returns:
        dict: Un diccionario con los resultados de la verificación de deflexiones.
    """
    resultado = {
        "status": "Error", "mensaje": "", "verificaciones": {}
    }
    try:
        # --- 1. Extraer Datos ---
        Ix, Iy = seccion_props['Ix'], seccion_props['Iy']
        Iz, Iw = seccion_props['Iz'], seccion_props['Iw']
        tan_alpha = seccion_props.get('tan_alpha', 0) # tan(alpha)
        
        E = material_props['E']
        
        L = beam_params['L']
        w_d = beam_params['w_dead']
        w_l = beam_params['w_live']
        w_t = w_d + w_l
        
        lim_viva = L / beam_params['limite_viva']
        lim_total = L / beam_params['limite_total']
        
        alpha = math.atan(tan_alpha)

        # --- 2. Verificación Simple (Carga en Eje Geométrico Y) ---
        # Esta es una simplificación común, pero no es el cálculo completo.
        
        # Carga Viva
        delta_viva_y = (5 * w_l * L**4) / (384 * E * Ix)
        pasa_viva_simple = delta_viva_y <= lim_viva
        
        # Carga Total
        delta_total_y = (5 * w_t * L**4) / (384 * E * Ix)
        pasa_total_simple = delta_total_y <= lim_total
        
        # --- 3. Verificación Completa (Flexión Biaxial en Ejes Principales) ---
        # Descomponer la carga vertical en componentes a lo largo de los ejes principales w y z.
        w_d_w, w_d_z = w_d * math.sin(alpha), w_d * math.cos(alpha)
        w_l_w, w_l_z = w_l * math.sin(alpha), w_l * math.cos(alpha)
        
        # Calcular deflexiones a lo largo de los ejes principales
        delta_viva_w = (5 * w_l_w * L**4) / (384 * E * Iw)
        delta_viva_z = (5 * w_l_z * L**4) / (384 * E * Iz)
        
        # Componer vectorialmente para obtener la deflexión resultante
        delta_viva_resultante = math.sqrt(delta_viva_w**2 + delta_viva_z**2)
        pasa_viva_completo = delta_viva_resultante <= lim_viva

        # --- 4. Ensamblar Resultados ---
        resultado["status"] = "Exitoso"
        resultado["mensaje"] = "Verificación de deflexiones completada."
        resultado["verificaciones"] = {
            "deflexion_viva_simple": {
                "calculada": delta_viva_y, "limite": lim_viva,
                "status": "Pasa" if pasa_viva_simple else "No Pasa"
            },
            "deflexion_total_simple": {
                "calculada": delta_total_y, "limite": lim_total,
                "status": "Pasa" if pasa_total_simple else "No Pasa"
            },
            "deflexion_viva_resultante (biaxial)": {
                "calculada": delta_viva_resultante, "limite": lim_viva,
                "status": "Pasa" if pasa_viva_completo else "No Pasa"
            }
        }
        
    except (KeyError, ZeroDivisionError) as e:
        resultado["mensaje"] = f"Error en los datos de entrada o propiedades: {e}."
    except Exception as e:
        resultado["mensaje"] = f"Error inesperado: {e}."

    return resultado