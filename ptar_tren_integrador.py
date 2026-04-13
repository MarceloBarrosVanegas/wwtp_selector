#!/usr/bin/env python3
"""
PTAR TREN INTEGRADOR - Integración de unidades en un tren de tratamiento

Toma la configuración de un tren, ejecuta el dimensionamiento de cada unidad,
y consolida los resultados en una estructura unificada.

Uso:
    from ptar_tren_config import TrenConfig, get_tren_piloto_humedal
    from ptar_tren_integrador import integrar_tren
    
    entrada = get_tren_piloto_humedal()
    config = TrenConfig.from_dict(entrada)
    
    resultado = integrar_tren(config)
    # resultado contendrá todas las unidades dimensionadas, balance de calidad,
    # lodos, consumos, etc.
"""

import sys
import os
from typing import Dict, Any, List, Optional
import copy

# Agregar directorio padre al path para importar módulos existentes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ptar_tren_config import TrenConfig, UNIDADES_SOPORTADAS, obtener_info_unidad
from ptar_dimensionamiento import (
    ConfigDiseno,
    dimensionar_rejillas,
    dimensionar_desarenador,
    dimensionar_uasb,
    dimensionar_abr_rap,
    dimensionar_filtro_percolador,
    dimensionar_biofiltro_carga_mecanizada_hidraulica,
    dimensionar_baf,
    dimensionar_humedal_vertical,
    dimensionar_sedimentador_sec,
    dimensionar_desinfeccion_cloro,
    dimensionar_uv,
    dimensionar_lecho_secado,
)

# =============================================================================
# MAPEO DE UNIDADES A FUNCIONES DE DIMENSIONAMIENTO
# =============================================================================

DIMENSIONADORES = {
    "rejillas": dimensionar_rejillas,
    "desarenador": dimensionar_desarenador,
    "uasb": dimensionar_uasb,
    "abr": dimensionar_abr_rap,
    "filtro_percolador": dimensionar_filtro_percolador,
    "taf": dimensionar_biofiltro_carga_mecanizada_hidraulica,
    "baf": dimensionar_baf,
    "humedal_vertical": dimensionar_humedal_vertical,
    "sedimentador_secundario": dimensionar_sedimentador_sec,
    "cloro": dimensionar_desinfeccion_cloro,
    "uv": dimensionar_uv,
    "lecho_secado": dimensionar_lecho_secado,
}


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def crear_config_diseno(config_tren: TrenConfig) -> ConfigDiseno:
    """
    Crea un objeto ConfigDiseno a partir de la configuración del tren.
    
    Args:
        config_tren: Configuración del tren
        
    Returns:
        ConfigDiseno configurado para el tren
    """
    cfg = ConfigDiseno()
    
    # Configurar caudales
    cfg.Q_total_L_s = config_tren.caudal_total_lps
    cfg.Q_linea_L_s = config_tren.caudal_por_linea_lps
    cfg.num_lineas = config_tren.num_lineas
    
    # Configurar calidad del afluente
    cfg.DBO5_mg_L = config_tren.afluente.DBO5_mg_L
    cfg.DQO_mg_L = config_tren.afluente.DQO_mg_L
    cfg.SST_mg_L = config_tren.afluente.SST_mg_L
    cfg.CF_NMP = config_tren.afluente.CF_NMP_100mL
    cfg.T_agua_C = config_tren.afluente.temperatura_C
    cfg.T_min_C = config_tren.afluente.temperatura_C - 3.0  # Estimación conservadora
    
    return cfg


def calcular_balance_calidad(
    unidades_resultados: Dict[str, Dict],
    config_tren: TrenConfig
) -> Dict[str, Any]:
    """
    Calcula el balance de calidad del agua a través del tren.
    
    Args:
        unidades_resultados: Resultados de cada unidad dimensionada
        config_tren: Configuración del tren
        
    Returns:
        Dict con balance de calidad y eficiencias
    """
    # Valores iniciales (afluente)
    calidad_actual = {
        "DBO5_mg_L": config_tren.afluente.DBO5_mg_L,
        "DQO_mg_L": config_tren.afluente.DQO_mg_L,
        "SST_mg_L": config_tren.afluente.SST_mg_L,
        "CF_NMP": config_tren.afluente.CF_NMP_100mL,
    }
    
    # Traza de calidad por unidad
    traza_calidad = {}
    
    # Eficiencias típicas por unidad (valores de referencia)
    # Estos son valores orientativos, cada unidad puede tener sus propios cálculos
    eficiencias_referencia = {
        "rejillas": {"DBO5": 0.0, "DQO": 0.0, "SST": 0.05, "CF": 0.0},
        "desarenador": {"DBO5": 0.0, "DQO": 0.0, "SST": 0.10, "CF": 0.0},
        "uasb": {"DBO5": 0.70, "DQO": 0.65, "SST": 0.60, "CF": 0.50},
        "abr": {"DBO5": 0.65, "DQO": 0.60, "SST": 0.55, "CF": 0.40},
        "filtro_percolador": {"DBO5": 0.75, "DQO": 0.70, "SST": 0.70, "CF": 0.60},
        "taf": {"DBO5": 0.75, "DQO": 0.70, "SST": 0.70, "CF": 0.60},
        "baf": {"DBO5": 0.85, "DQO": 0.80, "SST": 0.80, "CF": 0.70},
        "humedal_vertical": {"DBO5": 0.85, "DQO": 0.80, "SST": 0.85, "CF": 0.90},
        "sedimentador_secundario": {"DBO5": 0.15, "DQO": 0.15, "SST": 0.90, "CF": 0.10},
        "cloro": {"DBO5": 0.0, "DQO": 0.0, "SST": 0.0, "CF": 0.99},
        "uv": {"DBO5": 0.0, "DQO": 0.0, "SST": 0.0, "CF": 0.99},
        "lecho_secado": {"DBO5": 0.0, "DQO": 0.0, "SST": 0.0, "CF": 0.0},
    }
    
    for codigo_unidad in config_tren.unidades:
        if codigo_unidad not in unidades_resultados:
            continue
            
        resultado_unidad = unidades_resultados[codigo_unidad]
        eficiencia = eficiencias_referencia.get(codigo_unidad, {})
        
        # Calcular salida de esta unidad
        calidad_salida = {
            "DBO5_mg_L": calidad_actual["DBO5_mg_L"] * (1 - eficiencia.get("DBO5", 0)),
            "DQO_mg_L": calidad_actual["DQO_mg_L"] * (1 - eficiencia.get("DQO", 0)),
            "SST_mg_L": calidad_actual["SST_mg_L"] * (1 - eficiencia.get("SST", 0)),
            "CF_NMP": max(1, calidad_actual["CF_NMP"] * (1 - eficiencia.get("CF", 0))),
        }
        
        # Guardar traza
        traza_calidad[codigo_unidad] = {
            "entrada": copy.deepcopy(calidad_actual),
            "salida": copy.deepcopy(calidad_salida),
            "eficiencia": eficiencia,
        }
        
        # Actualizar calidad para siguiente unidad
        calidad_actual = calidad_salida
    
    # Calcular eficiencias globales
    eficiencias_globales = {
        "DBO5_pct": (1 - calidad_actual["DBO5_mg_L"] / config_tren.afluente.DBO5_mg_L) * 100,
        "DQO_pct": (1 - calidad_actual["DQO_mg_L"] / config_tren.afluente.DQO_mg_L) * 100,
        "SST_pct": (1 - calidad_actual["SST_mg_L"] / config_tren.afluente.SST_mg_L) * 100,
        "CF_pct": (1 - calidad_actual["CF_NMP"] / config_tren.afluente.CF_NMP_100mL) * 100,
    }
    
    return {
        "afluente": {
            "DBO5_mg_L": config_tren.afluente.DBO5_mg_L,
            "DQO_mg_L": config_tren.afluente.DQO_mg_L,
            "SST_mg_L": config_tren.afluente.SST_mg_L,
            "CF_NMP": config_tren.afluente.CF_NMP_100mL,
        },
        "efluente": calidad_actual,
        "eficiencias_globales": eficiencias_globales,
        "traza_por_unidad": traza_calidad,
        "cumplimiento_TULSMA": {
            "DBO5": calidad_actual["DBO5_mg_L"] <= 100.0,
            "SST": calidad_actual["SST_mg_L"] <= 100.0,
            "CF": calidad_actual["CF_NMP"] <= 3000.0,
        }
    }


def calcular_lodos(unidades_resultados: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Consolida la información de lodos de todas las unidades.
    
    Args:
        unidades_resultados: Resultados de cada unidad
        
    Returns:
        Dict con consolidación de lodos
    """
    lodos_por_unidad = {}
    produccion_total_kg_d = 0.0
    volumen_total_m3_d = 0.0
    
    for codigo, resultado in unidades_resultados.items():
        # Extraer información de lodos si existe
        lodos_unidad = {}
        
        # Buscar claves comunes de lodos en el resultado
        if "produccion_lodos_kg_d" in resultado:
            lodos_unidad["produccion_kg_d"] = resultado["produccion_lodos_kg_d"]
            produccion_total_kg_d += resultado["produccion_lodos_kg_d"]
        elif "P_x_kg_d" in resultado:
            lodos_unidad["produccion_kg_d"] = resultado["P_x_kg_d"]
            produccion_total_kg_d += resultado["P_x_kg_d"]
            
        if "volumen_lodos_m3_d" in resultado:
            lodos_unidad["volumen_m3_d"] = resultado["volumen_lodos_m3_d"]
            volumen_total_m3_d += resultado["volumen_lodos_m3_d"]
        elif "Q_lodos_m3_d" in resultado:
            lodos_unidad["volumen_m3_d"] = resultado["Q_lodos_m3_d"]
            volumen_total_m3_d += resultado["Q_lodos_m3_d"]
        
        if lodos_unidad:
            lodos_por_unidad[codigo] = lodos_unidad
    
    return {
        "lodos_por_unidad": lodos_por_unidad,
        "produccion_total_kg_d": produccion_total_kg_d,
        "volumen_total_m3_d": volumen_total_m3_d,
        "nota": "Estimación preliminar. Cálculo detallado de lodos pendiente."
    }


def calcular_consumos(unidades_resultados: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Consolida los consumos de energía y químicos del tren.
    
    Args:
        unidades_resultados: Resultados de cada unidad
        
    Returns:
        Dict con consumos consolidados
    """
    energia_total_kW = 0.0
    cloro_total_kg_d = 0.0
    
    for codigo, resultado in unidades_resultados.items():
        # Energía
        if "potencia_total_kW" in resultado:
            energia_total_kW += resultado["potencia_total_kW"]
        elif "potencia_bomba_W" in resultado:
            energia_total_kW += resultado["potencia_bomba_W"] / 1000.0
            
        # Cloro
        if "dosificacion_cloro_kg_d" in resultado:
            cloro_total_kg_d += resultado["dosificacion_cloro_kg_d"]
    
    return {
        "energia_total_kW": energia_total_kW,
        "energia_total_kWh_d": energia_total_kW * 24,
        "cloro_total_kg_d": cloro_total_kg_d,
        "nota": "Consumos estimados. Cálculos detallados en módulos individuales."
    }


# =============================================================================
# FUNCIÓN PRINCIPAL DE INTEGRACIÓN
# =============================================================================

def integrar_tren(config_tren: TrenConfig) -> Dict[str, Any]:
    """
    Integra todas las unidades de un tren y genera el resultado consolidado.
    
    Args:
        config_tren: Configuración del tren
        
    Returns:
        Dict con toda la información del tren integrado:
        {
            "entrada": {...},
            "tren": {...},
            "unidades": {...},
            "balance_calidad": {...},
            "lodos": {...},
            "consumos": {...},
        }
    """
    print(f"\n[Integrador] Procesando tren: {config_tren.nombre_tren}")
    
    # Crear configuración de diseño
    cfg = crear_config_diseno(config_tren)
    
    # Dimensionar cada unidad
    unidades_resultados = {}
    unidades_con_error = []
    
    for codigo_unidad in config_tren.unidades:
        print(f"  - Dimensionando: {codigo_unidad}...")
        
        if codigo_unidad not in DIMENSIONADORES:
            print(f"    ⚠️  No hay dimensionador para: {codigo_unidad}")
            unidades_con_error.append(codigo_unidad)
            continue
        
        try:
            # Llamar al dimensionador correspondiente
            dimensionador = DIMENSIONADORES[codigo_unidad]
            resultado = dimensionador(cfg)
            unidades_resultados[codigo_unidad] = resultado
            print(f"    [OK]")
        except Exception as e:
            print(f"    [ERROR] {e}")
            unidades_con_error.append(codigo_unidad)
    
    # Calcular balance de calidad
    print(f"  - Calculando balance de calidad...")
    balance_calidad = calcular_balance_calidad(unidades_resultados, config_tren)
    
    # Calcular lodos
    print(f"  - Consolidando lodos...")
    lodos = calcular_lodos(unidades_resultados)
    
    # Calcular consumos
    print(f"  - Consolidando consumos...")
    consumos = calcular_consumos(unidades_resultados)
    
    # Armar resultado consolidado
    resultado = {
        "entrada": config_tren.to_dict(),
        "tren": {
            "nombre": config_tren.nombre_tren,
            "caudal_total_L_s": config_tren.caudal_total_lps,
            "caudal_por_linea_L_s": config_tren.caudal_por_linea_lps,
            "num_lineas": config_tren.num_lineas,
            "num_unidades": len(config_tren.unidades),
            "unidades_con_error": unidades_con_error,
        },
        "unidades": unidades_resultados,
        "balance_calidad": balance_calidad,
        "lodos": lodos,
        "consumos": consumos,
    }
    
    print(f"[Integrador] Tren procesado: {len(unidades_resultados)} unidades OK")
    if unidades_con_error:
        print(f"  [!] Unidades con error: {unidades_con_error}")
    
    return resultado


# =============================================================================
# MAIN - PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PTAR TREN INTEGRADOR - Prueba de integración")
    print("=" * 60)
    
    from ptar_tren_config import get_tren_piloto_humedal, get_tren_piloto_fp
    
    # Probar tren piloto con humedal
    print("\n[1] Integrando tren piloto - Humedal Vertical:")
    entrada = get_tren_piloto_humedal()
    config = TrenConfig.from_dict(entrada)
    
    resultado = integrar_tren(config)
    
    print(f"\n  Resumen:")
    print(f"    - Unidades: {resultado['tren']['num_unidades']}")
    print(f"    - Eficiencia DBO: {resultado['balance_calidad']['eficiencias_globales']['DBO5_pct']:.1f}%")
    print(f"    - Eficiencia CF: {resultado['balance_calidad']['eficiencias_globales']['CF_pct']:.1f}%")
    print(f"    - Cumple TULSMA: {resultado['balance_calidad']['cumplimiento_TULSMA']}")
    
    # Probar tren piloto con filtro percolador
    print("\n[2] Integrando tren piloto - Filtro Percolador:")
    entrada = get_tren_piloto_fp()
    config = TrenConfig.from_dict(entrada)
    
    resultado = integrar_tren(config)
    
    print(f"\n  Resumen:")
    print(f"    - Unidades: {resultado['tren']['num_unidades']}")
    print(f"    - Eficiencia DBO: {resultado['balance_calidad']['eficiencias_globales']['DBO5_pct']:.1f}%")
    print(f"    - Eficiencia CF: {resultado['balance_calidad']['eficiencias_globales']['CF_pct']:.1f}%")
    print(f"    - Cumple TULSMA: {resultado['balance_calidad']['cumplimiento_TULSMA']}")
    
    print("\n" + "=" * 60)
    print("Integración completada")
    print("=" * 60)
