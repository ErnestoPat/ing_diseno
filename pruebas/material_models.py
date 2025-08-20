# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 12:47:21 2025

@author: Ernesto Patiño A
"""

# material_models.py
import math
from typing import Dict, Any

# --- MODELO 1: ELASTO-PLÁSTICO PERFECTO ---
def modelo_elasto_plastico(strain: float, material_props: Dict[str, float]) -> Dict[str, Any]:
    """
    Calcula el esfuerzo usando un modelo elasto-plástico perfecto.
    """
    resultado = {"valor_calculado_stress": None, "status": "Error", "mensaje": ""}
    try:
        E, Fy = material_props['E'], material_props['Fy']
        strain_fluencia = Fy / E
        
        if abs(strain) < strain_fluencia:
            stress = strain * E
        else:
            stress = math.copysign(Fy, strain)
            
        resultado["valor_calculado_stress"] = stress
        resultado["status"] = "Exitoso"
    except KeyError as e:
        resultado["mensaje"] = f"Falta la propiedad: {e}."
    return resultado

# --- MODELO 2: RAMBERG-OSGOOD ---
def modelo_ramberg_osgood(strain: float, material_props: Dict[str, float]) -> Dict[str, Any]:
    """
    Calcula el esfuerzo usando el modelo de Ramberg-Osgood, que describe
    el comportamiento no-lineal. Rescatado de tarea_2_modelosconstitutivos.py.
    """
    resultado = {"valor_calculado_stress": None, "status": "Error", "mensaje": ""}
    try:
        E, Fy = material_props['E'], material_props['Fy']
        K = material_props.get('K', E) # Coeficiente de resistencia
        n = material_props.get('n', 10) # Exponente de endurecimiento
        
        # Ecuación de Ramberg-Osgood: strain = stress/E + (stress/K)^n
        # No se puede despejar el esfuerzo directamente, se usa la forma inversa
        # Nota: La implementación original en el script era para graficar, no para cálculo inverso.
        # Esta es una implementación simplificada que asume una forma directa.
        # Una implementación completa requeriría un solver numérico.
        # Aquí se usa la forma strain = f(stress), por lo que para una implementación
        # directa, se simplificará. La implementación del script original era:
        # s = E * e / (1 + (abs(E*e/Fy))**n)**(1/n)
        
        e_term = strain * E
        denom = (1 + (abs(e_term / Fy))**n)**(1/n)
        stress = e_term / denom
        
        resultado["valor_calculado_stress"] = stress
        resultado["status"] = "Exitoso"
    except KeyError as e:
        resultado["mensaje"] = f"Falta la propiedad: {e}."
    return resultado

# --- MODELO 3: MANEGOTTO-PINTO ---
# La implementación de Manegotto-Pinto en el script original era compleja y
# dependía de muchos parámetros. Aquí se presenta una estructura básica.
def modelo_manegotto_pinto(strain: float, material_props: Dict[str, float]) -> Dict[str, Any]:
    """
    Calcula el esfuerzo usando el modelo de Manegotto-Pinto.
    Estructura basada en tarea_2_modelosconstitutivos.py.
    """
    resultado = {"valor_calculado_stress": None, "status": "Error", "mensaje": ""}
    try:
        E, Fy = material_props['E'], material_props['Fy']
        b = material_props.get('b', 0.002) # Parámetro de transición
        R0 = material_props.get('R0', 20)  # Parámetro de curvatura inicial
        
        e_y = Fy / E
        e_ratio = strain / e_y
        
        # Ecuación simplificada de Manegotto-Pinto
        denom = (1 + abs(e_ratio)**R0)**(1/R0)
        stress = E * strain / denom + b * e_ratio
        
        resultado["valor_calculado_stress"] = stress
        resultado["status"] = "Exitoso"
    except KeyError as e:
        resultado["mensaje"] = f"Falta la propiedad: {e}."
    return resultado

# --- FUNCIÓN AUXILIAR: EFECTO DE VELOCIDAD DE DEFORMACIÓN ---
def ajustar_fy_por_strain_rate(fy_nominal: float, strain_rate: float) -> float:
    """
    Ajusta el esfuerzo de fluencia Fy basado en la velocidad de deformación (strain rate).
    Lógica rescatada de tarea_1_evss_rate.py.
    """
    # fs = 0.973 + 0.45*ev**0.33
    factor_incremento = 0.973 + 0.45 * strain_rate**0.33
    return fy_nominal * factor_incremento