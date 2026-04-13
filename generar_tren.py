#!/usr/bin/env python3
"""
GENERADOR TREN SIMPLE - Genera un documento LaTeX para un tren personalizado

Uso simple:
    from generar_tren_simple import generar_documento_tren
    
    entrada = {
        "nombre_tren": "Mi Tren Personalizado",
        "caudal_total_lps": 17.0,
        "num_lineas": 3,
        "afluente": {
            "DBO5_mg_L": 250.0,
            "DQO_mg_L": 500.0,
            "SST_mg_L": 220.0,
            "CF_NMP_100mL": 1.0e7,
            "temperatura_C": 24.0,
        },
        "unidades": [
            "rejillas",
            "desarenador",
            "uasb",
            "humedal_vertical",
            "cloro",
            "lecho_secado"
        ]
    }
    
    generar_documento_tren(entrada, output_dir="resultados/mis_trenes")
"""

import os
import sys
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import ollama

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar dimensionadores
from ptar_dimensionamiento import (
    ConfigDiseno,
    dimensionar_rejillas,
    dimensionar_desarenador,
    dimensionar_uasb,
    dimensionar_filtro_percolador,
    dimensionar_humedal_vertical,
    dimensionar_sedimentador_sec,
    dimensionar_desinfeccion_cloro,
    dimensionar_lecho_secado,
    dimensionar_abr_rap,
    dimensionar_baf,
    dimensionar_biofiltro_carga_mecanizada_hidraulica,  # TAF - Biofiltro de carga mecanizada e hidráulica
)

# Importar generadores LaTeX
from latex_unidades.rejillas import GeneradorRejillas
from latex_unidades.desarenador import GeneradorDesarenador
from latex_unidades.uasb import GeneradorUASB
from latex_unidades.filtro_percolador import GeneradorFiltroPercolador
from latex_unidades.humedal_vertical import GeneradorHumedalVertical
from latex_unidades.sedimentador_secundario import GeneradorSedimentadorSecundario
from latex_unidades.cloro import GeneradorCloro
from latex_unidades.lecho_secado import GeneradorLechoSecado
from latex_unidades.abr_rap import GeneradorABR_RAP
from latex_unidades.baf import GeneradorBAF
from latex_unidades.taf import GeneradorBiofiltroCargaMecanizadaHidraulica

# Importar generador de layout
from ptar_layout_graficador import generar_layout
from latex_unidades.reporte_resultados import (
    generar_latex_seccion_layout,
    generar_resumen_resultados,
)
from generador_texto_ia import (
    generar_resumen_proyecto_ia,
    generar_conclusiones_resultados_ia,
)


# =============================================================================
# BIBLIOGRAFIA
# =============================================================================

def _generar_bibliografia(output_dir):
    """Genera el archivo .bib con las referencias bibliograficas"""
    bib_content = r'''%% Archivo de referencias bibliograficas
%% Generado automaticamente

@book{metcalf2014,
    author    = {Metcalf and Eddy, Inc.},
    title     = {Wastewater Engineering: Treatment and Resource Recovery},
    edition   = {5th},
    publisher = {McGraw-Hill Education},
    year      = {2014},
    address   = {New York, NY},
    isbn      = {978-0073401188}
}

@techreport{ops2005,
    author      = {{OPS/CEPIS}},
    title       = {Guia para el diseno de plantas de tratamiento de aguas residuales},
    institution = {Organizacion Panamericana de la Salud / Centro Panamericano de Ingenieria Sanitaria y Ciencias del Ambiente},
    year        = {2005},
    address     = {Lima, Peru},
    type        = {Guia Tecnica}
}

@techreport{senagua2012,
    author      = {{SENAGUA}},
    title       = {Normativa para el diseno de sistemas de tratamiento de aguas residuales},
    institution = {Secretaria Nacional del Agua del Ecuador},
    year        = {2012},
    address     = {Quito, Ecuador},
    type        = {Norma Tecnica}
}

@book{vanhaandel1994,
    author    = {Van Haandel, A. C. and Lettinga, G.},
    title     = {Anaerobic Sewage Treatment: A Practical Guide for Regions with a Hot Climate},
    publisher = {John Wiley & Sons},
    year      = {1994},
    address   = {Chichester, UK},
    isbn      = {978-0471951055}
}

@book{sperling2007,
    author    = {von Sperling, M.},
    title     = {Activated Sludge and Aerobic Biofilm Reactors},
    series    = {Biological Wastewater Treatment Series},
    volume    = {5},
    publisher = {IWA Publishing},
    year      = {2007},
    address   = {London, UK},
    isbn      = {978-1843391651}
}

@book{chernicharo2007,
    author    = {Chernicharo, C. A. L.},
    title     = {Biological Wastewater Treatment in Warm Climate Regions},
    volume    = {2},
    publisher = {IWA Publishing},
    year      = {2007},
    address   = {London, UK},
    isbn      = {978-1843391613}
}

@book{wef_mop8_2010,
    author    = {{Water Environment Federation}},
    title     = {Design of Municipal Wastewater Treatment Plants},
    edition   = {5th},
    series    = {Manual of Practice No. 8},
    publisher = {McGraw-Hill Education},
    year      = {2010},
    address   = {New York, NY},
    isbn      = {978-0071663601}
}

@techreport{usepa2003,
    author      = {{U.S. Environmental Protection Agency}},
    title       = {Manual de Disinfeccion de Aguas Residuales},
    institution = {EPA},
    year        = {2003},
    address     = {Washington, DC},
    type        = {Manual Tecnico}
}
'''
    bib_path = os.path.join(output_dir, 'referencias.bib')
    with open(bib_path, 'w', encoding='utf-8') as f:
        f.write(bib_content)
    return bib_path


# =============================================================================
# CONFIGURACION DEL TREN
# =============================================================================

@dataclass
class ConfigTren:
    """Configuracion simple de un tren."""
    nombre: str
    caudal_lps: float
    num_lineas: int
    dbo: float
    dqo: float
    sst: float
    cf: float
    temperatura: float
    factor_maximo_horario: float
    unidades: List[str]
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ConfigTren":
        afluente = data.get("afluente", {})
        return cls(
            nombre=data.get("nombre_tren", "Tren sin nombre"),
            caudal_lps=data.get("caudal_total_lps", 10.0),
            num_lineas=data.get("num_lineas", 2),
            dbo=afluente.get("DBO5_mg_L", 250.0),
            dqo=afluente.get("DQO_mg_L", 500.0),
            sst=afluente.get("SST_mg_L", 220.0),
            cf=afluente.get("CF_NMP_100mL", 1.0e7),
            temperatura=afluente.get("temperatura_C", 24.0),
            factor_maximo_horario=data.get("factor_maximo_horario", 2.5),
            unidades=data.get("unidades", []),
        )


# =============================================================================
# MAPEO DE UNIDADES
# =============================================================================

DIMENSIONADORES = {
    "rejillas": dimensionar_rejillas,
    "desarenador": dimensionar_desarenador,
    "uasb": dimensionar_uasb,
    "filtro_percolador": dimensionar_filtro_percolador,
    "humedal_vertical": dimensionar_humedal_vertical,
    "sedimentador_sec": dimensionar_sedimentador_sec,
    "cloro": dimensionar_desinfeccion_cloro,
    "lecho_secado": dimensionar_lecho_secado,
    "abr_rap": dimensionar_abr_rap,
    "baf": dimensionar_baf,
    "taf": dimensionar_biofiltro_carga_mecanizada_hidraulica,
}

GENERADORES_LATEX = {
    "rejillas": GeneradorRejillas,
    "desarenador": GeneradorDesarenador,
    "uasb": GeneradorUASB,
    "filtro_percolador": GeneradorFiltroPercolador,
    "humedal_vertical": GeneradorHumedalVertical,
    "sedimentador_sec": GeneradorSedimentadorSecundario,
    "cloro": GeneradorCloro,
    "lecho_secado": GeneradorLechoSecado,
    "abr_rap": GeneradorABR_RAP,
    "baf": GeneradorBAF,
    "taf": GeneradorBiofiltroCargaMecanizadaHidraulica,
}

NOMBRES_UNIDADES = {
    "rejillas": "Canal de Desbaste con Rejillas",
    "desarenador": "Desarenador de Flujo Horizontal",
    "uasb": "Reactor Anaerobio de Flujo Ascendente con Manto de Lodos (UASB)",
    "filtro_percolador": "Filtro Percolador",
    "humedal_vertical": "Humedal Artificial de Flujo Vertical (HAFV)",
    "sedimentador_sec": "Sedimentador Secundario",
    "cloro": "Sistema de Desinfeccion con Hipoclorito de Sodio",
    "lecho_secado": "Lechos de Secado de Lodos",
    "abr_rap": "Reactor Anaerobio con Pantallas (ABR/RAP)",
    "baf": "Biofiltro Biológico Aireado (BAF)",
    "taf": "Biofiltro de Carga Mecanizada e Hidráulica",
}


# =============================================================================
# FUNCIONES PRINCIPALES
# =============================================================================

def crear_configuracion(cfg_tren: ConfigTren) -> ConfigDiseno:
    """Crea ConfigDiseno a partir de ConfigTren."""
    cfg = ConfigDiseno()
    cfg.Q_total_L_s = cfg_tren.caudal_lps
    cfg.Q_linea_L_s = cfg_tren.caudal_lps / cfg_tren.num_lineas
    cfg.num_lineas = cfg_tren.num_lineas
    cfg.DBO5_mg_L = cfg_tren.dbo
    cfg.DQO_mg_L = cfg_tren.dqo
    cfg.SST_mg_L = cfg_tren.sst
    cfg.CF_NMP = cfg_tren.cf
    cfg.T_agua_C = cfg_tren.temperatura
    cfg.factor_pico_Qmax = cfg_tren.factor_maximo_horario
    cfg.desarenador_factor_pico = cfg_tren.factor_maximo_horario
    
    # Recalcular valores derivados del caudal (que se calculan en __post_init__)
    # ya que al cambiar Q_linea_L_s despues de crear el objeto, estos no se actualizan
    cfg.Q_linea_m3_d = cfg.Q_linea_L_s * 86.4
    cfg.Q_total_m3_d = cfg.Q_total_L_s * 86.4
    cfg.Q_linea_m3_h = cfg.Q_linea_m3_d / 24.0
    cfg.Q_linea_m3_s = cfg.Q_linea_L_s / 1000.0
    
    return cfg


def actualizar_calidad_tren(calidad_actual: Dict[str, float], unidad: str, 
                           resultado: Dict[str, Any], cfg: ConfigDiseno) -> Dict[str, float]:
    """
    Actualiza la calidad del agua tras pasar por una unidad de tratamiento.
    
    Esta función encadena la calidad del agua entre unidades, manteniendo un registro
    actualizado de los parámetros de calidad a medida que el agua avanza por el tren.
    
    Parámetros:
        calidad_actual: Dict con calidad actual del agua (DBO5, DQO, SST, CF)
        unidad: Nombre de la unidad que acaba de procesar el agua
        resultado: Resultado del dimensionamiento de la unidad
        cfg: Configuración de diseño con parámetros de eficiencia
    
    Retorna:
        Dict actualizado con la nueva calidad del efluente
    """
    calidad_nueva = calidad_actual.copy()
    
    # REJILLAS: remoción mínima de SST (~5%) y CF (~5%)
    if unidad == "rejillas":
        eta_SST = 0.05
        eta_CF = 0.05
        calidad_nueva["SST_mg_L"] = calidad_actual["SST_mg_L"] * (1 - eta_SST)
        calidad_nueva["CF_NMP_100mL"] = calidad_actual["CF_NMP_100mL"] * (1 - eta_CF)
    
    # DESARENADOR: remoción de SST (~15%) y mínima de DBO/DQO/CF (~5%)
    elif unidad == "desarenador":
        eta_SST = 0.15
        eta_DBO = 0.05
        eta_CF = 0.05
        calidad_nueva["DBO5_mg_L"] = calidad_actual["DBO5_mg_L"] * (1 - eta_DBO)
        calidad_nueva["DQO_mg_L"] = calidad_actual["DQO_mg_L"] * (1 - eta_DBO)
        calidad_nueva["SST_mg_L"] = calidad_actual["SST_mg_L"] * (1 - eta_SST)
        calidad_nueva["CF_NMP_100mL"] = calidad_actual["CF_NMP_100mL"] * (1 - eta_CF)
    
    # UASB: remoción significativa de DBO (~70%), DQO (~65%), SST (~70%), CF (~30%)
    elif unidad == "uasb":
        eta_DBO = resultado.get("eta_DBO", cfg.uasb_eta_DBO)
        eta_DQO = resultado.get("eta_DQO", cfg.uasb_eta_DBO * 0.93)  # DQO típicamente ~93% de DBO
        eta_SST = eta_DBO  # Similar a DBO
        eta_CF = cfg.balance_eta_CF_uasb
        calidad_nueva["DBO5_mg_L"] = calidad_actual["DBO5_mg_L"] * (1 - eta_DBO)
        calidad_nueva["DQO_mg_L"] = calidad_actual["DQO_mg_L"] * (1 - eta_DQO)
        calidad_nueva["SST_mg_L"] = calidad_actual["SST_mg_L"] * (1 - eta_SST)
        calidad_nueva["CF_NMP_100mL"] = calidad_actual["CF_NMP_100mL"] * (1 - eta_CF)
    
    # FILTRO PERCOLADOR: remoción alta de DBO (~80%), DQO (~75%), SST (~60%), CF (~50%)
    elif unidad == "filtro_percolador":
        relacion = resultado.get("relacion_Se_S0_Germain", 0.20)
        eta_DBO = 1 - relacion
        eta_DQO = eta_DBO * cfg.balance_eta_DQO_fp_factor
        eta_SST = cfg.balance_eta_SST_fp
        eta_CF = cfg.balance_eta_CF_fp
        calidad_nueva["DBO5_mg_L"] = calidad_actual["DBO5_mg_L"] * (1 - eta_DBO)
        calidad_nueva["DQO_mg_L"] = calidad_actual["DQO_mg_L"] * (1 - eta_DQO)
        calidad_nueva["SST_mg_L"] = calidad_actual["SST_mg_L"] * (1 - eta_SST)
        calidad_nueva["CF_NMP_100mL"] = calidad_actual["CF_NMP_100mL"] * (1 - eta_CF)
    
    # HUMEDAL VERTICAL: remoción según modelo k-C*
    elif unidad == "humedal_vertical":
        DBO_salida = resultado.get("DBO_salida_mg_L", cfg.humedal_DBO_salida_mg_L)
        if calidad_actual["DBO5_mg_L"] > 0:
            eta_DBO = 1 - (DBO_salida / calidad_actual["DBO5_mg_L"])
        else:
            eta_DBO = 0
        eta_DQO = eta_DBO
        eta_SST = cfg.balance_eta_SST_humedal
        eta_CF = cfg.humedal_eta_CF
        calidad_nueva["DBO5_mg_L"] = DBO_salida
        calidad_nueva["DQO_mg_L"] = calidad_actual["DQO_mg_L"] * (1 - eta_DQO)
        calidad_nueva["SST_mg_L"] = calidad_actual["SST_mg_L"] * (1 - eta_SST)
        calidad_nueva["CF_NMP_100mL"] = calidad_actual["CF_NMP_100mL"] * (1 - eta_CF)
    
    # SEDIMENTADOR SECUNDARIO: remoción de SST (~80%), DBO/DQO (~30%), CF (~10%)
    elif unidad == "sedimentador_sec":
        eta_DBO = resultado.get("eta_DBO_sed", cfg.sed_eta_DBO)
        eta_DQO = eta_DBO
        eta_SST = cfg.balance_eta_SST_sed
        eta_CF = cfg.balance_eta_CF_sed
        calidad_nueva["DBO5_mg_L"] = calidad_actual["DBO5_mg_L"] * (1 - eta_DBO)
        calidad_nueva["DQO_mg_L"] = calidad_actual["DQO_mg_L"] * (1 - eta_DQO)
        calidad_nueva["SST_mg_L"] = calidad_actual["SST_mg_L"] * (1 - eta_SST)
        calidad_nueva["CF_NMP_100mL"] = calidad_actual["CF_NMP_100mL"] * (1 - eta_CF)
    
    # CLORO: solo remueve CF (>99.9%), no afecta DBO/DQO/SST
    elif unidad == "cloro":
        log_red = resultado.get("log_reduccion", 6.0)  # Default 6 log ~ 99.9999%
        eta_CF = 1 - (10 ** (-log_red))
        calidad_nueva["CF_NMP_100mL"] = calidad_actual["CF_NMP_100mL"] * (1 - eta_CF)
        if calidad_nueva["CF_NMP_100mL"] < 1:
            calidad_nueva["CF_NMP_100mL"] = 1.0  # Mínimo detectable
    
    # LECHO DE SECADO: unidad de lodos, no modifica calidad del agua
    # No hay cambios en calidad_nueva
    
    # ABR_RAP: Reactor Anaerobio con Pantallas (similar a UASB)
    # Remoción típica: DBO ~75%, DQO ~70%, SST ~75%, CF ~40%
    elif unidad == "abr_rap":
        eta_DBO = 0.75
        eta_DQO = 0.70
        eta_SST = 0.75
        eta_CF = 0.40
        calidad_nueva["DBO5_mg_L"] = calidad_actual["DBO5_mg_L"] * (1 - eta_DBO)
        calidad_nueva["DQO_mg_L"] = calidad_actual["DQO_mg_L"] * (1 - eta_DQO)
        calidad_nueva["SST_mg_L"] = calidad_actual["SST_mg_L"] * (1 - eta_SST)
        calidad_nueva["CF_NMP_100mL"] = calidad_actual["CF_NMP_100mL"] * (1 - eta_CF)
    
    # BAF: Biofiltro Biológico Aireado (proceso aerobio con alta eficiencia)
    # Remoción típica: DBO ~85%, DQO ~80%, SST ~80%, CF ~60%
    elif unidad == "baf":
        eta_DBO = 0.85
        eta_DQO = 0.80
        eta_SST = 0.80
        eta_CF = 0.60
        calidad_nueva["DBO5_mg_L"] = calidad_actual["DBO5_mg_L"] * (1 - eta_DBO)
        calidad_nueva["DQO_mg_L"] = calidad_actual["DQO_mg_L"] * (1 - eta_DQO)
        calidad_nueva["SST_mg_L"] = calidad_actual["SST_mg_L"] * (1 - eta_SST)
        calidad_nueva["CF_NMP_100mL"] = calidad_actual["CF_NMP_100mL"] * (1 - eta_CF)
    
    # TAF: Biofiltro de Carga Mecanizada e Hidráulica
    # Remoción típica: DBO ~80%, DQO ~75%, SST ~75%, CF ~50%
    elif unidad == "taf":
        eta_DBO = 0.80
        eta_DQO = 0.75
        eta_SST = 0.75
        eta_CF = 0.50
        calidad_nueva["DBO5_mg_L"] = calidad_actual["DBO5_mg_L"] * (1 - eta_DBO)
        calidad_nueva["DQO_mg_L"] = calidad_actual["DQO_mg_L"] * (1 - eta_DQO)
        calidad_nueva["SST_mg_L"] = calidad_actual["SST_mg_L"] * (1 - eta_SST)
        calidad_nueva["CF_NMP_100mL"] = calidad_actual["CF_NMP_100mL"] * (1 - eta_CF)
    
    return calidad_nueva


def dimensionar_tren(cfg_tren: ConfigTren) -> Dict[str, Any]:
    """Dimensiona todas las unidades del tren."""
    print(f"\nDimensionando tren: {cfg_tren.nombre}")
    print(f"Caudal: {cfg_tren.caudal_lps} L/s en {cfg_tren.num_lineas} lineas")
    
    cfg = crear_configuracion(cfg_tren)
    resultados = {}
    
    # Calidad inicial del afluente (entrada al tren)
    calidad_actual = {
        "DBO5_mg_L": cfg_tren.dbo,
        "DQO_mg_L": cfg_tren.dqo,
        "SST_mg_L": cfg_tren.sst,
        "CF_NMP_100mL": cfg_tren.cf,
    }
    
    # Guardar calidad inicial en resultados
    resultados["_calidad_afluente"] = calidad_actual.copy()
    
    # Acumulador de lodos para lecho de secado
    lodos_total_kg_SST_d = 0.0
    desglose_lodos = []  # Lista de diccionarios con origen y cantidad
    
    for unidad in cfg_tren.unidades:
        print(f"  - {unidad}...", end=" ")
        if unidad in DIMENSIONADORES:
            try:
                # Pasar calidad actual a las unidades que lo necesiten
                if unidad == "humedal_vertical":
                    resultado = DIMENSIONADORES[unidad](
                        cfg, 
                        DBO_entrada_mg_L=calidad_actual["DBO5_mg_L"]
                    )
                    print(f"[DBO entrada: {calidad_actual['DBO5_mg_L']:.1f} mg/L]", end=" ")
                elif unidad == "cloro":
                    resultado = DIMENSIONADORES[unidad](
                        cfg, 
                        CF_entrada_NMP=calidad_actual["CF_NMP_100mL"]
                    )
                    print(f"[CF entrada: {calidad_actual['CF_NMP_100mL']:.0f} NMP/100mL]", end=" ")
                # Para lecho de secado necesitamos los lodos acumulados
                elif unidad == "lecho_secado":
                    if lodos_total_kg_SST_d > 0:
                        resultado = DIMENSIONADORES[unidad](cfg, lodos_kg_SST_d=lodos_total_kg_SST_d)
                        # Actualizar el desglose con información real de las unidades
                        if desglose_lodos:
                            filas_desglose = []
                            for item in desglose_lodos:
                                filas_desglose.append({
                                    "origen": item["nombre"],
                                    "por_linea_kg_d": round(item["kg_SST_d"] / cfg.num_lineas, 2),
                                    "total_kg_d": round(item["kg_SST_d"], 2)
                                })
                            resultado["desglose_lodos"] = filas_desglose
                    else:
                        raise ValueError("No se han acumulado lodos de las unidades anteriores para dimensionar el lecho de secado")
                else:
                    resultado = DIMENSIONADORES[unidad](cfg)
                resultados[unidad] = resultado
                
                # Actualizar calidad del agua tras esta unidad
                calidad_anterior = calidad_actual.copy()
                calidad_actual = actualizar_calidad_tren(calidad_actual, unidad, resultado, cfg)
                # Guardar calidad de entrada y salida en el resultado de la unidad
                resultado["_calidad_entrada"] = calidad_anterior
                resultado["_calidad_salida"] = calidad_actual.copy()
                
                # Acumular lodos de cada unidad (excepto lecho de secado que los recibe)
                if unidad != "lecho_secado":
                    lodos_unidad = extraer_lodos_unidad(resultado, unidad)
                    if lodos_unidad > 0:
                        lodos_total_kg_SST_d += lodos_unidad
                        # Agregar al desglose
                        nombre_unidad = NOMBRES_UNIDADES.get(unidad, unidad)
                        desglose_lodos.append({
                            "unidad": unidad,
                            "nombre": nombre_unidad,
                            "kg_SST_d": lodos_unidad
                        })
                        print(f"OK (lodos: {lodos_unidad:.1f} kg SST/d)")
                    else:
                        print("OK")
                else:
                    print("OK")
            except Exception as e:
                print(f"ERROR: {e}")
                resultados[unidad] = {"error": str(e)}
        else:
            print("NO SOPORTADA")
            resultados[unidad] = {"error": "Unidad no soportada"}
    
    # Si hay lecho de secado en el tren, pasarle los lodos acumulados
    if "lecho_secado" in cfg_tren.unidades and lodos_total_kg_SST_d > 0:
        print(f"\n  Total lodos para lecho de secado: {lodos_total_kg_SST_d:.2f} kg SST/d")
        # Guardar para usar cuando se dimensione el lecho
        resultados["_lodos_acumulados_kg_SST_d"] = lodos_total_kg_SST_d
        # Guardar también el desglose por unidad
        resultados["_desglose_lodos"] = desglose_lodos
    
    # Guardar calidad final del efluente
    resultados["_calidad_efluente"] = calidad_actual.copy()
    
    # Mostrar resumen de calidad
    print(f"\n  Calidad del efluente final:")
    print(f"    DBO5: {calidad_actual['DBO5_mg_L']:.1f} mg/L")
    print(f"    DQO: {calidad_actual['DQO_mg_L']:.1f} mg/L")
    print(f"    SST: {calidad_actual['SST_mg_L']:.1f} mg/L")
    print(f"    CF: {calidad_actual['CF_NMP_100mL']:.0f} NMP/100mL")
    
    return resultados


def extraer_lodos_unidad(resultado: Dict, unidad: str) -> float:
    """
    Extrae la producción de lodos (kg SST/d) del resultado de una unidad.
    Busca recursivamente en todo el diccionario para encontrar valores de lodos.
    """
    lodos_kg_d = 0.0
    
    # Campos específicos conocidos por nombre
    campos_directos = [
        "lodos_kg_SST_d",
        "lodos_total_kg_d",
        "solidos_humus_kg_d",
        "solidos_biologicos_kg_d",
        "produccion_humus_kg_d",
        "lodos_kg_SSV_d",
    ]
    
    for campo in campos_directos:
        if campo in resultado and resultado[campo]:
            valor = resultado[campo]
            # Si es SSV, convertir a SST (asumir 80% SSV/SST típico)
            if "SSV" in campo:
                valor = valor / 0.80
            lodos_kg_d += valor
    
    # Si no encontramos directamente, buscar en estructura "lodos"
    if "lodos" in resultado and isinstance(resultado["lodos"], list):
        for item in resultado["lodos"]:
            if isinstance(item, dict):
                # Buscar kg_SST_d, kg_d, kg_SSV_d
                if "kg_SST_d" in item:
                    lodos_kg_d += item.get("kg_SST_d", 0)
                elif "kg_d" in item and "SSV" not in str(item):
                    lodos_kg_d += item.get("kg_d", 0)
                elif "kg_SSV_d" in item:
                    lodos_kg_d += item.get("kg_SSV_d", 0) / 0.80
    
    # Si aún no hay nada, hacer búsqueda recursiva en todo el dict
    if lodos_kg_d == 0:
        lodos_kg_d = _buscar_lodos_recursivo(resultado)
    
    return lodos_kg_d


def _buscar_lodos_recursivo(obj, profundidad_max=3, profundidad=0):
    """
    Búsqueda recursiva de valores de lodos en cualquier estructura de datos.
    Busca claves que contengan 'lodos', 'solidos', 'produccion' + 'kg'
    """
    if profundidad >= profundidad_max:
        return 0.0
    
    total = 0.0
    
    if isinstance(obj, dict):
        for clave, valor in obj.items():
            clave_lower = str(clave).lower()
            # Si la clave parece ser de lodos
            if any(x in clave_lower for x in ["lodos", "solidos", "produccion", "humus"]):
                if isinstance(valor, (int, float)) and valor > 0:
                    # Convertir SSV a SST si es necesario
                    if "ssv" in clave_lower:
                        total += valor / 0.80
                    else:
                        total += valor
                elif isinstance(valor, (dict, list)):
                    total += _buscar_lodos_recursivo(valor, profundidad_max, profundidad + 1)
            # También buscar dentro de sub-estructuras
            elif isinstance(valor, (dict, list)):
                total += _buscar_lodos_recursivo(valor, profundidad_max, profundidad + 1)
    
    elif isinstance(obj, list):
        for item in obj:
            total += _buscar_lodos_recursivo(item, profundidad_max, profundidad + 1)
    
    return total


def generar_latex_unidad(unidad: str, resultado: Dict, cfg: ConfigDiseno, figuras_dir: str) -> str:
    """Genera el LaTeX para una unidad, convirtiendo subsections internos a subsubsections."""
    if unidad not in GENERADORES_LATEX:
        return f"\\subsubsection{{{NOMBRES_UNIDADES.get(unidad, unidad)}}}\nUnidad no disponible en LaTeX.\n\n"
    
    try:
        generador_class = GENERADORES_LATEX[unidad]
        # Pasar ruta de figuras al generador
        generador = generador_class(cfg, resultado, ruta_figuras='figuras')
        contenido = generador.generar_completo()
        
        # Convertir \subsection a \subsubsection para que no aparezcan en el indice
        # Esto hace que Dimensionamiento, Verificacion, Resultados sean 1.1.1, 1.1.2, etc.
        contenido = contenido.replace(r'\subsection{', r'\subsubsection{')
        contenido = contenido.replace(r'\subsection*{', r'\subsubsection*{')
        
        return contenido
    except Exception as e:
        return f"\\subsubsection{{{NOMBRES_UNIDADES.get(unidad, unidad)}}}\nError: {e}\n\n"


def generar_documento_tren(
    entrada: Dict,
    output_dir: str = "resultados/trenes",
    nombre_archivo: Optional[str] = None,
    compilar_pdf: bool = False,
    usar_ia: bool = True
) -> str:
    """
    Genera un documento LaTeX completo para el tren.
    
    Args:
        entrada: Diccionario con configuracion del tren
        output_dir: Directorio de salida
        nombre_archivo: Nombre del archivo (sin extension)
        compilar_pdf: Si True, intenta compilar a PDF
        usar_ia: Si True, genera resumen y conclusiones con IA local
        
    Returns:
        Ruta al archivo .tex generado
    """
    # Crear configuracion
    cfg_tren = ConfigTren.from_dict(entrada)
    cfg = crear_configuracion(cfg_tren)
    
    # Dimensionar
    resultados = dimensionar_tren(cfg_tren)
    
    # Crear directorios: principal y figuras
    os.makedirs(output_dir, exist_ok=True)
    figuras_dir = os.path.join(output_dir, "figuras")
    os.makedirs(figuras_dir, exist_ok=True)
    
    # Generar nombre de archivo
    if nombre_archivo is None:
        nombre_archivo = cfg_tren.nombre.lower().replace(" ", "_").replace("+", "_")
    
    tex_path = os.path.join(output_dir, f"{nombre_archivo}.tex")
    
    # Generar documento LaTeX
    print(f"\nGenerando documento LaTeX: {tex_path}")
    
    # Encabezado
    latex_parts = []
    latex_parts.append(r"\documentclass[12pt,a4paper]{article}")
    latex_parts.append(r"\usepackage[utf8]{inputenc}")
    latex_parts.append(r"\usepackage[spanish]{babel}")
    latex_parts.append(r"\usepackage{geometry}")
    latex_parts.append(r"\usepackage{amsmath}")
    latex_parts.append(r"\usepackage{amssymb}")
    latex_parts.append(r"\usepackage{booktabs}")
    latex_parts.append(r"\usepackage{longtable}")
    latex_parts.append(r"\usepackage{graphicx}")
    latex_parts.append(r"\usepackage{enumitem}")
    latex_parts.append(r"\usepackage{float}")
    latex_parts.append(r"\usepackage{xcolor}")
    latex_parts.append(r"\usepackage{fancyhdr}")
    latex_parts.append(r"\usepackage{caption}")
    latex_parts.append(r"\usepackage[numbers]{natbib}")
    latex_parts.append(r"\usepackage[colorlinks=true,linkcolor=black,citecolor=blue,urlcolor=blue]{hyperref}")
    latex_parts.append("")
    latex_parts.append(r"\geometry{margin=2.5cm}")
    latex_parts.append("")
    latex_parts.append(r"\pagestyle{fancy}")
    latex_parts.append(r"\fancyhf{}")
    latex_parts.append(r"\fancyhead[L]{" + cfg_tren.nombre + r"}")
    latex_parts.append(r"\fancyhead[R]{\thepage}")
    latex_parts.append("")
    latex_parts.append(r"\setcounter{tocdepth}{2}")  # Indice hasta subsection
    latex_parts.append("")
    latex_parts.append(r"\begin{document}")
    latex_parts.append("")
    
    # Caratula profesional
    latex_parts.append(r"\begin{titlepage}")
    latex_parts.append(r"\centering")
    latex_parts.append(r"\vspace*{2cm}")
    latex_parts.append("")
    latex_parts.append(r"{\Huge\bfseries Memoria de Cálculo\par}")
    latex_parts.append(r"\vspace{1.5cm}")
    latex_parts.append("")
    latex_parts.append(r"{\Large\itshape Dimensionamiento de:\par}")
    latex_parts.append(r"\vspace{0.5cm}")
    latex_parts.append("")
    latex_parts.append(r"{\LARGE\bfseries " + cfg_tren.nombre + r"\par}")
    latex_parts.append(r"\vspace{2cm}")
    latex_parts.append("")
    latex_parts.append(r"{\large Caudal de diseño: " + f"{cfg_tren.caudal_lps}" + r" L/s\par}")
    latex_parts.append(r"{\large Número de líneas: " + f"{cfg_tren.num_lineas}" + r"\par}")
    latex_parts.append(r"\vfill")
    latex_parts.append(r"{\large\today\par}")
    latex_parts.append(r"\end{titlepage}")
    latex_parts.append("")
    
    # Indices (todos juntos en la misma pagina)
    latex_parts.append(r"\tableofcontents")
    latex_parts.append("")
    latex_parts.append(r"\listoffigures")
    latex_parts.append("")
    latex_parts.append(r"\listoftables")
    latex_parts.append("")
    
    # Resumen en nueva pagina
    latex_parts.append(r"\newpage")
    latex_parts.append(r"\section{Resumen del Proyecto}")
    latex_parts.append("")

    resumen_ia_generado = False
    if usar_ia:
        # Generar texto descriptivo con IA (qwen2.5:3b local)
        print("\nGenerando resumen del proyecto con IA (qwen2.5:3b)...")
        try:
            resumen_ia = generar_resumen_proyecto_ia(
                nombre_tren=cfg_tren.nombre,
                caudal_lps=cfg_tren.caudal_lps,
                num_lineas=cfg_tren.num_lineas,
                afluente={
                    "DBO5_mg_L": cfg_tren.dbo,
                    "DQO_mg_L": cfg_tren.dqo,
                    "SST_mg_L": cfg_tren.sst,
                    "CF_NMP_100mL": cfg_tren.cf,
                    "temperatura_C": cfg_tren.temperatura,
                },
                unidades=cfg_tren.unidades,
                nombres_unidades=NOMBRES_UNIDADES,
            )
            if resumen_ia.startswith("[ATENCION:") or resumen_ia.startswith("[Error"):
                print(f"  [ADVERTENCIA] {resumen_ia}")
                print("  El documento se generara sin el texto de IA en el resumen.")
            else:
                latex_parts.append(resumen_ia)
                latex_parts.append("")
                resumen_ia_generado = True
        except Exception as e:
            print(f"\n  [ADVERTENCIA] No se pudo generar el resumen con IA: {e}")
            print("  Asegurate de tener Ollama instalado y ejecutandose.")
            print("  Para instalar el modelo necesario, ejecuta: ollama pull qwen2.5:3b")
            print("  El documento se generara sin el texto de IA en el resumen.")

    if not resumen_ia_generado:
        # Fallback cuando no se usa IA o fallo la generacion
        latex_parts.append(f"Este documento presenta el dimensionamiento detallado del {cfg_tren.nombre}, disenado para tratar un caudal de {cfg_tren.caudal_lps} L/s distribuido en {cfg_tren.num_lineas} lineas paralelas ({cfg_tren.caudal_lps / cfg_tren.num_lineas:.2f} L/s por linea).")
        latex_parts.append("")
        latex_parts.append(r"\textbf{Caracteristicas del afluente:}")
        latex_parts.append(r"\begin{itemize}")
        latex_parts.append(f"    \\item DBO$_5$: {cfg_tren.dbo} mg/L")
        latex_parts.append(f"    \\item DQO: {cfg_tren.dqo} mg/L")
        latex_parts.append(f"    \\item SST: {cfg_tren.sst} mg/L")
        latex_parts.append(f"    \\item Coliformes fecales: {cfg_tren.cf:.0e} NMP/100mL")
        latex_parts.append(f"    \\item Temperatura: {cfg_tren.temperatura}°C")
        latex_parts.append(r"\end{itemize}")
        latex_parts.append("")
        latex_parts.append(r"\textbf{Secuencia de unidades del tren:} ")
        latex_parts.append(r" $\rightarrow$ ".join([NOMBRES_UNIDADES.get(u, u) for u in cfg_tren.unidades]))
        latex_parts.append("")
    
    # ============================================================
    # PASO 1: Generar figuras ANTES de generar el documento LaTeX
    # Esto asegura que las figuras existan cuando el LaTeX las referencie
    # ============================================================
    print(f"\nGenerando figuras en: {figuras_dir}")
    figuras_exitosas = {}
    for unidad in cfg_tren.unidades:
        if unidad in resultados and unidad in GENERADORES_LATEX:
            try:
                generador_class = GENERADORES_LATEX[unidad]
                generador = generador_class(cfg, resultados[unidad], ruta_figuras='figuras')
                # Intentar generar esquema si existe el método
                if hasattr(generador, 'generar_esquema_matplotlib'):
                    fig_path = generador.generar_esquema_matplotlib(figuras_dir)
                    if fig_path and os.path.exists(fig_path):
                        figuras_exitosas[unidad] = fig_path
                        print(f"  - Figura {unidad}: OK [{os.path.basename(fig_path)}]")
                    else:
                        print(f"  - Figura {unidad}: ERROR (no se generó archivo)")
                else:
                    print(f"  - Figura {unidad}: No tiene método de generación")
            except Exception as e:
                print(f"  - Figura {unidad}: ERROR [{e}]")
    
    # Si hay figuras faltantes críticas, advertir pero continuar
    figuras_faltantes = [u for u in cfg_tren.unidades if u in resultados and u not in figuras_exitosas 
                        and hasattr(GENERADORES_LATEX.get(u, None), 'generar_esquema_matplotlib')]
    if figuras_faltantes:
        print(f"\n  [ADVERTENCIA] Figuras no generadas: {figuras_faltantes}")
        print(f"  El documento LaTeX se generará pero puede tener referencias rotas.")
    
    # ============================================================
    # PASO 1.5: Generar layout general del tren
    # ============================================================
    print(f"\nGenerando layout general del tren...")
    try:
        # Filtrar unidades que tienen dimensiones de layout
        unidades_con_layout = [u for u in cfg_tren.unidades if u in resultados and u != 'lecho_secado']
        
        layout_info = generar_layout(
            tren_id=cfg_tren.nombre.replace(" ", "_").lower(),
            unidades=unidades_con_layout,
            resultados=resultados,
            output_dir=figuras_dir,
            num_lineas=cfg_tren.num_lineas,
            incluir_lecho_secado='lecho_secado' in cfg_tren.unidades,
            caudal_L_s=cfg_tren.caudal_lps / cfg_tren.num_lineas if cfg_tren.num_lineas > 0 else None,
            nombre_tren=cfg_tren.nombre
        )
        
        print(f"  Layout generado: {os.path.basename(layout_info['fig_path'])}")
        print(f"  Dimensiones: {layout_info['ancho_total_m']:.1f}m x {layout_info['largo_total_m']:.1f}m")
        print(f"  Área layout: {layout_info['area_layout_m2']:.0f} m²")
        
        # Guardar referencia para el documento LaTeX
        layout_tren_path = layout_info['fig_path']
        layout_caption = layout_info.get('caption', '')
        
    except Exception as e:
        print(f"  [ADVERTENCIA] No se pudo generar layout del tren: {e}")
        layout_tren_path = None
        layout_caption = ''
    
    # ============================================================
    # PASO 2: Generar documento LaTeX (ahora las figuras ya existen)
    # ============================================================
    print(f"\nGenerando documento LaTeX: {tex_path}")
    
    # Seccion de dimensionamiento (nueva pagina)
    latex_parts.append(r"\newpage")
    latex_parts.append(r"\section{Dimensionamiento de Unidades}")
    latex_parts.append("")
    
    # Generar cada unidad con titulo claro
    for i, unidad in enumerate(cfg_tren.unidades, 1):
        if unidad in resultados:
            # Agregar titulo de la unidad (sin "Unidad X:" para que quede como en el ejemplo)
            nombre_unidad = NOMBRES_UNIDADES.get(unidad, unidad)
            latex_parts.append(f"\\subsection{{{nombre_unidad}}}")
            latex_parts.append("")
            
            # Contenido LaTeX de la unidad (con ruta de figuras)
            latex_unidad = generar_latex_unidad(unidad, resultados[unidad], cfg, figuras_dir)
            latex_parts.append(latex_unidad)
            latex_parts.append("")
    
    # Seccion: Resultados (con layout y areas de predio)
    if layout_tren_path:
        latex_parts.append(r"\newpage")
        latex_parts.append(r"\section{Resultados}")
        latex_parts.append("")
        latex_parts.append(generar_latex_seccion_layout(cfg, layout_info, titulo_section=False))
        latex_parts.append("")
        latex_parts.append(generar_resumen_resultados(cfg, resultados, area_m2=layout_info.get('area_layout_m2', 0)))
        latex_parts.append("")

        # NOTA: Las conclusiones generadas por IA se omiten temporalmente
        # hasta obtener una calidad de redaccion aceptable.
    
    # Bibliografia
    latex_parts.append("")
    latex_parts.append(r"\newpage")
    # latex_parts.append(r"\section{Referencias Bibliograficas}")
    latex_parts.append(r"\bibliographystyle{plain}")
    latex_parts.append(r"\bibliography{referencias}")
    latex_parts.append("")
    
    # Anexo TULSMA
    latex_parts.append("")
    latex_parts.append(r"\newpage")
    latex_parts.append(r"\appendix")
    latex_parts.append(r"\section{Anexo: TULSMA -- Criterios de Calidad del Recurso Agua}")
    latex_parts.append(r"\label{app:tulsma}")
    latex_parts.append("")
    latex_parts.append(r"\begin{center}")
    latex_parts.append(r"{\LARGE\bfseries TULSMA -- Norma de Calidad Ambiental\\[4pt]")
    latex_parts.append(r"del Recurso Agua}\\[8pt]")
    latex_parts.append(r"{\large Libro VI, Anexo 1 -- Acuerdo Ministerial 097-A (2015)\\")
    latex_parts.append(r"Decreto Ejecutivo 3516 -- Ecuador}\\[4pt]")
    latex_parts.append(r"{\small Criterios de calidad por uso del agua y limites de descarga de efluentes}")
    latex_parts.append(r"\end{center}")
    latex_parts.append(r"\vspace{10pt}")
    latex_parts.append("")
    latex_parts.append(r"\subsection{Tabla 1 -- Consumo Humano y Uso Domestico (tratamiento convencional)}")
    latex_parts.append(r"\small")
    latex_parts.append(r"\begin{longtable}{p{4.5cm}p{2.0cm}p{2.0cm}p{3.5cm}}")
    latex_parts.append(r"\caption{Limites maximos permisibles para aguas de consumo humano y uso domestico que unicamente requieren tratamiento convencional (TULSMA, Tabla~1).}\\")
    latex_parts.append(r"\toprule")
    latex_parts.append(r"\textbf{Parametro} & \textbf{Expresado como} & \textbf{Unidad} & \textbf{Limite maximo permisible} \\")
    latex_parts.append(r"\midrule")
    latex_parts.append(r"\endfirsthead")
    latex_parts.append(r"\multicolumn{4}{c}{\small\itshape Continuacion de la Tabla}\\")
    latex_parts.append(r"\toprule")
    latex_parts.append(r"\textbf{Parametro} & \textbf{Expresado como} & \textbf{Unidad} & \textbf{Limite maximo permisible} \\")
    latex_parts.append(r"\midrule")
    latex_parts.append(r"\endhead")
    latex_parts.append(r"\bottomrule")
    latex_parts.append(r"\endlastfoot")
    latex_parts.append(r"Aceites y Grasas & Sust.\ solubles en hexano & mg/L & $\leq$ 0,3 \\")
    latex_parts.append(r"Aluminio & Al & mg/L & $\leq$ 0,2 \\")
    latex_parts.append(r"Amoniaco & N-Amoniacal & mg/L & $\leq$ 1,0 \\")
    latex_parts.append(r"Amonio & NH$_4$ & mg/L & $\leq$ 0,05 \\")
    latex_parts.append(r"Arsenico (total) & As & mg/L & $\leq$ 0,05 \\")
    latex_parts.append(r"Bario & Ba & mg/L & $\leq$ 1,0 \\")
    latex_parts.append(r"Cadmio & Cd & mg/L & $\leq$ 0,01 \\")
    latex_parts.append(r"Cianuro total & CN$^-$ & mg/L & $\leq$ 0,1 \\")
    latex_parts.append(r"Cloruros & Cl$^-$ & mg/L & $\leq$ 250 \\")
    latex_parts.append(r"Cobre & Cu & mg/L & $\leq$ 1,0 \\")
    latex_parts.append(r"\textbf{Coliformes totales} & NMP & NMP/100 mL & $\leq$ 3\,000 \\")
    latex_parts.append(r"\textbf{Coliformes fecales} & NMP & NMP/100 mL & $\leq$ 600 \\")
    latex_parts.append(r"Color real & UC & Unidades de color & $\leq$ 100 \\")
    latex_parts.append(r"Compuestos fenolicos & Fenol & mg/L & $\leq$ 0,002 \\")
    latex_parts.append(r"Cromo hexavalente & Cr$^{6+}$ & mg/L & $\leq$ 0,05 \\")
    latex_parts.append(r"\textbf{DBO$_5$} & -- & mg/L & $\leq$ 2,0 \\")
    latex_parts.append(r"Dureza & CaCO$_3$ & mg/L & $\leq$ 500 \\")
    latex_parts.append(r"Fluoruro total & F & mg/L & $\leq$ 1,5 \\")
    latex_parts.append(r"Hierro total & Fe & mg/L & $\leq$ 1,0 \\")
    latex_parts.append(r"Manganeso total & Mn & mg/L & $\leq$ 0,1 \\")
    latex_parts.append(r"Materia flotante & -- & -- & Ausencia \\")
    latex_parts.append(r"Mercurio total & Hg & mg/L & $\leq$ 0,001 \\")
    latex_parts.append(r"Nitrato & N-Nitrato & mg/L & $\leq$ 10,0 \\")
    latex_parts.append(r"Nitrito & N-Nitrito & mg/L & $\leq$ 1,0 \\")
    latex_parts.append(r"Oxigeno disuelto & O.D. & mg/L & $\geq$ 80\% saturacion; $\geq$ 6 mg/L \\")
    latex_parts.append(r"pH & -- & -- & $6,0 - 9,0$ \\")
    latex_parts.append(r"Plata total & Ag & mg/L & $\leq$ 0,05 \\")
    latex_parts.append(r"Plomo total & Pb & mg/L & $\leq$ 0,05 \\")
    latex_parts.append(r"Selenio total & Se & mg/L & $\leq$ 0,01 \\")
    latex_parts.append(r"Sodio & Na & mg/L & $\leq$ 200 \\")
    latex_parts.append(r"Solidos disueltos totales & -- & mg/L & $\leq$ 1\,000 \\")
    latex_parts.append(r"Sulfatos & SO$_4^{2-}$ & mg/L & $\leq$ 400 \\")
    latex_parts.append(r"Temperatura & -- & $^\circ$C & Cond.\ natural $\pm$ 3\,$^\circ$C \\")
    latex_parts.append(r"Tensoactivos & SAAM & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"Turbiedad & -- & UTN & $\leq$ 100 \\")
    latex_parts.append(r"Zinc & Zn & mg/L & $\leq$ 5,0 \\")
    latex_parts.append(r"\end{longtable}")
    latex_parts.append("")
    latex_parts.append(r"\subsection{Tabla 12 -- Descarga a Cuerpo de Agua Dulce}")
    latex_parts.append(r"{\small\textbf{Nota:} Esta es la tabla aplicable al proyecto de tratamiento de aguas residuales municipales cuando el efluente se vierte a un rio, lago o cuerpo superficial de agua dulce.}")
    latex_parts.append(r"\vspace{6pt}")
    latex_parts.append(r"\small")
    latex_parts.append(r"\begin{longtable}{p{4.5cm}p{2.0cm}p{2.0cm}p{3.5cm}}")
    latex_parts.append(r"\caption{Limites maximos permisibles de descarga a un cuerpo de agua dulce (TULSMA, Tabla~12).}\\")
    latex_parts.append(r"\toprule")
    latex_parts.append(r"\textbf{Parametro} & \textbf{Expresado como} & \textbf{Unidad} & \textbf{Limite maximo permisible} \\")
    latex_parts.append(r"\midrule")
    latex_parts.append(r"\endfirsthead")
    latex_parts.append(r"\multicolumn{4}{c}{\small\itshape Continuacion de la Tabla}\\")
    latex_parts.append(r"\toprule")
    latex_parts.append(r"\textbf{Parametro} & \textbf{Expresado como} & \textbf{Unidad} & \textbf{Limite maximo permisible} \\")
    latex_parts.append(r"\midrule")
    latex_parts.append(r"\endhead")
    latex_parts.append(r"\bottomrule")
    latex_parts.append(r"\endlastfoot")
    latex_parts.append(r"Aceites y grasas & Sust.\ solubles en hexano & mg/L & $\leq$ 0,3 \\")
    latex_parts.append(r"Aluminio & Al & mg/L & $\leq$ 5,0 \\")
    latex_parts.append(r"Arsenico total & As & mg/L & $\leq$ 0,1 \\")
    latex_parts.append(r"Bario & Ba & mg/L & $\leq$ 2,0 \\")
    latex_parts.append(r"Cadmio & Cd & mg/L & $\leq$ 0,02 \\")
    latex_parts.append(r"Cianuro total & CN$^-$ & mg/L & $\leq$ 0,1 \\")
    latex_parts.append(r"Cloruros & Cl$^-$ & mg/L & $\leq$ 1\,000 \\")
    latex_parts.append(r"Cobre & Cu & mg/L & $\leq$ 1,0 \\")
    latex_parts.append(r"\textbf{Coliformes fecales}$^\dagger$ & NMP & NMP/100 mL & $\leq$ 3\,000 \\")
    latex_parts.append(r"Compuestos fenolicos & Fenol & mg/L & $\leq$ 0,2 \\")
    latex_parts.append(r"Cromo hexavalente & Cr$^{6+}$ & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"\textbf{DBO$_5$} & -- & mg/L & $\leq$ 100 \\")
    latex_parts.append(r"\textbf{DQO} & -- & mg/L & $\leq$ 250 \\")
    latex_parts.append(r"Fluoruros & F$^-$ & mg/L & $\leq$ 5,0 \\")
    latex_parts.append(r"Fosforo total & P & mg/L & $\leq$ 10,0 \\")
    latex_parts.append(r"Hierro total & Fe & mg/L & $\leq$ 10,0 \\")
    latex_parts.append(r"Manganeso total & Mn & mg/L & $\leq$ 2,0 \\")
    latex_parts.append(r"Materia flotante & -- & -- & Ausencia \\")
    latex_parts.append(r"Mercurio total & Hg & mg/L & $\leq$ 0,005 \\")
    latex_parts.append(r"Niquel & Ni & mg/L & $\leq$ 2,0 \\")
    latex_parts.append(r"Nitrogeno amoniacal & N-NH$_3$ & mg/L & $\leq$ 30,0 \\")
    latex_parts.append(r"Nitrogeno total Kjeldahl & N-TKN & mg/L & $\leq$ 50,0 \\")
    latex_parts.append(r"pH & -- & -- & $6,0 - 9,0$ \\")
    latex_parts.append(r"Plata total & Ag & mg/L & $\leq$ 0,1 \\")
    latex_parts.append(r"Plomo total & Pb & mg/L & $\leq$ 0,2 \\")
    latex_parts.append(r"Selenio & Se & mg/L & $\leq$ 0,1 \\")
    latex_parts.append(r"\textbf{Solidos sedimentables} & -- & mL/L & $\leq$ 1,0 \\")
    latex_parts.append(r"\textbf{Solidos suspendidos totales} & -- & mg/L & $\leq$ 130 \\")
    latex_parts.append(r"Solidos totales & -- & mg/L & $\leq$ 1\,600 \\")
    latex_parts.append(r"Sulfatos & SO$_4^{2-}$ & mg/L & $\leq$ 1\,000 \\")
    latex_parts.append(r"Sulfuros & S$^{2-}$ & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"Temperatura & -- & $^\circ$C & Cond.\ natural $\pm$ 3\,$^\circ$C; max.\ 32\,$^\circ$C \\")
    latex_parts.append(r"Tensoactivos & SAAM & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"Zinc & Zn & mg/L & $\leq$ 5,0 \\")
    latex_parts.append(r"\multicolumn{4}{l}{\scriptsize $^\dagger$ Aquellos con descargas $\leq$ 3\,000 NMP/100 mL quedan exentos de tratamiento de desinfeccion.}\\")
    latex_parts.append(r"\end{longtable}")
    latex_parts.append(r"\normalsize")
    latex_parts.append("")
    latex_parts.append(r"\subsection{Tabla 13 -- Descarga a Cuerpo de Agua Marina}")
    latex_parts.append(r"\small")
    latex_parts.append(r"\begin{longtable}{p{4.5cm}p{2.0cm}p{2.0cm}p{3.5cm}}")
    latex_parts.append(r"\caption{Limites maximos permisibles de descarga a un cuerpo de agua marina (TULSMA, Tabla~13).}\\")
    latex_parts.append(r"\toprule")
    latex_parts.append(r"\textbf{Parametro} & \textbf{Expresado como} & \textbf{Unidad} & \textbf{Limite maximo permisible} \\")
    latex_parts.append(r"\midrule")
    latex_parts.append(r"\endfirsthead")
    latex_parts.append(r"\multicolumn{4}{c}{\small\itshape Continuacion de la Tabla}\\")
    latex_parts.append(r"\toprule")
    latex_parts.append(r"\textbf{Parametro} & \textbf{Expresado como} & \textbf{Unidad} & \textbf{Limite maximo permisible} \\")
    latex_parts.append(r"\midrule")
    latex_parts.append(r"\endhead")
    latex_parts.append(r"\bottomrule")
    latex_parts.append(r"\endlastfoot")
    latex_parts.append(r"Aceites y grasas & Sust.\ solubles en hexano & mg/L & $\leq$ 0,3 \\")
    latex_parts.append(r"Aluminio & Al & mg/L & $\leq$ 5,0 \\")
    latex_parts.append(r"Arsenico total & As & mg/L & $\leq$ 0,1 \\")
    latex_parts.append(r"Cadmio & Cd & mg/L & $\leq$ 0,1 \\")
    latex_parts.append(r"Cianuro total & CN$^-$ & mg/L & $\leq$ 0,1 \\")
    latex_parts.append(r"Cobre & Cu & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"\textbf{Coliformes fecales}$^\ddagger$ & NMP & NMP/100 mL & $\leq$ 3\,000 \\")
    latex_parts.append(r"Compuestos fenolicos & Fenol & mg/L & $\leq$ 0,2 \\")
    latex_parts.append(r"Cromo hexavalente & Cr$^{6+}$ & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"\textbf{DBO$_5$} & -- & mg/L & $\leq$ 100 \\")
    latex_parts.append(r"\textbf{DQO} & -- & mg/L & $\leq$ 250 \\")
    latex_parts.append(r"Fluoruros & F$^-$ & mg/L & $\leq$ 5,0 \\")
    latex_parts.append(r"Hierro total & Fe & mg/L & $\leq$ 10,0 \\")
    latex_parts.append(r"Manganeso total & Mn & mg/L & $\leq$ 2,0 \\")
    latex_parts.append(r"Materia flotante & -- & -- & Ausencia \\")
    latex_parts.append(r"Mercurio total & Hg & mg/L & $\leq$ 0,005 \\")
    latex_parts.append(r"Niquel & Ni & mg/L & $\leq$ 2,0 \\")
    latex_parts.append(r"Nitrogeno amoniacal & N-NH$_3$ & mg/L & $\leq$ 30,0 \\")
    latex_parts.append(r"Nitrogeno total Kjeldahl & N-TKN & mg/L & $\leq$ 50,0 \\")
    latex_parts.append(r"pH & -- & -- & $6,0 - 9,0$ \\")
    latex_parts.append(r"Plomo total & Pb & mg/L & $\leq$ 0,2 \\")
    latex_parts.append(r"\textbf{Solidos suspendidos totales} & -- & mg/L & $\leq$ 100 \\")
    latex_parts.append(r"Temperatura & -- & $^\circ$C & Cond.\ natural $\pm$ 3\,$^\circ$C; max.\ 32\,$^\circ$C \\")
    latex_parts.append(r"Tensoactivos & SAAM & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"Zinc & Zn & mg/L & $\leq$ 5,0 \\")
    latex_parts.append(r"\multicolumn{4}{l}{\footnotesize $^\ddagger$ Aquellos con descargas $\leq$ 3\,000 NMP/100 mL quedan exentos de tratamiento de desinfeccion.}\\")
    latex_parts.append(r"\end{longtable}")
    latex_parts.append("")
    latex_parts.append(r"\subsection{Tabla 11 -- Descarga al Sistema de Alcantarillado Publico}")
    latex_parts.append(r"\small")
    latex_parts.append(r"\begin{longtable}{p{4.5cm}p{2.0cm}p{2.0cm}p{3.5cm}}")
    latex_parts.append(r"\caption{Limites maximos permisibles de descarga al sistema de alcantarillado publico (TULSMA, Tabla~11).}\\")
    latex_parts.append(r"\toprule")
    latex_parts.append(r"\textbf{Parametro} & \textbf{Expresado como} & \textbf{Unidad} & \textbf{Limite maximo permisible} \\")
    latex_parts.append(r"\midrule")
    latex_parts.append(r"\endfirsthead")
    latex_parts.append(r"\multicolumn{4}{c}{\small\itshape Continuacion de la Tabla}\\")
    latex_parts.append(r"\toprule")
    latex_parts.append(r"\textbf{Parametro} & \textbf{Expresado como} & \textbf{Unidad} & \textbf{Limite maximo permisible} \\")
    latex_parts.append(r"\midrule")
    latex_parts.append(r"\endhead")
    latex_parts.append(r"\bottomrule")
    latex_parts.append(r"\endlastfoot")
    latex_parts.append(r"Aceites y grasas & Sust.\ solubles en hexano & mg/L & $\leq$ 70,0 \\")
    latex_parts.append(r"Aluminio & Al & mg/L & $\leq$ 5,0 \\")
    latex_parts.append(r"Arsenico total & As & mg/L & $\leq$ 0,1 \\")
    latex_parts.append(r"Bario & Ba & mg/L & $\leq$ 2,0 \\")
    latex_parts.append(r"Cadmio & Cd & mg/L & $\leq$ 0,02 \\")
    latex_parts.append(r"Cianuro total & CN$^-$ & mg/L & $\leq$ 1,0 \\")
    latex_parts.append(r"Cloruros & Cl$^-$ & mg/L & $\leq$ 1\,000 \\")
    latex_parts.append(r"Cobre & Cu & mg/L & $\leq$ 1,0 \\")
    latex_parts.append(r"Coliformes fecales & NMP & NMP/100 mL & No especificado \\")
    latex_parts.append(r"Compuestos fenolicos & Fenol & mg/L & $\leq$ 0,2 \\")
    latex_parts.append(r"Cromo hexavalente & Cr$^{6+}$ & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"Cromo total & Cr & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"\textbf{DBO$_5$} & -- & mg/L & $\leq$ 250 \\")
    latex_parts.append(r"\textbf{DQO} & -- & mg/L & $\leq$ 500 \\")
    latex_parts.append(r"Fluoruros & F$^-$ & mg/L & $\leq$ 5,0 \\")
    latex_parts.append(r"Hierro total & Fe & mg/L & $\leq$ 25,0 \\")
    latex_parts.append(r"Manganeso total & Mn & mg/L & $\leq$ 10,0 \\")
    latex_parts.append(r"Materia flotante & -- & -- & Ausencia \\")
    latex_parts.append(r"Mercurio total & Hg & mg/L & $\leq$ 0,01 \\")
    latex_parts.append(r"Niquel & Ni & mg/L & $\leq$ 2,0 \\")
    latex_parts.append(r"Nitrogeno amoniacal & N-NH$_3$ & mg/L & $\leq$ 30,0 \\")
    latex_parts.append(r"pH & -- & -- & $6,0 - 9,0$ \\")
    latex_parts.append(r"Plata total & Ag & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"Plomo total & Pb & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"Selenio & Se & mg/L & $\leq$ 0,5 \\")
    latex_parts.append(r"\textbf{Solidos sedimentables} & -- & mL/L/h & $\leq$ 20 \\")
    latex_parts.append(r"\textbf{Solidos suspendidos totales} & -- & mg/L & $\leq$ 220 \\")
    latex_parts.append(r"Sulfatos & SO$_4^{2-}$ & mg/L & $\leq$ 1\,000 \\")
    latex_parts.append(r"Sulfuros & S$^{2-}$ & mg/L & $\leq$ 1,0 \\")
    latex_parts.append(r"Temperatura & -- & $^\circ$C & $\leq$ 40 \\")
    latex_parts.append(r"Tensoactivos & SAAM & mg/L & $\leq$ 2,0 \\")
    latex_parts.append(r"Zinc & Zn & mg/L & $\leq$ 5,0 \\")
    latex_parts.append(r"\end{longtable}")
    latex_parts.append("")

    # Cierre
    latex_parts.append(r"\end{document}")
    
    # Guardar
    documento = "\n".join(latex_parts)
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(documento)
    
    # Generar archivo de bibliografia
    _generar_bibliografia(output_dir)
    print(f"Bibliografia generada: {os.path.join(output_dir, 'referencias.bib')}")
    
    print(f"\nDocumento guardado: {tex_path}")
    print(f"Tamano: {len(documento)} caracteres")
    print(f"Figuras generadas: {len(figuras_exitosas)} de {len([u for u in cfg_tren.unidades if u in GENERADORES_LATEX])}")
    
    # Compilar PDF si se solicita
    if compilar_pdf:
        print("Compilando PDF...")
        try:
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            pdf_path = tex_path.replace('.tex', '.pdf')
            if os.path.exists(pdf_path):
                print(f"PDF generado: {pdf_path}")
        except Exception as e:
            print(f"Error compilando PDF: {e}")
    
    return tex_path


# =============================================================================
# MAIN - PRUEBA
# =============================================================================

if __name__ == "__main__":
    import subprocess
    
    print("=" * 60)
    print("GENERADOR TREN")
    print("=" * 60)
    
    # Ejemplo de uso
    entrada = {
        "nombre_tren": "Sistema de Tratamiento con Reactor de Flujo Ascendente y Humedal Vertical",
        "caudal_total_lps": 17.31,
        "num_lineas": 3,
        "afluente": {
            "DBO5_mg_L": 243.10,
            "DQO_mg_L": 498,
            "SST_mg_L": 156.,
            "CF_NMP_100mL": 3300,
            "temperatura_C": 25.6,
        },
        "factor_maximo_horario": 2.77,
        "unidades": [
            "rejillas",
            "desarenador",
            "uasb",
            "humedal_vertical",
            "cloro",
            "lecho_secado"
        ]
    }
    
    # -------------------------------------------------------------------------
    # CONFIGURACION RAPIDA: activar/desactivar generacion de texto con IA
    # -------------------------------------------------------------------------
    USAR_IA = True  # <-- Cambia a False para omitir los textos generados por IA
    # -------------------------------------------------------------------------

    print("\nGenerando documento con el tren de ejemplo...")
    tex_path = generar_documento_tren(
        entrada,
        output_dir="resultados/mis_trenes",
        nombre_archivo="tren_ejemplo",
        compilar_pdf=False,  # Se compila manualmente abajo para mostrar progreso
        usar_ia=USAR_IA
    )
    
    print(f"\nArchivo LaTeX generado: {tex_path}")
    
    # Compilar PDF (2 veces para indices)
    print("\n" + "=" * 60)
    print("[5] Compilando PDF (2 pasadas para indices)...")
    print("=" * 60)
    try:
        output_dir = "resultados/mis_trenes"
        tex_name = os.path.basename(tex_path)
        
        # Primera pasada
        print("  Primera pasada...")
        subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
            capture_output=True,
            timeout=60
        )
        
        # BibTeX para referencias
        print("  Ejecutando BibTeX...")
        subprocess.run(
            ['bibtex', tex_name.replace('.tex', '')],
            cwd=output_dir,
            capture_output=True,
            timeout=60
        )
        
        # Segunda pasada (para indices y refs)
        print("  Segunda pasada (indices)...")
        subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
            capture_output=True,
            timeout=60
        )
        
        # Tercera pasada (para resolver refs cruzadas)
        print("  Tercera pasada (referencias)...")
        subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
            capture_output=True,
            timeout=60
        )
        
        pdf_path = tex_path.replace('.tex', '.pdf')
        if os.path.exists(pdf_path):
            print(f"PDF generado: {pdf_path}")
        else:
            print("PDF no generado (posible error en compilacion)")
    except Exception as e:
        print(f"Error compilando PDF: {e}")
    
    print("\n" + "=" * 60)
    print("Generacion completada")
    print("=" * 60)
    print("=" * 60)
