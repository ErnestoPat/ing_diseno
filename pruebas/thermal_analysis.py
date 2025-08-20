# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 12:52:36 2025

@author: Ernesto Patiño A
"""

# thermal_analysis.py
import math
from typing import Dict, Any

def modelo_nist_temperatura(
    strain: float,
    fy_nominal: float,
    temperatura_c: float
) -> Dict[str, Any]:
    """
    Calcula el esfuerzo del acero para una deformación y temperatura dadas,
    utilizando el modelo del NIST.

    Este modelo describe la degradación de las propiedades mecánicas del acero
    a altas temperaturas.

    Args:
        strain (float): La deformación unitaria en un punto.
        fy_nominal (float): El esfuerzo de fluencia nominal del acero a
                             temperatura ambiente (ej. 50 ksi).
        temperatura_c (float): La temperatura del acero en grados Celsius.

    Returns:
        dict: Un diccionario con el resultado, incluyendo el esfuerzo calculado
              a la temperatura especificada.
    """
    resultado = {
        "valor_calculado_stress": None,
        "status": "Error",
        "mensaje": ""
    }
    try:
        # Fórmulas del modelo NIST para los parámetros K y n
        # Nota: Las constantes del script original (734, 575, etc.) parecen
        # estar calibradas para unidades específicas (posiblemente MPa y °C).
        # Se asume que Fy se introduce en ksi y se convierte si es necesario,
        # aunque el script original parece usarlo directamente.
        # Mantendremos la consistencia con el script original.
        
        T = temperatura_c
        Fy = fy_nominal

        # Coeficiente de resistencia K
        K = (734 + 0.315 * Fy) * math.exp(-(T / 575)**4.92)

        # Exponente de endurecimiento por deformación n
        n = (0.329 - 0.000423 * Fy) * math.exp(-(T / 637)**4.51)

        # Cálculo de un esfuerzo intermedio (similar a un esfuerzo verdadero)
        sigma = K * (strain**n) if strain > 0 else 0

        # Conversión a esfuerzo ingenieril (stress)
        stress = sigma / (1 + strain) if (1 + strain) != 0 else sigma
            
        resultado["valor_calculado_stress"] = stress
        resultado["status"] = "Exitoso"
        resultado["mensaje"] = f"Esfuerzo calculado para T={T}°C."

    except Exception as e:
        resultado["mensaje"] = f"Error inesperado en el modelo NIST: {e}."

    return resultado

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    fy_acero = 50 # ksi
    temperaturas_a_probar = [20, 300, 500, 700] # Grados Celsius
    strain_max = 0.02
    
    strains = np.linspace(0, strain_max, 100)
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 7))

    for temp in temperaturas_a_probar:
        stresses = [
            modelo_nist_temperatura(s, fy_acero, temp)["valor_calculado_stress"]
            for s in strains
        ]
        ax.plot(strains, stresses, label=f'{temp}°C', linewidth=2)

    ax.set_title(f'Modelo Esfuerzo-Deformación del Acero (Fy={fy_acero} ksi) vs. Temperatura', fontsize=16)
    ax.set_xlabel('Deformación Unitaria (strain)', fontsize=12)
    ax.set_ylabel('Esfuerzo (stress) (ksi)', fontsize=12)
    ax.legend(title='Temperatura')
    ax.grid(True)
    plt.tight_layout()
    plt.show()