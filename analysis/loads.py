# calculos/cargas.py
# -*- coding: utf-8 -*-
from enum import Enum

class CasoCarga(Enum):
    """Enumeración para los casos de carga primarios."""
    D = "Carga Muerta (Dead Load)"
    L = "Carga Viva (Live Load)"
    Lr = "Carga Viva de Azotea (Live Roof Load)"
    S = "Carga de Nieve (Snow Load)"
    W = "Carga de Viento (Wind Load)"
    E = "Carga de Sismo (Earthquake Load)"

class Carga:
    """Clase base para representar una carga en una viga."""
    def __init__(self, magnitud: float, caso_carga: CasoCarga):
        if not isinstance(caso_carga, CasoCarga):
            raise TypeError("El caso de carga debe ser una instancia de la clase CasoCarga.")
        self.magnitud = magnitud
        self.caso_carga = caso_carga

class CargaPuntual(Carga):
    """Representa una carga puntual."""
    def __init__(self, magnitud: float, posicion: float, caso_carga: CasoCarga):
        super().__init__(magnitud, caso_carga)
        self.posicion = posicion

    def __repr__(self):
        return f"CargaPuntual(mag={self.magnitud}, pos={self.posicion}, caso='{self.caso_carga.name}')"

class CargaDistribuida(Carga):
    """Representa una carga distribuida rectangular."""
    def __init__(self, magnitud: float, pos_inicio: float, pos_fin: float, caso_carga: CasoCarga):
        super().__init__(magnitud, caso_carga)
        self.pos_inicio = pos_inicio
        self.pos_fin = pos_fin

    def __repr__(self):
        return f"CargaDistribuida(mag={self.magnitud}, [{self.pos_inicio}-{self.pos_fin}], caso='{self.caso_carga.name}')"

# Podrían añadirse CargaMomento, CargaTriangular, etc. en el futuro.