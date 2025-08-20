# calculos/arriostramiento.py (VERSIÓN FINAL CON ARRIOSTRAMIENTO TORSIONAL)
# -*- coding: utf-8 -*-
import collections
from enum import Enum
from core.config import MetodoDiseno, ProyectoConfig

# --- CLASES (sin cambios) ---
class ArriostramientoTipo(Enum):
    PUNTUAL = "puntual"; PANEL = "panel"

class CurvaturaTipo(Enum):
    DOBLE = "doble"; NORMAL = "normal"

class CalculadoraArriostramiento:
    """
    Calcula los requisitos de resistencia y rigidez para el arriostramiento
    de columnas y vigas, utilizando la configuración global del proyecto.
    """
    FACTORES_RESISTENCIA = {'columna': {'puntual': 0.01, 'panel': 0.005}, 'viga_lateral': {'puntual': 0.02, 'panel': 0.01}}
    FACTORES_RIGIDEZ = {'columna': {'puntual': 8, 'panel': 2}, 'viga_lateral': {'puntual': 10, 'panel': 4}}
    
    def __init__(self, config: ProyectoConfig):
        self.config = config
        self.metodo_diseno = config.metodo_diseno
        self.phi = 0.75
        self.omega_lateral = 2.0
        self.omega_torsional = 3.0 # <-- Factor para arriostramiento torsional en ASD
        
        # Namedtuples para organizar las salidas
        self.ResultadoLateral = collections.namedtuple('ResultadoLateral', ['resistencia', 'rigidez'])
        self.ResultadoTorsional = collections.namedtuple('ResultadoTorsional', ['resistencia_momento', 'rigidez_torsional'])

    def _get_factor_analisis(self, tipo='lateral'):
        """Obtiene el factor multiplicador según el método de diseño (LRFD o ASD)."""
        if self.metodo_diseno == MetodoDiseno.LRFD:
            return 1 / self.phi
        # Para ASD
        return self.omega_torsional if tipo == 'torsional' else self.omega_lateral

    def arriostramiento_lateral_columna(self, Pr: float, Lbr: float, tipo_arriostramiento: ArriostramientoTipo):
        # ... (sin cambios aquí) ...
        factor_resistencia = self.FACTORES_RESISTENCIA['columna'][tipo_arriostramiento.value]
        Vbr = factor_resistencia * Pr
        factor_rigidez = self.FACTORES_RIGIDEZ['columna'][tipo_arriostramiento.value]
        factor_analisis = self._get_factor_analisis()
        Bbr = factor_analisis * (factor_rigidez * Pr / Lbr)
        return self.ResultadoLateral(resistencia=Vbr, rigidez=Bbr)

    def arriostramiento_lateral_viga(self, Mr: float, h0: float, Lbr: float, tipo_arriostramiento: ArriostramientoTipo, tipo_curvatura: CurvaturaTipo):
        # ... (sin cambios aquí) ...
        Cd = 2.0 if tipo_curvatura == CurvaturaTipo.DOBLE else 1.0
        factor_resistencia = self.FACTORES_RESISTENCIA['viga_lateral'][tipo_arriostramiento.value]
        Vbr = factor_resistencia * (Mr * Cd / h0)
        factor_rigidez = self.FACTORES_RIGIDEZ['viga_lateral'][tipo_arriostramiento.value]
        factor_analisis = self._get_factor_analisis()
        Bbr = factor_analisis * (factor_rigidez * Mr * Cd) / (h0 * Lbr)
        return self.ResultadoLateral(resistencia=Vbr, rigidez=Bbr)

    # --- ¡NUEVO MÉTODO RESTAURADO Y REFACTORIZADO! ---
    def arriostramiento_torsional_viga(self, Mr: float, Lbr: float):
        """
        Calcula la resistencia (Mbr) y rigidez (βT) requeridas para
        el arriostramiento torsional de una viga.
        """
        # Requisito de Resistencia (AISC Eq. A-6-7)
        Mbr = 0.024 * Mr
        
        # Requisito de Rigidez (AISC Eq. A-6-8)
        # NOTA: Este cálculo es más complejo y depende de factores como Cb, E, Ix y el
        # número de arriostramientos, que no estamos calculando en nuestro motor simple.
        # Por ahora, devolvemos un placeholder (valor 0.0) y lo marcaremos en el reporte.
        # En una futura versión, se podría implementar el cálculo completo.
        beta_T = 0.0 # Placeholder
        
        factor_analisis = self._get_factor_analisis(tipo='torsional')
        beta_T_req = factor_analisis * beta_T

        return self.ResultadoTorsional(resistencia_momento=Mbr, rigidez_torsional=beta_T_req)