# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 11:39:59 2025

@author: Ernesto Patiño A
"""

import math

def calcular_factor_cb_avanzado(**kwargs):
    """
    Calcula el factor de modificación de pandeo lateral-torsional (Cb) utilizando
    diferentes ecuaciones seleccionables, basado en el script original de MATLAB.

    Esta función sigue los lineamientos de la API de desarrollo, operando como
    una 'caja negra' y devolviendo un diccionario estructurado con los resultados.

    Args:
        **kwargs (dict): Un diccionario de argumentos de palabra clave que debe
                         contener 'metodo' y los parámetros requeridos por ese
                         método.

        'metodo' (str): El nombre de la ecuación a utilizar. Opciones:
            - 'aisc_f1_1': Ecuación estándar del AISC 360-22 (Eq. F1-1).
            - 'linea_recta': Para momentos lineales.
            - 'yura': Ecuación de Yura.
            - 'caso_a', 'caso_b', 'caso_c': Para casos de carga específicos.
            - 'conservador': Devuelve un valor de 1.0.

        Parámetros requeridos por método:
            - 'aisc_f1_1': mmax, ma, mb, mc
            - 'linea_recta': m1, m2, curvatura ('simple' o 'doble')
            - 'yura': m1, m0, mb
            - 'caso_a': m0, m1, mb
            - 'caso_b': m1, m0, mb
            - 'caso_c': m0, m1, mb

    Returns:
        dict: Un diccionario con los resultados del cálculo, incluyendo el valor de Cb,
              el estado de la operación, la ecuación utilizada y los datos de entrada.
    """
    metodo = kwargs.get('metodo', '').lower()
    
    # Extraer todos los posibles parámetros con valores por defecto
    mmax = kwargs.get('mmax')
    ma = kwargs.get('ma')
    mb = kwargs.get('mb')
    mc = kwargs.get('mc')
    m1 = kwargs.get('m1')
    m2 = kwargs.get('m2')
    m0 = kwargs.get('m0')
    curvatura = kwargs.get('curvatura', 'simple')
    
    # Inicializar el diccionario de respuesta estándar
    resultado = {
        "valor_calculado": None,
        "status": "Error",
        "metodo_utilizado": metodo,
        "mensaje": "",
        "datos_entrada": kwargs
    }

    try:
        cb = None
        if metodo == 'aisc_f1_1':
            # Esta es la ecuación del AISC 360-22, F1-1 (anteriormente llamada 'kirby' o 'wong' en el script original)
            resultado["referencia_norma"] = "AISC 360-22, Eq. F1-1"
            denominador = 2.5 * mmax + 3 * ma + 4 * mb + 3 * mc
            if denominador == 0:
                cb = 1.0
                resultado["mensaje"] = "Denominador cero. Se asumió momento constante."
            else:
                cb = (12.5 * mmax) / denominador
                # Limitación a 3.0 es una práctica común permitida por AISC
                if cb > 3.0:
                    cb = 3.0
                    resultado["mensaje"] = "Cálculo exitoso. El valor fue limitado a 3.0."
                else:
                    resultado["mensaje"] = "Cálculo exitoso."

        elif metodo == 'linea_recta':
            if m2 is None or m1 is None: raise ValueError("m1 y m2 son requeridos.")
            if m2 == 0: m2 = 1e-9 # Evitar división por cero
            ratio = m1 / m2
            if curvatura == "simple":
                cb = max(1.75 + 1.05 * ratio + 0.3 * (-ratio)**2, 2.3)
            else: # doble
                cb = max(1.75 + 1.05 * ratio + 0.3 * ratio**2, 2.3)
            resultado["mensaje"] = "Cálculo exitoso."

        elif metodo == 'yura':
            if m1 is None or m0 is None or mb is None: raise ValueError("m1, m0 y mb son requeridos.")
            mcl = mb
            if m0 == 0: m0 = 1e-9
            if (m0 + m1) == 0: m1 += 1e-9
            cb = 3 - (2/3) * (m1 / m0) - (8/3) * (mcl / (m0 + m1))
            resultado["mensaje"] = "Cálculo exitoso."

        elif metodo == 'caso_a':
            if m0 is None or m1 is None or mb is None: raise ValueError("m0, m1 y mb son requeridos.")
            mcl = mb
            if mcl == 0: mcl = 1e-9
            cb = 2 - (m0 + 0.6 * m1) / mcl
            resultado["mensaje"] = "Cálculo exitoso."

        elif metodo == 'caso_b':
            if m1 is None or m0 is None or mb is None: raise ValueError("m1, m0 y mb son requeridos.")
            mcl = mb
            denominador = (0.5 * m1 - mcl)
            if denominador == 0: denominador = 1e-9
            cb = (2 * m1 - 2 * mcl + 0.165 * m0) / denominador
            resultado["mensaje"] = "Cálculo exitoso."

        elif metodo == 'caso_c':
            if m0 is None or m1 is None or mb is None: raise ValueError("m0, m1 y mb son requeridos.")
            mcl = mb
            if mcl == 0: mcl = 1e-9
            if m0 == 0: m0 = 1e-9
            cb = 2 - ((m0 + m1) / mcl) * (0.165 + (1/3) * (m1 / m0))
            resultado["mensaje"] = "Cálculo exitoso."

        elif metodo == 'conservador':
            cb = 1.0
            resultado["mensaje"] = "Valor conservador Cb=1.0 asignado."
            
        else:
            raise ValueError(f"El método '{metodo}' no es reconocido.")

        resultado["valor_calculado"] = cb
        resultado["status"] = "Exitoso"

    except (TypeError, ValueError) as e:
        resultado["mensaje"] = f"Error de entrada de datos: {e}"
    except Exception as e:
        resultado["mensaje"] = f"Error inesperado durante el cálculo: {e}"

    return resultado

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    print("--- Método: AISC F1-1 (Carga Uniforme) ---")
    resultado_aisc = calcular_factor_cb_avanzado(metodo='aisc_f1_1', mmax=1.0, ma=0.875, mb=1.0, mc=0.875)
    print(resultado_aisc)

    print("\n" + "="*50 + "\n")

    print("--- Método: linea_recta (Curvatura simple) ---")
    resultado_lineal = calcular_factor_cb_avanzado(metodo='linea_recta', m1=50, m2=100, curvatura='simple')
    print(resultado_lineal)

    print("\n" + "="*50 + "\n")
    
    print("--- Método: yura ---")
    resultado_yura = calcular_factor_cb_avanzado(metodo='yura', m1=50, m0=100, mb=80)
    print(resultado_yura)
    
    print("\n" + "="*50 + "\n")

    print("--- Método: conservador ---")
    resultado_cons = calcular_factor_cb_avanzado(metodo='conservador')
    print(resultado_cons)
    
    print("\n" + "="*50 + "\n")
    
    print("--- Error: Método no reconocido ---")
    resultado_error = calcular_factor_cb_avanzado(metodo='metodo_invalido')
    print(resultado_error)