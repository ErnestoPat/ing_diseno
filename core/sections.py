# calculos/perfil.py (NUEVA VERSIÓN CON PANDAS)
# -*- coding: utf-8 -*-
import os
import pandas as pd
from core.config import ProyectoConfig
from core.materials import MaterialAcero

# ==============================================================================
# MÓDULO 3 (Parte B): PROPIEDADES DE LA SECCIÓN (LEYENDO XLSX CON PANDAS)
# ==============================================================================

# --- Factores de Conversión (sin cambios) ---
IN_A_MM = 25.4
IN2_A_MM2 = IN_A_MM ** 2
IN3_A_MM3 = IN_A_MM ** 3
IN4_A_MM4 = IN_A_MM ** 4

def _cargar_base_de_datos_aisc_xlsx():
    """
    Carga la base de datos de perfiles AISC desde el archivo .xlsx usando Pandas.
    Crea dos diccionarios en memoria: uno en unidades imperiales y otro en SI.
    """
    db_imp = {}
    db_si = {}
    
    # Ruta al archivo .xlsx
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    ruta_base = os.path.dirname(ruta_script)
    # ¡IMPORTANTE! Asegúrate de que el nombre del archivo coincida con el tuyo.
    nombre_archivo = 'aisc-shapes-database-v15.0.xlsx'
    ruta_xlsx = os.path.join(ruta_base, 'database', nombre_archivo)

    try:
        # Usamos pandas para leer el archivo de Excel.
        # 'Database v15.0' es el nombre de la hoja dentro del archivo de Excel.
        df = pd.read_excel(ruta_xlsx, sheet_name='Database v15.0', engine='openpyxl')
        
        # Iteramos sobre cada fila del DataFrame de pandas
        for index, row in df.iterrows():
            if row['Type'] == 'W':
                label = row['AISC_Manual_Label']
                
                try:
                    props_imp = {
                        "A": float(row['A']), "d": float(row['d']), "bf": float(row['bf']),
                        "tf": float(row['tf']), "tw": float(row['tw']), "Ix": float(row['Ix']),
                        "Zx": float(row['Zx']), "Sx": float(row['Sx']), "ry": float(row['ry']),
                        "rts": float(row['rts'])
                    }
                    db_imp[label] = props_imp

                    props_si = {
                        "A": props_imp["A"] * IN2_A_MM2, "d": props_imp["d"] * IN_A_MM,
                        "bf": props_imp["bf"] * IN_A_MM, "tf": props_imp["tf"] * IN_A_MM,
                        "tw": props_imp["tw"] * IN_A_MM, "Ix": props_imp["Ix"] * IN4_A_MM4,
                        "Zx": props_imp["Zx"] * IN3_A_MM3, "Sx": props_imp["Sx"] * IN3_A_MM3,
                        "ry": props_imp["ry"] * IN_A_MM, "rts": props_imp["rts"] * IN_A_MM
                    }
                    db_si[label] = props_si
                except (ValueError, TypeError):
                    continue
                    
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo de Excel en: {ruta_xlsx}")
        raise SystemExit("El programa no puede continuar sin la base de datos de perfiles.")
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo de Excel: {e}")
        raise SystemExit("Verifica que la librería 'openpyxl' esté instalada (pip install openpyxl).")
        
    return db_imp, db_si

# --- Se cargan las bases de datos al iniciar el programa ---
_db_perfiles_imp, _db_perfiles_si = _cargar_base_de_datos_aisc_xlsx()


# La clase PerfilAcero no necesita ningún cambio en su lógica.
# Sigue funcionando igual, pero ahora se alimenta de una fuente de datos mucho más robusta.
class PerfilAcero:
    def __init__(self, nombre_perfil: str, material: MaterialAcero, config: ProyectoConfig):
        self.nombre = nombre_perfil
        self.material = material
        self.config = config
        self._cargar_propiedades_geometricas()

    def _cargar_propiedades_geometricas(self):
        unidad_long = self.config.unidades.get('longitud')
        db = _db_perfiles_si if unidad_long in ['m', 'mm'] else _db_perfiles_imp
        
        if self.nombre in db:
            propiedades = db[self.nombre]
            for key, value in propiedades.items():
                setattr(self, key, value)
        else:
            raise ValueError(
                f"El perfil '{self.nombre}' no se encuentra en la base de datos AISC cargada "
                f"o no es un perfil tipo 'W'."
            )

    def __repr__(self):
        return f"PerfilAcero(nombre='{self.nombre}', material='{self.material.nombre}')"