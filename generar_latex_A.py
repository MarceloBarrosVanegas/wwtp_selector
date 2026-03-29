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


def _generar_bibliografia(output_dir):
    """Genera el archivo .bib con las referencias bibliográficas"""
    bib_content = r'''%% Archivo de referencias bibliográficas
%% Generado automáticamente - Alternativa A

@book{metcalf2014,
    author    = {Metcalf and Eddy, Inc.},
    title     = {Wastewater Engineering: Treatment and Resource Recovery},
    edition   = {5th},
    publisher = {McGraw-Hill Education},
    year      = {2014},
    address   = {New York, NY},
    isbn      = {978-0073401188}
}

@techreport{ops2005,
    author      = {{OPS/CEPIS}},
    title       = {Guía para el diseño de plantas de tratamiento de aguas residuales},
    institution = {Organización Panamericana de la Salud / Centro Panamericano de Ingeniería Sanitaria y Ciencias del Ambiente},
    year        = {2005},
    address     = {Lima, Perú},
    type        = {Guía Técnica}
}

@techreport{senagua2012,
    author      = {{SENAGUA}},
    title       = {Normativa para el diseño de sistemas de tratamiento de aguas residuales},
    institution = {Secretaría Nacional del Agua del Ecuador},
    year        = {2012},
    address     = {Quito, Ecuador},
    type        = {Norma Técnica}
}

@book{vanhaandel1994,
    author    = {Van Haandel, A. C. and Lettinga, G.},
    title     = {Anaerobic Sewage Treatment: A Practical Guide for Regions with a Hot Climate},
    publisher = {John Wiley \& Sons},
    year      = {1994},
    address   = {Chichester, UK},
    isbn      = {978-0471951055}
}

@book{sperling2007,
    author    = {von Sperling, M.},
    title     = {Activated Sludge and Aerobic Biofilm Reactors},
    series    = {Biological Wastewater Treatment Series},
    volume    = {5},
    publisher = {IWA Publishing},
    year      = {2007},
    address   = {London, UK},
    isbn      = {978-1843391651}
}

@book{chernicharo2007,
    author    = {Chernicharo, C. A. L.},
    title     = {Biological Wastewater Treatment in Warm Climate Regions},
    volume    = {2},
    publisher = {IWA Publishing},
    year      = {2007},
    address   = {London, UK},
    isbn      = {978-1843391613}
}
'''
    bib_path = os.path.join(output_dir, 'referencias.bib')
    with open(bib_path, 'w', encoding='utf-8') as f:
        f.write(bib_content)
    return bib_path


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
    # Usar parámetros configurables desde ConfigDiseno
    if balance_calidad is None:
        # Calcular remociones usando parámetros de configuración
        dbo_tras_uasb = cfg.DBO5_mg_L * (1 - cfg.balance_remov_uasb_dbo)
        dqo_tras_uasb = cfg.DQO_mg_L * (1 - cfg.balance_remov_uasb_dqo)
        sst_tras_uasb = cfg.SST_mg_L * (1 - cfg.balance_remov_uasb_sst)
        cf_tras_uasb = cfg.CF_NMP * (1 - cfg.balance_remov_uasb_cf)
        
        dbo_tras_fp = dbo_tras_uasb * (1 - cfg.balance_remov_fp_dbo)
        dqo_tras_fp = dqo_tras_uasb * (1 - cfg.balance_remov_fp_dqo_factor * cfg.balance_remov_fp_dbo)
        sst_tras_fp = sst_tras_uasb * (1 - cfg.balance_remov_fp_sst)
        cf_tras_fp = cf_tras_uasb * (1 - cfg.balance_remov_fp_cf)
        
        dbo_tras_sed = dbo_tras_fp * (1 - cfg.balance_remov_sed_dbo)
        dqo_tras_sed = dqo_tras_fp  # Asumimos misma remoción relativa
        sst_tras_sed = sst_tras_fp * (1 - cfg.balance_remov_sed_sst)
        cf_tras_sed = cf_tras_fp * (1 - cfg.balance_remov_sed_cf)
        
        # CF final desde resultado de desinfección si está disponible
        cf_final = cfg.balance_cf_objetivo_nmp
        if 'desinfeccion' in resultados:
            cf_final = resultados['desinfeccion'].get('CF_final_NMP', cf_final)
        elif 'cloro' in resultados:
            cf_final = resultados['cloro'].get('CF_final_NMP', cf_final)
        
        balance_calidad = {
            'afluente': {'DBO5_mg_L': cfg.DBO5_mg_L, 'DQO_mg_L': cfg.DQO_mg_L, 'SST_mg_L': cfg.SST_mg_L, 'CF_NMP': cfg.CF_NMP},
            'tras_uasb': {'DBO5_mg_L': dbo_tras_uasb, 'DQO_mg_L': dqo_tras_uasb, 'SST_mg_L': sst_tras_uasb, 'CF_NMP': cf_tras_uasb},
            'tras_fp': {'DBO5_mg_L': dbo_tras_fp, 'DQO_mg_L': dqo_tras_fp, 'SST_mg_L': sst_tras_fp, 'CF_NMP': cf_tras_fp},
            'tras_sed': {'DBO5_mg_L': dbo_tras_sed, 'DQO_mg_L': dqo_tras_sed, 'SST_mg_L': sst_tras_sed, 'CF_NMP': cf_tras_sed},
            'efluente_final': {'DBO5_mg_L': dbo_tras_sed, 'DQO_mg_L': dqo_tras_sed, 'SST_mg_L': sst_tras_sed, 'CF_NMP': cf_final}
        }
    
    # Calcular areas complementarias basadas en el area real de tratamiento
    # Usar parámetros configurables desde ConfigDiseno
    area_tratamiento = area_m2 if area_m2 else 990
    area_amortiguacion = area_tratamiento * cfg.layout_factor_amortiguacion
    area_complementaria = area_tratamiento * cfg.layout_factor_complementaria
    area_total_calc = (area_tratamiento + area_amortiguacion + area_complementaria) / (1 - cfg.layout_factor_zona_verde)
    
    r = resultados.get('rejillas', dimensionar_rejillas(cfg))
    d = resultados.get('desarenador', dimensionar_desarenador(cfg))
    u = resultados.get('uasb', dimensionar_uasb(cfg))
    
    # Usar texto de recomendación de temperatura del evaluador centralizado
    # Viene de ptar_dimensionamiento.evaluar_temperatura_uasb()
    temp_recomendacion = u.get('texto_recomendacion_temp', 
        "Para mantener el rendimiento óptimo del reactor en caso de descenso de temperatura, "
        "se recomienda monitorear periodicamente.")
    
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
%  UASB + FILTRO PERCOLADOR + CLORO
% Memoria de Cálculo
%============================================================================
\newpage
\section{{Tratamiento Anaerobio-Aerobio con UASB y Filtro Percolador}}

La presente alternativa propone un esquema de tratamiento que combina procesos anaerobios y aerobios para lograr la remoción de contaminantes de manera eficiente y con bajo consumo energético. El tren de tratamiento completo comprende: rejillas y desarenador para el pretratamiento, reactor UASB para el tratamiento primario anaerobio, filtro percolador para el tratamiento secundario aerobio, sedimentador secundario para la separación de sólidos biológicos, y finalmente desinfección con hipoclorito de sodio antes del vertimiento.

\subsection{{Canal de Desbaste con Rejillas}}

Las rejillas constituyen la primera barrera de protección del sistema, reteniendo sólidos gruesos como plásticos, ramas y papel que podrían dañar equipos o causar obstrucciones en tuberías aguas abajo. El diseño hidráulico de esta unidad debe garantizar velocidades suficientes para arrastrar sólidos sedimentables, pero no tan elevadas que dificulten el paso del agua a través de las barras.

Según los criterios establecidos por Metcalf y Eddy \cite{{metcalf2014}}, las velocidades de diseño en canales con rejillas deben mantenerse entre {cfg.rejillas_v_canal_min_m_s:.2f} y {cfg.rejillas_v_canal_max_m_s:.2f}~m/s. Para este proyecto se adopta un valor intermedio de {v_canal:.2f}~m/s, lo cual resulta apropiado considerando el caudal de diseño. El tirante hidráulico se establece en {h_tirante:.2f}~m, valor que permite una velocidad de flujo uniforme en la sección del canal y evita la sedimentación de sólidos orgánicos antes de la rejilla, según los criterios de Metcalf y Eddy \cite{{metcalf2014}}.

La pérdida de carga en rejillas limpias se calcula mediante la fórmula de Kirschmer (1926), que relaciona la geometría de las barras con las características del flujo. Los parámetros que determinan esta pérdida son: el espaciado entre barras ($b$), el espesor de las barras ($w$), la velocidad del flujo ($v$) y el ángulo de inclinación ($\theta$):

\begin{{equation}}
h_L = \beta \cdot \left(\frac{{w}}{{b}}\right)^{{4/3}} \cdot \frac{{v^2}}{{2g}} \cdot \sin\theta
\end{{equation}}
\captionequation{{Perdida de carga en rejillas limpias - Formula de Kirschmer}}

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
\captionequation{{Criterios de verificacion de velocidad en rejillas}}

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

El desarenador remueve partículas minerales (arena, grava) con diámetro superior a 0,20~mm mediante sedimentación gravitacional. Según Metcalf y Eddy \cite{{metcalf2014}}, los parámetros de diseño son: velocidad horizontal {cfg.desarenador_v_h_min_m_s:.2f}--{cfg.desarenador_v_h_max_m_s:.2f}~m/s (máximo {cfg.desarenador_v_h_max_m_s:.2f}~m/s para evitar arrastre de sedimentos), tiempo de retención {cfg.desarenador_t_retencion_min_s:.0f}--{cfg.desarenador_t_retencion_max_s:.0f}~s, y profundidad de flujo {cfg.desarenador_H_min_m:.2f}--{cfg.desarenador_H_max_m:.1f}~m (OPS/CEPIS \cite{{ops2005}} permite valores menores en plantas pequeñas).

La profundidad total del canal incluye: profundidad útil de flujo ({d['H_util_m']:.2f}~m), zona de almacenamiento de arena (0,25 - 0,30~m), y bordo libre (0,30~m).

El diseño del desarenador se fundamenta en la teoría de sedimentación discreta. Primero se calcula la velocidad de sedimentación de las partículas objetivo mediante la Ley de Stokes:

\begin{{equation}}
v_s = \frac{{g \cdot (S_s - 1) \cdot d^2}}{{18 \cdot \nu}}
\end{{equation}}
\captionequation{{Ley de Stokes - Velocidad de sedimentacion de particulas}}

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
\captionequation{{Velocidad critica de resuspension - Camp-Shields}}

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
\captionequation{{Velocidad critica calculada}}

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
\captionequation{{Criterios de verificacion de resuspension}}

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
Óptima & $>=$ {cfg.uasb_temp_optimina_C:.0f} & {cfg.uasb_Cv_optimo_min:.1f}--{cfg.uasb_Cv_optimo_max:.1f} & {cfg.uasb_HRT_optimo_min_h:.0f}--{cfg.uasb_HRT_optimo_max_h:.0f} \\
Moderada & {cfg.uasb_temp_min_operativa_C:.0f}--{cfg.uasb_temp_optimina_C:.0f} & {cfg.uasb_Cv_moderado_min:.1f}--{cfg.uasb_Cv_moderado_max:.1f} & {cfg.uasb_HRT_moderado_min_h:.0f}--{cfg.uasb_HRT_moderado_max_h:.0f} \\
Baja & 15--{cfg.uasb_temp_min_operativa_C:.0f} & {cfg.uasb_Cv_bajo_min:.1f}--{cfg.uasb_Cv_bajo_max:.1f} & {cfg.uasb_HRT_bajo_min_h:.0f}--{cfg.uasb_HRT_bajo_max_h:.0f} \\
Muy baja & 10--15 & {cfg.uasb_Cv_muybajo_min:.1f}--{cfg.uasb_Cv_muybajo_max:.1f} & {cfg.uasb_HRT_muybajo_min_h:.0f}--{cfg.uasb_HRT_muybajo_max_h:.0f} \\
Crítica & $<$ 10 & No recomendable & Requiere calefacción \\
\bottomrule
\end{{tabular}}
\end{{table}}

{temp_recomendacion}

Notas importantes de diseño: se debe incluir un separador gas-líquido-sólido (GLS) en la parte superior (altura referencial de {cfg.uasb_H_GLS_m:.1f} m) y un sistema de distribución uniforme en el fondo. El biogás requiere sistema de recolección y manejo seguro (prevención contra explosión).

Los siguientes parámetros han sido seleccionados como criterios de diseño para el reactor UASB:

\begin{{table}}[H]
\centering
\caption{{Parámetros seleccionados para el diseño UASB}}
\begin{{tabular}}{{p{{6cm}}cc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Valor adoptado}} & \textbf{{Rango recomendado}} \\
\midrule
Caudal por línea ($Q$) & {u['Q_m3_h']:.2f} m³/h & - \\
Carga orgánica volumétrica ($C_v$) & {u['Cv_kgDQO_m3_d']:.2f} kg DQO/m³·d & {u['rango_Cv']} \\
Velocidad ascendente de diseño ($v_{{up}}$) & {cfg.uasb_v_up_m_h:.2f} m/h & {u['rango_vup']} \\
Altura máxima del reactor ($H_{{max}}$) & {cfg.uasb_H_max_m:.1f} m & {cfg.uasb_H_min_m:.1f}--{cfg.uasb_H_max_m:.1f} m \\
Factor de efectividad sedimentador & {int(cfg.uasb_factor_efectividad_sed*100):d}\% & {int(cfg.uasb_factor_efectividad_sed*100 - 5):d}--{int(cfg.uasb_factor_efectividad_sed*100 + 5):d}\% \\
Altura sedimentador ($H_{{sed}}$) & {cfg.uasb_H_sed_m:.1f} m & {cfg.uasb_H_sed_min_m:.1f}--{cfg.uasb_H_sed_max_m:.1f} m \\
Carga superficial máxima límite (SOR) & {cfg.uasb_SOR_max_limite_m_h:.1f} m/h & $<$ {cfg.uasb_SOR_max_limite_m_h:.1f} m/h \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textit{{Nota: El valor de velocidad ascendente indicado en el cuadro corresponde al parámetro de diseño configurado. Sin embargo, tras el proceso de verificación hidráulica según las condiciones de temperatura del agua residual ({u['T_agua_C']:.1f}°C) y los criterios de estabilidad del manto de lodos, el valor efectivo adoptado para el cálculo del área superficial es {u['v_up_m_h']:.2f} m/h, resultando en un área de {u['A_sup_m2']:.2f} m².}}

\subsubsection{{Zona de Reacción -- Dimensionamiento}}

El dimensionamiento del reactor UASB se fundamenta en dos criterios complementarios: el criterio biológico (carga orgánica volumétrica) y el criterio hidráulico (velocidad ascendente). Ambos enfoques deben satisfacerse simultáneamente para garantizar el correcto funcionamiento del sistema.

\textbf{{Criterio biológico:}} Según Van Haandel y Lettinga \cite{{vanhaandel1994}}, el volumen del reactor se determina a partir de la carga orgánica volumétrica ($C_v$), que representa la cantidad de materia orgánica que debe procesar el reactor por unidad de volumen y tiempo. Para aguas residuales municipales a temperaturas superiores a {cfg.uasb_temp_optimina_C:.0f}°C, los autores recomiendan una carga entre {cfg.uasb_Cv_optimo_min:.1f} y {cfg.uasb_Cv_optimo_max:.1f} kg DQO/m³·d. La expresión fundamental es:

\begin{{equation}}
V_r = \frac{{Q \cdot S_0}}{{C_v}}
\end{{equation}}
\captionequation{{Volumen util del reactor UASB segun Van Haandel y Lettinga (1994)}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$V_r$] = Volumen útil del reactor (m³)
    \item[$Q$] = Caudal diario ({u['Q_m3_d']:.1f} m³/d)
    \item[$S_0$] = Concentración de DQO afluente ({u['DQO_kg_m3']:.4f} kg/m³)
    \item[$C_v$] = Carga orgánica volumétrica adoptada ({u['Cv_kgDQO_m3_d']:.1f} kg DQO/m³·d)
\end{{itemize}}

Sustituyendo los valores del proyecto:

\begin{{equation}}
V_r = \frac{{{u['Q_m3_d']:.1f} \times {u['DQO_kg_m3']:.4f}}}{{{u['Cv_kgDQO_m3_d']:.1f}}} = {u['V_r_m3']:.1f} \text{{ m}}^3
\end{{equation}}

Este volumen garantiza el tiempo de retención hidráulico necesario para que los microorganismos anaerobios degraden la materia orgánica. Van Haandel y Lettinga establecen que a temperaturas óptimas ($>${cfg.uasb_temp_optimina_C:.0f}°C), el TRH debe estar entre {cfg.uasb_HRT_optimo_min_h:.0f} y {cfg.uasb_HRT_optimo_max_h:.0f} horas para asegurar la estabilidad del manto de lodos.

\textbf{{Criterio hidráulico:}} De manera simultánea, según Sperling \cite{{sperling2007}}, la velocidad ascendente ($v_{{up}}$) debe mantenerse dentro de rangos que permitan retener el manto de lodos sin arrastre. El autor recomienda velocidades entre 0,5 y {cfg.uasb_v_up_max_recomendado_m_h:.1f} m/h para condiciones normales, con un máximo de {cfg.uasb_v_up_max_destructivo_m_h:.1f} m/h durante picos de caudal. Con la velocidad adoptada de {u['v_up_m_h']:.2f} m/h, el área superficial requerida se calcula como:

\begin{{equation}}
A_s = \frac{{Q}}{{v_{{up}}}}
\end{{equation}}
\captionequation{{Area superficial del reactor UASB}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_s$] = Área superficial del reactor (m²)
    \item[$Q$] = Caudal por línea ({cfg.Q_linea_m3_h:.2f} m³/h)
    \item[$v_{{up}}$] = Velocidad ascendente adoptada ({u['v_up_m_h']:.2f} m/h)
\end{{itemize}}

\begin{{equation}}
A_s = \frac{{{cfg.Q_linea_m3_h:.2f}}}{{{u['v_up_m_h']:.2f}}} = {u['A_sup_m2']:.2f} \text{{ m}}^2
\end{{equation}}

El diámetro del reactor circular se obtiene a partir de la geometría del círculo, considerando que el área superficial debe ser la calculada hidráulicamente. Esta formulación geométrica estándar permite determinar las dimensiones constructivas del reactor:

\begin{{equation}}
D = \sqrt{{\frac{{4 \cdot A_s}}{{\pi}}}}
\end{{equation}}
\captionequation{{Diametro del reactor circular - Geometria basica}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$D$] = Diámetro del reactor circular (m)
    \item[$A_s$] = Área superficial calculada ({u['A_sup_m2']:.2f} m²)
    \item[$\pi$] = 3,14159
\end{{itemize}}

\begin{{equation}}
D = \sqrt{{\frac{{4 \times {u['A_sup_m2']:.2f}}}{{\pi}}}} = {u['D_m']:.2f} \text{{ m}}
\end{{equation}}

La altura de la zona de reacción (manto de lodos) resulta {u['H_r_m']:.2f}~m, proporcionando un tiempo de retención hidráulico de {u['TRH_h']:.1f} horas, valor adecuado según Sperling \cite{{sperling2007}} para la temperatura de {u['T_agua_C']:.1f}°C del agua residual.

\textbf{{Producción de biogás:}} La metanogénesis en el reactor UASB genera biogás compuesto principalmente por metano (CH$_4$) y dióxido de carbono (CO$_2$). Según Van Haandel y Lettinga \cite{{vanhaandel1994}}, la producción teórica de metano puede estimarse mediante relaciones estequiométricas. Experimentalmente se ha determinado que por cada kilogramo de DQO removida en condiciones anaerobias, se producen aproximadamente 0,35 m³ de metano (a condiciones estándar). Esta relación permite estimar la producción esperada de biogás:

\begin{{equation}}
V_{{CH_4}} = (Q_d \cdot S_0 \cdot E) \times {u['factor_biogas_ch4']:.2f}
\end{{equation}}
\captionequation{{Produccion de biogas - Relacion estequiometrica}}

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

\subsubsection{{Zona de Reacción -- Verificación}}

El fundamento de la verificación hidráulica establece que el diseño del reactor UASB debe garantizar no solo el funcionamiento adecuado bajo condiciones normales (caudal medio), sino también durante eventos de pico de caudal que ocurren típicamente en horas de mayor consumo de agua. Según Metcalf y Eddy \cite{{metcalf2014}}, los sistemas de tratamiento deben verificarse para el caudal máximo horario, el cual se estima aplicando un factor de pico sobre el caudal medio diario. El factor denominado $f_p$, adoptado de {u['factor_pico']:.1f} considera las características de la zona de estudio y las variaciones esperadas del caudal durante el día. La aplicación de este factor permite determinar el caudal máximo horario de diseño:

\begin{{equation}}
Q_{{max}} = f_p \times Q_{{medio}} = {u['factor_pico']:.1f} \times {u['Q_m3_d']:.1f} = {u['Q_max_m3_d']:.1f} \text{{ m}}^3\text{{/d}} = {u['Q_max_m3_h']:.2f} \text{{ m}}^3\text{{/h}}
\end{{equation}}

El análisis de la velocidad ascendente de pico considera que, bajo condiciones de caudal máximo, la velocidad ascendente en el reactor aumenta proporcionalmente. Esta velocidad de pico, $v_{{up,max}}$, se calcula manteniendo el área superficial del reactor (determinada previamente por el criterio de velocidad media) pero incrementando el caudal al valor máximo esperado:

\begin{{equation}}
v_{{up,max}} = \frac{{Q_{{max}}}}{{A_s}} = \frac{{{u['Q_max_m3_h']:.2f}}}{{{u['A_sup_m2']:.2f}}} = {u['v_up_max_m_h']:.2f} \text{{ m/h}}
\end{{equation}}

Los criterios de evaluación del estado del reactor, según Metcalf y Eddy \cite{{metcalf2014}}, clasifican el estado operacional en función de la velocidad ascendente máxima calculada. Esta clasificación permite determinar si el diseño garantiza la estabilidad del manto de lodos o si existe riesgo de arrastre de biomasa. Los autores definen tres estados operacionales basados en estudios experimentales de la hidrodinámica de reactores UASB. Formalmente, el estado se determina mediante:

\begin{{equation}}
\text{{Estado}} = \begin{{cases}}
    \text{{ÓPTIMO}} & \text{{si }} v_{{up,max}} \leq {cfg.uasb_v_up_max_recomendado_m_h:.1f} \text{{ m/h}} \\
    \text{{ACEPTABLE}} & \text{{si }} {cfg.uasb_v_up_max_recomendado_m_h:.1f} < v_{{up,max}} \leq {cfg.uasb_v_up_max_destructivo_m_h:.1f} \text{{ m/h}} \\
    \text{{NO ADMISIBLE}} & \text{{si }} v_{{up,max}} > {cfg.uasb_v_up_max_destructivo_m_h:.1f} \text{{ m/h}}
\end{{cases}}
\end{{equation}}
\captionequation{{Criterios de verificación de arrastre del manto según Metcalf y Eddy (2014)}}

Para el presente diseño, con una velocidad ascendente máxima calculada de $v_{{up,max}} = {u['v_up_max_m_h']:.2f}$~m/h, el reactor se clasifica en estado \textbf{{{u['estado_verificacion']}}}. Este resultado indica que el dimensionamiento propuesto {('garantiza la estabilidad del manto de lodos bajo todas las condiciones operativas esperadas.' if u['estado_verificacion'] == 'ÓPTIMO' else 'requiere monitoreo durante eventos de pico de caudal.' if u['estado_verificacion'] == 'ACEPTABLE CON MONITOREO' else 'no es admisible y debe redimensionarse.')}

\subsubsection{{Cámara de Sedimentación -- Dimensionamiento}}

El compartimiento de sedimentación superior constituye una zona crítica del reactor UASB, ya que debe retener los sólidos biológicos antes de que salgan con el efluente. Según Chernicharo \cite{{chernicharo2007}}, el diseño de esta zona se fundamenta en el concepto de Carga Superficial (SOR - Surface Overflow Rate), análogo al utilizado en sedimentadores convencionales, pero adaptado a las condiciones particulares del UASB donde el biogás generado puede afectar la sedimentación.

Chernicharo recomienda que la carga superficial a caudal máximo no debe exceder {cfg.uasb_SOR_max_limite_m_h:.1f} m/h para evitar el arrastre de sólidos hacia el efluente. Este valor es más restrictivo que el utilizado en sedimentadores primarios convencionales debido a la presencia de biogás y la naturaleza floculenta de los lodos anaerobios. Adicionalmente, el autor sugiere una altura mínima del compartimiento de sedimentación entre {cfg.uasb_TRH_sed_medio_min_h:.1f} y {cfg.uasb_TRH_sed_medio_max_h:.1f} m para garantizar el tiempo necesario de separación gas-líquido-sólido.

Los criterios de diseño según Chernicharo (2007) son:

\begin{{equation}}
\text{{SOR}}_{{max}} < {cfg.uasb_SOR_max_limite_m_h:.1f} \text{{ m/h}} \quad \text{{(límite para evitar arrastre de sólidos)}}
\end{{equation}}

\begin{{equation}}
H_{{sed}} \geq {cfg.uasb_TRH_sed_medio_min_h:.1f} \text{{ m}} \quad \text{{(altura mínima constructiva)}}
\end{{equation}}

El área efectiva de sedimentación considera el factor de efectividad del {cfg.uasb_factor_efectividad_sed*100:.0f}\% del área total (Chernicharo):

\begin{{equation}}
A_{{sed}} = {cfg.uasb_factor_efectividad_sed:.2f} \times A_{{sup}} = {cfg.uasb_factor_efectividad_sed:.2f} \times {u['A_sup_m2']:.2f} = {u['A_sed_efectiva_m2']:.2f} \text{{ m}}^2
\end{{equation}}

El volumen del sedimentador se calcula con la altura adoptada de {u['H_sed_m']:.1f}~m:

\begin{{equation}}
V_{{sed}} = A_{{sed}} \times H_{{sed}} = {u['A_sed_efectiva_m2']:.2f} \times {u['H_sed_m']:.1f} = {u['V_sed_m3']:.2f} \text{{ m}}^3
\end{{equation}}

El tiempo de retención hidráulico en el sedimentador resulta:

\begin{{equation}}
t_{{sed}} = \frac{{V_{{sed}}}}{{Q}} = \frac{{{u['V_sed_m3']:.2f}}}{{{u['Q_m3_h']:.2f}}} = {u['TRH_sed_medio_h']:.2f} \text{{ h}}
\end{{equation}}

\subsubsection{{Cámara de Sedimentación -- Verificación}}

El principio de verificación de la sedimentación establece que la cámara de sedimentación superior del reactor UASB debe evaluarse tanto para condiciones de caudal medio como para caudal máximo. Según Chernicharo \cite{{chernicharo2007}}, la verificación a caudal medio permite evaluar si el diseño opera dentro del rango óptimo de eficiencia, mientras que la verificación a caudal máximo determina si se evita el arrastre de sólidos durante picos de flujo.

El autor establece que, aunque el criterio crítico es el SOR máximo ($<$ {cfg.uasb_SOR_max_limite_m_h:.1f} m/h), también es deseable que el SOR medio se mantenga entre {cfg.uasb_SOR_medio_min_m_h:.1f} y {cfg.uasb_SOR_medio_max_m_h:.1f} m/h. Valores inferiores a este rango, aunque conservadores, indican que el área del sedimentador es mayor de lo estrictamente necesario, lo cual no representa un problema operativo pero implica mayores costos de construcción. Valores superiores sugieren riesgo de arrastre incluso en operación normal.

El cálculo de la Carga Superficial Operacional se realiza aplicando la ecuación fundamental del SOR para ambas condiciones de caudal:

Para caudal medio (condición de operación normal):
\begin{{equation}}
SOR_{{medio}} = \frac{{Q_{{medio}}}}{{A_{{sed}}}} = \frac{{{u['Q_m3_h']:.2f}}}{{{u['A_sed_efectiva_m2']:.2f}}} = {u['SOR_medio_m_h']:.2f} \text{{ m/h}}
\end{{equation}}

Para caudal máximo horario (condición de pico):
\begin{{equation}}
SOR_{{max}} = \frac{{Q_{{max}}}}{{A_{{sed}}}} = \frac{{{u['Q_max_m3_h']:.2f}}}{{{u['A_sed_efectiva_m2']:.2f}}} = {u['SOR_max_m_h']:.2f} \text{{ m/h}}
\end{{equation}}

El análisis de cumplimiento de criterios evalúa los valores calculados según los parámetros establecidos por Chernicharo (2007) para sedimentadores en reactores UASB:

\begin{{itemize}}[leftmargin=2em]
    \item \textbf{{SOR máximo}}: El valor de {u['SOR_max_m_h']:.2f} m/h se compara contra el límite crítico de {cfg.uasb_SOR_max_limite_m_h:.1f} m/h. Este límite representa la velocidad de asentamiento mínima de los agregados de lodos anaerobios. Superar este valor implica que el flujo ascendente supera la velocidad de caída de los sólidos, causando su arrastre hacia el efluente.
    
    \item \textbf{{SOR medio}}: El valor de {u['SOR_medio_m_h']:.2f} m/h se evalúa respecto al rango óptimo de {cfg.uasb_SOR_medio_min_m_h:.1f}--{cfg.uasb_SOR_medio_max_m_h:.1f} m/h. Según Chernicharo, este rango garantiza una eficiente separación sólido-líquido sin requerir áreas excesivas. Valores inferiores (como en este caso) son aceptables y proporcionan un margen de seguridad adicional.
    
    \item \textbf{{TRH en sedimentador}}: El tiempo de retención de {u['TRH_sed_medio_h']:.2f} h cumple ampliamente con el mínimo de {cfg.uasb_TRH_sed_medio_min_h:.1f} h recomendado por Chernicharo para permitir la adecuada separación gas-líquido-sólido y la sedimentación de partículas finas.
\end{{itemize}}

\begin{{table}}[H]
\centering
\caption{{Verificación de criterios de diseño de la cámara de sedimentación según Chernicharo (2007)}}
\begin{{tabular}}{{lccc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Valor calculado}} & \textbf{{Criterio}} & \textbf{{Estado}} \\
\midrule
SOR máximo & {u['SOR_max_m_h']:.2f} m/h & $<$ {cfg.uasb_SOR_max_limite_m_h:.1f} m/h & {'Cumple' if u.get('SOR_max_cumple', False) else 'No cumple'} \\
SOR medio & {u['SOR_medio_m_h']:.2f} m/h & {cfg.uasb_SOR_medio_min_m_h:.1f}--{cfg.uasb_SOR_medio_max_m_h:.1f} m/h & {'Cumple (conservador)' if u.get('SOR_medio_cumple', False) else 'Bajo (aceptable)'} \\
TRH sedimentador & {u['TRH_sed_medio_h']:.2f} h & $\geq$ {cfg.uasb_TRH_sed_medio_min_h:.1f} h & {'Cumple' if u.get('TRH_sed_cumple', False) else 'No cumple'} \\
\bottomrule
\end{{tabular}}
\end{{table}}

La verificación demuestra que el compartimiento de sedimentación diseñado cumple satisfactoriamente con todos los criterios técnicos establecidos en la literatura especializada para reactores UASB.

\subsubsection{{Aberturas GLS -- Dimensionamiento}}

El separador gas-líquido-sólido (GLS) incluye aberturas que permiten el paso del líquido clarificado desde la zona de digestión hacia el compartimiento de sedimentación. Según Chernicharo \cite{{chernicharo2007}}, estas aberturas deben dimensionarse cuidadosamente para evitar velocidades que arrastren sólidos hacia el efluente.

La velocidad admisible en las aberturas es mayor que en el cuerpo del reactor porque el líquido ya está parcialmente clarificado. Los valores recomendados son {cfg.uasb_v_abertura_medio_min_m_h:.1f}--{cfg.uasb_v_abertura_medio_max_m_h:.1f} m/h a caudal medio y hasta {cfg.uasb_v_abertura_max_m_h:.1f} m/h a caudal máximo. El área mínima requerida se calcula como:

\begin{{equation}}
A_{{ab}} = \frac{{Q}}{{v_{{adm}}}}
\end{{equation}}
\captionequation{{Area minima de aberturas GLS}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_{{ab}}$] = Área total libre de aberturas (m²)
    \item[$Q$] = Caudal por línea ({u['Q_m3_h']:.2f} m³/h)
    \item[$v_{{adm}}$] = Velocidad admisible adoptada ({u['v_abertura_adoptada_m_h']:.2f} m/h)
\end{{itemize}}

\begin{{equation}}
A_{{ab}} = \frac{{{u['Q_m3_h']:.2f}}}{{{u['v_abertura_adoptada_m_h']:.2f}}} = {u['A_aberturas_min_m2']:.2f} \text{{ m}}^2
\end{{equation}}

Verificando para caudal máximo ($Q_{{max}} = {u['Q_max_m3_h']:.2f}$ m³/h):

\begin{{equation}}
v_{{ab,max}} = \frac{{Q_{{max}}}}{{A_{{ab}}}} = \frac{{{u['Q_max_m3_h']:.2f}}}{{{u['A_aberturas_min_m2']:.2f}}} = {u['v_abertura_max_calculada_m_h']:.2f} \text{{ m/h}} \quad {'< ' + str(cfg.uasb_v_abertura_max_m_h) if u['v_abertura_max_cumple'] else '> ' + str(cfg.uasb_v_abertura_max_m_h)} \text{{ m/h }} \text{{({'Cumple' if u['v_abertura_max_cumple'] else 'No cumple'})}}
\end{{equation}}

Adicionalmente, el GLS debe construirse con pendientes de {cfg.uasb_GLS_pendiente_min_grados:.0f}° a {cfg.uasb_GLS_pendiente_max_grados:.0f}° (adoptado {u['GLS_pendiente_adoptada_grados']:.0f}°) y un traslape de {cfg.uasb_GLS_traslape_m:.2f} m sobre las aberturas para garantizar la retención de sólidos.

\subsubsection{{Distribución del Afluente -- Dimensionamiento}}

La distribución uniforme del afluente en el fondo del reactor es crítica para garantizar un flujo ascendente homogéneo y evitar cortocircuitos que reducirían la eficiencia del tratamiento. Según Chernicharo \cite{{chernicharo2007}}, el número de puntos de distribución se determina en función del área del reactor y el área de influencia que puede atender cada punto.

El área de influencia por punto recomendada varía entre {cfg.uasb_A_inf_min_m2:.1f} y {cfg.uasb_A_inf_max_m2:.1f} m² por punto. Adoptando un valor intermedio de {u['A_inf_adoptada_m2']:.2f} m²/punto, el número de puntos de distribución resulta:

\begin{{equation}}
N = \frac{{A}}{{A_{{inf}}}} = \frac{{{u['A_sup_m2']:.2f}}}{{{u['A_inf_adoptada_m2']:.2f}}} = {u['num_puntos_distribucion']:.0f} \text{{ puntos}}
\end{{equation}}
\captionequation{{Numero de puntos de distribucion del afluente}}

El caudal por punto de distribución se calcula dividiendo el caudal total entre el número de puntos:

\begin{{equation}}
q = \frac{{Q}}{{N}} = \frac{{{u['Q_m3_s']:.3f} \times 1000}}{{{u['num_puntos_distribucion']:.0f}}} = {u['caudal_por_punto_L_s']:.3f} \text{{ L/s}}
\end{{equation}}


Los tubos de distribución se diseñan según la práctica estándar de Lettinga y Hulshoff Pol: tubería principal de gran diámetro para transporte sin obstrucciones, con bocas de salida reducidas para garantizar velocidad de inyección adecuada. Se adopta una tubería de distribución de {u['diam_tubo_distribucion_mm']:.0f} mm con bocas de salida de {u['diam_boca_salida_mm']:.0f} mm.

\textbf{{Verificación de velocidades:}}

La velocidad en la tubería principal(transporte) se calcula como:

\begin{{equation}}
v_{{tubo}} = \frac{{q}}{{a_{{tubo}}}} = \frac{{{u['caudal_por_punto_L_s']:.3f} \times 10^{{-3}}}}{{\pi \times ({u['diam_tubo_distribucion_mm']:.0f} \times 10^{{-3}})^2 / 4}} = {u['velocidad_tubo_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

La velocidad en la boca de salida (inyección al lecho de lodo) es el parámetro crítico según Lettinga. Debe estar entre {u['v_boca_min_m_s']:.1f} y {u['v_boca_max_m_s']:.1f} m/s para garantizar arrastre de sólidos sin erosión:

\begin{{equation}}
v_{{boca}} = \frac{{q}}{{a_{{boca}}}} = \frac{{{u['caudal_por_punto_L_s']:.3f} \times 10^{{-3}}}}{{\pi \times ({u['diam_boca_salida_mm']:.0f} \times 10^{{-3}})^2 / 4}} = {u['velocidad_boca_m_s']:.2f} \text{{ m/s}}
\end{{equation}}

\begin{{table}}[H]
\centering
\caption{{Verificación de velocidades en sistema de distribución}}
\begin{{tabular}}{{lccc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} & \textbf{{Criterio}} & \textbf{{Estado}} \\
\midrule
Velocidad en tubería principal& {u['velocidad_tubo_m_s']:.3f} m/s & Transporte sin obstrucción ($<$ {u['v_tubo_max_m_s']:.2f} m/s) & {'Adecuado' if u['velocidad_tubo_m_s'] <= u['v_tubo_max_m_s'] else 'Revisar'} \\
Velocidad en boca de salida & {u['velocidad_boca_m_s']:.2f} m/s & {u['v_boca_min_m_s']:.1f}--{u['v_boca_max_m_s']:.1f} m/s & {'Cumple' if u['v_boca_cumple'] else 'No cumple'} \\
\bottomrule
\end{{tabular}}
\end{{table}}

La velocidad en boca de {u['velocidad_boca_m_s']:.2f} m/s {'cumple con el rango recomendado por Lettinga y Hulshoff Pol para inyección adecuada en el lecho de lodo.' if u['v_boca_cumple'] else 'está fuera del rango recomendado. Se recomienda revisar el diámetro de las bocas de salida.'}

\subsubsection{{Resultados del Reactor UASB}}

\begin{{table}}[H]
\centering
\caption{{Dimensiones y parámetros del reactor UASB}}
\begin{{tabular}}{{ll}}
\toprule
Parámetro & Valor \\
\midrule
Diámetro & {u['D_m']:.2f} m \\
\multicolumn{{2}}{{l}}{{\textit{{Desglose de alturas:}}}} \\
\quad Zona de distribución (fondo) & {u['H_distribucion_m']:.2f} m \\
\quad Zona de reacción (manto de lodos) & {u['H_zona_reaccion_m']:.2f} m \\
\quad Zona de sedimentación & {u['H_sed_m']:.2f} m \\
\quad Separador GLS & {u['H_GLS_m']:.2f} m \\
\quad Bordo libre & {u['H_bordo_libre_m']:.2f} m \\
\midrule
\textbf{{Altura total de construcción}} & \textbf{{{u['H_total_construccion_m']:.2f} m}} \\
\midrule
Volumen útil & {u['V_r_m3']:.1f} m³ \\
Área superficial & {u['A_sup_m2']:.2f} m² \\
Tiempo de retención hidráulico & {u['TRH_h']:.1f} h \\
Carga orgánica volumétrica & {u['Cv_kgDQO_m3_d']:.1f} kg DQO/m³·d \\
Biogás producido & {u['biogaz_m3_d']:.1f} m$^3$ CH$_4$/d \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Subdivisión zona de reacción:}}}} \\
\quad Lecho granular ({cfg.uasb_porcion_lecho_granular*100:.0f}\%) & {u.get('H_lecho_granular_m', u['H_r_m']*cfg.uasb_porcion_lecho_granular):.2f} m \\
\quad Manto expandido ({cfg.uasb_porcion_manto_expandido*100:.0f}\%) & {u.get('H_manto_expandido_m', u['H_r_m']*cfg.uasb_porcion_manto_expandido):.2f} m \\
\bottomrule
\end{{tabular}}
\end{{table}}

La subdivisión interna de la zona de reacción sigue criterios establecidos por Chernicharo \cite{{chernicharo2007}}. El lecho de lodo denso o granular (aproximadamente {cfg.uasb_porcion_lecho_granular*100:.0f}\% de la altura útil) contiene los lodos más viejos y densos, mientras que el manto de lodos expandido (aproximadamente {cfg.uasb_porcion_manto_expandido*100:.0f}\% de la altura útil) mantiene los lodos en suspensión activa donde ocurre la mayor parte de la degradación biológica.

El reactor UASB requiere un inóculo inicial de lodo anaeróbico granular o, en su defecto, lodo digerido anaeróbicamente. Según Lettinga y Hulshoff-Pol \cite{{vanhaandel1994}}, la cantidad recomendada de inóculo para el arranque es de 10--15 kg SSV/m³ (sólidos suspendidos volátiles), equivalente a llenar aproximadamente el 15--30% del volumen del reactor. El lodo granular consiste en agregados microbianos densos de 0,5--5 mm de diámetro, con velocidades de sedimentación superiores a 50 m/h. Si no se dispone de lodo granular, pueden utilizarse alternativas como lodo de digestor anaerobio, estiércol de cerdo/vaca o lodo de fosas sépticas, desarrollándose la granulación natural en un período de 2--6 meses mediante aumento gradual de la carga orgánica. 

La siguiente figura presenta un esquema del reactor UASB con sus componentes principales y los flujos de agua y biogás:

\begin{{figure}}[H]
\centering
\includegraphics[width=\textwidth]{{Esquema_UASB.png}}
\caption{{Esquema del reactor UASB: distribución del afluente, zonas de reacción, separación gas-líquido-sólido y recolección de biogás. Caudal por línea: {u['Q_m3_h']:.2f} m³/h, Biogás: {u['biogaz_m3_d']:.1f} m³ CH$_4$/d, {u['num_puntos_distribucion']:.0f} puntos de distribución.}}
\label{{fig:esquema_uasb}}
\end{{figure}}

El esquema ilustra el flujo ascendente del afluente a través del lecho de lodo granular, donde ocurre la digestión anaerobia. El biogás producido se separa en el GLS y se recolecta en la cámara superior, mientras que el efluente tratado sale por el lateral del reactor. La velocidad ascendente de diseño de {u['v_up_m_h']:.2f} m/h garantiza la retención del manto de lodos.

\subsection{{Filtro Percolador}}

El filtro percolador constituye la unidad de tratamiento secundario aerobio, diseñada para remover la carga orgánica restante después del tratamiento anaerobio en el UASB. El diseño se fundamenta en el modelo cinético de Germain (1966), que describe la remoción de DBO mediante la expresión exponencial, y en criterios de carga orgánica volumétrica según WEF (2010) y Metcalf \& Eddy (2014).

Según las recomendaciones para medio plástico aleatorio, las cargas óptimas oscilan entre 0,3 y 3,0 kg DBO/m³·d. Se adopta un valor conservador de {fp['Cv_kgDBO_m3_d']:.2f} kg DBO/m³·d, apropiado para la condición de pretratamiento previo con UASB.

El volumen de medio filtrante requerido se calcula mediante:

\begin{{equation}}
V = \frac{{Q \cdot S_0}}{{C_v}}
\end{{equation}}
\captionequation{{Volumen de medio filtrante - Filtro Percolador}}

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
\captionequation{{Correccion de constante cinética por temperatura}}

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
\captionequation{{Modelo de Germain - Relacion de eficiencia}}

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

Se verifica el comportamiento hidráulico para el caudal máximo horario, aplicando un factor de pico típico de {fp['factor_pico']:.1f} sobre el caudal medio:

\begin{{equation}}
Q_{{max}} = {fp['factor_pico']:.1f} \times Q_{{medio}} = {fp['factor_pico']:.1f} \times {fp['Q_m3_d']:.1f} = {fp['Q_max_m3_d']:.1f} \text{{ m}}^3\text{{/d}}
\end{{equation}}

A caudal máximo, la tasa hidráulica resulta:

\begin{{equation}}
q_{{A,max}} = \frac{{Q_{{max}} \cdot (1 + R)}}{{A_s \cdot 24}} = \frac{{{fp['Q_max_m3_d']:.1f} \times {1+fp['R_recirculacion']:.1f}}}{{{fp['A_sup_m2']:.2f} \times 24}} = {fp['Q_A_max_m3_m2_h']:.2f} \text{{ m}}^3\text{{/m}}^2\text{{·h}}
\end{{equation}}

El valor obtenido se compara con el límite máximo recomendado de {fp['Q_A_limite_m3_m2_h']:.1f} m³/m²·h. {fp['verif_qmax_texto']}.

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
\text{{Dosis total}} = \text{{Demanda}} + \text{{Residual}} = {cl['demanda_cloro_mg_L']:.1f} + {cl['cloro_residual_mg_L']:.1f} = {cl['dosis_cloro_mg_L']:.1f} \text{{ mg/L}}
\end{{equation}}
\captionequation{{Dosis total de cloro}}

\begin{{table}}[H]
\centering
\caption{{Parámetros de diseño de la desinfección}}
\small
\begin{{tabular}}{{lccl}}
\toprule
Parámetro & Rango recomendado & Valor adoptado & Fuente \\
\midrule
Demanda de cloro & 2--5 & {cl['demanda_cloro_mg_L']:.1f} mg/L & Estimado efluente UASB+FP \\
Cloro residual & 0.5--2.0 & {cl['cloro_residual_mg_L']:.1f} mg/L & OPS/CEPIS \cite{{ops2005}} \\
Dosis total & 3--10 & {cl['dosis_cloro_mg_L']:.1f} mg/L & Metcalf \& Eddy \cite{{metcalf2014}} \\
Tiempo de contacto & 15--45 & {cl['TRH_min']:.0f} min & Metcalf \& Eddy \\
CT & $\geq$ 15 & {cl['CT_mg_min_L']:.0f} mg.min/L & Diseño conservador \\
\bottomrule
\end{{tabular}}
\end{{table}}


La eficacia de la desinfección se cuantifica mediante el parámetro CT:

\begin{{equation}}
CT = C \times t
\end{{equation}}
\captionequation{{Producto concentracion-tiempo CT}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$CT$] = Producto concentración-tiempo (mg.min/L)
    \item[$C$] = Cloro residual ({cl['cloro_residual_mg_L']:.1f} mg/L)
    \item[$t$] = Tiempo de contacto ({cl['TRH_min']:.0f} min)
\end{{itemize}}

\begin{{equation}}
CT = {cl['cloro_residual_mg_L']:.1f} \times {cl['TRH_min']:.0f} = {cl['CT_mg_min_L']:.0f} \text{{ mg.min/L}}
\end{{equation}}

La reducción de coliformes se estima mediante:

\begin{{equation}}
\text{{Log reducción}} \approx 0.22 \times CT
\end{{equation}}
\captionequation{{Log reduccion de coliformes}}

\begin{{equation}}
\text{{Log reducción}} \approx 0.22 \times {cl['CT_mg_min_L']:.0f} = {cl['log_reduccion']:.1f} \text{{ log}}
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
\captionequation{{Volumen del tanque de contacto}}

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
\text{{Consumo Cl}}_2 = \frac{{D \times Q}}{{1000}} = \frac{{{cl['dosis_cloro_mg_L']:.1f} \times {cl['Q_m3_d']:.1f}}}{{1000}} = {cl['consumo_cloro_kg_d']:.2f} \text{{ kg Cl}}_2\text{{/d}}
\end{{equation}}

\textbf{{Conversión a hipoclorito de sodio comercial (NaOCl):}}

El hipoclorito de sodio se comercializa típicamente al 10--12.5\% de cloro disponible. La conversión se realiza mediante:

\begin{{equation}}
\text{{Consumo NaOCl}} = \frac{{\text{{Consumo Cl}}_2}}{{[\% \text{{ NaOCl}}]}} = \frac{{{cl['consumo_cloro_kg_d']:.2f}}}{{{cl['concentracion_NaOCl_pct']:.0f}\%}} = {cl['consumo_NaOCl_kg_d']:.1f} \text{{ kg NaOCl/d}}
\end{{equation}}
\captionequation{{Conversion a hipoclorito de sodio comercial}}

Considerando una densidad de {cfg.desinfeccion_densidad_NaOCl:.2f} kg/L para la solución al {cl['concentracion_NaOCl_pct']:.0f}\%:

\begin{{equation}}
\text{{Volumen NaOCl}} = \frac{{{cl['consumo_NaOCl_kg_d']:.1f} \text{{ kg/d}}}}{{{cfg.desinfeccion_densidad_NaOCl:.2f} \text{{ kg/L}}}} = {cl['volumen_NaOCl_L_d']:.1f} \text{{ L/d}} \approx {cl['volumen_almacenamiento_L']:.0f} \text{{ L/mes}}
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
Concentración NaOCl & {cl['concentracion_NaOCl_pct']:.0f} \% \\
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

La producción de lodos se estima considerando:
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item \textbf{{Lodos UASB:}} producción de 0,10 kg SST/kg DBO removida (factor configurado)
    \item \textbf{{Humus FP + Sedimentador:}} producción asociada a la DBO removida en el tratamiento secundario
\end{{itemize}}

\textbf{{Balance de producción de lodos:}}

\begin{{table}}[H]
\centering
\caption{{Producción de lodos por línea y total planta}}
\begin{{tabular}}{{lcc}}
\toprule
\textbf{{Origen}} & \textbf{{Por línea (kg SST/d)}} & \textbf{{Total planta ({l.get('num_lineas', 2)} líneas) (kg SST/d)}} \\
\midrule
Lodos UASB (anaerobios) & {l.get('lodos_uasb_kg_d_por_linea', l['lodos_kg_SST_d']/2):.2f} & {l.get('lodos_uasb_kg_d', l['lodos_kg_SST_d']/2*l.get('num_lineas', 2)):.2f} \\
Humus FP + Sedimentador & {l.get('lodos_fp_kg_d_por_linea', l['lodos_kg_SST_d']/2):.2f} & {l.get('lodos_fp_kg_d', l['lodos_kg_SST_d']/2*l.get('num_lineas', 2)):.2f} \\
\midrule
\textbf{{Total}} & \textbf{{{(l.get('lodos_uasb_kg_d_por_linea', l['lodos_kg_SST_d']/2) + l.get('lodos_fp_kg_d_por_linea', l['lodos_kg_SST_d']/2)):.2f}}} & \textbf{{{l.get('lodos_total_kg_d', l['lodos_kg_SST_d']):.2f}}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Ecuaciones de diseño}}

El volumen diario de lodo a tratar se determina mediante:

\begin{{equation}}
V_{{lodo}} = \frac{{M_{{SST}}}}{{C_{{SST}}}}
\end{{equation}}
\captionequation{{Volumen diario de lodo a tratar}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$V_{{lodo}}$] = Volumen diario de lodo (m³/d)
    \item[$M_{{SST}}$] = Masa de sólidos producidos TOTAL ({l.get('lodos_total_kg_d', l['lodos_kg_SST_d']):.2f} kg SST/d)
    \item[$C_{{SST}}$] = Concentración de sólidos ({l['C_SST_kg_m3']:.0f} kg/m³)
\end{{itemize}}

\begin{{equation}}
V_{{lodo}} = \frac{{{l.get('lodos_total_kg_d', l['lodos_kg_SST_d']):.2f}}}{{{l['C_SST_kg_m3']:.0f}}} = {l['V_lodo_m3_d']:.3f} \text{{ m}}^3\text{{/d}}
\end{{equation}}

\textbf{{Dimensionamiento del área}}

El área requerida se calcula considerando el volumen de lodo, el tiempo de secado y el espesor de aplicación:

\begin{{equation}}
A_{{total}} = \frac{{V_{{lodo}} \cdot t_s}}{{h_{{lodo}}}}
\end{{equation}}
\captionequation{{Area superficial total del lecho de secado}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_{{total}}$] = Área superficial total requerida (m²)
    \item[$t_s$] = Tiempo de secado ({l['t_secado_d']:.0f} días)
    \item[$h_{{lodo}}$] = Espesor de aplicación ({l['h_lodo_m']:.2f} m)
    \item[$n_{{celdas}}$] = Número de celdas ({l['n_celdas']:.0f}) (subdivisión interna)
\end{{itemize}}

\begin{{equation}}
A_{{total}} = \frac{{{l['V_lodo_m3_d']:.3f} \times {l['t_secado_d']:.0f}}}{{{l['h_lodo_m']:.2f}}} = {l['A_total_m2']:.1f} \text{{ m}}^2
\end{{equation}}

\textbf{{Distribución por tren de tratamiento}}

El área total se distribuye en bloques independientes, uno al final de cada tren de tratamiento:

\begin{{equation}}
A_{{bloque}} = \frac{{A_{{total}}}}{{n_{{lineas}}}} = \frac{{{l['A_total_m2']:.1f}}}{{{l['num_lineas']:.0f}}} = {l['A_bloque_m2']:.1f} \text{{ m}}^2 \text{{ por bloque}}
\end{{equation}}

\textbf{{Subdivisión interna en celdas}}

Cada bloque se subdivide internamente en celdas para operación por rotación:

\begin{{equation}}
A_{{celda}} = \frac{{A_{{total}}}}{{n_{{celdas}}}} = \frac{{{l['A_total_m2']:.1f}}}{{{l['n_celdas']:.0f}}} = {l['A_celda_m2']:.1f} \text{{ m}}^2 \text{{ por celda}}
\end{{equation}}

Con una relación largo/ancho de 3:1, las dimensiones de cada bloque son {l['largo_m']:.1f} m de largo por {l['ancho_m']:.1f} m de ancho.

\subsubsection{{Verificación de carga superficial}}

La carga superficial de sólidos se verifica mediante:

\begin{{equation}}
\rho_S = \frac{{M_{{SST}} \times 365}}{{A_{{total}}}} = \frac{{{l.get('lodos_total_kg_d', l['lodos_kg_SST_d']):.2f} \times 365}}{{{l['A_total_m2']:.1f}}} = {l['rho_S_kgSST_m2_año']:.1f} \text{{ kg SST/m}}^2\text{{·año}}
\end{{equation}}

El valor obtenido está dentro del rango recomendado de 60--220 kg SST/m²·año para lechos de secado de lodos anaerobios según Metcalf \& Eddy \cite{{metcalf2014}}.

\subsubsection{{Resultados}}

\begin{{table}}[H]
\centering
\caption{{Resumen del dimensionamiento del lecho de secado}}
\begin{{tabular}}{{ll}}
\toprule
Parámetro & Valor \\
\midrule
Área total requerida & {l['A_total_m2']:.1f} m² \\
Número de bloques (uno por tren) & {l['num_lineas']:.0f} \\
Área por bloque & {l['A_bloque_m2']:.1f} m² \\
Dimensiones de cada bloque (L×A) & {l['largo_m']:.1f} m × {l['ancho_m']:.1f} m \\
Número total de celdas & {l['n_celdas']:.0f} \\
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

\subsection{{Disposicion de la Planta y Areas de Predio}}

La figura \ref{{fig:layout_a}} presenta la disposicion espacial de las unidades de tratamiento. El layout muestra dos lineas paralelas operativas, cada una con capacidad para tratar {cfg.Q_linea_L_s:.1f} L/s, permitiendo la operacion con una sola linea durante mantenimiento o reparaciones.

\begin{{figure}}[H]
\centering
\includegraphics[width=\textwidth]{{{layout_filename}}}
\caption{{Disposición espacial de unidades}}
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
Zona de amortiguacion & Perimetral alrededor de unidades (2-3 m) para acceso y seguridad & {area_m2 * cfg.layout_factor_amortiguacion:.0f} m$^2$ ({cfg.layout_factor_amortiguacion*100:.0f}\%) \\
\addlinespace
Bodega de quimicos & Almacenamiento de hipoclorito y productos quimicos & {max(cfg.layout_area_min_bodega_quimicos_m2, area_m2 * cfg.layout_factor_bodega_quimicos):.0f} m$^2$ \\
\addlinespace
Laboratorio/control & Analisis de calidad del agua (DBO, SST, CF, pH) & {max(cfg.layout_area_min_laboratorio_m2, area_m2 * cfg.layout_factor_laboratorio):.0f} m$^2$ \\
\addlinespace
Caseta de operacion & Control, panel, escritorio, bano & {max(cfg.layout_area_min_caseta_operacion_m2, area_m2 * cfg.layout_factor_caseta):.0f} m$^2$ \\
\addlinespace
Area de lavado & Limpieza de equipos y herramientas & {max(cfg.layout_area_min_lavado_m2, area_m2 * cfg.layout_factor_lavado):.0f} m$^2$ \\
\addlinespace
Estacionamiento & Vehiculos del personal y visitantes (2-3 vehiculos) & {max(cfg.layout_area_min_estacionamiento_m2, area_m2 * cfg.layout_factor_estacionamiento):.0f} m$^2$ \\
\addlinespace
Zona de camiones & Acceso de camiones cisterna/retiro de lodo & {max(cfg.layout_area_min_zona_camiones_m2, area_m2 * cfg.layout_factor_zona_camiones):.0f} m$^2$ \\
\addlinespace
Caminos internas & Circulacion vehicular y peatonal (ancho 3--4 m) & {area_m2 * cfg.layout_factor_caminos:.0f} m$^2$ ({cfg.layout_factor_caminos*100:.0f}\% area) \\
\addlinespace
Acceso principal & Entrada, porton y caseta de guardia & {max(cfg.layout_area_min_acceso_principal_m2, area_m2 * cfg.layout_factor_acceso):.0f} m$^2$ \\
\addlinespace
Bodega general & Herramientas, repuestos, EPP & {max(cfg.layout_area_min_bodega_general_m2, area_m2 * cfg.layout_factor_bodega_general):.0f} m$^2$ \\
\addlinespace
Zona carga de lodos & Carga/descarga de lodo deshidratado & {max(cfg.layout_area_min_carga_lodos_m2, area_m2 * cfg.layout_factor_carga_lodos):.0f} m$^2$ \\
\addlinespace
Area verde/buffer & Separacion de limites, revegetacion & {area_total_calc * cfg.layout_factor_zona_verde:.0f} m$^2$ ({cfg.layout_factor_zona_verde*100:.0f}\% total) \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Area total estimada del predio}}

Considerando el area de tratamiento ({area_m2:.0f} m$^2$), amortiguacion ({cfg.layout_factor_amortiguacion*100:.0f}\%), complementarias operativas y zona verde ({cfg.layout_factor_zona_verde*100:.0f}\% del total):

\begin{{equation}}
A_{{total}} = \frac{{A_{{tratamiento}} + A_{{amortiguacion}} + A_{{complementarias}}}}{{1 - {cfg.layout_factor_zona_verde:.2f}}}
\end{{equation}}
\captionequation{{Formula del area total del predio}}

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_{{tratamiento}}$] = {area_m2:.0f} m$^2$
    \item[$A_{{amortiguacion}}$] = {area_m2 * cfg.layout_factor_amortiguacion:.0f} m$^2$ ({cfg.layout_factor_amortiguacion*100:.0f}\%)
    \item[$A_{{complementarias}}$] = {area_m2 * 0.25:.0f} m$^2$ (25\% operativas estimado)
\end{{itemize}}

\begin{{equation}}
A_{{total}} = \frac{{{area_m2:.0f} + {area_m2 * 0.20:.0f} + {area_m2 * 0.25:.0f}}}{{0.85}} \approx \mathbf{{{((area_m2 * 1.45) / 0.85):.0f} \text{{ m}}^2}} \approx \mathbf{{{(area_m2 * 1.705 / 10000):.2f} \text{{ ha}}}}
\end{{equation}}

\textbf{{Nota:}} El area total del predio debe ser de aproximadamente {((area_m2 * 1.45) / 0.85):.0f} m$^2$ ({(area_m2 * 1.705 / 10000):.2f} ha) para operacion adecuada con circulacion interna, estacionamiento y zonas verdes.
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
    sed = r.get('sedimentador_sec', {})
    desinf = r.get('cloro', r.get('desinfeccion', {}))
    lecho = r.get('lecho_secado', {})
    
    # Valores de calidad
    afluente = bal.get('afluente', {})
    efluente = bal.get('efluente_final', {})
    
    # Calcular area total del predio (dinamico)
    area_tratamiento = area_m2 if area_m2 else 990  # valor default si no se proporciona
    area_amortiguacion = area_tratamiento * 0.20
    area_complementaria = area_tratamiento * 0.25  # 25% para operativas
    area_total_calc = (area_tratamiento + area_amortiguacion + area_complementaria) / 0.85  # incluye 15% zona verde
    
    # Valores del efluente
    dbo_ef = efluente.get('DBO5_mg_L', 0)
    dqo_ef = efluente.get('DQO_mg_L', 0)
    sst_ef = efluente.get('SST_mg_L', 0)
    cf_ef = efluente.get('CF_NMP', 0)
    
    # Verificacion de cumplimiento para cada tabla TULSMA
    # Tabla 12 - Agua dulce
    cumple_t12_dbo = dbo_ef <= 100
    cumple_t12_dqo = dqo_ef <= 250
    cumple_t12_sst = sst_ef <= 130
    cumple_t12_cf = cf_ef <= 3000
    cumple_t12 = cumple_t12_dbo and cumple_t12_dqo and cumple_t12_sst and cumple_t12_cf
    
    # Tabla 13 - Agua marina
    cumple_t13_dbo = dbo_ef <= 100
    cumple_t13_dqo = dqo_ef <= 250
    cumple_t13_sst = sst_ef <= 100
    cumple_t13_cf = cf_ef <= 3000
    cumple_t13 = cumple_t13_dbo and cumple_t13_dqo and cumple_t13_sst and cumple_t13_cf
    
    # Tabla 11 - Alcantarillado
    cumple_t11_dbo = dbo_ef <= 250
    cumple_t11_dqo = dqo_ef <= 500
    cumple_t11_sst = sst_ef <= 220
    cumple_t11 = cumple_t11_dbo and cumple_t11_dqo and cumple_t11_sst
    
    # Tabla 3 - Flora y fauna (solo CF)
    cumple_t3_cf = cf_ef <= 200
    
    # Tabla 6/7 - Agricola/Pecuario (solo CF)
    cumple_t6_cf = cf_ef <= 1000
    
    # Tabla 9/10 - Recreativo
    cumple_t9_cf = cf_ef <= 200
    cumple_t10_cf = cf_ef <= 2000
    
    # Tabla 1 - Consumo humano
    cumple_t1_dbo = dbo_ef <= 2.0
    cumple_t1_cf = cf_ef <= 600
    
    # Estado de cumplimiento (sin conclusiones textuales, solo datos)
    estado_cumplimiento = "Cumple" if cumple_t12 else "No cumple"
    
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
\small
\begin{{tabular}}{{p{{3.2cm}}p{{3.5cm}}p{{1.5cm}}p{{4.8cm}}}}
\toprule
\textbf{{Unidad}} & \textbf{{Dimensiones (m)}} & \textbf{{Cantidad}} & \textbf{{Parametro Clave}} \\
\midrule
Rejillas & {rej.get('ancho_layout_m'):.2f} $\times$ {rej.get('h_tirante_m'):.2f} & {cfg.num_lineas} & Velocidad: {rej.get('v_canal_adoptada_m_s'):.2f} m/s \\
Desarenador & {des.get('b_canal_m'):.2f} $\times$ {des.get('L_diseno_m'):.1f} $\times$ {des.get('H_util_m') + 0.3:.1f} & {cfg.num_lineas} & TRH: {des.get('t_r_real_s', des.get('t_r_nominal_s', 30)):.0f}~s (referencia: 30--60~s) \\
Reactor UASB & D = {uasb.get('D_m'):.2f}, H = {uasb.get('H_r_m'):.1f} & {cfg.num_lineas} & v$_{{up}}$ = {uasb.get('v_up_m_h'):.2f} m/h \\
Filtro Percolador & D = {fp.get('D_filtro_m'):.2f}, H = {fp.get('H_total_m'):.1f} & {cfg.num_lineas} & Q$_A$ = {fp.get('Q_A_real_m3_m2_h', 0):.3f} m$^3$/m$^2$·h (máx: {fp.get('Q_A_max_m3_m2_h', 0):.2f}) \\
Sedimentador Secundario & D = {sed.get('D_m'):.2f}, H = {sed.get('h_sed_m'):.1f} & {cfg.num_lineas} & SOR = {sed.get('SOR_m3_m2_d'):.1f} m$^3$/m$^2\cdot$d \\
Desinfeccion (Cloro) & {desinf.get('largo_m'):.1f} $\times$ {desinf.get('ancho_m'):.1f} $\times$ {desinf.get('h_total_m'):.1f} & {cfg.num_lineas} & CT = {desinf.get('CT_mg_min_L'):.0f} mg$\cdot$min/L \\
Lecho de Secado & {lecho.get('largo_m'):.1f} $\times$ {lecho.get('ancho_m'):.1f} & {cfg.num_lineas} & Área: {lecho.get('A_bloque_m2'):.1f} m$^2$ \\
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
Agua dulce -- Tabla 12 & $\leq$100 & $\leq$250 & $\leq$130 & $\leq$3000 & {'CUMPLE' if cumple_t12 else 'NO CUMPLE'} \\
Agua marina -- Tabla 13 & $\leq$100 & $\leq$250 & $\leq$100 & $\leq$3000 & {'CUMPLE' if cumple_t13 else 'NO CUMPLE'} \\
Alcantarillado -- Tabla 11 & $\leq$250 & $\leq$500 & $\leq$220 & --- & {'CUMPLE' if cumple_t11 else 'NO CUMPLE'} \\
Flora y fauna -- Tabla 3 & --- & --- & --- & $\leq$200 & {'CUMPLE' if cumple_t3_cf else 'NO CUMPLE'} \\
Agricola/riego -- Tabla 6 & --- & --- & --- & $\leq$1000 & {'CUMPLE' if cumple_t6_cf else 'NO CUMPLE'} \\
Pecuario -- Tabla 7 & --- & --- & --- & $\leq$1000 & {'CUMPLE' if cumple_t6_cf else 'NO CUMPLE'} \\
Recreativo primario -- Tabla 9 & --- & --- & --- & $\leq$200 & {'CUMPLE' if cumple_t9_cf else 'NO CUMPLE'} \\
Recreativo secundario -- Tabla 10 & --- & --- & --- & $\leq$2000 & {'CUMPLE' if cumple_t10_cf else 'NO CUMPLE'} \\
Consumo humano trat. conv. -- Tabla 1 & $\leq$2.0 & --- & --- & $\leq$600 & {'CUMPLE' if (cumple_t1_dbo and cumple_t1_cf) else 'NO CUMPLE'} \\
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
Area de amortiguacion (20\%) & {area_m2 * 0.20:.0f} m$^2$ \\
Area complementaria operativa & {area_m2 * 0.25:.0f} m$^2$ (25\% estimado) \\
Zona verde (15\% del total) & {area_total_calc * 0.15:.0f} m$^2$ \\
\midrule
\textbf{{Area total requerida}} & \textbf{{{area_total_calc:.0f} m$^2$ ({(area_total_calc/10000):.2f} ha)}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Produccion de Lodos}}

% Calcular valores por línea para tabla
\begin{{table}}[H]
\centering
\caption{{Generacion y manejo de lodos - TOTAL PLANTA ({cfg.num_lineas} líneas)}}
\begin{{tabular}}{{lcc}}
\toprule
\textbf{{Concepto}} & \textbf{{Por línea}} & \textbf{{Total planta}} \\
\midrule
Produccion lodos UASB & {lecho.get('lodos_uasb_kg_d_por_linea', lecho.get('lodos_uasb_kg_d', 0)/2):.1f} kg SST/d & {lecho.get('lodos_uasb_kg_d', 0):.1f} kg SST/d \\
Produccion humus FP + Sed & {lecho.get('lodos_fp_kg_d_por_linea', lecho.get('lodos_fp_kg_d', 0)/2):.1f} kg SST/d & {lecho.get('lodos_fp_kg_d', 0):.1f} kg SST/d \\
\midrule
\textbf{{Total lodos}} & \textbf{{{lecho.get('lodos_total_kg_d_por_linea', lecho.get('lodos_total_kg_d', 0)/2):.1f} kg SST/d}} & \textbf{{{lecho.get('lodos_total_kg_d', 0):.1f} kg SST/d}} \\
Area de lechos de secado & --- & {lecho.get('A_total_m2'):.1f} m$^2$ ({cfg.num_lineas} bloques) \\
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
Hipoclorito de sodio ({desinf.get('concentracion_NaOCl_pct', 10):.0f}\\%) & {desinf.get('volumen_NaOCl_L_d'):.1f} & L/d \\
Consumo hipoclorito anual & {desinf.get('volumen_NaOCl_L_d') * 365 / 1000:.0f} & m$^3$/a\~no \\
\bottomrule
\end{{tabular}}
\end{{table}}

"""


def generar_latex_alternativa_A(cfg, resultados, output_path, area_m2=None, balance_calidad=None):
    """Genera archivo LaTeX completo (incluye layout automático)"""
    
    # Importar y generar layout automáticamente
    from ptar_layout_graficador import generar_layout_con_resultados, generar_esquema_uasb
    import os
    
    output_dir = os.path.dirname(output_path) or '.'
    unidades = ["Rejillas", "Desarenador", "UASB", "Filtro_Percolador", 
                "Sedimentador", "Cloro"]
    
    print("Generando layout automáticamente...")
    try:
        x, y = generar_layout_con_resultados(
            "A", unidades, "UASB + Filtro Percolador", resultados, output_dir,
            caudal_L_s=cfg.Q_linea_L_s
        )
        area_m2 = round(x * y)
        layout_filename = "Layout_A_2lineas.png"
        print(f"  Layout generado: {layout_filename} ({x:.1f}m x {y:.1f}m)")
    except Exception as e:
        print(f"  [ADVERTENCIA] No se pudo generar layout: {e}")
        layout_filename = "Layout_A_2lineas.png"
    
    # Generar esquema del UASB
    print("Generando esquema del reactor UASB...")
    try:
        uasb_resultados = resultados.get('uasb', {})
        if uasb_resultados:
            esquema_path = generar_esquema_uasb(uasb_resultados, output_dir)
            esquema_filename = "Esquema_UASB.png"
            print(f"  Esquema UASB generado: {esquema_filename}")
        else:
            esquema_filename = None
    except Exception as e:
        print(f"  [ADVERTENCIA] No se pudo generar esquema UASB: {e}")
        esquema_filename = None
    
    # Generar archivo de bibliografía
    print("Generando archivo de bibliografía...")
    try:
        _generar_bibliografia(output_dir)
        print("  Bibliografía generada: referencias.bib")
    except Exception as e:
        print(f"  [ADVERTENCIA] No se pudo generar bibliografía: {e}")
    
    contenido = generar_contenido_alternativa_A(cfg, resultados, layout_filename=layout_filename, area_m2=area_m2, balance_calidad=balance_calidad)
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
\usepackage{{tocloft}}
\usepackage{{titletoc}}
\usepackage{{natbib}}

% Configuracion para indice de ecuaciones
\newcommand{{\listequationsname}}{{Indice de Ecuaciones}}
\newlistof{{myequation}}{{loe}}{{\listequationsname}}
\renewcommand{{\themyequation}}{{\arabic{{equation}}}}
\newcommand{{\captionequation}}[1]{{%
    \addcontentsline{{loe}}{{myequation}}{{\protect\numberline{{\themyequation}}#1}}%
}}

\geometry{{margin=2.5cm}}

\hypersetup{{
    colorlinks=true,
    linkcolor=black,
    citecolor=blue,
    urlcolor=blue
}}

\begin{{document}}

% Profundidad del indice: solo secciones principales (sin 1.1, 1.1.1, etc.)
\setcounter{{tocdepth}}{{2}}

% ============================================================================
% PORTADA
% ============================================================================
\begin{{titlepage}}
    \centering
    \vspace*{{3cm}}
    {{\Huge\bfseries Memoria de Calculo}}\\[1.5cm]
    {{\Large Dimensionamiento de:}}\\[0.5cm]
    {{\LARGE Sistema de Tratamiento Anaerobio-Aerobio}}\\[0.3cm]
    {{\LARGE con Reactor de Flujo Ascendente y Filtracion Percolante}}\\[2cm]
    {{\large Caudal de disenio: {cfg.Q_linea_L_s * cfg.num_lineas:.1f} L/s}}\\[0.3cm]
    {{\large Numero de lineas: {cfg.num_lineas}}}\\[2cm]
    \vfill
    {{\large Fecha: \today}}
\end{{titlepage}}

% ============================================================================
% INDICES
% ============================================================================
\newpage
\tableofcontents
\newpage
\listoffigures
\listoftables
\listof{{myequation}}{{\listequationsname}}
\newpage

{contenido}

{resumen}

\newpage
%============================================================================
% ANEXO: TABLAS TULSMA COMPLETAS
%============================================================================
\appendix
\section{{Anexo: TULSMA -- Criterios de Calidad del Recurso Agua}}
\label{{app:tulsma}}

\begin{{center}}
{{\LARGE\bfseries TULSMA -- Norma de Calidad Ambiental\\[4pt]
del Recurso Agua}}\\[8pt]
{{\large Libro VI, Anexo 1 -- Acuerdo Ministerial 097-A (2015)\\
Decreto Ejecutivo 3516 -- Ecuador}}\\[4pt]
{{\small Criterios de calidad por uso del agua y l\'imites de descarga de efluentes}}
\end{{center}}
\vspace{{10pt}}

% ----------------------------------------------------------
\subsection{{Tabla 1 -- Consumo Humano y Uso Dom\'estico (tratamiento convencional)}}
% ----------------------------------------------------------

\small
\begin{{longtable}}{{p{{4.5cm}}p{{2.0cm}}p{{2.0cm}}p{{3.5cm}}}}
\caption{{L\'imites m\'aximos permisibles para aguas de consumo humano y uso dom\'estico que \'unicamente requieren tratamiento convencional (TULSMA, Tabla~1).}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endfirsthead
\multicolumn{{4}}{{c}}{{\small\itshape Continuaci\'on de la Tabla}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endhead
\bottomrule
\endlastfoot
Aceites y Grasas & Sust.\ solubles en hexano & mg/L & $\leq$ 0,3 \\
Aluminio & Al & mg/L & $\leq$ 0,2 \\
Amoniaco & N-Amoniacal & mg/L & $\leq$ 1,0 \\
Amonio & NH$_4$ & mg/L & $\leq$ 0,05 \\
Ars\'enico (total) & As & mg/L & $\leq$ 0,05 \\
Bario & Ba & mg/L & $\leq$ 1,0 \\
Cadmio & Cd & mg/L & $\leq$ 0,01 \\
Cianuro total & CN$^-$ & mg/L & $\leq$ 0,1 \\
Cloruros & Cl$^-$ & mg/L & $\leq$ 250 \\
Cobre & Cu & mg/L & $\leq$ 1,0 \\
\textbf{{Coliformes totales}} & NMP & NMP/100 mL & $\leq$ 3\,000 \\
\textbf{{Coliformes fecales}} & NMP & NMP/100 mL & $\leq$ 600 \\
Color real & UC & Unidades de color & $\leq$ 100 \\
Compuestos fen\'olicos & Fenol & mg/L & $\leq$ 0,002 \\
Cromo hexavalente & Cr$^{{6+}}$ & mg/L & $\leq$ 0,05 \\
\textbf{{DBO$_5$}} & -- & mg/L & $\leq$ 2,0 \\
Dureza & CaCO$_3$ & mg/L & $\leq$ 500 \\
Fluoruro total & F & mg/L & $\leq$ 1,5 \\
Hierro total & Fe & mg/L & $\leq$ 1,0 \\
Manganeso total & Mn & mg/L & $\leq$ 0,1 \\
Materia flotante & -- & -- & Ausencia \\
Mercurio total & Hg & mg/L & $\leq$ 0,001 \\
Nitrato & N-Nitrato & mg/L & $\leq$ 10,0 \\
Nitrito & N-Nitrito & mg/L & $\leq$ 1,0 \\
Ox\'igeno disuelto & O.D. & mg/L & $\geq$ 80\% saturaci\'on; $\geq$ 6 mg/L \\
pH & -- & -- & $6,0 - 9,0$ \\
Plata total & Ag & mg/L & $\leq$ 0,05 \\
Plomo total & Pb & mg/L & $\leq$ 0,05 \\
Selenio total & Se & mg/L & $\leq$ 0,01 \\
Sodio & Na & mg/L & $\leq$ 200 \\
S\'olidos disueltos totales & -- & mg/L & $\leq$ 1\,000 \\
Sulfatos & SO$_4^{{2-}}$ & mg/L & $\leq$ 400 \\
Temperatura & -- & $^\circ$C & Cond.\ natural $\pm$ 3\,$^\circ$C \\
Tensoactivos & SAAM & mg/L & $\leq$ 0,5 \\
Turbiedad & -- & UTN & $\leq$ 100 \\
Zinc & Zn & mg/L & $\leq$ 5,0 \\
\end{{longtable}}

% ----------------------------------------------------------
\subsection{{Tabla 12 -- Descarga a Cuerpo de Agua Dulce}}
\tiny
% ----------------------------------------------------------

{{\small\textbf{{Nota:}} Esta es la tabla aplicable al proyecto de tratamiento de aguas residuales municipales cuando el efluente se vierte a un r\'io, lago o cuerpo superficial de agua dulce.}}

\vspace{{6pt}}

\small
\begin{{longtable}}{{p{{4.5cm}}p{{2.0cm}}p{{2.0cm}}p{{3.5cm}}}}
\caption{{L\'imites m\'aximos permisibles de descarga a un cuerpo de agua dulce (TULSMA, Tabla~12).}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endfirsthead
\multicolumn{{4}}{{c}}{{\small\itshape Continuaci\'on de la Tabla}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endhead
\bottomrule
\endlastfoot
Aceites y grasas & Sust.\ solubles en hexano & mg/L & $\leq$ 0,3 \\
Aluminio & Al & mg/L & $\leq$ 5,0 \\
Ars\'enico total & As & mg/L & $\leq$ 0,1 \\
Bario & Ba & mg/L & $\leq$ 2,0 \\
Cadmio & Cd & mg/L & $\leq$ 0,02 \\
Cianuro total & CN$^-$ & mg/L & $\leq$ 0,1 \\
Cloruros & Cl$^-$ & mg/L & $\leq$ 1\,000 \\
Cobre & Cu & mg/L & $\leq$ 1,0 \\
\textbf{{Coliformes fecales}}$^\dagger$ & NMP & NMP/100 mL & $\leq$ 3\,000 \\
Compuestos fen\'olicos & Fenol & mg/L & $\leq$ 0,2 \\
Cromo hexavalente & Cr$^{{6+}}$ & mg/L & $\leq$ 0,5 \\
\textbf{{DBO$_5$}} & -- & mg/L & $\leq$ 100 \\
\textbf{{DQO}} & -- & mg/L & $\leq$ 250 \\
Fluoruros & F$^-$ & mg/L & $\leq$ 5,0 \\
F\'osforo total & P & mg/L & $\leq$ 10,0 \\
Hierro total & Fe & mg/L & $\leq$ 10,0 \\
Manganeso total & Mn & mg/L & $\leq$ 2,0 \\
Materia flotante & -- & -- & Ausencia \\
Mercurio total & Hg & mg/L & $\leq$ 0,005 \\
N\'iquel & Ni & mg/L & $\leq$ 2,0 \\
Nitr\'ogeno amoniacal & N-NH$_3$ & mg/L & $\leq$ 30,0 \\
Nitr\'ogeno total Kjeldahl & N-TKN & mg/L & $\leq$ 50,0 \\
pH & -- & -- & $6,0 - 9,0$ \\
Plata total & Ag & mg/L & $\leq$ 0,1 \\
Plomo total & Pb & mg/L & $\leq$ 0,2 \\
Selenio & Se & mg/L & $\leq$ 0,1 \\
\textbf{{S\'olidos sedimentables}} & -- & mL/L & $\leq$ 1,0 \\
\textbf{{S\'olidos suspendidos totales}} & -- & mg/L & $\leq$ 130 \\
S\'olidos totales & -- & mg/L & $\leq$ 1\,600 \\
Sulfatos & SO$_4^{{2-}}$ & mg/L & $\leq$ 1\,000 \\
Sulfuros & S$^{{2-}}$ & mg/L & $\leq$ 0,5 \\
Temperatura & -- & $^\circ$C & Cond.\ natural $\pm$ 3\,$^\circ$C; m\'ax.\ 32\,$^\circ$C \\
Tensoactivos & SAAM & mg/L & $\leq$ 0,5 \\
Zinc & Zn & mg/L & $\leq$ 5,0 \\
\multicolumn{{4}}{{l}}{{\scriptsize $^\dagger$ Aquellos con descargas $\leq$ 3\,000 NMP/100 mL quedan exentos de tratamiento de desinfecci\'on.}}\\
\end{{longtable}}
\normalsize

% ----------------------------------------------------------
\subsection{{Tabla 13 -- Descarga a Cuerpo de Agua Marina}}
\tiny
% ----------------------------------------------------------

\small
\begin{{longtable}}{{p{{4.5cm}}p{{2.0cm}}p{{2.0cm}}p{{3.5cm}}}}
\caption{{L\'imites m\'aximos permisibles de descarga a un cuerpo de agua marina (TULSMA, Tabla~13).}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endfirsthead
\multicolumn{{4}}{{c}}{{\small\itshape Continuaci\'on de la Tabla}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endhead
\bottomrule
\endlastfoot
Aceites y grasas & Sust.\ solubles en hexano & mg/L & $\leq$ 0,3 \\
Aluminio & Al & mg/L & $\leq$ 5,0 \\
Ars\'enico total & As & mg/L & $\leq$ 0,1 \\
Cadmio & Cd & mg/L & $\leq$ 0,1 \\
Cianuro total & CN$^-$ & mg/L & $\leq$ 0,1 \\
Cobre & Cu & mg/L & $\leq$ 0,5 \\
\textbf{{Coliformes fecales}}$^\ddagger$ & NMP & NMP/100 mL & $\leq$ 3\,000 \\
Compuestos fen\'olicos & Fenol & mg/L & $\leq$ 0,2 \\
Cromo hexavalente & Cr$^{{6+}}$ & mg/L & $\leq$ 0,5 \\
\textbf{{DBO$_5$}} & -- & mg/L & $\leq$ 100 \\
\textbf{{DQO}} & -- & mg/L & $\leq$ 250 \\
Fluoruros & F$^-$ & mg/L & $\leq$ 5,0 \\
Hierro total & Fe & mg/L & $\leq$ 10,0 \\
Manganeso total & Mn & mg/L & $\leq$ 2,0 \\
Materia flotante & -- & -- & Ausencia \\
Mercurio total & Hg & mg/L & $\leq$ 0,005 \\
N\'iquel & Ni & mg/L & $\leq$ 2,0 \\
Nitr\'ogeno amoniacal & N-NH$_3$ & mg/L & $\leq$ 30,0 \\
Nitr\'ogeno total Kjeldahl & N-TKN & mg/L & $\leq$ 50,0 \\
pH & -- & -- & $6,0 - 9,0$ \\
Plomo total & Pb & mg/L & $\leq$ 0,2 \\
\textbf{{S\'olidos suspendidos totales}} & -- & mg/L & $\leq$ 100 \\
Temperatura & -- & $^\circ$C & Cond.\ natural $\pm$ 3\,$^\circ$C; m\'ax.\ 32\,$^\circ$C \\
Tensoactivos & SAAM & mg/L & $\leq$ 0,5 \\
Zinc & Zn & mg/L & $\leq$ 5,0 \\
\multicolumn{{4}}{{l}}{{\footnotesize $^\ddagger$ Aquellos con descargas $\leq$ 3\,000 NMP/100 mL quedan exentos de tratamiento de desinfecci\'on.}}\\
\end{{longtable}}

% ----------------------------------------------------------
\subsection{{Tabla 2 -- Consumo Humano (solo desinfecci\'on)}}
% ----------------------------------------------------------

\small
\begin{{longtable}}{{p{{4.5cm}}p{{2.0cm}}p{{2.0cm}}p{{3.5cm}}}}
\caption{{L\'imites m\'aximos permisibles para aguas de consumo humano que \'unicamente requieren desinfecci\'on (TULSMA, Tabla~2).}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endfirsthead
\multicolumn{{4}}{{c}}{{\small\itshape Continuaci\'on de la Tabla}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endhead
\bottomrule
\endlastfoot
Aceites y Grasas & Sust.\ solubles en hexano & mg/L & $\leq$ 0,3 \\
Aluminio total & Al & mg/L & $\leq$ 0,1 \\
Amoniaco & N-Amoniacal & mg/L & $\leq$ 1,0 \\
Ars\'enico total & As & mg/L & $\leq$ 0,05 \\
Bario & Ba & mg/L & $\leq$ 1,0 \\
Berilio & Be & mg/L & $\leq$ 0,1 \\
Boro total & B & mg/L & $\leq$ 0,75 \\
Cadmio & Cd & mg/L & $\leq$ 0,001 \\
Cianuro total & CN$^-$ & mg/L & $\leq$ 0,01 \\
Cobalto & Co & mg/L & $\leq$ 0,2 \\
Cobre & Cu & mg/L & $\leq$ 1,0 \\
Color real & -- & UC & $\leq$ 20 \\
\textbf{{Coliformes totales}}$^*$ & NMP & NMP/100 mL & $\leq$ 50 \\
Cloruros & Cl$^-$ & mg/L & $\leq$ 250 \\
Compuestos fen\'olicos & Fenol & mg/L & $\leq$ 0,002 \\
Cromo hexavalente & Cr$^{{6+}}$ & mg/L & $\leq$ 0,05 \\
\textbf{{DBO$_5$}} & -- & mg/L & $\leq$ 2,0 \\
Dureza & CaCO$_3$ & mg/L & $\leq$ 500 \\
Esta\~no & Sn & mg/L & $\leq$ 2,0 \\
Fluoruros & F & mg/L & $<$ 1,4 \\
Hierro total & Fe & mg/L & $\leq$ 0,3 \\
Litio & Li & mg/L & $\leq$ 2,5 \\
Manganeso total & Mn & mg/L & $\leq$ 0,1 \\
Materia flotante & -- & -- & Ausencia \\
Mercurio total & Hg & mg/L & $\leq$ 0,001 \\
N\'iquel & Ni & mg/L & $\leq$ 0,025 \\
Nitrato & N-Nitrato & mg/L & $\leq$ 10,0 \\
Nitrito & N-Nitrito & mg/L & $\leq$ 1,0 \\
Olor y sabor & -- & -- & Ausencia \\
Ox\'igeno disuelto & O.D. & mg/L & $\geq$ 80\% saturaci\'on; $\geq$ 6 mg/L \\
pH & -- & -- & $6,0 - 9,0$ \\
Plata total & Ag & mg/L & $\leq$ 0,05 \\
Plomo total & Pb & mg/L & $\leq$ 0,05 \\
Selenio total & Se & mg/L & $\leq$ 0,01 \\
Sodio & Na & mg/L & $\leq$ 200 \\
S\'olidos disueltos totales & -- & mg/L & $\leq$ 500 \\
Sulfatos & SO$_4^{{2-}}$ & mg/L & $\leq$ 250 \\
Temperatura & -- & $^\circ$C & Cond.\ natural $\pm$ 3\,$^\circ$C \\
Tensoactivos & SAAM & mg/L & $\leq$ 0,5 \\
Turbiedad & -- & UTN & $\leq$ 10 \\
Vanadio & V & mg/L & $\leq$ 0,1 \\
Zinc & Zn & mg/L & $\leq$ 5,0 \\
\multicolumn{{4}}{{l}}{{\scriptsize $^*$ Si $>$40\% del NMP corresponde a coliformes fecales, se requiere tratamiento convencional.}}\\
\end{{longtable}}
\normalsize

% ----------------------------------------------------------
\subsection{{Tabla 3 -- Preservaci\'on de Flora y Fauna}}
% ----------------------------------------------------------

\small
\begin{{longtable}}{{p{{4.0cm}}p{{1.8cm}}p{{1.2cm}}p{{2.5cm}}p{{2.5cm}}p{{2.5cm}}}}
\caption{{Criterios de calidad admisibles para la preservaci\'on de flora y fauna en aguas dulces y marinas (TULSMA, Tabla~3).}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{Agua fr\'ia dulce}} & \textbf{{Agua c\'alida dulce}} & \textbf{{Agua marina/estuario}} \\
\midrule
\endfirsthead
\multicolumn{{6}}{{c}}{{\small\itshape Continuaci\'on de la Tabla}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{Agua fr\'ia dulce}} & \textbf{{Agua c\'alida dulce}} & \textbf{{Agua marina/estuario}} \\
\midrule
\endhead
\bottomrule
\endlastfoot
Aluminio & Al & mg/L & $\leq$ 0,1 & $\leq$ 0,1 & $\leq$ 1,5 \\
Amoniaco no ionizado & NH$_3$ & mg/L & $\leq$ 0,02 & $\leq$ 0,02 & $\leq$ 0,4 \\
Ars\'enico & As & mg/L & $\leq$ 0,05 & $\leq$ 0,05 & $\leq$ 0,05 \\
Bario & Ba & mg/L & $\leq$ 1,0 & $\leq$ 1,0 & $\leq$ 1,0 \\
Berilio & Be & mg/L & $\leq$ 0,1 & $\leq$ 0,1 & $\leq$ 1,5 \\
Bifenilos policlorados (PCBs) & PCBs totales & mg/L & $\leq$ 0,001 & $\leq$ 0,001 & $\leq$ 0,001 \\
Boro & B & mg/L & $\leq$ 0,75 & $\leq$ 0,75 & $\leq$ 5,0 \\
Cadmio & Cd & mg/L & $\leq$ 0,001 & $\leq$ 0,001 & $\leq$ 0,005 \\
Cianuro libre & CN$^-$ & mg/L & $\leq$ 0,01 & $\leq$ 0,01 & $\leq$ 0,01 \\
Cloro residual & Cl & mg/L & $\leq$ 0,01 & $\leq$ 0,01 & $\leq$ 0,01 \\
Clorofenoles & -- & mg/L & $\leq$ 0,5 & $\leq$ 0,5 & $\leq$ 0,5 \\
Cobalto & Co & mg/L & $\leq$ 0,2 & $\leq$ 0,2 & $\leq$ 0,2 \\
\textbf{{Coliformes fecales}} & NMP & NMP/100 mL & $\leq$ 200 & $\leq$ 200 & $\leq$ 200 \\
Cobre & Cu & mg/L & $\leq$ 0,02 & $\leq$ 0,02 & $\leq$ 0,05 \\
Cromo total & Cr & mg/L & $\leq$ 0,05 & $\leq$ 0,05 & $\leq$ 0,05 \\
Fenoles monoh\'idricos & Fenoles & mg/L & $\leq$ 0,001 & $\leq$ 0,001 & $\leq$ 0,001 \\
Grasas y aceites & Sust.\ hex. & mg/L & $\leq$ 0,3 & $\leq$ 0,3 & $\leq$ 0,3 \\
HAPs totales & HAPs & mg/L & $\leq$ 0,0003 & $\leq$ 0,0003 & $\leq$ 0,0003 \\
Hierro & Fe & mg/L & $\leq$ 0,3 & $\leq$ 0,3 & $\leq$ 0,3 \\
Hidrocarburos totales de petr\'oleo & TPH & mg/L & $\leq$ 0,5 & $\leq$ 0,5 & $\leq$ 0,5 \\
Manganeso & Mn & mg/L & $\leq$ 0,1 & $\leq$ 0,1 & $\leq$ 0,1 \\
Materia flotante & -- & -- & Ausencia & Ausencia & Ausencia \\
Mercurio & Hg & mg/L & $\leq$ 0,0002 & $\leq$ 0,0002 & $\leq$ 0,0001 \\
N\'iquel & Ni & mg/L & $\leq$ 0,025 & $\leq$ 0,025 & $\leq$ 0,1 \\
Ox\'igeno disuelto & O.D. & mg/L & $\geq$ 80\%; $\geq$ 6 & $\geq$ 60\%; $\geq$ 5 & $\geq$ 60\%; $\geq$ 5 \\
pH & -- & -- & $6,5 - 9,0$ & $6,5 - 9,0$ & $6,5 - 9,5$ \\
Plaguicidas organoclorados & Org.\ totales & $\mu$g/L & $\leq$ 10,0 & $\leq$ 10,0 & $\leq$ 10,0 \\
Plaguicidas organofosforados & Org.\ totales & $\mu$g/L & $\leq$ 10,0 & $\leq$ 10,0 & $\leq$ 10,0 \\
Plata & Ag & mg/L & $\leq$ 0,01 & $\leq$ 0,01 & $\leq$ 0,005 \\
Plomo & Pb & mg/L & $\leq$ 0,01 & $\leq$ 0,01 & -- \\
Piretroides & Piretroides totales & mg/L & $\leq$ 0,05 & $\leq$ 0,05 & $\leq$ 0,05 \\
Selenio & Se & mg/L & $\leq$ 0,01 & $\leq$ 0,01 & $\leq$ 0,01 \\
Sulfuro de hidr\'ogeno ionizado & H$_2$S & mg/L & $\leq$ 0,0002 & $\leq$ 0,0002 & $\leq$ 0,0002 \\
Temperatura & -- & $^\circ$C & C.N.\ + 3 (m\'ax.\ 20) & C.N.\ + 3 (m\'ax.\ 32) & C.N.\ + 3 (m\'ax.\ 32) \\
Tensoactivos & SAAM & mg/L & $\leq$ 0,5 & $\leq$ 0,5 & $\leq$ 0,5 \\
Zinc & Zn & mg/L & $\leq$ 0,18 & $\leq$ 0,18 & $\leq$ 0,17 \\
\multicolumn{{6}}{{l}}{{\scriptsize C.N.~= Condici\'on natural.}}\\
\end{{longtable}}
\normalsize

% ----------------------------------------------------------
\subsection{{Tabla 6 -- Uso Agr\'icola o de Riego}}
% ----------------------------------------------------------

\small
\begin{{longtable}}{{p{{4.5cm}}p{{2.0cm}}p{{2.0cm}}p{{3.5cm}}}}
\caption{{Criterios de calidad admisibles para aguas de uso agr\'icola o de riego (TULSMA, Tabla~6).}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endfirsthead
\multicolumn{{4}}{{c}}{{\small\itshape Continuaci\'on de la Tabla}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endhead
\bottomrule
\endlastfoot
Aceites y grasas & Sust.\ solubles en hexano & mg/L & $\leq$ 0,1 \\
Ars\'enico & As & mg/L & $\leq$ 0,1 \\
Benceno & -- & mg/L & $\leq$ 0,01 \\
Cadmio & Cd & mg/L & $\leq$ 0,01 \\
Cianuro total & CN$^-$ & mg/L & $\leq$ 0,2 \\
\textbf{{Coliformes fecales}}$^*$ & NMP & NMP/100 mL & $\leq$ 1\,000 \\
Conductividad el\'ectrica & -- & $\mu$mho/cm & $\leq$ 3\,000 \\
Cloruros & Cl$^-$ & mg/L & $\leq$ 1\,000 \\
Cromo total & Cr & mg/L & $\leq$ 0,1 \\
Hierro & Fe & mg/L & $\leq$ 5,0 \\
Mercurio total & Hg & mg/L & $\leq$ 0,001 \\
pH & -- & -- & $6,0 - 9,0$ \\
Plomo & Pb & mg/L & $\leq$ 5,0 \\
Sodio & Na & mg/L & $\leq$ 200 \\
Sulfatos & SO$_4^{{2-}}$ & mg/L & $\leq$ 1\,000 \\
Vanadio & V & mg/L & $\leq$ 0,1 \\
Zinc & Zn & mg/L & $\leq$ 2,0 \\
\multicolumn{{4}}{{l}}{{\scriptsize $^*$ Para riego de cultivos para consumo humano en contacto directo con el suelo.}}\\
\end{{longtable}}
\normalsize

% ----------------------------------------------------------
\subsection{{Tabla 7 -- Uso Pecuario}}
% ----------------------------------------------------------

\small
\begin{{longtable}}{{p{{4.5cm}}p{{2.0cm}}p{{2.0cm}}p{{3.5cm}}}}
\caption{{Criterios de calidad admisibles para aguas de uso pecuario (TULSMA, Tabla~7).}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endfirsthead
\multicolumn{{4}}{{c}}{{\small\itshape Continuaci\'on de la Tabla}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endhead
\bottomrule
\endlastfoot
Aceites y grasas & Sust.\ solubles en hexano & mg/L & $\leq$ 0,1 \\
Ars\'enico & As & mg/L & $\leq$ 0,2 \\
Cadmio & Cd & mg/L & $\leq$ 0,05 \\
Cianuro total & CN$^-$ & mg/L & $\leq$ 0,2 \\
\textbf{{Coliformes fecales}} & NMP & NMP/100 mL & $\leq$ 1\,000 \\
Conductividad el\'ectrica & -- & $\mu$mho/cm & $\leq$ 5\,000 \\
Cromo total & Cr & mg/L & $\leq$ 1,0 \\
Fluoruros & F$^-$ & mg/L & $\leq$ 2,0 \\
Mercurio total & Hg & mg/L & $\leq$ 0,01 \\
Nitratos & NO$_3^-$ & mg/L & $\leq$ 45 \\
pH & -- & -- & $6,0 - 9,0$ \\
Plomo & Pb & mg/L & $\leq$ 0,1 \\
Sulfatos & SO$_4^{{2-}}$ & mg/L & $\leq$ 500 \\
\end{{longtable}}

% ----------------------------------------------------------
\subsection{{Tablas 9 y 10 -- Uso Recreativo}}
% ----------------------------------------------------------

\begin{{longtable}}{{p{{5.0cm}}p{{1.8cm}}p{{3.5cm}}p{{3.5cm}}}}
\caption{{Criterios de calidad para aguas destinadas a fines recreativos (TULSMA, Tablas~9 y 10).}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Unidad}} & \textbf{{Contacto primario$^a$}} & \textbf{{Contacto secundario$^b$}} \\
\midrule
\endfirsthead
\multicolumn{{4}}{{c}}{{\small\itshape Continuaci\'on de la Tabla}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Unidad}} & \textbf{{Contacto primario}} & \textbf{{Contacto secundario}} \\
\midrule
\endhead
\bottomrule
\endlastfoot
\textbf{{Coliformes fecales}} & NMP/100 mL & $\leq$ 200 & $\leq$ 2\,000 \\
Coliformes totales & NMP/100 mL & $\leq$ 1\,000 & -- \\
Aceites y grasas & -- & Ausencia visible & Ausencia visible \\
Color & -- & Inapreciable & Inapreciable \\
Materia flotante & -- & Ausencia & Ausencia \\
Ox\'igeno disuelto & mg/L & $\geq$ 6,0 & $\geq$ 5,0 \\
pH & -- & $6,0 - 9,0$ & $6,0 - 9,0$ \\
Temperatura & $^\circ$C & $\leq$ 30 & $\leq$ 30 \\
Turbiedad & UTN & $\leq$ 10 & -- \\
\multicolumn{{4}}{{l}}{{\scriptsize $^a$ Nado, buc\'eo, esqu\'i acu\'atico, surf.}} \\
\multicolumn{{4}}{{l}}{{\scriptsize $^b$ Pesca, navegaci\'on deportiva, remo.}} \\
\end{{longtable}}
\normalsize

% ============================================================
\newpage
\subsection{{L\'imites de Descarga de Efluentes}}
% ============================================================

% ----------------------------------------------------------
\subsubsection{{Tabla 11 -- Descarga al Sistema de Alcantarillado P\'ublico}}
\tiny
% ----------------------------------------------------------

\small
\begin{{longtable}}{{p{{4.5cm}}p{{2.0cm}}p{{2.0cm}}p{{3.5cm}}}}
\caption{{L\'imites m\'aximos permisibles de descarga al sistema de alcantarillado p\'ublico (TULSMA, Tabla~11).}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endfirsthead
\multicolumn{{4}}{{c}}{{\small\itshape Continuaci\'on de la Tabla}}\\
\toprule
\textbf{{Par\'ametro}} & \textbf{{Expresado como}} & \textbf{{Unidad}} & \textbf{{L\'imite m\'aximo permisible}} \\
\midrule
\endhead
\bottomrule
\endlastfoot
Aceites y grasas & Sust.\ solubles en hexano & mg/L & $\leq$ 70,0 \\
Aluminio & Al & mg/L & $\leq$ 5,0 \\
Ars\'enico total & As & mg/L & $\leq$ 0,1 \\
Bario & Ba & mg/L & $\leq$ 2,0 \\
Cadmio & Cd & mg/L & $\leq$ 0,02 \\
Cianuro total & CN$^-$ & mg/L & $\leq$ 1,0 \\
Cloruros & Cl$^-$ & mg/L & $\leq$ 1\,000 \\
Cobre & Cu & mg/L & $\leq$ 1,0 \\
Coliformes fecales & NMP & NMP/100 mL & No especificado \\
Compuestos fen\'olicos & Fenol & mg/L & $\leq$ 0,2 \\
Cromo hexavalente & Cr$^{{6+}}$ & mg/L & $\leq$ 0,5 \\
Cromo total & Cr & mg/L & $\leq$ 0,5 \\
\textbf{{DBO$_5$}} & -- & mg/L & $\leq$ 250 \\
\textbf{{DQO}} & -- & mg/L & $\leq$ 500 \\
Fluoruros & F$^-$ & mg/L & $\leq$ 5,0 \\
Hierro total & Fe & mg/L & $\leq$ 25,0 \\
Manganeso total & Mn & mg/L & $\leq$ 10,0 \\
Materia flotante & -- & -- & Ausencia \\
Mercurio total & Hg & mg/L & $\leq$ 0,01 \\
N\'iquel & Ni & mg/L & $\leq$ 2,0 \\
Nitr\'ogeno amoniacal & N-NH$_3$ & mg/L & $\leq$ 30,0 \\
pH & -- & -- & $6,0 - 9,0$ \\
Plata total & Ag & mg/L & $\leq$ 0,5 \\
Plomo total & Pb & mg/L & $\leq$ 0,5 \\
Selenio & Se & mg/L & $\leq$ 0,5 \\
\textbf{{S\'olidos sedimentables}} & -- & mL/L/h & $\leq$ 20 \\
\textbf{{S\'olidos suspendidos totales}} & -- & mg/L & $\leq$ 220 \\
Sulfatos & SO$_4^{{2-}}$ & mg/L & $\leq$ 1\,000 \\
Sulfuros & S$^{{2-}}$ & mg/L & $\leq$ 1,0 \\
Temperatura & -- & $^\circ$C & $\leq$ 40 \\
Tensoactivos & SAAM & mg/L & $\leq$ 2,0 \\
Zinc & Zn & mg/L & $\leq$ 5,0 \\
\end{{longtable}}

\newpage
%============================================================================
% BIBLIOGRAFÍA
%============================================================================
\bibliographystyle{{plain}}
\bibliography{{referencias}}

\end{{document}}
"""
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    
    print(f"[OK] Memoria de calculo generada: {{output_path}}")
    return output_path
