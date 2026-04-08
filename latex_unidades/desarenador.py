#!/usr/bin/env python3
"""
Generador LaTeX para Desarenador - Copia exacta de generar_latex_A.py lineas 396-550
Reorganizado en 3 subsections: Teoria, Verificacion, Resultados
"""

import os
import sys

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GeneradorDesarenador:
    """Generador LaTeX para unidad Desarenador - Copia exacta del original."""
    
    def __init__(self, cfg, datos, ruta_figuras='figuras'):
        self.cfg = cfg
        self.datos = datos
        self.ruta_figuras = ruta_figuras
    
    def generar_completo(self) -> str:
        """Genera todo el contenido LaTeX del desarenador en 3 subsections."""
        cfg = self.cfg
        d = self.datos
        
        # Generar figura si es posible
        figura_latex = ""
        try:
            fig_path = self.generar_esquema_matplotlib()
            if fig_path:
                if os.path.isabs(self.ruta_figuras):
                    latex_ruta_base = 'figuras'
                else:
                    latex_ruta_base = self.ruta_figuras
                fig_relativa = (latex_ruta_base + '/' + os.path.basename(fig_path)).replace('\\', '/')
                figura_latex = rf"""\begin{{figure}}[H]
\centering
\includegraphics[width=\textwidth]{{{fig_relativa}}}
\caption{{Esquema del desarenador de flujo horizontal con perfil longitudinal y corte transversal. Se muestran la entrada del afluente, la zona de flujo, el dep\'osito de arena y la salida . }}
\label{{fig:desarenador}}
\end{{figure}}
"""
        except Exception:
            pass
        
        # NOTA: Copia EXACTA de generar_latex_A.py reorganizada en 3 subsections
        # Seccion 1: Dimensionamiento (contiene teoria + parametros + calculos)
        teoria = rf"""\subsection{{Dimensionamiento}}

El desarenador remueve part\'iculas minerales (arena, grava) con di\'ametro superior a {d['d_mm']:.2f}~mm mediante sedimentaci\'on gravitacional. Seg\'un Metcalf y Eddy \cite{{metcalf2014}}, los par\'ametros de dise\~no son: velocidad horizontal {cfg.desarenador_v_h_min_m_s:.2f}--{cfg.desarenador_v_h_max_m_s:.2f}~m/s (m\'aximo {cfg.desarenador_v_h_max_m_s:.2f}~m/s para evitar arrastre de sedimentos), tiempo de retenci\'on {cfg.desarenador_t_retencion_min_s:.0f}--{cfg.desarenador_t_retencion_max_s:.0f}~s, y profundidad de flujo {cfg.desarenador_H_min_m:.2f}--{cfg.desarenador_H_max_m:.1f}~m (OPS/CEPIS \cite{{ops2005}} permite valores menores en plantas peque\~nas).

La profundidad total del canal incluye: profundidad \'util de flujo ({d['H_util_m']:.2f}~m), zona de almacenamiento de arena ({d['h_almacenamiento_arena_min_m']:.2f}--{d['h_almacenamiento_arena_max_m']:.2f}~m; se adopta {d['h_almacenamiento_arena_m']:.2f}~m), y bordo libre ({d['bordo_libre_m']:.2f}~m).

El dise\~no del desarenador se fundamenta en la teor\'ia de sedimentaci\'on discreta. Primero se calcula la velocidad de sedimentaci\'on de las part\'iculas objetivo mediante la Ley de Stokes:

\begin{{equation}}
v_s = \frac{{g \cdot (S_s - 1) \cdot d^2}}{{18 \cdot \nu}}
\end{{equation}}
\captionequation{{Ley de Stokes - Velocidad de sedimentacion de particulas}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$v_s$] = Velocidad de sedimentaci\'on (m/s)
    \item[$g$] = Aceleraci\'on de la gravedad ({d['g_m_s2']:.2f} m/s²)
    \item[$S_s$] = Gravedad espec\'ifica de la arena ({d['Ss']:.2f})
    \item[$d$] = Di\'ametro de la part\'icula ({d['d_m']:.5f} m)
    \item[$\nu$] = Viscosidad cinem\'atica del agua a {cfg.T_agua_C:.1f}°C (${d['nu_m2_s']:.4e}$ m²/s)
\end{{itemize}}

\begin{{equation}}
v_s = \frac{{{d['g_m_s2']:.2f} \times ({d['Ss']:.2f} - 1) \times ({d['d_m']:.5f})^2}}{{18 \times {d['nu_m2_s']:.4e}}} = {d['v_s_stokes_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

Con este valor de $v_s$ se determina la longitud te\'orica del desarenador mediante la ecuaci\'on de sedimentaci\'on tipo I:

\begin{{equation}}
L = \frac{{H \cdot v_h}}{{v_s}} = \frac{{{d['H_util_m']:.2f} \times {d['v_h_adoptada_m_s']:.2f}}}{{{d['v_s_stokes_m_s']:.3f}}} = {d['L_teorica_stokes_m']:.1f} \text{{ m}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$L$] = Longitud del desarenador (m)
    \item[$H$] = Profundidad \'util ({d['H_util_m']:.2f} m)
    \item[$v_h$] = Velocidad horizontal adoptada ({d['v_h_adoptada_m_s']:.2f} m/s)
\end{{itemize}}

La longitud te\'orica resultante ({d['L_teorica_stokes_m']:.1f}~m) es adecuada para el caudal de dise\~no y se adopta como longitud de dise\~no.

El ancho del canal se determina por la ecuaci\'on de continuidad:

\begin{{equation}}
B = \frac{{Q}}{{v_h \cdot H}} = \frac{{{cfg.Q_linea_m3_s:.5f}}}{{{d['v_h_adoptada_m_s']:.2f} \times {d['H_util_m']:.2f}}} = {d['b_teorico_m']:.3f} \text{{ m}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$B$] = Ancho te\'orico del canal (m)
    \item[$Q$] = Caudal de dise\~no ({cfg.Q_linea_m3_s:.5f} m³/s)
\end{{itemize}}

El ancho te\'orico resulta inferior al m\'inimo constructivo. Se adopta {d['b_canal_m']:.2f} m seg\'un OPS/CEPIS \cite{{ops2005}} y SENAGUA \cite{{senagua2012}}, que establecen {d['b_min_constructivo_m']:.2f} m como ancho m\'inimo para operaci\'on y mantenimiento.

Verificando la velocidad horizontal real con el ancho adoptado:

\begin{{equation}}
v_{{real}} = \frac{{Q}}{{B \cdot H}} = \frac{{{cfg.Q_linea_m3_s:.5f}}}{{{d['b_canal_m']:.2f} \times {d['H_util_m']:.2f}}} = {d['v_h_real_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

El tiempo de retenci\'on real resulta:

\begin{{equation}}
t_r = \frac{{L}}{{v_{{real}}}} = \frac{{{d['L_diseno_m']:.1f}}}{{{d['v_h_real_m_s']:.3f}}} = {d['t_r_real_s']:.1f} \text{{ s}}
\end{{equation}}"""

        verificacion = rf"""\subsection{{Verificacion}}

\textbf{{Verificacion de Velocidad Critica de Resuspension}}

Para garantizar que la arena sedimentada no sea resuspendida por el flujo, se verifica que la velocidad horizontal del dise\~no sea menor que la velocidad cr\'itica de resuspensi\'on, calculada mediante la f\'ormula de Camp-Shields:

\begin{{equation}}
v_c = \sqrt{{\frac{{8 \beta g (S_s - 1) d}}{{f}}}}
\end{{equation}}
\captionequation{{Velocidad critica de resuspension - Camp-Shields}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$v_c$] = Velocidad cr\'itica de resuspensi\'on (m/s)
    \item[$\beta$] = Factor de forma ({d['beta']:.2f}, rango {d['beta_min']:.2f}--{d['beta_max']:.2f})
    \item[$g$] = Aceleraci\'on de la gravedad ({d['g_m_s2']:.2f} m/s²)
    \item[$S_s$] = Gravedad espec\'ifica de la arena ({d['Ss']:.2f})
    \item[$d$] = Di\'ametro de la part\'icula ({d['d_m']:.5f} m)
    \item[$f$] = Factor de fricci\'on de Darcy-Weisbach ({d['f_darcy']:.3f}, rango {d['f_darcy_min']:.2f}--{d['f_darcy_max']:.2f})
\end{{itemize}}

\begin{{equation}}
v_c = \sqrt{{\frac{{8 \times {d['beta']:.2f} \times {d['g_m_s2']:.2f} \times ({d['Ss']:.2f} - 1) \times {d['d_m']:.5f}}}{{{d['f_darcy']:.3f}}}}} = {d['v_c_scour_m_s']:.3f} \text{{ m/s}}
\end{{equation}}
\captionequation{{Velocidad critica calculada}}

\textbf{{Verificacion para Caudal Maximo Horario}}

Se verifica el comportamiento hidr\'aulico para el caudal m\'aximo horario, aplicando un factor de pico t\'ipico de {d['factor_pico']:.1f} sobre el caudal medio:

\begin{{equation}}
Q_{{max}} = {d['factor_pico']:.1f} \times Q_{{medio}} = {d['factor_pico']:.1f} \times {cfg.Q_linea_L_s:.1f} = {d['Q_max_L_s']:.1f} \text{{ L/s}}
\end{{equation}}

A caudal m\'aximo, la velocidad horizontal resulta:

\begin{{equation}}
v_{{h,max}} = \frac{{Q_{{max}}}}{{B \cdot H}} = \frac{{{d['Q_max_L_s']:.3f}/1000}}{{{d['b_canal_m']:.2f} \times {d['H_util_m']:.2f}}} = {d['v_h_max_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

El tiempo de retenci\'on a caudal m\'aximo:

\begin{{equation}}
t_{{r,max}} = \frac{{L}}{{v_{{h,max}}}} = \frac{{{d['L_diseno_m']:.1f}}}{{{d['v_h_max_m_s']:.3f}}} = {d['t_r_max_s']:.1f} \text{{ s}}
\end{{equation}}

\textbf{{Criterios de verificaci\'on de resuspensi\'on}} (Camp-Shields, Metcalf y Eddy \cite{{metcalf2014}}):

La velocidad calculada $v_{{h,max}} = {d['v_h_max_m_s']:.3f}$~m/s se eval\'ua seg\'un (l\'imite: $v_c \times {d['factor_seguridad_scour_pct']}\% = {d['v_h_max_limite_scour_m_s']:.3f}$~m/s):

\begin{{equation}}
\text{{Estado}} = \begin{{cases}}
    \text{{SEGURIDAD}} & \text{{si }} v_{{h,max}} \leq {d['v_h_max_limite_scour_m_s']:.3f} \text{{ m/s}} \quad \text{{(no hay resuspensi\'on)}} \\
    \text{{RIESGO}} & \text{{si }} v_{{h,max}} > {d['v_h_max_limite_scour_m_s']:.3f} \text{{ m/s}} \quad \text{{(arena resuspendida)}}
\end{{cases}}
\end{{equation}}
\captionequation{{Criterios de verificacion de resuspension}}

Con la velocidad calculada $v_{{h,max}} = {d['v_h_max_m_s']:.3f}$~m/s, la unidad se clasifica como \textbf{{{d['estado_resuspension']}}}. En terminos de cumplimiento, la verificacion de resuspension \textbf{{{d['estado_resuspension_norma']}}} porque {d['verif_scour_texto']}."""

        resultados = rf"""\subsection{{Resultados}}

\begin{{table}}[H]
\centering
\caption{{Dimensiones del desarenador}}
\begin{{tabular}}{{l p{{9cm}}}}
\toprule
Par\'ametro & Valor \\
\midrule
Longitud dise\~no & {d['L_diseno_m']:.1f} m (m\'inimo constructivo SENAGUA) \\
Ancho & {d['b_canal_m']:.2f} m (m\'inimo constructivo) \\
Profundidad \'util & {d['H_util_m']:.2f} m \\
Velocidad horizontal real & {d['v_h_real_m_s']:.3f} m/s \\
Velocidad cr\'itica resuspensi\'on & {d['v_c_scour_m_s']:.3f} m/s (Camp-Shields) \\
Tiempo retenci\'on real & {d['t_r_real_s']:.1f} s \\
\bottomrule
\multicolumn{{2}}{{p{{\textwidth}}}}{{\small\textit{{$^a$Nota: El TRH de {d['t_r_real_s']:.0f}~s y velocidad de {d['v_h_real_m_s']:.3f}~m/s se deben al ancho m\'inimo constructivo de {d['b_min_constructivo_m']:.2f}~m. }}}}
\end{{tabular}}
\end{{table}}

{figura_latex}\textbf{{Manejo de arena removida}}

El desarenador retiene part\'iculas minerales (arena, grava fina) que se sedimentan en el fondo del canal. El manejo adecuado de estos residuos incluye:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item \textbf{{Caracter\'isticas de la arena:}} Part\'iculas minerales con di\'ametro $>${d['d_mm']:.2f}~mm, gravedad espec\'ifica de {d['Ss']:.2f}, que representan s\'olidos inorg\'anicos de alta densidad presentes en el agua residual.
    \item \textbf{{Volumen de almacenamiento:}} El canal incluye una zona de almacenamiento de {d['h_almacenamiento_arena_m']:.2f}~m de altura, dise\~nada para acumular la arena removida entre operaciones de limpieza.
    \item \textbf{{Frecuencia de limpieza:}} Diaria o seg\'un acumulaci\'on observada. En condiciones normales, la arena acumulada no debe superar el 50\% de la altura de almacenamiento designada.
    \item \textbf{{M\'etodo de remoci\'on:}} Manual mediante palas y cubos desde la plataforma de operaci\'on, o mediante sistema de succi\'on/bombeo si el caudal y la producci\'on de arena lo justifican.
\end{{itemize}}

\textbf{{Disposici\'on final de la arena:}}

La arena removida en el desarenador tiene las siguientes opciones de manejo, seg\'un su composici\'on y la normativa local:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item \textbf{{Relleno sanitario:}} Es la opci\'on m\'as com\'un. La arena, al ser material inorg\'anico inerte, puede disposicionarse en rellenos sanitarios autorizados sin restricciones especiales.
    \item \textbf{{Reuso condicionado:}} Si la arena est\'a relativamente limpia (bajo contenido de materia org\'anica adherida), puede utilizarse para:
    \begin{{itemize}}[noitemsep,leftmargin=1.5em]
        \item Relleno y compactaci\'on en obras civiles (previa caracterizaci\'on)
        \item Mezcla con concreto para elementos no estructurales
        \item Complemento en sistemas de filtraci\'on gruesa (previo lavado)
    \end{{itemize}}
    \item \textbf{{Lavado previo:}} Si se detecta alta carga org\'anica adherida a los granos de arena (olor f\'etido, color oscuro), se recomienda lavado antes de la disposici\'on final para reducir el impacto ambiental.
\end{{itemize}}

\textit{{Nota sobre cantidades:}} El presente dimensionamiento no estima la masa o volumen diario de arena removida. Seg\'un Metcalf y Eddy \cite{{metcalf2014}}, la producci\'on t\'ipica de arena en aguas residuales municipales var\'ia entre 0.004--0.15 L/m\textsuperscript{{3}} de agua tratada, dependiendo de las caracter\'isticas del sistema de alcantarillado (red combinada vs. separada) y del suelo local. Para el caudal de dise\'no, esto representar\'ia aproximadamente 0.02--0.6 L/d (total planta), sujeto a caracterizaci\'on local."""

        return f"{teoria}\n\n{verificacion}\n\n{resultados}"

    def generar_esquema_matplotlib(self, output_dir: str = None) -> str:
        """Genera esquema del desarenador usando la funcion original de ptar_layout_graficador."""
        try:
            from ptar_layout_graficador import generar_esquema_desarenador
        except ImportError:
            return None
        
        if output_dir is None:
            if os.path.isabs(self.ruta_figuras):
                output_dir = self.ruta_figuras
            else:
                output_dir = os.path.join(_base_dir, 'resultados', self.ruta_figuras)
        
        return generar_esquema_desarenador(self.datos, output_dir)


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    sys.path.insert(0, _base_dir)
    from ptar_dimensionamiento import ConfigDiseno, dimensionar_desarenador
    import subprocess
    
    print("=" * 60)
    print("TEST - GENERADOR MODULAR DE DESARENADOR")
    print("=" * 60)
    
    cfg = ConfigDiseno()
    cfg.Q_linea_L_s = 5.0
    cfg.Q_linea_m3_s = 0.005
    print(f"\n[1] Q_linea = {cfg.Q_linea_L_s} L/s")
    
    datos = dimensionar_desarenador(cfg)
    print(f"[2] Dimensiones: L={datos['L_diseno_m']:.1f}m, b={datos['b_canal_m']:.2f}m, H={datos['H_util_m']:.2f}m")
    
    resultados_dir = os.path.join(_base_dir, 'resultados', 'test_modular')
    figuras_dir = os.path.join(resultados_dir, 'figuras')
    os.makedirs(figuras_dir, exist_ok=True)
    
    gen = GeneradorDesarenador(cfg, datos, ruta_figuras=figuras_dir)
    latex = gen.generar_completo()
    print(f"[3] LaTeX generado: {len(latex)} chars")
    
    # Guardar .tex
    tex_path = os.path.join(resultados_dir, 'desarenador_test.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    
    doc_path = os.path.join(resultados_dir, 'desarenador_test_completo.tex')
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{colortbl}
\usepackage{graphicx}
\usepackage{enumitem}
\usepackage{tikz}
\usepackage{float}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{tocloft}
\usepackage{titletoc}

\geometry{margin=2.5cm}

\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=blue,
    urlcolor=blue
}

\newcommand{\captionequation}[1]{}  % Simplificado para test

\begin{document}

\section{Unidad de Desarenado}

""" + latex + r"""

\end{document}""")
    
    print(f"[4] Archivos guardados en: {resultados_dir}")
    
    # COMPILAR PDF
    print("[5] Compilando PDF...")
    try:
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', resultados_dir, doc_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        pdf_path = os.path.join(resultados_dir, 'desarenador_test_completo.pdf')
        if os.path.exists(pdf_path):
            print(f"    PDF generado: {pdf_path}")
        else:
            print(f"    ERROR: No se genero el PDF")
    except Exception as e:
        print(f"    ERROR al compilar: {e}")
    
    print("=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
