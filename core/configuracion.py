# calculos/configuracion.py (ACTUALIZADO PARA DESACOPLAR)
# -*- coding: utf-8 -*-
import datetime
from enum import Enum

class NormativaAcciones(Enum):
    """Enumeración para las normativas de ACCIONES (cargas y combinaciones)."""
    ASCE_7_22 = "ASCE 7-22 (Equivalente a AISC 360-22)"
    NTC_ACCIONES_2023 = "NTC-CDMX-2023 (Acciones y Criterios)"

class NormativaDisenoAcero(Enum):
    """Enumeración para las normativas de DISEÑO (resistencia de elementos)."""
    AISC_360_22 = "AISC 360-22"
    NTC_ACERO_2020 = "NTC-Acero-2020"

class MetodoDiseno(Enum):
    LRFD = "LRFD (Load and Resistance Factor Design)"
    ASD = "ASD (Allowable Strength Design)"

class ProyectoConfig:
    """Clase para almacenar la configuración general del proyecto."""
    UNIDADES_PERMITIDAS = {
        'fuerza': ['kN', 'kips', 'N', 'lbf'],
        'longitud': ['m', 'ft', 'mm', 'in'],
        'momento': ['kNm', 'kip-ft', 'Nm', 'lbf-in'],
        'esfuerzo': ['MPa', 'ksi', 'Pa', 'psi']
    }

    def __init__(self,
                 nombre_proyecto: str, ubicacion: str, titulo: str,
                 normativa_acciones: NormativaAcciones,
                 normativa_diseno: NormativaDisenoAcero,
                 metodo_diseno: MetodoDiseno = MetodoDiseno.LRFD,
                 id_proyecto: str = "S/N",
                 descripcion_elemento: str = "Viga de Acero Genérica",
                 cliente: str = "N/A",
                 ingeniero_responsable: str = "N/A",
                 revisor: str = "N/A",
                 fecha_emision: str = datetime.date.today().strftime('%Y-%m-%d'),
                 revision: str = "A",
                 unidades: dict = None):
        
        # ... (Asignación de datos del reporte sin cambios) ...
        self.nombre_proyecto = nombre_proyecto
        self.ubicacion = ubicacion
        self.titulo = titulo
        self.id_proyecto = id_proyecto
        self.descripcion_elemento = descripcion_elemento # <-- LÍNEA FALTANTE
        self.cliente = cliente
        self.ingeniero_responsable = ingeniero_responsable
        self.revisor = revisor
        self.fecha_emision = fecha_emision
        self.revision = revision

        # --- Validación y asignación de datos de configuración DESACOPLADOS ---
        if not isinstance(normativa_acciones, NormativaAcciones):
            raise TypeError("La 'normativa_acciones' debe ser una instancia de NormativaAcciones.")
        self.normativa_acciones = normativa_acciones

        if not isinstance(normativa_diseno, NormativaDisenoAcero):
            raise TypeError("La 'normativa_diseno' debe ser una instancia de NormativaDisenoAcero.")
        self.normativa_diseno = normativa_diseno

        if not isinstance(metodo_diseno, MetodoDiseno):
            raise TypeError("El 'metodo_diseno' debe ser una instancia de MetodoDiseno.")
        self.metodo_diseno = metodo_diseno
        
        # ... (Configuración de unidades sin cambios) ...
        if unidades is None:
            self.unidades = {'fuerza': 'kN', 'longitud': 'm', 'momento': 'kNm', 'esfuerzo': 'MPa'}
        else:
            self._validar_unidades(unidades)
            self.unidades = unidades

    def _validar_unidades(self, unidades_ingresadas):
        """Método privado para validar el diccionario de unidades."""
        if not isinstance(unidades_ingresadas, dict):
            raise TypeError("El parámetro 'unidades' debe ser un diccionario.")
        
        for categoria, opciones_validas in self.UNIDADES_PERMITIDAS.items():
            if categoria not in unidades_ingresadas:
                raise ValueError(f"Falta la clave de unidad requerida: '{categoria}'.")
            if unidades_ingresadas[categoria] not in opciones_validas:
                raise ValueError(
                    f"Unidad '{unidades_ingresadas[categoria]}' no es válida para '{categoria}'. "
                    f"Opciones válidas: {opciones_validas}"
                )

 # --- MÉTODO generar_encabezado_reporte ACTUALIZADO ---
    def generar_encabezado_reporte(self) -> str:
        """
        Genera una cadena de texto con formato de encabezado para una memoria de cálculo.
        """
        encabezado = f"""
======================================================================
                               MEMORIA DE CÁLCULO
======================================================================
**Proyecto:** {self.nombre_proyecto} ({self.id_proyecto})
**Ubicación:** {self.ubicacion}
**Cliente:** {self.cliente}
----------------------------------------------------------------------
**Título del Reporte:** {self.titulo}
**Elemento Analizado:** {self.descripcion_elemento}
----------------------------------------------------------------------
**Normativa de Acciones:** {self.normativa_acciones.value}
**Normativa de Diseño:** {self.normativa_diseno.value}
**Método de Diseño:** {self.metodo_diseno.value}
**Fecha de Emisión:** {self.fecha_emision}
**Revisión:** {self.revision}
----------------------------------------------------------------------
**Realizado por:** {self.ingeniero_responsable}
**Revisado por:** {self.revisor}
======================================================================
"""
        return encabezado

    def __repr__(self):
        # ... (Este método no necesita cambios)
        return (f"ProyectoConfig(id='{self.id_proyecto}', "
                f"acciones='{self.normativa_acciones.value}', "
                f"diseno='{self.normativa_diseno.value}')")
