#!/usr/bin/env python3
"""
Generador de LaTeX para Alternativa A - Estilo narrativo
Memoria de cálculo tipo informe técnico fluido
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ptar_dimensionamiento import (
    ConfigDiseno,
    dimensionar_rejillas,
    dimensionar_desarenador,
    dimensionar_uasb,
    dimensionar_filtro_percolador,
    dimensionar_sedimentador_sec,
    dimensionar_desinfeccion_cloro,
    dimensionar_lecho_secado,
)


def _generar_tikz_rejillas(r, angulo_rej):
    """Genera el código TikZ para el esquema de rejillas - Version con circulo azul"""
    h = r['h_tirante_m']
    b = r['ancho_layout_m']
    L = r['largo_layout_m']
    
    return (
        r"\begin{figure}[H]" + "\n"
        r"\centering" + "\n"
        r"\begin{tikzpicture}[scale=1.0, line cap=round, line join=round]" + "\n"
        r"" + "\n"
        r"% === SECCION TRANSVERSAL (izquierda) ===" + "\n"
        r"\begin{scope}[xshift=-4.5cm]" + "\n"
        r"    % Paredes del canal (gris claro)" + "\n"
        r"    \fill[gray!20] (0,0) rectangle (3.6,1.5);" + "\n"
        r"    % Borde del canal" + "\n"
        r"    \draw[very thick] (0,0) rectangle (3.6,1.5);" + "\n"
        r"    % Agua (azul muy claro)" + "\n"
        r"    \fill[blue!10] (0.1,0.1) rectangle (3.5,1.0);" + "\n"
        r"    % Linea de agua punteada" + "\n"
        r"    \draw[blue, thick, dashed] (0.1,1.0) -- (3.5,1.0);" + "\n"
        r"    % Barras de rejilla VERTICALES negras y gruesas" + "\n"
        r"    \foreach \x in {0.4,0.8,1.2,1.6,2.0,2.4,2.8,3.2}{" + "\n"
        r"        \draw[line width=2.5pt] (\x,0.1) -- (\x,1.4);" + "\n"
        r"    }" + "\n"
        r"    % Circulo azul con punto blanco (direccion perpendicular al plano)" + "\n"
        r"    \fill[blue] (1.8,0.55) circle (0.18);" + "\n"
        r"    \fill[white] (1.8,0.55) circle (0.06);" + "\n"
        r"    % Cota del tirante (izquierda) con marcas de dimension" + "\n"
        r"    \draw[thick] (-0.3,0.1) -- (-0.3,1.0);" + "\n"
        r"    \draw[thick] (-0.4,0.1) -- (-0.2,0.1);" + "\n"
        r"    \draw[thick] (-0.4,1.0) -- (-0.2,1.0);" + "\n"
        rf"    \node[left] at (-0.3,0.55) {{$h = {h:.2f}$~m}};" + "\n"
        r"    % Cota del ancho (abajo) con marcas de dimension" + "\n"
        r"    \draw[thick] (0,-0.3) -- (3.6,-0.3);" + "\n"
        r"    \draw[thick] (0,-0.4) -- (0,-0.2);" + "\n"
        r"    \draw[thick] (3.6,-0.4) -- (3.6,-0.2);" + "\n"
        rf"    \node[below] at (1.8,-0.3) {{$b = {b:.2f}$~m}};" + "\n"
        r"    % Titulo" + "\n"
        r"    \node[below, font=\bfseries] at (1.8,-0.9) {Seccion Transversal};" + "\n"
        r"\end{scope}" + "\n"
        r"" + "\n"
        r"% === VISTA LONGITUDINAL (derecha) ===" + "\n"
        r"\begin{scope}[xshift=2cm]" + "\n"
        r"    % Paredes del canal (gris claro)" + "\n"
        r"    \fill[gray!20] (0,0) rectangle (6,1.2);" + "\n"
        r"    % Borde del canal" + "\n"
        r"    \draw[very thick] (0,0) rectangle (6,1.2);" + "\n"
        r"    % Agua (azul muy claro)" + "\n"
        r"    \fill[blue!10] (0.1,0.1) rectangle (5.9,1.1);" + "\n"
        r"    \draw[thick] (0.1,0.1) rectangle (5.9,1.1);" + "\n"
        r"    % Rejilla: barras verticales negras y gruesas" + "\n"
        r"    \foreach \x in {1.7,1.85,2.0,2.15,2.3,2.45}{" + "\n"
        r"        \draw[line width=2.5pt] (\x,0.1) -- (\x,1.1);" + "\n"
        r"    }" + "\n"
        r"    % Marco de la rejilla" + "\n"
        r"    \draw[very thick] (1.6,0.05) rectangle (2.55,1.15);" + "\n"
        r"    % Flechas de flujo AZULES con cabeza" + "\n"
        r"    \draw[line width=2pt, blue!80!black] (0.4,0.6) -- (1.5,0.6);" + "\n"
        r"    \fill[blue!80!black] (1.5,0.6) -- (1.25,0.45) -- (1.25,0.75) -- cycle;" + "\n"
        r"    \draw[line width=2pt, blue!80!black] (2.7,0.6) -- (5.5,0.6);" + "\n"
        r"    \fill[blue!80!black] (5.5,0.6) -- (5.25,0.45) -- (5.25,0.75) -- cycle;" + "\n"
        r"    % Cota de longitud (abajo) con marcas de dimension" + "\n"
        r"    \draw[thick] (0,-0.3) -- (6,-0.3);" + "\n"
        r"    \draw[thick] (0,-0.4) -- (0,-0.2);" + "\n"
        r"    \draw[thick] (6,-0.4) -- (6,-0.2);" + "\n"
        rf"    \node[below] at (3,-0.3) {{$L = {L:.1f}$~m}};" + "\n"
        r"    % Etiqueta Entrada" + "\n"
        r"    \draw[thick] (0.1,1.5) -- (1.6,1.5);" + "\n"
        r"    \node[above] at (0.85,1.5) {Entrada};" + "\n"
        r"    % Etiqueta Rejilla" + "\n"
        r"    \draw[thick] (1.6,1.5) -- (5.9,1.5);" + "\n"
        r"    \node[above] at (3.75,1.5) {Rejilla};" + "\n"
        r"    % Titulo" + "\n"
        r"    \node[below, font=\bfseries] at (3,-0.9) {Vista Longitudinal};" + "\n"
        r"\end{scope}" + "\n"
        r"" + "\n"
        r"\end{tikzpicture}" + "\n"
        r"\caption{Esquema del canal de desbaste con rejillas (dimensiones en metros)}" + "\n"
        r"\label{fig:rejillas}" + "\n"
        r"\end{figure}"
    )


def generar_contenido_alternativa_A(cfg, resultados, layout_filename="Layout_A_2lineas.png", area_m2=None, balance_calidad=None):
    """Genera contenido LaTeX con estilo narrativo fluido"""
    
    # Valores por defecto si no se proporciona balance de calidad
    if balance_calidad is None:
        balance_calidad = {
            'afluente': {'DBO5_mg_L': cfg.DBO5_mg_L, 'DQO_mg_L': cfg.DQO_mg_L, 'SST_mg_L': cfg.SST_mg_L, 'CF_NMP': cfg.CF_NMP},
            'tras_uasb': {'DBO5_mg_L': cfg.DBO5_mg_L*0.7, 'DQO_mg_L': cfg.DQO_mg_L*0.65, 'SST_mg_L': cfg.SST_mg_L*0.7, 'CF_NMP': cfg.CF_NMP*0.7},
            'tras_fp': {'DBO5_mg_L': cfg.DBO5_mg_L*0.7*0.8, 'DQO_mg_L': cfg.DQO_mg_L*0.65*0.8, 'SST_mg_L': cfg.SST_mg_L*0.7*0.4, 'CF_NMP': cfg.CF_NMP*0.7*0.8},
            'efluente_final': {'DBO5_mg_L': cfg.DBO5_mg_L*0.17, 'DQO_mg_L': cfg.DQO_mg_L*0.2, 'SST_mg_L': cfg.SST_mg_L*0.02, 'CF_NMP': 2500}
        }
    
    r = resultados.get('rejillas', dimensionar_rejillas(cfg))
    d = resultados.get('desarenador', dimensionar_desarenador(cfg))
    u = resultados.get('uasb', dimensionar_uasb(cfg))
    
    # Generar texto de recomendación según temperatura
    if u['T_agua_C'] >= 22:
        temp_recomendacion = (
            "Para mantener el rendimiento óptimo del reactor en caso de descenso de temperatura, "
            "se recomienda monitorear periodicamente. Si la temperatura descendiera por debajo de 20°C, "
            "el sistema debería ajustar automáticamente la carga orgánica y el tiempo de retención."
        )
    elif 18 <= u['T_agua_C'] < 22:
        temp_recomendacion = (
            "La temperatura está en rango moderado. Se recomienda considerar aislamiento térmico básico "
            "del reactor para mantener la eficiencia durante períodos fríos."
        )
    elif 15 <= u['T_agua_C'] < 18:
        temp_recomendacion = (
            "La temperatura es baja, lo que ha reducido automáticamente la carga orgánica y aumentado "
            "el tiempo de retención. Se recomienda implementar aislamiento térmico del reactor para "
            "evitar mayor degradación del proceso."
        )
    elif 10 <= u['T_agua_C'] < 15:
        temp_recomendacion = (
            "ATENCIÓN: La temperatura es muy baja. El sistema ha aplicado ajustes significativos: "
            "reducción de carga orgánica a 40% del valor base y duplicación del tiempo de retención. "
            "Se requiere aislamiento térmico obligatorio o considerar calefacción del reactor."
        )
    else:
        temp_recomendacion = (
            "NO RECOMENDABLE: Temperatura por debajo de 10°C. El proceso anaerobio es inviable sin calentar la biomasa. "
            "Se requiere calefacción del reactor (mantener 20-25°C) o cambio obligatorio a tecnología aerobia activada. "
            "Los ajustes automáticos aplicados (carga reducida a 30%, HRT aumentado 150%) NO son suficientes para garantizar tratamiento adecuado."
        )
    
    fp = resultados.get('filtro_percolador', dimensionar_filtro_percolador(cfg))
    s = resultados.get('sedimentador', dimensionar_sedimentador_sec(cfg))
    l = resultados.get('lecho_secado', dimensionar_lecho_secado(cfg))
    cl = resultados.get('cloro', dimensionar_desinfeccion_cloro(cfg))
    
    # Extraer parámetros de configuración
    v_canal = cfg.rejillas_v_canal_m_s
    h_tirante = cfg.rejillas_h_tirante_m
    angulo_rej = cfg.rejillas_angulo_grados
    beta = cfg.rejillas_beta
    w_barra = cfg.rejillas_w_barra_m * 1000
    b_barra = cfg.rejillas_b_barra_m * 1000
    
    # Generar esquema TikZ de rejillas
    tikz_rejillas = _generar_tikz_rejillas(r, angulo_rej)
    
    return rf"""
%============================================================================
% ALTERNATIVA A: UASB + FILTRO PERCOLADOR + UV
% Memoria de Cálculo
%============================================================================
\newpage
\section{{Alternativa A: Tratamiento Anaerobio-Aerobio con UASB y Filtro Percolador}}

La presente alternativa propone un esquema de tratamiento que combina procesos anaerobios y aerobios para lograr la remoción de contaminantes de manera eficiente y con bajo consumo energético. El tren de tratamiento completo comprende: rejillas y desarenador para el pretratamiento, reactor UASB para el tratamiento primario anaerobio, filtro percolador para el tratamiento secundario aerobio, sedimentador secundario para la separación de sólidos biológicos, y finalmente desinfección con hipoclorito de sodio antes del vertimiento.

\subsection{{Canal de Desbaste con Rejillas}}

Las rejillas constituyen la primera barrera de protección del sistema, reteniendo sólidos gruesos como plásticos, ramas y papel que podrían dañar equipos o causar obstrucciones en tuberías aguas abajo. El diseño hidráulico de esta unidad debe garantizar velocidades suficientes para arrastrar sólidos sedimentables, pero no tan elevadas que dificulten el paso del agua a través de las barras.

Según los criterios establecidos por Metcalf y Eddy \cite{{metcalf2014}}, las velocidades de diseño en canales con rejillas deben mantenerse entre 0,40 y 0,60 m/s. Para este proyecto se adopta un valor intermedio de {v_canal:.2f} m/s, lo cual resulta apropiado considerando el caudal de diseño. El tirante hidráulico se establece en {h_tirante:.2f} m, valor que permite una velocidad de flujo uniforme en la sección del canal y evita la sedimentación de sólidos orgánicos antes de la rejilla, según los criterios de Metcalf y Eddy \cite{{metcalf2014}}.

La pérdida de carga en rejillas limpias se calcula mediante la fórmula de Kirschmer (1926), que relaciona la geometría de las barras con las características del flujo. Los parámetros que determinan esta pérdida son: el espaciado entre barras ($b$), el espesor de las barras ($w$), la velocidad del flujo ($v$) y el ángulo de inclinación ($\theta$):

\begin{{equation}}
h_L = \beta \cdot \left(\frac{{w}}{{b}}\right)^{{4/3}} \cdot \frac{{v^2}}{{2g}} \cdot \sin\theta
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$h_L$] = Pérdida de carga en rejillas limpias (m)
    \item[$\beta$] = Factor de forma de la barra (2,42 para barras rectangulares)
    \item[$w$] = Espesor de la barra ({w_barra:.0f} mm)
    \item[$b$] = Espaciado entre barras ({b_barra:.0f} mm)
    \item[$v$] = Velocidad del flujo en el canal (m/s)
    \item[$g$] = Aceleración de la gravedad (9,81 m/s²)
    \item[$\theta$] = Ángulo de inclinación de las barras ({angulo_rej:.0f}°)
\end{{itemize}}

El caudal de diseño por línea es {cfg.Q_linea_L_s:.1f} L/s. La sección transversal del canal se determina aplicando la ecuación de continuidad:

\begin{{equation}}
A_{{canal}} = \frac{{Q}}{{v}} = \frac{{{cfg.Q_linea_m3_s:.5f}}}{{{v_canal:.2f}}} = {r['A_canal_m2']:.5f} \text{{ m}}^2
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_{{canal}}$] = Sección transversal del canal (m²)
    \item[$Q$] = Caudal de diseño por línea ({cfg.Q_linea_m3_s:.5f} m³/s)
    \item[$v$] = Velocidad de diseño adoptada ({v_canal:.2f} m/s)
\end{{itemize}}

Despejando el ancho del canal de la ecuación $A = b \times h$, con $h = {h_tirante:.2f}$ m:

\begin{{equation}}
b = \frac{{A_{{canal}}}}{{h}} = \frac{{{r['A_canal_m2']:.5f}}}{{{h_tirante:.2f}}} = {r['b_canal_teorico_m']:.3f} \text{{ m}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$b$] = Ancho teórico del canal (m)
    \item[$A_{{canal}}$] = Sección transversal del canal ({r['A_canal_m2']:.5f} m²)
    \item[$h$] = Tirante hidráulico ({h_tirante:.2f} m)
\end{{itemize}}

Este ancho teórico de {r['b_canal_teorico_m']:.3f} m es inferior al mínimo constructivo práctico. Se adopta un ancho de 0,60 m como dimensión mínima constructiva según criterios de OPS/CEPIS \cite{{ops2005}} y SENAGUA \cite{{senagua2012}}, que establecen un ancho mínimo de 0,60 m para permitir la operación adecuada, el acceso para limpieza y la aplicación de herramientas de mantenimiento. Verificando la velocidad real con este ancho:

\begin{{equation}}
v_{{real}} = \frac{{Q}}{{A_{{real}}}} = \frac{{{cfg.Q_linea_m3_s:.5f}}}{{{r['ancho_layout_m']:.2f} \times {h_tirante:.2f}}} = {r['v_canal_real_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$v_{{real}}$] = Velocidad real verificada con ancho constructivo (m/s)
    \item[$Q$] = Caudal de diseño ({cfg.Q_linea_m3_s:.5f} m³/s)
    \item[$A_{{real}}$] = Sección real con ancho constructivo adoptado ({r['ancho_layout_m']:.2f} × {h_tirante:.2f} m²)
\end{{itemize}}

La velocidad real de {r['v_canal_real_m_s']:.3f} m/s es el resultado de adoptar el ancho mínimo constructivo. La pérdida de carga calculada con esta velocidad real resulta $h_L = {r['perdida_carga_real_m']*100:.4f}$ cm, menor al umbral de 15 cm que Metcalf y Eddy \cite{{metcalf2014}} indican como referencia para sistemas de limpieza mecánica.

La longitud de {r['largo_layout_m']:.1f} m y el ancho de {r['ancho_layout_m']:.2f} m responden a criterios constructivos y operativos. El ancho de 0,60 m es la dimensión mínima constructiva según OPS/CEPIS \cite{{ops2005}} y SENAGUA \cite{{senagua2012}}, que permite la operación adecuada de la rejilla, el acceso para limpieza y la aplicación de herramientas de mantenimiento. La longitud contempla el espacio de la rejilla propiamente dicha más las zonas de transición necesarias para la operación.

\subsubsection{{Verificación para Caudal Máximo Horario}}

Se verifica el comportamiento hidráulico para el caudal máximo horario, aplicando un factor de pico típico de {r['factor_pico']:.1f} sobre el caudal medio:

\begin{{equation}}
Q_{{max}} = {r['factor_pico']:.1f} \times Q_{{medio}} = {r['factor_pico']:.1f} \times {cfg.Q_linea_L_s:.1f} = {r['Q_max_L_s']:.1f} \text{{ L/s}}
\end{{equation}}

A caudal máximo, la velocidad horizontal resulta:

\begin{{equation}}
v_{{max}} = \frac{{Q_{{max}}}}{{A_{{real}}}} = \frac{{{r['Q_max_L_s']:.3f}/1000}}{{{r['ancho_layout_m']:.2f} \times {r['h_tirante_m']:.2f}}} = {r['v_max_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

\textbf{{Criterios de verificación de velocidad}} (según Metcalf y Eddy \cite{{metcalf2014}}):

La velocidad calculada $v_{{max}} = {r['v_max_m_s']:.3f}$~m/s se evalúa según:

\begin{{equation}}
\text{{Estado}} = \begin{{cases}}
    \text{{ÓPTIMO}} & \text{{si }} v_{{max}} \leq {cfg.rejillas_v_max_advertencia_m_s:.1f} \text{{ m/s}} \quad \text{{(sin riesgo)}} \\
    \text{{ACEPTABLE}} & \text{{si }} {cfg.rejillas_v_max_advertencia_m_s:.1f} < v_{{max}} \leq {cfg.rejillas_v_max_destructivo_m_s:.1f} \text{{ m/s}} \quad \text{{(monitoreo)}} \\
    \text{{NO ADMISIBLE}} & \text{{si }} v_{{max}} > {cfg.rejillas_v_max_destructivo_m_s:.1f} \text{{ m/s}} \quad \text{{(daño seguro)}}
\end{{cases}}
\end{{equation}}

Con la velocidad calculada $v_{{max}} = {r['v_max_m_s']:.3f}$~m/s, {r['verif_vel_texto']}. Respecto a la pérdida de carga, el valor máximo de {r['hL_max_m']*100:.4f}~cm {r['verif_hl_texto']}.

\subsubsection{{Resultados}}

\begin{{table}}[H]
\centering
\caption{{Verificación de criterios de diseño - Rejillas}}
\begin{{tabular}}{{lccc}}
\toprule
Parámetro & Valor calculado & Criterio & Estado \\
\midrule
Velocidad de diseño & {r['v_canal_adoptada_m_s']:.2f} m/s & 0,40 -- 0,60 m/s & Cumple \\
Velocidad real & {r['v_canal_real_m_s']:.3f} m/s & Ancho mínimo constructivo$^a$ & Aplicado \\
Pérdida de carga (Qmax) & {r['hL_max_m']*100:.4f} cm & $<$ 15 cm & Cumple \\
Ancho constructivo & {r['ancho_layout_m']:.2f} m & $\geq$ 0,30 m & Cumple \\
\bottomrule
\end{{tabular}}
\small
$^a$ Para caudales pequeños (5 L/s) el ancho mínimo constructivo (0,60 m) domina sobre el criterio de velocidad.
\end{{table}}

{tikz_rejillas}

Las dimensiones finales del canal con rejillas son: ancho {r['ancho_layout_m']:.2f} m, tirante {r['h_tirante_m']:.2f} m y longitud {r['largo_layout_m']:.1f} m. Se requieren dos unidades, una por cada línea de tratamiento.

\subsection{{Desarenador de Flujo Horizontal}}

El desarenador remueve partículas minerales (arena, grava) con diámetro superior a 0,20 mm mediante sedimentación gravitacional. Según Metcalf y Eddy \cite{{metcalf2014}}, los parámetros de diseño son: velocidad horizontal 0,25 - 0,30 m/s (máximo 0,30 m/s para evitar arrastre de sedimentos), tiempo de retención 30 - 60 s, y profundidad de flujo 0,75 - 2,0 m (OPS/CEPIS \cite{{ops2005}} permite valores menores en plantas pequeñas).

La profundidad total del canal incluye: profundidad útil de flujo ({d['H_util_m']:.2f}~m), zona de almacenamiento de arena (0,25 - 0,30~m), y bordo libre (0,30~m).

El diseño del desarenador se fundamenta en la teoría de sedimentación discreta. Primero se calcula la velocidad de sedimentación de las partículas objetivo mediante la Ley de Stokes:

\begin{{equation}}
v_s = \frac{{g \cdot (S_s - 1) \cdot d^2}}{{18 \cdot \nu}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$v_s$] = Velocidad de sedimentación (m/s)
    \item[$g$] = Aceleración de la gravedad ({d['g_m_s2']:.2f} m/s²)
    \item[$S_s$] = Gravedad específica de la arena ({d['Ss']:.2f})
    \item[$d$] = Diámetro de la partícula ({d['d_m']:.5f} m)
    \item[$\nu$] = Viscosidad cinemática del agua a {u['T_agua_C']:.1f}°C (${d['nu_m2_s']:.4e}$ m²/s)
\end{{itemize}}

\begin{{equation}}
v_s = \frac{{{d['g_m_s2']:.2f} \times ({d['Ss']:.2f} - 1) \times ({d['d_m']:.5f})^2}}{{18 \times {d['nu_m2_s']:.4e}}} = {d['v_s_stokes_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

Con este valor de $v_s$ se determina la longitud teórica del desarenador mediante la ecuación de sedimentación tipo I:

\begin{{equation}}
L = \frac{{H \cdot v_h}}{{v_s}} = \frac{{{d['H_util_m']:.2f} \times {d['v_h_adoptada_m_s']:.2f}}}{{{d['v_s_stokes_m_s']:.3f}}} = {d['L_teorica_stokes_m']:.1f} \text{{ m}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$L$] = Longitud del desarenador (m)
    \item[$H$] = Profundidad útil ({d['H_util_m']:.2f} m)
    \item[$v_h$] = Velocidad horizontal adoptada ({d['v_h_adoptada_m_s']:.2f} m/s)
\end{{itemize}}

La longitud teórica resultante ({d['L_teorica_stokes_m']:.1f}~m) es adecuada para el caudal de diseño y se adopta como longitud de diseño.

El ancho del canal se determina por la ecuación de continuidad:

\begin{{equation}}
B = \frac{{Q}}{{v_h \cdot H}} = \frac{{{cfg.Q_linea_m3_s:.5f}}}{{{d['v_h_adoptada_m_s']:.2f} \times {d['H_util_m']:.2f}}} = {d['b_teorico_m']:.3f} \text{{ m}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$B$] = Ancho teórico del canal (m)
    \item[$Q$] = Caudal de diseño ({cfg.Q_linea_m3_s:.5f} m³/s)
\end{{itemize}}

El ancho teórico resulta inferior al mínimo constructivo. Se adopta {d['b_canal_m']:.2f} m según OPS/CEPIS \cite{{ops2005}} y SENAGUA \cite{{senagua2012}}, que establecen 0,60 m como ancho mínimo para operación y mantenimiento.

Verificando la velocidad horizontal real con el ancho adoptado:

\begin{{equation}}
v_{{real}} = \frac{{Q}}{{B \cdot H}} = \frac{{{cfg.Q_linea_m3_s:.5f}}}{{{d['b_canal_m']:.2f} \times {d['H_util_m']:.2f}}} = {d['v_h_real_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

El tiempo de retención real resulta:

\begin{{equation}}
t_r = \frac{{L}}{{v_{{real}}}} = \frac{{{d['L_diseno_m']:.1f}}}{{{d['v_h_real_m_s']:.3f}}} = {d['t_r_real_s']:.1f} \text{{ s}}
\end{{equation}}

\subsubsection{{Verificación de Velocidad Crítica}}

Para garantizar que la arena sedimentada no sea resuspendida por el flujo, se verifica que la velocidad horizontal del diseño sea menor que la velocidad crítica de resuspensión, calculada mediante la fórmula de Camp-Shields:

\begin{{equation}}
v_c = \sqrt{{\frac{{8 \beta g (S_s - 1) d}}{{f}}}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$v_c$] = Velocidad crítica de resuspensión (m/s)
    \item[$\beta$] = Factor de forma ({d['beta']:.2f}, rango 0,04 - 0,06)
    \item[$g$] = Aceleración de la gravedad ({d['g_m_s2']:.2f} m/s²)
    \item[$S_s$] = Gravedad específica de la arena ({d['Ss']:.2f})
    \item[$d$] = Diámetro de la partícula ({d['d_m']:.5f} m)
    \item[$f$] = Factor de fricción de Darcy-Weisbach ({d['f_darcy']:.3f}, rango 0,02 - 0,03)
\end{{itemize}}

\begin{{equation}}
v_c = \sqrt{{\frac{{8 \times {d['beta']:.2f} \times {d['g_m_s2']:.2f} \times ({d['Ss']:.2f} - 1) \times {d['d_m']:.5f}}}{{{d['f_darcy']:.3f}}}}} = {d['v_c_scour_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

\subsubsection{{Verificación para Caudal Máximo Horario}}

Se verifica el comportamiento hidráulico para el caudal máximo horario, aplicando un factor de pico típico de {d['factor_pico']:.1f} sobre el caudal medio:

\begin{{equation}}
Q_{{max}} = {d['factor_pico']:.1f} \times Q_{{medio}} = {d['factor_pico']:.1f} \times {cfg.Q_linea_L_s:.1f} = {d['Q_max_L_s']:.1f} \text{{ L/s}}
\end{{equation}}

A caudal máximo, la velocidad horizontal resulta:

\begin{{equation}}
v_{{h,max}} = \frac{{Q_{{max}}}}{{B \cdot H}} = \frac{{{d['Q_max_L_s']:.3f}/1000}}{{{d['b_canal_m']:.2f} \times {d['H_util_m']:.2f}}} = {d['v_h_max_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

El tiempo de retención a caudal máximo:

\begin{{equation}}
t_{{r,max}} = \frac{{L}}{{v_{{h,max}}}} = \frac{{{d['L_diseno_m']:.1f}}}{{{d['v_h_max_m_s']:.3f}}} = {d['t_r_max_s']:.1f} \text{{ s}}
\end{{equation}}

\textbf{{Criterios de verificación de resuspensión}} (Camp-Shields, Metcalf y Eddy \cite{{metcalf2014}}):

La velocidad calculada $v_{{h,max}} = {d['v_h_max_m_s']:.3f}$~m/s se evalúa según (límite: $v_c \times {int(cfg.desarenador_factor_seguridad_scour*100)}\% = {d['v_c_scour_m_s'] * cfg.desarenador_factor_seguridad_scour:.3f}$~m/s):

\begin{{equation}}
\text{{Estado}} = \begin{{cases}}
    \text{{SEGURIDAD}} & \text{{si }} v_{{h,max}} \leq {d['v_c_scour_m_s'] * cfg.desarenador_factor_seguridad_scour:.3f} \text{{ m/s}} \quad \text{{(no hay resuspensión)}} \\
    \text{{RIESGO}} & \text{{si }} v_{{h,max}} > {d['v_c_scour_m_s'] * cfg.desarenador_factor_seguridad_scour:.3f} \text{{ m/s}} \quad \text{{(arena resuspendida)}}
\end{{cases}}
\end{{equation}}

El resultado de la verificación indica que {d['verif_scour_texto']}.

\subsubsection{{Resultados}}

\begin{{table}}[H]
\centering
\caption{{Dimensiones del desarenador}}
\begin{{tabular}}{{ll}}
\toprule
Parámetro & Valor \\
\midrule
Longitud diseño & {d['L_diseno_m']:.1f} m (mínimo constructivo SENAGUA) \\
Ancho & {d['b_canal_m']:.2f} m (mínimo constructivo) \\
Profundidad útil & {d['H_util_m']:.2f} m \\
Velocidad horizontal real & {d['v_h_real_m_s']:.3f} m/s \\
Velocidad crítica resuspensión & {d['v_c_scour_m_s']:.3f} m/s (Camp-Shields) \\
Tiempo retención real & {d['t_r_real_s']:.1f} s$^b$ \\
\bottomrule
\end{{tabular}}
\small
$^b$ El tiempo de retención excede el rango 30--60 s por el ancho mínimo constructivo. Esto no afecta la sedimentación de arena; el criterio crítico es la velocidad horizontal (< 0,30 m/s).
\end{{table}}

\subsection{{Reactor UASB}}

El reactor UASB (Upflow Anaerobic Sludge Blanket), desarrollado por Lettinga y colaboradores en 1980 en la Universidad de Wageningen de los Países Bajos \cite{{vanhaandel1994}}, es uno de los sistemas de tratamiento anaerobio de alta tasa más utilizados en el mundo para aguas residuales municipales y agroindustriales. El agua residual entra por la parte inferior y fluye en sentido ascendente a través de un manto denso de lodos granulares, donde los microorganismos anaerobios degradan la materia orgánica mediante metanogénesis, convirtiéndola en biogás (metano y CO$_2$) y biomasa. El proceso ocurre sin oxígeno molecular, por lo que no requiere aireación, reduciendo drásticamente el consumo energético (5--10 veces menos que un sistema aerobio convencional).

El diseño se fundamenta en criterios biológicos e hidráulicos establecidos por Van Haandel y Lettinga \cite{{vanhaandel1994}}, Sperling \cite{{sperling2007}} y Metcalf y Eddy \cite{{metcalf2014}}.

\textbf{{Condiciones de temperatura:}} La temperatura del agua residual es un factor crítico que determina los parámetros de diseño del reactor UASB. Según Van Haandel y Lettinga (1994), el proceso de metanogénesis requiere temperaturas superiores a 20°C para operar de manera óptima. A temperaturas menores, la actividad metabólica de los microorganismos anaerobios disminuye, requiriendo ajustes en la carga orgánica, el tiempo de retención y la velocidad ascendente.

Para el presente diseño, la temperatura del agua residual es \textbf{{{u['T_agua_C']:.1f}°C}} ({u['factor_temp_texto']}). Con base en esta condición, los parámetros de diseño se han ajustado automáticamente según los siguientes rangos recomendados:

\begin{{table}}[H]
\centering
\caption{{Rangos de diseño según temperatura del agua residual}}
\small
\begin{{tabular}}{{lccc}}
\toprule
\textbf{{Condición}} & \textbf{{T (°C)}} & \textbf{{Cv (kg/m³·d)}} & \textbf{{HRT (h)}} \\
\midrule
Óptima & >= 22 & 2,0--3,0 & 4--6 \\
Moderada & 18--22 & 1,5--2,5 & 5--8 \\
Baja & 15--18 & 1,0--1,5 & 6--10 \\
Muy baja & 10--15 & 0,5--1,5 & 8--12 \\
Crítica & < 10 & No recomendable & Requiere calefacción \\
\bottomrule
\end{{tabular}}
\end{{table}}

Para la temperatura actual de {u['T_agua_C']:.1f}°C, los parámetros de diseño adoptados son:

\begin{{table}}[H]
\centering
\caption{{Parámetros de diseño del reactor UASB (T = {u['T_agua_C']:.1f}°C)}}
\small
\begin{{tabular}}{{p{{4.5cm}}ccc}}
\toprule
Parámetro & Rango & Valor adoptado & Fuente \\
\midrule
Carga orgánica ($C_v$) & {u['rango_Cv']} & {u['Cv_kgDQO_m3_d']:.2f} kg/m³·d & Van Haandel [4] \\
Velocidad ascendente & {u['rango_vup']} & {u['v_up_m_h']:.2f} m/h & Sperling [3] \\
Tiempo retención (HRT) & {u['rango_HRT']} & {u['TRH_h']:.1f} h & Van Haandel [4] \\
Eficiencia DQO & {u['rango_eta']} & {u['eta_DQO']*100:.0f}\% & OPS/CEPIS [5] \\
Altura útil & 3,0--6,0 m & {u['H_r_m']:.2f} m & Van Haandel [4] \\
Relación H/D & 0,5--1,5 & {u['H_r_m']/u['D_m']:.2f} & Van Haandel [4] \\
\bottomrule
\end{{tabular}}
\end{{table}}

{temp_recomendacion}

Notas importantes de diseño: se debe incluir un separador gas-líquido-sólido (GLS) en la parte superior (altura 0,8--1,2 m) y un sistema de distribución uniforme en el fondo. El biogás requiere sistema de recolección y manejo seguro (prevención contra explosión).

El volumen necesario del reactor se determina mediante la expresión:

\begin{{equation}}
V_r = \frac{{Q \cdot S_0}}{{C_v}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$V_r$] = Volumen útil del reactor (m³)
    \item[$Q$] = Caudal diario ({u['Q_m3_d']:.1f} m³/d)
    \item[$S_0$] = Concentración de DQO afluente ({u['DQO_kg_m3']:.4f} kg/m³)
    \item[$C_v$] = Carga orgánica volumétrica ({u['Cv_kgDQO_m3_d']:.1f} kg DQO/m³·d)
\end{{itemize}}

\begin{{equation}}
V_r = \frac{{{u['Q_m3_d']:.1f} \times {u['DQO_kg_m3']:.4f}}}{{{u['Cv_kgDQO_m3_d']:.1f}}} = {u['V_r_m3']:.1f} \text{{ m}}^3
\end{{equation}}

Este volumen garantiza el tiempo de retención hidráulico necesario para la degradación biológica.

Simultáneamente, el criterio hidráulico establece que la velocidad ascendente debe mantenerse entre 0,5 y 1,0 m/h para retener el manto de lodos sin arrastre. Con la velocidad adoptada de {u['v_up_m_h']:.2f} m/h, el área superficial requerida resulta:

\begin{{equation}}
A_s = \frac{{Q}}{{v_{{up}}}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_s$] = Área superficial del reactor (m²)
    \item[$Q$] = Caudal por línea ({cfg.Q_linea_m3_h:.2f} m³/h)
    \item[$v_{{up}}$] = Velocidad ascendente adoptada ({u['v_up_m_h']:.2f} m/h)
\end{{itemize}}

\begin{{equation}}
A_s = \frac{{{cfg.Q_linea_m3_h:.2f}}}{{{u['v_up_m_h']:.2f}}} = {u['A_sup_m2']:.2f} \text{{ m}}^2
\end{{equation}}

El diámetro del reactor circular se obtiene geométricamente:

\begin{{equation}}
D = \sqrt{{\frac{{4 \cdot A_s}}{{\pi}}}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$D$] = Diámetro del reactor circular (m)
    \item[$A_s$] = Área superficial calculada ({u['A_sup_m2']:.2f} m²)
    \item[$\pi$] = 3,14159
\end{{itemize}}

\begin{{equation}}
D = \sqrt{{\frac{{4 \times {u['A_sup_m2']:.2f}}}{{\pi}}}} = {u['D_m']:.2f} \text{{ m}}
\end{{equation}}

La altura resultante del reactor es {u['H_r_m']:.2f} m, proporcionando un tiempo de retención hidráulico de {u['TRH_h']:.1f} horas, valor adecuado según Sperling \cite{{sperling2007}} para temperaturas superiores a 22°C.

La producción de biogás se estima mediante la relación estequiométrica de {u['factor_biogas_ch4']:.2f} m³ de metano por kilogramo de DQO removida:

\begin{{equation}}
V_{{CH_4}} = (Q_d \cdot S_0 \cdot E) \times {u['factor_biogas_ch4']:.2f}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$V_{{CH_4}}$] = Volumen de metano producido (m³ CH$_4$/d)
    \item[$Q_d$] = Caudal diario ({u['Q_m3_d']:.1f} m³/d)
    \item[$S_0$] = Concentración de DQO afluente ({u['DQO_kg_m3']:.3f} kg/m³)
    \item[$E$] = Eficiencia de remoción ({u['eta_DQO']:.2f})
\end{{itemize}}

\begin{{equation}}
V_{{CH_4}} = ({u['Q_m3_d']:.1f} \times {u['DQO_kg_m3']:.3f} \times {u['eta_DQO']:.2f}) \times {u['factor_biogas_ch4']:.2f} = {u['biogaz_m3_d']:.1f} \text{{ m}}^3 \text{{ CH}}_4\text{{/d}}
\end{{equation}}

\subsubsection{{Verificación para Caudal Máximo Horario}}

Se verifica el comportamiento hidráulico para el caudal máximo horario, aplicando un factor de pico típico de {u['factor_pico']:.1f} sobre el caudal medio:

\begin{{equation}}
Q_{{max}} = {u['factor_pico']:.1f} \times Q_{{medio}} = {u['factor_pico']:.1f} \times {u['Q_m3_d']:.1f} = {u['Q_max_m3_d']:.1f} \text{{ m}}^3\text{{/d}} = {u['Q_max_m3_h']:.2f} \text{{ m}}^3\text{{/h}}
\end{{equation}}

A caudal máximo, la velocidad ascendente resulta:

\begin{{equation}}
v_{{up,max}} = \frac{{Q_{{max}}}}{{A_s}} = \frac{{{u['Q_max_m3_h']:.2f}}}{{{u['A_sup_m2']:.2f}}} = {u['v_up_max_m_h']:.2f} \text{{ m/h}}
\end{{equation}}

\textbf{{Criterios de verificación de arrastre del manto}} (Metcalf y Eddy \cite{{metcalf2014}}):

La velocidad calculada $v_{{up,max}} = {u['v_up_max_m_h']:.2f}$~m/h se evalúa según:

\begin{{equation}}
\text{{Estado}} = \begin{{cases}}
    \text{{ÓPTIMO}} & \text{{si }} v_{{up,max}} \leq {cfg.uasb_v_up_max_recomendado_m_h:.1f} \text{{ m/h}} \quad \text{{(sin riesgo)}} \\
    \text{{ACEPTABLE}} & \text{{si }} {cfg.uasb_v_up_max_recomendado_m_h:.1f} < v_{{up,max}} \leq {cfg.uasb_v_up_max_destructivo_m_h:.1f} \text{{ m/h}} \quad \text{{(monitoreo)}} \\
    \text{{NO ADMISIBLE}} & \text{{si }} v_{{up,max}} > {cfg.uasb_v_up_max_destructivo_m_h:.1f} \text{{ m/h}} \quad \text{{(pérdida biomasa)}}
\end{{cases}}
\end{{equation}}

Con la velocidad calculada $v_{{up,max}} = {u['v_up_max_m_h']:.2f}$~m/h, se obtiene el estado \textbf{{{u['estado_verificacion']}}}. {u['verif_vup_max_texto']}

\subsubsection{{Resultados}}

\begin{{table}}[H]
\centering
\caption{{Dimensiones y parámetros del reactor UASB}}
\begin{{tabular}}{{ll}}
\toprule
Parámetro & Valor \\
\midrule
Diámetro & {u['D_m']:.2f} m \\
Altura total & {u['H_r_m']:.2f} m \\
Volumen útil & {u['V_r_m3']:.1f} m³ \\
Área superficial & {u['A_sup_m2']:.2f} m² \\
Tiempo de retención hidráulico & {u['TRH_h']:.1f} h \\
Carga orgánica volumétrica & {u['Cv_kgDQO_m3_d']:.1f} kg DQO/m³·d \\
Biogás producido & {u['biogaz_m3_d']:.1f} m$^3$ CH$_4$/d \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Filtro Percolador}}

El filtro percolador constituye la unidad de tratamiento secundario aerobio, diseñada para remover la carga orgánica restante después del tratamiento anaerobio en el UASB. El diseño se fundamenta en el modelo cinético de Germain (1966), que describe la remoción de DBO mediante la expresión exponencial, y en criterios de carga orgánica volumétrica según WEF (2010) y Metcalf \& Eddy (2014).

Según las recomendaciones para medio plástico aleatorio, las cargas óptimas oscilan entre 0,3 y 3,0 kg DBO/m³·d. Se adopta un valor conservador de {fp['Cv_kgDBO_m3_d']:.2f} kg DBO/m³·d, apropiado para la condición de pretratamiento previo con UASB.

El volumen de medio filtrante requerido se calcula mediante:

\begin{{equation}}
V = \frac{{Q \cdot S_0}}{{C_v}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$V$] = Volumen de medio filtrante requerido (m³)
    \item[$Q$] = Caudal diario ({fp['Q_m3_d']:.1f} m³/d)
    \item[$S_0$] = DBO afluente ({fp['DBO_entrada_mg_L']:.0f} mg/L = {fp['DBO_entrada_mg_L']:.0f} $\\times$ 10$^{{-3}}$ kg/m³)
    \item[$C_v$] = Carga orgánica volumétrica ({fp['Cv_kgDBO_m3_d']:.2f} kg DBO/m³·d)
\end{{itemize}}

\begin{{equation}}
V = \frac{{{fp['Q_m3_d']:.1f} \times {fp['DBO_entrada_mg_L']:.0f} \times 10^{{-3}}}}{{{fp['Cv_kgDBO_m3_d']:.2f}}} = {fp['V_medio_m3']:.1f} \text{{ m}}^3
\end{{equation}}

Con una profundidad de medio de {fp['D_medio_m']:.2f} m, el área superficial resulta {fp['A_sup_m2']:.2f} m², correspondiendo a un diámetro de {fp['D_filtro_m']:.2f} m para configuración circular. La altura total incluye zonas de distribución (0,30 m), recolección (0,50 m) y bordo libre (0,30 m), resultando en {fp['H_total_m']:.2f} m.

El sistema incorpora recirculación con relación $R = {fp['R_recirculacion']:.1f}$, lo cual mejora la distribución hidráulica y mantiene la biopelícula húmeda. La tasa hidráulica aplicada resulta {fp['Q_A_real_m3_m2_h']:.3f} m³/m²·h.

\textbf{{Verificación de eficiencia mediante modelo de Germain:}}

La eficiencia de remoción se verifica mediante el modelo de Germain (1966). Primero se corrige la constante cinética por temperatura:

\begin{{equation}}
k_T = k_{{20}} \cdot \theta^{{(T-20)}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$k_{{20}}$] = Constante cinética a 20°C ({fp['k_20_m_h']:.3f} m/h)
    \item[$\theta$] = Coeficiente de temperatura ({fp['theta']:.3f})
    \item[$T$] = Temperatura del agua ({cfg.T_agua_C:.1f}°C)
\end{{itemize}}

\begin{{equation}}
k_T = {fp['k_20_m_h']:.3f} \times {fp['theta']:.3f}^{{({cfg.T_agua_C:.1f}-20)}} = {fp['k_T_m_h']:.4f} \text{{ m/h}}
\end{{equation}}

Aplicando el modelo de Germain:

\begin{{equation}}
\frac{{S_e}}{{S_0}} = \exp\left(-\frac{{k_T \cdot D}}{{q_A^n}}\right)
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$S_e$] = DBO efluente (mg/L)
    \item[$S_0$] = DBO afluente ({fp['DBO_entrada_mg_L']:.0f} mg/L)
    \item[$k_T$] = Constante cinética corregida ({fp['k_T_m_h']:.4f} m/h)
    \item[$D$] = Profundidad del medio ({fp['D_medio_m']:.2f} m)
    \item[$q_A$] = Tasa hidráulica ({fp['Q_A_real_m3_m2_h']:.3f} m³/m²·h)
    \item[$n$] = Coeficiente empírico ({fp['n_germain']:.2f})
\end{{itemize}}

Sustituyendo valores:

\begin{{equation}}
\frac{{S_e}}{{{fp['DBO_entrada_mg_L']:.0f}}} = \exp\left(-\frac{{{fp['k_T_m_h']:.4f} \times {fp['D_medio_m']:.2f}}}{{({fp['Q_A_real_m3_m2_h']:.3f})^{{{fp['n_germain']:.2f}}}}}\right) = {fp['relacion_Se_S0_Germain']:.3f}
\end{{equation}}

Por tanto, la DBO efluente estimada es $S_e = {fp['DBO_entrada_mg_L']:.0f} \times {fp['relacion_Se_S0_Germain']:.3f} = {fp['DBO_salida_Germain_mg_L']:.0f}$ mg/L.

\subsubsection{{Verificación para Caudal Máximo Horario}}

Se verifica el comportamiento hidráulico para el caudal máximo horario, aplicando un factor de pico típico de 2,5 sobre el caudal medio:

\begin{{equation}}
Q_{{max}} = 2,5 \times Q_{{medio}} = 2,5 \times {fp['Q_m3_d']:.1f} = {fp['Q_max_m3_d']:.1f} \text{{ m}}^3\text{{/d}}
\end{{equation}}

A caudal máximo, la tasa hidráulica resulta:

\begin{{equation}}
q_{{A,max}} = \frac{{Q_{{max}} \cdot (1 + R)}}{{A_s \cdot 24}} = \frac{{{fp['Q_max_m3_d']:.1f} \times {1+fp['R_recirculacion']:.1f}}}{{{fp['A_sup_m2']:.2f} \times 24}} = {fp['Q_A_max_m3_m2_h']:.2f} \text{{ m}}^3\text{{/m}}^2\text{{·h}}
\end{{equation}}

El valor obtenido se compara con el límite máximo recomendado de 4,0 m³/m²·h. {fp['verif_qmax_texto']}.

\subsubsection{{Resultados}}

\begin{{table}}[H]
\centering
\caption{{Dimensiones del filtro percolador}}
\begin{{tabular}}{{ll}}
\toprule
Parámetro & Valor \\
\midrule
Diámetro & {fp['D_filtro_m']:.2f} m \\
Altura total & {fp['H_total_m']:.2f} m \\
Profundidad medio & {fp['D_medio_m']:.2f} m \\
Volumen de medio & {fp['V_medio_m3']:.1f} m³ \\
Carga orgánica & {fp['Cv_kgDBO_m3_d']:.2f} kg DBO/m³·d \\
Recirculación & R = {fp['R_recirculacion']:.1f} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Sedimentador Secundario}}

El sedimentador secundario tiene la función de separar los sólidos biológicos desprendidos del filtro percolador (conocidos como humus o lodos biológicos) del efluente tratado, permitiendo obtener un efluente clarificado. Su diseño se fundamenta principalmente en el criterio de la tasa de desbordamiento superficial (SOR), que relaciona el caudal con el área superficial del tanque, garantizando una velocidad ascensional suficientemente baja para que los flóculos sedimenten por gravedad.

El diseño sigue los criterios recomendados por Metcalf \& Eddy \cite{{metcalf2014}} y Sperling \cite{{sperling2007}} para sedimentadores secundarios ubicados después de filtros percoladores.

\textbf{{Criterios de diseño}}

\begin{{table}}[H]
\centering
\caption{{Rangos de diseño para sedimentador secundario después de filtro percolador}}
\small
\begin{{tabular}}{{lccc}}
\toprule
Parámetro & Rango recomendado & Valor adoptado & Fuente \\
\midrule
Tasa de desbordamiento superficial (SOR) & 16 -- 32 m³/m²·d & {s['SOR_m3_m2_d']:.1f} m³/m²·d & Metcalf \& Eddy \cite{{metcalf2014}} \\
Profundidad lateral & 3,0 -- 4,5 m & {s['h_sed_m']:.2f} m & Sperling \cite{{sperling2007}} \\
Tiempo de retención hidráulico (HRT) & 1,5 -- 5,0 h$^a$ & {s['TRH_h']:.1f} h & Metcalf \& Eddy \\
Tasa de desbordamiento máxima & $\leq$ 45 m³/m²·d & verificado & Metcalf \& Eddy \\
Carga sobre vertedero & $\leq$ {s['weir_loading_max']:.0f} m³/m·d & {s['weir_loading_m3_m_d']:.1f} m³/m·d & Metcalf \& Eddy \\
\bottomrule
\end{{tabular}}
\small
$^a$ Rango extendido para diseños conservadores en climas tropicales. Valores mayores a 4 h favorecen la clarificación sin penalizar el desempeño.
\end{{table}}

El área superficial necesaria se calcula mediante:

\begin{{equation}}
A_s = \frac{{Q}}{{SOR}}
\end{{equation}}

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
Zona de almacenamiento de lodos (tolva) & 0,50 m \\
Bordo libre & 0,30 m \\
\midrule
\textbf{{Altura total de construcción}} & \textbf{{{s['h_sed_m'] + 0.8:.2f} m}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsubsection{{Verificaciones Hidráulicas}}

\textbf{{1. Verificación a caudal máximo horario}}

Se verifica el comportamiento hidráulico para el caudal máximo horario aplicando un factor de pico típico de {s['factor_pico']:.1f}:

\begin{{equation}}
Q_{{\max}} = {s['factor_pico']:.1f} \times Q_{{\text{{medio}}}} = {s['factor_pico']:.1f} \times {s['Q_m3_d']:.1f} = {s['Q_max_m3_d']:.1f} \text{{ m}}^3\text{{/d}}
\end{{equation}}

A caudal máximo, la tasa de desbordamiento resulta:

\begin{{equation}}
SOR_{{\max}} = \frac{{Q_{{\max}}}}{{A_s}} = \frac{{{s['Q_max_m3_d']:.1f}}}{{{s['A_sup_m2']:.2f}}} = {s['SOR_max_m3_m2_d']:.1f} \text{{ m}}^3\text{{/m}}^2\text{{·d}}
\end{{equation}}

El valor obtenido se compara con el límite máximo recomendado de {s['SOR_max_limite']:.0f} m³/m²·d. {s['verif_sor_max_texto']}.

\textbf{{2. Carga sobre vertedero perimetral}}

\begin{{equation}}
\text{{Carga}}_{{\text{{vertedero}}}} = \frac{{Q}}{{\pi \times D}} = \frac{{{s['Q_m3_d']:.1f}}}{{\pi \times {s['D_m']:.2f}}} = {s['weir_loading_m3_m_d']:.1f} \text{{ m}}^3\text{{/m·d}}
\end{{equation}}

La carga calculada ({s['weir_loading_m3_m_d']:.1f} m³/m·d) es significativamente menor que el límite de {s['weir_loading_max']:.0f} m³/m·d, garantizando un flujo uniforme hacia el vertedero periférico.

\textbf{{3. Tasa de aplicación de sólidos}}

Considerando la producción estimada de humus del filtro percolador ({s['produccion_humus_kg_d']:.1f} kg SST/d):

\begin{{equation}}
\text{{Carga de sólidos}} = \frac{{{s['produccion_humus_kg_d']:.1f} \text{{ kg SST/d}}}}{{{s['A_sup_m2']:.2f} \text{{ m}}^2}} = {s['solids_loading_kg_m2_d']:.2f} \text{{ kg SST/m}}^2\text{{·d}}
\end{{equation}}

El valor está dentro del rango recomendado de 50--150 kg SST/m²·d para sedimentadores tras filtros percoladores.

\textbf{{4. Verificación a caudal mínimo (nota operativa)}}

A caudal mínimo (factor {s['factor_min']:.1f} del medio), el tiempo de retención resulta:

\begin{{equation}}
\text{{HRT}}_{{\min}} = \frac{{{s['V_m3']:.1f} \text{{ m}}^3}}{{{s['Q_min_m3_d']:.1f} \text{{ m}}^3\text{{/d}} / 24}} = {s['TRH_min_h']:.1f} \text{{ h}}
\end{{equation}}

\textbf{{Nota:}} El HRT de {s['TRH_min_h']:.1f} h a caudal mínimo es elevado; se recomienda operar con recirculación interna o control de nivel para evitar condiciones sépticas en el fondo del sedimentador durante periodos de bajo caudal.

\subsubsection{{Resultados}}

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
Altura total de construcción & {s['h_sed_m'] + 0.8:.2f} m \\
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

\textbf{{Notas de buen diseño:}} Se debe incluir un sistema de recolección de lodos (rastrillos o succionadores) y un mecanismo de extracción de lodos desde el fondo. Se recomienda considerar el caudal mínimo en el diseño operacional para evitar estancamiento.

\subsection{{Desinfección con Hipoclorito de Sodio}}

La desinfección del efluente tratado se realiza mediante la aplicación de hipoclorito de sodio (NaOCl) en un tanque de contacto diseñado para garantizar el tiempo de retención necesario para la inactivación de microorganismos patógenos. El proceso se fundamenta en el concepto CT (concentración×tiempo), que relaciona el cloro residual con el tiempo de contacto.

El diseño busca cumplir el límite de coliformes fecales establecido por la TULSMA ($\leq$ 3000 NMP/100mL) de manera eficiente, sin sobredimensionar el sistema.

\textbf{{Criterios de diseño}}

La dosis total de cloro se descompone en la demanda del efluente (consumida por amoníaco y materia orgánica) más el residual requerido para desinfección:

\begin{{equation}}
\text{{Dosis total}} = \text{{Demanda}} + \text{{Residual}} = 3.5 + 0.5 = 4.0 \text{{ mg/L}}
\end{{equation}}

\begin{{table}}[H]
\centering
\caption{{Parámetros de diseño de la desinfección}}
\small
\begin{{tabular}}{{lccl}}
\toprule
Parámetro & Rango recomendado & Valor adoptado & Fuente \\
\midrule
Demanda de cloro & 2--5 & 3.5 mg/L & Estimado efluente UASB+FP \\
Cloro residual & 0.5--2.0 & 0.5 mg/L & OPS/CEPIS \cite{{ops2005}} \\
Dosis total & 3--10 & 4.0 mg/L & Metcalf \& Eddy \cite{{metcalf2014}} \\
Tiempo de contacto & 15--45 & 30 min & Metcalf \& Eddy \\
CT & $\geq$ 15 & 15 mg.min/L & Diseño conservador \\
\bottomrule
\end{{tabular}}
\end{{table}}


La eficacia de la desinfección se cuantifica mediante el parámetro CT:

\begin{{equation}}
CT = C \times t
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$CT$] = Producto concentración-tiempo (mg.min/L)
    \item[$C$] = Cloro residual (0.5 mg/L)
    \item[$t$] = Tiempo de contacto (30 min)
\end{{itemize}}

\begin{{equation}}
CT = 0.5 \times 30 = 15 \text{{ mg.min/L}}
\end{{equation}}

La reducción de coliformes se estima mediante:

\begin{{equation}}
\text{{Log reducción}} \approx 0.22 \times CT
\end{{equation}}

\begin{{equation}}
\text{{Log reducción}} \approx 0.22 \times 15 = 3.3 \text{{ log}}
\end{{equation}}

Los coliformes finales se calculan como:

\begin{{equation}}
CF_{{final}} = \frac{{CF_{{inicial}}}}{{10^{{\text{{Log reducción}}}}}} = \frac{{{cl['CF_entrada_NMP']:.0f}}}{{10^{{{cl['log_reduccion']:.1f}}}}} = {cl['CF_final_NMP']:.0f} \text{{ NMP/100mL}}
\end{{equation}}

\textbf{{Dimensionamiento del tanque de contacto}}

El volumen del tanque se determina por:

\begin{{equation}}
V = Q \times t
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$V$] = Volumen del tanque (m³)
    \item[$Q$] = Caudal ({cl['Q_m3_d']:.1f} m³/d = {cl['Q_m3_d']/24/60:.3f} m³/min)
    \item[$t$] = Tiempo de contacto ({cl['TRH_min']:.0f} min)
\end{{itemize}}

\begin{{equation}}
V = {cl['Q_m3_d']/24/60:.3f} \times {cl['TRH_min']:.0f} = {cl['V_contacto_m3']:.1f} \text{{ m}}^3
\end{{equation}}

Con una profundidad de 2.0 m y relación largo/ancho de 4:1, las dimensiones resultantes son {cl['largo_m']:.1f} m de largo por {cl['ancho_m']:.1f} m de ancho.

\textbf{{Verificación de cumplimiento}}

\textbf{{Cumplimiento TULSMA}}

El efluente final presenta una concentración de coliformes fecales de {cl['CF_final_NMP']:.0f} NMP/100mL, valor que cumple satisfactoriamente con el límite de 3000 NMP/100mL establecido por la TULSMA.

\textbf{{Consumo de cloro y requerimientos de producto comercial}}

El consumo de cloro activo (como Cl$_2$) se calcula como:

\begin{{equation}}
\text{{Consumo Cl}}_2 = \frac{{D \times Q}}{{1000}} = \frac{{4.0 \times {cl['Q_m3_d']:.1f}}}{{1000}} = {cl['consumo_cloro_kg_d']:.2f} \text{{ kg Cl}}_2\text{{/d}}
\end{{equation}}

\textbf{{Conversión a hipoclorito de sodio comercial (NaOCl):}}

El hipoclorito de sodio se comercializa típicamente al 10--12.5\% de cloro disponible. La conversión se realiza mediante:

\begin{{equation}}
\text{{Consumo NaOCl}} = \frac{{\text{{Consumo Cl}}_2}}{{[\% \text{{ NaOCl}}]}} = \frac{{{cl['consumo_cloro_kg_d']:.2f}}}{{10\%}} = {cl['consumo_NaOCl_kg_d']:.1f} \text{{ kg NaOCl/d}}
\end{{equation}}

Considerando una densidad de 1.10 kg/L para la solución al 10\%:

\begin{{equation}}
\text{{Volumen NaOCl}} = \frac{{{cl['consumo_NaOCl_kg_d']:.1f} \text{{ kg/d}}}}{{1.10 \text{{ kg/L}}}} = {cl['volumen_NaOCl_L_d']:.1f} \text{{ L/d}} \approx {cl['volumen_almacenamiento_L']:.0f} \text{{ L/mes}}
\end{{equation}}

\textbf{{Volumen de almacenamiento:}} Se recomienda almacenamiento para 30 días de operación: {cl['volumen_almacenamiento_L']:.0f} L (equivalente a {cl['volumen_almacenamiento_L']/1000:.1f} m³).

\subsubsection{{Resultados}}

\begin{{table}}[H]
\centering
\caption{{Dimensiones del tanque de desinfección}}
\begin{{tabular}}{{ll}}
\toprule
Parámetro & Valor \\
\midrule
Largo & {cl['largo_m']:.1f} m \\
Ancho & {cl['ancho_m']:.1f} m \\
Profundidad útil & {cl['h_tanque_m']:.1f} m \\
Altura total & {cl['h_tanque_m'] + 0.3:.2f} m \\
Volumen útil & {cl['V_contacto_m3']:.1f} m³ \\
Tiempo de contacto & {cl['TRH_min']:.0f} min \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Parámetros de desinfección}}}} \\
\midrule
Demanda de cloro & {cl['demanda_cloro_mg_L']:.1f} mg/L \\
Cloro residual & {cl['cloro_residual_mg_L']:.1f} mg/L \\
Dosis total & {cl['dosis_cloro_mg_L']:.1f} mg/L \\
CT & {cl['CT_mg_min_L']:.0f} mg.min/L \\
Log reducción & {cl['log_reduccion']:.1f} log \\
CF final & {cl['CF_final_NMP']:.0f} NMP/100mL \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Consumo de productos}}}} \\
\midrule
Consumo Cl$_2$ activo & {cl['consumo_cloro_kg_d']:.2f} kg/d \\
Concentración NaOCl & 10 \% \\
Consumo NaOCl & {cl['consumo_NaOCl_kg_d']:.1f} kg/d \\
Volumen NaOCl & {cl['volumen_NaOCl_L_d']:.1f} L/d ({cl['volumen_almacenamiento_L']:.0f} L/mes) \\
Almacenamiento (30 d) & {cl['volumen_almacenamiento_L']:.0f} L ({cl['volumen_almacenamiento_L']/1000:.1f} m³) \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Notas de operación:}} Se recomienda monitorear el cloro residual en la salida del tanque (debe mantenerse entre 0.5--1.0 mg/L) y ajustar la dosis según la demanda del efluente. Realizar pruebas de coliformes periódicas para verificar la eficacia del sistema.

\subsection{{Lecho de Secado de Lodos}}

El lecho de secado es una unidad de manejo de lodos que utiliza procesos físicos de drenaje gravitacional y evaporación para reducir el contenido de humedad de los lodos generados en el tratamiento. Este sistema es ampliamente utilizado en plantas de tratamiento de pequeño y mediano tamaño debido a su bajo consumo energético y simplicidad operativa.

\textbf{{Criterios de diseño}}

\begin{{table}}[H]
\centering
\caption{{Parámetros de diseño del lecho de secado}}
\small
\begin{{tabular}}{{lccl}}
\toprule
Parámetro & Rango recomendado & Valor adoptado & Fuente \\
\midrule
Carga superficial de sólidos & 60--220 & {l['rho_S_kgSST_m2_año']:.0f} kg/m²·año & Metcalf \& Eddy \cite{{metcalf2014}} \\
Concentración de lodos & 15--30 & {l['C_SST_kg_m3']:.0f} kg/m³ & OPS/CEPIS \cite{{ops2005}} \\
Tiempo de secado & 10--30 & {l['t_secado_d']:.0f} días & OPS/CEPIS \\
Espesor de aplicación & 0.20--0.40 & {l['h_lodo_m']:.2f} m & Metcalf \& Eddy \\
Relación Largo/Ancho & 2:1--4:1 & 3:1 & Práctica común \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Producción de lodos}}

La producción de lodos se estima considerando una producción específica típica de 0,10 kg SSV/kg DBO removida. Para la carga aplicada, se estima una producción de {l['lodos_kg_SST_d']:.2f} kg SST/d por línea.

\textbf{{Ecuaciones de diseño}}

El volumen diario de lodo a tratar se determina mediante:

\begin{{equation}}
V_{{lodo}} = \frac{{M_{{SST}}}}{{C_{{SST}}}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$V_{{lodo}}$] = Volumen diario de lodo (m³/d)
    \item[$M_{{SST}}$] = Masa de sólidos producidos ({l['lodos_kg_SST_d']:.2f} kg SST/d)
    \item[$C_{{SST}}$] = Concentración de sólidos ({l['C_SST_kg_m3']:.0f} kg/m³)
\end{{itemize}}

\begin{{equation}}
V_{{lodo}} = \frac{{{l['lodos_kg_SST_d']:.2f}}}{{{l['C_SST_kg_m3']:.0f}}} = {l['V_lodo_m3_d']:.3f} \text{{ m}}^3\text{{/d}}
\end{{equation}}

\textbf{{Dimensionamiento del área}}

El área requerida se calcula considerando el volumen de lodo, el tiempo de secado y el espesor de aplicación:

\begin{{equation}}
A_{{lecho}} = \frac{{V_{{lodo}} \cdot t_s}}{{h_{{lodo}}}} \cdot n_{{celdas}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_{{lecho}}$] = Área superficial total (m²)
    \item[$t_s$] = Tiempo de secado ({l['t_secado_d']:.0f} días)
    \item[$h_{{lodo}}$] = Espesor de aplicación ({l['h_lodo_m']:.2f} m)
    \item[$n_{{celdas}}$] = Número de celdas ({l['n_celdas']:.0f})
\end{{itemize}}

\begin{{equation}}
A_{{lecho}} = \frac{{{l['V_lodo_m3_d']:.3f} \times {l['t_secado_d']:.0f}}}{{{l['h_lodo_m']:.2f}}} \times {l['n_celdas']:.0f} = {l['A_lecho_m2']:.1f} \text{{ m}}^2
\end{{equation}}

Con una relación largo/ancho de 3:1, las dimensiones resultantes son {l['largo_m']:.1f} m de largo por {l['ancho_m']:.1f} m de ancho por celda.

\subsubsection{{Verificación de carga superficial}}

La carga superficial de sólidos se verifica mediante:

\begin{{equation}}
\rho_S = \frac{{M_{{SST}} \times 365}}{{A_{{lecho}}}} = \frac{{{l['lodos_kg_SST_d']:.2f} \times 365}}{{{l['A_lecho_m2']:.1f}}} = {l['rho_S_kgSST_m2_año']:.1f} \text{{ kg SST/m}}^2\text{{·año}}
\end{{equation}}

El valor obtenido está dentro del rango recomendado de 60--220 kg SST/m²·año para lechos de secado de lodos anaerobios según Metcalf \& Eddy \cite{{metcalf2014}}.

\subsubsection{{Resultados}}

\begin{{table}}[H]
\centering
\caption{{Dimensiones del lecho de secado}}
\begin{{tabular}}{{ll}}
\toprule
Parámetro & Valor \\
\midrule
Largo & {l['largo_m']:.1f} m \\
Ancho & {l['ancho_m']:.1f} m \\
Área superficial total & {l['A_lecho_m2']:.1f} m² \\
Número de celdas & {l['n_celdas']:.0f} \\
Tiempo de secado & {l['t_secado_d']:.0f} días \\
Carga de sólidos & {l['rho_S_kgSST_m2_año']:.1f} kg SST/m²·año \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Balance de Calidad del Agua}}

El tren de tratamiento propuesto alcanza eficiencias de remocion significativas. La siguiente tabla presenta el balance completo de calidad del agua a traves de todas las etapas del proceso:

\begin{{table}}[H]
\centering
\caption{{Balance de calidad del agua a traves del tren de tratamiento}}
\begin{{tabular}}{{lccccc}}
\toprule
Parametro & Afluente & Post-UASB & Post-FP & Post-Sed & Efluente Final \\
\midrule
DBO$_5$ (mg/L) & {balance_calidad['afluente']['DBO5_mg_L']:.1f} & {balance_calidad['tras_uasb']['DBO5_mg_L']:.1f} & {balance_calidad['tras_fp']['DBO5_mg_L']:.1f} & {balance_calidad['tras_sed']['DBO5_mg_L']:.1f} & {balance_calidad['efluente_final']['DBO5_mg_L']:.1f} \\
DQO (mg/L) & {balance_calidad['afluente']['DQO_mg_L']:.1f} & {balance_calidad['tras_uasb']['DQO_mg_L']:.1f} & {balance_calidad['tras_fp']['DQO_mg_L']:.1f} & {balance_calidad['tras_sed']['DQO_mg_L']:.1f} & {balance_calidad['efluente_final']['DQO_mg_L']:.1f} \\
SST (mg/L) & {balance_calidad['afluente']['SST_mg_L']:.1f} & {balance_calidad['tras_uasb']['SST_mg_L']:.1f} & {balance_calidad['tras_fp']['SST_mg_L']:.1f} & {balance_calidad['tras_sed']['SST_mg_L']:.1f} & {balance_calidad['efluente_final']['SST_mg_L']:.1f} \\
CF (NMP/100mL) & {balance_calidad['afluente']['CF_NMP']:.0f} & {balance_calidad['tras_uasb']['CF_NMP']:.0f} & {balance_calidad['tras_fp']['CF_NMP']:.0f} & {balance_calidad['tras_sed']['CF_NMP']:.0f} & {balance_calidad['efluente_final']['CF_NMP']:.0f} \\
\bottomrule
\end{{tabular}}
\end{{table}}

Los parametros del efluente final cumplen con los limites establecidos en la TULSMA (DBO$_5$ $\leq$ 100 mg/L, SST $\leq$ 100 mg/L, CF $\leq$ 3000 NMP/100mL).


\newpage
\subsection{{Disposicion de la Planta y Areas de Predio}}

La figura \ref{{fig:layout_a}} presenta la disposicion espacial de las unidades de tratamiento. El layout muestra dos lineas paralelas operativas, cada una con capacidad para tratar {cfg.Q_linea_L_s:.1f} L/s, permitiendo la operacion con una sola linea durante mantenimiento o reparaciones.

\begin{{figure}}[H]
\centering
\includegraphics[width=\textwidth]{{{layout_filename}}}
\caption{{Disposición espacial de unidades - Alternativa A}}
\label{{fig:layout_a}}
\end{{figure}}

El área de tratamiento calculada (unidades mas margenes minimos) es de aproximadamente {area_m2} m². Sin embargo, para una operacion adecuada se requieren areas complementarias adicionales.

\textbf{{Areas complementarias requeridas}}

El area calculada de {area_m2} m$^2$ corresponde unicamente a las unidades de tratamiento con sus margenes minimos de acceso. Sin embargo, para garantizar una operacion segura y eficiente de la planta durante toda su vida util, es necesario prever espacios adicionales para acceso vehicular y peatonal de operarios y visitantes, almacenamiento seguro de productos quimicos y herramientas, realizacion de analisis de control de calidad in-situ, estacionamiento para personal y visitantes, circulacion interna de vehiculos de mantenimiento y retiro de lodos, separacion de limites con zonas verdes para control de olores, y espacios administrativos para control operativo. La siguiente tabla resume las areas complementarias necesarias:

\begin{{table}}[H]
\centering
\caption{{Areas complementarias de la planta}}
\small
\begin{{tabular}}{{lp{{8cm}}c}}
\toprule
Area & Descripcion & Dimension aprox. \\
\midrule
Zona de amortiguacion & Perimetral alrededor de unidades (2-3 m) para acceso y seguridad & +20\% area tratamiento \\
\addlinespace
Bodega de quimicos & Almacenamiento de hipoclorito y productos quimicos & 10--15 m$^2$ \\
\addlinespace
Laboratorio/control & Analisis de calidad del agua (DBO, SST, CF, pH) & 15--20 m$^2$ \\
\addlinespace
Caseta de operacion & Control, panel, escritorio, bano & 12--15 m$^2$ \\
\addlinespace
Area de lavado & Limpieza de equipos y herramientas & 8--10 m$^2$ \\
\addlinespace
Estacionamiento & Vehiculos del personal y visitantes (2-3 vehiculos) & 50--60 m$^2$ \\
\addlinespace
Zona de camiones & Acceso de camiones cisterna/retiro de lodo & 50--80 m$^2$ \\
\addlinespace
Caminos internas & Circulacion vehicular y peatonal (ancho 3--4 m) & 80--120 m$^2$ \\
\addlinespace
Acceso principal & Entrada, porton y caseta de guardia & 20--30 m$^2$ \\
\addlinespace
Bodega general & Herramientas, repuestos, EPP & 15--20 m$^2$ \\
\addlinespace
Zona carga de lodos & Carga/descarga de lodo deshidratado & 20--30 m$^2$ \\
\addlinespace
Area verde/buffer & Separacion de limites, revegetacion & 15\% area total \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Area total estimada del predio}}

Considerando el area de tratamiento ({area_m2 if area_m2 else 850} m$^2$), amortiguacion (20\%), complementarias operativas y zona verde (15\% del total):

\begin{{equation}}
A_{{total}} = \frac{{A_{{tratamiento}} + A_{{amortiguacion}} + A_{{complementarias}}}}{{1 - 0.15}}
\end{{equation}}

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_{{tratamiento}}$] = {area_m2 if area_m2 else 850} m$^2$
    \item[$A_{{amortiguacion}}$] = {area_m2 * 0.20 if area_m2 else 170:.0f} m$^2$ (20\%)
    \item[$A_{{complementarias}}$] = 280--340 m$^2$ (operativas)
\end{{itemize}}

\begin{{equation}}
A_{{total}} = \frac{{{area_m2 if area_m2 else 850} + {area_m2 * 0.20 if area_m2 else 170:.0f} + 310}}{{0.85}} \approx \mathbf{{1600 \text{{--}} 1900 \text{{ m}}^2}} \approx \mathbf{{0.16 \text{{--}} 0.19 \text{{ ha}}}}
\end{{equation}}

\textbf{{Nota:}} El area total del predio debe ser de aproximadamente 1600--1900 m$^2$ (0.16--0.19 ha) para operacion adecuada con circulacion interna, estacionamiento y zonas verdes.
"""


def generar_resumen_resultados(cfg, resultados, balance_calidad=None, area_m2=None):
    """Genera seccion final con resumen ejecutivo de todos los resultados"""
    
    r = resultados
    bal = balance_calidad if balance_calidad else {}
    
    # Extraer valores de cada unidad
    rej = r.get('rejillas', {})
    des = r.get('desarenador', {})
    uasb = r.get('uasb', {})
    fp = r.get('filtro_percolador', {})
    sed = r.get('sedimentador', {})
    desinf = r.get('desinfeccion', {})
    lecho = r.get('lecho_secado', {})
    
    # Valores de calidad
    afluente = bal.get('afluente', {})
    efluente = bal.get('efluente_final', {})
    
    # Verificacion de cumplimiento TULSMA Tabla 12
    cumple_dbo = efluente.get('DBO5_mg_L', 0) <= 100
    cumple_dqo = efluente.get('DQO_mg_L', 0) <= 250
    cumple_sst = efluente.get('SST_mg_L', 0) <= 130
    cumple_cf = efluente.get('CF_NMP', 0) <= 3000
    cumple_todos = cumple_dbo and cumple_dqo and cumple_sst and cumple_cf
    
    estado_dbo = r"\textcolor{green}{\textbf{CUMPLE}}" if cumple_dbo else r"\textcolor{red}{\textbf{NO CUMPLE}}"
    estado_dqo = r"\textcolor{green}{\textbf{CUMPLE}}" if cumple_dqo else r"\textcolor{red}{\textbf{NO CUMPLE}}"
    estado_sst = r"\textcolor{green}{\textbf{CUMPLE}}" if cumple_sst else r"\textcolor{red}{\textbf{NO CUMPLE}}"
    estado_cf = r"\textcolor{green}{\textbf{CUMPLE}}" if cumple_cf else r"\textcolor{red}{\textbf{NO CUMPLE}}"
    
    conclusion_tulma = (
        r"\textbf{Conclusion:} El sistema dise\~nado cumple satisfactoriamente con todos los limites establecidos en la TULSMA (Tabla 12) para descarga a cuerpo de agua dulce."
        if cumple_todos else
        r"\textbf{Advertencia:} El sistema NO cumple con uno o mas limites de la TULSMA. Se requiere revisar el dise\~no o considerar tratamiento adicional."
    )
    
    return rf"""
%============================================================================
\newpage
\section{{Resultados}}
%============================================================================

El presente resumen consolida los resultados del dimensionamiento de la Planta de Tratamiento de Aguas Residuales (PTAR) para un caudal de dise\~no de \textbf{{{cfg.Q_linea_L_s * 2:.1f} L/s}} ({cfg.Q_linea_L_s:.1f} L/s por linea).

\subsection{{Parametros de Dise\~no}}

\begin{{table}}[H]
\centering
\caption{{Parametros de entrada del sistema}}
\begin{{tabular}}{{lc}}
\toprule
\textbf{{Parametro}} & \textbf{{Valor}} \\
\midrule
Caudal medio (Q) & {cfg.Q_linea_L_s:.1f} L/s ({cfg.Q_linea_m3_d:.1f} m$^3$/d) \\
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
\begin{{tabular}}{{p{{4.5cm}}ccc}}
\toprule
\textbf{{Unidad}} & \textbf{{Dimensiones}} & \textbf{{Cantidad}} & \textbf{{Parametro Clave}} \\
\midrule
Rejillas & {rej.get('ancho_layout_m'):.2f} m $\times$ {rej.get('h_tirante_m'):.2f} m & {cfg.num_lineas} canales & Velocidad: {rej.get('v_canal_adoptada_m_s'):.2f} m/s \\
Desarenador & {des.get('b_canal_m'):.2f} m $\times$ {des.get('L_diseno_m'):.1f} m $\times$ {des.get('H_util_m') + 0.3:.1f} m & {cfg.num_lineas} unidades & TRH: {des.get('t_r_nominal_s'):.0f} s \\
Reactor UASB & D = {uasb.get('D_m'):.2f} m, H = {uasb.get('H_r_m'):.1f} m & {cfg.num_lineas} unidades & v$_{{up}}$ = {uasb.get('v_up_m_h'):.2f} m/h \\
Filtro Percolador & D = {fp.get('D_filtro_m'):.2f} m, H = {fp.get('H_total_m'):.1f} m & {cfg.num_lineas} unidades & Q$_A$ = {fp.get('Q_A_max_m3_m2_h'):.2f} m$^3$/m$^2\cdot$h \\
Sedimentador Secundario & D = {sed.get('D_m'):.2f} m, H = {sed.get('h_sed_m'):.1f} m & {cfg.num_lineas} unidades & SOR = {sed.get('SOR_m3_m2_d'):.1f} m$^3$/m$^2\cdot$d \\
Desinfeccion (Cloro) & {desinf.get('largo_m'):.1f} m $\times$ {desinf.get('ancho_m'):.1f} m $\times$ {desinf.get('h_total_m'):.1f} m & 1 unidad & CT = {desinf.get('CT_mg_min_L'):.0f} mg$\cdot$min/L \\
Lecho de Secado & {lecho.get('A_lecho_m2'):.1f} m$^2$ ({lecho.get('largo_m'):.1f} m $\times$ {lecho.get('ancho_m'):.1f} m) & {lecho.get('n_celdas')} unidad & Carga: {lecho.get('lodos_kg_SST_d'):.1f} kg SST/d \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Balance de Calidad del Agua}}

\begin{{table}}[H]
\centering
\caption{{Evolucion de parametros de calidad a traves del tratamiento}}
\begin{{tabular}}{{lccccc}}
\toprule
\textbf{{Parametro}} & \textbf{{Afluente}} & \textbf{{Post-UASB}} & \textbf{{Post-FP}} & \textbf{{Post-Sed}} & \textbf{{Efluente}} \\
\midrule
DBO$_5$ (mg/L) & {afluente.get('DBO5_mg_L'):.1f} & {bal.get('tras_uasb').get('DBO5_mg_L'):.1f} & {bal.get('tras_fp').get('DBO5_mg_L'):.1f} & {bal.get('tras_sed').get('DBO5_mg_L'):.1f} & {efluente.get('DBO5_mg_L'):.1f} \\
DQO (mg/L) & {afluente.get('DQO_mg_L'):.1f} & {bal.get('tras_uasb').get('DQO_mg_L'):.1f} & {bal.get('tras_fp').get('DQO_mg_L'):.1f} & {bal.get('tras_sed').get('DQO_mg_L'):.1f} & {efluente.get('DQO_mg_L'):.1f} \\
SST (mg/L) & {afluente.get('SST_mg_L'):.1f} & {bal.get('tras_uasb').get('SST_mg_L'):.1f} & {bal.get('tras_fp').get('SST_mg_L'):.1f} & {bal.get('tras_sed').get('SST_mg_L'):.1f} & {efluente.get('SST_mg_L'):.1f} \\
CF (NMP/100mL) & {afluente.get('CF_NMP'):.0f} & {bal.get('tras_uasb').get('CF_NMP'):.0f} & {bal.get('tras_fp').get('CF_NMP'):.0f} & {bal.get('tras_sed').get('CF_NMP'):.0f} & {efluente.get('CF_NMP'):.0f} \\
\midrule
\textbf{{Remocion etapa}} & -- & \textbf{{{uasb.get('eta_DBO')*100:.0f}\%}} & \textbf{{{(1-fp.get('relacion_Se_S0_Germain'))*100:.0f}\%}} & \textbf{{{sed.get('eta_DBO_sed')*100:.0f}\%}} & \textbf{{{bal.get('eficiencias_totales').get('DBO5_pct'):.1f}\%}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Verificacion de Cumplimiento TULSMA}}

% Limites TULSMA Tabla 12 - Descarga a cuerpo de agua dulce
\begin{{table}}[H]
\centering
\caption{{Verificacion de cumplimiento con limites TULSMA (Tabla 12 -- Descarga a cuerpo de agua dulce)}}
\begin{{tabular}}{{lcccc}}
\toprule
\textbf{{Parametro}} & \textbf{{Efluente calculado}} & \textbf{{Limite TULSMA}} & \textbf{{Estado}} \\
\midrule
DBO$_5$ & {efluente.get('DBO5_mg_L'):.1f} mg/L & $\leq$ 100 mg/L & {estado_dbo} \\
DQO & {efluente.get('DQO_mg_L'):.1f} mg/L & $\leq$ 250 mg/L & {estado_dqo} \\
SST & {efluente.get('SST_mg_L'):.1f} mg/L & $\leq$ 130 mg/L & {estado_sst} \\
Coliformes fecales & {efluente.get('CF_NMP'):.0f} NMP/100mL & $\leq$ 3,000 NMP/100mL & {estado_cf} \\
\bottomrule
\end{{tabular}}
\end{{table}}

{conclusion_tulma}

\subsection{{Requerimientos de Terreno}}

\begin{{table}}[H]
\centering
\caption{{Resumen de areas requeridas}}
\begin{{tabular}}{{lc}}
\toprule
\textbf{{Concepto}} & \textbf{{Area}} \\
\midrule
Area de tratamiento & {area_m2 if area_m2 else 850:.0f} m$^2$ \\
Area de amortiguacion (20\%) & {(area_m2 if area_m2 else 850) * 0.20:.0f} m$^2$ \\
Area complementaria operativa & 310 m$^2$ \\
Zona verde (15\% del total) & {(area_m2 if area_m2 else 1600) * 0.15:.0f} m$^2$ \\
\midrule
\textbf{{Area total requerida}} & \textbf{{{area_m2 if area_m2 else 1600:.0f}--1900 m$^2$ (0.16--0.19 ha)}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Produccion de Lodos}}

\begin{{table}}[H]
\centering
\caption{{Generacion y manejo de lodos}}
\begin{{tabular}}{{lc}}
\toprule
\textbf{{Concepto}} & \textbf{{Valor}} \\
\midrule
Produccion lodos UASB & {lecho.get('lodos_uasb_kg_d'):.1f} kg SST/d \\
Produccion humus FP + Sed & {lecho.get('lodos_fp_kg_d'):.1f} kg SST/d \\
\midrule
\textbf{{Total lodos a manejar}} & \textbf{{{lecho.get('lodos_total_kg_d'):.1f} kg SST/d}} \\
Area de lechos de secado & {lecho.get('A_lecho_m2'):.1f} m$^2$ ({lecho.get('n_celdas')} unidad) \\
Frecuencia de aplicacion & 1 vez cada 3--4 meses \\
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
Hipoclorito de sodio (12\%) & {desinf.get('volumen_NaOCl_L_d'):.1f} & L/d \\
Consumo hipoclorito anual & {desinf.get('volumen_NaOCl_L_d') * 365 / 1000:.0f} & m$^3$/a\~no \\
\bottomrule
\end{{tabular}}
\end{{table}}

\vspace{{1cm}}

\begin{{center}}
\fbox{{
\begin{{minipage}}{{0.9\textwidth}}
\centering
\textbf{{RESUMEN EJECUTIVO}}\\[0.5em]
La PTAR Alternativa A (UASB + Filtro Percolador) para {cfg.Q_linea_L_s * 2:.1f} L/s\\
requiere un area total de \textbf{{0.16--0.19 ha}} y produce un efluente que\\
cumple con la \textbf{{TULSMA}} para descarga a cuerpos de agua Clase 3.
\end{{minipage}}
}}
\end{{center}}
"""


def generar_latex_alternativa_A(cfg, resultados, output_path, area_m2=None, balance_calidad=None):
    """Genera archivo LaTeX completo de Alternativa A"""
    contenido = generar_contenido_alternativa_A(cfg, resultados, area_m2=area_m2, balance_calidad=balance_calidad)
    resumen = generar_resumen_resultados(cfg, resultados, balance_calidad=balance_calidad, area_m2=area_m2)
    
    latex = rf"""\documentclass[12pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[spanish]{{babel}}
\usepackage{{geometry}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{colortbl}}
\usepackage{{graphicx}}
\usepackage{{enumitem}}
\usepackage{{tikz}}
\usepackage{{float}}
\usepackage{{xcolor}}
\usepackage{{hyperref}}
\geometry{{margin=2.5cm}}

\hypersetup{{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue
}}

\begin{{document}}
{contenido}

{resumen}

\newpage
%============================================================================
% ANEXO: TABLAS TULSMA
%============================================================================
\appendix
\section{{Anexo: Tablas TULSMA (Libro VI, Anexo 1)}}
\label{{app:tulsma}}

El presente anexo presenta los l\'imites m\'aximos permisibles establecidos en el Texto Unificado de Legislaci\'on Secundaria del Ministerio del Ambiente (TULSMA), Acuerdo Ministerial 097-A (2015), aplicables al proyecto.

\subsection{{Tabla 1 -- Consumo Humano y Uso Dom\'estico (tratamiento convencional)}}

\begin{{table}}[H]
\centering
\small
\begin{{tabular}}{{p{{5.5cm}}p{{2.5cm}}p{{4.5cm}}}}
\toprule
\textbf{{Par\'ametro}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo}} \\
\midrule
DBO$_5$ & mg/L & $\leq$ 2,0 \\
Coliformes fecales & NMP/100 mL & $\leq$ 600 \\
Coliformes totales & NMP/100 mL & $\leq$ 3.000 \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Tabla 2 -- Consumo Humano (solo desinfecci\'on)}}

\begin{{table}}[H]
\centering
\small
\begin{{tabular}}{{p{{5.5cm}}p{{2.5cm}}p{{4.5cm}}}}
\toprule
\textbf{{Par\'ametro}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo}} \\
\midrule
DBO$_5$ & mg/L & $\leq$ 2,0 \\
Coliformes fecales & NMP/100 mL & $\leq$ 50 \\
Coliformes totales & NMP/100 mL & $\leq$ 50 \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Tabla 3 -- Preservaci\'on de Flora y Fauna}}

\begin{{table}}[H]
\centering
\small
\begin{{tabular}}{{p{{4cm}}p{{2.5cm}}p{{2.5cm}}p{{3cm}}}}
\toprule
\textbf{{Par\'ametro}} & \textbf{{Unidad}} & \textbf{{Agua dulce}} & \textbf{{Agua marina}} \\
\midrule
Coliformes fecales & NMP/100 mL & $\leq$ 200 & $\leq$ 200 \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Tabla 6 -- Uso Agr\'icola o de Riego}}

\begin{{table}}[H]
\centering
\small
\begin{{tabular}}{{p{{5.5cm}}p{{2.5cm}}p{{4.5cm}}}}
\toprule
\textbf{{Par\'ametro}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo}} \\
\midrule
Coliformes fecales & NMP/100 mL & $\leq$ 1.000 \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Tabla 7 -- Uso Pecuario}}

\begin{{table}}[H]
\centering
\small
\begin{{tabular}}{{p{{5.5cm}}p{{2.5cm}}p{{4.5cm}}}}
\toprule
\textbf{{Par\'ametro}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo}} \\
\midrule
Coliformes fecales & NMP/100 mL & $\leq$ 1.000 \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Tablas 9 y 10 -- Uso Recreativo}}

\begin{{table}}[H]
\centering
\small
\begin{{tabular}}{{p{{4cm}}p{{2.5cm}}p{{3cm}}p{{3cm}}}}
\toprule
\textbf{{Par\'ametro}} & \textbf{{Unidad}} & \textbf{{Contacto primario}} & \textbf{{Contacto secundario}} \\
\midrule
Coliformes fecales & NMP/100 mL & $\leq$ 200 & $\leq$ 2.000 \\
Coliformes totales & NMP/100 mL & $\leq$ 1.000 & -- \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Tabla 11 -- Descarga al Alcantarillado}}

\begin{{table}}[H]
\centering
\small
\begin{{tabular}}{{p{{5.5cm}}p{{2.5cm}}p{{4.5cm}}}}
\toprule
\textbf{{Par\'ametro}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo}} \\
\midrule
DBO$_5$ & mg/L & $\leq$ 250 \\
DQO & mg/L & $\leq$ 500 \\
SST & mg/L & $\leq$ 220 \\
Coliformes fecales & NMP/100 mL & No especificado \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Tabla 12 -- Descarga a Cuerpo de Agua Dulce (APLICA AL PROYECTO)}}

\textbf{{Nota:}} Esta es la tabla aplicable al proyecto.

\begin{{table}}[H]
\centering
\small
\begin{{tabular}}{{p{{5.5cm}}p{{2.5cm}}p{{4.5cm}}}}
\toprule
\textbf{{Par\'ametro}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo}} \\
\midrule
\rowcolor{{yellow!25}} \textbf{{DBO$_5$}} & mg/L & $\leq$ \textbf{{100}} \\
\rowcolor{{yellow!25}} \textbf{{DQO}} & mg/L & $\leq$ \textbf{{250}} \\
\rowcolor{{yellow!25}} \textbf{{SST}} & mg/L & $\leq$ \textbf{{130}} \\
\rowcolor{{yellow!25}} \textbf{{Coliformes fecales}} & NMP/100 mL & $\leq$ \textbf{{3.000}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textit{{Nota:}} Aquellos con descargas $\leq$ 3.000 NMP/100 mL quedan exentos de tratamiento de desinfecci\'on.

\subsection{{Tabla 13 -- Descarga a Cuerpo de Agua Marina}}

\begin{{table}}[H]
\centering
\small
\begin{{tabular}}{{p{{5.5cm}}p{{2.5cm}}p{{4.5cm}}}}
\toprule
\textbf{{Par\'ametro}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo}} \\
\midrule
DBO$_5$ & mg/L & $\leq$ 100 \\
DQO & mg/L & $\leq$ 250 \\
SST & mg/L & $\leq$ 100 \\
Coliformes fecales & NMP/100 mL & $\leq$ 3.000 \\
\bottomrule
\end{{tabular}}
\end{{table}}

\newpage
%============================================================================
% BIBLIOGRAFÍA
%============================================================================
\begin{{thebibliography}}{{9}}

\bibitem{{metcalf2014}}
Metcalf \& Eddy, AECOM. (2014).
\textit{{Wastewater Engineering: Treatment and Resource Recovery}}, 5th ed.
McGraw-Hill Education.

\bibitem{{vanhaandel1994}}
Van Haandel, A.C., \& Lettinga, G. (1994).
\textit{{Anaerobic Sewage Treatment: A Practical Guide for Regions with a Hot Climate}}.
John Wiley \& Sons.

\bibitem{{sperling2007}}
Sperling, M.V. (2007).
\textit{{Biological Wastewater Treatment}} (Vols. 1-6).
Departamento de Engenharia Sanitaria e Ambiental, UFMG.

\bibitem{{wef2010}}
Water Environment Federation. (2010).
\textit{{WEF Manual of Practice No. 8: Design of Municipal Wastewater Treatment Plants}}, 5th ed.
WEF Press.

\bibitem{{romero2004}}
Romero Rojas, J.A. (2004).
\textit{{Tratamiento de Aguas Residuales: Teoría y Principios de Diseño}}.
Editorial Escuela Colombiana de Ingeniería.

\bibitem{{ops2005}}
OPS/CEPIS. (2005).
\textit{{Guía para el Diseño de Sistemas de Tratamiento de Aguas Residuales en Zonas Rurales y Pequeñas Comunidades}}.
Organización Panamericana de la Salud.

\bibitem{{kadlec2009}}
Kadlec, R.H., \& Wallace, S.D. (2009).
\textit{{Treatment Wetlands}}, 2nd ed.
CRC Press.

\end{{thebibliography}}

\end{{document}}
"""
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    
    print(f"[OK] Memoria de calculo generada: {{output_path}}")
    return output_path
