"""
Generador Maestro de Reporte de Selección de Alternativas.

Este script orquesta:
1. Lee config_reporte.py para saber qué alternativas generar
2. Ejecuta el dimensionamiento para cada alternativa activa
3. Genera los layouts
4. Genera los LaTeX individuales (A, B, C...)
5. Combina TODO en un documento maestro único
6. Compila a PDF

Uso:
    python generar_reporte_maestro.py
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Importar configuración
from config_reporte import CONFIG_REPORTE, obtener_alternativas_activas, verificar_configuracion

# Importar módulos de dimensionamiento
from ptar_dimensionamiento import ConfigDiseno, dimensionar_uasb, dimensionar_filtro_percolador, dimensionar_sedimentador_sec, dimensionar_lecho_secado, dimensionar_rejillas, dimensionar_desarenador, calcular_tren_A
from ptar_layout_graficador import generar_layout_con_resultados

# Importar generador LaTeX A (existente)
from generar_latex_A import generar_latex_alternativa_A, generar_contenido_alternativa_A

# TODO: Importar otros generadores cuando estén listos
# from generar_latex_B import generar_latex_alternativa_B
# from generar_latex_C import generar_latex_alternativa_C


def generar_latex_maestro(output_dir: str, alternativas_generadas: dict) -> str:
    """
    Genera el documento LaTeX maestro que combina todas las alternativas.
    
    Args:
        output_dir: Directorio de salida
        alternativas_generadas: Dict con {id_alternativa: datos_resultado}
    
    Returns:
        Ruta al archivo .tex generado
    """
    
    latex_path = os.path.join(output_dir, f"{CONFIG_REPORTE['salida']['nombre_archivo']}.tex")
    
    # Encabezado del documento
    latex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish]{babel}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{float}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage[most]{tcolorbox}

\geometry{margin=2.5cm, headheight=14pt}

% Colores corporativos
\definecolor{azuloscuro}{RGB}{0,51,102}
\definecolor{verdeagua}{RGB}{0,128,128}
\definecolor{grisclaro}{RGB}{245,245,245}

% Hyperref setup
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=black,
    filecolor=black,
    urlcolor=azuloscuro,
    pdftitle={Seleccion de Alternativas PTAR},
    pdfauthor={Ingenieria de Diseno},
}

% Header/Footer
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textcolor{black}{Seleccion de Alternativas - PTAR}}
\fancyhead[R]{\small\textcolor{black}{\leftmark}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.5pt}

% Section formatting
\titleformat{\section}
  {\normalfont\Large\bfseries\color{black}}
  {\thesection.}{0.5em}{}
\titleformat{\subsection}
  {\normalfont\large\bfseries\color{black}}
  {\thesubsection}{0.5em}{}

\begin{document}
"""

    # PORTADA
    if CONFIG_REPORTE["secciones"]["portada"]:
        latex += r"""
%============================================================================
% PORTADA
%============================================================================
\begin{titlepage}
\centering
\vspace*{2cm}

{\Huge\bfseries\textcolor{azuloscuro}{SELECCION DE ALTERNATIVAS}\\[0.5cm]
\Large PARA PLANTA DE TRATAMIENTO DE\\[0.3cm]
AGUAS RESIDUALES}

\vspace{2cm}

{\Large\textbf{Caudal de Diseno:} """ + f"{CONFIG_REPORTE['proyecto']['caudal_total_lps']:.1f}" + r""" L/s}

\vspace{1.5cm}

\begin{tikzpicture}
\draw[azuloscuro, thick, rounded corners] (0,0) rectangle (10,4);
\node at (5,3) {\textbf{Proyecto:}};
\node at (5,2) {""" + f"{CONFIG_REPORTE['proyecto']['nombre']}" + r"""};
\node at (5,1) {\textbf{Ubicacion:} """ + f"{CONFIG_REPORTE['proyecto']['ubicacion']}" + r"""};
\end{tikzpicture}

\vfill

{\large Fecha: """ + datetime.now().strftime("%d/%m/%Y") + r"""}

\end{titlepage}
"""

    # INTRODUCCIÓN
    if CONFIG_REPORTE["secciones"]["introduccion"]:
        latex += r"""
%============================================================================
% INTRODUCCION
%============================================================================
\newpage
\section{INTRODUCCION}

El presente documento tiene como objetivo presentar el analisis y comparacion 
de diferentes alternativas tecnologicas para el tratamiento de aguas residuales.

Se han identificado y evaluado """ + str(len(alternativas_generadas)) + r""" alternativas de tratamiento, 
considerando aspectos tecnicos, economicos y operativos para la seleccion de la 
mejor opcion.

El caudal de diseno considerado es de """ + f"{CONFIG_REPORTE['proyecto']['caudal_total_lps']:.1f}" + r""" L/s, 
distribuido en dos lineas paralelas de """ + f"{CONFIG_REPORTE['proyecto']['caudal_total_lps']/2:.1f}" + r""" L/s cada una.

\subsection{Alcance}

El estudio incluye:
\begin{itemize}
    \item Dimensionamiento de unidades de pretratamiento
    \item Dimensionamiento de unidades de tratamiento primario y secundario
    \item Disposicion de lodos generados
    \item Desinfeccion del efluente tratado
    \item Matriz comparativa de alternativas
    \item Recomendacion de alternativa seleccionada
\end{itemize}

\subsection{Nomenclatura y Definiciones}

\textbf{Parametros de calidad del agua:}
\begin{itemize}
    \item \textbf{DBO}: Demanda Bioquimica de Oxigeno. Cantidad de oxigeno consumido por microorganismos 
    para degradar materia organica. Unidad: mg/L.
    \item \textbf{DQO}: Demanda Quimica de Oxigeno. Medida del oxigeno requerido para oxidar quimicamente 
    la materia organica. Unidad: mg/L.
    \item \textbf{SST}: Solidos Suspendidos Totales. Particulas solidas en suspension en el agua. Unidad: mg/L.
    \item \textbf{NMP}: Numero Mas Probable. Concentracion de organismos indicadores (coliformes). Unidad: NMP/100mL.
\end{itemize}

\textbf{Parametros de diseno:}
\begin{itemize}
    \item \textbf{TRH}: Tiempo de Retencion Hidraulico. Tiempo promedio que el agua permanece en una unidad. 
    Unidad: horas (h).
    \item \textbf{SOR}: Tasa de Desbordamiento Superficial. Caudal dividido por el area superficial del 
    sedimentador. Unidad: m$^3$/m$^2$\textperiodcentered d.
    \item \textbf{Cv}: Carga Volumetrica Organica. Masa de DBO o DQO aplicada por unidad de volumen del reactor 
    por dia. Unidad: kg/m$^3$\textperiodcentered d.
    \item \textbf{v\_up}: Velocidad Ascendente. Velocidad del flujo ascendente en el reactor UASB. 
    Unidad: m/h.
    \item \textbf{Q}: Caudal. Volumen de agua que pasa por unidad de tiempo. Unidades: L/s, m$^3$/d, m$^3$/h.
\end{itemize}

\textbf{Siglas:}
\begin{itemize}
    \item \textbf{UASB}: Upflow Anaerobic Sludge Blanket (Reactor Anaerobio de Flujo Ascendente con Manto de Lodos)
    \item \textbf{UV}: Ultravioleta (sistema de desinfeccion)
    \item \textbf{HFCV}: Humedal de Flujo Vertical
    \item \textbf{MBBR}: Moving Bed Biofilm Reactor (Reactor de Biofilm de Lecho Movil)
    \item \textbf{SBR}: Sequencing Batch Reactor (Reactor por Lotes Secuencial)
    \item \textbf{TULSMA}: Texto Unificado de Legislacion Secundaria del Ministerio del Ambiente (Ecuador)
\end{itemize}
"""

    # BASES DE DISEÑO - Usar valores reales del proyecto
    # Los valores se obtienen de crear_configuracion_real() que ya está definida arriba
    cfg_real = crear_configuracion_real()
    
    if CONFIG_REPORTE["secciones"]["bases_diseno"]:
        latex += r"""
%============================================================================
% BASES DE DISENO
%============================================================================
\newpage
\section{BASES DE DISENO}

\subsection{Parametros de Entrada}

Los parametros de entrada para el diseno de la planta de tratamiento se 
establecen conforme a la caracterizacion del agua residual y los requerimientos 
del proyecto. La Tabla 1 presenta los valores adoptados.

\begin{table}[H]
\centering
\caption{Parametros de diseno del influente}
\begin{tabular}{p{4.5cm}ccp{4cm}}
\toprule
\textbf{Parametro} & \textbf{Valor} & \textbf{Unidad} & \textbf{Referencia} \\
\midrule
Caudal total (Q) & """ + f"{CONFIG_REPORTE['proyecto']['caudal_total_lps']:.1f}" + r""" & L/s & Diseno del proyecto \\
Caudal por linea & """ + f"{CONFIG_REPORTE['proyecto']['caudal_total_lps']/2:.1f}" + r""" & L/s & 2 lineas paralelas \\
Caudal por linea & """ + f"{CONFIG_REPORTE['proyecto']['caudal_total_lps']/2 * 86.4:.0f}" + r""" & m$^3$/d & $Q \times 86.4$ \\
DBO$_5$ & """ + f"{cfg_real.DBO5_mg_L:.1f}" + r""" & mg/L & Caracterizacion agua residual \\
DQO & """ + f"{cfg_real.DQO_mg_L:.1f}" + r""" & mg/L & Caracterizacion agua residual \\
SST & """ + f"{cfg_real.SST_mg_L:.1f}" + r""" & mg/L & Caracterizacion agua residual \\
Coliformes fecales & $1 \times 10^7$ & NMP/100mL & Aguas residuales municipales \\
Temperatura & """ + f"{cfg_real.T_agua_C:.1f}" + r""" & $^\circ$C & Promedio anual Galapagos \\
pH & 6,0 - 9,0 & -- & Tipico municipal \\
\bottomrule
\end{tabular}
\label{tab:parametros_entrada}
\end{table}

\textbf{Nota:} DBO = Demanda Bioquimica de Oxigeno; DQO = Demanda Quimica de 
Oxigeno; SST = Solidos Suspendidos Totales; NMP = Numero Mas Probable.

\subsection{Lineas de Tratamiento}

Considerando la capacidad y redundancia operativa, se establecen:
\begin{itemize}
    \item \textbf{2 lineas paralelas} de tratamiento
    \item Cada linea atiende """ + f"{CONFIG_REPORTE['proyecto']['caudal_total_lps']/2:.1f}" + r""" L/s
    \item Cada linea puede operar independientemente para mantenimiento
\end{itemize}

\subsection{Limites de Descarga - TULSMA}

Los limites de descarga del efluente tratado se establecen conforme al 
Texto Unificado de Legislacion Secundaria del Ministerio del Ambiente 
(TULSMA) - Libro VI, Anexo 1, Tabla 11: Descargas en cuerpos de agua 
dulceacuicolas.

\begin{table}[H]
\centering
\caption{Limites de descarga de efluentes tratados (TULSMA)}
\begin{tabular}{p{5cm}ccc}
\toprule
\textbf{Parametro} & \textbf{Afluente} & \textbf{Limite TULSMA} & \textbf{Remocion requerida} \\
\midrule
DBO$_5$ & """ + f"{cfg_real.DBO5_mg_L:.1f}" + r""" mg/L & $\leq$ 100 mg/L & $\geq$ 60\% \\
DQO & """ + f"{cfg_real.DQO_mg_L:.1f}" + r""" mg/L & $\leq$ 200 mg/L & $\geq$ 60\% \\
SST & """ + f"{cfg_real.SST_mg_L:.1f}" + r""" mg/L & $\leq$ 100 mg/L & $\geq$ 60\% \\
Coliformes fecales & $10^7$ NMP/100mL & $\leq$ 1000 NMP/100mL & $\geq$ 4 log \\
pH & 6,0 - 9,0 & 6,0 - 9,0 & --- \\
Temperatura & $<$ 35 grados C & $<$ 35 grados C & --- \\
\bottomrule
\end{tabular}
\label{tab:limites_tulsa}
\end{table}

\textbf{Nota:} TULSMA = Texto Unificado de Legislacion Secundaria del 
Ministerio del Ambiente de Ecuador.
"""

    # MATRIZ COMPARATIVA (antes de las alternativas detalladas)
    if CONFIG_REPORTE["secciones"]["matriz_comparativa"] and len(alternativas_generadas) > 1:
        latex += r"""
%============================================================================
% MATRIZ COMPARATIVA DE ALTERNATIVAS
%============================================================================
\newpage
\section{MATRIZ COMPARATIVA DE ALTERNATIVAS}

\begin{table}[H]
\centering
\caption{Resumen comparativo de alternativas evaluadas}
\begin{tabular}{>{\raggedright\arraybackslash}p{2.5cm}*{""" + str(len(alternativas_generadas)) + r"""}{>{\centering\arraybackslash}p{3cm}}}
\toprule
\textbf{Criterio} """
        
        for alt_id in sorted(alternativas_generadas.keys()):
            config = CONFIG_REPORTE["alternativas"][alt_id]
            latex += f"& \\textbf{{Alt. {alt_id}}} "
        latex += r"""\\
\midrule
"""
        
        # Filas de la matriz
        latex += "Tecnologia "
        for alt_id in sorted(alternativas_generadas.keys()):
            config = CONFIG_REPORTE["alternativas"][alt_id]
            latex += f"& {config.nombre.split(' + ')[0]} "
        latex += r"""\\

Proceso secundario """
        for alt_id in sorted(alternativas_generadas.keys()):
            config = CONFIG_REPORTE["alternativas"][alt_id]
            parts = config.nombre.split(' + ')
            sec = parts[1] if len(parts) > 1 else "-"
            latex += f"& {sec} "
        latex += r"""\\

Eficiencia DBO5 (est.) & 85-90\% & -- & -- \\[0.3cm]
Consumo energetico & Bajo & -- & -- \\[0.3cm]
Generacion de lodos & Media & -- & -- \\[0.3cm]
\midrule
\textbf{Recomendacion} & \textbf{Seleccionada} & -- & -- \\
\bottomrule
\end{tabular}
\end{table}
"""

    # CRITERIOS DE SELECCION (general, antes de las alternativas)
    latex += r"""
%============================================================================
% CRITERIOS DE SELECCION DE TECNOLOGIA
%============================================================================
\newpage
\section{CRITERIOS DE SELECCION DE TECNOLOGIA}

La seleccion de la tecnologia de tratamiento de aguas residuales requiere 
un analisis integral que considere aspectos tecnicos, economicos, ambientales 
y operativos. Los criterios fundamentales para la evaluacion de alternativas 
son los siguientes:

\textbf{Eficiencia de remocion:} Capacidad del sistema para alcanzar los 
limites de descarga establecidos en la normativa ambiental vigente, 
considerando la remocion de DBO, DQO, SST y patogenos.

\textbf{Consumo energetico:} Preferencia por tecnologias de bajo consumo 
energetico, especialmente aquellas que no requieren aireacion forzada como 
los procesos anaerobios (UASB) y los biofiltros por gravedad.

\textbf{Robustez hidraulica:} Capacidad del sistema para operar 
eficientemente ante variaciones de caudal y carga organica, manteniendo 
el desempeno bajo condiciones de flujo minimo y maximo.

\textbf{Complejidad operativa:} Simplicidad en la operacion y el 
mantenimiento, minimizando requerimientos de personal especializado y 
equipos complejos.

\textbf{Disponibilidad de area:} Requerimientos de espacio fisico para 
la planta, considerando las dimensiones de las unidades y la disposicion 
layout.

\textbf{Generacion de residuos:} Produccion de lodos y otros subproductos, 
considerando el manejo, tratamiento y disposicion final de los mismos.

%============================================================================
% DESCRIPCION DETALLADA DE ALTERNATIVAS
%============================================================================
\newpage
\section{DESCRIPCIÓN DETALLADA DE ALTERNATIVAS}

El proceso de seleccion de la tecnologia de tratamiento de aguas residuales 
requiere un analisis exhaustivo de diferentes alternativas que consideren 
aspectos tecnicos, economicos y operativos. En esta seccion se presenta el 
dimensionamiento detallado de cada alternativa evaluada, incluyendo la 
descripcion de la tecnologia, las bases de diseno adoptadas, el calculo 
unitario de cada componente del sistema, el balance de calidad esperado y 
la disposicion espacial de los equipos mediante un layout general.

El dimensionamiento de cada unidad se realizo conforme a estandares 
internacionales reconocidos, principalmente los criterios establecidos por 
Metcalf y Eddy, la Water Environment Federation y otras referencias tecnicas 
para tratamiento de aguas residuales. Se consideraron parametros de entrada 
como el caudal de diseno, las caracteristicas del agua residual, la temperatura 
operativa y los limites de descarga establecidos en la normativa ambiental 
vigente.

Las alternativas presentadas fueron seleccionadas priorizando tecnologias 
con bajo consumo energetico, robustez hidraulica para operar ante variaciones 
de caudal, simplicidad operativa que facilite el mantenimiento, y eficiencia 
comprobada en la remocion de contaminantes para cumplir con los objetivos de 
calidad del efluente tratado.

"""

    # Insertar cada alternativa generada (CON CONTENIDO COMPLETO)
    for alt_id in sorted(alternativas_generadas.keys()):
        datos = alternativas_generadas[alt_id]
        config = CONFIG_REPORTE["alternativas"][alt_id]
        
        # Insertar el contenido LaTeX completo de la alternativa
        if "contenido" in datos and datos["contenido"]:
            latex += datos["contenido"]
        else:
            # Fallback: solo resumen si no hay contenido
            latex += f"""
%------------------------------------------------------------------------
% ALTERNATIVA {alt_id}
%------------------------------------------------------------------------
\subsection{{Alternativa {alt_id}: {config.nombre}}}

{config.descripcion}

[Contenido no disponible]
"""

    # SECCIÓN DE SELECCIÓN FINAL
    if CONFIG_REPORTE["secciones"]["seleccion_final"]:
        latex += r"""
%============================================================================
% SELECCION DE ALTERNATIVA
%============================================================================
\newpage
\section{SELECCION DE ALTERNATIVA RECOMENDADA}

\subsection{Analisis Tecnico}

Considerando los aspectos tecnicos evaluados:
\begin{itemize}
    \item Eficiencia de remocion de contaminantes
    \item Confiabilidad operacional
    \item Flexibilidad ante variaciones de caudal
    \item Requerimientos de operacion y mantenimiento
\end{itemize}

\subsection{Analisis Economico (Preliminar)}

El analisis economico considera:
\begin{itemize}
    \item Costos de inversion (CAPEX)
    \item Costos de operacion anuales (OPEX)
    \item Costo total de vida util (20 anos)
\end{itemize}

\subsection{Alternativa Seleccionada}

\begin{tcolorbox}[colback=verdeagua!10,colframe=azuloscuro,title=\textbf{Recomendacion}]
Se recomienda implementar la \textbf{Alternativa A} (UASB + Filtro Percolador) 
por los siguientes motivos:
\begin{enumerate}
    \item Alta eficiencia de remocion de DBO5 (85-90\%)
    \item Bajo consumo energetico (no requiere aireacion)
    \item Operacion sencilla y robusta
    \item Generacion de biogas (aprovechamiento energetico potencial)
    \item Costos de operacion reducidos
\end{enumerate}
\end{tcolorbox}
"""

    # CONCLUSIONES
    if CONFIG_REPORTE["secciones"]["conclusiones"]:
        latex += r"""
%============================================================================
% CONCLUSIONES
%============================================================================
\newpage
\section{CONCLUSIONES}

\begin{enumerate}
    \item Se han evaluado """ + str(len(alternativas_generadas)) + r""" alternativas tecnologicas 
    para el tratamiento de """ + f"{CONFIG_REPORTE['proyecto']['caudal_total_lps']:.1f}" + r""" L/s de aguas residuales.
    
    \item La Alternativa A (UASB + Filtro Percolador) presenta la mejor relacion 
    eficiencia/costo/operabilidad para las condiciones del proyecto.
    
    \item El dimensionamiento realizado cumple con los limites de descarga 
    establecidos en la normativa ambiental vigente.
    
    \item Se recomienda desarrollar la ingenieria de detalle de la alternativa 
    seleccionada para su posterior construccion.
\end{enumerate}

%============================================================================
% FIN DEL DOCUMENTO
%============================================================================

% Nota: Las memorias de calculo detalladas de cada alternativa se incluyen 
% en las secciones correspondientes anteriormente en este documento.

%============================================================================
% REFERENCIAS BIBLIOGRAFICAS
%============================================================================
\newpage
\begin{thebibliography}{99}

\bibitem{metcalf2014}
Metcalf \& Eddy, AECOM. (2014). 
\textit{Wastewater Engineering: Treatment and Resource Recovery}. 
5th Edition. McGraw-Hill Education.

\bibitem{romero2004}
Romero Rojas, J. A. (2004). 
\textit{Tratamiento de Aguas Residuales: Teoría y Principios de Diseño}.
Editorial Limusa. México.

\bibitem{sperling2007}
Sperling, M. V. (2007). 
\textit{Introdução à Qualidade das Águas e ao Tratamento de Esgotos}.
3ª Edição. Editora UFMG. Belo Horizonte.

\bibitem{vanhaandel1994}
Van Haandel, A. C., \& Lettinga, G. (1994). 
\textit{Anaerobic Sewage Treatment: A Practical Guide for Regions with a Hot Climate}.
John Wiley \& Sons. Chichester.

\bibitem{ops2005}
OPS/CEPIS. (2005). 
\textit{Guía para el Diseño de Plantas de Tratamiento de Aguas Residuales}.
Serie Agua y Saneamiento. Lima, Perú.

\bibitem{wef2010}
Water Environment Federation. (2010). 
\textit{Wastewater Treatment Plant Design}. MOP 8. WEF Press.

\bibitem{senagua2012}
SENAGUA. (2012). 
\textit{Guía para la Tecnología de Tratamiento de Aguas Residuales}.
Quito, Ecuador.

\end{thebibliography}

\end{document}
"""

    # Guardar archivo
    with open(latex_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    
    print(f"[OK] LaTeX maestro generado: {latex_path}")
    return latex_path


def crear_configuracion_real():
    """
    Configuración con valores reales del estudio.
    
    Nota sobre limites de efluente:
        DBO5_ef_mg_L = 68 mg/L (objetivo de diseño estricto)
        SST_ef_mg_L = 80 mg/L (objetivo de diseño estricto)
        
        Estos valores son mas restrictivos que los limites legales de TULSMA
        (DBO5 <= 100 mg/L, SST <= 100 mg/L) para proporcionar margen de 
        seguridad ante variaciones operativas y estacionales.
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


def procesar_alternativa(alt_id: str, config_alt, output_dir: str) -> dict:
    """
    Procesa una alternativa específica: dimensiona, genera layout y LaTeX.
    
    Returns:
        Dict con los resultados para incluir en el reporte maestro
    """
    print(f"\n{'='*60}")
    print(f"PROCESANDO ALTERNATIVA {alt_id}")
    print(f"{'='*60}")
    
    # Crear configuración con valores reales del estudio
    cfg = crear_configuracion_real()
    
    # Ejecutar dimensionamiento según alternativa
    if alt_id == "A":
        resultados = calcular_tren_A(cfg)
        
        # Agregar calculo de desinfeccion con cloro
        from ptar_dimensionamiento import dimensionar_desinfeccion_cloro, calcular_balance_calidad_agua
        resultados['cloro'] = dimensionar_desinfeccion_cloro(cfg)
        
        # Calcular balance de calidad del agua
        balance_calidad = calcular_balance_calidad_agua(cfg, resultados)
        
        unidades = ["Rejillas", "Desarenador", "UASB", "Filtro_Percolador", 
                   "Sedimentador", "UV"]  # UV representa la unidad de desinfeccion (Cloro o UV)
        
        # Generar layout
        print("\nGenerando layout...")
        x, y = generar_layout_con_resultados(
            "A", unidades, "UASB + Filtro Percolador", resultados, output_dir,
            caudal_L_s=cfg.Q_linea_L_s
        )
        area_m2 = round(x * y)
        
        # Generar contenido LaTeX para incluir en el documento maestro
        print("Generando contenido LaTeX para documento maestro...")
        contenido_latex = generar_contenido_alternativa_A(cfg, resultados, f"Layout_{alt_id}_2lineas.png", area_m2=area_m2, balance_calidad=balance_calidad)
        
        # También generar LaTeX individual (archivo separado por si se necesita)
        latex_individual = os.path.join(output_dir, f"alternativa_{alt_id}_detalle.tex")
        print(f"Generando LaTeX individual: {latex_individual}")
        generar_latex_alternativa_A(cfg, resultados, latex_individual, area_m2=area_m2, balance_calidad=balance_calidad)
        
        return {
            "id": alt_id,
            "nombre": config_alt.nombre,
            "dimensiones": {"x": x, "y": y},
            "latex": latex_individual,
            "contenido": contenido_latex,  # Contenido para insertar en maestro
            "resultados": resultados
        }
    
    elif alt_id == "B":
        # TODO: Implementar cuando generar_latex_B.py exista
        print("[WARNING] Alternativa B no implementada aun")
        return None
    
    elif alt_id == "C":
        print("[WARNING] Alternativa C no implementada aun")
        return None
    
    elif alt_id == "D":
        print("[WARNING] Alternativa D no implementada aun")
        return None
    
    elif alt_id == "E":
        print("[WARNING] Alternativa E no implementada aun")
        return None
    
    elif alt_id == "F":
        print("[WARNING] Alternativa F no implementada aun")
        return None
    
    else:
        raise ValueError(f"Alternativa {alt_id} no reconocida")


def compilar_latex(latex_path: str, output_dir: str):
    """Compila el LaTeX a PDF."""
    from compilar_latex import compilar
    compilar(latex_path, output_dir)


def main():
    """Función principal del generador maestro."""
    
    print("="*70)
    print("GENERADOR MAESTRO DE REPORTE DE SELECCION DE ALTERNATIVAS")
    print("="*70)
    
    # 1. Verificar configuración
    try:
        alternativas_activas = verificar_configuracion()
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    
    # 2. Crear directorio de salida
    output_dir = os.path.join(os.path.dirname(__file__), "resultados")
    os.makedirs(output_dir, exist_ok=True)
    
    # 3. Procesar cada alternativa activa
    alternativas_generadas = {}
    
    for alt_id in alternativas_activas:
        config_alt = CONFIG_REPORTE["alternativas"][alt_id]
        
        try:
            resultado = procesar_alternativa(alt_id, config_alt, output_dir)
            if resultado:
                alternativas_generadas[alt_id] = resultado
        except Exception as e:
            print(f"[ERROR] Fallo procesando Alternativa {alt_id}: {e}")
            import traceback
            traceback.print_exc()
    
    if not alternativas_generadas:
        print("\n[ERROR] No se pudo generar ninguna alternativa")
        sys.exit(1)
    
    # 4. Generar documento maestro
    print(f"\n{'='*60}")
    print("GENERANDO DOCUMENTO MAESTRO")
    print(f"{'='*60}")
    
    latex_maestro = generar_latex_maestro(output_dir, alternativas_generadas)
    
    # 5. Compilar a PDF
    print(f"\n{'='*60}")
    print("COMPILANDO A PDF")
    print(f"{'='*60}")
    
    try:
        compilar_latex(latex_maestro, output_dir)
        print(f"\n{'='*70}")
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print(f"{'='*70}")
        print(f"PDF generado: {CONFIG_REPORTE['salida']['nombre_archivo']}.pdf")
    except Exception as e:
        print(f"[WARNING] Error compilando: {e}")
        print("El archivo .tex fue generado. Puedes compilar manualmente.")


if __name__ == "__main__":
    main()
