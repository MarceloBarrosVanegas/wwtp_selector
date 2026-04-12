#!/usr/bin/env python3
"""
Generador LaTeX para Filtro Percolador - Copia exacta de generar_latex_A.py lineas 921-1261
Reorganizado en 3 subsections: Dimensionamiento, Verificacion, Resultados
"""

import os
import sys

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GeneradorFiltroPercolador:
    """Generador LaTeX para unidad Filtro Percolador - Copia exacta del original."""
    
    def __init__(self, cfg, datos, ruta_figuras='figuras'):
        self.cfg = cfg
        self.datos = datos
        self.ruta_figuras = ruta_figuras
    
    def generar_completo(self) -> str:
        """Genera todo el contenido LaTeX del filtro percolador en 3 subsections."""
        return "\n\n".join([
            self.generar_descripcion(),
            self.generar_verificacion(),
            self.generar_resultados()
        ])
    
    def generar_esquema_matplotlib(self, output_dir=None):
        """Genera esquema del filtro percolador usando la funcion existente."""
        sys.path.insert(0, _base_dir)
        from ptar_layout_graficador import generar_esquema_filtro_percolador

        if output_dir is None:
            output_dir = os.path.join(_base_dir, 'resultados', 'figuras')

        return generar_esquema_filtro_percolador(self.datos, output_dir)
    
    def generar_descripcion(self) -> str:
        """Genera subsection Dimensionamiento con toda la teoria y calculos."""
        cfg = self.cfg
        fp = self.datos
        
        return rf"""\subsection{{Dimensionamiento}}

El filtro percolador (también denominado trickling filter) constituye la unidad de tratamiento secundario aerobio por biopelícula (attached growth), diseñada específicamente para remover la carga orgánica restante después del tratamiento anaerobio en el UASB. Este reactor biológico opera mediante el paso del agua residual por gravedad a través de un medio poroso, donde se desarrolla una biopelícula aerobia (biofilm) de aproximadamente 0.1--0.2 mm de espesor que adsorbe y oxida la materia orgánica.

El principio de funcionamiento se basa en el contacto intermitente entre el agua residual, la biopelícula y el aire, permitiendo la degradación aerobia de la DBO. El aire circula por convección natural en sentido contrario (o igual, según la temperatura) al flujo del agua, suministrando el oxígeno necesario para mantener la actividad microbiana. Los microorganismos forman una capa adherida al medio denominada biopelícula, mientras que el exceso de biomasa (sloughings) se desprende periódicamente y es recolectado en el sistema de drenaje inferior (underdrain), requiriendo posterior sedimentación secundaria.

El dimensionamiento del filtro percolador se realiza mediante el criterio de carga orgánica volumétrica (COV) según WEF MOP-8 (2010), que es el método estándar para el diseño de filtros con medio plástico. Este enfoque garantiza que el volumen de medio sea suficiente para soportar la carga biológica aplicada sin riesgo de sobrecarga orgánica.

El modelo cinético de Germain (1966) se utiliza como verificación complementaria para estimar la concentración de DBO en el efluente y confirmar que el diseño cumple con el objetivo de calidad del agua tratada. Este modelo describe la remoción de DBO mediante una expresión exponencial relacionada con la profundidad del medio y la tasa hidráulica aplicada.



Según Metcalf \& Eddy (2014), existen tres tipos principales de medio filtrante, con el plástico aleatorio siendo la opción recomendada para plantas post-UASB debido a su menor peso, mayor profundidad posible y mejor aireación:

\begin{{table}}[H]
\centering
\caption{{Comparación de tipos de medio filtrante (Metcalf \& Eddy, 2014)}}
\small
\begin{{tabular}}{{lccc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Roca/Grava}} & \textbf{{Plástico Aleatorio}} & \textbf{{Plástico Estructurado}} \\
\midrule
Superficie específica & 40--70 m²/m³ & 90--150 m²/m³ & 100--200 m²/m³ \\
Índice de vacíos & 40--50 \% & 94--97 \% & 95--99 \% \\
Densidad aparente & 800--1100 kg/m³ & 30--100 kg/m³ & 20--80 kg/m³ \\
Profundidad máxima & 1.5--3.0 m & 6--12 m & 6--15 m \\
Carga orgánica máxima & 0.08--0.32 kg/m³·d & 0.3--3.0 kg/m³·d & 0.5--5.0 kg/m³·d \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Nota importante:}} Para tratamiento carbonáceo (solo DBO, sin nitrificación) con medio plástico, la superficie específica no debe exceder 100 m²/m³ para evitar taponamiento por biopelícula excesiva (WEF, Manual of Practice No. 8).

\textbf{{Parámetros de diseño}}

\begin{{table}}[H]
\centering
\caption{{Parámetros de diseño para filtro percolador}}
\begin{{tabular}}{{lccc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Rango}} & \textbf{{Valor adoptado}} & \textbf{{Fuente}} \\
\midrule
Carga orgánica (kg DBO/m³·d) & {cfg.fp_Cv_minima_kgDBO_m3_d:.1f}--{cfg.fp_Cv_maxima_kgDBO_m3_d:.1f} & {fp['Cv_kgDBO_m3_d']:.2f} & WEF MOP-8 \\
Profundidad medio (m) & {fp['D_medio_min_m']:.1f}--{fp['D_medio_max_m']:.1f} & {fp['D_medio_m']:.2f} & Metcalf \& Eddy \\
Espacio distribuidor--medio (m) & {fp['H_distribucion_min_m']:.2f}--{fp['H_distribucion_max_m']:.2f} & {fp['H_distribucion_m']:.2f} & EPA (2000) \\
Altura underdrain (m) & {fp['H_underdrain_min_m']:.2f}--{fp['H_underdrain_max_m']:.2f} & {fp['H_underdrain_m']:.2f} & Metcalf \& Eddy \\
Bordo libre (m) & {fp['H_bordo_libre_min_m']:.2f}--{fp['H_bordo_libre_max_m']:.2f} & {fp['H_bordo_libre_m']:.2f} & Norma constructiva \\
Recirculación R (-) & {cfg.fp_R_recomendado_min:.1f}--{cfg.fp_R_recomendado_max:.1f} & {fp['R_recirculacion']:.1f} & Metcalf \& Eddy \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Carga Orgánica -- Dimensionamiento}}

Según las recomendaciones para medio plástico aleatorio, las cargas óptimas oscilan entre {cfg.fp_Cv_minima_kgDBO_m3_d:.1f} y {cfg.fp_Cv_maxima_kgDBO_m3_d:.1f} kg DBO/m³·d. Se adopta un valor conservador de {fp['Cv_kgDBO_m3_d']:.2f} kg DBO/m³·d, apropiado para la condición de pretratamiento previo con UASB.

El volumen de medio filtrante requerido se calcula mediante:

\begin{{equation}}
V = \frac{{Q \cdot S_0}}{{C_v}}
\end{{equation}}
\captionequation{{Volumen de medio filtrante - Filtro Percolador}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$V$] = Volumen de medio filtrante requerido (m³)
    \item[$Q$] = Caudal diario ({fp['Q_m3_d']:.1f} m³/d)
    \item[$S_0$] = DBO afluente ({fp['DBO_entrada_mg_L']:.0f} mg/L = {fp['DBO_entrada_mg_L']:.0f} $\times$ 10$^{{-3}}$ kg/m³)
    \item[$C_v$] = Carga orgánica volumétrica ({fp['Cv_kgDBO_m3_d']:.2f} kg DBO/m³·d)
\end{{itemize}}

\begin{{equation}}
V = \frac{{{fp['Q_m3_d']:.1f} \times {fp['DBO_entrada_mg_L']:.0f} \times 10^{{-3}}}}{{{fp['Cv_kgDBO_m3_d']:.2f}}} = {fp['V_medio_m3']:.1f} \text{{ m}}^3
\end{{equation}}

Con una profundidad de medio de {fp['D_medio_m']:.2f} m, el área superficial resulta {fp['A_sup_m2']:.2f} m², correspondiendo a un diámetro de {fp['D_filtro_m']:.2f} m para configuración circular. La altura total incluye zonas de distribución ({fp['H_distribucion_m']:.2f} m), recolección ({fp['H_underdrain_m']:.2f} m) y bordo libre ({fp['H_bordo_libre_m']:.2f} m), resultando en {fp['H_total_m']:.2f} m.

El sistema incorpora recirculación con relación $R = {fp['R_recirculacion']:.1f}$, lo cual mejora la distribución hidráulica y mantiene la biopelícula húmeda. La tasa hidráulica aplicada resulta {fp['Q_A_real_m3_m2_h']:.3f} m³/m²·h.

\textbf{{Recirculación -- Dimensionamiento}}

La recirculación en filtros percoladores cumple funciones fundamentales según Metcalf \& Eddy \cite{{metcalf2014}}. En primer lugar, garantiza que la biopelícula permanezca húmeda durante periodos de bajo caudal, evitando su deterioro por desecación. Adicionalmente, aumenta la tasa hidráulica superficial, promoviendo una distribución más uniforme del afluente sobre el medio filtrante. Finalmente, reduce la concentración de DBO del afluente por efecto de dilución, disminuyendo el riesgo de sobrecarga orgánica y la generación de olores.

Según Metcalf \& Eddy (2014), las relaciones de recirculación típicas para filtros percoladores con medio plástico varían entre $R = {cfg.fp_R_recomendado_min:.1f}$ y $R = {cfg.fp_R_recomendado_max:.1f}$, dependiendo de la variabilidad del caudal y la calidad del agua residual. Para este diseño se adopta $R = {fp['R_recirculacion']:.1f}$.

El caudal total que llega al filtro incluye el afluente más el recirculado:

\begin{{equation}}
Q_{{total}} = Q_{{medio}} \times (1 + R) = {fp['Q_m3_d']:.1f} \times {1+fp['R_recirculacion']:.1f} = {fp['Q_ap_m3_h']*24:.1f} \text{{ m}}^3\text{{/d}}
\end{{equation}}

Este caudal se distribuye uniformemente mediante el sistema de distribución rotatorio. El número de brazos del distribuidor se selecciona en función del diámetro del filtro, adoptándose {fp['num_brazos']:.0f} brazos para esta configuración, lo que resulta en un caudal por brazo de:

\begin{{equation}}
Q_{{brazo}} = \frac{{Q_{{total}}}}{{N_{{brazos}}}} = \frac{{{fp['Q_ap_m3_h']:.1f}}}{{{fp['num_brazos']:.0f}}} = {fp['Q_por_brazo_m3_h']:.1f} \text{{ m}}^3\text{{/h}}
\end{{equation}}

\textbf{{Distribuidor Rotatorio -- Dimensionamiento}}

El distribuidor rotatorio es el componente encargado de aplicar el agua residual uniformemente sobre la superficie del medio filtrante. Consiste en una columna central hueca (pivot) por donde ingresa el caudal, con brazos radiales que giran por acción de la fuerza de reacción del agua al salir por las boquillas.

\textbf{{Número de brazos:}} Según Metcalf \& Eddy (2014) y criterios constructivos, el número de brazos del distribuidor rotatorio se selecciona en función del diámetro del filtro de la siguiente manera: para diámetros menores a 6 m se utilizan 2 brazos; para diámetros entre 6 m y 15 m se pueden utilizar 2 o 4 brazos; y para diámetros mayores a 15 m se requieren 4 brazos. Para este diseño con diámetro de {fp['D_filtro_m']:.2f} m, se adoptan \textbf{{{fp['num_brazos']:.0f} brazos}}.

\textbf{{Longitud de cada brazo:}}

\begin{{equation}}
L_{{brazo}} = \frac{{D_{{filtro}}}}{{2}} = \frac{{{fp['D_filtro_m']:.2f}}}{{2}} = {fp['L_brazo_m']:.2f} \text{{ m}}
\end{{equation}}

\textbf{{Caudal por brazo:}}

\begin{{equation}}
Q_{{brazo}} = \frac{{Q_{{total}}}}{{N_{{brazos}}}} = \frac{{{fp['Q_ap_m3_h']:.1f}}}{{{fp['num_brazos']:.0f}}} = {fp['Q_por_brazo_m3_h']:.1f} \text{{ m}}^3\text{{/h}}
\end{{equation}}

\textbf{{Sistema de boquillas:}} El número de boquillas por brazo se selecciona para garantizar distribución uniforme. Se adoptan {fp['num_boquillas_por_brazo']:.0f} boquillas por brazo.

Caudal por boquilla:
\begin{{equation}}
q_{{boquilla}} = \frac{{Q_{{brazo}}}}{{N_{{boquillas}}}} = \frac{{{fp['Q_por_brazo_m3_h']:.1f}}}{{{fp['num_boquillas_por_brazo']:.0f}}} = {fp['Q_por_boquilla_L_s']:.2f} \text{{ L/s}} = {fp['Q_por_boquilla_L_s']*3.6:.2f} \text{{ m}}^3\text{{/h}}
\end{{equation}}

Velocidad de salida en boquillas (rango recomendado {cfg.fp_velocidad_boquilla_min_m_s:.1f}--{cfg.fp_velocidad_boquilla_max_m_s:.1f} m/s según Metcalf \& Eddy):

\begin{{equation}}
v_{{boquilla}} = \frac{{q_{{boquilla}}}}{{A_{{orificio}}}} = {fp['v_boquilla_m_s']:.2f} \text{{ m/s}}
\end{{equation}}

Diámetro de orificio calculado:
\begin{{equation}}
d_{{orificio}} = \sqrt{{\frac{{4 \times q_{{boquilla}}}}{{\pi \times v_{{boquilla}}}}}} = {fp['diam_orificio_mm']:.1f} \text{{ mm}}
\end{{equation}}

\textbf{{Altura sobre el medio:}} La altura libre entre el fondo del brazo y la superficie del medio debe estar entre {fp['H_distribucion_min_m']:.2f}--{fp['H_distribucion_max_m']:.2f} m según EPA (2000), para permitir que el agua se distribuya en forma de abanico antes de caer sobre el medio.

\textbf{{Drenaje Inferior -- Dimensionamiento}}

El sistema de drenaje inferior tiene la función dual de recolectar el efluente tratado que percola a través del medio filtrante y de servir como conducto para el aire de ventilación natural. El diseño se basa en la configuración de canal central colector con pendiente hacia el punto de descarga.

Según Metcalf \& Eddy (2014), la altura del sistema de drenaje debe oscilar entre {fp['H_underdrain_min_m']:.2f} m y {fp['H_underdrain_max_m']:.2f} m para garantizar el almacenamiento temporal de efluente y permitir la entrada de aire. Para este diseño se adopta una altura de {fp['H_underdrain_m']:.2f} m.

El caudal de diseño del canal central se determina aplicando un factor de capacidad de seguridad, dimensionando el canal para conducir el doble del caudal aplicado al filtro. Esto garantiza que incluso en condiciones de pico o con acumulación parcial de sólidos, el sistema evacue el agua sin riesgo de inundación del medio filtrante. El caudal de diseño resulta:

\begin{{equation}}
Q_{{\text{{diseno}}}} = \frac{{Q_{{aplicado}}}}{{{cfg.fp_factor_capacidad_underdrain:.2f}}} = \frac{{{fp['Q_ap_m3_h']:.1f}}}{{{cfg.fp_factor_capacidad_underdrain:.2f}}} = {fp['Q_underdrain_diseno_m3_h']:.1f} \text{{ m}}^3\text{{/h}}
\end{{equation}}

El canal central se dimensiona con una sección rectangular de {fp['ancho_canal_central_m']:.2f} m de ancho por {fp['altura_canal_central_m']:.2f} m de alto, con una pendiente mínima del {fp['pendiente_underdrain_pct']:.1f} hacia la descarga. La capacidad hidráulica se verifica mediante la ecuación de Manning para flujo a superficie libre:

\begin{{equation}}
Q = \frac{{1}}{{n}} \cdot A \cdot R^{{2/3}} \cdot S^{{1/2}}
\end{{equation}}

Donde $n = {cfg.fp_n_manning_underdrain:.3f}$ es el coeficiente de rugosidad de Manning para concreto, $A$ es el área transversal del canal, $R$ es el radio hidráulico y $S$ es la pendiente. Sustituyendo valores:

\begin{{equation}}
Q_{{canal}} = {fp['Q_canal_capacidad_m3_h']:.1f} \text{{ m}}^3\text{{/h}}
\end{{equation}}

La relación entre el caudal aplicado y la capacidad del canal determina el porcentaje de llenado:

\begin{{equation}}
\text{{Llenado}} = \frac{{Q_{{aplicado}}}}{{Q_{{canal}}}} \times 100 = {fp['llenado_canal_pct']:.1f}\\%
\end{{equation}}

{fp['texto_underdrain']}

\textbf{{Ventilación Natural -- Dimensionamiento}}

La ventilación natural del filtro percolador es un componente crítico para mantener el proceso aerobio de la biopelícula. El aire circula por convección natural desde las aberturas inferiores (ubicadas en el drenaje) hacia la superficie del medio, suministrando el oxígeno necesario para la degradación aerobia de la materia orgánica. Según Metcalf \& Eddy (2014) y WEF MOP-8, el diseño debe garantizar un área de ventilación mínima equivalente al {cfg.fp_area_ventilacion_pct:.1f} por ciento del área superficial del filtro.

El área de ventilación requerida se calcula como:

\begin{{equation}}
A_{{vent}} = A_{{sup}} \times \frac{{{cfg.fp_area_ventilacion_pct:.1f}}}{{100}} = {fp['A_sup_m2']:.2f} \times {cfg.fp_area_ventilacion_pct/100:.3f} = {fp['area_ventilacion_requerida_m2']:.4f} \text{{ m}}^2
\end{{equation}}

Donde $A_{{sup}}$ es el área superficial del filtro y {cfg.fp_area_ventilacion_pct:.1f} por ciento es el porcentaje mínimo requerido según criterios de diseño.

Las aperturas de ventilación se dimensionan con una sección de {cfg.fp_apertura_ventilacion_ancho_m:.2f} m de ancho por {cfg.fp_apertura_ventilacion_alto_m:.2f} m de alto, resultando en un área por apertura de {cfg.fp_apertura_ventilacion_ancho_m * cfg.fp_apertura_ventilacion_alto_m:.2f} m². El número mínimo de aperturas necesarias se determina dividiendo el área de ventilación requerida entre el área de una apertura:

\begin{{equation}}
N_{{aperturas}} = \lceil\frac{{A_{{vent}}}}{{A_{{apertura}}}}\rceil = \lceil\frac{{{fp['area_ventilacion_requerida_m2']:.4f}}}{{{cfg.fp_apertura_ventilacion_ancho_m * cfg.fp_apertura_ventilacion_alto_m:.4f}}}\rceil = \lceil{fp['area_ventilacion_requerida_m2'] / (cfg.fp_apertura_ventilacion_ancho_m * cfg.fp_apertura_ventilacion_alto_m):.4f}\rceil = {fp['num_aperturas_ventilacion']:.0f}
\end{{equation}}

Las aperturas se distribuyen uniformemente alrededor del perímetro del filtro, resultando en un espaciado entre centros de:

\begin{{equation}}
espaciado = \frac{{\pi \times D_{{filtro}}}}{{N_{{aperturas}}}} = \frac{{\pi \times {fp['D_filtro_m']:.2f}}}{{{fp['num_aperturas_ventilacion']:.0f}}} = {fp['espaciado_aperturas_m']:.2f} \text{{ m}}
\end{{equation}}

El caudal de aire necesario para mantener las condiciones aerobias se estima mediante factores de relación con el caudal de agua. Según criterios de diseño, el caudal mínimo de aire debe ser {cfg.fp_Q_aire_min_factor:.1f} veces el caudal de agua, resultando en {fp['Q_aire_min_m3_h']:.1f} m³/h, mientras que el valor óptimo recomendado es {cfg.fp_Q_aire_factor:.1f} veces el caudal de agua, equivalente a {fp['Q_aire_opt_m3_h']:.1f} m³/h. Esta ventilación natural, impulsada por la diferencia de temperatura entre el aire ambiente y el interior del filtro, es suficiente para mantener la biopelícula aerobia sin requerir ventilación forzada."""

    def generar_verificacion(self) -> str:
        """Genera subsection Verificacion con todas las verificaciones."""
        cfg = self.cfg
        fp = self.datos
        
        return rf"""\subsection{{Verificación}}

\textbf{{Verificación de Carga Orgánica y Modelo de Germain}}

Se verifica el comportamiento hidráulico para el caudal máximo horario, aplicando un factor de pico típico de {fp['factor_pico']:.1f} sobre el caudal medio:

\begin{{equation}}
Q_{{max}} = {fp['factor_pico']:.1f} \times Q_{{medio}} = {fp['factor_pico']:.1f} \times {fp['Q_m3_d']:.1f} = {fp['Q_max_m3_d']:.1f} \text{{ m}}^3\text{{/d}}
\end{{equation}}

A caudal máximo, la tasa hidráulica resulta:

\begin{{equation}}
q_{{A,max}} = \frac{{Q_{{max}} \cdot (1 + R)}}{{A_s \cdot 24}} = \frac{{{fp['Q_max_m3_d']:.1f} \times {1+fp['R_recirculacion']:.1f}}}{{{fp['A_sup_m2']:.2f} \times 24}} = {fp['Q_A_max_m3_m2_h']:.2f} \text{{ m}}^3\text{{/m}}^2\text{{·h}}
\end{{equation}}

El valor obtenido se compara con el límite máximo recomendado de {fp['Q_A_limite_m3_m2_h']:.1f} m³/m²·h. {fp['verif_qmax_texto']}.

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

\textbf{{Verificación de cumplimiento del objetivo:}} {fp['texto_germain']}

\textbf{{Verificación de Recirculación}}

La verificación de la recirculación se centra en garantizar el caudal mínimo necesario para mantener la biopelícula húmeda durante condiciones de bajo flujo. Según Metcalf \& Eddy \cite{{metcalf2014}}, la tasa hidráulica superficial mínima recomendada es de $q_{{A,min}} \geq {cfg.fp_qA_min_humectacion_m3_m2_h:.1f}$ m³/m²·h para evitar la desecación del medio y garantizar el riego adecuado sobre la biopelícula.

Se evalúa la condición de caudal mínimo, correspondiente típicamente al {int(cfg.fp_factor_caudal_min_nocturno*100)}\% del caudal medio (operación nocturna):

\begin{{equation}}
q_{{A,min}} = \frac{{Q_{{min}} \times (1 + R)}}{{A_s}} = \frac{{{fp['Q_m3_d']:.1f} \times {cfg.fp_factor_caudal_min_nocturno:.2f} \times {1+fp['R_recirculacion']:.1f}}}{{{fp['A_sup_m2']:.2f} \times 24}} = {fp['qA_min_m3_m2_h']:.2f} \text{{ m}}^3\text{{/m}}^2\text{{·h}}
\end{{equation}}

{fp['qA_min_texto']}

Según Metcalf \& Eddy (2014, p. 843), valores de $q_{{A,min}}$ inferiores a {cfg.fp_qA_min_humectacion_m3_m2_h:.1f} m³/m²·h requieren considerar aumentar la recirculación o implementar sistemas de control de nivel para mantener la biopelícula activa.

\textbf{{Verificación del Distribuidor Rotatorio}}

La verificación del distribuidor rotatorio se centra en garantizar que el sistema pueda operar sin intervención mecánica externa durante las condiciones normales de funcionamiento. Para que el distribuidor gire por fuerza hidráulica sin necesidad de motor eléctrico auxiliar, el caudal por brazo debe ser suficiente para generar el par de reacción necesario mediante la fuerza de salida del agua por las boquillas.

Según Metcalf \& Eddy (2014), se establece como regla práctica que si el caudal por brazo es mayor o igual a {cfg.fp_Q_por_brazo_min_rotacion_m3_h:.1f} m³/h, la rotación hidráulica automática está garantizada. Por el contrario, si el caudal por brazo es inferior a este umbral, se requiere instalar un motor eléctrico auxiliar para asegurar la rotación continua del distribuidor.

En este diseño, el caudal por brazo calculado es:

\begin{{equation}}
Q_{{brazo}} = {fp['Q_por_brazo_m3_h']:.1f} \text{{ m}}^3\text{{/h}}
\end{{equation}}

{fp['texto_rotacion']}

Respecto a la velocidad de rotación, la literatura técnica establece que la velocidad típica debe encontrarse entre {cfg.fp_rotacion_rpm_min:.1f} y {cfg.fp_rotacion_rpm_max:.1f} rpm (revoluciones por minuto), lo que corresponde a una velocidad periférica en el extremo del brazo de {cfg.fp_vel_periferica_min_m_min:.1f} a {cfg.fp_vel_periferica_max_m_min:.1f} m/min. Esta velocidad garantiza una distribución uniforme del agua sobre toda la superficie del medio sin generar salpicaduras excesivas o zonas sin riego.

Finalmente, se verifica que la velocidad de salida en las boquillas se encuentre dentro del rango recomendado de {cfg.fp_velocidad_boquilla_min_m_s:.1f} a {cfg.fp_velocidad_boquilla_max_m_s:.1f} m/s, necesario para generar suficiente par de reacción. La velocidad calculada de {fp['v_boquilla_m_s']:.2f} m/s {fp['texto_boquillas']}.

\textbf{{Verificación del Drenaje Inferior}}

La verificación del sistema de drenaje inferior se centra en garantizar que el canal central operará con flujo a superficie libre bajo todas las condiciones de operación, permitiendo simultáneamente el paso del efluente y el aire de ventilación natural. Según Metcalf \& Eddy (2014) y WEF MOP-8, el diseño debe cumplir con dos criterios fundamentales: el llenado máximo del canal no debe exceder el {cfg.fp_llenado_max_underdrain*100:.0f} por ciento de su capacidad, y la pendiente debe ser suficiente para mantener velocidades de auto-limpieza que eviten la sedimentación de sólidos.

El criterio de llenado máximo establece que el canal debe operar como máximo a la mitad de su capacidad hidráulica. Esta condición garantiza que la sección superior del canal permanezca disponible para el flujo de aire ascendente desde las aberturas de ventilación hacia el medio filtrante, proceso esencial para mantener el suministro de oxígeno a la biopelícula aerobia. La verificación compara el caudal aplicado contra la capacidad del canal:

\begin{{equation}}
\text{{Llenado}}_{{max}} = \frac{{Q_{{aplicado}}}}{{Q_{{canal}}}} \times 100 = {fp['llenado_canal_pct']:.1f} \% \leq {cfg.fp_llenado_max_underdrain*100:.0f} \%
\end{{equation}}

{fp['texto_underdrain']}

Respecto a la pendiente, el diseño adopta un valor del {fp['pendiente_underdrain_pct']:.1f} por ciento, que cumple con el mínimo requerido de {cfg.fp_pendiente_underdrain_pct:.1f} por ciento establecido por Metcalf \& Eddy (2014) para garantizar el auto-limpiezo del canal y prevenir la sedimentación de sólidos provenientes del filtro.

\textbf{{Verificación de Especificación del Medio}}

La verificación mecánica del medio filtrante plástico asegura que el material seleccionado puede soportar las cargas aplicadas durante la operación del filtro percolador sin sufrir deformaciones permanentes o colapso estructural. Según las especificaciones técnicas de fabricantes y los criterios de WEF MOP-8, el medio plástico aleatorio debe resistir una carga compresiva que incluye el peso propio del medio saturado de agua, el peso de la biopelícula que se desarrolla sobre su superficie, y el peso del agua que circula temporalmente durante la operación.

La carga total sobre el medio se calcula considerando la densidad aparente del medio plástico ({fp['densidad_media_kg_m3']:.0f} kg/m³), la carga de agua sobre el medio ({cfg.fp_carga_agua_sobre_medio_kg_m3:.0f} kg/m³), y la carga de biopelícula ({cfg.fp_carga_biopelicula_sobre_medio_kg_m3:.0f} kg/m³), multiplicadas por la profundidad del medio filtrante:

\begin{{equation}}
C_{{total}} = (\rho_{{medio}} + C_{{agua}} + C_{{biopelicula}}) \times D = {fp['carga_sobre_medio_kg_m2']:.1f} \text{{ kg/m}}^2
\end{{equation}}

El criterio de resistencia a compresión establece límites diferentes según la profundidad del medio. Para profundidades hasta {cfg.fp_resistencia_umbral_profundidad_m:.1f} m, la resistencia mínima requerida es de {cfg.fp_resistencia_min_baja_kg_m2:.0f} kg/m², mientras que para profundidades mayores la resistencia debe ser al menos de {cfg.fp_resistencia_min_alta_kg_m2:.0f} kg/m². Esta diferenciación considera que a mayor profundidad, el peso del medio sobre las capas inferiores incrementa la carga compresiva.

{fp['texto_resistencia']}

Adicionalmente, el medio debe cumplir con las siguientes especificaciones técnicas: superficie específica de {fp['sup_especifica_medio_m2_m3']:.0f} m²/m³ que proporciona área suficiente para el crecimiento de la biopelícula, índice de vacíos del {fp['vacios_medio_pct']:.0f} por ciento que garantiza la permeabilidad del medio para el flujo de agua y aire, y densidad aparente de {fp['densidad_media_kg_m3']:.0f} kg/m³ que asegura la flotabilidad negativa necesaria para mantener el medio en posición durante la operación."""

    def generar_resultados(self) -> str:
        """Genera subsection Resultados con tabla y figura."""
        cfg = self.cfg
        fp = self.datos
        
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
\includegraphics[width=\textwidth]{{{fig_relativa}}}
\caption{{Esquema del filtro percolador: sistema de distribución rotatorio con {fp['num_brazos']:.0f} brazos, medio filtrante de {fp['D_medio_m']:.2f} m de profundidad, y underdrain para recolección de efluente y aireación.}}
\label{{fig:filtro_percolador}}
\end{{figure}}\

El esquema ilustra la aplicación del afluente mediante el distribuidor rotatorio, el
flujo descendente a través del medio plástico con biopelícula aerobia, la recolección
del efluente en el drenaje inferior y la ventilación natural requerida para mantener
condiciones aerobias dentro del filtro.
"""
        else:
            figura_latex = ""
        
        return rf"""\subsection{{Resultados}}

\begingroup
\small
\begin{{longtable}}{{ll}}
\caption{{Resumen de resultados del filtro percolador}}\\
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} \\
\midrule
\endfirsthead
\caption[]{{Resumen de resultados del filtro percolador (continuación)}}\\
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} \\
\midrule
\endhead
\midrule
\multicolumn{{2}}{{r}}{{\textit{{Continúa en la siguiente página}}}} \\
\endfoot
\bottomrule
\endlastfoot
\multicolumn{{2}}{{l}}{{\textit{{Geometría principal}}}} \\
Diámetro & {fp['D_filtro_m']:.2f} m \\
Altura total & {fp['H_total_m']:.2f} m \\
Profundidad medio & {fp['D_medio_m']:.2f} m \\
Volumen de medio & {fp['V_medio_m3']:.1f} m³ \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Cargas y recirculación}}}} \\
Carga orgánica & {fp['Cv_kgDBO_m3_d']:.2f} kg DBO/m³·d \\
Recirculación & R = {fp['R_recirculacion']:.1f} \\
Tasa hidráulica aplicada & {fp['Q_A_real_m3_m2_h']:.2f} m³/m²·h \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Distribuidor rotatorio}}}} \\
Número de brazos & {fp['num_brazos']:.0f} \\
Caudal por brazo & {fp['Q_por_brazo_m3_h']:.1f} m³/h \\
Diámetro de orificio & {fp['diam_orificio_mm']:.1f} mm \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Drenaje inferior (underdrain)}}}} \\
Caudal de diseño & {fp['Q_underdrain_diseno_m3_h']:.1f} m³/h \\
Capacidad del canal & {fp['Q_canal_capacidad_m3_h']:.1f} m³/h \\
Llenado del canal & {fp['llenado_canal_pct']:.1f} \\% \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Ventilación natural}}}} \\
Área de ventilación requerida & {fp['area_ventilacion_requerida_m2']:.2f} m² \\
Número de aperturas & {fp['num_aperturas_ventilacion']:.0f} \\
Espaciado entre aperturas & {fp['espaciado_aperturas_m']:.2f} m \\
Caudal de aire (mínimo) & {fp['Q_aire_min_m3_h']:.1f} m³/h \\
Caudal de aire (óptimo) & {fp['Q_aire_opt_m3_h']:.1f} m³/h \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Verificación mecánica del medio}}}} \\
Carga sobre el medio & {fp['carga_sobre_medio_kg_m2']:.1f} kg/m² \\
Resistencia a compresión & {fp['estado_resistencia']} \\
\end{{longtable}}
\endgroup\



{figura_latex}"""


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_dir)
    
    from ptar_dimensionamiento import ConfigDiseno, dimensionar_filtro_percolador
    import subprocess
    
    print("=" * 60)
    print("TEST - GENERADOR MODULAR DE FILTRO PERCOLADOR")
    print("=" * 60)
    
    cfg = ConfigDiseno()
    print(f"\n[1] Q_linea = {cfg.Q_linea_L_s} L/s")
    
    # Para el filtro percolador necesitamos DBO de entrada (salida del UASB)
    from ptar_dimensionamiento import dimensionar_uasb
    uasb = dimensionar_uasb(cfg)
    DBO_entrada_fp = cfg.DBO5_mg_L * (1 - uasb['eta_DBO'])
    
    datos = dimensionar_filtro_percolador(cfg, DBO_entrada_mg_L=DBO_entrada_fp)
    print(f"[2] Dimensiones: D={datos['D_filtro_m']:.2f}m, H={datos['H_total_m']:.2f}m, V={datos['V_medio_m3']:.1f}m³")
    
    resultados_dir = os.path.join(base_dir, 'resultados', 'test_modular')
    figuras_dir = os.path.join(resultados_dir, 'figuras')
    os.makedirs(figuras_dir, exist_ok=True)
    
    gen = GeneradorFiltroPercolador(cfg, datos, ruta_figuras=figuras_dir)
    latex = gen.generar_completo()
    print(f"[3] LaTeX generado: {len(latex)} chars")
    
    tex_path = os.path.join(resultados_dir, 'filtro_percolador_test.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    
    doc_path = os.path.join(resultados_dir, 'filtro_percolador_test_completo.tex')
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{graphicx}
\usepackage{enumitem}
\usepackage{tikz}
\usepackage{float}
\usepackage{xcolor}
\usepackage{hyperref}

\geometry{margin=2.5cm}

\newcommand{\captionequation}[1]{}  % Simplificado para test

\begin{document}

\section{Filtro Percolador}

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
        pdf_path = os.path.join(resultados_dir, 'filtro_percolador_test_completo.pdf')
        if os.path.exists(pdf_path):
            print(f"    PDF generado: {pdf_path}")
    except Exception as e:
        print(f"    ERROR: {e}")
    
    print("=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
