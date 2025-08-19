# calculos/viga.py (ACTUALIZADO)
# -*- coding: utf-8 -*-
from enum import Enum
from .configuracion import ProyectoConfig
from .perfil import PerfilAcero
from .cargas import Carga

class TipoApoyo(Enum):
    # ... (sin cambios aquí)
    SIMPLE = "Simplemente apoyada (Articulación - Rodillo)"
    CANTILEVER = "Cantilever (Empotramiento - Libre)"
    DOBLE_EMPOTRAMIENTO = "Doble empotramiento (Empotramiento - Empotramiento)"

class Viga:
    # ... (el __init__ se queda igual)
    def __init__(self,
                 longitud: float,
                 tipo_apoyo: TipoApoyo,
                 config: ProyectoConfig):
        # ... (sin cambios aquí)
        self.longitud = longitud
        self.tipo_apoyo = tipo_apoyo
        self.config = config
        self.perfil_asignado = None # El valor inicial es None
        self.cargas = []

    def asignar_perfil(self, perfil: PerfilAcero):
        """
        Asigna un objeto PerfilAcero a la viga.
        """
        if not isinstance(perfil, PerfilAcero):
            raise TypeError("Se debe asignar un objeto de la clase PerfilAcero.")
        self.perfil_asignado = perfil
        print(f"\nPerfil '{perfil.nombre}' con material '{perfil.material.nombre}' asignado a la viga.")

    def agregar_carga(self, carga: Carga):
        """Añade un objeto de carga a la lista de cargas de la viga."""
        if not isinstance(carga, Carga):
            raise TypeError("El objeto a añadir debe ser una instancia de la clase Carga.")
        self.cargas.append(carga)
        print(f"Carga agregada: {carga}")

    # --- MÉTODO ACTUALIZADO ---
    def describir_geometria(self) -> str:
        """
        Genera una cadena de texto describiendo las propiedades de la viga.
        """
        unidad_long = self.config.unidades['longitud']
        unidad_esfuerzo = self.config.unidades['esfuerzo']
        
        descripcion = (
            f"Descripción de la Viga y sus Propiedades:\n"
            f"--------------------------------------------\n"
            f"  - Longitud Total: {self.longitud} {unidad_long}\n"
            f"  - Condiciones de Apoyo: {self.tipo_apoyo.value}\n"
        )
        
        # Si ya se asignó un perfil, lo añadimos a la descripción
        if self.perfil_asignado:
            perfil = self.perfil_asignado
            descripcion += (
                f"  - Perfil Asignado: {perfil.nombre}\n"
                f"  - Material del Acero: {perfil.material.nombre}\n"
                f"  - Esfuerzo de Fluencia (Fy): {perfil.material.Fy} {unidad_esfuerzo}\n"
                f"  - Módulo de Elasticidad (E): {perfil.material.E} {unidad_esfuerzo}\n"
            )
        
        descripcion += f"--------------------------------------------"
        return descripcion

    # ... (__repr__ se queda igual)
    def __repr__(self):
        return (f"Viga(longitud={self.longitud} {self.config.unidades['longitud']}, "
                f"apoyo='{self.tipo_apoyo.name}')")