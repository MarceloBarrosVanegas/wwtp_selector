#!/usr/bin/env python3
"""
================================================================================
GENERADOR LaTeX PARA ALTERNATIVA C - MEMORIA COMPLETA ESTÁNDAR
================================================================================

Alternativa C: UASB + Humedal Vertical de Flujo Subsuperficial + Cloro

Estructura documental (formato estándar del proyecto):
- Cada unidad: 1.Descripción/Teoría → 2.Parámetros → 3.Dimensionamiento → 
              4.Verificación → 5.Resultados

Estrategia de reutilización desde A:
- _generar_bibliografia() → Importado desde generar_latex_A (extender para humedal)
- _generar_tikz_rejillas() → Importado desde generar_latex_A (misma unidad)
- Layout → Usa ptar_layout_graficador directamente (igual que A)

Contenido nuevo/nativo de C:
- Todas las secciones narrativas específicas de C
- Sección de Humedal Vertical (completa, es la unidad diferente)
- Balance de calidad adaptado (UASB→Humedal→Cloro)
- Lecho de secado adaptado (solo lodos UASB + humedal)

Autor: Generado automáticamente
Versión: Memoria completa estándar (reemplaza simplificado temporal)
================================================================================
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ==============================================================================
# IMPORTACIONES
# ==============================================================================

from ptar_dimensionamiento import ConfigDiseno

# Reutilización selectiva desde Alternativa A (solo helpers verificados)
from generar_latex_A import (
    _generar_bibliografia as _generar_biblio_base_A,
    _generar_tikz_rejillas,
)


# ==============================================================================
# SECCIÓN 0: BIBLIOGRAFÍA EXTENDIDA (base A + referencias humedal)
# ==============================================================================

def _generar_bibliografia_C(output_dir):
    """
    Genera archivo .bib con referencias para Alternativa C.
    
    Estrategia: Toma base de A y extiende con referencias específicas de humedal.
    """
    # Primero generar la base de A
    bib_path = _generar_biblio_base_A(output_dir)
    
    # Contenido adicional específico de humedal
    bib_humedal = r"""

%% Referencias adicionales para Humedal Vertical (Alternativa C)

@book{kadlec2009,
    author    = {Kadlec, R. H. and Wallace, S. D.},
    title     = {Treatment Wetlands},
    edition   = {2nd},
    publisher = {CRC Press},
    year      = {2009},
    address   = {Boca Raton, FL},
    isbn      = {978-1566705264}
}

@techreport{molle2015,
    author      = {Molle, P. and Lienard, A. and Grasmick, A.},
    title       = {Vertical Flow Constructed Wetlands: French Concept and Modelling},
    institution = {IRSTEA},
    year        = {2015},
    address     = {Montpellier, France},
    type        = {Technical Report}
}

@article{molle2006,
    author    = {Molle, P. and Lienard, A. and Boutin, C.},
    title     = {Constructed wetlands for wastewater treatment: A French perspective},
    journal   = {Water Science and Technology},
    volume    = {54},
    number    = {11--12},
    pages     = {55--62},
    year      = {2006},
    publisher = {IWA Publishing}
}

@book{cooper1996,
    author    = {Cooper, P. F. and Job, G. D. and Green, M. B. and Shutes, R. B. E.},
    title     = {Reed Beds and Constructed Wetlands for Wastewater Treatment},
    publisher = {WRc Publications},
    year      = {1996},
    address   = {Marlow, UK},
    isbn      = {978-1898920105}
}
"""
    
    # Leer archivo existente y agregar referencias humedal
    with open(bib_path, 'r', encoding='utf-8') as f:
        contenido_base = f.read()
    
    # Escribir contenido extendido
    with open(bib_path, 'w', encoding='utf-8') as f:
        f.write(contenido_base + bib_humedal)
    
    return bib_path


# ==============================================================================
# PLANTILLA BASE DEL DOCUMENTO (estructura estándar)
# ==============================================================================

def _generar_preambulo_documento():
    """Genera el preámbulo LaTeX común para Alternativa C."""
    return r"""\documentclass[12pt,a4paper]{article}

% =============================================================================
% PAQUETES
% =============================================================================
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish]{babel}
\usepackage{amsmath,amssymb}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{multirow}
\usepackage{float}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage[numbers]{natbib}

% Geometría de página
\geometry{margin=2.5cm,top=2.5cm,bottom=2.5cm}

% Colores institucionales
\definecolor{azulagua}{RGB}{0,102,153}
\definecolor{verdehmedal}{RGB}{34,139,34}

% Encabezados
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small Memoria de Cálculo -- PTAR San Cristóbal}
\fancyhead[R]{\small Alternativa C}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% Formato de secciones
\titleformat{\section}{\Large\bfseries\color{azulagua}}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{\thesubsubsection}{1em}{}

% TikZ libraries
\usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc, patterns, decorations.pathmorphing}

% Comando para ecuaciones con caption
\newcommand{\captionequation}[1]{%
    \vspace{0.3em}%
    \textit{\small #1}%
    \vspace{0.5em}%
}

\begin{document}

% =============================================================================
% PORTADA
% =============================================================================
\begin{titlepage}
\centering
\vspace*{2cm}

{\Huge\bfseries\color{azulagua} Memoria de Cálculo}\\[0.5cm]
{\LARGE Alternativa C}\\[0.3cm]
{\Large Sistema UASB + Humedal Vertical + Desinfección}\\[2cm]

\rule{\textwidth}{1.5pt}\\[0.5cm]
{\Large\bfseries Planta de Tratamiento de Aguas Residuales}\\[0.3cm]
{\large San Cristóbal -- Galápagos}\\[0.5cm]
\rule{\textwidth}{1.5pt}\\[2cm]

\vfill

{\large Documento generado automáticamente}\\[0.3cm]
{\large \today}

\end{titlepage}

% =============================================================================
% ÍNDICE
% =============================================================================
\tableofcontents
\newpage

% =============================================================================
% 1. INTRODUCCIÓN Y MARCO TEÓRICO
% =============================================================================
\section{Introducción y Marco Teórico}

\subsection{Descripción del Sistema de Tratamiento}

La Alternativa C propone un sistema de tratamiento de aguas residuales 
compuesto por tres etapas principales:

\begin{enumerate}
    \item \textbf{Tratamiento Primario Anaerobio:} Reactor UASB (Upflow Anaerobic 
    Sludge Blanket) que remueve la materia orgánica biodegradable mediante 
    digestión anaerobia.
    
    \item \textbf{Tratamiento Secundario Aerobio:} Humedal Artificial de Flujo 
    Vertical Subsuperficial (HAFV) que complementa la remoción de materia orgánica 
    y sólidos suspendidos.
    
    \item \textbf{Desinfección:} Cloración con hipoclorito de sodio para reducir 
    la carga microbiológica antes del vertido.
\end{enumerate}

Este sistema es particularmente adecuado para climas tropicales cálidos 
(temperatura del agua $>$ 20°C) y contextos donde se dispone de área suficiente 
para el humedal.

\subsection{Principios de Funcionamiento}

\subsubsection{Reactor UASB}

El reactor UASB opera con flujo ascendente a través de un manto de lodos 
anaerobios granulares. La materia orgánica es convertida en biogás (principalmente 
metano y dióxido de carbono) y biomasa. El diseño incorpora un separador 
gas-líquido-sólido (GLS) en la parte superior para retener la biomasa y 
permitir la salida del efluente clarificado.

\subsubsection{Humedal Vertical de Flujo Subsuperficial}

El humedal construido de flujo vertical (HAFV) opera mediante pulsos 
intermitentes de agua residual sobre un lecho filtrante permeable. El agua 
percola verticalmente a través de la grava mientras el oxígeno del aire 
difunde hacia el lecho, creando condiciones aerobias que favorecen la 
degradación de la materia orgánica remanente.

\textbf{Nota metodológica sobre selección del sistema:} El manual de diseño 
considera dos variantes del HAFV: el Sistema Clásico (Cooper et al., 1996) 
y el Sistema Francés Tropical (Molle et al., 2005). Para este proyecto se 
adopta el Sistema Francés Tropical, dado el contexto climático (tropical 
cálido) y la disponibilidad de área. La decisión sigue los criterios de 
selección del manual, traducidos implementablemente en una regla simplificada 
de puntuación que valora el área disponible y la capacitación operativa.

\subsubsection{Desinfección con Hipoclorito de Sodio}

La cloración es el método más común de desinfección en plantas de tratamiento 
de pequeña y mediana escala. El hipoclorito de sodio (NaOCl) reacciona con 
los microorganismos patógenos inactivándolos, permitiendo cumplir con los 
límites de descarga establecidos en la normativa ambiental.

\newpage
"""


def _generar_cierre_documento():
    """Genera el cierre del documento LaTeX (bibliografía y end)."""
    return r"""
% =============================================================================
% BIBLIOGRAFÍA
% =============================================================================
\newpage
\bibliographystyle{plain}
\bibliography{referencias}

\end{document}
"""


# ==============================================================================
# SECCIONES POR UNIDAD (PLACEHOLDERS - SE COMPLETAN EN PASOS SIGUIENTES)
# ==============================================================================

def _seccion_rejillas(cfg, resultados):
    """
    SECCIÓN 2.1: REJILLAS
    
    Formato estándar:
    1. Descripción general y teoría general
    2. Parámetros de diseño
    3. Componente - dimensionamiento
    4. Componente - verificación
    5. Resultados
    
    TODO: Completar en PASO 3
    """
    r = resultados.get('rejillas', {})
    largo = r.get('largo_layout_m', 0)
    velocidad = r.get('v_m_s', 0)
    return (
        r"""
% =============================================================================
\subsection{Canal de Desbaste con Rejillas}

\textbf{[PLACEHOLDER SECCIÓN COMPLETA]}

Esta sección se completará en el PASO 3 con:
\begin{enumerate}
    \item Descripción general y teoría general del desbaste
    \item Parámetros de diseño (tabla con valores adoptados)
    \item Dimensionamiento del canal y rejillas
    \item Verificación hidráulica
    \item Resultados del dimensionamiento
\end{enumerate}

Valores preliminares: Largo = """ + f"{largo:.1f}" + r""" m, 
Velocidad = """ + f"{velocidad:.2f}" + r""" m/s.

""")


def _seccion_desarenador(cfg, resultados):
    """
    SECCIÓN 2.2: DESARENADOR
    
    TODO: Completar en PASO 4
    """
    d = resultados.get('desarenador', {})
    largo = d.get('L_diseno_m', 0)
    return (
        r"""
% =============================================================================
\subsection{Desarenador de Flujo Horizontal}

\textbf{[PLACEHOLDER SECCIÓN COMPLETA]}

Esta sección se completará en el PASO 4 con la memoria completa del desarenador.

Valores preliminares: Largo = """ + f"{largo:.1f}" + r""" m.

""")


def _seccion_uasb(cfg, resultados):
    """
    SECCIÓN 2.3: REACTOR UASB
    
    TODO: Completar en PASO 5
    """
    u = resultados.get('uasb', {})
    diametro = u.get('D_m', 0)
    altura = u.get('H_total_m', 0)
    return (
        r"""
% =============================================================================
\subsection{Reactor UASB}

\textbf{[PLACEHOLDER SECCIÓN COMPLETA]}

Esta sección se completará en el PASO 5 con la memoria completa del UASB,
incluyendo:
\begin{enumerate}
    \item Descripción general y teoría del proceso anaerobio
    \item Parámetros de diseño (tabla)
    \item Dimensionamiento zona de reacción
    \item Dimensionamiento cámara de sedimentación
    \item Verificación hidráulica (arrastre del manto)
    \item Verificación sedimentación
    \item Resultados completos
\end{enumerate}

Valores preliminares: Diámetro = """ + f"{diametro:.1f}" + r""" m, 
Altura = """ + f"{altura:.1f}" + r""" m.

""")


def _seccion_humedal(cfg, resultados):
    """
    SECCIÓN 2.4: HUMEDAL VERTICAL (CRÍTICA)
    
    TODO: Completar en PASO 6
    Esta es la sección más importante y diferente de Alternativa C.
    """
    h = resultados.get('humedal', {})
    area = h.get('A_total_m2', 0)
    filtros = h.get('num_filtros', 0)
    return (
        r"""
% =============================================================================
\subsection{Humedal Vertical de Flujo Subsuperficial}

\textbf{[PLACEHOLDER SECCIÓN CRÍTICA]}

Esta sección se completará en el PASO 6 con la memoria completa del humedal,
reflejando el manual actualizado y la selección del sistema adoptado.

Contenido obligatorio:
\begin{enumerate}
    \item \textbf{Descripción general y teoría:}
    \begin{itemize}
        \item Teoría de humedales construidos
        \item Sistema Clásico (Cooper et al., 1996) vs Sistema Francés Tropical (Molle et al., 2005)
        \item \textbf{Selección del sistema para San Cristóbal:} explicar criterios A2
        \item Sistema adoptado: Francés Tropical (Ruta B) con justificación
        \item \textbf{Nota metodológica:} la regla implementada 2/2 criterios afectivos 
              es una simplificación traducida del manual, no una formulación literal.
    \end{itemize}
    
    \item \textbf{Parámetros de diseño:} Tabla con valores Ruta B (Molle et al.)
    
    \item \textbf{Dimensionamiento:}
    \begin{itemize}
        \item Cálculo de área según carga orgánica (OLR)
        \item Cálculo según carga hidráulica (HLR)
        \item Número de filtros y ciclo alimentación/reposo
        \item Geometría del filtro
    \end{itemize}
    
    \item \textbf{Verificación:}
    \begin{itemize}
        \item Modelo k-C* (verificación secundaria obligatoria)
        \item DBO calculada vs objetivo
        \item Verificación HLR máximo
    \end{itemize}
    
    \item \textbf{Resultados:} Tabla resumen dimensiones y esquema de ciclos
\end{enumerate}

Valores preliminares: Área total = """ + f"{area:.0f}" + r""" m$^2$, 
Filtros = """ + f"{filtros}" + r""".

""")


def _seccion_desinfeccion(cfg, resultados):
    """
    SECCIÓN 2.5: DESINFECCIÓN
    
    TODO: Completar en PASO 7
    """
    c = resultados.get('desinfeccion', {})
    ct = c.get('CT_mg_min_L', 0)
    return (
        r"""
% =============================================================================
\subsection{Desinfección con Hipoclorito de Sodio}

\textbf{[PLACEHOLDER SECCIÓN COMPLETA]}

Esta sección se completará en el PASO 7 con la memoria completa de desinfección.

Valores preliminares: CT = """ + f"{ct:.1f}" + r""" mg min/L.

""")


def _seccion_lecho_secado(cfg, resultados):
    """
    SECCIÓN 2.6: LECHO DE SECADO
    
    TODO: Completar en PASO 8
    """
    l = resultados.get('lecho_secado', {})
    area = l.get('A_total_m2', 0)
    return (
        r"""
% =============================================================================
\subsection{Lecho de Secado de Lodos}

\textbf{[PLACEHOLDER SECCIÓN COMPLETA]}

Esta sección se completará en el PASO 8 con la memoria completa del lecho.

Diferencia clave con Alternativa A: Solo lodos del UASB y humedal 
(sin humus de filtro percolador).

Valores preliminares: Area total = """ + f"{area:.1f}" + r""" m$^2$.

""")


def _seccion_disposicion_planta(cfg, resultados, area_m2, layout_filename):
    """
    SECCIÓN 3: DISPOSICIÓN DE PLANTA Y ÁREAS
    
    TODO: Completar en PASO 9
    """
    return (
        r"""
% =============================================================================
\newpage
\section{Disposición de la Planta y Áreas}

\textbf{[PLACEHOLDER SECCIÓN COMPLETA]}

Esta sección se completará en el PASO 9 con:
\begin{itemize}
    \item Layout de planta (figura)
    \item Área de tratamiento calculada
    \item Áreas complementarias requeridas
    \item Cálculo del área total del predio
\end{itemize}

\textit{Layout: """ + layout_filename + r"""}
\textit{Área estimada: """ + str(area_m2) + r""" m²}

""")


def _seccion_resultados_cumplimiento(cfg, resultados, balance_calidad, area_m2):
    """
    SECCIÓN 4: RESULTADOS Y CUMPLIMIENTO
    
    TODO: Completar en PASO 9
    """
    return r"""
% =============================================================================
\newpage
\section{Resultados y Cumplimiento}

\textbf{[PLACEHOLDER SECCIÓN COMPLETA]}

Esta sección se completará en el PASO 9 con:
\begin{enumerate}
    \item Tabla resumen de parámetros de diseño
    \item Tabla resumen de dimensionamiento de unidades
    \item Balance de calidad del agua (UASB → Humedal → Cloro)
    \item Verificación de cumplimiento TULSMA
    \item Requerimientos de terreno
    \item Producción de lodos (UASB + humedal)
    \item Consumos estimados
\end{enumerate}

\textit{Esta sección es específica de Alternativa C y se adapta del esquema de A.}

"""


# ==============================================================================
# ORQUESTADOR PRINCIPAL (BASE COMPLETA)
# ==============================================================================

def generar_latex_alternativa_C_completa(cfg, resultados, output_path, 
                                          area_m2=None, balance_calidad=None):
    """
    Genera archivo LaTeX COMPLETO para Alternativa C (memoria estándar).
    
    Esta función orquesta el documento completo siguiendo el formato estándar
    del proyecto: cada unidad con sus 5 secciones (Descripción, Parámetros,
    Dimensionamiento, Verificación, Resultados).
    
    Args:
        cfg: Configuración de diseño
        resultados: Diccionario con resultados de dimensionamiento
        output_path: Ruta del archivo .tex a generar
        area_m2: Área total calculada (opcional, se recalcula si es None)
        balance_calidad: Balance de calidad del agua (opcional)
    
    Returns:
        Ruta del archivo generado
    """
    from ptar_layout_graficador import generar_layout_con_resultados
    import os
    
    output_dir = os.path.dirname(output_path) or '.'
    
    # ==================================================================
    # GENERAR LAYOUT AUTOMÁTICAMENTE (igual que A)
    # ==================================================================
    unidades = ["Rejillas", "Desarenador", "UASB", "Humedal_Vertical", 
                "Desinfeccion"]
    
    print("Generando layout para Alternativa C...")
    try:
        x, y = generar_layout_con_resultados(
            "C", unidades, "UASB + Humedal Vertical + Cloro", resultados, output_dir,
            caudal_L_s=cfg.Q_linea_L_s
        )
        area_m2 = round(x * y)
        layout_filename = "Layout_C_2lineas.png"
        print(f"  Layout generado: {layout_filename} ({x:.1f}m x {y:.1f}m)")
    except Exception as e:
        print(f"  [ADVERTENCIA] No se pudo generar layout: {e}")
        layout_filename = "Layout_C_2lineas.png"
        if area_m2 is None:
            area_m2 = 1600  # Valor estimado por defecto
    
    # ==================================================================
    # CONSTRUIR DOCUMENTO COMPLETO
    # ==================================================================
    
    # 1. Preambulo y sección introductoria
    contenido = _generar_preambulo_documento()
    
    # 2. Sección 2: Diseño de Unidades (con placeholders por completar)
    contenido += r"\section{Diseño de Unidades de Tratamiento}" + "\n"
    contenido += r"\label{sec:unidades}" + "\n\n"
    
    contenido += _seccion_rejillas(cfg, resultados)
    contenido += _seccion_desarenador(cfg, resultados)
    contenido += _seccion_uasb(cfg, resultados)
    contenido += _seccion_humedal(cfg, resultados)
    contenido += _seccion_desinfeccion(cfg, resultados)
    contenido += _seccion_lecho_secado(cfg, resultados)
    
    # 3. Sección 3: Disposición de planta
    contenido += _seccion_disposicion_planta(cfg, resultados, area_m2, layout_filename)
    
    # 4. Sección 4: Resultados y cumplimiento
    contenido += _seccion_resultados_cumplimiento(cfg, resultados, balance_calidad, area_m2)
    
    # 5. Cierre del documento
    contenido += _generar_cierre_documento()
    
    # ==================================================================
    # ESCRIBIR ARCHIVO
    # ==================================================================
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"  Documento base completo generado: {output_path}")
    
    # ==================================================================
    # GENERAR BIBLIOGRAFÍA
    # ==================================================================
    try:
        bib_path = _generar_bibliografia_C(output_dir)
        print(f"  Bibliografía extendida generada: {bib_path}")
    except Exception as e:
        print(f"  [ADVERTENCIA] Error en bibliografía: {e}")
    
    return output_path


# ==============================================================================
# COMPATIBILIDAD HACIA ATRÁS (temporal)
# ==============================================================================

# Nota: El generador simplificado 'generar_latex_alternativa_C_simple()' 
# permanece en dimensionar_escogida.py como fallback temporal.
# 
# Este módulo (generar_latex_C.py) provee la versión completa estándar.
# Cuando todas las secciones estén completadas (PASOS 3-9), el orquestador
# en dimensionar_escogida.py deberá actualizarse para usar
# generar_latex_alternativa_C_completa() en lugar de _simple().


if __name__ == "__main__":
    print("=" * 70)
    print("GENERADOR LATEX ALTERNATIVA C - MEMORIA COMPLETA ESTÁNDAR")
    print("=" * 70)
    print()
    print("Este módulo debe ser importado y usado desde dimensionar_escogida.py")
    print("para generar la memoria completa de Alternativa C.")
    print()
    print("Función principal: generar_latex_alternativa_C_completa()")
    print()
    print("Estado actual: BASE CREADA (placeholders por unidad)")
    print("- PASO 3: Completar sección Rejillas")
    print("- PASO 4: Completar sección Desarenador")
    print("- PASO 5: Completar sección UASB")
    print("- PASO 6: Completar sección Humedal Vertical (crítica)")
    print("- PASO 7: Completar sección Desinfección")
    print("- PASO 8: Completar sección Lecho de Secado")
    print("- PASO 9: Completar Resultados/Cumplimiento")
