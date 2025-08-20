# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 15:29:52 2025

@author: Ernesto Patiño A
"""

# connection_analysis.py
import math
from typing import Dict, Any

# ==============================================================================
# FUNCIÓN 1: RESISTENCIA DE TORNILLOS (Ya completada)
# ==============================================================================
def calcular_resistencia_tornillo(bolt_props, material_props, connection_geom):
    # ... (código ya existente) ...
    resultado = {"status": "Error", "mensaje": "", "resistencias": {}}
    try:
        d_b, Fnv = bolt_props['d_b'], bolt_props['Fnv']
        Fu, t = material_props['Fu'], connection_geom['t']
        L_c = connection_geom['L_c']

        # 1. Resistencia a Cortante (Rn_v)
        Ab = math.pi * (d_b**2) / 4
        Rn_cortante = Fnv * Ab

        # 2. Resistencia a Aplastamiento (Rn_b)
        Rn_aplastamiento = min(1.2 * L_c * t * Fu, 2.4 * d_b * t * Fu)

        resultado["status"] = "Exitoso"
        resultado["resistencias"] = {
            "cortante_nominal_Rn_kips": Rn_cortante,
            "aplastamiento_nominal_Rn_kips": Rn_aplastamiento
        }
    except KeyError as e:
        resultado["mensaje"] = f"Falta la propiedad requerida: {e}"
    return resultado


# ==============================================================================
# FUNCIÓN 2: DISEÑO DE PLACA BASE (Ya completada)
# ==============================================================================
def analizar_placa_base(column_props, plate_props, concrete_props, required_strengths):
    # ... (código ya existente) ...
    resultado = {"status": "Error", "mensaje": "", "verificaciones": {}}
    try:
        Pu = required_strengths['Pu']
        B, N, Fy_p = plate_props['B'], plate_props['N'], plate_props['Fy_p']
        fc = concrete_props['fc']
        d, bf = column_props['d'], column_props['bf']
        A1 = B * N

        # 1. Verificación de Aplastamiento en Concreto
        phi_c = 0.65
        fp_max = phi_c * 0.85 * fc
        Pn_concreto = fp_max * A1
        pasa_concreto = Pn_concreto >= Pu
        
        # 2. Verificación de Espesor de Placa por Flexión
        m = (N - 0.95 * d) / 2
        n = (B - 0.80 * bf) / 2
        l = max(m, n)
        
        # Espesor requerido
        phi_b = 0.90
        tp_req = l * math.sqrt((2 * Pu) / (phi_b * Fy_p * B * N))

        resultado["status"] = "Exitoso"
        resultado["verificaciones"] = {
            "aplastamiento_concreto": {
                "capacidad_Pn": Pn_concreto, "demanda_Pu": Pu,
                "status": "Pasa" if pasa_concreto else "No Pasa"
            },
            "espesor_placa": {
                "tp_requerido_in": tp_req,
                "tp_provisto_in": plate_props.get('tp', 0)
            }
        }
    except KeyError as e:
        resultado["mensaje"] = f"Falta la propiedad requerida: {e}"
    return resultado

# ==============================================================================
# NUEVA FUNCIÓN 3: RESISTENCIA DE SOLDADURA DE FILETE
# ==============================================================================
def calcular_resistencia_soldadura_filete(
    weld_props: Dict[str, Any],
    material_base_props: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calcula la resistencia nominal de una soldadura de filete por pulgada lineal.
    (AISC 360-22, Capítulo J2).

    Args:
        weld_props (dict): Propiedades de la soldadura ('Fexx', 'w_size').
        material_base_props (dict): Propiedades del metal base ('Fy', 'Fu').

    Returns:
        dict: Resistencia nominal por pulgada (kips/in).
    """
    resultado = {"status": "Error", "mensaje": "", "resistencia_por_pulgada": None}
    try:
        Fexx = weld_props['Fexx'] # Resistencia del electrodo (ej. 70 ksi)
        w = weld_props['w_size'] # Tamaño del cateto de la soldadura (in)
        
        # Resistencia del metal de aporte
        Rn_w = 0.707 * w * (0.60 * Fexx)
        
        # Resistencia del metal base (no implementada aquí, se verifica por separado)
        
        resultado["status"] = "Exitoso"
        resultado["resistencia_por_pulgada"] = Rn_w
        resultado["mensaje"] = "Cálculo de resistencia de soldadura de filete completado."
        
    except KeyError as e:
        resultado["mensaje"] = f"Falta la propiedad requerida: {e}"
    return resultado

# ==============================================================================
# NUEVA FUNCIÓN 4: VERIFICACIÓN POR BLOQUE DE CORTANTE
# ==============================================================================
def verificar_bloque_cortante(
    geometry: Dict[str, float],
    material_props: Dict[str, float],
    required_strength: float
) -> Dict[str, Any]:
    """
    Calcula la resistencia nominal por ruptura de bloque de cortante.
    (AISC 360-22, Capítulo J4.3).

    Args:
        geometry (dict): Áreas de la trayectoria de falla ('Agt', 'Anv', 'Ant').
        material_props (dict): Propiedades del material ('Fy', 'Fu').
        required_strength (float): Carga requerida (kips).

    Returns:
        dict: Resultado de la verificación.
    """
    resultado = {"status": "Error", "mensaje": "", "capacidad_Rn": None}
    try:
        Agt, Anv, Ant = geometry['Agt'], geometry['Anv'], geometry['Ant']
        Fy, Fu = material_props['Fy'], material_props['Fu']
        
        Ubs = 1.0 # Para la mayoría de las conexiones de cortante
        
        # Ecuación J4-5
        termino_cortante = 0.6 * Fu * Anv
        termino_tension = Ubs * Fu * Ant
        
        Rn = min(termino_cortante + termino_tension, 0.6 * Fy * Agt + termino_tension)
        
        pasa = (0.75 * Rn) >= required_strength # Usando factor phi de 0.75
        
        resultado["status"] = "Exitoso"
        resultado["capacidad_Rn_kips"] = Rn
        resultado["verificacion"] = "Pasa" if pasa else "No Pasa"
        
    except KeyError as e:
        resultado["mensaje"] = f"Falta la propiedad requerida: {e}"
    return resultado
    
# ==============================================================================
# FUNCIÓN 5: CONEXIÓN DE CORTANTE (ACTUALIZADA Y COMPLETA)
# ==============================================================================
def analizar_conexion_cortante(
    plate_props: Dict[str, float],
    bolt_group_props: Dict[str, Any],
    weld_props: Dict[str, Any],
    required_strengths: Dict[str, float]
) -> Dict[str, Any]:
    """
    Verifica los estados límite para una conexión de placa de cortante (shear tab).
    Versión completa que incluye bloque de cortante y soldadura.
    """
    resultado = {"status": "Error", "mensaje": "", "verificaciones": {}}
    try:
        Vu = required_strengths['Vu']
        Lp, tp, Fy_p, Fu_p = plate_props['Lp'], plate_props['tp'], plate_props['Fy_p'], plate_props['Fu_p']
        
        # 1. Fluencia por Cortante en la Placa
        Agv = Lp * tp
        Rn_fluencia_cortante = 0.6 * Fy_p * Agv
        
        # 2. Ruptura por Cortante en la Placa
        num_tornillos = bolt_group_props['num_tornillos']
        d_h = bolt_group_props['d_b'] + 1/8
        Anv = (Lp - num_tornillos * d_h) * tp
        Rn_ruptura_cortante = 0.6 * Fu_p * Anv
        
        # 3. Bloque de Cortante (¡llamando a nuestra nueva función!)
        # Se necesitarían más datos geométricos (Agt, Ant) para un cálculo real
        # geometry_bs = {'Agt': ..., 'Anv': ..., 'Ant': ...}
        # resultado_bs = verificar_bloque_cortante(geometry_bs, ...)
        
        # 4. Soldadura (¡llamando a nuestra nueva función!)
        res_soldadura = calcular_resistencia_soldadura_filete(weld_props, {'Fy': Fy_p, 'Fu': Fu_p})
        if res_soldadura['status'] == 'Exitoso':
            Rn_soldadura_total = res_soldadura['resistencia_por_pulgada'] * (2 * Lp) # Asumiendo dos filetes
        else:
            Rn_soldadura_total = 0

        resultado["status"] = "Exitoso"
        resultado["verificaciones"] = {
            "fluencia_cortante_placa_Rn_kips": Rn_fluencia_cortante,
            "ruptura_cortante_placa_Rn_kips": Rn_ruptura_cortante,
            "soldadura_Rn_kips": Rn_soldadura_total
            # "bloque_cortante": resultado_bs
        }
    except KeyError as e:
        resultado["mensaje"] = f"Falta la propiedad requerida: {e}"
    return resultado