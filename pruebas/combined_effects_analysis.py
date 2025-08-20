# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 12:58:38 2025

@author: Ernesto Patiño A
"""

# combined_effects_analysis.py
import numpy as np
from typing import Dict, Any

def verificar_interaccion_flexo_compresion(
    required_strengths: Dict[str, float],
    available_strengths: Dict[str, float]
) -> Dict[str, Any]:
    """
    Verifica una sección sometida a flexo-compresión utilizando las
    ecuaciones de interacción del AISC 360-22, Capítulo H (H1-1).

    Esta es la versión consolidada que reemplaza a Flexocompresion.py y flexion_axial.m.
    """
    resultado = {
        "status": "Error", "referencia_norma": "AISC 360-22, Eq. H1-1",
        "mensaje": "", "ratio_demanda_capacidad": None
    }
    try:
        Pr, Mrx, Mry = required_strengths['Pr'], required_strengths.get('Mrx', 0), required_strengths.get('Mry', 0)
        Pc, Mcx, Mcy = available_strengths['Pc'], available_strengths.get('Mcx', 1e9), available_strengths.get('Mcy', 1e9)

        if Pc == 0: raise ValueError("La resistencia a compresión (Pc) no puede ser cero.")

        ratio_axial = Pr / Pc
        
        # Usar 1e9 como valor muy grande si Mc no se proporciona o es cero, para anular el término
        ratio_flex_x = (Mrx / Mcx) if Mcx != 0 else 0
        ratio_flex_y = (Mry / Mcy) if Mcy != 0 else 0
        
        if ratio_axial >= 0.2:
            # Ecuación H1-1a
            ratio_total = ratio_axial + (8/9) * (ratio_flex_x + ratio_flex_y)
            ecuacion_usada = "H1-1a"
        else:
            # Ecuación H1-1b
            ratio_total = (ratio_axial / 2) + (ratio_flex_x + ratio_flex_y)
            ecuacion_usada = "H1-1b"
        
        pasa = ratio_total <= 1.0
        
        resultado["status"] = "Pasa" if pasa else "No Pasa"
        resultado["mensaje"] = f"Verificación completa usando la ecuación {ecuacion_usada}."
        resultado["ratio_demanda_capacidad"] = ratio_total

    except (KeyError, ValueError) as e:
        resultado["mensaje"] = f"Error en los datos de entrada: {e}."
    return resultado


def generar_diagrama_interaccion_pm(
    seccion_props: Dict[str, float],
    material_props: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calcula la curva del diagrama de interacción Plástico P-M para el eje fuerte de un perfil W.
    Lógica mejorada y consolidada a partir de los scripts de diagrama_interaccion.m.
    """
    resultado = {"status": "Error", "mensaje": "", "datos_diagrama": None}
    try:
        Fy = material_props['Fy']
        d, bf, tf, tw = seccion_props['d'], seccion_props['bf'], seccion_props['tf'], seccion_props['tw']
        Ag, Zx = seccion_props['Ag'], seccion_props['Zx']
        
        h_alma = d - 2 * tf
        area_alma = h_alma * tw
        area_patin = bf * tf
        
        # Capacidades máximas
        Py = Ag * Fy
        Mp = Zx * Fy
        P_alma = area_alma * Fy # Carga axial que puede tomar el alma
        
        # Vector de cargas axiales para el cálculo
        cargas_p = np.linspace(0, Py, 100)
        momentos_m = []

        for P in cargas_p:
            if P <= P_alma:
                # Eje neutro plástico en el alma
                a = P / (2 * tw * Fy) # Distancia desde el centroide del alma
                Mn = Mp - (P**2) / (4 * tw * Fy)
            else:
                # Eje neutro plástico en los patines
                P_patines = P - P_alma
                a = P_patines / (2 * bf * Fy) # Distancia desde el borde interior del patín
                Mn = (Fy / 2) * (area_alma * (h_alma/2) + area_patin * (h_alma + tf - a)) * 2 - P * (h_alma/2 + a/2)
                # Esta es una aproximación, la fórmula exacta es más compleja.
                # Una simplificación común:
                Mn_reducido_patin = (bf * Fy) * (tf - a) * (d - tf - a)
                momentos_m.append(Mn_reducido_patin)
                continue # Saltar el append de abajo

            momentos_m.append(Mn)

        resultado["status"] = "Exitoso"
        resultado["mensaje"] = "Diagrama de interacción P-M calculado."
        resultado["datos_diagrama"] = {
            "cargas_axiales_P": cargas_p.tolist(), "momentos_M": momentos_m
        }
    except KeyError as e:
        resultado["mensaje"] = f"Error en propiedades de entrada: {e}."
    return resultado