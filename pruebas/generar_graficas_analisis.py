# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 15:36:57 2025

@author: Ernesto Patiño A
"""
"""
Script principal para la visualización del comportamiento y resistencia de
un perfil de acero.

Este programa funciona como un "dashboard" que utiliza el paquete 'acero_analysis'
para generar un panel con 5 gráficas clave:
1. Resistencia a Compresión vs. Longitud (Pn vs. L)
2. Resistencia a Flexión vs. Longitud no Arriostrada (Mn vs. Lb)
3. Diagrama de Interacción Plástico (P-M)
4. Curva Momento-Curvatura
5. Curva Momento-Rotación de Rótula Plástica
"""
import numpy as np
import matplotlib.pyplot as plt

# --- Importaciones de Nuestro Paquete de Análisis ---
from aisc_database import DatabaseAISC
from compression_analysis import calcular_resistencia_compresion
from flexure_analysis import calcular_resistencia_flexion
from combined_effects_analysis import generar_diagrama_interaccion_pm
from moment_curvature_analysis import calcular_momento_curvatura
from hinge_rotation_analysis import calcular_momento_rotacion

# ==============================================================================
# FUNCIONES DEDICADAS PARA CADA GRÁFICA
# ==============================================================================

def plot_compresion_vs_longitud(ax, seccion, material):
    """Genera la gráfica de Pn vs. Longitud."""
    longitudes_ft = np.linspace(1, 50, 100)
    Pn_vector = []
    for L_ft in longitudes_ft:
        L_in = L_ft * 12
        params = {'Lx': L_in, 'Ly': L_in, 'Lz': L_in, 'Kx': 1.0, 'Ky': 1.0, 'Kz': 1.0}
        res = calcular_resistencia_compresion(material, seccion, params)
        Pn_vector.append(res['valor_calculado_Pn'] if res['status'] == 'Exitoso' else 0)
    
    ax.plot(longitudes_ft, Pn_vector, color='red', linewidth=2)
    ax.set_title('Compresión vs. Longitud', fontsize=10)
    ax.set_xlabel('Longitud Efectiva (ft)', fontsize=8)
    ax.set_ylabel('Resistencia Nominal, Pn (kips)', fontsize=8)
    ax.grid(True)

def plot_flexion_vs_longitud(ax, seccion, material):
    """Genera la gráfica de Mn vs. Longitud no Arriostrada."""
    longitudes_ft = np.linspace(0.1, 50, 100)
    Mn_vector = []
    for Lb_ft in longitudes_ft:
        params = {'Lb': Lb_ft * 12, 'Cb': 1.0, 'eje': 'mayor'}
        res = calcular_resistencia_flexion(material, seccion, params)
        Mn_vector.append(res['valor_calculado_Mn'] / 12 if res['status'] == 'Exitoso' else 0)

    ax.plot(longitudes_ft, Mn_vector, color='blue', linewidth=2)
    ax.set_title('Flexión vs. Longitud no Arriostrada', fontsize=10)
    ax.set_xlabel('Longitud no Arriostrada, Lb (ft)', fontsize=8)
    ax.set_ylabel('Resistencia Nominal, Mn (kip-ft)', fontsize=8)
    ax.grid(True)

def plot_diagrama_interaccion(ax, seccion, material):
    """Genera la gráfica del Diagrama de Interacción P-M."""
    res = generar_diagrama_interaccion_pm(seccion, material)
    if res['status'] == 'Exitoso':
        P_vec = np.array(res['datos_diagrama']['cargas_axiales_P'])
        M_vec = np.array(res['datos_diagrama']['momentos_M']) / 12
        ax.plot(M_vec, P_vec, color='green', linewidth=2)
        ax.fill_between(M_vec, P_vec, color='green', alpha=0.1)
    
    ax.set_title('Diagrama de Interacción P-M', fontsize=10)
    ax.set_xlabel('Momento Nominal, Mn (kip-ft)', fontsize=8)
    ax.set_ylabel('Carga Axial Nominal, Pn (kips)', fontsize=8)
    ax.grid(True)

def plot_momento_curvatura(ax, seccion, material):
    """Genera la gráfica de Momento vs. Curvatura."""
    params = {'num_fibras': 200, 'curvatura_max': 0.005}
    res = calcular_momento_curvatura(seccion, material, params)
    if res['status'] == 'Exitoso':
        curvaturas = res['datos_curva']['curvaturas']
        momentos = np.array(res['datos_curva']['momentos']) / 12
        ax.plot(curvaturas, momentos, color='purple', linewidth=2)

    ax.set_title('Momento vs. Curvatura', fontsize=10)
    ax.set_xlabel('Curvatura (rad/in)', fontsize=8)
    ax.set_ylabel('Momento (kip-ft)', fontsize=8)
    ax.grid(True)

def plot_momento_rotacion(ax, seccion, material, L_ft=30):
    """Genera la gráfica de Momento vs. Rotación de Rótula Plástica."""
    params = {'L': L_ft * 12}
    res = calcular_momento_rotacion(seccion, material, params)
    if res['status'] == 'Exitoso':
        puntos = res['puntos_curva']
        rotaciones = [p[1] for p in puntos.values()]
        momentos = [p[0] / 12 for p in puntos.values()]
        ax.plot(rotaciones, momentos, 'o-', color='orange', linewidth=2)

    ax.set_title(f'Momento vs. Rotación (L={L_ft} ft)', fontsize=10)
    ax.set_xlabel('Rotación (rad)', fontsize=8)
    ax.set_ylabel('Momento (kip-ft)', fontsize=8)
    ax.grid(True)


# ==============================================================================
# FUNCIÓN PRINCIPAL
# ==============================================================================

def main():
    # --- 1. Configuración ---
    perfil_a_analizar = "W18X50"
    material = {'Fy': 50, 'E': 29000, 'G': 11200}

    # --- 2. Obtener Propiedades del Perfil ---
    try:
        db = DatabaseAISC()
        respuesta_db = db.obtener_propiedades_perfil(perfil_a_analizar)
        if respuesta_db['status'] == 'Error':
            print(respuesta_db['mensaje'])
            return
        seccion = respuesta_db['propiedades']
    except FileNotFoundError:
        print("Error: No se encontró 'aisc-shapes-database-v15.0.xlsx'.")
        return
    
    # --- 3. Crear el Panel de Gráficas ---
    fig, axs = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle(f'Panel de Análisis para Perfil: {perfil_a_analizar} (Fy = {material["Fy"]} ksi)', fontsize=16, fontweight='bold')
    
    # Llamar a cada función de graficación pasándole su 'ax' correspondiente
    plot_compresion_vs_longitud(axs[0, 0], seccion, material)
    plot_flexion_vs_longitud(axs[0, 1], seccion, material)
    plot_diagrama_interaccion(axs[0, 2], seccion, material)
    plot_momento_curvatura(axs[1, 0], seccion, material)
    plot_momento_rotacion(axs[1, 1], seccion, material)
    
    # Ocultar el último subplot vacío
    axs[1, 2].set_visible(False)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    main()