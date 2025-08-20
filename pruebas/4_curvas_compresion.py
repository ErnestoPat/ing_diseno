# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 12:33:28 2025

@author: Ernesto Patiño A
"""

# generar_curvas_compresion.py
import numpy as np
import matplotlib.pyplot as plt

# Importamos nuestras herramientas desde los otros archivos del paquete
from aisc_database import DatabaseAISC
from compression_analysis import calcular_resistencia_compresion

def main():
    """
    Función principal que define los parámetros, calcula las resistencias y
    genera la gráfica de las curvas de compresión.
    """
    # --- 1. Datos de Entrada (Configuración) ---
    perfiles_a_analizar = ['W12X58', 'W14X61', 'W16X67', 'W21X68']
    propiedades_material = {'Fy': 50, 'E': 29000}
    factores_k = {'Kx': 1.0, 'Ky': 1.0, 'Kz': 1.0}
    longitud_max_ft = 40

    # --- 2. Inicialización ---
    try:
        db = DatabaseAISC()
    except FileNotFoundError:
        print("\nError: Asegúrate de que 'aisc-shapes-database-v15.0.xlsx' esté en la carpeta.")
        return

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 8))

    # --- 3. Bucle de Cálculo y Gráfica ---
    print("\nIniciando cálculo de curvas de compresión...")
    longitudes_vector_ft = np.linspace(1, longitud_max_ft, num=100)
    longitudes_vector_in = longitudes_vector_ft * 12

    for perfil_nombre in perfiles_a_analizar:
        print(f"  - Procesando perfil: {perfil_nombre}")
        
        respuesta_db = db.obtener_propiedades_perfil(perfil_nombre)
        if respuesta_db['status'] == 'Error':
            print(f"    Advertencia: {respuesta_db['mensaje']}.")
            continue
        
        props_seccion = respuesta_db['propiedades']
        Pn_vector_kips = []

        for L_in in longitudes_vector_in:
            longitudes_efectivas = {'Lx': L_in, 'Ly': L_in, 'Lz': L_in, **factores_k}
            
            # ¡Aquí usamos la función importada!
            resultado_pn = calcular_resistencia_compresion(
                propiedades_material, props_seccion, longitudes_efectivas
            )
            
            Pn_vector_kips.append(resultado_pn['valor_calculado_Pn'] if resultado_pn['status'] == 'Exitoso' else 0)

        ax.plot(longitudes_vector_ft, Pn_vector_kips, label=perfil_nombre, linewidth=2.5)

    # --- 4. Formato y Visualización ---
    ax.set_title('Curvas de Resistencia a Compresión (Pn vs. L)', fontsize=18)
    ax.set_xlabel('Longitud Efectiva no Arriostrada (pies)', fontsize=14)
    ax.set_ylabel('Resistencia Nominal a Compresión, Pn (kips)', fontsize=14)
    ax.legend(title='Perfil')
    ax.set_xlim(left=0); ax.set_ylim(bottom=0)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
Resumen de las Ventajas
Organización: Cada archivo tiene una única responsabilidad. aisc_database.py maneja datos, compression_analysis.py realiza cálculos de compresión.

Reutilización: Si mañana necesitamos escribir otro script que calcule la resistencia a compresión de un solo perfil, simplemente importaremos calcular_resistencia_compresion sin tener que copiar el código.

Mantenimiento: Si encontramos un error o queremos mejorar la función de cálculo de compresión, solo tenemos que editar compression_analysis.py. Todos los scripts que la usen se beneficiarán automáticamente del cambio.

Escalabilidad: A medida que traduzcamos más funciones (flexión, cortante, etc.), simplemente crearemos más archivos (flexure_analysis.py, shear_analysis.py) y los importaremos cuando los necesitemos.