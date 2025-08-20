# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 12:20:18 2025

@author: Ernesto Patiño A
"""

import pandas as pd
from typing import Dict, Any

class DatabaseAISC:
    """
    Gestiona el acceso a la base de datos de perfiles de acero de la AISC.

    Esta clase carga la base de datos desde un archivo Excel una sola vez para
    permitir consultas rápidas y eficientes de las propiedades de los perfiles.
    Funciona como una 'caja negra' para la obtención de datos geométricos.

    Attributes:
        db (pd.DataFrame): Un DataFrame de pandas que contiene la base de datos completa.
        ruta_archivo (str): La ruta al archivo Excel de la base de datos.
    """

    def __init__(self, ruta_archivo: str = "aisc-shapes-database-v15.0.xlsx"):
        """
        Inicializa la clase cargando la base de datos de perfiles.

        Args:
            ruta_archivo (str): La ruta al archivo Excel de la base de datos AISC.
                                Debe estar en formato .xlsx.
        
        Raises:
            FileNotFoundError: Si el archivo de la base de datos no se encuentra en la ruta especificada.
            Exception: Para otros errores relacionados con la lectura del archivo.
        """
        self.db = None
        self.ruta_archivo = ruta_archivo
        try:
            # Usamos 'engine='openpyxl'' para compatibilidad con .xlsx
            self.db = pd.read_excel(self.ruta_archivo, sheet_name="Database v15.0")
            print(f"Base de datos AISC cargada exitosamente desde '{self.ruta_archivo}'.")
        except FileNotFoundError:
            print(f"Error Crítico: No se encontró el archivo de la base de datos en '{self.ruta_archivo}'.")
            raise
        except Exception as e:
            print(f"Error Crítico: No se pudo leer el archivo Excel. Causa: {e}")
            raise

    def obtener_propiedades_perfil(self, nombre_perfil: str) -> Dict[str, Any]:
        """
        Busca un perfil por su nombre y devuelve sus propiedades en un diccionario estructurado.

        Args:
            nombre_perfil (str): El nombre del perfil según la nomenclatura de la AISC
                                 (ej. "W18X86", "C9X15").

        Returns:
            dict: Un diccionario con los resultados de la búsqueda, incluyendo el estado,
                  un mensaje y un sub-diccionario con las propiedades si se encuentra.
        """
        resultado = {
            "propiedades": None,
            "status": "Error",
            "mensaje": f"El perfil '{nombre_perfil}' no fue encontrado en la base de datos.",
            "datos_entrada": {
                "nombre_perfil": nombre_perfil
            }
        }

        try:
            # 'AISC_Manual_Label' es la columna con los nombres estándar de los perfiles
            fila_perfil = self.db.loc[self.db['AISC_Manual_Label'] == nombre_perfil]

            if not fila_perfil.empty:
                # Convierte la primera fila encontrada a un diccionario
                # y elimina los valores nulos (NaN) que pandas a veces introduce
                propiedades = fila_perfil.iloc[0].dropna().to_dict()
                
                resultado["propiedades"] = propiedades
                resultado["status"] = "Exitoso"
                resultado["mensaje"] = f"Propiedades para el perfil '{nombre_perfil}' obtenidas exitosamente."
            
        except KeyError:
            resultado["mensaje"] = "Error: La columna 'AISC_Manual_Label' no se encontró en el archivo Excel."
        except Exception as e:
            resultado["mensaje"] = f"Error inesperado durante la búsqueda: {e}"
            
        return resultado

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    try:
        # 1. Crear una instancia de la base de datos (esto carga el archivo)
        #    Asegúrate de que 'aisc-shapes-database-v15.0.xlsx' esté en la misma carpeta.
        base_de_datos = DatabaseAISC()

        print("\n" + "="*50 + "\n")

        # 2. Buscar un perfil que existe
        print("--- Buscando perfil 'W18X86' ---")
        respuesta_w18 = base_de_datos.obtener_propiedades_perfil("W18X86")
        
        if respuesta_w18["status"] == "Exitoso":
            # Imprimir algunas propiedades clave para verificar
            props = respuesta_w18["propiedades"]
            print(f"Status: {respuesta_w18['status']}")
            print(f"  - Peso (W): {props.get('W')} lb/ft")
            print(f"  - Módulo Plástico en X (Zx): {props.get('Zx')} in^3")
            print(f"  - Módulo Elástico en X (Sx): {props.get('Sx')} in^3")
            print(f"  - Inercia en X (Ix): {props.get('Ix')} in^4")
        else:
            print(respuesta_w18["mensaje"])
        
        print("\n" + "="*50 + "\n")

        # 3. Buscar un perfil que NO existe
        print("--- Buscando perfil 'W1X1' ---")
        respuesta_inexistente = base_de_datos.obtener_propiedades_perfil("W1X1")
        print(f"Status: {respuesta_inexistente['status']}")
        print(f"Mensaje: {respuesta_inexistente['mensaje']}")

    except FileNotFoundError:
        print("\nPor favor, asegúrate de que el archivo 'aisc-shapes-database-v15.0.xlsx' se encuentra en la misma carpeta que el script.")