# calculos/analizador.py
# -*- coding: utf-8 -*-
import numpy as np
from .model import Viga, TipoApoyo
from .loads import CargaPuntual, CargaDistribuida

class AnalizadorViga:
    """
    Motor de análisis estructural simple para una viga.
    Calcula reacciones, cortantes y momentos para una combinación de carga dada.
    """
    def __init__(self, viga: Viga):
        if not isinstance(viga, Viga):
            raise TypeError("El analizador requiere un objeto Viga válido.")
        self.viga = viga
        self.L = viga.longitud

    def analizar(self, combinacion: dict) -> dict:
        """
        Realiza el análisis para una combinación de carga específica.
        
        Args:
            combinacion (dict): Un diccionario que representa la combinación (ej. {'D': 1.2, 'L': 1.6}).
            
        Returns:
            dict: Un diccionario con los resultados del análisis (reacciones, Vu, Mu).
        """
        reaccion_A, reaccion_B, momento_A = 0.0, 0.0, 0.0
        
        # 1. Aplicar factores a las cargas
        cargas_factorizadas = self._aplicar_factores(combinacion)
        
        # 2. Calcular reacciones basadas en el tipo de apoyo
        if self.viga.tipo_apoyo == TipoApoyo.SIMPLE:
            for carga in cargas_factorizadas:
                if isinstance(carga, CargaPuntual):
                    P, a = carga.magnitud, carga.posicion
                    b = self.L - a
                    reaccion_A += P * b / self.L
                    reaccion_B += P * a / self.L
                elif isinstance(carga, CargaDistribuida):
                    w, a, b = carga.magnitud, carga.pos_inicio, carga.pos_fin
                    l_carga = b - a
                    P_total = w * l_carga
                    centroide = a + l_carga / 2
                    reaccion_A += P_total * (self.L - centroide) / self.L
                    reaccion_B += P_total * centroide / self.L

        elif self.viga.tipo_apoyo == TipoApoyo.CANTILEVER: # Apoyo A es el empotramiento
            for carga in cargas_factorizadas:
                if isinstance(carga, CargaPuntual):
                    P, a = carga.magnitud, carga.posicion
                    reaccion_A += P
                    momento_A -= P * a
                elif isinstance(carga, CargaDistribuida):
                    w, a, b = carga.magnitud, carga.pos_inicio, carga.pos_fin
                    l_carga = b - a
                    P_total = w * l_carga
                    centroide = a + l_carga / 2
                    reaccion_A += P_total
                    momento_A -= P_total * centroide

        # 3. Calcular diagramas y envolventes (simplificado)
        # Usamos numpy para crear los diagramas. 1000 puntos a lo largo de la viga.
        x = np.linspace(0, self.L, 1000)
        V = np.full_like(x, reaccion_A)
        M = np.full_like(x, momento_A)
        M += reaccion_A * x
        
        for carga in cargas_factorizadas:
            if isinstance(carga, CargaPuntual):
                V[x >= carga.posicion] -= carga.magnitud
                M[x >= carga.posicion] -= carga.magnitud * (x[x >= carga.posicion] - carga.posicion)
            elif isinstance(carga, CargaDistribuida):
                # Inicio de la carga
                V[x >= carga.pos_inicio] -= carga.magnitud * (x[x >= carga.pos_inicio] - carga.pos_inicio)
                M[x >= carga.pos_inicio] -= 0.5 * carga.magnitud * (x[x >= carga.pos_inicio] - carga.pos_inicio)**2
                # Fin de la carga
                V[x > carga.pos_fin] += carga.magnitud * (x[x > carga.pos_fin] - carga.pos_fin)
                M[x > carga.pos_fin] += 0.5 * carga.magnitud * (x[x > carga.pos_fin] - carga.pos_fin)**2
                
        Vu_max = max(abs(V.min()), abs(V.max()))
        Mu_max = max(abs(M.min()), abs(M.max()))

        return {
            "combinacion": combinacion,
            "reacciones": {"RA": reaccion_A, "RB": reaccion_B, "MA": momento_A},
            "Vu_max": Vu_max,
            "Mu_max": Mu_max,
        }

    def _aplicar_factores(self, combinacion: dict) -> list:
        """Filtra y factoriza las cargas de la viga según la combinación."""
        cargas_factorizadas = []
        for carga_original in self.viga.cargas:
            factor = combinacion.get(carga_original.caso_carga.name, 0)
            if factor > 0:
                # Creamos una nueva instancia de la carga con la magnitud factorizada
                magnitud_factorizada = carga_original.magnitud * factor
                if isinstance(carga_original, CargaPuntual):
                    cargas_factorizadas.append(
                        CargaPuntual(magnitud_factorizada, carga_original.posicion, carga_original.caso_carga)
                    )
                elif isinstance(carga_original, CargaDistribuida):
                    cargas_factorizadas.append(
                        CargaDistribuida(magnitud_factorizada, carga_original.pos_inicio, carga_original.pos_fin, carga_original.caso_carga)
                    )
        return cargas_factorizadas