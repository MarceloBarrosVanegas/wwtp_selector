#!/usr/bin/env python3
"""
Generador LaTeX para Sedimentador Secundario - Copia exacta de generar_latex_A.py lineas 1263-1428
Reorganizado en 3 subsections: Dimensionamiento, Verificacion, Resultados
"""

import os
import sys

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GeneradorSedimentadorSecundario:
    """Generador LaTeX para unidad Sedimentador Secundario - Copia exacta del original."""
    
    def __init__(self, cfg, datos, ruta_figuras='figuras'):
        self.cfg = cfg
        self.datos = datos
        self.ruta_figuras = ruta_figuras
    
    def generar_completo(self) -> str:
        """Genera todo el contenido LaTeX del sedimentador secundario en 3 subsections."""
        return "\n\n".join([
            self.generar_descripcion(),
            self.generar_verificacion(),
            self.generar_resultados()
        ])
    
    def generar_esquema_matplotlib(self, output_dir=None):
        """Genera esquema del sedimentador secundario usando la funcion existente."""
        sys.path.insert(0, _base_dir)
        from ptar_layout_graficador import generar_esquema_sedimentador_secundario

        if output_dir is None:
            output_dir = os.path.join(_base_dir, 'resultados', 'figuras')

        return generar_esquema_sedimentador_secundario(self.datos, output_dir)
    
    def generar_descripcion(self) -> str:
        """Genera subsection Dimensionamiento con toda la teoria y calculos."""
        cfg = self.cfg
        s = self.datos
        
        return rf"""\subsection{{Dimensionamiento}}

\textbf{{Fundamentos teóricos y principios de operación}}

El sedimentador secundario constituye una unidad de separación física por gravedad diseñada específicamente para remover los sólidos biológicos desprendidos de procesos de tratamiento aerobio previos. A diferencia de los sedimentadores primarios que remueven sólidos suspendidos en el agua cruda, el sedimentador secundario debe manejar flóculos biológicos activos (conocidos técnicamente como ``humus'' o lodos biológicos secundarios) que presentan características físicas y de sedimentación distintivas.

Los flóculos biológicos provenientes de filtros percoladores, MBBR o biofiltros aerados son agregados relativamente ligeros con densidades ligeramente superiores al agua, típicamente en el rango de 1,02--1,05 g/cm³, y velocidades de sedimentación que oscilan entre 0,3 y 1,2 m/h según Sperling \cite{{sperling2007}}. Estas partículas son susceptibles a la compactación y pueden re-suspenderse fácilmente si la velocidad ascensional del líquido excede ciertos límites críticos, lo que justifica el diseño conservador de estos tanques.

\textbf{{Densidad de flóculos y su relevancia en el diseño:}}

La densidad de los flóculos biológicos es un parámetro crítico que determina la velocidad de sedimentación y, consecuentemente, la eficiencia de separación en el sedimentador secundario. A diferencia de los sólidos minerales (arena, grava) que tienen densidades superiores a 2,5 g/cm³, los flóculos biológicos presentan:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item \textbf{{Densidad aparente:}} 1,02--1,05 g/cm³ (incluyendo agua intraflocular), solo ligeramente superior al agua (1,0 g/cm³).
    \item \textbf{{Densidad real de sólidos:}} 1,10--1,15 g/cm³ si se considera únicamente la materia seca de los microorganismos.
    \item \textbf{{Porosidad del flóculo:}} 90--95\% de agua embebida en la estructura del biofloc.
\end{{itemize}}

Esta baja diferencia de densidad (2--5\% respecto al agua) implica que la fuerza de flotación es casi igual al peso del flóculo, resultando en velocidades de sedimentación muy bajas. Por esta razón, el diseño del sedimentador secundario requiere:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item \textbf{{SOR conservadora:}} Valores de 16--32 m³/m²·d (equivalente a 0,67--1,33 m/h) que garanticen que la velocidad ascensional del líquido no supere la velocidad de caída de los flóculos.
    \item \textbf{{Tiempo de retención suficiente:}} Mínimo 1,5 horas para permitir que incluso los flóculos más pequeños sedimenten.
    \item \textbf{{Gradientes de velocidad bajos:}} Evitar turbulencias que puedan fragmentar los flóculos o mantenerlos en suspensión.
\end{{itemize}}

\textit{{Nota técnica:}} La densidad de los flóculos puede variar según la carga orgánica aplicada al sistema biológico previo. A mayor carga, los flóculos tienden a ser más livianos (mayor contenido de biomasa activa, menor densidad), requiriendo diseños más conservadores del sedimentador.

\textbf{{Mecanismos de sedimentación y transporte}}

El proceso de separación en el sedimentador secundario involucra cuatro mecanismos principales: (1) \textit{{sedimentación discreta}} de partículas individuales en la zona superior, (2) \textit{{sedimentación en floculación}} donde las partículas se agregan durante su descenso aumentando su velocidad de caída, (3) \textit{{compresión por estratificación}} en la zona de acumulación de lodos, y (4) \textit{{transporte por flujo laminar}} hacia el sistema de recolección de efluente clarificado.

El diseño geométrico del tanque debe asegurar un flujo hidrodinámico que minimice la turbulencia y los cortocircuitos hidráulicos. La relación diámetro/profundidad típica para sedimentadores circulares secundarios varía entre 1,5:1 y 4:1, según recomendaciones de Metcalf \& Eddy \cite{{metcalf2014}}. Un diseño más profundo favorece el almacenamiento de lodos y reduce el riesgo de re-suspensión por venteo, mientras que un diámetro mayor mejora la eficiencia de sedimentación al reducir la velocidad ascensional superficial.

\textbf{{Características del humus y requerimientos de almacenamiento}}

El humus o lodo biológico secundario acumulado en el fondo del sedimentador presenta una concentración típica de sólidos totales entre 2\% y 4\% en peso, con un índice de volumen de lodos (IVL) que puede variar significativamente según la carga orgánica aplicada al sistema biológico precedente. Según Sperling \cite{{sperling2007}}, el lodo de filtros percoladores presenta mejores características de sedimentación que el de lodos activados, con valores de IVL típicamente menores a 150 mL/g, lo que permite diseños más compactos.

La capacidad de almacenamiento de lodos debe dimensionarse considerando: (a) la producción diaria de humus estimada en 0,2--0,5 kg SST por kg de DBO₅ removida en el sistema biológico, (b) la frecuencia de purga programada (típicamente diaria o semanal según operación), y (c) un factor de seguridad del 25\% para manejar picos de producción de sólidos.

\textbf{{Criterios de diseño y parámetros fundamentales}}

El diseño del sedimentador secundario se fundamenta en tres criterios interrelacionados: (1) la \textit{{tasa de desbordamiento superficial}} (SOR) como parámetro de control de la sedimentación, (2) el \textit{{tiempo de retención hidráulico}} (TRH) como garantía de tiempo de contacto suficiente para la separación, y (3) la \textit{{carga sobre el vertedero perimetral}} como control del flujo de salida que evite arrastre de sólidos.

La SOR representa la velocidad ascensional teórica del líquido en el tanque y se calcula como el cociente entre el caudal y el área superficial neta. Para sedimentadores secundarios posteriores a procesos de biopelícula, Metcalf \& Eddy \cite{{metcalf2014}} establecen un rango operativo óptimo de 16--32 m³/m²·d para condiciones de caudal medio, con un límite máximo absoluto de 45 m³/m²·d durante picos horarios para evitar la re-suspensión del lodo sedimentado.

El TRH mínimo requerido es de 1,5 horas para garantizar que los flóculos biológicos tengan tiempo suficiente para sedimentar antes de ser arrastrados hacia el efluente. Valores superiores a 4 horas son aceptables y favorecen la clarificación, especialmente en climas tropicales donde las temperaturas elevadas pueden afectar la densidad del agua y los flóculos.

La carga sobre vertedero perimetral debe mantenerse por debajo de 250 m³/m·d para sedimentadores circulares secundarios, aunque valores más conservadores de 186 m³/m·d son recomendados por Sperling \cite{{sperling2007}} para sistemas de biopelícula, garantizando una velocidad de aproximación al vertedero suficientemente baja que no arrastre los sólidos sedimentados hacia el efluente clarificado.

\textbf{{Parámetros de diseño}}

\begin{{table}}[H]
\centering
\caption{{Parámetros de diseño del sedimentador secundario}}
\footnotesize
\setlength{{\tabcolsep}}{{3pt}}
\renewcommand{{\arraystretch}}{{1.18}}
\begin{{tabular}}{{@{{}}p{{0.25\textwidth}}p{{0.17\textwidth}}p{{0.25\textwidth}}p{{0.17\textwidth}}@{{}}}}
\toprule
\textbf{{Parámetro}} & \textbf{{Valor adoptado}} & \textbf{{Rango/Unidad}} & \textbf{{Fuente}} \\
\midrule
Caudal medio por línea (Q) & {s['Q_m3_d']:.1f} m³/d & – & – \\
Factor de pico horario ($f_p$) & {s['factor_pico']:.1f} & – & Metcalf \& Eddy \\
Caudal máximo horario ($Q_{{max}}$) & {s['Q_max_m3_d']:.1f} m³/d & – & – \\
Tasa de desbordamiento\newline superficial (SOR) & {s['SOR_m3_m2_d']:.1f} m³/m²·d & {s['SOR_min_m3_m2_d']:.0f}--{s['SOR_max_rango_m3_m2_d']:.0f} m³/m²·d & Metcalf \& Eddy \\\\
Profundidad lateral & {s['h_sed_m']:.2f} m & {s['h_sed_min_m']:.1f}--{s['h_sed_max_m']:.1f} m & Sperling \\
Tiempo de retención\newline hidráulico (HRT) & {s['TRH_h']:.1f} h & $\geq$ {s['TRH_min_criterio_h']:.1f} h & Metcalf \& Eddy \\\\
SOR máximo\newline permisible & {s['estado_sor_max']} & $\leq$ {s['SOR_max_limite']:.0f} m³/m²·d & Metcalf \& Eddy \\\\
Carga sobre vertedero\newline perimetral & {s['weir_loading_m3_m_d']:.1f} m³/m·d & $\leq$ {s['weir_loading_max']:.0f} m³/m·d & Metcalf \& Eddy \\\\
Zona de almacenamiento\newline de lodos & {s['h_lodos_tolva_m']:.2f} m (tolva) & – & Metcalf \& Eddy \\\\
Bordo libre & {s['bordo_libre_m']:.2f} m & – & Norma constructiva \\
\bottomrule
\end{{tabular}}
\end{{table}}

El diseño del sedimentador secundario se fundamenta en la tasa de desbordamiento superficial (SOR), que relaciona el caudal con el área superficial del tanque. Para sedimentadores secundarios ubicados después de procesos biológicos aerobios (como filtros percoladores, MBBR o biofiltros), Metcalf \& Eddy (2014) recomiendan valores de SOR entre {s['SOR_min_m3_m2_d']:.0f} y {s['SOR_max_rango_m3_m2_d']:.0f} m³/m²·d para operación normal, con un límite máximo de {s['SOR_max_limite']:.0f} m³/m²·d para condiciones de pico horario.

El tiempo de retención hidráulico (TRH) resultante del volumen del tanque debe ser al menos {s['TRH_min_criterio_h']:.1f} horas para garantizar la sedimentación efectiva de los sólidos biológicos. El valor calculado para este diseño es {s['TRH_h']:.1f} horas.

\textbf{{Carga Superficial -- Dimensionamiento}}

Según Metcalf \& Eddy \cite{{metcalf2014}}, el dimensionamiento de sedimentadores secundarios se fundamenta en la tasa de desbordamiento superficial (SOR), que representa la relación entre el caudal y el área superficial disponible para la sedimentación. Este parámetro garantiza que la velocidad ascensional del líquido sea suficientemente baja para permitir la decantación gravitacional de los flóculos biológicos. La ecuación fundamental es:

\begin{{equation}}
A_s = \frac{{Q}}{{SOR}}
\end{{equation}}
\captionequation{{Area superficial del sedimentador - Criterio SOR}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_s$] = Área superficial del sedimentador (m²)
    \item[$Q$] = Caudal diario ({s['Q_m3_d']:.1f} m³/d)
    \item[$SOR$] = Tasa de desbordamiento superficial ({s['SOR_m3_m2_d']:.1f} m³/m²·d)
\end{{itemize}}

\begin{{equation}}
A_s = \frac{{{s['Q_m3_d']:.1f}}}{{{s['SOR_m3_m2_d']:.1f}}} = {s['A_sup_m2']:.2f} \text{{ m}}^2
\end{{equation}}

Correspondiendo a un diámetro de {s['D_m']:.2f} m para configuración circular. La profundidad lateral de {s['h_sed_m']:.2f} m proporciona un volumen útil de {s['V_m3']:.1f} m³.

\textbf{{Desglose de altura total:}}

\begin{{table}}[H]
\centering
\small
\begin{{tabular}}{{lc}}
\toprule
Zona & Altura \\
\midrule
Zona de sedimentación (profundidad lateral) & {s['h_sed_m']:.2f} m \\
Zona de almacenamiento de lodos (tolva) & {s['h_lodos_tolva_m']:.2f} m \\
Bordo libre & {s['bordo_libre_m']:.2f} m \\
\midrule
\textbf{{Altura total de construcción}} & \textbf{{{s['altura_total_construccion_m']:.2f} m}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Vertedero Perimetral -- Dimensionamiento}}

El vertedero perimetral constituye el elemento de recolección del efluente clarificado. Su diseño debe garantizar una distribución uniforme del caudal perimetral para evitar zonas de acumulación o cortocircuito. Según Metcalf \& Eddy \cite{{metcalf2014}} y Sperling \cite{{sperling2007}}, la carga sobre el vertedero (weir loading) es un parámetro crítico que determina la uniformidad del flujo de salida. Para un sedimentador circular, el perímetro se calcula como:

\begin{{equation}}
P = \pi \times D = \pi \times {s['D_m']:.2f} = {s['perimetro_m']:.2f} \text{{ m}}
\end{{equation}}

La carga sobre el vertedero se calcula como:

\begin{{equation}}
q_{{\text{{vertedero}}}} = \frac{{Q}}{{P}} = \frac{{{s['Q_m3_d']:.1f}}}{{{s['perimetro_m']:.2f}}} = {s['weir_loading_m3_m_d']:.1f} \text{{ m}}^3\text{{/m·d}}
\end{{equation}}

\textbf{{Almacenamiento de Lodos -- Dimensionamiento}}

La producción de humus —sólidos biológicos desprendidos de la etapa biológica aerobia como resultado del control de espesor de la biopelícula— se estima siguiendo los criterios de Metcalf \& Eddy \cite{{metcalf2014}}. El factor de producción de {s['factor_produccion_humus']:.2f} kg SST por kg de DBO removida representa la fracción de sólidos generados en el proceso de oxidación biológica que deben ser separados en el sedimentador secundario. Este valor es característico de sistemas con biopelícula aerobia y permite estimar la carga de sólidos sobre el área de sedimentación:

\begin{{equation}}
P_{{\text{{humus}}}} = {s['factor_produccion_humus']:.2f} \times \text{{DBO}}_{{\text{{removida}}}} = {s['produccion_humus_kg_d']:.1f} \text{{ kg SST/d}}
\end{{equation}}

La tasa de aplicación de sólidos sobre el área del sedimentador resulta:

\begin{{equation}}
C_{{\text{{sólidos}}}} = \frac{{P_{{\text{{humus}}}}}}{{A_s}} = \frac{{{s['produccion_humus_kg_d']:.1f}}}{{{s['A_sup_m2']:.2f}}} = {s['solids_loading_kg_m2_d']:.2f} \text{{ kg SST/m}}^2\text{{·d}}
\end{{equation}}"""

    def generar_verificacion(self) -> str:
        """Genera subsection Verificacion con todas las verificaciones."""
        cfg = self.cfg
        s = self.datos
        
        return rf"""\subsection{{Verificación}}

\textbf{{Verificación de Carga Superficial}}

De acuerdo con los criterios de Metcalf \& Eddy \cite{{metcalf2014}} y WEF MOP-8 \cite{{wef_mop8_2010}}, el sedimentador debe verificarse para condiciones de caudal máximo horario. El factor de pico ($f_p$) de {s['factor_pico']:.1f} representa la relación entre el caudal máximo horario y el caudal medio diario, típico de sistemas de alcantarillado municipal. La verificación establece que:

\begin{{equation}}
Q_{{\max}} = f_p \times Q = {s['factor_pico']:.1f} \times {s['Q_m3_d']:.1f} = {s['Q_max_m3_d']:.1f} \text{{ m}}^3\text{{/d}}
\end{{equation}}

A caudal máximo, la tasa de desbordamiento resulta:

\begin{{equation}}
SOR_{{\max}} = \frac{{Q_{{\max}}}}{{A_s}} = \frac{{{s['Q_max_m3_d']:.1f}}}{{{s['A_sup_m2']:.2f}}} = {s['SOR_max_m3_m2_d']:.1f} \text{{ m}}^3\text{{/m}}^2\text{{·d}}
\end{{equation}}

{s['texto_sor_max_verificacion']}

\textbf{{Verificación del Vertedero Perimetral}}

{s['texto_weir_loading']}

\textbf{{Verificación de Almacenamiento de Lodos}}

{s['texto_solids_loading']}

Respecto al tiempo de retención a caudal mínimo (factor {s['factor_min']:.1f} del medio), el TRH resultante es de {s['TRH_min_h']:.1f} horas. {s['texto_trh_min']}

\textbf{{Nota técnica sobre operación a caudal mínimo:}} {s['nota_operacion_caudal_minimo']}"""

    def generar_resultados(self) -> str:
        """Genera subsection Resultados con tabla y figura."""
        cfg = self.cfg
        s = self.datos
        
        # Generar figura
        if os.path.isabs(self.ruta_figuras):
            output_dir = self.ruta_figuras
            latex_ruta_base = 'figuras'
        else:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados', self.ruta_figuras)
            latex_ruta_base = self.ruta_figuras
        
        fig_path = self.generar_esquema_matplotlib(output_dir)
        
        if fig_path:
            fig_relativa = (latex_ruta_base + '/' + os.path.basename(fig_path)).replace('\\', '/')
            figura_latex = rf"""\begin{{figure}}[H]
\centering
\includegraphics[width=0.92\textwidth]{{{fig_relativa}}}
\caption{{Esquema del sedimentador secundario circular: entrada central del efluente de la etapa biológica, zona de clarificación, tolva de lodos, vertedero perimetral y salida de efluente clarificado. Diámetro adoptado: {s['D_m']:.2f} m, profundidad lateral: {s['h_sed_m']:.2f} m, SOR promedio: {s['SOR_m3_m2_d']:.1f} m³/m²·d.}}
\label{{fig:sedimentador_secundario}}
\end{{figure}}

"""
        else:
            figura_latex = ""
        
        return rf"""\subsection{{Resultados}}

\begin{{table}}[H]
\centering
\caption{{Dimensiones del sedimentador secundario}}
\begin{{tabular}}{{ll}}
\toprule
Parámetro & Valor \\
\midrule
Diámetro & {s['D_m']:.2f} m \\
Área superficial & {s['A_sup_m2']:.2f} m² \\
Profundidad lateral & {s['h_sed_m']:.2f} m \\
Altura total de construcción & {s['altura_total_construccion_m']:.2f} m \\
Volumen útil & {s['V_m3']:.1f} m³ \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Parámetros hidráulicos}}}} \\
\midrule
SOR (promedio) & {s['SOR_m3_m2_d']:.1f} m³/m²·d \\
SOR (caudal máximo) & {s['SOR_max_m3_m2_d']:.1f} m³/m²·d \\
HRT (promedio) & {s['TRH_h']:.1f} h \\
HRT (caudal máximo) & {s['TRH_max_h']:.1f} h \\
Carga sobre vertedero & {s['weir_loading_m3_m_d']:.1f} m³/m·d \\
Carga de sólidos & {s['solids_loading_kg_m2_d']:.2f} kg/m²·d \\
\bottomrule
\end{{tabular}}
\end{{table}}

{figura_latex}Se debe incluir un sistema de recolección de lodos (rastrillos o succionadores) y un mecanismo de extracción de lodos desde el fondo. Se recomienda considerar el caudal mínimo en el diseño operacional para evitar estancamiento."""


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_dir)
    
    from ptar_dimensionamiento import ConfigDiseno, dimensionar_sedimentador_sec, dimensionar_filtro_percolador, dimensionar_uasb
    import subprocess
    
    print("=" * 60)
    print("TEST - GENERADOR MODULAR DE SEDIMENTADOR SECUNDARIO")
    print("=" * 60)
    
    cfg = ConfigDiseno()
    print(f"\n[1] Q_linea = {cfg.Q_linea_L_s} L/s")
    
    # Para el sedimentador secundario necesitamos DBO de entrada (salida del FP)
    uasb = dimensionar_uasb(cfg)
    DBO_entrada_fp = cfg.DBO5_mg_L * (1 - uasb['eta_DBO'])
    
    fp = dimensionar_filtro_percolador(cfg, DBO_entrada_mg_L=DBO_entrada_fp)
    DBO_entrada_sed = fp['DBO_salida_Germain_mg_L']
    DBO_removida_fp_kg_d = fp['DBO_removida_kg_d']
    
    datos = dimensionar_sedimentador_sec(
        cfg,
        DBO_entrada_mg_L=DBO_entrada_sed,
        DBO_removida_fp_kg_d=DBO_removida_fp_kg_d
    )
    print(f"[2] Dimensiones: D={datos['D_m']:.2f}m, SOR={datos['SOR_m3_m2_d']:.1f}m³/m²·d, TRH={datos['TRH_h']:.1f}h")
    
    resultados_dir = os.path.join(base_dir, 'resultados', 'test_modular')
    figuras_dir = os.path.join(resultados_dir, 'figuras')
    os.makedirs(figuras_dir, exist_ok=True)
    
    gen = GeneradorSedimentadorSecundario(cfg, datos, ruta_figuras=figuras_dir)
    latex = gen.generar_completo()
    print(f"[3] LaTeX generado: {len(latex)} chars")
    
    tex_path = os.path.join(resultados_dir, 'sedimentador_secundario_test.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    
    doc_path = os.path.join(resultados_dir, 'sedimentador_secundario_test_completo.tex')
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{enumitem}
\usepackage{tikz}
\usepackage{float}
\usepackage{xcolor}
\usepackage{hyperref}

\geometry{margin=2.5cm}

\newcommand{\captionequation}[1]{}  % Simplificado para test

\begin{document}

\section{Sedimentador Secundario}

""" + latex + r"""

\end{document}""")
    
    print(f"[4] Archivos guardados en: {resultados_dir}")
    
    print("[5] Compilando PDF...")
    try:
        subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', resultados_dir, doc_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        pdf_path = os.path.join(resultados_dir, 'sedimentador_secundario_test_completo.pdf')
        if os.path.exists(pdf_path):
            print(f"    PDF generado: {pdf_path}")
    except Exception as e:
        print(f"    ERROR: {e}")
    
    print("=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
