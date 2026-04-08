#!/usr/bin/env python3
"""
SCRIPT MAESTRO - Dimensiona y genera reporte para la alternativa ESCOGIDA
Uso: python dimensionar_escogida.py [A|B|C|D|E|F]
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ptar_dimensionamiento import ConfigDiseno, calcular_balance_calidad_agua
from generar_latex_A import generar_latex_alternativa_A
from ptar_layout_graficador import generar_layout_con_resultados

# Importar generador completo de Alternativa C (estructura estándar por unidad)
# El generador simplificado (generar_latex_alternativa_C_simple) se mantiene
# temporalmente en este archivo como fallback, pero se deprecará.
from generar_latex_C import generar_latex_alternativa_C_completa


def crear_configuracion_real():
    """
    Configuracion con valores reales del estudio.
    
    Limites de efluente segun TULSMA (Tabla 11):
        DBO5_ef_mg_L = 100 mg/L (limite legal)
        SST_ef_mg_L = 100 mg/L (limite legal)
    """
    return ConfigDiseno(
        Q_total_L_s=10.0,
        Q_linea_L_s=5.0,
        num_lineas=2,
        T_agua_C=25.6,
        T_min_C=21.0,
        DBO5_mg_L=243.10,
        DQO_mg_L=498.00,
        SST_mg_L=156.00,
        DBO5_ef_mg_L=100.00,  # Limite TULSMA (mg/L)
        SST_ef_mg_L=100.00,   # Limite TULSMA (mg/L)
        CS_area=2.0,
        CS_volumen=1.50
    )


def dimensionar_UASB_FiltroPercolador_Cloro(cfg):
    """Dimensiona Alternativa UASB + Filtro Percolador + Cloro"""
    from ptar_dimensionamiento import (
        dimensionar_rejillas, dimensionar_desarenador, dimensionar_uasb,
        dimensionar_filtro_percolador, dimensionar_lecho_secado
    )
    
    resultados = {}
    
    print("\n1. Dimensionando REJILLAS...")
    resultados['rejillas'] = dimensionar_rejillas(cfg)
    print(f"   - Largo: {resultados['rejillas']['largo_layout_m']} m")
    
    print("\n2. Dimensionando DESARENADOR...")
    resultados['desarenador'] = dimensionar_desarenador(cfg)
    print(f"   - Largo: {resultados['desarenador']['L_diseno_m']} m")
    
    print("\n3. Dimensionando UASB...")
    resultados['uasb'] = dimensionar_uasb(cfg)
    print(f"   - Diametro: {resultados['uasb']['D_m']} m")
    
    print("\n4. Dimensionando FILTRO PERCOLADOR...")
    # Usar eficiencia REAL calculada por el UASB (ajustada por temperatura)
    eta_DBO_real = resultados['uasb']['eta_DBO']
    DBO_tras_uasb = cfg.DBO5_mg_L * (1 - eta_DBO_real)
    resultados['filtro_percolador'] = dimensionar_filtro_percolador(cfg, DBO_entrada_mg_L=DBO_tras_uasb)
    print(f"   - DBO entrada: {DBO_tras_uasb:.1f} mg/L (efluente UASB, eta={eta_DBO_real*100:.0f}%)")
    print(f"   - Diametro: {resultados['filtro_percolador']['D_filtro_m']} m")
    
    print("\n5. Dimensionando SEDIMENTADOR...")
    from ptar_dimensionamiento import dimensionar_sedimentador_sec
    # El sedimentador recibe efluente de la etapa biologica aerobia (filtro percolador)
    # Calcula produccion de solidos biologicos (humus) a partir de DBO removida
    DBO_removida_fp_kg_d = resultados['filtro_percolador']['DBO_removida_kg_d']
    DBO_entrada_sed = resultados['filtro_percolador']['DBO_salida_Germain_mg_L']
    
    # Calcular carga de solidos biologicos usando factor de produccion de humus
    solidos_biologicos_kg_d = cfg.sed_factor_produccion_humus * DBO_removida_fp_kg_d
    
    resultados['sedimentador_sec'] = dimensionar_sedimentador_sec(
        cfg, 
        DBO_entrada_mg_L=DBO_entrada_sed,
        solidos_biologicos_entrada_kg_d=solidos_biologicos_kg_d
    )
    print(f"   - Diametro: {resultados['sedimentador_sec']['D_m']} m")
    print(f"   - DBO salida: {resultados['sedimentador_sec']['DBO_salida_mg_L']:.1f} mg/L")
    
    print("\n6. Dimensionando DESINFECCION CON CLORO...")
    from ptar_dimensionamiento import dimensionar_desinfeccion_cloro
    # Calcular CF de entrada (post-sedimentador) basado en eficiencias configuradas
    # CF afluente típico: 1e7 NMP/100mL (aguas residuales sin tratar)
    cf_afluente = 1e7  # NMP/100mL
    cf_tras_uasb = cf_afluente * (1 - cfg.balance_eta_CF_uasb)
    cf_tras_fp = cf_tras_uasb * (1 - cfg.balance_eta_CF_fp)
    cf_tras_sed = cf_tras_fp * (1 - cfg.balance_eta_CF_sed)
    CF_entrada = cf_tras_sed
    resultados['desinfeccion'] = dimensionar_desinfeccion_cloro(cfg, CF_entrada_NMP=CF_entrada)
    d = resultados['desinfeccion']
    print(f"   - Tanque: {d['largo_m']} m x {d['ancho_m']} m")
    print(f"   - Tiempo contacto: {d['TRH_min']} min")
    print(f"   - CT: {d['CT_mg_min_L']} mg.min/L")
    print(f"   - Log reduccion: {d['log_reduccion']}")
    print(f"   - CF final: {d['CF_final_NMP']:.0f} NMP/100mL")
    print(f"   - Cumple TULSMA: {'SI' if d['cumple_TULSMA'] else 'NO'}")
    
    print("\n7. Dimensionando LECHO DE SECADO...")
    # Calcular producción de lodos POR LÍNEA
    # UASB: lodos anaerobios (factor de producción desde config)
    DBO_removida_uasb_kg_d_por_linea = cfg.Q_linea_m3_d * (cfg.DBO5_mg_L / 1000) * resultados['uasb']['eta_DBO']
    lodos_uasb_kg_d_por_linea = cfg.lecho_factor_produccion_lodos * DBO_removida_uasb_kg_d_por_linea
    # Filtro Percolador: humus (calculado por el sedimentador secundario)
    lodos_fp_kg_d_por_linea = resultados['sedimentador_sec']['produccion_humus_kg_d']
    # Producción total de lodos (ambas líneas)
    lodos_total_kg_d_por_linea = lodos_uasb_kg_d_por_linea + lodos_fp_kg_d_por_linea
    lodos_uasb_kg_d_total = lodos_uasb_kg_d_por_linea * cfg.num_lineas
    lodos_fp_kg_d_total = lodos_fp_kg_d_por_linea * cfg.num_lineas
    lodos_total_kg_d_total = lodos_total_kg_d_por_linea * cfg.num_lineas
    
    # Dimensionar lecho con TOTAL de lodos
    resultados['lecho_secado'] = dimensionar_lecho_secado(cfg, lodos_kg_SST_d=lodos_total_kg_d_total)
    
    # Agregar detalles de producción de lodos al resultado para el reporte
    # Por línea
    resultados['lecho_secado']['lodos_uasb_kg_d_por_linea'] = lodos_uasb_kg_d_por_linea
    resultados['lecho_secado']['lodos_fp_kg_d_por_linea'] = lodos_fp_kg_d_por_linea
    resultados['lecho_secado']['lodos_total_kg_d_por_linea'] = lodos_total_kg_d_por_linea
    # Total planta
    resultados['lecho_secado']['lodos_uasb_kg_d'] = lodos_uasb_kg_d_total
    resultados['lecho_secado']['lodos_fp_kg_d'] = lodos_fp_kg_d_total
    resultados['lecho_secado']['lodos_total_kg_d'] = lodos_total_kg_d_total
    resultados['lecho_secado']['num_lineas'] = cfg.num_lineas
    
    print(f"   - Lodos UASB por línea: {lodos_uasb_kg_d_por_linea:.2f} kg SST/d")
    print(f"   - Lodos FP por línea: {lodos_fp_kg_d_por_linea:.2f} kg SST/d")
    print(f"   - Total por línea: {lodos_total_kg_d_por_linea:.2f} kg SST/d")
    print(f"   - Lodos UASB total ({cfg.num_lineas} líneas): {lodos_uasb_kg_d_total:.2f} kg SST/d")
    print(f"   - Lodos FP total ({cfg.num_lineas} líneas): {lodos_fp_kg_d_total:.2f} kg SST/d")
    print(f"   - TOTAL LODOS PLANTA: {lodos_total_kg_d_total:.2f} kg SST/d")
    print(f"   - Area total: {resultados['lecho_secado']['A_total_m2']} m2")
    print(f"   - Area por bloque: {resultados['lecho_secado']['A_bloque_m2']} m2")
    
    # Calcular balance completo de calidad
    print("\n8. Calculando BALANCE DE CALIDAD DEL AGUA...")
    balance = calcular_balance_calidad_agua(cfg, resultados)
    resultados['balance_calidad'] = balance
    
    # Imprimir resumen del balance
    print("\n   BALANCE DE CALIDAD DEL AGUA:")
    print("   " + "-" * 66)
    print(f"   {'Parametro':<15} {'Afluente':>12} {'Post-UASB':>12} {'Post-FP':>12} {'Efluente':>12}")
    print("   " + "-" * 66)
    
    # DBO5
    dbos = balance['afluente']['DBO5_mg_L']
    dbos_uasb = balance['tras_uasb']['DBO5_mg_L']
    dbos_fp = balance['tras_fp']['DBO5_mg_L']
    dbos_final = balance['efluente_final']['DBO5_mg_L']
    print(f"   {'DBO5 (mg/L)':<15} {dbos:>12.1f} {dbos_uasb:>12.1f} {dbos_fp:>12.1f} {dbos_final:>12.1f}")
    
    # DQO
    dqos = balance['afluente']['DQO_mg_L']
    dqos_uasb = balance['tras_uasb']['DQO_mg_L']
    dqos_fp = balance['tras_fp']['DQO_mg_L']
    dqos_final = balance['efluente_final']['DQO_mg_L']
    print(f"   {'DQO (mg/L)':<15} {dqos:>12.1f} {dqos_uasb:>12.1f} {dqos_fp:>12.1f} {dqos_final:>12.1f}")
    
    # SST
    ssts = balance['afluente']['SST_mg_L']
    ssts_uasb = balance['tras_uasb']['SST_mg_L']
    ssts_fp = balance['tras_fp']['SST_mg_L']
    ssts_final = balance['efluente_final']['SST_mg_L']
    print(f"   {'SST (mg/L)':<15} {ssts:>12.1f} {ssts_uasb:>12.1f} {ssts_fp:>12.1f} {ssts_final:>12.1f}")
    
    # CF
    cfs = balance['afluente']['CF_NMP']
    cfs_uasb = balance['tras_uasb']['CF_NMP']
    cfs_fp = balance['tras_fp']['CF_NMP']
    cfs_final = balance['efluente_final']['CF_NMP']
    print(f"   {'CF (NMP/100mL)':<15} {cfs:>12.0f} {cfs_uasb:>12.0f} {cfs_fp:>12.0f} {cfs_final:>12.0f}")
    
    print("   " + "-" * 66)
    
    # Eficiencias totales
    print("\n   EFICIENCIAS TOTALES:")
    ef = balance['eficiencias_totales']
    print(f"     DBO5: {ef['DBO5_pct']:.1f}% | DQO: {ef['DQO_pct']:.1f}% | SST: {ef['SST_pct']:.1f}% | CF: {ef['CF_pct']:.1f}%")
    
    # Cumplimiento TULSMA
    print("\n   CUMPLIMIENTO TULSMA:")
    cumple = balance['cumplimiento_TULSMA']
    print(f"     DBO5 <= 100 mg/L: {'CUMPLE' if cumple['DBO5'] else 'NO CUMPLE'}")
    print(f"     SST <= 100 mg/L:  {'CUMPLE' if cumple['SST'] else 'NO CUMPLE'}")
    print(f"     CF <= 3000 NMP/100mL: {'CUMPLE' if cumple['CF'] else 'NO CUMPLE'}")
    
    return resultados


def dimensionar_UASB_HumedalVertical_Cloro(cfg):
    """Dimensiona Alternativa C: UASB + Humedal Vertical + Cloro"""
    from ptar_dimensionamiento import (
        dimensionar_rejillas, dimensionar_desarenador, dimensionar_uasb,
        dimensionar_humedal_vertical, dimensionar_desinfeccion_cloro,
        dimensionar_lecho_secado, calcular_balance_calidad_agua
    )
    
    resultados = {}
    
    print("\n1. Dimensionando REJILLAS...")
    resultados['rejillas'] = dimensionar_rejillas(cfg)
    print(f"   - Largo: {resultados['rejillas']['largo_layout_m']} m")
    
    print("\n2. Dimensionando DESARENADOR...")
    resultados['desarenador'] = dimensionar_desarenador(cfg)
    print(f"   - Largo: {resultados['desarenador']['L_diseno_m']} m")
    
    print("\n3. Dimensionando UASB...")
    resultados['uasb'] = dimensionar_uasb(cfg)
    print(f"   - Diametro: {resultados['uasb']['D_m']} m")
    
    print("\n4. Dimensionando HUMEDAL VERTICAL...")
    # Usar eficiencia REAL calculada por el UASB (ajustada por temperatura)
    eta_DBO_real = resultados['uasb']['eta_DBO']
    DBO_tras_uasb = cfg.DBO5_mg_L * (1 - eta_DBO_real)
    resultados['humedal'] = dimensionar_humedal_vertical(cfg, DBO_entrada_mg_L=DBO_tras_uasb)
    print(f"   - DBO entrada: {DBO_tras_uasb:.1f} mg/L (efluente UASB, eta={eta_DBO_real*100:.0f}%)")
    print(f"   - Area: {resultados['humedal']['A_sup_m2']:.0f} m²")
    print(f"   - Dimensiones: {resultados['humedal']['largo_m']:.1f} x {resultados['humedal']['ancho_m']:.1f} m")
    
    print("\n5. Dimensionando DESINFECCION CON CLORO...")
    # Calcular CF de entrada (post-humedal)
    cf_afluente = 1e7  # NMP/100mL (típico aguas residuales sin tratar)
    cf_tras_uasb = cf_afluente * (1 - cfg.balance_eta_CF_uasb)
    cf_tras_humedal = cf_tras_uasb * (1 - cfg.humedal_eta_CF)
    resultados['desinfeccion'] = dimensionar_desinfeccion_cloro(cfg, CF_entrada_NMP=cf_tras_humedal)
    print(f"   - Tanque: {resultados['desinfeccion']['largo_m']:.1f} m x {resultados['desinfeccion']['ancho_m']:.1f} m")
    print(f"   - Tiempo contacto: {resultados['desinfeccion']['TRH_min']:.1f} min")
    print(f"   - CT: {resultados['desinfeccion']['CT_mg_min_L']:.1f} mg.min/L")
    print(f"   - Log reduccion: {resultados['desinfeccion']['log_reduccion']}")
    print(f"   - CF final: {resultados['desinfeccion']['CF_final_NMP']:.0f} NMP/100mL")
    print(f"   - Cumple TULSMA: {'SI' if resultados['desinfeccion']['cumple_TULSMA'] else 'NO'}")
    
    print("\n6. Dimensionando LECHO DE SECADO...")
    # Calcular producción de lodos
    DBO_removida_uasb_kg_d_por_linea = cfg.Q_linea_m3_d * (cfg.DBO5_mg_L / 1000) * resultados['uasb']['eta_DBO']
    lodos_uasb_kg_d_por_linea = cfg.lecho_factor_produccion_lodos * DBO_removida_uasb_kg_d_por_linea
    lodos_humedal_kg_d_por_linea = 0.0  # Los sólidos se acumulan en el lecho
    lodos_total_kg_d_total = (lodos_uasb_kg_d_por_linea + lodos_humedal_kg_d_por_linea) * cfg.num_lineas
    resultados['lecho_secado'] = dimensionar_lecho_secado(cfg, lodos_kg_SST_d=lodos_total_kg_d_total)
    print(f"   - Lodos UASB por línea: {lodos_uasb_kg_d_por_linea:.2f} kg SST/d")
    print(f"   - Lodos humedal por línea: {lodos_humedal_kg_d_por_linea:.2f} kg SST/d")
    print(f"   - Total por línea: {lodos_uasb_kg_d_por_linea + lodos_humedal_kg_d_por_linea:.2f} kg SST/d")
    print(f"   - Area total: {resultados['lecho_secado']['A_total_m2']:.1f} m2")
    
    print("\n7. Calculando BALANCE DE CALIDAD DEL AGUA...")
    # Calcular balance completo de calidad
    resultados['balance_calidad'] = calcular_balance_calidad_agua(cfg, resultados)
    balance = resultados['balance_calidad']
    
    print("\n   BALANCE DE CALIDAD DEL AGUA:")
    print("   " + "-" * 66)
    print(f"   {'Parametro':<15} {'Afluente':>12} {'Post-UASB':>12} {'Post-Humedal':>12} {'Efluente':>12}")
    print("   " + "-" * 66)
    
    # DBO5
    dbos = balance['afluente']['DBO5_mg_L']
    dbos_uasb = balance['tras_uasb']['DBO5_mg_L']
    dbos_hum = balance['tras_humedal'].get('DBO5_mg_L', resultados['humedal']['DBO_salida_mg_L'])
    dbos_final = balance['efluente_final']['DBO5_mg_L']
    print(f"   {'DBO5 (mg/L)':<15} {dbos:>12.1f} {dbos_uasb:>12.1f} {dbos_hum:>12.1f} {dbos_final:>12.1f}")
    
    # SST
    ssts = balance['afluente']['SST_mg_L']
    ssts_uasb = balance['tras_uasb']['SST_mg_L']
    ssts_hum = balance['tras_humedal']['SST_mg_L']
    ssts_final = balance['efluente_final']['SST_mg_L']
    print(f"   {'SST (mg/L)':<15} {ssts:>12.1f} {ssts_uasb:>12.1f} {ssts_hum:>12.1f} {ssts_final:>12.1f}")
    
    # CF
    cfs = balance['afluente']['CF_NMP']
    cfs_uasb = balance['tras_uasb']['CF_NMP']
    cfs_hum = balance['tras_humedal']['CF_NMP']
    cfs_final = balance['efluente_final']['CF_NMP']
    print(f"   {'CF (NMP/100mL)':<15} {cfs:>12.0f} {cfs_uasb:>12.0f} {cfs_hum:>12.0f} {cfs_final:>12.0f}")
    
    print("   " + "-" * 66)
    
    # Eficiencias totales
    print("\n   EFICIENCIAS TOTALES:")
    ef = balance['eficiencias_totales']
    print(f"     DBO5: {ef['DBO5_pct']:.1f}% | SST: {ef['SST_pct']:.1f}% | CF: {ef['CF_pct']:.1f}%")
    
    # Cumplimiento TULSMA
    print("\n   CUMPLIMIENTO TULSMA:")
    cumple = balance['cumplimiento_TULSMA']
    print(f"     DBO5 <= 100 mg/L: {'CUMPLE' if cumple['DBO5'] else 'NO CUMPLE'}")
    print(f"     SST <= 100 mg/L:  {'CUMPLE' if cumple['SST'] else 'NO CUMPLE'}")
    print(f"     CF <= 3000 NMP/100mL: {'CUMPLE' if cumple['CF'] else 'NO CUMPLE'}")
    
    return resultados


def generar_latex_alternativa_C_simple(cfg, resultados, output_path, area_m2=None, balance_calidad=None):
    """
    [TEMPORAL/DEPRECATED] Generador simplificado para Alternativa C.
    
    Este generador se mantiene temporalmente como fallback, pero el objetivo
    final es usar generar_latex_alternativa_C_completa() desde generar_latex_C.py
    que sigue el formato estándar del proyecto (5 secciones por unidad).
    
    Cuando el generador completo esté terminado (PASOS 3-9), esta función
    podrá eliminarse o deprecarse oficialmente.
    
    2026-04-06: Marcado como temporal mientras se completa memoria estándar.
    """
    
    output_dir = os.path.dirname(output_path) or '.'
    
    # Extraer resultados
    uasb = resultados.get('uasb', {})
    humedal = resultados.get('humedal', {})
    desinfeccion = resultados.get('desinfeccion', {})
    lecho = resultados.get('lecho_secado', {})
    balance = resultados.get('balance_calidad', balance_calidad or {})
    
    # Layout filename
    layout_filename = f"Layout_C_2lineas.png"
    
    # Crear contenido LaTeX simplificado
    contenido = rf"""\documentclass[12pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[spanish]{{babel}}
\usepackage{{geometry}}
\usepackage{{amsmath}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{xcolor}}
\usepackage{{hyperref}}

\geometry{{margin=2.5cm}}

\title{{{{\large Memoria de Cálculo -- PTAR San Cristóbal}}\\[0.5em]
\textbf{{Alternativa C: UASB + Humedal Vertical + Cloro}}}}
\author{{Diseño PTAR}}
\date{{\today}}

\begin{{document}}

\maketitle

\section{{Resumen Ejecutivo}}

\begin{{table}}[h]
\centering
\caption{{Parámetros de diseño -- Alternativa C}}
\begin{{tabular}}{{lc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} \\
\midrule
Caudal de diseño & {cfg.Q_total_L_s:.1f} L/s \\
DBO$_5$ afluente & {cfg.DBO5_mg_L:.1f} mg/L \\
Temperatura & {cfg.T_agua_C:.1f}°C \\
\bottomrule
\end{{tabular}}
\end{{table}}

\section{{Dimensionamiento de Unidades}}

\subsection{{1. Reactor UASB}}
\begin{{itemize}}
    \item Diámetro: {uasb.get('D_m', 0):.2f} m
    \item Altura: {uasb.get('H_r_m', 0):.2f} m
    \item Volumen: {uasb.get('V_r_m3', 0):.1f} m$^3$
    \item TRH: {uasb.get('TRH_h', 0):.1f} h
    \item Eficiencia DBO: {uasb.get('eta_DBO', 0)*100:.0f}\%
\end{{itemize}}

\subsection{{2. Humedal Vertical}}
\begin{{itemize}}
    \item Área superficial: {humedal.get('A_sup_m2', 0):.1f} m$^2$
    \item Dimensiones: {humedal.get('largo_m', 0):.1f} m $\times$ {humedal.get('ancho_m', 0):.1f} m
    \item Profundidad: {humedal.get('H_total_m', 0):.2f} m
    \item DBO salida: {humedal.get('DBO_salida_mg_L', 0):.1f} mg/L
\end{{itemize}}

\subsection{{3. Desinfección con Cloro}}
\begin{{itemize}}
    \item Tanque: {desinfeccion.get('largo_m', 0):.1f} m $\times$ {desinfeccion.get('ancho_m', 0):.1f} m
    \item Tiempo de contacto: {desinfeccion.get('TRH_min', 0):.1f} min
    \item Dosis de cloro: {desinfeccion.get('dosis_cloro_mg_L', 0):.1f} mg/L
    \item CF final: {desinfeccion.get('CF_final_NMP', 0):.0f} NMP/100mL
    \item Cumple TULSMA: {'Sí' if desinfeccion.get('cumple_TULSMA', False) else 'No'}
\end{{itemize}}

\subsection{{4. Lecho de Secado}}
\begin{{itemize}}
    \item Área total: {lecho.get('A_total_m2', 0):.1f} m$^2$
    \item Número de celdas: {lecho.get('n_celdas', 0)}
    \item Dimensiones: {lecho.get('largo_m', 0):.1f} m $\times$ {lecho.get('ancho_m', 0):.1f} m
\end{{itemize}}

"""
    
    # Agregar balance si está disponible
    if balance:
        ef = balance.get('eficiencias_totales', {})
        cumple = balance.get('cumplimiento_TULSMA', {})
        contenido += rf"""
\section{{Balance de Calidad del Agua}}

\begin{{table}}[h]
\centering
\caption{{Eficiencias de remoción}}
\begin{{tabular}}{{lc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Eficiencia}} \\
\midrule
DBO$_5$ & {ef.get('DBO5_pct', 0):.1f}\% \\
SST & {ef.get('SST_pct', 0):.1f}\% \\
CF & {ef.get('CF_pct', 0):.1f}\% \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Cumplimiento TULSMA}}
\begin{{itemize}}
    \item DBO$_5$ $\leq$ 100 mg/L: {'CUMPLE' if cumple.get('DBO5', False) else 'NO CUMPLE'}
    \item SST $\leq$ 100 mg/L: {'CUMPLE' if cumple.get('SST', False) else 'NO CUMPLE'}
    \item CF $\leq$ 3000 NMP/100mL: {'CUMPLE' if cumple.get('CF', False) else 'NO CUMPLE'}
\end{{itemize}}

"""
    
    # Agregar layout y cierre
    contenido += rf"""
\section{{Layout de Planta}}

\begin{{figure}}[h]
\centering
\includegraphics[width=\textwidth]{{{layout_filename}}}
\caption{{Layout general -- Alternativa C (2 líneas de tratamiento)}}
\end{{figure}}

\vspace{{1cm}}
\noindent\textbf{{Área total aproximada:}} {area_m2 or 'N/A'} m$^2$

\end{{document}}
"""
    
    # Guardar archivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"   Archivo LaTeX generado: {output_path}")


def main():
    """Funcion principal."""
    
    if len(sys.argv) < 2:
        print("Uso: python dimensionar_escogida.py [A|B|C|D|E|F]")
        print("Ejemplo: python dimensionar_escogida.py A")
        return
    
    alt_id = sys.argv[1].upper()
    
    print("=" * 70)
    print(f"DIMENSIONAMIENTO ALTERNATIVA {alt_id}")
    print("=" * 70)
    
    # Crear configuracion
    cfg = crear_configuracion_real()
    print(f"\nParametros de entrada:")
    print(f"  - Caudal total: {cfg.Q_total_L_s} L/s")
    print(f"  - DBO5: {cfg.DBO5_mg_L} mg/L")
    print(f"  - Temperatura: {cfg.T_agua_C} C")
    
    # Dimensionar segun la alternativa
    if alt_id == 'A':
        resultados = dimensionar_UASB_FiltroPercolador_Cloro(cfg)
    elif alt_id == 'C':
        resultados = dimensionar_UASB_HumedalVertical_Cloro(cfg)
    else:
        print(f"\n[ADVERTENCIA] Alternativa {alt_id} aun no implementada.")
        print("Usando Alternativa UASB + Filtro Percolador + Cloro como ejemplo...")
        resultados = dimensionar_UASB_FiltroPercolador_Cloro(cfg)
    
    # Crear directorios de salida
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')
    os.makedirs(output_dir, exist_ok=True)
    
    # PASO 1: Generar Layout PRIMERO (para que exista cuando compile el PDF)
    print("\n" + "=" * 70)
    print("GENERANDO LAYOUT...")
    print("=" * 70)
    
    area_m2 = None
    try:
        # Definir unidades según la alternativa
        if alt_id == 'C':
            unidades = ['Rejillas', 'Desarenador', 'UASB', 'Humedal_Vertical', 'Desinfeccion']
        else:
            unidades = ['Rejillas', 'Desarenador', 'UASB', 'Filtro_Percolador', 'Sedimentador', 'Desinfeccion']
        x, y = generar_layout_con_resultados(
            alt_id, unidades, f'Alternativa {alt_id}', resultados, output_dir,
            caudal_L_s=cfg.Q_linea_L_s
        )
        area_m2 = round(x * y)
        print(f"\n   - Layout generado: {x:.1f} m x {y:.1f} m")
        print(f"   - Area total: {area_m2} m2")
        print(f"   - Guardado en: {output_dir}/Layout_{alt_id}_2lineas.png")
    except Exception as e:
        print(f"\n   [ADVERTENCIA] Error generando layout: {e}")
    
    # PASO 2: Generar LaTeX
    print("\n" + "=" * 70)
    print("GENERANDO REPORTE LATEX...")
    print("=" * 70)
    
    latex_path = os.path.join(output_dir, f'seleccion_alternativa_{alt_id}.tex')
    balance_calidad = resultados.get('balance_calidad')
    
    if alt_id == 'A':
        generar_latex_alternativa_A(cfg, resultados, latex_path, area_m2=area_m2, balance_calidad=balance_calidad)
    elif alt_id == 'C':
        # Alternativa C: Usar generador completo estándar (estructura 5-secciones por unidad)
        # El generador simplificado queda disponible como fallback temporal abajo.
        print("   Usando generador COMPLETO estándar (memoria por unidad)...")
        generar_latex_alternativa_C_completa(cfg, resultados, latex_path, 
                                              area_m2=area_m2, balance_calidad=balance_calidad)
    else:
        print(f"   [INFO] Generación de LaTeX no implementada para Alternativa {alt_id}")
    
    # PASO 3: Compilar PDF (ahora el layout ya existe)
    print("\n   Intentando compilar a PDF...")
    try:
        from compilar_latex import compilar
        exito, mensaje, pdf_path = compilar(latex_path, output_dir)
        if exito:
            print(f"   [OK] PDF generado: {pdf_path}")
        else:
            print(f"   [INFO] {mensaje}")
    except Exception as e:
        print(f"   [INFO] No se pudo compilar: {e}")
    
    print("\n" + "=" * 70)
    if alt_id == 'A':
        print("PROCESO COMPLETADO - Alternativa A: UASB + Filtro Percolador + Cloro")
    elif alt_id == 'C':
        print("PROCESO COMPLETADO - Alternativa C: UASB + Humedal Vertical + Cloro")
    else:
        print(f"PROCESO COMPLETADO - Alternativa {alt_id}")
    print("=" * 70)


if __name__ == "__main__":
    main()
