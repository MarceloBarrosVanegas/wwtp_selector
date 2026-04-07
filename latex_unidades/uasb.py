#!/usr/bin/env python3
"""
Generador LaTeX para Reactor UASB - Copia exacta de generar_latex_A.py lineas 551-920
Reorganizado en 3 subsections: Dimensionamiento, Verificacion, Resultados
"""

import os
import sys

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GeneradorUASB:
    """Generador LaTeX para unidad Reactor UASB - Copia exacta del original."""
    
    def __init__(self, cfg, datos, ruta_figuras='resultados'):
        self.cfg = cfg
        self.datos = datos
        self.ruta_figuras = ruta_figuras
    
    def generar_completo(self) -> str:
        """Genera todo el contenido LaTeX del UASB en 3 subsections."""
        return "\n\n".join([
            self.generar_descripcion(),
            self.generar_verificacion(),
            self.generar_resultados()
        ])
    
    def generar_descripcion(self) -> str:
        """Genera subsection Dimensionamiento con toda la teoria y calculos."""
        cfg = self.cfg
        u = self.datos
        
        # Texto de recomendacion de temperatura
        temp_recomendacion = u['texto_recomendacion_temp']
        
        return rf"""\subsection{{Dimensionamiento}}

El reactor UASB (Upflow Anaerobic Sludge Blanket), desarrollado por Lettinga y colaboradores en 1980 en la Universidad de Wageningen de los Países Bajos \cite{{vanhaandel1994}}, es uno de los sistemas de tratamiento anaerobio de alta tasa más utilizados en el mundo para aguas residuales municipales y agroindustriales. El agua residual entra por la parte inferior y fluye en sentido ascendente a través de un manto denso de lodo anaerobio, donde los microorganismos anaerobios degradan la materia orgánica mediante metanogénesis, convirtiéndola en biogás (metano y CO$_2$) y biomasa. El proceso ocurre sin oxígeno molecular, por lo que no requiere aireación, reduciendo drásticamente el consumo energético (5--10 veces menos que un sistema aerobio convencional).

El diseño se fundamenta en criterios biológicos e hidráulicos establecidos por Van Haandel y Lettinga \cite{{vanhaandel1994}}, Sperling \cite{{sperling2007}} y Metcalf y Eddy \cite{{metcalf2014}}.

\textbf{{Condiciones de temperatura:}} La temperatura del agua residual es un factor crítico que determina los parámetros de diseño del reactor UASB. Según Van Haandel y Lettinga (1994), el proceso de metanogénesis requiere temperaturas superiores a {cfg.uasb_temp_optimina_C:.0f}°C para operar de manera óptima. A temperaturas menores, la actividad metabólica de los microorganismos anaerobios disminuye, requiriendo ajustes en la carga orgánica, el tiempo de retención y la velocidad ascendente.

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
Moderada & {cfg.uasb_temp_moderada_min_C:.0f}--{cfg.uasb_temp_optimina_C:.0f} & {cfg.uasb_Cv_moderado_min:.1f}--{cfg.uasb_Cv_moderado_max:.1f} & {cfg.uasb_HRT_moderado_min_h:.0f}--{cfg.uasb_HRT_moderado_max_h:.0f} \\
Baja & {cfg.uasb_temp_min_operativa_C:.0f}--{cfg.uasb_temp_moderada_min_C:.0f} & {cfg.uasb_Cv_bajo_min:.1f}--{cfg.uasb_Cv_bajo_max:.1f} & {cfg.uasb_HRT_bajo_min_h:.0f}--{cfg.uasb_HRT_bajo_max_h:.0f} \\
Muy baja & {cfg.uasb_temp_muy_baja_min_C:.0f}--{cfg.uasb_temp_min_operativa_C:.0f} & {cfg.uasb_Cv_muybajo_min:.1f}--{cfg.uasb_Cv_muybajo_max:.1f} & {cfg.uasb_HRT_muybajo_min_h:.0f}--{cfg.uasb_HRT_muybajo_max_h:.0f} \\
Crítica & $<$ {cfg.uasb_temp_muy_baja_min_C:.0f} & No recomendable & Requiere calefacción \\
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

\textbf{{Zona de Reacción -- Dimensionamiento}}

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
V_{{biol}} = \frac{{{u['Q_m3_d']:.1f} \times {u['DQO_kg_m3']:.4f}}}{{{u['Cv_kgDQO_m3_d']:.1f}}} = {u['V_r_biol_m3']:.1f} \text{{ m}}^3
\end{{equation}}

Este volumen biológico teórico de {u['V_r_biol_m3']:.1f} m³ garantizaría el tiempo de retención hidráulico necesario para que los microorganismos anaerobios degraden la materia orgánica según Van Haandel y Lettinga. Sin embargo, el criterio hidráulico (velocidad ascendente) requiere un área superficial mayor para evitar el arrastre del manto de lodos, lo que resulta en un volumen final adoptado de \textbf{{{u['V_r_m3']:.1f} m³}}. Este ajuste incrementa el TRH respecto al mínimo teórico, proporcionando un margen de seguridad adicional en la operación del reactor.

\textbf{{Criterio hidráulico:}} De manera simultánea, según Sperling \cite{{sperling2007}}, la velocidad ascendente ($v_{{up}}$) debe mantenerse dentro de rangos que permitan retener el manto de lodos sin arrastre. El autor recomienda velocidades entre {cfg.uasb_v_up_min_m_h:.1f} y {cfg.uasb_v_up_max_recomendado_m_h:.1f} m/h para condiciones normales, con un máximo de {cfg.uasb_v_up_max_destructivo_m_h:.1f} m/h durante picos de caudal. Con la velocidad adoptada de {u['v_up_m_h']:.2f} m/h, el área superficial requerida se calcula como:

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

La altura de la zona de reacción (manto de lodos) resulta {u['H_r_m']:.2f}~m, proporcionando un tiempo de retención hidráulico de {u['TRH_h']:.1f} horas para la temperatura de {u['T_agua_C']:.1f}°C del agua residual. La evaluación de adecuación hidráulica se presenta en la sección de verificación.

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

\textbf{{Cámara de Sedimentación -- Dimensionamiento}}

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

\textbf{{Aberturas GLS -- Dimensionamiento}}

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

Adicionalmente, el GLS debe construirse con pendientes de {cfg.uasb_GLS_pendiente_min_grados:.0f}° a {cfg.uasb_GLS_pendiente_max_grados:.0f}° (adoptado {u['GLS_pendiente_adoptada_grados']:.0f}°) y un traslape de {cfg.uasb_GLS_traslape_m:.2f} m sobre las aberturas para garantizar la retención de sólidos.

\textbf{{Distribución del Afluente -- Dimensionamiento}}

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
\end{{equation}}"""

    def generar_verificacion(self) -> str:
        """Genera subsection Verificacion con todas las verificaciones."""
        cfg = self.cfg
        u = self.datos

        return rf"""\subsection{{Verificación}}

\textbf{{Verificación de Velocidad Ascendente a Caudal Máximo}}

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

Para el presente diseño, con una velocidad ascendente máxima calculada de $v_{{up,max}} = {u['v_up_max_m_h']:.2f}$~m/h, el reactor se clasifica en estado \textbf{{{u['estado_verificacion']}}}. Este resultado indica que el dimensionamiento propuesto {u['estado_verificacion_texto']}

\textbf{{Verificación de la Cámara de Sedimentación}}

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
    \item \textbf{{SOR máximo}}: {u['SOR_max_texto']}. Este límite representa la velocidad de asentamiento mínima de los agregados de lodos anaerobios. Superar este valor implica que el flujo ascendente supera la velocidad de caída de los sólidos, causando su arrastre hacia el efluente.
    
    \item \textbf{{SOR medio}}: {u['SOR_medio_texto']}. Según Chernicharo, este rango permite evaluar la eficiencia de separación sólido-líquido y el margen operativo de la cámara de sedimentación.
    
    \item \textbf{{TRH en sedimentador}}: {u['TRH_sed_texto']}
\end{{itemize}}

\begin{{table}}[H]
\centering
\caption{{Verificación de criterios de diseño de la cámara de sedimentación según Chernicharo (2007)}}
\begin{{tabular}}{{lccc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Valor calculado}} & \textbf{{Criterio}} & \textbf{{Estado}} \\
\midrule
SOR máximo & {u['SOR_max_m_h']:.2f} m/h & $<$ {cfg.uasb_SOR_max_limite_m_h:.1f} m/h & {u['estado_SOR_max']} \\
SOR medio & {u['SOR_medio_m_h']:.2f} m/h & {cfg.uasb_SOR_medio_min_m_h:.1f}--{cfg.uasb_SOR_medio_max_m_h:.1f} m/h & {u['estado_SOR_medio']} \\
TRH sedimentador & {u['TRH_sed_medio_h']:.2f} h & $\geq$ {cfg.uasb_TRH_sed_medio_min_h:.1f} h & {u['estado_TRH_sed']} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Nota sobre márgenes operativos:}} {u['nota_margenes_operativos']}

{u['verif_sed_final']}

\textbf{{Verificación de Aberturas GLS}}

Verificando para caudal máximo ($Q_{{max}} = {u['Q_max_m3_h']:.2f}$ m³/h):

\begin{{equation}}
v_{{ab,max}} = \frac{{Q_{{max}}}}{{A_{{ab}}}} = \frac{{{u['Q_max_m3_h']:.2f}}}{{{u['A_aberturas_min_m2']:.2f}}} = {u['v_abertura_max_calculada_m_h']:.2f} \text{{ m/h}} \quad {u['simbolo_abertura_max']} {cfg.uasb_v_abertura_max_m_h:.1f} \text{{ m/h }} \text{{({u['estado_aberturas']})}}
\end{{equation}}

{u['verif_aberturas_gls_texto']}

\textbf{{Verificación del Sistema de Distribución}}

\begin{{table}}[H]
\centering
\caption{{Verificación de velocidades en sistema de distribución}}
\begin{{tabular}}{{lccc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} & \textbf{{Criterio}} & \textbf{{Estado}} \\
\midrule
Velocidad en tubería principal& {u['velocidad_tubo_m_s']:.3f} m/s & Transporte sin obstrucción ($<$ {u['v_tubo_max_m_s']:.2f} m/s) & {u['estado_tubo']} \\
Velocidad en boca de salida & {u['velocidad_boca_m_s']:.2f} m/s & {u['v_boca_min_m_s']:.1f}--{u['v_boca_max_m_s']:.1f} m/s & {u['estado_boca']} \\
\bottomrule
\end{{tabular}}
\end{{table}}

La velocidad en boca de {u['velocidad_boca_m_s']:.2f} m/s {u['texto_boca']}"""

# Función original generar_esquema_uasb adaptada como método
    def generar_esquema_matplotlib(self, output_dir=None):
        """
        Genera un esquema técnico del reactor UASB con proporciones verticales.
        Basado en esquema de referencia con ancho fijo y altura proporcional.
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch, Polygon, Circle, FancyArrowPatch, Rectangle
        import numpy as np
        
        resultados_uasb = self.datos
        
        # Extraer valores calculados. Sin fallbacks: si falta un dato, debe corregirse
        # en dimensionar_uasb(), no inventarse en el render LaTeX.
        D = resultados_uasb['D_m']
        H_total = resultados_uasb['H_total_construccion_m']
        H_reaccion = resultados_uasb['H_zona_reaccion_m']
        H_GLS = resultados_uasb['H_GLS_m']
        H_distribucion = resultados_uasb['H_distribucion_m']
        H_sed = resultados_uasb['H_sed_m']
        H_bordo = resultados_uasb['H_bordo_libre_m']
        
        v_up = resultados_uasb['v_up_m_h']
        TRH = resultados_uasb['TRH_h']
        biogas = resultados_uasb['biogaz_m3_d']
        Q_L_s = resultados_uasb['Q_m3_h'] * 1000 / 3600
        n_puntos = resultados_uasb['num_puntos_distribucion']
        
        # Proporciones del esquema (más vertical, como referencia)
        ancho = 5.0  # Ancho fijo para estética (20% más ancho)
        altura_total = 8.0  # Altura total del diagrama
        escala = altura_total / (H_distribucion + H_reaccion + H_sed + H_GLS + H_bordo + 0.5)
        
        # Coordenadas base
        x_centro = 5
        y_base = 1
        x_izq = x_centro - ancho/2
        x_der = x_centro + ancho/2
        
        # Alturas escaladas
        h_dist = H_distribucion * escala
        h_reac = H_reaccion * escala
        h_sed = H_sed * escala
        h_gls = H_GLS * escala
        h_bordo = H_bordo * escala
        
        h_lecho = h_reac * self.cfg.uasb_porcion_lecho_granular
        h_manto = h_reac * self.cfg.uasb_porcion_manto_expandido
        
        # Crear figura (vertical)
        fig, ax = plt.subplots(figsize=(8, 11))
        
        # Colores (suaves como en el esquema de referencia)
        c_lecho = '#E8C4A0'      # Beige/marrón claro
        c_manto = '#F5E6D3'      # Crema muy claro
        c_liquido = '#E8F0F5'    # Azul muy pálido
        c_gls = '#F0F0F0'        # Gris claro
        c_biogas = '#E8F5E9'     # Verde muy pálido
        c_gris_placa = '#C0C0C0' # Gris para placas GLS
        
        # === DIBUJO DEL REACTOR ===
        
        # Cuerpo principal (con bordes redondeados)
        y_bottom = y_base
        y_top = y_bottom + h_dist + h_reac + h_sed + h_gls + h_bordo
        reactor = FancyBboxPatch((x_izq, y_bottom), ancho, y_top - y_bottom,
                                boxstyle="round,pad=0.15", 
                                facecolor='white', edgecolor='#555555', linewidth=2)
        ax.add_patch(reactor)
        
        # 1. Lecho granular (fondo)
        y_lecho_bottom = y_bottom + h_dist
        lecho = Rectangle((x_izq + 0.1, y_lecho_bottom), ancho - 0.2, h_lecho,
                         facecolor=c_lecho, edgecolor='none', alpha=0.9)
        ax.add_patch(lecho)
        
        # Gránulos (círculos marrones)
        np.random.seed(42)
        for _ in range(20):
            cx = x_centro + np.random.uniform(-ancho/2 + 0.3, ancho/2 - 0.3)
            cy = y_lecho_bottom + np.random.uniform(0.1, h_lecho - 0.1)
            r = np.random.uniform(0.08, 0.12)
            ax.add_patch(Circle((cx, cy), r, facecolor='#D4A574', edgecolor='#B8956A', alpha=0.8))
        
        # 2. Manto de lodos expandido
        y_manto_bottom = y_lecho_bottom + h_lecho
        manto = Rectangle((x_izq + 0.1, y_manto_bottom), ancho - 0.2, h_manto,
                         facecolor=c_manto, edgecolor='none', alpha=0.9)
        ax.add_patch(manto)
        
        # Burbujas de biogás en manto (verdes pequeñas)
        for _ in range(12):
            cx = x_centro + np.random.uniform(-ancho/2 + 0.4, ancho/2 - 0.4)
            cy = y_manto_bottom + np.random.uniform(0.1, h_manto - 0.1)
            r = np.random.uniform(0.04, 0.08)
            ax.add_patch(Circle((cx, cy), r, facecolor='#A8D5BA', edgecolor='#7CB87C', alpha=0.6))
        
        # 3. Zona líquida sedimentación
        y_liq_bottom = y_manto_bottom + h_manto
        liquido = Rectangle((x_izq + 0.1, y_liq_bottom), ancho - 0.2, h_sed,
                           facecolor=c_liquido, edgecolor='none', alpha=0.8)
        ax.add_patch(liquido)
        
        # Calcular posición de salida
        y_salida = y_liq_bottom + h_sed * 0.6
        
        # 4. Separador GLS (placas inclinadas 50-55° según Lettinga & Hulshoff Pol)
        y_gls_bottom = y_liq_bottom + h_sed
        
        # Parámetros del GLS desde dimensionamiento/configuración
        angulo_gls = resultados_uasb['GLS_pendiente_adoptada_grados']
        rad = np.radians(angulo_gls)
        traslape = resultados_uasb['GLS_traslape_m']
        espesor_placa = 0.06  # espesor visual de la placa
        
        # Longitud horizontal de la placa desde la pared
        dx = (h_gls - 0.1) / np.tan(rad)
        
        # Placa izquierda (triángulo que sobresale desde la pared)
        x_placa_izq_base = x_izq + 0.1
        x_placa_izq_punta = x_placa_izq_base + dx
        y_placa_izq_abajo = y_gls_bottom + 0.05
        y_placa_izq_arriba = y_gls_bottom + h_gls - 0.05
        
        ax.add_patch(Polygon([
            (x_placa_izq_base, y_placa_izq_abajo),  # abajo izquierda
            (x_placa_izq_punta, y_placa_izq_arriba),  # punta arriba
            (x_placa_izq_punta + espesor_placa * np.cos(rad), y_placa_izq_arriba - espesor_placa * np.sin(rad)),  # punta abajo
            (x_placa_izq_base + espesor_placa * np.cos(rad), y_placa_izq_abajo - espesor_placa * np.sin(rad)),  # abajo derecha
        ], facecolor=c_gris_placa, edgecolor='#808080', linewidth=0.8))
        
        # Placa derecha (espejo)
        x_placa_der_base = x_der - 0.1
        x_placa_der_punta = x_placa_der_base - dx
        y_placa_der_abajo = y_gls_bottom + 0.05
        y_placa_der_arriba = y_gls_bottom + h_gls - 0.05
        
        ax.add_patch(Polygon([
            (x_placa_der_base, y_placa_der_abajo),
            (x_placa_der_punta, y_placa_der_arriba),
            (x_placa_der_punta - espesor_placa * np.cos(rad), y_placa_der_arriba - espesor_placa * np.sin(rad)),
            (x_placa_der_base - espesor_placa * np.cos(rad), y_placa_der_abajo - espesor_placa * np.sin(rad)),
        ], facecolor=c_gris_placa, edgecolor='#808080', linewidth=0.8))
        
        # Línea punteada mostrando el traslape (overlap) - concepto importante según Lettinga
        y_traslape = y_placa_izq_arriba - traslape
        ax.axhline(y=y_traslape, xmin=0.25, xmax=0.75, linestyle=':', color='#666666', linewidth=0.8, alpha=0.7)
        
        # === FLECHAS DE FLUJO INTERNO (verticales simples) ===
        # Tres flechas verticales ascendentes en zona líquida
        for fx in [x_centro - 1.0, x_centro, x_centro + 1.0]:
            ax.annotate('', xy=(fx, y_liq_bottom + h_sed * 0.85), 
                       xytext=(fx, y_lecho_bottom + h_lecho * 0.1),
                       arrowprops=dict(arrowstyle='->', color='#5B9BD5', lw=2.5))
        
        # Flecha horizontal hacia la salida
        ax.annotate('', xy=(x_der + 0.8, y_salida), 
                   xytext=(x_der + 0.1, y_salida),
                   arrowprops=dict(arrowstyle='->', color='#1565C0', lw=3))
        
        # 5. Cámara de biogás
        y_bio_bottom = y_gls_bottom + h_gls
        camara = Rectangle((x_izq + 0.1, y_bio_bottom), ancho - 0.2, h_bordo - 0.1,
                          facecolor=c_biogas, edgecolor='none', alpha=0.8)
        ax.add_patch(camara)
        
        # Burbujas grandes en cámara
        for _ in range(8):
            cx = x_centro + np.random.uniform(-ancho/2 + 0.5, ancho/2 - 0.5)
            cy = y_bio_bottom + np.random.uniform(0.1, h_bordo - 0.2)
            r = np.random.uniform(0.06, 0.12)
            ax.add_patch(Circle((cx, cy), r, facecolor='#A5D6A7', edgecolor='#81C784', alpha=0.7))
        
        # === CONEXIONES EXTERNAS ===
        
        # Tubería de entrada (lateral izquierdo, abajo)
        y_entrada = y_bottom + 0.15
        ax.plot([x_izq - 1.5, x_izq], [y_entrada, y_entrada], 'k-', linewidth=3)
        # Puntos de distribución (negros)
        n_show = min(n_puntos, 6)
        for i in range(n_show):
            x_p = x_izq + 0.3 + i * ((ancho - 0.6) / (n_show - 1)) if n_show > 1 else x_centro
            ax.add_patch(Circle((x_p, y_entrada), 0.06, facecolor='black'))
        
        # Flecha de entrada horizontal (verde)
        ax.annotate('', xy=(x_izq, y_entrada), xytext=(x_izq - 1.2, y_entrada),
                   arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=3))
        
        # Salida de efluente (lateral derecho, nivel líquido) - y_salida ya calculado arriba
        ax.plot([x_der, x_der + 1.0], [y_salida, y_salida], 'k-', linewidth=2.5)
        ax.plot([x_der, x_der], [y_salida - 0.15, y_salida + 0.15], 'k-', linewidth=2)
        ax.add_patch(Rectangle((x_der, y_salida - 0.12), 0.3, 0.24, 
                              facecolor=c_liquido, edgecolor='#555555'))
        # Flecha de salida horizontal (azul)
        ax.annotate('', xy=(x_der + 1.0, y_salida), xytext=(x_der + 0.2, y_salida),
                   arrowprops=dict(arrowstyle='->', color='#1565C0', lw=3))
        
        # Chimenea de biogás (arriba, centro)
        y_chim = y_top
        ax.plot([x_centro, x_centro], [y_chim, y_chim + 0.6], 'k-', linewidth=2.5)
        # Caja colector
        ax.add_patch(Rectangle((x_centro - 0.25, y_chim - 0.1), 0.5, 0.15,
                              facecolor='#E0E0E0', edgecolor='#555555'))
        ax.annotate('', xy=(x_centro, y_chim + 0.6), xytext=(x_centro, y_chim + 0.1),
                   arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=2.5))
        
        # === LÍNEAS DIVISORIAS (punteadas) ===
        dash = dict(linestyle='--', color='#999999', linewidth=0.8, alpha=0.6)
        # Entre lecho y manto
        ax.axhline(y=y_manto_bottom, xmin=0.18, xmax=0.82, **dash)
        # Entre manto y líquido
        ax.axhline(y=y_liq_bottom, xmin=0.18, xmax=0.82, **dash)
        # Entre líquido y GLS
        ax.axhline(y=y_gls_bottom, xmin=0.18, xmax=0.82, **dash)
        # Entre GLS y biogás
        ax.axhline(y=y_bio_bottom, xmin=0.18, xmax=0.82, **dash)
        
        # === LÍNEAS DE DIMENSIÓN ===
        
        # Posición X para líneas de dimensión izquierdas
        x_dim_izq = x_izq - 1.8
        
        # Función auxiliar para dibujar línea de dimensión con flechas
        def draw_dim_line(y1, y2, x_pos, label, offset_x=0):
            # Línea vertical
            ax.plot([x_pos, x_pos], [y1, y2], 'k-', linewidth=0.8)
            # Ticks horizontales
            ax.plot([x_pos - 0.1, x_pos + 0.1], [y1, y1], 'k-', linewidth=0.8)
            ax.plot([x_pos - 0.1, x_pos + 0.1], [y2, y2], 'k-', linewidth=0.8)
            # Flechas
            ax.annotate('', xy=(x_pos, y2 - 0.05), xytext=(x_pos, y2 - 0.25),
                       arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
            ax.annotate('', xy=(x_pos, y1 + 0.05), xytext=(x_pos, y1 + 0.25),
                       arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
            # Texto
            ax.text(x_pos - 0.15, (y1 + y2) / 2, label, ha='right', va='center',
                   fontsize=7, rotation=0)
        
        # Dibujar dimensiones verticales (de abajo hacia arriba)
        # Distribución
        if h_dist > 0.3:
            draw_dim_line(y_bottom, y_bottom + h_dist, x_dim_izq, f'{H_distribucion:.1f} m')
        
        # Lecho granular
        draw_dim_line(y_lecho_bottom, y_lecho_bottom + h_lecho, x_dim_izq, 
                      f'{resultados_uasb["H_lecho_granular_m"]:.1f} m')
        
        # Manto de lodos
        draw_dim_line(y_manto_bottom, y_manto_bottom + h_manto, x_dim_izq,
                      f'{resultados_uasb["H_manto_expandido_m"]:.1f} m')
        
        # Zona líquida sedimentación
        draw_dim_line(y_liq_bottom, y_liq_bottom + h_sed, x_dim_izq,
                      f'{H_sed:.1f} m')
        
        # GLS
        draw_dim_line(y_gls_bottom, y_gls_bottom + h_gls, x_dim_izq,
                      f'{H_GLS:.1f} m')
        
        # Bordo libre / Cámara biogás
        if h_bordo > 0.2:
            draw_dim_line(y_bio_bottom, y_bio_bottom + h_bordo - 0.1, x_dim_izq,
                          f'{H_bordo:.1f} m')
        
        # Dimensión horizontal (ancho)
        y_dim_bottom = y_bottom - 0.8
        ax.plot([x_izq, x_der], [y_dim_bottom, y_dim_bottom], 'k-', linewidth=0.8)
        ax.plot([x_izq, x_izq], [y_dim_bottom - 0.1, y_dim_bottom + 0.1], 'k-', linewidth=0.8)
        ax.plot([x_der, x_der], [y_dim_bottom - 0.1, y_dim_bottom + 0.1], 'k-', linewidth=0.8)
        # Flechas
        ax.annotate('', xy=(x_izq + 0.25, y_dim_bottom), xytext=(x_izq + 0.05, y_dim_bottom),
                   arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
        ax.annotate('', xy=(x_der - 0.25, y_dim_bottom), xytext=(x_der - 0.05, y_dim_bottom),
                   arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
        # Texto
        ax.text(x_centro, y_dim_bottom - 0.15, f'Ø {D:.1f} m', ha='center', va='top', fontsize=8)
        
        # Altura total (línea izquierda completa) - más a la izquierda para evitar solapamiento
        x_dim_total = x_izq - 2.8
        ax.plot([x_dim_total, x_dim_total], [y_bottom, y_top], 'k-', linewidth=0.8)
        ax.plot([x_dim_total - 0.1, x_dim_total + 0.1], [y_bottom, y_bottom], 'k-', linewidth=0.8)
        ax.plot([x_dim_total - 0.1, x_dim_total + 0.1], [y_top, y_top], 'k-', linewidth=0.8)
        ax.text(x_dim_total - 0.15, (y_bottom + y_top) / 2, f'H = {H_total:.1f} m',
               ha='right', va='center', fontsize=8, fontweight='bold')
        
        # === ETIQUETAS (bien distribuidas) ===
        
        # Título eliminado - se pone en LaTeX
        # ax.text(x_centro, y_top + 1.5, 'REACTOR UASB - Esquema de Funcionamiento',
        #        ha='center', va='bottom', fontsize=13, fontweight='bold')
        
        # Biogás (arriba a la derecha)
        ax.text(x_centro + 0.5, y_chim + 0.5, f'Biogás\n{biogas:.1f} m³ CH₄/d',
               ha='left', va='bottom', fontsize=9, color='#2E7D32', fontweight='bold')
        
        # Etiquetas laterales derechas (alineadas con cada zona)
        offset_x = x_der + 0.5
        
        # Cámara biogás
        ax.text(offset_x, y_bio_bottom + h_bordo/2, 'Cámara de biogás\nrecolección CH₄',
               ha='left', va='center', fontsize=8)
        
        # Separador GLS
        ax.text(offset_x, y_gls_bottom + h_gls/2, 'Separador GLS\ngas-líquido-sólido',
               ha='left', va='center', fontsize=8)
        
        # Zona líquida
        ax.text(offset_x, y_liq_bottom + h_sed/2 - 0.4, 'Zona líquida\nsedimentación',
               ha='left', va='center', fontsize=8)
        
        # Manto de lodos
        ax.text(offset_x, y_manto_bottom + h_manto/2, f'Manto de lodos\nvup = {v_up:.2f} m/h',
               ha='left', va='center', fontsize=8, fontweight='bold')
        
        # Lecho granular
        ax.text(offset_x, y_lecho_bottom + h_lecho/2, f'Lecho granular\nHRT = {TRH:.1f} h',
               ha='left', va='center', fontsize=8, fontweight='bold')
        
        # Distribución
        ax.text(offset_x, y_bottom + h_dist/2, f'Distribución afluente\n{n_puntos} puntos',
               ha='left', va='center', fontsize=8)
        
        # Afluente (abajo izquierda)
        ax.text(x_izq - 0.8, y_entrada - 0.5, f'Afluente\n{Q_L_s:.1f} L/s',
               ha='center', va='top', fontsize=9, fontweight='bold', color='#2E7D32')
        
        # Efluente (derecha)
        ax.text(x_der + 1.0, y_salida + 0.1, 'Efluente\ntratado',
               ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1565C0')
        
        # === CONFIGURACIÓN ===
        ax.set_xlim(x_izq - 3.3, x_der + 2.0)
        ax.set_ylim(y_bottom - 1.2, y_top + 1.8)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Guardar
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados', 'figuras')
        os.makedirs(output_dir, exist_ok=True)
        
        fig_path = os.path.join(output_dir, 'Esquema_UASB.png')
        fig.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white', 
                    pad_inches=0.2)
        plt.close()
        
        return fig_path
    def generar_resultados(self) -> str:
        """Genera subsection Resultados con tabla y figura."""
        cfg = self.cfg
        u = self.datos
        
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
        
        return rf"""\subsection{{Resultados}}

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
\quad Lecho de lodo denso/granular ({int(cfg.uasb_porcion_lecho_granular*100):d}\%) & {u['H_lecho_granular_m']:.2f} m \\
\quad Manto expandido ({int(cfg.uasb_porcion_manto_expandido*100):d}\%) & {u['H_manto_expandido_m']:.2f} m \\
\bottomrule
\end{{tabular}}
\end{{table}}

La subdivisión interna de la zona de reacción sigue criterios establecidos por Chernicharo \cite{{chernicharo2007}}. El lecho de lodo denso o granular (aproximadamente {int(cfg.uasb_porcion_lecho_granular*100):d}\% de la altura útil) contiene los lodos más viejos y densos, mientras que el manto de lodos expandido (aproximadamente {int(cfg.uasb_porcion_manto_expandido*100):d}\% de la altura útil) mantiene los lodos en suspensión activa donde ocurre la mayor parte de la degradación biológica.

El reactor UASB requiere un inóculo inicial de lodo anaeróbico denso/granular o, en su defecto, lodo digerido anaeróbicamente. Según Lettinga y Hulshoff-Pol \cite{{vanhaandel1994}}, la cantidad recomendada de inóculo para el arranque es de {cfg.uasb_inoculo_ssv_min_kg_m3:.0f}--{cfg.uasb_inoculo_ssv_max_kg_m3:.0f} kg SSV/m³ (sólidos suspendidos volátiles), equivalente a llenar aproximadamente el {cfg.uasb_inoculo_vol_min_pct:.0f}--{cfg.uasb_inoculo_vol_max_pct:.0f}\% del volumen del reactor. El lodo granular consiste en agregados microbianos densos de {cfg.uasb_lodo_granular_diam_min_mm:.1f}--{cfg.uasb_lodo_granular_diam_max_mm:.0f} mm de diámetro, con velocidades de sedimentación superiores a {cfg.uasb_lodo_granular_vsed_min_m_h:.0f} m/h. Si no se dispone de lodo granular, pueden utilizarse alternativas como lodo de digestor anaerobio, estiércol de cerdo/vaca o lodo de fosas sépticas, desarrollándose la granulación natural en un período de {cfg.uasb_granulacion_natural_min_meses:.0f}--{cfg.uasb_granulacion_natural_max_meses:.0f} meses mediante aumento gradual de la carga orgánica. 

La siguiente figura presenta un esquema del reactor UASB con sus componentes principales y los flujos de agua y biogás:

\begin{{figure}}[H]
\centering
\includegraphics[width=\textwidth]{{{fig_relativa}}}
\caption{{Esquema del reactor UASB: distribución del afluente, zonas de reacción, separación gas-líquido-sólido y recolección de biogás. Caudal por línea: {u['Q_m3_h']:.2f} m³/h, Biogás: {u['biogaz_m3_d']:.1f} m³ CH$_4$/d, {u['num_puntos_distribucion']:.0f} puntos de distribución.}}
\label{{fig:esquema_uasb}}
\end{{figure}}

El esquema ilustra el flujo ascendente del afluente a través del lecho de lodo denso, donde ocurre la digestión anaerobia. El biogás producido se separa en el GLS y se recolecta en la cámara superior, mientras que el efluente tratado sale por el lateral del reactor. La velocidad ascendente de diseño de {u['v_up_m_h']:.2f} m/h garantiza la retención del manto de lodos."""


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_dir)
    
    from ptar_dimensionamiento import ConfigDiseno, dimensionar_uasb
    import subprocess
    
    print("=" * 60)
    print("TEST - GENERADOR MODULAR DE UASB")
    print("=" * 60)
    
    cfg = ConfigDiseno()
    print(f"\n[1] Q_linea = {cfg.Q_linea_L_s} L/s")
    
    datos = dimensionar_uasb(cfg)
    print(f"[2] Dimensiones: D={datos['D_m']:.2f}m, H={datos['H_total_construccion_m']:.2f}m, V={datos['V_r_m3']:.1f}m³")
    
    resultados_dir = os.path.join(base_dir, 'resultados', 'test_modular')
    figuras_dir = os.path.join(resultados_dir, 'figuras')
    os.makedirs(figuras_dir, exist_ok=True)
    
    gen = GeneradorUASB(cfg, datos, ruta_figuras=figuras_dir)
    latex = gen.generar_completo()
    print(f"[3] LaTeX generado: {len(latex)} chars")
    
    tex_path = os.path.join(resultados_dir, 'uasb_test.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    
    doc_path = os.path.join(resultados_dir, 'uasb_test_completo.tex')
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

\section{Reactor UASB}

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
        pdf_path = os.path.join(resultados_dir, 'uasb_test_completo.pdf')
        if os.path.exists(pdf_path):
            print(f"    PDF generado: {pdf_path}")
    except Exception as e:
        print(f"    ERROR: {e}")
    
    print("=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)

