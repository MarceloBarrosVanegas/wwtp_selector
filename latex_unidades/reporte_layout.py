#!/usr/bin/env python3
"""
reporte_layout.py
=================
Módulo reutilizable para generar la sección LaTeX completa de
disposición de planta, layout y áreas de predio.

Se conecta directamente con la salida de ptar_layout_graficador.generar_layout()
y con los parámetros de ConfigDiseno de ptar_dimensionamiento.
"""

import os
import sys
from typing import Dict, Any


def calcular_areas_complementarias(cfg, area_tratamiento: float) -> Dict[str, Any]:
    """
    Calcula todas las áreas complementarias basadas en ConfigDiseno.

    Args:
        cfg: instancia de ConfigDiseno
        area_tratamiento: área de tratamiento en m²

    Returns:
        dict con desglose completo de áreas y totales.
    """
    area_amortiguacion = area_tratamiento * cfg.layout_factor_amortiguacion
    area_complementaria = area_tratamiento * cfg.layout_factor_complementaria
    area_caminos = area_tratamiento * cfg.layout_factor_caminos
    area_total = (area_tratamiento + area_amortiguacion + area_complementaria) / (1 - cfg.layout_factor_zona_verde)
    area_verde = area_total * cfg.layout_factor_zona_verde

    # Áreas mínimas vs proporcionales
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

    Args:
        cfg: instancia de ConfigDiseno
        layout_info: dict devuelto por generar_layout() con keys:
            - fig_path: ruta completa al PNG
            - area_layout_m2: float
            - ancho_total_m: float
            - largo_total_m: float
            - caption: str (caption de la figura)
        titulo_section: si True, usa \\section en vez de \\subsection para el título.

    Returns:
        str con código LaTeX listo para insertar.
    """
    area_m2 = float(layout_info.get('area_layout_m2', 0))
    fig_filename = os.path.basename(layout_info.get('fig_path', 'layout.png'))
    caption = layout_info.get('caption', 'Disposición espacial de unidades')
    ancho = layout_info.get('ancho_total_m', 0)
    largo = layout_info.get('largo_total_m', 0)
    lineas_texto = f"{cfg.num_lineas} línea{'s' if cfg.num_lineas > 1 else ''}"

    areas = calcular_areas_complementarias(cfg, area_m2)
    a = areas  # alias corto para el f-string

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


if __name__ == "__main__":
    """
    Test simple del módulo reporte_layout.
    Crea una ConfigDiseno de prueba y genera la sección LaTeX.
    """
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ptar_dimensionamiento import ConfigDiseno

    print("=" * 60)
    print("TEST reporte_layout.py")
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

    areas = calcular_areas_complementarias(cfg, layout_info_test['area_layout_m2'])
    print("\nÁreas calculadas:")
    for k, v in areas.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.1f} m²")

    latex_out = generar_latex_seccion_layout(cfg, layout_info_test)
    print(f"\nLongitud del bloque LaTeX generado: {len(latex_out)} caracteres")
    print("\n--- Primeras 10 líneas del LaTeX ---")
    print("\n".join(latex_out.splitlines()[:10]))
    print("\n--- Últimas 5 líneas del LaTeX ---")
    print("\n".join(latex_out.splitlines()[-5:]))
    print("\n" + "=" * 60)
    print("Test completado OK")
    print("=" * 60)
