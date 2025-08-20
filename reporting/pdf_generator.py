# report_generator.py (VERSIÓN COMPLETA Y FINAL)
# -*- coding: utf-8 -*-

import os
from fpdf import FPDF
from core.config import ProyectoConfig
from analysis.model import Viga
from analysis.loads import CargaPuntual, CargaDistribuida

class ReportePDF(FPDF):
    """
    Clase para generar la memoria de cálculo completa en formato PDF
    utilizando la fuente estándar Arial.
    """
    def __init__(self, config: ProyectoConfig, viga: Viga, envolvente: dict, resultados_diseno: dict, res_arriostramiento: dict):
        super().__init__()
        # Almacenamos todos los datos necesarios para el reporte
        self.config = config
        self.viga = viga
        self.envolvente = envolvente
        self.res_flexion = resultados_diseno['flexion']
        self.res_cortante = resultados_diseno['cortante']
        self.res_arr_lateral = res_arriostramiento['lateral']
        self.res_arr_torsional = res_arriostramiento['torsional']
        
        # Usamos Arial como fuente principal por su compatibilidad
        self.font_family = 'Arial'

        self.add_page()
        self.set_font(self.font_family, '', 10)

    def header(self):
        """Define el encabezado de cada página del reporte."""
        self.set_font(self.font_family, 'B', 14)
        self.cell(0, 10, 'Memoria de Cálculo Estructural', 0, 1, 'C')
        self.set_font(self.font_family, 'I', 8)
        self.cell(0, 5, f"Proyecto: {self.config.nombre_proyecto}", 0, 1, 'C')
        self.ln(10)

    def footer(self):
        """Define el pie de página, incluyendo el número de página."""
        self.set_y(-15)
        self.set_font(self.font_family, 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def titulo_seccion(self, titulo):
        """Crea un formato estandarizado para los títulos de sección."""
        self.set_font(self.font_family, 'B', 12)
        self.cell(0, 10, titulo, 0, 1, 'L')
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(5)

    def escribir_datos_generales(self):
        """Escribe la Sección 1: Datos Generales del Proyecto."""
        self.titulo_seccion('1. Datos Generales del Proyecto')
        datos = {
            "Elemento Analizado": self.config.descripcion_elemento,
            "Normativa de Acciones": self.config.normativa_acciones.value,
            "Normativa de Diseño": self.config.normativa_diseno.value,
            "Método de Diseño": self.config.metodo_diseno.value,
            "Fecha": self.config.fecha_emision,
            "Revisión": self.config.revision
        }
        for clave, valor in datos.items():
            self.set_font(self.font_family, 'B', 10)
            self.multi_cell(50, 8, f"{clave}:", border=1)
            self.set_xy(self.get_x() + 50, self.get_y() - 8)
            self.set_font(self.font_family, '', 10)
            self.multi_cell(140, 8, f"{valor}", border=1)
        self.ln(10)

    def escribir_propiedades_elemento(self):
        """Escribe la Sección 2: Propiedades del Elemento."""
        self.titulo_seccion('2. Propiedades del Elemento')
        perfil = self.viga.perfil_asignado
        unidades = self.config.unidades
        propiedades = {
            "Longitud": f"{self.viga.longitud} {unidades['longitud']}",
            "Condiciones de Apoyo": self.viga.tipo_apoyo.value,
            "Perfil de Acero": perfil.nombre,
            "Material": perfil.material.nombre,
            "Esfuerzo de Fluencia (Fy)": f"{perfil.material.Fy} {unidades['esfuerzo']}",
            "Módulo de Elasticidad (E)": f"{perfil.material.E} {unidades['esfuerzo']}",
            "Módulo Plástico (Zx)": f"{perfil.Zx:.2f} mm³" if unidades['longitud'] == 'm' else f"{perfil.Zx:.2f} in³"
        }
        for clave, valor in propiedades.items():
            self.set_font(self.font_family, 'B', 10)
            self.cell(60, 8, f"{clave}:", border='B')
            self.set_font(self.font_family, '', 10)
            self.cell(0, 8, f"{valor}", border='B', ln=1)
        self.ln(10)

    def escribir_cargas_aplicadas(self):
        """Escribe la Sección 3: Cargas Aplicadas (sin factorizar)."""
        self.titulo_seccion('3. Cargas Aplicadas (Sin factorizar)')
        self.set_font(self.font_family, 'B', 10)
        self.cell(30, 8, "Tipo", 1, 0, 'C'); self.cell(40, 8, "Magnitud", 1, 0, 'C')
        self.cell(80, 8, "Ubicación", 1, 0, 'C'); self.cell(40, 8, "Caso de Carga", 1, 1, 'C')
        self.set_font(self.font_family, '', 10)
        for carga in self.viga.cargas:
            if isinstance(carga, CargaPuntual):
                self.cell(30, 8, "Puntual", 1)
                self.cell(40, 8, f"{carga.magnitud} {self.config.unidades['fuerza']}", 1)
                self.cell(80, 8, f"en x = {carga.posicion} {self.config.unidades['longitud']}", 1)
                self.cell(40, 8, carga.caso_carga.name, 1, 1)
            elif isinstance(carga, CargaDistribuida):
                self.cell(30, 8, "Distribuida", 1)
                self.cell(40, 8, f"{carga.magnitud} {self.config.unidades['fuerza']}/{self.config.unidades['longitud']}", 1)
                self.cell(80, 8, f"de x={carga.pos_inicio} a x={carga.pos_fin} {self.config.unidades['longitud']}", 1)
                self.cell(40, 8, carga.caso_carga.name, 1, 1)
        self.ln(10)
    
    def escribir_resultados_analisis(self):
        """Escribe la Sección 4: Solicitaciones de Diseño (Envolvente)."""
        self.titulo_seccion('4. Solicitaciones de Diseño (Envolvente)')
        unidades = self.config.unidades
        self.set_font(self.font_family, '', 10)
        self.multi_cell(0, 5, "Los siguientes valores representan las máximas solicitaciones encontradas después de analizar todas las combinaciones de carga aplicables.")
        self.ln(3)
        self.set_font(self.font_family, 'B', 11)
        self.cell(60, 8, "Momento Último (Mu):")
        self.set_font(self.font_family, '', 11)
        self.cell(0, 8, f"{self.envolvente['Mu']:.2f} {unidades['momento']}", ln=1)
        self.set_font(self.font_family, 'B', 11)
        self.cell(60, 8, "Cortante Último (Vu):")
        self.set_font(self.font_family, '', 11)
        self.cell(0, 8, f"{self.envolvente['Vu']:.2f} {unidades['fuerza']}", ln=1)
        self.ln(10)
        
    def escribir_verificacion_resistencia(self):
        """Escribe la Sección 5: Verificación de Resistencia."""
        self.titulo_seccion('5. Verificación de Resistencia')
        unidades = self.config.unidades
        self.set_font(self.font_family, 'B', 10)
        self.cell(0, 8, "Revisión por Flexión", 0, 1)
        self.cell(47.5, 8, "Solicitación (Mu)", 1, 0, 'C'); self.cell(47.5, 8, "Resistencia (phi*Mn)", 1, 0, 'C')
        self.cell(47.5, 8, "Ratio (Mu/phi*Mn)", 1, 0, 'C'); self.cell(47.5, 8, "Estatus", 1, 1, 'C')
        self.set_font(self.font_family, '', 10)
        self.cell(47.5, 8, f"{self.res_flexion['Mu']:.2f} {unidades['momento']}", 1, 0, 'C')
        self.cell(47.5, 8, f"{self.res_flexion['phi_Mn']:.2f} {unidades['momento']}", 1, 0, 'C')
        self.cell(47.5, 8, f"{self.res_flexion['Ratio']:.3f}", 1, 0, 'C')
        self.cell(47.5, 8, f"{self.res_flexion['Status']}", 1, 1, 'C'); self.ln(10)
        self.set_font(self.font_family, 'B', 10)
        self.cell(0, 8, "Revisión por Cortante", 0, 1)
        self.cell(47.5, 8, "Solicitación (Vu)", 1, 0, 'C'); self.cell(47.5, 8, "Resistencia (phi*Vn)", 1, 0, 'C')
        self.cell(47.5, 8, "Ratio (Vu/phi*Vn)", 1, 0, 'C'); self.cell(47.5, 8, "Estatus", 1, 1, 'C')
        self.set_font(self.font_family, '', 10)
        self.cell(47.5, 8, f"{self.res_cortante['Vu']:.2f} {unidades['fuerza']}", 1, 0, 'C')
        self.cell(47.5, 8, f"{self.res_cortante['phi_Vn']:.2f} {unidades['fuerza']}", 1, 0, 'C')
        self.cell(47.5, 8, f"{self.res_cortante['Ratio']:.3f}", 1, 0, 'C')
        self.cell(47.5, 8, f"{self.res_cortante['Status']}", 1, 1, 'C'); self.ln(10)

    def escribir_requisitos_arriostramiento(self):
        """Escribe la Sección 6: Requisitos de Arriostramiento."""
        self.titulo_seccion('6. Requisitos de Arriostramiento')
        unidades = self.config.unidades
        self.set_font(self.font_family, 'B', 10)
        self.cell(0, 8, "Arriostramiento Lateral (en el patín)", 0, 1)
        self.set_font(self.font_family, 'B', 11)
        self.cell(80, 8, "  - Resistencia Requerida (Vbr):")
        self.set_font(self.font_family, '', 11)
        self.cell(0, 8, f"{self.res_arr_lateral.resistencia:.4f} {unidades['fuerza']}", ln=1)
        self.set_font(self.font_family, 'B', 11)
        self.cell(80, 8, "  - Rigidez Requerida (betabr):")
        self.set_font(self.font_family, '', 11)
        self.cell(0, 8, f"{self.res_arr_lateral.rigidez:.4f} {unidades['rigidez_fuerza']}", ln=1); self.ln(5)
        self.set_font(self.font_family, 'B', 10)
        self.cell(0, 8, "Arriostramiento Torsional (en la sección transversal)", 0, 1)
        self.set_font(self.font_family, 'B', 11)
        self.cell(80, 8, "  - Resistencia Requerida (Mbr):")
        self.set_font(self.font_family, '', 11)
        self.cell(0, 8, f"{self.res_arr_torsional.resistencia_momento:.4f} {unidades['momento']}", ln=1)
        self.set_font(self.font_family, 'B', 11)
        self.cell(80, 8, "  - Rigidez Requerida (betaT):")
        self.set_font(self.font_family, 'I', 11)
        self.cell(0, 8, f"Cálculo complejo no implementado en esta versión.", ln=1); self.ln(10)

    def generar(self, nombre_archivo: str):
        """
        Ensambla todas las secciones en el documento PDF y lo guarda en el disco.
        """
        self.escribir_datos_generales()
        self.escribir_propiedades_elemento()
        self.escribir_cargas_aplicadas()
        self.escribir_resultados_analisis()
        self.escribir_verificacion_resistencia()
        self.escribir_requisitos_arriostramiento()
        
        # Nos aseguramos de que la carpeta de salida exista.
        directorio_salida = 'reporting/output'
        if not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)
            
        # Guardamos el PDF en la ruta correcta.
        ruta_salida = os.path.join(directorio_salida, nombre_archivo)
        self.output(ruta_salida, 'F')