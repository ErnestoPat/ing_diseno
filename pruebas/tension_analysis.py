# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 12:43:31 2025

@author: Ernesto Patiño A
"""

# tension_analysis.py
from typing import Dict, Any
# ¡Importamos nuestra nueva función independiente!
from shear_lag_analysis import calcular_factor_u

def calcular_resistencia_tension(
    material_props: Dict[str, float],
    seccion_props: Dict[str, float],
    connection_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calcula la resistencia nominal a tensión (Pn) considerando fluencia y fractura.
    (AISC 360-22, Capítulo D).
    
    Esta función ahora llama a 'calcular_factor_u' para el análisis de cortante
    diferido, haciéndola modular e independiente de esa lógica específica.
    """
    resultado = {
        "valor_calculado_Pn": None, "status": "Error", "referencia_norma": "AISC 360-22, Cap. D",
        "mensaje": "", "detalles": {}, "datos_entrada": {
            "material": material_props, "seccion": seccion_props, "conexion": connection_details
        }
    }

    try:
        # --- 1. Extraer Datos de Entrada ---
        Fy = material_props['Fy']
        Fu = material_props['Fu']
        Ag = seccion_props['Ag']
        An = connection_details.get('An', Ag)

        # --- 2. Estado Límite de Fluencia (AISC D2-1) ---
        Pn_fluencia = Fy * Ag

        # --- 3. Estado Límite de Fractura (AISC D2-2) ---
        
        # 3.1. OBTENER FACTOR U LLAMANDO A LA FUNCIÓN INDEPENDIENTE
        resultado_u = calcular_factor_u(seccion_props, connection_details)
        
        if resultado_u["status"] == "Error":
            # Si el cálculo de U falla, no podemos continuar.
            raise ValueError(f"No se pudo calcular el factor U: {resultado_u['mensaje']}")
        
        U = resultado_u["valor_calculado_U"]
        
        # 3.2. Calcular Área Neta Efectiva (Ae) y Resistencia a Fractura
        Ae = An * U
        Pn_fractura = Fu * Ae

        # --- 4. Determinar Resistencia Nominal (Pn) ---
        Pn = min(Pn_fluencia, Pn_fractura)
        estado_limite_controla = "Fluencia" if Pn == Pn_fluencia else "Fractura"

        # --- 5. Llenar el Diccionario de Resultados ---
        resultado["valor_calculado_Pn"] = Pn
        resultado["status"] = "Exitoso"
        resultado["mensaje"] = f"Cálculo completado. Controla: {estado_limite_controla}."
        resultado["detalles"] = {
            "Pn_fluencia_kips": Pn_fluencia, "Pn_fractura_kips": Pn_fractura,
            "Area_bruta_Ag_in2": Ag, "Area_neta_An_in2": An,
            "Factor_cortante_diferido_U": U, "Area_neta_efectiva_Ae_in2": Ae,
            "info_calculo_U": resultado_u['mensaje'] # Incluimos el mensaje de la función U
        }

    except (KeyError, ValueError) as e:
        resultado["mensaje"] = f"Error en los datos de entrada: {e}."
    except Exception as e:
        resultado["mensaje"] = f"Error inesperado: {e}."

    return resultado