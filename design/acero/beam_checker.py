# calculos/verificador.py (NUEVO MÓDULO)
# -*- coding: utf-8 -*-
from analysis.model import Viga
from core.config import NormativaDisenoAcero, MetodoDiseno

class VerificadorResistencia:
    """
    Clase base para los verificadores de resistencia.
    Selecciona el motor de cálculo de resistencia correcto según la normativa de diseño.
    """
    def __new__(cls, viga: Viga, Mu: float, Vu: float):
        config = viga.config
        norma_diseno = config.normativa_diseno
        
        if norma_diseno == NormativaDisenoAcero.AISC_360_22 and config.metodo_diseno == MetodoDiseno.LRFD:
            # Si se elige AISC, crea una instancia del verificador específico para AISC
            return VerificadorAISC36022_LRFD(viga, Mu, Vu)
        
        # Futuro: Añadir otros verificadores
        # elif norma_diseno == NormativaDisenoAcero.NTC_ACERO_2020:
        #     return VerificadorNTCAcero2020_LRFD(viga, Mu, Vu)
            
        raise NotImplementedError(f"No hay un motor de verificación de resistencia para {norma_diseno.value}")

class VerificadorAISC36022_LRFD:
    """Calcula la resistencia de una viga de acero según AISC 360-22 (LRFD)."""
    def __init__(self, viga: Viga, Mu: float, Vu: float):
        self.viga = viga
        self.Mu = Mu  # Momento último requerido (Acción)
        self.Vu = Vu  # Cortante último requerido (Acción)
        self.perfil = viga.perfil_asignado
        self.material = self.perfil.material
        
        # Factores de Resistencia (φ) para LRFD
        self.phi_b = 0.90  # Factor de resistencia a flexión
        self.phi_v = 0.90  # Factor de resistencia a cortante (para almas sin rigidizar)

    def revisar_flexion(self) -> dict:
        """
        Revisa la viga por flexión (Capítulo F, AISC 360-22).
        NOTA: Implementación simplificada asumiendo sección compacta y Lb=0.
        """
        # Resistencia Nominal a Momento (Mn)
        # Asumimos que la sección es compacta y no hay pandeo lateral-torsional (PLT).
        # Mp = Momento plástico = Fy * Zx
        Mp = self.material.Fy * self.perfil.Zx
        Mn = Mp
        
        # Resistencia de Diseño a Momento (φMn)
        phi_Mn = self.phi_b * Mn

        # Conversión de unidades si es necesario (ej. Zx de mm3 a m3)
        unidad_long = self.viga.config.unidades['longitud']
        if unidad_long in ['m', 'mm']:
            # Zx(mm3) * Fy(MPa=N/mm2) = N*mm. Convertir a kNm
            phi_Mn /= (1000 * 1000)
            
        ratio = self.Mu / phi_Mn
        status = "CUMPLE" if ratio <= 1.0 else "NO CUMPLE"
        
        return {"Mu": self.Mu, "phi_Mn": phi_Mn, "Ratio": ratio, "Status": status}

    def revisar_cortante(self) -> dict:
        """
        Revisa la viga por cortante (Capítulo G, AISC 360-22).
        NOTA: Implementación simplificada.
        """
        # Resistencia Nominal a Cortante (Vn)
        # Vn = 0.6 * Fy * Aw * Cv1  (asumimos Cv1=1.0)
        Aw = self.perfil.d * self.perfil.tw # Área del alma
        Vn = 0.6 * self.material.Fy * Aw
        
        # Resistencia de Diseño a Cortante (φVn)
        phi_Vn = self.phi_v * Vn

        # Conversión de unidades si es necesario (ej. Aw de mm2 a m2)
        if self.viga.config.unidades['longitud'] in ['m', 'mm']:
            # Fy(MPa=N/mm2) * Aw(mm2) = N. Convertir a kN
            phi_Vn /= 1000

        ratio = self.Vu / phi_Vn
        status = "CUMPLE" if ratio <= 1.0 else "NO CUMPLE"

        return {"Vu": self.Vu, "phi_Vn": phi_Vn, "Ratio": ratio, "Status": status}