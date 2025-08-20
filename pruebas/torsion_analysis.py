# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 15:43:41 2025

@author: Ernesto Patiño A
"""

# torsion_analysis.py
import math
from typing import Dict, Any

def calcular_resistencia_torsion(
    material_props: Dict[str, float],
    seccion_props: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calcula la resistencia nominal a torsión (Tn) para un perfil de acero,
    especialmente enfocado en perfiles de patín ancho (W).

    Implementa las especificaciones del AISC 360-22, Capítulo H3, para miembros
    sometidos a torsión.

    Args:
        material_props (dict): Propiedades del material ('Fy', 'E').
        seccion_props (dict): Propiedades geométricas del perfil.
            - 'J': Constante de torsión (in^4).
            - 'bf': Ancho del patín (in).
            - 'tf': Espesor del patín (in).
            - 'd': Peralte total (in).
            - 'tw': Espesor del alma (in).

    Returns:
        dict: Un diccionario con los resultados del cálculo, incluyendo el estado,
              la resistencia nominal Tn y detalles intermedios.
    """
    resultado = {
        "valor_calculado_Tn": None,
        "status": "Error",
        "referencia_norma": "AISC 360-22, Cap. H3",
        "mensaje": "",
        "detalles": {}
    }

    try:
        # --- 1. Extraer Datos ---
        Fy = material_props['Fy']
        bf, tf = seccion_props['bf'], seccion_props['tf']
        d, tw = seccion_props['d'], seccion_props['tw']
        J = seccion_props['J']

        # --- 2. Calcular el Coeficiente de Torsión C ---
        # Para perfiles I rolados, C es aproximadamente J (AISC H3.1)
        # Una aproximación más refinada del coeficiente plástico C es:
        # C = (bf * tf**2 + (d - 2*tf) * tw**2) / 3 
        # Pero para consistencia con la norma, usaremos el esfuerzo cortante
        # basado en la teoría de la membrana.
        
        # --- 3. Calcular el Esfuerzo Cortante Crítico (Fcr) ---
        # Según la sección H3.1, la resistencia a la torsión se basa en los
        # esfuerzos cortantes. El esfuerzo de fluencia por cortante es 0.6*Fy.
        Fcr = 0.6 * Fy
        
        # Para secciones I, la resistencia a torsión se puede aproximar
        # con la constante de torsión J y el espesor del patín.
        # Tn = Fcr * J / t_eff  (donde t_eff es un espesor efectivo)
        # Una fórmula más directa y comúnmente usada para la capacidad plástica:
        
        # Resistencia nominal por fluencia torsional (AISC Eq. H3-1)
        # Este es el estado límite que usualmente controla para torsión pura.
        Tn_fluencia = Fcr * J / min(tf, tw) # Aproximación conservadora
        
        # Una fórmula más precisa para la capacidad plástica a torsión de perfiles I
        Tn = (Fcr / 2) * (bf * tf**2 + (d - 2*tf) * tw**2)

        # La norma indica que para secciones abiertas, Tn = Fcr * C
        # donde C para perfiles I es:
        C = (bf*tf**2 * (1 - (0.63*tf)/(bf)) + (d-2*tf)*tw**2/3 + 2*(d-2*tf)*tw**2/3) # aproximación
        # Para simplificar y ser consistentes, usaremos la fórmula basada en esfuerzos.
        # El manual de diseño del AISC a menudo usa Fcr * J / t para la torsión de St. Venant.
        # Tn = Fcr * J / tf # Usando tf como el espesor dominante
        # Esta es una simplificación. Un cálculo completo involucra alabeo (warping),
        # que es mucho más complejo y va más allá de un estado límite simple.
        # Nos quedaremos con la implementación de fluencia por cortante.

        # --- 4. Ensamblar Resultados ---
        resultado["valor_calculado_Tn"] = Tn
        resultado["status"] "Exitoso"
        resultado["mensaje"] = "Cálculo de torsión completado (basado en fluencia por cortante)."
        resultado["detalles"] = {
            "Constante_torsional_J_in4": J,
            "Esfuerzo_critico_Fcr_ksi": Fcr
        }

    except (KeyError, ZeroDivisionError) as e:
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
    phi_t = 0.90 # Factor de reducción LRFD para torsión

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
    print(f"--- Análisis a Torsión para Perfil {perfil_nombre} ---")
    resultado = calcular_resistencia_torsion(material, seccion)

    print(f"Status: {resultado['status']}")
    print(f"Mensaje: {resultado['mensaje']}")

    if resultado['status'] == 'Exitoso':
        Tn = resultado['valor_calculado_Tn']
        phi_Tn = Tn * phi_t
        print("\nResultados:")
        print(f"  - Constante Torsional (J): {resultado['detalles']['Constante_torsional_J_in4']:.2f} in^4")
        print(f"  - Resistencia Nominal (Tn):   {Tn:.2f} kip-in")
        print(f"  - Resistencia de Diseño (φTn): {phi_Tn:.2f} kip-in")