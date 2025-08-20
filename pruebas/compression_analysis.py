# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 12:23:50 2025

@author: Ernesto Patiño A
"""

import math
from typing import Dict, Any

def calcular_resistencia_compresion(
    material_props: Dict[str, float],
    seccion_props: Dict[str, float],
    longitudes_efectivas: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calcula la resistencia nominal a compresión (Pn) de un perfil de acero,
    considerando pandeo por flexión y pandeo por torsión/flexo-torsión.

    Esta función implementa las especificaciones del AISC 360-22, Capítulo E.

    Args:
        material_props (dict): Diccionario con las propiedades del material.
            - 'Fy': Esfuerzo de fluencia (ej. 50 ksi).
            - 'E': Módulo de elasticidad (ej. 29000 ksi).
            - 'G': Módulo de corte (ej. 11200 ksi).

        seccion_props (dict): Diccionario con las propiedades geométricas de la sección.
            - 'tipo': Tipo de perfil ("W", "C", "WT", etc.).
            - 'Ag': Área bruta (in^2).
            - 'rx', 'ry': Radios de giro (in).
            - 'r0': Radio de giro polar (in).
            - 'J': Constante de torsión (in^4).
            - 'Cw': Constante de alabeo (in^6).
            - 'Ix', 'Iy': Momentos de inercia (in^4).
            - 'H': Coeficiente para secciones asimétricas (calculado).
            - 'x0', 'y0': Coordenadas del centro de corte (in).

        longitudes_efectivas (dict): Diccionario con las longitudes efectivas.
            - 'Lx', 'Ly', 'Lz': Longitudes no arriostradas para los ejes x, y, z (in).
            - 'Kx', 'Ky', 'Kz': Factores de longitud efectiva para los ejes.

    Returns:
        dict: Un diccionario con los resultados del cálculo, incluyendo el estado,
              la resistencia nominal Pn, el esfuerzo crítico Fcr y detalles intermedios.
    """
    # Inicializar el diccionario de respuesta
    resultado = {
        "valor_calculado_Pn": None,
        "status": "Error",
        "referencia_norma": "AISC 360-22, Cap. E",
        "mensaje": "",
        "detalles": {},
        "datos_entrada": {
            "material": material_props,
            "seccion": seccion_props,
            "longitudes": longitudes_efectivas
        }
    }

    try:
        # Extraer propiedades para facilitar la lectura
        Fy = material_props['Fy']
        E = material_props['E']
        G = material_props.get('G', E / (2 * (1 + 0.3))) # Calcular G si no se proporciona

        tipo = seccion_props['tipo']
        Ag = seccion_props['Ag']
        rx = seccion_props['rx']
        ry = seccion_props['ry']
        r0 = math.sqrt(seccion_props['r0_sq']) # r0_sq = x0^2 + y0^2 + (Ix+Iy)/Ag
        J = seccion_props['J']
        Cw = seccion_props['Cw']
        Ix = seccion_props['Ix']
        Iy = seccion_props['Iy']
        x0 = seccion_props.get('x0', 0) # Para secciones doblemente simétricas, x0 = 0
        H = 1 - (x0**2 / seccion_props['r0_sq']) # Eq. E4-10
        
        Kx, Ky, Kz = longitudes_efectivas['Kx'], longitudes_efectivas['Ky'], longitudes_efectivas['Kz']
        Lx, Ly, Lz = longitudes_efectivas['Lx'], longitudes_efectivas['Ly'], longitudes_efectivas['Lz']

        # --- 1. Pandeo por Flexión (Sección E3) ---
        # Eje X
        slenderness_x = (Kx * Lx) / rx if rx > 0 else 0
        Fe_x = (math.pi**2 * E) / slenderness_x**2 if slenderness_x > 0 else float('inf')
        
        # Eje Y
        slenderness_y = (Ky * Ly) / ry if ry > 0 else 0
        Fe_y = (math.pi**2 * E) / slenderness_y**2 if slenderness_y > 0 else float('inf')

        # --- 2. Pandeo Torsional y Flexo-Torsional (Sección E4) ---
        Lcz = Kz * Lz
        # Esfuerzo de pandeo elástico torsional
        Fe_z = (((math.pi**2 * E * Cw) / Lcz**2) + (G * J)) * (1 / (Ag * r0**2)) if Lcz > 0 else float('inf')
        
        # Determinar el esfuerzo de pandeo elástico Fe que controla
        # Para perfiles W (doblemente simétricos), se compara Fex, Fey y Fez
        if tipo in ["W", "M", "S", "HP"]:
            Fe = min(Fe_x, Fe_y, Fe_z)
        # Para perfiles C (simetría simple)
        elif tipo in ["C", "MC"]:
            # Ecuación de pandeo por flexo-torsión (AISC E4-4)
            Fe = ((Fe_y + Fe_z) / (2 * H)) * (1 - math.sqrt(1 - (4 * Fe_y * Fe_z * H) / (Fe_y + Fe_z)**2))
            Fe = min(Fe_x, Fe) # El pandeo en X sigue siendo un estado límite independiente
        # Para perfiles WT (simetría simple)
        elif tipo in ["WT", "MT", "ST"]:
            Fe = ((Fe_x + Fe_z) / (2 * H)) * (1 - math.sqrt(1 - (4 * Fe_x * Fe_z * H) / (Fe_x + Fe_z)**2))
            Fe = min(Fe_y, Fe)
        else:
            # Para otros perfiles, considerar solo pandeo por flexión como simplificación
            Fe = min(Fe_x, Fe_y)
            resultado["mensaje"] += f"Advertencia: El pandeo torsional para el tipo '{tipo}' no está implementado; se usó pandeo por flexión."

        # --- 3. Esfuerzo Crítico y Resistencia Nominal (Sección E3) ---
        if Fe <= 0: raise ValueError("El esfuerzo de pandeo elástico (Fe) debe ser positivo.")
        
        ratio_esbeltez = Fy / Fe
        
        if ratio_esbeltez <= 2.25:
            # Pandeo inelástico (AISC Eq. E3-2)
            Fcr = Fy * (0.658**ratio_esbeltez)
        else:
            # Pandeo elástico (AISC Eq. E3-3)
            Fcr = 0.877 * Fe
            
        Pn = Fcr * Ag

        # Llenar el diccionario de resultados
        resultado["valor_calculado_Pn"] = Pn
        resultado["status"] = "Exitoso"
        if not resultado["mensaje"]: resultado["mensaje"] = "Cálculo de resistencia a compresión completado."
        resultado["detalles"] = {
            "Esfuerzo_critico_Fcr_ksi": Fcr,
            "Esfuerzo_pandeo_elastico_Fe_ksi": Fe,
            "Pandeo_flexion_eje_x_Fe_x_ksi": Fe_x,
            "Pandeo_flexion_eje_y_Fe_y_ksi": Fe_y,
            "Pandeo_torsional_Fe_z_ksi": Fe_z
        }

    except KeyError as e:
        resultado["mensaje"] = f"Error: Falta la propiedad requerida en los datos de entrada: {e}."
    except Exception as e:
        resultado["mensaje"] = f"Error inesperado durante el cálculo: {e}."

    return resultado


# --- EJEMPLO DE USO ---
# Simula la forma en que llamarías a esta función después de obtener
# las propiedades con la clase DatabaseAISC.
if __name__ == "__main__":
    
    # Propiedades para un perfil W8X21 (obtenidas de la base de datos AISC)
    # Nota: r0^2 = x0^2 + y0^2 + (Ix+Iy)/Ag. Como x0=y0=0, r0^2 = (Ix+Iy)/Ag
    propiedades_w8x21 = {
        'tipo': "W", 'Ag': 6.16, 'rx': 3.42, 'ry': 1.25,
        'r0_sq': 12.80, # (75.3 + 9.77) / 6.16
        'J': 0.353, 'Cw': 102, 'Ix': 75.3, 'Iy': 9.77, 'x0': 0, 'y0': 0
    }
    
    propiedades_material = { 'Fy': 50, 'E': 29000, 'G': 11200 }
    
    # Longitudes efectivas para una columna de 10 ft (120 in)
    longitudes = { 'Lx': 120, 'Ly': 120, 'Lz': 120, 'Kx': 1.0, 'Ky': 1.0, 'Kz': 1.0 }
    
    print("--- Calculando resistencia para un perfil W8X21 ---")
    resultado_compresion = calcular_resistencia_compresion(
        propiedades_material,
        propiedades_w8x21,
        longitudes
    )

    # Imprimir un resumen de los resultados
    print(f"Status: {resultado_compresion['status']}")
    print(f"Mensaje: {resultado_compresion['mensaje']}")
    if resultado_compresion['status'] == 'Exitoso':
        print(f"Esfuerzo Crítico (Fcr): {resultado_compresion['detalles']['Esfuerzo_critico_Fcr_ksi']:.2f} ksi")
        print(f"Resistencia Nominal a Compresión (Pn): {resultado_compresion['valor_calculado_Pn']:.2f} kips")