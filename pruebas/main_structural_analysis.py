# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 13:03:22 2025

@author: Ernesto Patiño A
"""

# main_structural_analysis.py
"""
Script principal para el análisis y diseño de miembros de acero.
Este programa integra todos los módulos del paquete 'acero_analysis' para
realizar una verificación completa de un perfil estructural, similar al
script de MATLAB 'Programa_estructuaras_metalicas.m'.
"""
# --- Importaciones de Nuestro Paquete de Análisis ---
from aisc_database import DatabaseAISC
from compression_analysis import calcular_resistencia_compresion
from flexure_analysis import calcular_resistencia_flexion
from combined_effects_analysis import verificar_interaccion_flexo_compresion

def imprimir_resultados(titulo, resultados, factor_reduccion=0.9):
    """Función auxiliar para imprimir resultados de forma ordenada."""
    print("\n" + "="*50)
    print(f"RESULTADOS: {titulo}")
    print("="*50)
    print(f"  - Resistencia Nominal (Mn):   {resultados.get('valor_calculado_Mn', 0) / 12:.2f} kip-ft")
    print(f"  - Resistencia de Diseño (φMn): {resultados.get('valor_calculado_Mn', 0) * factor_reduccion / 12:.2f} kip-ft")
    print("\n  Detalles de Estados Límite (kip-ft):")
    detalles = resultados.get('detalles', {})
    print(f"    - Fluencia (Mp):                {detalles.get('Estado_limite_fluencia_Mp', 0) / 12:.2f}")
    print(f"    - Pandeo Lateral-Torsional (Mtb): {detalles.get('Estado_limite_LTB_Mtb', 0) / 12:.2f}")
    print(f"    - Pandeo Local (Ml):            {detalles.get('Estado_limite_pandeo_local_Ml', 0) / 12:.2f}")
    print("\n  Parámetros de Pandeo:")
    print(f"    - Lp: {detalles.get('Lp', 0) / 12:.2f} ft")
    print(f"    - Lr: {detalles.get('Lr', 0) / 12:.2f} ft")
    print("="*50)

def main():
    """Función principal que ejecuta el flujo de análisis."""
    
    # ==========================================================================
    # --- 1. DATOS DE ENTRADA (Configuración del Usuario) ---
    # ==========================================================================
    perfil_nombre = 'W40X503'
    material = {'Fy': 50, 'E': 29000, 'G': 11200} # ksi
    
    # Parámetros para análisis a flexión
    params_viga = {
        'Lb': 137.794, # Longitud no arriostrada en pulgadas
        'Cb': 1.0,      # Factor Cb (1.0 es conservador)
    }

    # Parámetros para análisis a compresión
    params_columna = {
        'Lx': 137.794, 'Ly': 137.794, 'Lz': 137.794, # Longitudes en pulgadas
        'Kx': 1.0, 'Ky': 1.0, 'Kz': 1.0
    }
    
    # Cargas requeridas (actuantes) para efectos combinados
    cargas_requeridas = {
        'Pr': 337,      # kips
        'Mrx': 445.9 * 12, # kip-in
        'Mry': 64.9 * 12   # kip-in
    }

    # Control de flujo
    revisar_efectos_combinados = True
    phi_c, phi_b = 0.90, 0.90 # Factores de reducción LRFD

    # ==========================================================================
    # --- 2. INICIALIZACIÓN Y OBTENCIÓN DE PROPIEDADES ---
    # ==========================================================================
    try:
        db = DatabaseAISC()
        respuesta_db = db.obtener_propiedades_perfil(perfil_nombre)
        if respuesta_db['status'] == 'Error':
            print(respuesta_db['mensaje'])
            return
        seccion = respuesta_db['propiedades']
        print(f"Análisis para el perfil: {perfil_nombre} (Fy = {material['Fy']} ksi)")
    except FileNotFoundError:
        print("\nError: No se encontró 'aisc-shapes-database-v15.0.xlsx'.")
        return
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return

    # ==========================================================================
    # --- 3. ANÁLISIS DE RESISTENCIA ---
    # ==========================================================================

    # --- Análisis a Flexión (Eje Fuerte) ---
    params_viga['eje'] = 'mayor'
    resultado_flexion_x = calcular_resistencia_flexion(material, seccion, params_viga)
    imprimir_resultados("Flexión - Eje Fuerte (X-X)", resultado_flexion_x)
    Mnx = resultado_flexion_x.get('valor_calculado_Mn', 0)

    # --- Verificación de Efectos Combinados ---
    if revisar_efectos_combinados:
        
        # --- Análisis a Flexión (Eje Débil) ---
        params_viga['eje'] = 'menor'
        # NOTA: La lógica para flexión en eje débil no estaba en 'flexion.m'.
        # Se usa una simplificación común: Momento plástico del eje débil.
        # Una implementación completa requeriría añadir el Caso F6 del AISC a flexure_analysis.py
        Mny = material['Fy'] * seccion.get('Zy', 0)
        print("\n" + "="*50)
        print("RESULTADOS: Flexión - Eje Débil (Y-Y) (Simplificado)")
        print(f"  - Resistencia Nominal (Mny):   {Mny / 12:.2f} kip-ft")
        print("="*50)
        
        # --- Análisis a Compresión ---
        resultado_compresion = calcular_resistencia_compresion(material, seccion, params_columna)
        Pn = resultado_compresion.get('valor_calculado_Pn', 0)
        print("\n" + "="*50)
        print("RESULTADOS: Compresión Axial")
        print(f"  - Resistencia Nominal (Pn):   {Pn:.2f} kips")
        print(f"  - Resistencia de Diseño (φcPn): {Pn * phi_c:.2f} kips")
        print("="*50)

        # --- Verificación por Interacción (Capítulo H) ---
        resistencias_disponibles = {
            'Pc': Pn * phi_c,
            'Mcx': Mnx * phi_b,
            'Mcy': Mny * phi_b
        }
        
        resultado_interaccion = verificar_interaccion_flexo_compresion(
            cargas_requeridas,
            resistencias_disponibles
        )
        print("\n" + "="*50)
        print("VERIFICACIÓN: Efectos Combinados (Flexo-Compresión)")
        print(f"  - Estado: {resultado_interaccion['status']}")
        print(f"  - Ratio Demanda/Capacidad: {resultado_interaccion.get('ratio_demanda_capacidad', 0):.3f}")
        print(f"  - Mensaje: {resultado_interaccion['mensaje']}")
        print("="*50)

if __name__ == "__main__":
    main()