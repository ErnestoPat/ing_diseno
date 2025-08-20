# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 15:42:07 2025

@author: Ernesto Patiño A
"""

# shear_analysis.py
import math
from typing import Dict, Any

def calcular_resistencia_cortante(
    material_props: Dict[str, float],
    seccion_props: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calcula la resistencia nominal a cortante (Vn) de un perfil de acero,
    principalmente para el alma de perfiles tipo I, W y C.

    Implementa las especificaciones del AISC 360-22, Capítulo G. El cálculo
    incluye la determinación del coeficiente de cortante Cv (Cv1 o Cv2)
    basado en la esbeltez del alma.

    Args:
        material_props (dict): Propiedades del material ('Fy', 'E').
        seccion_props (dict): Propiedades geométricas del perfil.
            - 'd': Peralte total (in).
            - 'tf': Espesor del patín (in).
            - 'tw': Espesor del alma (in).
            - 'kdes': Distancia de diseño k (in).

    Returns:
        dict: Un diccionario con los resultados del cálculo, incluyendo el estado,
              la resistencia nominal Vn y detalles intermedios.
    """
    resultado = {
        "valor_calculado_Vn": None,
        "status": "Error",
        "referencia_norma": "AISC 360-22, Cap. G",
        "mensaje": "",
        "detalles": {}
    }

    try:
        # --- 1. Extraer Datos ---
        Fy, E = material_props['Fy'], material_props['E']
        d, tf = seccion_props['d'], seccion_props['tf']
        tw, kdes = seccion_props['tw'], seccion_props.get('kdes', tf) # Usar tf si kdes no está

        # --- 2. Calcular Propiedades del Alma ---
        # Aw: Área del alma
        Aw = d * tw
        # h: Altura libre del alma
        h = d - 2 * kdes
        # h/tw: Razón de esbeltez del alma
        h_tw = h / tw if tw > 0 else 0

        # --- 3. Calcular Coeficiente de Cortante (Cv) ---
        # Límite para almas no rigidizadas
        limite_esbeltez = 2.24 * math.sqrt(E / Fy)
        kv = 5.34 # Para almas no rigidizadas con h/tw < 260
        
        Cv1 = 1.0
        Cv2 = 0.0
        
        if h_tw <= limite_esbeltez:
            # Caso (G2-3): El alma no pandea
            Cv1 = 1.0
            caso_cv = "G2-3 (No pandea)"
        else:
            # Caso (G2-4 y G2-5): Pandeo inelástico o elástico
            limite_inelastico = 1.10 * math.sqrt(kv * E / Fy)
            limite_elastico = 1.37 * math.sqrt(kv * E / Fy)
            
            if h_tw <= limite_inelastico:
                # Pandeo inelástico (G2-4)
                Cv1 = limite_inelastico / h_tw
                caso_cv = "G2-4 (Pandeo inelástico)"
            elif h_tw <= limite_elastico:
                # Pandeo elástico (G2-5)
                Cv2 = (1.51 * kv * E) / (h_tw**2 * Fy)
                caso_cv = "G2-5 (Pandeo elástico)"
            else:
                 raise ValueError("La esbeltez del alma h/tw excede los límites de esta sección.")
        
        # El coeficiente final es Cv1 o Cv2, dependiendo del caso
        Cv = Cv1 if Cv1 != 1.0 else Cv2 if Cv2 != 0 else 1.0

        # --- 4. Calcular Resistencia Nominal a Cortante (Vn) ---
        # Ecuación G2-1
        Vn = 0.6 * Fy * Aw * Cv

        # --- 5. Ensamblar Resultados ---
        resultado["valor_calculado_Vn"] = Vn
        resultado["status"] = "Exitoso"
        resultado["mensaje"] = f"Cálculo de cortante completado. {caso_cv} aplica."
        resultado["detalles"] = {
            "Area_alma_Aw_in2": Aw,
            "Esbeltez_alma_h_tw": h_tw,
            "Limite_esbeltez": limite_esbeltez,
            "Coeficiente_Cv": Cv
        }

    except (KeyError, ValueError, ZeroDivisionError) as e:
        resultado["mensaje"] = f"Error en los datos de entrada o cálculo: {e}."
    except Exception as e:
        resultado["mensaje"] = f"Error inesperado: {e}."

    return resultado

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    from aisc_database import DatabaseAISC

    # --- 1. Configuración ---
    perfil_nombre = "W18X50"
    material = {'Fy': 50, 'E': 29000}
    phi_v = 0.90 # Factor de reducción LRFD para cortante

    # --- 2. Obtener Datos del Perfil ---
    try:
        db = DatabaseAISC()
        respuesta_db = db.obtener_propiedades_perfil(perfil_nombre)
        if respuesta_db['status'] == 'Error':
            print(respuesta_db['mensaje'])
            exit()
        seccion = respuesta_db['propiedades']
    except FileNotFoundError:
        print("Asegúrate de que 'aisc-shapes-database-v15.0.xlsx' esté en la carpeta.")
        exit()

    # --- 3. Realizar el Análisis ---
    print(f"--- Análisis a Cortante para Perfil {perfil_nombre} ---")
    resultado = calcular_resistencia_cortante(material, seccion)

    print(f"Status: {resultado['status']}")
    print(f"Mensaje: {resultado['mensaje']}")

    if resultado['status'] == 'Exitoso':
        Vn = resultado['valor_calculado_Vn']
        phi_Vn = Vn * phi_v
        print("\nResultados:")
        print(f"  - Esbeltez del alma (h/tw): {resultado['detalles']['Esbeltez_alma_h_tw']:.2f}")
        print(f"  - Coeficiente de Cortante (Cv): {resultado['detalles']['Coeficiente_Cv']:.3f}")
        print(f"  - Resistencia Nominal (Vn):   {Vn:.2f} kips")
        print(f"  - Resistencia de Diseño (φVn): {phi_Vn:.2f} kips")