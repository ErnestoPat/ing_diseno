# Contenido de run.py

# --- Capa 1: Herramientas Base ---
from core.config import ProyectoConfig, NormativaAcciones, NormativaDisenoAcero, MetodoDiseno
from core.materials import MaterialAcero
from core.sections import PerfilAcero

# --- Capa 2: Modelo y Análisis ---
from analysis.model import Viga, TipoApoyo
from analysis.loads import CargaPuntual, CargaDistribuida, CasoCarga
from analysis.combinations import GestorCombinaciones
from analysis.solver import AnalizadorViga

# --- Capa 3: Diseño Específico de Material ---
from design.acero.beam_checker import VerificadorResistencia
from design.acero.bracing_checker import CalculadoraArriostramiento, ArriostramientoTipo, CurvaturaTipo

# --- Herramientas de Reporte ---
from reporting.pdf_generator import ReportePDF

def ejemplo_calculo_arriostramiento_columna(config, calc_arriostramiento):
    print("\n--- EJEMPLO ADICIONAL: CÁLCULO DE ARRIOSTRAMIENTO DE COLUMNA ---")
    carga_axial_requerida_Pr = 1500; distancia_entre_arriostramientos_Lbr = 4.0
    res_columna = calc_arriostramiento.arriostramiento_lateral_columna(
        Pr=carga_axial_requerida_Pr, Lbr=distancia_entre_arriostramientos_Lbr,
        tipo_arriostramiento=ArriostramientoTipo.PUNTUAL)
    print(f"Para una columna con Pr = {carga_axial_requerida_Pr} kN y Lbr = {distancia_entre_arriostramientos_Lbr} m:")
    print(f"  - Resistencia Requerida (Vbr): {res_columna.resistencia:.4f} {config.unidades['fuerza']}")
    print(f"  - Rigidez Requerida (βbr):     {res_columna.rigidez:.4f} {config.unidades['rigidez_fuerza']}")

def programa_principal():
    config = ProyectoConfig(
        nombre_proyecto="Conjunto Ecatepec", id_proyecto="2025_01", ubicacion="Toluca, México", cliente="PJEDOMEX",
        titulo="Revisión de Viga Secundaria y Arriostramiento", descripcion_elemento="Viga V-203, Eje 4, Nivel 3",
        ingeniero_responsable="Ing. E. Patiño", revisor="Ing. J. Doe",
        normativa_acciones=NormativaAcciones.NTC_ACCIONES_2023, normativa_diseno=NormativaDisenoAcero.AISC_360_22,
        metodo_diseno=MetodoDiseno.LRFD,
        unidades={'fuerza': 'kN', 'longitud': 'm', 'momento': 'kNm', 'esfuerzo': 'MPa', 'rigidez_fuerza': 'kN/m'})
    
    viga = Viga(longitud=8.0, tipo_apoyo=TipoApoyo.SIMPLE, config=config)
    material = MaterialAcero.ASTM_A992(config=config)
    perfil = PerfilAcero(nombre_perfil="W18X35", material=material, config=config)
    viga.asignar_perfil(perfil)

    viga.agregar_carga(CargaDistribuida(magnitud=5.0, pos_inicio=0, pos_fin=8.0, caso_carga=CasoCarga.D))
    viga.agregar_carga(CargaDistribuida(magnitud=12.0, pos_inicio=0, pos_fin=8.0, caso_carga=CasoCarga.L))
    viga.agregar_carga(CargaPuntual(magnitud=15.0, posicion=4.0, caso_carga=CasoCarga.D))

    gestor_comb = GestorCombinaciones(config)
    combinaciones = gestor_comb.obtener_combinaciones()
    analizador = AnalizadorViga(viga)
    resultados_envolvente = {"Mu": 0.0, "Vu": 0.0}
    for combo in combinaciones:
        resultado = analizador.analizar(combinacion=combo)
        resultados_envolvente['Mu'] = max(resultados_envolvente['Mu'], resultado['Mu_max'])
        resultados_envolvente['Vu'] = max(resultados_envolvente['Vu'], resultado['Vu_max'])
    Mu_diseno = resultados_envolvente['Mu']; Vu_diseno = resultados_envolvente['Vu']
    
    verificador = VerificadorResistencia(viga, Mu=Mu_diseno, Vu=Vu_diseno)
    res_flexion = verificador.revisar_flexion(); res_cortante = verificador.revisar_cortante()
    resultados_diseno = {"flexion": res_flexion, "cortante": res_cortante}

    print("\n--- FASE 3: CÁLCULO DE ARRIOSTRAMIENTO ---")
    distancia_entre_arriostramientos = 4.0
    calc_arriostramiento = CalculadoraArriostramiento(config=config)
    h0 = (perfil.d - perfil.tf) / 1000 
    res_arr_lateral = calc_arriostramiento.arriostramiento_lateral_viga(
        Mr=Mu_diseno, h0=h0, Lbr=distancia_entre_arriostramientos,
        tipo_arriostramiento=ArriostramientoTipo.PUNTUAL, tipo_curvatura=CurvaturaTipo.NORMAL)
    print("Arriostramiento Lateral para la viga:", f"  - Resistencia Requerida (Vbr): {res_arr_lateral.resistencia:.4f} {config.unidades['fuerza']}", f"  - Rigidez Requerida (βbr):     {res_arr_lateral.rigidez:.4f} {config.unidades['rigidez_fuerza']}", sep='\n')
    res_arr_torsional = calc_arriostramiento.arriostramiento_torsional_viga(Mr=Mu_diseno, Lbr=distancia_entre_arriostramientos)
    print("Arriostramiento Torsional para la viga:", f"  - Resistencia Requerida (Mbr): {res_arr_torsional.resistencia_momento:.4f} {config.unidades['momento']}", f"  - Rigidez Requerida (βT):      {res_arr_torsional.rigidez_torsional:.4f} (Cálculo no implementado)", sep='\n')
    res_arriostramiento_final = {"lateral": res_arr_lateral, "torsional": res_arr_torsional}
    ejemplo_calculo_arriostramiento_columna(config, calc_arriostramiento)

    print("\n--- GENERANDO REPORTE PDF FINAL ---")
    try:
        reporte = ReportePDF(config, viga, resultados_envolvente, resultados_diseno, res_arriostramiento_final)
        nombre_reporte = f"Memoria_Calculo_{config.descripcion_elemento.replace(' ', '_').replace(',', '')}.pdf"
        reporte.generar(nombre_reporte)
        print(f"¡Éxito! El reporte '{nombre_reporte}' ha sido guardado en la carpeta 'reporting/output'.")
    except Exception as e:
        print(f"Error al generar el PDF: {e}")

if __name__ == "__main__":
    print(">>> INICIANDO PROGRAMA DE CÁLCULO DE VIGAS DE ACERO <<<")
    print("-" * 60)
    programa_principal()
    print("-" * 60)
    print(">>> PROGRAMA FINALIZADO <<<")