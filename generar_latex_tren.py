#!/usr/bin/env python3
"""
GENERADOR LATEX TREN - Generador de documentos LaTeX para trenes individuales

Genera un documento LaTeX completo para UN tren de tratamiento, sin depender
de alternativas fijas A/B/C.

Uso:
    from ptar_tren_config import get_tren_piloto_humedal, TrenConfig
    from generar_latex_tren import generar_documento_tren
    
    entrada = get_tren_piloto_humedal()
    config = TrenConfig.from_dict(entrada)
    
    generar_documento_tren(
        config_tren=config,
        output_dir="resultados/trenes"
    )
"""

import os
import sys
from typing import Dict, Any, Optional
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ptar_tren_config import TrenConfig, UNIDADES_SOPORTADAS
from ptar_tren_integrador import integrar_tren
from ptar_tren_layout import generar_layout_tren
from ptar_tren_predio import calcular_areas_predio, generar_tabla_areas_latex

# Importar generadores LaTeX existentes
from latex_unidades.rejillas import GeneradorRejillas
from latex_unidades.desarenador import GeneradorDesarenador
from latex_unidades.uasb import GeneradorUASB
from latex_unidades.abr_rap import GeneradorABR_RAP
from latex_unidades.filtro_percolador import GeneradorFiltroPercolador
from latex_unidades.humedal_vertical import GeneradorHumedalVertical
from latex_unidades.baf import GeneradorBAF
from latex_unidades.sedimentador_secundario import GeneradorSedimentadorSecundario
from latex_unidades.cloro import GeneradorCloro
from latex_unidades.lecho_secado import GeneradorLechoSecado

# Mapeo de códigos a generadores LaTeX
GENERADORES_LATEX = {
    "rejillas": GeneradorRejillas,
    "desarenador": GeneradorDesarenador,
    "uasb": GeneradorUASB,
    "abr": GeneradorABR_RAP,
    "filtro_percolador": GeneradorFiltroPercolador,
    "humedal_vertical": GeneradorHumedalVertical,
    "baf": GeneradorBAF,
    "sedimentador_secundario": GeneradorSedimentadorSecundario,
    "cloro": GeneradorCloro,
    "lecho_secado": GeneradorLechoSecado,
}


# =============================================================================
# PLANTILLA LATEX BASE
# =============================================================================

PLANTILLA_DOCUMENTO = r"""\documentclass[12pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[spanish]{{babel}}
\usepackage{{geometry}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{graphicx}}
\usepackage{{enumitem}}
\usepackage{{float}}
\usepackage{{xcolor}}
\usepackage{{hyperref}}
\usepackage{{fancyhdr}}

\geometry{{margin=2.5cm}}

\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{Memoria de Cálculo - {nombre_tren}}}
\fancyhead[R]{{\thepage}}

\title{{{titulo}}}
\author{{Diseño PTAR - Puerto Baquerizo Moreno}}
\date{{\today}}

\begin{{document}}

\maketitle

\section{{Descripción General}}

{nombre_tren} es un tren de tratamiento de aguas residuales configurado para un caudal de {caudal_total} L/s distribuido en {num_lineas} líneas de tratamiento paralelas ({caudal_linea} L/s por línea).

\textbf{{Características del afluente:}}
\begin{{itemize}}
    \item DBO$_5$: {dbo} mg/L
    \item DQO: {dqo} mg/L
    \item SST: {sst} mg/L
    \item Coliformes fecales: {cf:.0e} NMP/100mL
    \item Temperatura: {temp}°C
\end{{itemize}}

\textbf{{Secuencia de unidades:}}
{lista_unidades}

{seccion_dimensionamiento}

{seccion_layout}

{seccion_predio}

{seccion_resultados}

\end{{document}}
"""


# =============================================================================
# FUNCIONES DE GENERACIÓN
# =============================================================================

def generar_seccion_dimensionamiento(
    resultado_integracion: Dict[str, Any],
    config_tren: TrenConfig
) -> str:
    """Genera la sección de dimensionamiento de unidades."""
    
    secciones = []
    secciones.append(r"\section{Dimensionamiento de Unidades}")
    secciones.append(r"\label{sec:dimensionamiento}")
    secciones.append("")
    
    # Generar cada unidad
    for codigo_unidad in config_tren.unidades:
        if codigo_unidad not in resultado_integracion["unidades"]:
            secciones.append(f"\\subsection{{{codigo_unidad}}}")
            secciones.append("Unidad no dimensionada.\\")
            secciones.append("")
            continue
        
        if codigo_unidad not in GENERADORES_LATEX:
            secciones.append(f"\\subsection{{{codigo_unidad}}}")
            secciones.append("Generador LaTeX no disponible.\\")
            secciones.append("")
            continue
        
        try:
            # Crear generador
            generador_class = GENERADORES_LATEX[codigo_unidad]
            
            # Obtener datos de la unidad
            datos_unidad = resultado_integracion["unidades"][codigo_unidad]
            
            # Crear instancia del generador
            # Necesitamos adaptar los datos al formato que espera cada generador
            from ptar_dimensionamiento import ConfigDiseno
            cfg = ConfigDiseno()
            
            generador = generador_class(cfg, datos_unidad)
            
            # Generar contenido LaTeX
            latex_unidad = generador.generar_completo()
            secciones.append(latex_unidad)
            secciones.append("")
            
        except Exception as e:
            secciones.append(f"\\subsection{{{codigo_unidad}}}")
            secciones.append(f"Error generando LaTeX: {e}\\")
            secciones.append("")
    
    return "\n".join(secciones)


def generar_seccion_layout(layout_resultado: Dict[str, Any]) -> str:
    """Genera la sección de layout del tren."""
    
    secciones = []
    secciones.append(r"\section{Disposición de la Planta}")
    secciones.append(r"\label{sec:layout}")
    secciones.append("")
    
    # Incluir figura de layout
    ruta_figura = layout_resultado.get("ruta_imagen", "")
    if ruta_figura:
        # Ruta relativa al documento
        ruta_relativa = os.path.basename(ruta_figura)
        
        secciones.append(r"\begin{figure}[H]")
        secciones.append(r"\centering")
        secciones.append(f"\\includegraphics[width=0.95\\textwidth]{{{ruta_relativa}}}")
        secciones.append(r"\caption{Layout general del tren de tratamiento}")
        secciones.append(r"\label{fig:layout_tren}")
        secciones.append(r"\end{figure}")
        secciones.append("")
    
    # Información de dimensiones
    dims = layout_resultado.get("dimensiones", {})
    secciones.append(f"El layout del tren ocupa un área aproximada de {dims.get('ancho_m', 0):.1f} m × {dims.get('alto_m', 0):.1f} m ({dims.get('area_m2', 0):.1f} m²).")
    secciones.append("")
    
    return "\n".join(secciones)


def generar_seccion_predio(areas_predio: Dict[str, Any]) -> str:
    """Genera la sección de áreas de predio."""
    
    secciones = []
    secciones.append(r"\section{Disposición de la Planta y Áreas de Predio}")
    secciones.append(r"\label{sec:predio}")
    secciones.append("")
    
    secciones.append("El área total del predio se ha calculado considerando las áreas de tratamiento, las áreas complementarias necesarias para operación y mantenimiento, y las zonas de expansión futura.")
    secciones.append("")
    
    # Tabla de áreas
    tabla = generar_tabla_areas_latex(areas_predio)
    secciones.append(tabla)
    secciones.append("")
    
    return "\n".join(secciones)


def generar_seccion_resultados(
    resultado_integracion: Dict[str, Any],
    config_tren: TrenConfig
) -> str:
    """Genera la sección de resultados."""
    
    secciones = []
    secciones.append(r"\section{Resultados}")
    secciones.append(r"\label{sec:resultados}")
    secciones.append("")
    
    # Balance de calidad
    balance = resultado_integracion.get("balance_calidad", {})
    eficiencias = balance.get("eficiencias_globales", {})
    cumplimiento = balance.get("cumplimiento_TULSMA", {})
    
    secciones.append(r"\subsection{Balance de Calidad}")
    secciones.append("")
    
    # Tabla de calidad
    secciones.append(r"\begin{table}[H]")
    secciones.append(r"\centering")
    secciones.append(r"\caption{Balance de calidad del agua}")
    secciones.append(r"\begin{tabular}{lcccc}")
    secciones.append(r"\toprule")
    secciones.append(r"\textbf{Parámetro} & \textbf{Afluente} & \textbf{Efluente} & \textbf{Eficiencia} & \textbf{Cumple} \\")
    secciones.append(r"\midrule")
    
    afluente = balance.get("afluente", {})
    efluente = balance.get("efluente", {})
    
    secciones.append(f"DBO$_5$ (mg/L) & {afluente.get('DBO5_mg_L', 0):.0f} & {efluente.get('DBO5_mg_L', 0):.0f} & {eficiencias.get('DBO5_pct', 0):.1f}\\% & {'Sí' if cumplimiento.get('DBO5') else 'No'} \\\\")
    secciones.append(f"SST (mg/L) & {afluente.get('SST_mg_L', 0):.0f} & {efluente.get('SST_mg_L', 0):.0f} & {eficiencias.get('SST_pct', 0):.1f}\\% & {'Sí' if cumplimiento.get('SST') else 'No'} \\\\")
    secciones.append(f"CF (NMP/100mL) & {afluente.get('CF_NMP', 0):.0e} & {efluente.get('CF_NMP', 0):.0e} & {eficiencias.get('CF_pct', 0):.1f}\\% & {'Sí' if cumplimiento.get('CF') else 'No'} \\\\")
    
    secciones.append(r"\bottomrule")
    secciones.append(r"\end{tabular}")
    secciones.append(r"\end{table}")
    secciones.append("")
    
    # Consumos
    consumos = resultado_integracion.get("consumos", {})
    secciones.append(r"\subsection{Consumos Estimados}")
    secciones.append("")
    secciones.append(r"\begin{itemize}")
    secciones.append(f"    \\item Energía eléctrica: {consumos.get('energia_total_kW', 0):.2f} kW ({consumos.get('energia_total_kWh_d', 0):.1f} kWh/día)")
    if consumos.get('cloro_total_kg_d', 0) > 0:
        secciones.append(f"    \\item Cloro: {consumos.get('cloro_total_kg_d', 0):.2f} kg/día")
    secciones.append(r"\end{itemize}")
    secciones.append("")
    
    return "\n".join(secciones)


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def generar_documento_tren(
    config_tren: TrenConfig,
    output_dir: str = "resultados/trenes",
    nombre_archivo: Optional[str] = None,
    compilar_pdf: bool = True
) -> Dict[str, str]:
    """
    Genera un documento LaTeX completo para un tren.
    
    Args:
        config_tren: Configuración del tren
        output_dir: Directorio de salida
        nombre_archivo: Nombre base del archivo (sin extensión)
        compilar_pdf: Si True, intenta compilar el PDF
        
    Returns:
        Dict con rutas de archivos generados
    """
    print(f"\n[Generador LaTeX] Generando documento para: {config_tren.nombre_tren}")
    
    # Crear directorios
    os.makedirs(output_dir, exist_ok=True)
    figuras_dir = os.path.join(output_dir, "figuras")
    os.makedirs(figuras_dir, exist_ok=True)
    
    # Integrar tren
    print("  1. Integrando tren...")
    resultado_integracion = integrar_tren(config_tren)
    
    # Generar layout
    print("  2. Generando layout...")
    layout_resultado = generar_layout_tren(
        unidades=config_tren.unidades,
        resultados=resultado_integracion["unidades"],
        num_lineas=config_tren.num_lineas,
        output_dir=figuras_dir,
        nombre_archivo="layout_tren.png"
    )
    
    # Calcular áreas
    print("  3. Calculando áreas...")
    areas_predio = calcular_areas_predio(
        area_tratamiento_m2=layout_resultado["dimensiones"]["area_m2"],
        num_unidades=len(config_tren.unidades),
        config_tren=config_tren
    )
    
    # Generar secciones LaTeX
    print("  4. Generando secciones LaTeX...")
    
    # Sección de dimensionamiento (simplificada por ahora)
    # NOTA: La integración completa con todos los módulos LaTeX requiere
    # más trabajo de adaptación. Para el piloto, generamos un resumen.
    seccion_dimensionamiento = r"\section{Dimensionamiento de Unidades}\label{sec:dimensionamiento}" + "\n\n"
    seccion_dimensionamiento += "Se han dimensionado las siguientes unidades:\\[0.5em]\n\n"
    seccion_dimensionamiento += r"\begin{itemize}" + "\n"
    for codigo in config_tren.unidades:
        info = UNIDADES_SOPORTADAS.get(codigo, {})
        nombre = info.get("nombre_display", codigo)
        seccion_dimensionamiento += f"    \\item {nombre}\n"
    seccion_dimensionamiento += r"\end{itemize}" + "\n\n"
    seccion_dimensionamiento += "Los detalles de cada unidad se encuentran en la sección correspondiente."
    
    # Sección de layout
    seccion_layout = generar_seccion_layout(layout_resultado)
    
    # Sección de predio
    seccion_predio = generar_seccion_predio(areas_predio)
    
    # Sección de resultados
    seccion_resultados = generar_seccion_resultados(resultado_integracion, config_tren)
    
    # Completar plantilla
    print("  5. Completando plantilla...")
    
    afluente = config_tren.afluente
    
    documento = PLANTILLA_DOCUMENTO.format(
        nombre_tren=config_tren.nombre_tren,
        titulo=f"Memoria de Cálculo - {config_tren.nombre_tren}",
        caudal_total=config_tren.caudal_total_lps,
        num_lineas=config_tren.num_lineas,
        caudal_linea=config_tren.caudal_por_linea_lps,
        dbo=afluente.DBO5_mg_L,
        dqo=afluente.DQO_mg_L,
        sst=afluente.SST_mg_L,
        cf=afluente.CF_NMP_100mL,
        temp=afluente.temperatura_C,
        lista_unidades=r" \textrightarrow ".join([
            UNIDADES_SOPORTADAS.get(u, {}).get("nombre_display", u)
            for u in config_tren.unidades
        ]),
        seccion_dimensionamiento=seccion_dimensionamiento,
        seccion_layout=seccion_layout,
        seccion_predio=seccion_predio,
        seccion_resultados=seccion_resultados,
    )
    
    # Guardar archivo
    if nombre_archivo is None:
        nombre_archivo = config_tren.nombre_tren.lower().replace(" ", "_").replace("+", "_")
    
    tex_path = os.path.join(output_dir, f"{nombre_archivo}.tex")
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(documento)
    
    print(f"  Documento guardado: {tex_path}")
    
    resultado = {
        "tex_path": tex_path,
        "pdf_path": None,
    }
    
    # Compilar PDF
    if compilar_pdf:
        print("  6. Compilando PDF...")
        try:
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            pdf_path = os.path.join(output_dir, f"{nombre_archivo}.pdf")
            if os.path.exists(pdf_path):
                resultado["pdf_path"] = pdf_path
                print(f"  PDF generado: {pdf_path}")
        except Exception as e:
            print(f"  Error compilando PDF: {e}")
    
    return resultado


# =============================================================================
# MAIN - PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("GENERADOR LATEX TREN - Prueba de generación")
    print("=" * 60)
    
    from ptar_tren_config import get_tren_piloto_humedal, TrenConfig
    
    # Generar documento para tren piloto
    print("\n[1] Generando documento para tren piloto - Humedal:")
    entrada = get_tren_piloto_humedal()
    config = TrenConfig.from_dict(entrada)
    
    resultado = generar_documento_tren(
        config_tren=config,
        output_dir="resultados/trenes",
        nombre_archivo="tren_humedal_piloto",
        compilar_pdf=True
    )
    
    print(f"\n  Archivos generados:")
    print(f"    - LaTeX: {resultado['tex_path']}")
    if resultado['pdf_path']:
        print(f"    - PDF: {resultado['pdf_path']}")
    else:
        print(f"    - PDF: No generado (revisar errores)")
    
    print("\n" + "=" * 60)
    print("Generación completada")
    print("=" * 60)
