#!/usr/bin/env python3
"""
reporte_resultados.py
=====================
Módulo reutilizable para generar la sección LaTeX completa de
Resultados, incluyendo layout, áreas de predio, resumen de
unidades, balance de calidad, verificación TULSMA y consumos.

Se conecta directamente con:
  - ptar_layout_graficador.generar_layout() para la figura
  - ptar_dimensionamiento.ConfigDiseno para parámetros de diseño
"""

import os
import sys
from typing import Dict, Any, List, Tuple


def calcular_areas_complementarias(cfg, area_tratamiento: float) -> Dict[str, Any]:
    """
    Calcula todas las áreas complementarias basadas en ConfigDiseno.
    """
    area_amortiguacion = area_tratamiento * cfg.layout_factor_amortiguacion
    area_complementaria = area_tratamiento * cfg.layout_factor_complementaria
    area_caminos = area_tratamiento * cfg.layout_factor_caminos
    area_total = (area_tratamiento + area_amortiguacion + area_complementaria) / (1 - cfg.layout_factor_zona_verde)
    area_verde = area_total * cfg.layout_factor_zona_verde

    bodega_quimicos = max(cfg.layout_area_min_bodega_quimicos_m2, area_tratamiento * cfg.layout_factor_bodega_quimicos)
    laboratorio = max(cfg.layout_area_min_laboratorio_m2, area_tratamiento * cfg.layout_factor_laboratorio)
    caseta = max(cfg.layout_area_min_caseta_operacion_m2, area_tratamiento * cfg.layout_factor_caseta)
    lavado = max(cfg.layout_area_min_lavado_m2, area_tratamiento * cfg.layout_factor_lavado)
    estacionamiento = max(cfg.layout_area_min_estacionamiento_m2, area_tratamiento * cfg.layout_factor_estacionamiento)
    zona_camiones = max(cfg.layout_area_min_zona_camiones_m2, area_tratamiento * cfg.layout_factor_zona_camiones)
    acceso = max(cfg.layout_area_min_acceso_principal_m2, area_tratamiento * cfg.layout_factor_acceso)
    bodega_general = max(cfg.layout_area_min_bodega_general_m2, area_tratamiento * cfg.layout_factor_bodega_general)
    carga_lodos = max(cfg.layout_area_min_carga_lodos_m2, area_tratamiento * cfg.layout_factor_carga_lodos)

    return {
        'area_tratamiento': area_tratamiento,
        'area_amortiguacion': area_amortiguacion,
        'area_complementaria': area_complementaria,
        'area_caminos': area_caminos,
        'area_verde': area_verde,
        'area_total': area_total,
        'bodega_quimicos': bodega_quimicos,
        'laboratorio': laboratorio,
        'caseta': caseta,
        'lavado': lavado,
        'estacionamiento': estacionamiento,
        'zona_camiones': zona_camiones,
        'acceso': acceso,
        'bodega_general': bodega_general,
        'carga_lodos': carga_lodos,
    }


def generar_latex_seccion_layout(cfg, layout_info: Dict[str, Any], titulo_section: bool = False) -> str:
    """
    Genera el bloque LaTeX completo: figura del layout + tabla de áreas + fórmulas + nota.
    """
    area_m2 = float(layout_info.get('area_layout_m2', 0))
    fig_filename = os.path.basename(layout_info.get('fig_path', 'layout.png'))
    caption = layout_info.get('caption', 'Disposición espacial de unidades')
    ancho = layout_info.get('ancho_total_m', 0)
    largo = layout_info.get('largo_total_m', 0)
    lineas_texto = f"{cfg.num_lineas} línea{'s' if cfg.num_lineas > 1 else ''}"

    areas = calcular_areas_complementarias(cfg, area_m2)
    a = areas

    comando_titulo = r"\section" if titulo_section else r"\subsection"
    latex = rf"""
{comando_titulo}{{Disposición de la Planta y Áreas de Predio}}

La siguiente figura presenta la disposición espacial de las unidades de tratamiento. El layout muestra {lineas_texto} paralelas operativas, cada una con capacidad para tratar {cfg.Q_linea_L_s:.1f}~L/s, permitiendo la operación con una sola línea durante mantenimiento o reparaciones. Las dimensiones del área de tratamiento son aproximadamente {ancho:.1f}~m de ancho por {largo:.1f}~m de largo.

\begin{{figure}}[H]
\centering
\includegraphics[width=\textwidth]{{figuras/{fig_filename}}}
\caption{{{caption}}}
\label{{fig:layout_general}}
\end{{figure}}

El área calculada de {area_m2:.0f}~m$^2$ corresponde únicamente a las unidades de tratamiento con sus márgenes mínimos de acceso. Sin embargo, para garantizar una operación segura y eficiente durante toda la vida útil de la planta, es necesario prever espacios adicionales para acceso vehicular y peatonal de operarios y visitantes, almacenamiento seguro de productos químicos y herramientas, realización de análisis de control de calidad in-situ, estacionamiento para personal y visitantes, circulación interna de vehículos de mantenimiento y retiro de lodos, separación de límites con zonas verdes para control de olores, y espacios administrativos para control operativo.

\begin{{table}}[H]
\centering
\caption{{Áreas complementarias de la planta}}
\small
\begin{{tabular}}{{lp{{8cm}}c}}
\toprule
Área & Descripción & Dimensión aprox. \\
\midrule
Zona de amortiguación & Perimetral alrededor de unidades (2--3~m) para acceso y seguridad & {a['area_amortiguacion']:.0f}~m$^2$ ({cfg.layout_factor_amortiguacion*100:.0f}\%) \\
\addlinespace
Bodega de químicos & Almacenamiento de hipoclorito y productos químicos & {a['bodega_quimicos']:.0f}~m$^2$ \\
\addlinespace
Laboratorio/control & Análisis de calidad del agua (DBO, SST, CF, pH) & {a['laboratorio']:.0f}~m$^2$ \\
\addlinespace
Caseta de operación & Control, panel, escritorio, baño & {a['caseta']:.0f}~m$^2$ \\
\addlinespace
Área de lavado & Limpieza de equipos y herramientas & {a['lavado']:.0f}~m$^2$ \\
\addlinespace
Estacionamiento & Vehículos del personal y visitantes (2--3 vehículos) & {a['estacionamiento']:.0f}~m$^2$ \\
\addlinespace
Zona de camiones & Acceso de camiones cisterna/retiro de lodo & {a['zona_camiones']:.0f}~m$^2$ \\
\addlinespace
Caminos internas & Circulación vehicular y peatonal (ancho 3--4~m) & {a['area_caminos']:.0f}~m$^2$ ({cfg.layout_factor_caminos*100:.0f}\% área) \\
\addlinespace
Acceso principal & Entrada, portón y caseta de guardia & {a['acceso']:.0f}~m$^2$ \\
\addlinespace
Bodega general & Herramientas, repuestos, EPP & {a['bodega_general']:.0f}~m$^2$ \\
\addlinespace
Zona carga de lodos & Carga/descarga de lodo deshidratado & {a['carga_lodos']:.0f}~m$^2$ \\
\addlinespace
Área verde/buffer & Separación de límites, revegetación & {a['area_verde']:.0f}~m$^2$ ({cfg.layout_factor_zona_verde*100:.0f}\% total) \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Área total estimada del predio}}

Considerando el área de tratamiento ({area_m2:.0f}~m$^2$), amortiguación ({cfg.layout_factor_amortiguacion*100:.0f}\%), complementarias operativas y zona verde ({cfg.layout_factor_zona_verde*100:.0f}\% del total):

\begin{{equation}}
A_{{total}} = \frac{{A_{{tratamiento}} + A_{{amortiguación}} + A_{{complementarias}}}}{{1 - {cfg.layout_factor_zona_verde:.2f}}}
\end{{equation}}

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_{{tratamiento}}$] = {area_m2:.0f}~m$^2$
    \item[$A_{{amortiguación}}$] = {a['area_amortiguacion']:.0f}~m$^2$ ({cfg.layout_factor_amortiguacion*100:.0f}\%)
    \item[$A_{{complementarias}}$] = {a['area_complementaria']:.0f}~m$^2$ ({cfg.layout_factor_complementaria*100:.0f}\% operativas estimado)
\end{{itemize}}

\begin{{equation}}
A_{{total}} = \frac{{{area_m2:.0f} + {a['area_amortiguacion']:.0f} + {a['area_complementaria']:.0f}}}{{{1 - cfg.layout_factor_zona_verde:.2f}}} \approx \mathbf{{{a['area_total']:.0f} \text{{ m}}^2}} \approx \mathbf{{{a['area_total']/10000:.2f} \text{{ ha}}}}
\end{{equation}}

\textbf{{Nota:}} El área total del predio debe ser de aproximadamente {a['area_total']:.0f}~m$^2$ ({a['area_total']/10000:.2f}~ha) para operación adecuada con circulación interna, estacionamiento y zonas verdes.

\newpage
"""
    return latex.strip() + "\n"


def _fila_dimension_unidad(unidad: str, r: Dict[str, Any], cfg) -> str:
    """Genera una fila de la tabla de dimensionamiento para una unidad."""
    num_lineas = cfg.num_lineas
    u = r.get(unidad, {})
    if unidad == 'rejillas':
        return (f"Rejillas & {u.get('ancho_layout_m', 0):.2f} $\\times$ {u.get('h_tirante_m', 0):.2f} & {num_lineas} & "
                f"Velocidad: {u.get('v_canal_adoptada_m_s', 0):.2f} m/s \\\\")
    elif unidad == 'desarenador':
        H = u.get('H_util_m', 0) + 0.3
        trh = u.get('t_r_real_s', u.get('t_r_nominal_s', 30))
        return (f"Desarenador & {u.get('b_canal_m', 0):.2f} $\\times$ {u.get('L_diseno_m', 0):.1f} $\\times$ {H:.1f} & {num_lineas} & "
                f"TRH: {trh:.0f}~s (referencia: 30--60~s) \\\\")
    elif unidad == 'uasb':
        return (f"Reactor UASB & D = {u.get('D_m', 0):.2f}, H = {u.get('H_total_construccion_m', 0):.1f} & {num_lineas} & "
                f"v$_{{up}}$ = {u.get('v_up_m_h', 0):.2f} m/h \\\\")
    elif unidad == 'filtro_percolador':
        qa = u.get('Q_A_real_m3_m2_h', 0)
        qamax = u.get('Q_A_max_m3_m2_h', 0)
        return (f"Filtro Percolador & D = {u.get('D_filtro_m', 0):.2f}, H = {u.get('H_total_m', 0):.1f} & {num_lineas} & "
                f"Q$_A$ = {qa:.3f} m$^3$/m$^2$·h (máx: {qamax:.2f}) \\\\")
    elif unidad == 'sedimentador_sec':
        return (f"Sedimentador Secundario & D = {u.get('D_m', 0):.2f}, H = {u.get('h_sed_m', 0):.1f} & {num_lineas} & "
                f"SOR = {u.get('SOR_m3_m2_d', 0):.1f} m$^3$/m$^2\\cdot$d \\\\")
    elif unidad in ('cloro', 'desinfeccion'):
        return (f"Desinfeccion (Cloro) & {u.get('largo_m', 0):.1f} $\\times$ {u.get('ancho_m', 0):.1f} $\\times$ {u.get('h_total_m', 0):.1f} & {num_lineas} & "
                f"CT = {u.get('CT_mg_min_L', 0):.0f} mg$\\cdot$min/L \\\\")
    elif unidad == 'lecho_secado':
        return (f"Lecho de Secado & {u.get('largo_m', 0):.1f} $\\times$ {u.get('ancho_m', 0):.1f} & {num_lineas} & "
                f"Área: {u.get('A_bloque_m2', 0):.1f} m$^2$ \\\\")
    elif unidad == 'humedal_vertical':
        return (f"Humedal Vertical & {u.get('largo_total_m', u.get('largo_m', 0)):.1f} $\\times$ {u.get('ancho_total_m', u.get('ancho_m', 0)):.1f} & {num_lineas} & "
                f"Área: {u.get('A_sup_m2', 0):.1f} m$^2$ \\\\")
    elif unidad == 'baf':
        return (f"BAF & {u.get('largo_m', 0):.1f} $\\times$ {u.get('ancho_m', 0):.1f} & {num_lineas} & "
                f"EBCT: {u.get('EBCT_h', 0):.1f} h \\\\")
    elif unidad == 'taf':
        return (f"TAF & {u.get('largo_m', 0):.1f} $\\times$ {u.get('ancho_m', 0):.1f} & {num_lineas} & "
                f"Área: {u.get('A_sup_m2', 0):.1f} m$^2$ \\\\")
    elif unidad == 'abr_rap':
        return (f"ABR-RAP & {u.get('largo_m', 0):.1f} $\\times$ {u.get('ancho_m', 0):.1f} & {num_lineas} & "
                f"v$_{{up}}$ = {u.get('v_up_m_h', 0):.2f} m/h \\\\")
    return ""


def _filas_dimensionamiento(resultados: Dict[str, Any], cfg) -> str:
    """Genera las filas de la tabla de dimensionamiento dinámicamente."""
    orden = ['rejillas', 'desarenador', 'uasb', 'abr_rap', 'humedal_vertical',
             'filtro_percolador', 'sedimentador_sec', 'baf', 'taf', 'cloro', 'desinfeccion', 'lecho_secado']
    filas = []
    for u in orden:
        if u in resultados:
            fila = _fila_dimension_unidad(u, resultados, cfg)
            if fila:
                filas.append(fila)
    return "\n".join(filas)


def _eficiencia_pct(entrada: float, salida: float) -> float:
    if entrada and entrada > 0:
        return max(0.0, (1 - salida / entrada) * 100)
    return 0.0


def _armar_balance_calidad(resultados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construye un dict balance_calidad a partir de los _calidad_* guardados
    en resultados por generar_tren.py.
    """
    bal: Dict[str, Any] = {}
    if '_calidad_afluente' in resultados:
        bal['afluente'] = resultados['_calidad_afluente']
    if '_calidad_efluente' in resultados:
        bal['efluente_final'] = resultados['_calidad_efluente']

    # Mapeo de unidades a claves de etapa
    etapas = {
        'uasb': 'tras_uasb',
        'filtro_percolador': 'tras_fp',
        'sedimentador_sec': 'tras_sed',
        'humedal_vertical': 'tras_humedal',
        'baf': 'tras_baf',
        'taf': 'tras_taf',
        'abr_rap': 'tras_abr',
    }
    ef_map = {
        'uasb': 'eficiencias_uasb',
        'filtro_percolador': 'eficiencias_fp',
        'sedimentador_sec': 'eficiencias_sed',
        'humedal_vertical': 'eficiencias_humedal',
        'baf': 'eficiencias_baf',
        'taf': 'eficiencias_taf',
        'abr_rap': 'eficiencias_abr',
    }

    for unidad, key in etapas.items():
        if unidad in resultados and isinstance(resultados[unidad], dict):
            salida = resultados[unidad].get('_calidad_salida')
            entrada = resultados[unidad].get('_calidad_entrada')
            if salida is not None:
                bal[key] = salida
            if entrada is not None and salida is not None:
                ef_key = ef_map.get(unidad, f'eficiencias_{unidad}')
                bal[ef_key] = {
                    'DBO5_pct': _eficiencia_pct(entrada.get('DBO5_mg_L', 0), salida.get('DBO5_mg_L', 0)),
                    'DQO_pct': _eficiencia_pct(entrada.get('DQO_mg_L', 0), salida.get('DQO_mg_L', 0)),
                    'SST_pct': _eficiencia_pct(entrada.get('SST_mg_L', 0), salida.get('SST_mg_L', 0)),
                    'CF_pct': _eficiencia_pct(entrada.get('CF_NMP_100mL', 0), salida.get('CF_NMP_100mL', 0)),
                }

    # Eficiencias totales
    if 'afluente' in bal and 'efluente_final' in bal:
        aff = bal['afluente']
        eff = bal['efluente_final']
        bal['eficiencias_totales'] = {
            'DBO5_pct': _eficiencia_pct(aff.get('DBO5_mg_L', 0), eff.get('DBO5_mg_L', 0)),
            'DQO_pct': _eficiencia_pct(aff.get('DQO_mg_L', 0), eff.get('DQO_mg_L', 0)),
            'SST_pct': _eficiencia_pct(aff.get('SST_mg_L', 0), eff.get('SST_mg_L', 0)),
            'CF_pct': _eficiencia_pct(aff.get('CF_NMP_100mL', 0), eff.get('CF_NMP_100mL', 0)),
        }

    return bal


def _filas_balance_calidad(bal: Dict[str, Any]) -> Tuple[str, str]:
    """Genera encabezados y filas de la tabla de balance de calidad."""
    columnas: List[Tuple[str, str]] = [('Afluente', 'afluente')]
    orden_etapas = [
        ('Post-UASB', 'tras_uasb', 'eficiencias_uasb'),
        ('Post-ABR', 'tras_abr', 'eficiencias_abr'),
        ('Post-Hum', 'tras_humedal', 'eficiencias_humedal'),
        ('Post-FP', 'tras_fp', 'eficiencias_fp'),
        ('Post-Sed', 'tras_sed', 'eficiencias_sed'),
        ('Post-BAF', 'tras_baf', 'eficiencias_baf'),
        ('Post-TAF', 'tras_taf', 'eficiencias_taf'),
    ]
    for titulo, key, ef_key in orden_etapas:
        if key in bal:
            columnas.append((titulo, ef_key))
    columnas.append(('Efluente', 'eficiencias_totales'))

    headers = " & ".join([f"\\textbf{{{t}}}" for t, _ in columnas]) + " \\\\"

    params = [
        ('DBO$_5$ (mg/L)', 'DBO5_mg_L', '.1f'),
        ('DQO (mg/L)', 'DQO_mg_L', '.1f'),
        ('SST (mg/L)', 'SST_mg_L', '.1f'),
        ('CF (NMP/100mL)', 'CF_NMP_100mL', '.0f'),
    ]

    filas_datos = []
    for titulo_param, key_param, fmt in params:
        valores = []
        for _, ef_key in columnas:
            if ef_key == 'afluente':
                val = bal.get('afluente', {}).get(key_param, 0)
                valores.append(f"{val:{fmt}}")
            elif ef_key == 'eficiencias_totales':
                val = bal.get('efluente_final', {}).get(key_param, 0)
                valores.append(f"{val:{fmt}}")
            else:
                val = bal.get(ef_key, {}).get(key_param.replace('5_mg_L', '5_pct').replace('_mg_L', '_pct').replace('_NMP_100mL', '_pct'), 0)
                valores.append(f"{val:.0f}\\%")
        filas_datos.append(f"{titulo_param} & {' & '.join(valores)} \\\\")

    return headers, "\n".join(filas_datos)


def generar_resumen_resultados(cfg, resultados, balance_calidad=None, area_m2=None) -> str:
    """Genera seccion final con resumen ejecutivo de todos los resultados"""

    r = resultados

    # Si no se pasa balance_calidad, intentar armarlo desde resultados
    if balance_calidad is None:
        bal = _armar_balance_calidad(r)
    else:
        bal = balance_calidad

    afluente = bal.get('afluente', {})
    efluente = bal.get('efluente_final', {})

    # Calcular area total del predio (dinamico)
    if area_m2 is None:
        raise ValueError("area_m2 es requerida para generar el resumen de resultados")
    area_tratamiento = area_m2
    area_amortiguacion = area_tratamiento * cfg.layout_factor_amortiguacion
    area_complementaria = area_tratamiento * cfg.layout_factor_complementaria
    area_total_calc = (area_tratamiento + area_amortiguacion + area_complementaria) / (1 - cfg.layout_factor_zona_verde)

    # Valores del efluente
    dbo_ef = efluente.get('DBO5_mg_L', 0)
    dqo_ef = efluente.get('DQO_mg_L', 0)
    sst_ef = efluente.get('SST_mg_L', 0)
    cf_ef = efluente.get('CF_NMP_100mL', 0)

    # Verificacion de cumplimiento para cada tabla TULSMA
    cumple_t12 = (dbo_ef <= cfg.DBO5_ef_mg_L and dqo_ef <= 250 and sst_ef <= cfg.SST_ef_mg_L and cf_ef <= cfg.CF_ef_NMP)
    cumple_t13 = (dbo_ef <= 100 and dqo_ef <= 250 and sst_ef <= 100 and cf_ef <= 3000)
    cumple_t11 = (dbo_ef <= 250 and dqo_ef <= 500 and sst_ef <= 220)
    cumple_t3_cf = cf_ef <= 200
    cumple_t6_cf = cf_ef <= 1000
    cumple_t9_cf = cf_ef <= 200
    cumple_t10_cf = cf_ef <= 2000
    cumple_t1 = (dbo_ef <= 2.0 and cf_ef <= 600)

    # Tabla de dimensionamiento dinámica
    filas_dim = _filas_dimensionamiento(r, cfg)

    # Tabla de balance dinámica
    headers_balance, filas_balance = _filas_balance_calidad(bal)

    # Lodos
    lecho = r.get('lecho_secado', {})
    desinf = r.get('cloro') or r.get('desinfeccion') or {}
    num_lineas = cfg.num_lineas

    # Filas de lodos dinámicas (usar desglose real si existe)
    desglose_lodos = r.get('_desglose_lodos') or lecho.get('desglose_lodos') or []
    filas_lodos_tabla = []
    for item in desglose_lodos:
        por_linea = item.get('kg_SST_d', 0) / max(num_lineas, 1)
        total = item.get('kg_SST_d', 0)
        nombre = item.get('nombre', item.get('origen', 'Producción de lodos'))
        filas_lodos_tabla.append(
            f"{nombre} & {por_linea:.2f} kg SST/d & {total:.2f} kg SST/d \\\\"
        )
    filas_lodos_str = "\n".join(filas_lodos_tabla)

    return rf"""
El presente resumen consolida los resultados del dimensionamiento de la Planta de Tratamiento de Aguas Residuales (PTAR) para un caudal de dise\~no de \textbf{{{cfg.Q_linea_L_s * num_lineas:.1f} L/s}} ({cfg.Q_linea_L_s:.1f} L/s por linea).

\subsection{{Parametros de Dise\~no}}

\begin{{table}}[H]
\centering
\caption{{Parametros de entrada del sistema}}
\begin{{tabular}}{{lc}}
\toprule
\textbf{{Parametro}} & \textbf{{Valor}} \\
\midrule
Caudal total (Q$_{{total}}$) & {cfg.Q_linea_L_s * num_lineas:.1f} L/s ({cfg.Q_linea_m3_d * num_lineas:.1f} m$^3$/d) \\
Caudal por línea (Q$_{{linea}}$) & {cfg.Q_linea_L_s:.1f} L/s ({cfg.Q_linea_m3_d:.1f} m$^3$/d) \\
DBO$_5$ afluente & {cfg.DBO5_mg_L:.1f} mg/L \\
DQO afluente & {cfg.DQO_mg_L:.1f} mg/L \\
SST afluente & {cfg.SST_mg_L:.1f} mg/L \\
Temperatura & {cfg.T_agua_C:.1f} °C \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Dimensionamiento de Unidades}}

\begin{{table}}[H]
\centering
\caption{{Resumen de unidades de tratamiento}}
\small
\begin{{tabular}}{{p{{3.2cm}}p{{3.5cm}}p{{1.5cm}}p{{4.8cm}}}}
\toprule
\textbf{{Unidad}} & \textbf{{Dimensiones (m)}} & \textbf{{Cantidad}} & \textbf{{Parametro Clave}} \\
\midrule
{filas_dim}
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Balance de Calidad del Agua}}

\begin{{table}}[H]
\centering
\caption{{Evolucion de parametros de calidad a traves del tratamiento}}
\begin{{tabular}}{{l{'c' * len([c for c in _filas_balance_calidad(bal)[0].split('&')])}}}
\toprule
{headers_balance}
\midrule
{filas_balance}
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Verificacion de Cumplimiento TULSMA}}

\textbf{{Efluente calculado:}} DBO$_5$ = {dbo_ef:.1f} mg/L | DQO = {dqo_ef:.1f} mg/L | SST = {sst_ef:.1f} mg/L | CF = {cf_ef:.0f} NMP/100mL

\vspace{{0.5em}}
\begin{{table}}[H]
\centering
\small
\caption{{Comparacion con limites TULSMA por uso del agua}}
\begin{{tabular}}{{lcccccc}}
\toprule
\textbf{{Uso / Tabla TULSMA}} & \textbf{{DBO$_5$}} & \textbf{{DQO}} & \textbf{{SST}} & \textbf{{CF}} & \textbf{{Dictamen}} \\
& \textbf{{(limite)}} & \textbf{{(limite)}} & \textbf{{(limite)}} & \textbf{{(limite)}} & \\
\midrule
Agua dulce -- Tabla 12 & $\leq${cfg.DBO5_ef_mg_L:.0f} & $\leq$250 & $\leq${cfg.SST_ef_mg_L:.0f} & $\leq${cfg.CF_ef_NMP:.0f} & {'CUMPLE' if cumple_t12 else 'NO CUMPLE'} \\
Agua marina -- Tabla 13 & $\leq$100 & $\leq$250 & $\leq$100 & $\leq$3000 & {'CUMPLE' if cumple_t13 else 'NO CUMPLE'} \\
Alcantarillado -- Tabla 11 & $\leq$250 & $\leq$500 & $\leq$220 & --- & {'CUMPLE' if cumple_t11 else 'NO CUMPLE'} \\
Flora y fauna -- Tabla 3 & --- & --- & --- & $\leq$200 & {'CUMPLE' if cumple_t3_cf else 'NO CUMPLE'} \\
Agricola/riego -- Tabla 6 & --- & --- & --- & $\leq$1000 & {'CUMPLE' if cumple_t6_cf else 'NO CUMPLE'} \\
Pecuario -- Tabla 7 & --- & --- & --- & $\leq$1000 & {'CUMPLE' if cumple_t6_cf else 'NO CUMPLE'} \\
Recreativo primario -- Tabla 9 & --- & --- & --- & $\leq$200 & {'CUMPLE' if cumple_t9_cf else 'NO CUMPLE'} \\
Recreativo secundario -- Tabla 10 & --- & --- & --- & $\leq$2000 & {'CUMPLE' if cumple_t10_cf else 'NO CUMPLE'} \\
Consumo humano trat. conv. -- Tabla 1 & $\leq$2.0 & --- & --- & $\leq$600 & {'CUMPLE' if cumple_t1 else 'NO CUMPLE'} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Requerimientos de Terreno}}

\begin{{table}}[H]
\centering
\caption{{Resumen de areas requeridas}}
\begin{{tabular}}{{lc}}
\toprule
\textbf{{Concepto}} & \textbf{{Area}} \\
\midrule
Area de tratamiento & {area_m2:.0f} m$^2$ \\
Area de amortiguacion ({cfg.layout_factor_amortiguacion*100:.0f}\%) & {area_m2 * cfg.layout_factor_amortiguacion:.0f} m$^2$ \\
Area complementaria operativa & {area_m2 * cfg.layout_factor_complementaria:.0f} m$^2$ ({cfg.layout_factor_complementaria*100:.0f}\% estimado) \\
Zona verde ({cfg.layout_factor_zona_verde*100:.0f}\% del total) & {area_total_calc * cfg.layout_factor_zona_verde:.0f} m$^2$ \\
\midrule
\textbf{{Area total requerida}} & \textbf{{{area_total_calc:.0f} m$^2$ ({(area_total_calc/10000):.2f} ha)}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Produccion de Lodos}}

\begin{{table}}[H]
\centering
\caption{{Generacion y manejo de lodos - TOTAL PLANTA ({num_lineas} líneas)}}
\begin{{tabular}}{{p{{6cm}}cc}}
\toprule
\textbf{{Concepto}} & \textbf{{Por línea}} & \textbf{{Total planta}} \\
\midrule
{filas_lodos_str}
\midrule
\textbf{{Total lodos}} & \textbf{{{lecho.get('lodos_total_kg_d_por_linea', lecho.get('lodos_total_kg_d', 0)/max(num_lineas,1)):.2f} kg SST/d}} & \textbf{{{lecho.get('lodos_total_kg_d', 0):.2f} kg SST/d}} \\
Area de lechos de secado & --- & {lecho.get('A_total_m2', 0):.1f} m$^2$ ({num_lineas} bloques) \\
Frecuencia de aplicacion & --- & 1 vez cada 3--4 meses \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Consumos Estimados}}

\begin{{table}}[H]
\centering
\caption{{Consumos de energia y productos quimicos}}
\begin{{tabular}}{{lcc}}
\toprule
\textbf{{Concepto}} & \textbf{{Consumo}} & \textbf{{Unidad}} \\
\midrule
Potencia electrica estimada & 5--8 & kW \\
Consumo energia & 40,000--60,000 & kWh/a\~no \\
Hipoclorito de sodio ({desinf.get('concentracion_NaOCl_pct', 10):.0f}\%) & {desinf.get('volumen_NaOCl_L_d', 0):.1f} & L/d \\
Consumo hipoclorito anual & {desinf.get('volumen_NaOCl_L_d', 0) * 365 / 1000:.0f} & m$^3$/a\~no \\
\bottomrule
\end{{tabular}}
\end{{table}}

"""


if __name__ == "__main__":
    """
    Test simple del módulo reporte_resultados.
    """
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ptar_dimensionamiento import ConfigDiseno

    print("=" * 60)
    print("TEST reporte_resultados.py")
    print("=" * 60)

    cfg = ConfigDiseno()
    cfg.Q_linea_L_s = 5.7
    cfg.num_lineas = 3

    layout_info_test = {
        'fig_path': 'resultados/mis_trenes/figuras/Layout_test_3lineas.png',
        'area_layout_m2': 7651.0,
        'ancho_total_m': 96.6,
        'largo_total_m': 79.2,
        'caption': r'\textbf{1}=Rejillas; \textbf{2}=Desarenador; \textbf{3}=UASB; \textbf{4}=Humedal Vertical; \textbf{5}=Desinfección; \textbf{6}=Lecho de Secado.',
    }

    latex_out = generar_latex_seccion_layout(cfg, layout_info_test)
    print(f"Layout generado: {len(latex_out)} caracteres")

    resultados_test = {
        'rejillas': {'ancho_layout_m': 0.6, 'h_tirante_m': 0.4, 'v_canal_adoptada_m_s': 0.50},
        'desarenador': {'b_canal_m': 0.6, 'L_diseno_m': 3.0, 'H_util_m': 0.4, 't_r_real_s': 40.0},
        'uasb': {'D_m': 8.1, 'H_total_construccion_m': 6.0, 'v_up_m_h': 0.80},
        'cloro': {'largo_m': 8.0, 'ancho_m': 2.0, 'h_total_m': 2.3, 'CT_mg_min_L': 30, 'concentracion_NaOCl_pct': 10, 'volumen_NaOCl_L_d': 15.0},
        'lecho_secado': {'largo_m': 6.0, 'ancho_m': 2.0, 'A_bloque_m2': 12.0, 'A_total_m2': 36.0, 'lodos_total_kg_d': 10.6, 'lodos_uasb_kg_d': 10.6, 'lodos_fp_kg_d': 0.0},
        '_calidad_afluente': {'DBO5_mg_L': 250, 'DQO_mg_L': 500, 'SST_mg_L': 220, 'CF_NMP_100mL': 1e7},
        '_calidad_efluente': {'DBO5_mg_L': 60, 'DQO_mg_L': 140, 'SST_mg_L': 20, 'CF_NMP_100mL': 1},
    }

    resumen = generar_resumen_resultados(cfg, resultados_test, area_m2=7651.0)
    print(f"Resumen generado: {len(resumen)} caracteres")
    print("\n" + "=" * 60)
    print("Test completado OK")
    print("=" * 60)
