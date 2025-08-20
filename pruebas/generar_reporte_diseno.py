# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 15:33:10 2025

@author: Ernesto Patiño A
"""

"""
Script principal de aplicación para el diseño de múltiples miembros de acero.

Este programa utiliza el paquete 'acero_analysis' para:
1. Leer una lista de miembros estructurales y sus cargas.
2. Calcular la capacidad de cada miembro (compresión, flexión).
3. Realizar la verificación por efectos combinados (interacción).
4. Generar un reporte de diseño detallado en un archivo Excel.

Este script reemplaza la funcionalidad de 'Estados límites.py' y otros
scripts monolíticos.
"""
import pandas as pd

# --- Importaciones de Nuestro Paquete de Análisis ---
from aisc_database import DatabaseAISC
from compression_analysis import calcular_resistencia_compresion
from flexure_analysis import calcular_resistencia_flexion
from combined_effects_analysis import verificar_interaccion_flexo_compresion

def main():
    # ==========================================================================
    # --- 1. DATOS DE ENTRADA (Simula la salida de un análisis estructural) ---
    # ==========================================================================
    miembros_a_revisar = [
        {
            "id": "Columna-01", "perfil": "W14X90", "longitud_ft": 15,
            "cargas": {'Pr': 400, 'Mrx': 250*12, 'Mry': 0}
        },
        {
            "id": "Viga-01", "perfil": "W18X50", "longitud_ft": 30,
            "cargas": {'Pr': 0, 'Mrx': 280*12, 'Mry': 0}
        },
        {
            "id": "VigaCol-02", "perfil": "W12X58", "longitud_ft": 20,
            "cargas": {'Pr': 250, 'Mrx': 150*12, 'Mry': 20*12}
        },
        {
            "id": "Columna-Inv", "perfil": "W1X1", "longitud_ft": 10, # Perfil inválido para prueba
            "cargas": {'Pr': 100, 'Mrx': 50*12, 'Mry': 0}
        }
    ]
    
    material = {'Fy': 50, 'E': 29000, 'G': 11200} # ksi
    phi_c, phi_b = 0.90, 0.90 # Factores de reducción LRFD
    
    # ==========================================================================
    # --- 2. INICIALIZACIÓN ---
    # ==========================================================================
    try:
        db = DatabaseAISC()
    except FileNotFoundError:
        print("Error: No se encontró 'aisc-shapes-database-v15.0.xlsx'.")
        return

    resultados_diseno = []

    # ==========================================================================
    # --- 3. BUCLE DE ANÁLISIS POR LOTES ---
    # ==========================================================================
    for miembro in miembros_a_revisar:
        print(f"Procesando miembro: {miembro['id']} ({miembro['perfil']})...")
        
        # Obtener propiedades del perfil
        respuesta_db = db.obtener_propiedades_perfil(miembro['perfil'])
        if respuesta_db['status'] == 'Error':
            print(f"  -> ADVERTENCIA: {respuesta_db['mensaje']}")
            resultados_diseno.append({"ID": miembro['id'], "Perfil": miembro['perfil'], "Estado": "Error en Perfil"})
            continue
        
        seccion = respuesta_db['propiedades']
        
        # Preparar parámetros de análisis
        L_in = miembro['longitud_ft'] * 12
        params_columna = {'Lx': L_in, 'Ly': L_in, 'Lz': L_in, 'Kx': 1.0, 'Ky': 1.0, 'Kz': 1.0}
        params_viga = {'Lb': L_in, 'Cb': 1.0, 'eje': 'mayor'}
        
        # Calcular resistencias disponibles
        Pn = calcular_resistencia_compresion(material, seccion, params_columna)['valor_calculado_Pn']
        Mnx = calcular_resistencia_flexion(material, seccion, params_viga)['valor_calculado_Mn']
        Mny = material['Fy'] * seccion.get('Zy', 0)
        
        resistencias_disponibles = {'Pc': Pn * phi_c, 'Mcx': Mnx * phi_b, 'Mcy': Mny * phi_b}
        
        # Realizar verificación por interacción
        resultado_interaccion = verificar_interaccion_flexo_compresion(
            miembro['cargas'],
            resistencias_disponibles
        )
        
        # Almacenar resultados para el reporte
        resultados_diseno.append({
            "ID": miembro['id'],
            "Perfil": miembro['perfil'],
            "Estado": resultado_interaccion['status'],
            "Ratio D/C": f"{resultado_interaccion.get('ratio_demanda_capacidad', 0):.3f}",
            "φcPn (kips)": f"{resistencias_disponibles['Pc']:.2f}",
            "Pr (kips)": f"{miembro['cargas']['Pr']:.2f}",
            "φbMnx (kip-ft)": f"{resistencias_disponibles['Mcx']/12:.2f}",
            "Mrx (kip-ft)": f"{miembro['cargas']['Mrx']/12:.2f}",
        })
        
    # ==========================================================================
    # --- 4. GENERACIÓN DE REPORTE EN EXCEL ---
    # ==========================================================================
    if resultados_diseno:
        df_reporte = pd.DataFrame(resultados_diseno)
        nombre_reporte = "reporte_diseno_acero.xlsx"
        
        try:
            df_reporte.to_excel(nombre_reporte, index=False, sheet_name='Resumen de Diseño')
            print(f"\n¡Reporte de diseño generado exitosamente en '{nombre_reporte}'!")
        except Exception as e:
            print(f"\nError al escribir el archivo Excel: {e}")

if __name__ == "__main__":
    main()