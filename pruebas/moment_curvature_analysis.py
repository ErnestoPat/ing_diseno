# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 12:49:00 2025

@author: Ernesto Patiño A
"""

# moment_curvature_analysis.py
import numpy as np
from typing import Dict, Any

# ¡Importamos el modelo de material que creamos en el paso anterior!
from material_models import modelo_elasto_plastico

def calcular_momento_curvatura(
    seccion_props: Dict[str, float],
    material_props: Dict[str, float],
    analysis_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calcula la relación momento-curvatura para una sección transversal de acero
    mediante el método de integración de fibras.

    Args:
        seccion_props (dict): Propiedades geométricas del perfil.
            - 'd': Peralte total (in).
            - 'bf': Ancho del patín (in).
            - 'tf': Espesor del patín (in).
            - 'tw': Espesor del alma (in).

        material_props (dict): Propiedades del material.
            - 'E': Módulo de elasticidad (ksi).
            - 'Fy': Esfuerzo de fluencia (ksi).

        analysis_params (dict): Parámetros para el análisis numérico.
            - 'num_fibras': Número de fibras para discretizar la sección.
            - 'curvatura_max': Curvatura máxima a analizar (rad/in).

    Returns:
        dict: Un diccionario con los resultados, incluyendo los vectores de
              momento y curvatura para generar la gráfica.
    """
    resultado = {
        "status": "Error",
        "mensaje": "",
        "datos_curva": None
    }

    try:
        # --- 1. Extraer propiedades y parámetros ---
        d, bf, tf, tw = seccion_props['d'], seccion_props['bf'], seccion_props['tf'], seccion_props['tw']
        num_fibras = analysis_params['num_fibras']
        curvatura_max = analysis_params['curvatura_max']
        
        # --- 2. Discretizar la sección en fibras ---
        # Se discretiza solo la mitad de la sección y luego se duplica por simetría
        h_alma = d - 2 * tf
        
        # Coordenadas 'y' y áreas 'A' de las fibras desde el Eje Neutro hacia arriba
        y_patin, A_patin = np.linspace(h_alma/2, d/2, int(num_fibras/2 * (tf*bf) / (d*bf)), retstep=True)
        A_patin *= bf # El área es el ancho por el diferencial de altura
        
        y_alma, A_alma = np.linspace(0, h_alma/2, int(num_fibras/2 * (h_alma*tw) / (d*bf)), retstep=True)
        A_alma *= tw

        # Combinar fibras de media sección
        y_coords = np.concatenate([y_alma, y_patin])
        A_fibras = np.concatenate([np.full_like(y_alma, A_alma), np.full_like(y_patin, A_patin)])

        # --- 3. Bucle de Análisis: Incrementar la curvatura (phi) ---
        curvaturas = np.linspace(0, curvatura_max, 100)
        momentos = []

        for phi in curvaturas:
            momento_total = 0
            
            # Calcular el strain en cada fibra: strain = y * phi
            strains = y_coords * phi
            
            # Calcular el stress en cada fibra usando nuestro modelo de material
            stresses = np.array([
                modelo_elasto_plastico(s, material_props)["valor_calculado_stress"]
                for s in strains
            ])
            
            # Calcular la fuerza en cada fibra: F = stress * Area
            fuerzas = stresses * A_fibras
            
            # Calcular el momento de cada fibra: M = F * y
            momentos_fibras = fuerzas * y_coords
            
            # Sumar el momento de todas las fibras y duplicar por simetría
            momento_total = np.sum(momentos_fibras) * 2
            momentos.append(momento_total)

        resultado["status"] = "Exitoso"
        resultado["mensaje"] = "Análisis de Momento-Curvatura completado."
        resultado["datos_curva"] = {
            "curvaturas": curvaturas.tolist(),
            "momentos": momentos
        }

    except KeyError as e:
        resultado["mensaje"] = f"Error: Falta la propiedad requerida: {e}."
    except Exception as e:
        resultado["mensaje"] = f"Error inesperado en el análisis: {e}."

    return resultado