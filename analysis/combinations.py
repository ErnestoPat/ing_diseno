# calculos/combinaciones.py (ACTUALIZADO)
# -*- coding: utf-8 -*-
from core.config import ProyectoConfig, NormativaAcciones, MetodoDiseno

class GestorCombinaciones:
    def __init__(self, config: ProyectoConfig):
        self.config = config

    def obtener_combinaciones(self) -> list[dict]:
        # --- Lógica ahora depende de `normativa_acciones` ---
        norma = self.config.normativa_acciones
        
        if norma == NormativaAcciones.ASCE_7_22 and self.config.metodo_diseno == MetodoDiseno.LRFD:
            return [{"D": 1.4}, {"D": 1.2, "L": 1.6}]
            
        elif norma == NormativaAcciones.NTC_ACCIONES_2023 and self.config.metodo_diseno == MetodoDiseno.LRFD:
            print("INFO: Usando combinaciones de carga de las NTC-CDMX-2023.")
            return [{"D": 1.3}, {"D": 1.3, "L": 1.5}]
        
        raise NotImplementedError(f"Combinaciones para {norma.value} no implementadas.")