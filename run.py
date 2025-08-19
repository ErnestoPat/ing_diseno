# main.py (VERSIÓN COMPLETA Y FINAL)

# Módulos del proyecto
from calculos.configuracion import ProyectoConfig, NormativaAcciones, NormativaDisenoAcero, MetodoDiseno
from calculos.viga import Viga, TipoApoyo
from calculos.material import MaterialAcero
from calculos.perfil import PerfilAcero
from calculos.cargas import CargaPuntual, CargaDistribuida, CasoCarga
from calculos.combinaciones import GestorCombinaciones
from calculos.analizador import AnalizadorViga
from calculos.verificador import VerificadorResistencia
from calculos.arriostramiento import CalculadoraArriostramiento, ArriostramientoTipo, CurvaturaTipo
from report_generator import ReportePDF

def ejemplo_calculo_arriostramiento_columna(config, calc_arriostramiento):
    """
    Función de ejemplo para demostrar el cálculo de arriostramiento de una columna.
    Esta función es independiente del cálculo principal de la viga.
    """
    print("\n--- EJEMPLO ADICIONAL: CÁLCULO DE ARRIOSTRAMIENTO DE COLUMNA ---")
    
    # Parámetros de ejemplo para una columna
    carga_axial_requerida_Pr = 1500  # kN
    distancia_entre_arriostramientos_Lbr = 4.0  # metros

    # Realizamos el cálculo para la columna
    res_columna = calc_arriostramiento.arriostramiento_lateral_columna(
        Pr=carga_axial_requerida_Pr,
        Lbr=distancia_entre_arriostramientos_Lbr,
        tipo_arriostramiento=ArriostramientoTipo.PUNTUAL
    )

    print(f"Para una columna con Pr = {carga_axial_requerida_Pr} kN y Lbr = {distancia_entre_arriostramientos_Lbr} m:")
    print(f"  - Resistencia Requerida (Vbr): {res_columna.resistencia:.4f} {config.unidades['fuerza']}")
    print(f"  - Rigidez Requerida (βbr):     {res_columna.rigidez:.4f} {config.unidades['rigidez_fuerza']}")

def programa_principal():
    """
    Función que orquesta todo el flujo de trabajo:
    Configuración -> Creación del Modelo -> Análisis -> Diseño -> Reporte.
    """
    # --------------------------------------------------------------------------
    # PASO 1: Configuración del Proyecto
    # --------------------------------------------------------------------------
    config = ProyectoConfig(
        nombre_proyecto="Conjunto Ecatepec", id_proyecto="2025_01",
        ubicacion="Toluca, México", cliente="PJEDOMEX",
        titulo="Revisión de Viga Secundaria y Arriostramiento",
        descripcion_elemento="Viga V-203, Eje 4, Nivel 3",
        ingeniero_responsable="Ing. E. Patiño", revisor="Ing. J. Doe",
        normativa_acciones=NormativaAcciones.NTC_ACCIONES_2023,
        normativa_diseno=NormativaDisenoAcero.AISC_360_22,
        metodo_diseno=MetodoDiseno.LRFD,
        # Asegúrate de incluir 'rigidez_fuerza' para la calculadora de arriostramiento
        unidades={'fuerza': 'kN', 'longitud': 'm', 'momento': 'kNm', 'esfuerzo': 'MPa', 'rigidez_fuerza': 'kN/m'}
    )
    
    # --------------------------------------------------------------------------
    # PASO 2: Creación del Modelo (Viga, Material y Perfil)
    # --------------------------------------------------------------------------
    viga = Viga(longitud=8.0, tipo_apoyo=TipoApoyo.SIMPLE, config=config)
    material = MaterialAcero.ASTM_A992(config=config)
    perfil = PerfilAcero(nombre_perfil="W18X35", material=material, config=config)
    viga.asignar_perfil(perfil)

    # --------------------------------------------------------------------------
    # PASO 3: Definición de Cargas
    # --------------------------------------------------------------------------
    viga.agregar_carga(CargaDistribuida(magnitud=5.0, pos_inicio=0, pos_fin=8.0, caso_carga=CasoCarga.D))
    viga.agregar_carga(CargaDistribuida(magnitud=12.0, pos_inicio=0, pos_fin=8.0, caso_carga=CasoCarga.L))
    viga.agregar_carga(CargaPuntual(magnitud=15.0, posicion=4.0, caso_carga=CasoCarga.D))

    # --------------------------------------------------------------------------
    # PASO 4: ANÁLISIS ESTRUCTURAL (Cálculo de Acciones: Mu, Vu)
    # --------------------------------------------------------------------------
    gestor_comb = GestorCombinaciones(config)
    combinaciones = gestor_comb.obtener_combinaciones()
    analizador = AnalizadorViga(viga)
    
    resultados_envolvente = {"Mu": 0.0, "Vu": 0.0}
    for combo in combinaciones:
        resultado = analizador.analizar(combinacion=combo)
        resultados_envolvente['Mu'] = max(resultados_envolvente['Mu'], resultado['Mu_max'])
        resultados_envolvente['Vu'] = max(resultados_envolvente['Vu'], resultado['Vu_max'])
    
    Mu_diseno = resultados_envolvente['Mu']
    Vu_diseno = resultados_envolvente['Vu']
    
    # --------------------------------------------------------------------------
    # PASO 5: DISEÑO (Verificación de Resistencia: φMn, φVn)
    # --------------------------------------------------------------------------
    verificador = VerificadorResistencia(viga, Mu=Mu_diseno, Vu=Vu_diseno)
    res_flexion = verificador.revisar_flexion()
    res_cortante = verificador.revisar_cortante()
    resultados_diseno = {"flexion": res_flexion, "cortante": res_cortante}

    # --------------------------------------------------------------------------
    # PASO 6: CÁLCULO DE ARRIOSTRAMIENTO
    # --------------------------------------------------------------------------
    print("\n--- FASE 3: CÁLCULO DE ARRIOSTRAMIENTO ---")
    distancia_entre_arriostramientos = 4.0
    calc_arriostramiento = CalculadoraArriostramiento(config=config)
    h0 = (perfil.d - perfil.tf) / 1000  # Convertir de mm (base de datos) a m
    
    # Cálculo Lateral para la viga
    res_arr_lateral = calc_arriostramiento.arriostramiento_lateral_viga(
        Mr=Mu_diseno, h0=h0, Lbr=distancia_entre_arriostramientos,
        tipo_arriostramiento=ArriostramientoTipo.PUNTUAL,
        tipo_curvatura=CurvaturaTipo.NORMAL
    )
    print("Arriostramiento Lateral para la viga:")
    print(f"  - Resistencia Requerida (Vbr): {res_arr_lateral.resistencia:.4f} {config.unidades['fuerza']}")
    print(f"  - Rigidez Requerida (βbr):     {res_arr_lateral.rigidez:.4f} {config.unidades['rigidez_fuerza']}")

    # Cálculo Torsional para la viga
    res_arr_torsional = calc_arriostramiento.arriostramiento_torsional_viga(
        Mr=Mu_diseno, Lbr=distancia_entre_arriostramientos
    )
    print("Arriostramiento Torsional para la viga:")
    print(f"  - Resistencia Requerida (Mbr): {res_arr_torsional.resistencia_momento:.4f} {config.unidades['momento']}")
    print(f"  - Rigidez Requerida (βT):      {res_arr_torsional.rigidez_torsional:.4f} (Cálculo no implementado)")

    # Empaquetamos los resultados de arriostramiento para el reporte
    res_arriostramiento_final = {"lateral": res_arr_lateral, "torsional": res_arr_torsional}
    
    # Llamada al ejemplo de columna para demostrar que la funcionalidad existe
    ejemplo_calculo_arriostramiento_columna(config, calc_arriostramiento)

    # --------------------------------------------------------------------------
    # PASO 7: GENERACIÓN DEL REPORTE PDF
    # --------------------------------------------------------------------------
    print("\n--- GENERANDO REPORTE PDF FINAL ---")
    try:
        # Pasamos todos los resultados al generador de reportes
        reporte = ReportePDF(config, viga, resultados_envolvente, resultados_diseno, res_arriostramiento_final)
        nombre_reporte = f"Memoria_Calculo_{config.descripcion_elemento.replace(' ', '_').replace(',', '')}.pdf"
        reporte.generar(nombre_reporte)
        print(f"¡Éxito! El reporte '{nombre_reporte}' ha sido guardado en la carpeta 'reportes/'.")
    except Exception as e:
        print(f"Error al generar el PDF: {e}")


# --- Punto de Entrada del Programa ---
if __name__ == "__main__":
    print(">>> INICIANDO PROGRAMA DE CÁLCULO DE VIGAS DE ACERO <<<")
    print("-" * 60)
    # Llamamos a la función principal que contiene todo el flujo
    programa_principal()
    print("-" * 60)
    print(">>> PROGRAMA FINALIZADO <<<")