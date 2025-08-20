# calculos/material.py
# -*- coding: utf-8 -*-
from core.config import ProyectoConfig

# ==============================================================================
# MÓDULO 3 (Parte A): PROPIEDADES DEL MATERIAL
# ==============================================================================

class MaterialAcero:
    """
    Representa las propiedades mecánicas de un grado de acero específico.
    """
    def __init__(self, nombre: str, Fy: float, Fu: float, config: ProyectoConfig):
        """
        Inicializa el material de acero.

        Args:
            nombre (str): Nombre o designación del grado del acero (ej. "ASTM A992").
            Fy (float): Esfuerzo de fluencia mínimo especificado.
            Fu (float): Esfuerzo de ruptura mínimo especificado.
            config (ProyectoConfig): El objeto de configuración del proyecto para consistencia de unidades.
        """
        # El Módulo de Elasticidad (E) es prácticamente constante para todos los aceros estructurales.
        # Lo definimos aquí basándonos en el sistema de unidades del proyecto.
        unidades = config.unidades
        if unidades['esfuerzo'] in ['MPa', 'Pa']:
            self.E = 200000.0  # Módulo de Elasticidad en MPa
        elif unidades['esfuerzo'] in ['ksi', 'psi']:
            self.E = 29000.0   # Módulo de Elasticidad en ksi
        else:
            # Valor por defecto si la unidad no es reconocida, aunque ya está validada en config.
            self.E = 200000.0

        if not all(isinstance(i, (int, float)) and i > 0 for i in [Fy, Fu]):
            raise ValueError("Fy y Fu deben ser números positivos.")
        
        self.nombre = nombre
        self.Fy = Fy
        self.Fu = Fu
        self.config = config

    def __repr__(self):
        """Representación del objeto para desarrolladores."""
        return f"MaterialAcero(nombre='{self.nombre}', Fy={self.Fy} {self.config.unidades['esfuerzo']})"

    # --- MÉTODOS DE FÁBRICA (FACTORY METHODS) ---
    # Estos métodos nos permiten crear aceros comunes sin tener que recordar sus propiedades.
    
    @classmethod
    def ASTM_A992(cls, config: ProyectoConfig):
        """Crea un material ASTM A992 (común para perfiles W en EEUU y México)."""
        unidades = config.unidades
        if unidades['esfuerzo'] == 'MPa':
            return cls(nombre="ASTM A992", Fy=345.0, Fu=450.0, config=config)
        elif unidades['esfuerzo'] == 'ksi':
            return cls(nombre="ASTM A992", Fy=50.0, Fu=65.0, config=config)
        raise ValueError(f"Unidades de esfuerzo no soportadas para A992: {unidades['esfuerzo']}")

    @classmethod
    def ASTM_A36(cls, config: ProyectoConfig):
        """Crea un material ASTM A36 (común para perfiles C, L y placas)."""
        unidades = config.unidades
        if unidades['esfuerzo'] == 'MPa':
            return cls(nombre="ASTM A36", Fy=250.0, Fu=400.0, config=config)
        elif unidades['esfuerzo'] == 'ksi':
            return cls(nombre="ASTM A36", Fy=36.0, Fu=58.0, config=config)
        raise ValueError(f"Unidades de esfuerzo no soportadas para A36: {unidades['esfuerzo']}")