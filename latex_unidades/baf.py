#!/usr/bin/env python3
"""
GENERADOR LaTeX - UNIDAD: BIOFILTRO BIOLÓGICO AIREADO (BAF)

Sistema de lecho sumergido con aireación forzada para post-tratamiento
aerobio después de UASB. Combina degradación biológica y filtración física
en una sola unidad, eliminando la necesidad de sedimentador secundario.

Organizado en 3 subsections: Dimensionamiento, Verificación, Resultados
"""

import os
import sys

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GeneradorBAF:
    """Generador LaTeX para Biofiltro Biológico Aireado (BAF).

    Args:
        cfg: Configuracion de diseno
        datos: Resultados del dimensionamiento
        ruta_figuras: Ruta base donde se guardan las figuras (default: 'figuras')
    """

    def __init__(self, cfg, datos, ruta_figuras='figuras'):
        self.cfg = cfg
        self.datos = datos
        self.ruta_figuras = ruta_figuras

    def generar_completo(self) -> str:
        """Genera todo el contenido LaTeX del BAF en 3 subsections."""
        return "\n\n".join([
            self.generar_descripcion(),
            self.generar_verificacion(),
            self.generar_resultados()
        ])

    def generar_descripcion(self) -> str:
        """Genera subsection Dimensionamiento con teoría y cálculos."""
        cfg = self.cfg
        baf = self.datos

        return rf"""\subsection{{Dimensionamiento}}

El Biofiltro Biológico Aireado (BAF, por sus siglas en inglés \textit{{Biological Aerated Filter}}) es un reactor biológico de biopelícula que opera con el lecho de relleno completamente sumergido y con suministro forzado de oxígeno mediante difusores de burbuja fina instalados en la base del reactor. Esta configuración lo distingue fundamentalmente del filtro percolador tradicional, en el que el agua gotea por gravedad sobre un relleno expuesto al aire ambiente. En el BAF el control de la aireación es activo, lo que permite mantener condiciones plenamente aerobias en toda la altura del lecho con independencia de la carga aplicada.

La característica más relevante del BAF desde el punto de vista del tren de tratamiento es su doble función: actúa simultáneamente como reactor biológico y como filtro físico. Los microorganismos adheridos al relleno degradan la materia orgánica disuelta, mientras que el propio lecho retiene los sólidos suspendidos y la biomasa que eventualmente se desprende del biofilm. El resultado es un efluente clarificado que puede enviarse directamente a desinfección sin necesidad de sedimentador secundario, lo que reduce la huella de planta entre un 30\,\% y un 50\,\% respecto a los sistemas convencionales de lodos activados.

En el presente proyecto el BAF ocupa la posición de tratamiento secundario aerobio aguas abajo del reactor UASB, cuyo efluente contiene típicamente entre 80 y 150\,mg/L de DBO y sólidos suspendidos de tamaño medio. Para el dimensionamiento se adopta una concentración de DBO a la entrada del BAF de $S_0 = {baf['DBO_entrada_mg_L']:.0f}$\,mg/L, valor conservador representativo del efluente UASB para este tipo de sistema.

\subsubsection*{{Principio de Funcionamiento y Configuración}}

El BAF opera sobre la base de una biopelícula aerobia estable adherida a un medio de relleno plástico modular de alta superficie específica ($S_{{\text{{esp}}}} = {baf['sup_especifica_m2_m3']:.0f}$\,m²/m³). El agua residual entra por la parte inferior del reactor y asciende a través del lecho en configuración \textit{{up-flow}}, mientras el aire se inyecta en co-corriente desde el plenum de la base mediante difusores de membrana distribuidos uniformemente en planta.

El proceso de tratamiento que tiene lugar al interior del lecho es inherentemente multifuncional. A medida que el agua asciende por los intersticios del relleno, las bacterias del biofilm consumen la materia orgánica disuelta utilizando el oxígeno aportado por los difusores; paralelamente, el lecho granular actúa como un filtro compacto que retiene físicamente los sólidos en suspensión, las partículas coloidales y los flóculos de biomasa que se desprenden de la biopelícula. Esta doble acción, biológica y física, es lo que permite prescindir de una etapa posterior de clarificación. Si las condiciones de tiempo de contacto y oxigenación son suficientes, las bacterias nitrificantes presentes en las capas más internas del biofilm pueden además oxidar el amonio a nitrato, aunque la nitrificación no es el objetivo principal de diseño en esta unidad.

La biomasa permanece anclada al relleno durante toda la operación normal del reactor. El único mecanismo de extracción de sólidos es el retrolavado periódico, que se detalla más adelante. Esta estabilidad de la biomasa confiere al BAF una notable resiliencia frente a variaciones de caudal y carga: a diferencia de los sistemas de lodos activados, en los que un pico de caudal puede arrastrar masivamente la biomasa fuera del reactor, en el BAF el biofilm adherido permanece en su lugar y continúa tratando el agua incluso durante eventos de punta.

\subsubsection*{{Criterios de Diseño Hidráulico}}

El dimensionamiento del BAF se fundamenta en el criterio de la tasa hidráulica superficial (HLR, \textit{{Hydraulic Loading Rate}}), que relaciona el caudal aplicado con el área de la sección transversal del reactor. Este parámetro controla la velocidad de paso del agua a través del lecho y, en consecuencia, el tiempo de contacto efectivo entre el agua residual y la biopelícula. Valores de HLR elevados reducen el tiempo de contacto y pueden comprometer la eficiencia de tratamiento; valores demasiado bajos incrementan innecesariamente el área del reactor. La literatura técnica de referencia establece un rango operacional de {cfg.baf_HLR_min_m3_m2_h:.1f}--{cfg.baf_HLR_max_m3_m2_h:.1f}\,m³/m²·h para instalaciones de post-tratamiento aerobio (Metcalf \& Eddy, 2014).

Para el presente diseño se adopta una HLR de $q = {baf['HLR_diseño_m3_m2_h']:.1f}$\,m³/m²·h, que ofrece un margen holgado dentro del rango recomendado y permite absorber los picos de caudal sin que la tasa máxima supere el límite permisible. El área superficial requerida se obtiene despejando directamente:

\begin{{equation}}
A_{{s}} = \frac{{Q}}{{q}} = \frac{{{baf['Q_m3_h']:.2f}}}{{{baf['HLR_diseño_m3_m2_h']:.1f}}} = {baf['A_real_m2']:.2f}\ \text{{m}}^2
\end{{equation}}
\captionequation{{Área superficial del BAF por criterio HLR}}

Adoptando una sección circular, el diámetro del reactor es:

\begin{{equation}}
D = \sqrt{{\frac{{4 \cdot A_{{s}}}}{{\pi}}}} = \sqrt{{\frac{{4 \times {baf['A_real_m2']:.2f}}}{{\pi}}}} = {baf['D_m']:.2f}\ \text{{m}}
\end{{equation}}
\captionequation{{Diámetro del reactor BAF}}

Con el diámetro adoptado de {baf['D_m']:.2f}\,m, el área real resulta $A_{{s}} = {baf['A_real_m2']:.2f}$\,m², y la HLR real a caudal medio queda en $q_{{\text{{real}}}} = {baf['HLR_real_m3_m2_h']:.2f}$\,m³/m²·h, confirmando que el dimensionamiento se encuentra plenamente dentro del rango operacional establecido.

\subsubsection*{{Volumen de Lecho y Tiempo de Contacto}}

La profundidad del lecho de relleno determina el volumen biológicamente activo del reactor y, por tanto, el tiempo de contacto disponible para la degradación de la materia orgánica. Se adopta una profundidad de $H_{{\text{{lecho}}}} = {baf['H_lecho_m']:.2f}$\,m, valor que se encuentra dentro del rango habitual de 2.5--4.0\,m para BAF de flujo ascendente con relleno plástico. El volumen del medio filtrante resulta:

\begin{{equation}}
V_{{\text{{lecho}}}} = A_{{s}} \cdot H_{{\text{{lecho}}}} = {baf['A_real_m2']:.2f} \times {baf['H_lecho_m']:.2f} = {baf['V_lecho_m3']:.2f}\ \text{{m}}^3
\end{{equation}}
\captionequation{{Volumen del lecho de relleno}}

El tiempo de contacto en lecho vacío (EBCT, \textit{{Empty Bed Contact Time}}) es el parámetro de control más directo de la eficiencia de tratamiento. Representa el tiempo teórico que tardaría el caudal en llenar el volumen del lecho si estuviera completamente vacío; en la práctica, el tiempo de residencia real del agua es inferior porque el relleno ocupa parte del volumen, pero el EBCT constituye la referencia de diseño universalmente adoptada. Valores de EBCT demasiado cortos comprometen la remoción de contaminantes; valores excesivos no aportan beneficio adicional y aumentan innecesariamente las dimensiones del reactor:

\begin{{equation}}
\text{{EBCT}} = \frac{{V_{{\text{{lecho}}}}}}{{Q_{{h}}}} = \frac{{{baf['V_lecho_m3']:.2f}}}{{{baf['Q_m3_h']:.2f}}} = {baf['EBCT_h']:.2f}\ \text{{h}}
\end{{equation}}
\captionequation{{Tiempo de contacto en lecho vacío a caudal medio}}

El valor calculado de $\text{{EBCT}} = {baf['EBCT_h']:.2f}$\,h se encuentra dentro del rango recomendado de {cfg.baf_EBCT_min_h:.1f}--{cfg.baf_EBCT_max_h:.1f}\,h, confirmando que el lecho proporciona un tiempo de contacto adecuado para la degradación de la materia orgánica a caudal de operación normal.

\subsubsection*{{Carga Orgánica Volumétrica}}

La carga orgánica volumétrica (OLR, \textit{{Organic Loading Rate}}) relaciona la masa de contaminante que ingresa al reactor por unidad de volumen de lecho y por día. Es el criterio que garantiza que la biomasa del BAF no sea sobrecargada: si la OLR supera la capacidad metabólica del biofilm, la eficiencia de remoción cae y el efluente puede deteriorarse. La masa de DBO aplicada diariamente al reactor es:

\begin{{equation}}
W_{{\text{{DBO}}}} = Q_{{d}} \cdot S_0 = {baf['Q_m3_d']:.1f}\ \text{{m}}^3\text{{/d}} \times {baf['DBO_entrada_mg_L']:.0f}\ \text{{g/m}}^3 \times 10^{{-3}} = {baf['carga_DBO_kg_d']:.1f}\ \text{{kg DBO/d}}
\end{{equation}}
\captionequation{{Carga orgánica diaria aplicada al BAF}}

Dividiendo entre el volumen del lecho, la OLR de diseño resulta:

\begin{{equation}}
\text{{OLR}} = \frac{{W_{{\text{{DBO}}}}}}{{V_{{\text{{lecho}}}}}} = \frac{{{baf['carga_DBO_kg_d']:.1f}}}{{{baf['V_lecho_m3']:.2f}}} = {baf['OLR_kgDBO_m3_d']:.2f}\ \text{{kg DBO/m}}^3\text{{·d}}
\end{{equation}}
\captionequation{{Carga orgánica volumétrica del BAF}}

El valor de OLR = {baf['OLR_kgDBO_m3_d']:.2f}\,kg DBO/m³·d se encuentra dentro del rango operacional recomendado de {cfg.baf_OLR_min_kgDBO_m3_d:.1f}--{cfg.baf_OLR_max_kgDBO_m3_d:.1f}\,kg DBO/m³·d, lo que indica que la biomasa adherida operará con una carga manejable, con margen suficiente para absorber variaciones temporales de la concentración de DBO en el afluente.

\subsubsection*{{Sistema de Aireación}}

El suministro adecuado de oxígeno es condición necesaria para el correcto funcionamiento del BAF: sin oxígeno suficiente el biofilm pierde su actividad aerobia, la eficiencia de remoción cae y pueden generarse condiciones anóxicas o anaerobias en el interior del lecho, con producción de olores. El caudal de aire se dimensiona a partir de la relación aire:agua, que indica el volumen de aire en condiciones normales (0\,°C, 1\,atm) que debe inyectarse por cada metro cúbico de agua tratada. Se adopta una relación de ${baf['relacion_aire_agua']:.0f}:1$, valor típico para eliminación de DBO sin nitrificación intensiva:

\begin{{equation}}
Q_{{\text{{aire}}}} = r_{{\text{{a:w}}}} \times Q_{{h}} = {baf['relacion_aire_agua']:.0f} \times {baf['Q_m3_h']:.2f} = {baf['Q_aire_Nm3_h']:.1f}\ \text{{Nm}}^3\text{{/h}}
\end{{equation}}
\captionequation{{Caudal de aire suministrado al proceso biológico}}

La tasa específica de aireación (SAR, \textit{{Specific Air Rate}}) normaliza el caudal de aire por unidad de área superficial del reactor y permite comparar el nivel de aireación con los rangos de referencia:

\begin{{equation}}
\text{{SAR}} = \frac{{Q_{{\text{{aire}}}}}}{{A_{{s}}}} = \frac{{{baf['Q_aire_Nm3_h']:.1f}}}{{{baf['A_real_m2']:.2f}}} = {baf['SAR_m3_m2_h']:.1f}\ \text{{m}}^3\text{{aire/m}}^2\text{{·h}}
\end{{equation}}
\captionequation{{Tasa específica de aireación}}

El valor de SAR = {baf['SAR_m3_m2_h']:.1f}\,m³/m²·h se encuentra dentro del rango recomendado de {cfg.baf_SAR_min_m3_m2_h:.0f}--{cfg.baf_SAR_max_m3_m2_h:.0f}\,m³/m²·h. Como comprobación adicional, la demanda teórica de oxígeno para degradar {baf['carga_DBO_kg_d']:.1f}\,kg DBO/d —considerando un factor de {cfg.baf_factor_O2_kgO2_kgDBO:.2f}\,kg O₂/kg DBO y una eficiencia de transferencia de oxígeno (OTE) del {cfg.baf_OTE_pct:.0f}\%— exige un caudal mínimo de {baf['Q_aire_min_Nm3_h']:.1f}\,Nm³/h. El diseño proporciona {baf['Q_aire_Nm3_h']:.1f}\,Nm³/h, con un factor de seguridad de {baf['factor_seguridad_aire']:.1f} sobre la demanda biológica mínima; esto garantiza oxigenación suficiente en todo el lecho incluso bajo condiciones de carga elevada o variaciones en la concentración de DBO del afluente.

\subsubsection*{{Desglose de Alturas y Geometría del Reactor}}

La altura total del reactor BAF resulta de la superposición de varias zonas funcionales, cada una de las cuales cumple un propósito específico dentro del ciclo de operación. El plenum inferior aloja los difusores de aire y los colectores de distribución de agua, garantizando una entrada uniforme del afluente en toda la sección del reactor. El lecho de relleno es la zona de tratamiento activo. La zona libre sobre el relleno (\textit{{headspace}}) proporciona el espacio necesario para la expansión del lecho durante el retrolavado sin que el relleno sea arrastrado hacia el canal de salida. La zona de acumulación retiene temporalmente los sólidos desprendidos antes de su evacuación al final del ciclo de retrolavado. El bordo libre garantiza la seguridad hidráulica de la estructura frente a variaciones bruscas de caudal:

\begin{{table}}[H]
\centering
\caption{{Desglose de alturas del reactor BAF}}
\begin{{tabular}}{{lc}}
\toprule
\textbf{{Zona funcional}} & \textbf{{Altura (m)}} \\
\midrule
Plenum de distribución de agua y aire & {baf['H_plenum_m']:.2f} \\
Lecho de relleno (media biológica) & {baf['H_lecho_m']:.2f} \\
Zona libre sobre relleno (headspace) & {baf['H_headspace_m']:.2f} \\
Zona de acumulación durante retrolavado & {baf['H_acumulacion_m']:.2f} \\
Bordo libre & {baf['H_bordo_m']:.2f} \\
\midrule
\textbf{{Altura total de construcción}} & \textbf{{{baf['H_total_m']:.2f}}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

La relación de aspecto entre la profundidad del lecho y el diámetro del reactor, $H_{{\text{{lecho}}}} / D = {baf['relacion_H_D']:.2f}$, se encuentra dentro del rango recomendado de {cfg.baf_relacion_H_D_min:.1f}--{cfg.baf_relacion_H_D_max:.1f} para reactores BAF circulares, lo que garantiza una distribución uniforme del agua y el aire en toda la sección transversal y evita caminos preferenciales de flujo que reducirían el contacto efectivo entre el sustrato y la biomasa.

\subsubsection*{{Sistema de Retrolavado}}

El retrolavado es la operación de mantenimiento más característica del BAF. A medida que el reactor opera, el biofilm crece sobre el relleno y los sólidos filtrados se acumulan en los intersticios del lecho, produciendo un aumento progresivo de la pérdida de carga hidráulica. Cuando esa pérdida de carga alcanza el límite preestablecido, o cuando ha transcurrido el tiempo máximo del ciclo de operación, se inicia el retrolavado. El diseño contempla ciclos de retrolavado cada {baf['freq_retrolavado_h']:.0f}--{cfg.baf_freq_retrolavado_max_h:.0f}\,h, con una duración total aproximada de {baf['duracion_retrolavado_min']:.0f}\,minutos por ciclo, operando en dos fases consecutivas:

La primera fase, denominada retrolavado con aire (\textit{{air scour}}), consiste en inyectar aire a alta velocidad —{baf['vel_bw_aire_m3_m2_h']:.0f}\,m³/m²·h, equivalente a un caudal de $Q_{{\text{{bw,aire}}}} = {baf['Q_bw_aire_m3_h']:.1f}$\,m³/h— para despegar el biofilm excedente y los sólidos retenidos en los intersticios del relleno. La turbulencia generada por el aire libera la materia acumulada sin dañar la estructura del biofilm residente, que permanecerá adherida al relleno y continuará el tratamiento en el ciclo siguiente.

La segunda fase, el retrolavado con agua (\textit{{water flush}}), introduce agua limpia en sentido contrario al flujo de operación normal a una velocidad de {baf['vel_bw_agua_m3_m2_h']:.0f}\,m³/m²·h, generando un caudal de $Q_{{\text{{bw,agua}}}} = {baf['Q_bw_agua_m3_h']:.1f}$\,m³/h que arrastra hacia el canal de evacuación superior los sólidos liberados durante la fase anterior. El volumen total de agua de retrolavado por ciclo es $V_{{\text{{bw}}}} = {baf['V_bw_ciclo_m3']:.1f}$\,m³, lo que representa el {baf['fraccion_bw_pct']:.1f}\,\% del caudal diario tratado. Esta agua, cargada con sólidos biológicos en concentraciones de 500--3\,000\,mg/L de SST, debe retornar al inicio de la planta o dirigirse a un espesador de lodos; nunca debe descargarse directamente al efluente tratado. Dado que el sistema opera con dos líneas en paralelo, los ciclos de retrolavado deben escalonarse para que nunca coincidan dos unidades en retrolavado simultáneo."""

    def generar_verificacion(self) -> str:
        """Genera subsection Verificación con todas las verificaciones."""
        cfg = self.cfg
        baf = self.datos
        verifs = baf['verificaciones']

        # Extraer estados del cálculo (viene de ptar_dimensionamiento.py)
        estado_EBCT_pico = verifs['EBCT_pico']['estado']
        texto_EBCT_pico = verifs['EBCT_pico']['texto']
        estado_OLR_pico = verifs['OLR_pico']['estado']
        texto_OLR_pico = verifs['OLR_pico']['texto']
        estado_aire = verifs['suficiencia_aire']['estado']
        texto_aire = verifs['suficiencia_aire']['texto']
        texto_resumen = baf['texto_resumen_verificaciones']

        return rf"""\subsection{{Verificación}}

El dimensionamiento presentado en la sección anterior se basa en los parámetros de operación a caudal medio. Las verificaciones que se desarrollan a continuación comprueban que el reactor mantiene un comportamiento aceptable bajo las condiciones más exigentes: el caudal máximo horario, la condición de pico de carga orgánica y la suficiencia del suministro de aire. Se incluyen también las verificaciones de geometría del reactor y del sistema de retrolavado, que son criterios complementarios de buena práctica de diseño.

\subsubsection*{{Verificación de Tasa Hidráulica Superficial a Caudal de Pico}}

La verificación más crítica del BAF desde el punto de vista hidráulico consiste en comprobar que la tasa hidráulica superficial a caudal máximo horario —obtenido aplicando el factor de pico $f_p = {cfg.factor_pico_Qmax:.1f}$— no supera el límite establecido por la literatura técnica. Si la HLR de pico excede ese límite, la velocidad de paso del agua a través del lecho sería excesiva, los sólidos suspendidos que el lecho retiene podrían ser arrastrados hacia el efluente y la calidad de salida se deterioraría transitoriamente:

\begin{{equation}}
q_{{\text{{máx}}}} = \frac{{Q_{{\text{{máx}}}}}}{{A_{{s}}}} = \frac{{{baf['Q_max_m3_h']:.2f}}}{{{baf['A_real_m2']:.2f}}} = {baf['HLR_max_m3_m2_h']:.2f}\ \text{{m}}^3\text{{/m}}^2\text{{·h}} \leq {cfg.baf_HLR_max_pico_m3_m2_h:.1f}\ \text{{m}}^3\text{{/m}}^2\text{{·h}}
\end{{equation}}
\captionequation{{HLR a caudal máximo horario}}

El valor calculado de $q_{{\text{{máx}}}} = {baf['HLR_max_m3_m2_h']:.2f}$\,m³/m²·h deja un margen de seguridad del $({cfg.baf_HLR_max_pico_m3_m2_h:.1f} - {baf['HLR_max_m3_m2_h']:.2f}) / {cfg.baf_HLR_max_pico_m3_m2_h:.1f} \times 100 = {((cfg.baf_HLR_max_pico_m3_m2_h - baf['HLR_max_m3_m2_h'])/cfg.baf_HLR_max_pico_m3_m2_h*100):.1f}$\,\% respecto al límite permisible.

\textbf{{Resultado:}} \textbf{{{verifs['HLR_maximo']['estado']}}}

\subsubsection*{{Verificación de Tiempo de Contacto a Caudal de Pico}}

A caudal máximo, el EBCT se reduce en proporción inversa al incremento de caudal. Esta verificación es informativa y complementaria: el EBCT de diseño ya se garantiza a caudal medio; a caudal de pico se espera una reducción que es transitoria y que la inercia biológica del biofilm puede absorber:

\begin{{equation}}
\text{{EBCT}}_{{\text{{pico}}}} = \frac{{V_{{\text{{lecho}}}}}}{{Q_{{\text{{máx}}}}}} = \frac{{{baf['V_lecho_m3']:.2f}}}{{{baf['Q_max_m3_h']:.2f}}} = {baf['EBCT_pico_h']:.2f}\ \text{{h}}
\end{{equation}}
\captionequation{{EBCT a caudal máximo horario}}

{texto_EBCT_pico}

\textbf{{Resultado:}} \textbf{{{estado_EBCT_pico}}}

\subsubsection*{{Verificación de Carga Orgánica a Caudal de Pico}}

A caudal máximo, la OLR también se incrementa en la misma proporción que el caudal, puesto que la concentración de DBO del afluente no varía durante los picos hidráulicos. Esta verificación evalúa el estrés orgánico al que se somete la biomasa durante el evento de punta:

\begin{{equation}}
\text{{OLR}}_{{\text{{pico}}}} = \frac{{Q_{{\text{{máx,d}}}} \cdot S_0}}{{V_{{\text{{lecho}}}}}} = \frac{{{baf['Q_max_m3_d']:.1f} \times {baf['DBO_entrada_mg_L']:.0f} \times 10^{{-3}}}}{{{baf['V_lecho_m3']:.2f}}} = {baf['OLR_pico_kgDBO_m3_d']:.2f}\ \text{{kg/m}}^3\text{{·d}}
\end{{equation}}
\captionequation{{OLR a caudal máximo horario}}

{texto_OLR_pico}

\textbf{{Resultado:}} \textbf{{{estado_OLR_pico}}}

\subsubsection*{{Verificación de Suficiencia del Suministro de Aire}}

Esta verificación comprueba que el caudal de aire diseñado en función de la relación aire:agua es también suficiente para cubrir la demanda biológica de oxígeno del proceso. Se trata de una verificación cruzada entre el criterio hidráulico de aireación y el criterio bioquímico de demanda de oxígeno. La demanda teórica de oxígeno para degradar la carga orgánica media es:

\begin{{equation}}
\text{{DO}}_{{\text{{req}}}} = f_{{O_2}} \times W_{{\text{{DBO}}}} = {cfg.baf_factor_O2_kgO2_kgDBO:.2f} \times {baf['carga_DBO_kg_d']:.1f} = {baf['carga_DBO_kg_d'] * cfg.baf_factor_O2_kgO2_kgDBO:.1f}\ \text{{kg O}}_2\text{{/d}}
\end{{equation}}
\captionequation{{Demanda de oxígeno para degradación de DBO}}

Considerando una eficiencia de transferencia de oxígeno (OTE) del {cfg.baf_OTE_pct:.0f}\,\% para difusores de burbuja fina en lecho sumergido, el caudal mínimo de aire que satisface esa demanda biológica es {baf['Q_aire_min_Nm3_h']:.1f}\,Nm³/h. El diseño proporciona {baf['Q_aire_Nm3_h']:.1f}\,Nm³/h, es decir, un factor de seguridad de {baf['factor_seguridad_aire']:.1f} sobre el requerimiento mínimo. {texto_aire}

\textbf{{Resultado:}} \textbf{{{estado_aire}}}

\subsubsection*{{Verificación de Geometría del Reactor}}

La relación de aspecto entre la profundidad del lecho y el diámetro del reactor es un criterio complementario que verifica que las proporciones del reactor sean adecuadas para una distribución uniforme del flujo en toda la sección transversal. Reactores con relaciones $H/D$ muy bajas tienden a presentar distribución no uniforme del agua y el aire; reactores con relaciones muy altas pueden desarrollar canalizaciones verticales preferenciales:

\begin{{equation}}
\frac{{H_{{\text{{lecho}}}}}}{{D}} = \frac{{{baf['H_lecho_m']:.2f}}}{{{baf['D_m']:.2f}}} = {baf['relacion_H_D']:.2f}
\end{{equation}}
\captionequation{{Relación de aspecto del lecho de relleno}}

El valor de {baf['relacion_H_D']:.2f} se encuentra dentro del rango recomendado de {cfg.baf_relacion_H_D_min:.1f}--{cfg.baf_relacion_H_D_max:.1f}, confirmando que la geometría del reactor es adecuada.

\textbf{{Resultado:}} \textbf{{{verifs['relacion_H_D']['estado']}}}

\subsubsection*{{Resumen de Verificaciones}}

La Tabla~\ref{{tab:verif_baf}} consolida los criterios de verificación, los valores calculados y el estado de cumplimiento de cada parámetro.

\begin{{table}}[H]
\centering
\caption{{Resumen de verificaciones del BAF}}
\label{{tab:verif_baf}}
\begin{{tabular}}{{lccl}}
\toprule
\textbf{{Parámetro}} & \textbf{{Valor calculado}} & \textbf{{Criterio}} & \textbf{{Estado}} \\
\midrule
HLR medio        & {baf['HLR_real_m3_m2_h']:.2f} m³/m²·h   & {cfg.baf_HLR_min_m3_m2_h:.1f}--{cfg.baf_HLR_max_m3_m2_h:.1f} m³/m²·h  & \textbf{{{verifs['HLR_medio']['estado']}}} \\
HLR máximo       & {baf['HLR_max_m3_m2_h']:.2f} m³/m²·h   & $\leq$ {cfg.baf_HLR_max_pico_m3_m2_h:.1f} m³/m²·h             & \textbf{{{verifs['HLR_maximo']['estado']}}} \\
EBCT medio       & {baf['EBCT_h']:.2f} h                   & {cfg.baf_EBCT_min_h:.1f}--{cfg.baf_EBCT_max_h:.1f} h                   & \textbf{{{verifs['EBCT_medio']['estado']}}} \\
EBCT pico        & {baf['EBCT_pico_h']:.2f} h              & $\geq$ {cfg.baf_EBCT_min_h:.1f} h (diseño)             & \textbf{{{verifs['EBCT_pico']['estado']}}} \\
OLR medio        & {baf['OLR_kgDBO_m3_d']:.2f} kg/m³·d   & {cfg.baf_OLR_min_kgDBO_m3_d:.1f}--{cfg.baf_OLR_max_kgDBO_m3_d:.1f} kg/m³·d & \textbf{{{verifs['OLR_medio']['estado']}}} \\
OLR pico         & {baf['OLR_pico_kgDBO_m3_d']:.2f} kg/m³·d & $\leq$ {cfg.baf_OLR_max_kgDBO_m3_d:.1f} kg/m³·d          & \textbf{{{verifs['OLR_pico']['estado']}}} \\
SAR              & {baf['SAR_m3_m2_h']:.1f} m³/m²·h       & {cfg.baf_SAR_min_m3_m2_h:.0f}--{cfg.baf_SAR_max_m3_m2_h:.0f} m³/m²·h  & \textbf{{{verifs['SAR']['estado']}}} \\
Suficiencia aire & {baf['factor_seguridad_aire']:.1f}      & $\geq$ 1.0 (mínimo); $\geq$ {cfg.baf_factor_seguridad_aire_min:.1f} (holgura)  & \textbf{{{verifs['suficiencia_aire']['estado']}}} \\
Relación $H/D$   & {baf['relacion_H_D']:.2f}               & {cfg.baf_relacion_H_D_min:.1f}--{cfg.baf_relacion_H_D_max:.1f}          & \textbf{{{verifs['relacion_H_D']['estado']}}} \\
Agua retrolavado & {baf['fraccion_bw_pct']:.1f}\%          & {cfg.baf_fraccion_bw_min_pct:.0f}--{cfg.baf_fraccion_bw_max_pct:.0f}\%  & \textbf{{{verifs['fraccion_retrolavado']['estado']}}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

{texto_resumen}"""

    def generar_resultados(self) -> str:
        """Genera subsection Resultados con longtable consolidada y figura."""
        cfg = self.cfg
        baf = self.datos

        # Generar figura
        if os.path.isabs(self.ruta_figuras):
            output_dir = self.ruta_figuras
            # Para LaTeX, construir ruta completa y normalizar a forward slashes
            ruta_completa = os.path.join(self.ruta_figuras, 'Esquema_BAF.png')
            latex_ruta_figura = ruta_completa.replace('\\', '/')
        else:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados', self.ruta_figuras)
            latex_ruta_figura = self.ruta_figuras + '/Esquema_BAF.png'

        figura_generada = False
        try:
            self.generar_esquema_matplotlib(output_dir)
            figura_latex = rf"""\begin{{figure}}[H]
\centering
\includegraphics[width=0.75\textwidth]{{{latex_ruta_figura}}}
\caption{{Esquema del Biofiltro Biológico Aireado (BAF) -- vista vertical (sección transversal)}}
\label{{fig:esquema_baf}}
\end{{figure}}

"""
            figura_generada = True
        except Exception as e:
            figura_latex = ""
            figura_generada = False

        # Texto descriptivo condicional a la existencia de figura
        if figura_generada:
            texto_esquema = "El esquema muestra la configuración de flujo ascendente (\\textit{{up-flow}}) con aireación en co-corriente, el lecho de relleno plástico sumergido, y las zonas de plenum, headspace y acumulación para retrolavado."
        else:
            texto_esquema = "La configuración de flujo es ascendente (\\textit{{up-flow}}) con aireación en co-corriente, con lecho de relleno plástico sumergido y zonas de plenum, headspace y acumulación para retrolavado."

        return rf"""\subsection{{Resultados}}

La Tabla~\ref{{tab:resumen_baf}} consolida los parámetros geométricos, hidráulicos y de proceso del Biofiltro Biológico Aireado dimensionado para una de las dos líneas de tratamiento, cada una de las cuales procesa el caudal medio de $Q = {baf['Q_m3_d']:.1f}$\,m³/d.

\begin{{longtable}}{{p{{7cm}}p{{6cm}}}}
\caption{{Resumen de resultados del dimensionamiento -- Biofiltro Biológico Aireado (BAF)}}
\label{{tab:resumen_baf}} \\
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} \\
\midrule
\endfirsthead
\caption[]{{(continuación) Biofiltro Biológico Aireado (BAF)}} \\
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} \\
\midrule
\endhead
\midrule
\multicolumn{{2}}{{r}}{{\textit{{continúa en la página siguiente}}}} \\
\endfoot
\bottomrule
\endlastfoot
%
\multicolumn{{2}}{{l}}{{\textit{{Dimensiones principales}}}} \\[2pt]
Diámetro del reactor          & $D = {baf['D_m']:.2f}$\,m \\
Área superficial (real)       & $A_s = {baf['A_real_m2']:.2f}$\,m² \\
Profundidad del lecho         & $H_{{\text{{lecho}}}} = {baf['H_lecho_m']:.2f}$\,m \\
Altura total de construcción  & $H_{{\text{{total}}}} = {baf['H_total_m']:.2f}$\,m \\
Volumen de relleno            & $V_{{\text{{lecho}}}} = {baf['V_lecho_m3']:.2f}$\,m³ \\
Relación de aspecto           & $H_{{\text{{lecho}}}}/D = {baf['relacion_H_D']:.2f}$ \\[4pt]
%
\multicolumn{{2}}{{l}}{{\textit{{Parámetros hidráulicos}}}} \\[2pt]
Caudal medio por línea        & $Q = {baf['Q_m3_d']:.1f}$\,m³/d \;({baf['Q_m3_h']:.2f}\,m³/h) \\
Caudal máximo horario         & $Q_{{\text{{máx}}}} = {baf['Q_max_m3_d']:.1f}$\,m³/d \;({baf['Q_max_m3_h']:.2f}\,m³/h) \\
HLR a caudal medio            & $q = {baf['HLR_real_m3_m2_h']:.2f}$\,m³/m²·h \\
HLR a caudal máximo           & $q_{{\text{{máx}}}} = {baf['HLR_max_m3_m2_h']:.2f}$\,m³/m²·h \\
EBCT a caudal medio           & {baf['EBCT_h']:.2f}\,h \\
EBCT a caudal máximo          & {baf['EBCT_pico_h']:.2f}\,h \\[4pt]
%
\multicolumn{{2}}{{l}}{{\textit{{Parámetros de proceso y carga orgánica}}}} \\[2pt]
DBO afluente (efluente UASB)  & $S_0 = {baf['DBO_entrada_mg_L']:.0f}$\,mg/L \\
Carga orgánica media          & $W = {baf['carga_DBO_kg_d']:.1f}$\,kg DBO/d \\
Carga orgánica a pico         & $W_{{\text{{pico}}}} = {baf['carga_DBO_pico_kg_d']:.1f}$\,kg DBO/d \\
OLR a caudal medio            & {baf['OLR_kgDBO_m3_d']:.2f}\,kg DBO/m³·d \\
OLR a caudal máximo           & {baf['OLR_pico_kgDBO_m3_d']:.2f}\,kg DBO/m³·d \\[4pt]
%
\multicolumn{{2}}{{l}}{{\textit{{Sistema de aireación}}}} \\[2pt]
Relación aire:agua            & ${baf['relacion_aire_agua']:.0f}:1$\,Nm³/m³ \\
Caudal de aire de proceso     & $Q_{{\text{{aire}}}} = {baf['Q_aire_Nm3_h']:.1f}$\,Nm³/h \\
Tasa específica de aireación  & SAR $= {baf['SAR_m3_m2_h']:.1f}$\,m³/m²·h \\
Factor de seguridad oxígeno   & {baf['factor_seguridad_aire']:.1f} \\[4pt]
%
\multicolumn{{2}}{{l}}{{\textit{{Sistema de retrolavado}}}} \\[2pt]
Frecuencia de retrolavado     & cada {baf['freq_retrolavado_h']:.0f}--{cfg.baf_freq_retrolavado_max_h:.0f}\,h \\
Duración del ciclo            & $\sim${baf['duracion_retrolavado_min']:.0f}\,min \\
Velocidad retrolavado -- aire & {baf['vel_bw_aire_m3_m2_h']:.0f}\,m³/m²·h \\
Velocidad retrolavado -- agua & {baf['vel_bw_agua_m3_m2_h']:.0f}\,m³/m²·h \\
Caudal aire en retrolavado    & $Q_{{\text{{bw,aire}}}} = {baf['Q_bw_aire_m3_h']:.1f}$\,m³/h \\
Caudal agua en retrolavado    & $Q_{{\text{{bw,agua}}}} = {baf['Q_bw_agua_m3_h']:.1f}$\,m³/h \\
Volumen por ciclo             & $V_{{\text{{bw}}}} = {baf['V_bw_ciclo_m3']:.1f}$\,m³ \\
Fracción del caudal diario    & {baf['fraccion_bw_pct']:.1f}\,\% \\[4pt]
%
\multicolumn{{2}}{{l}}{{\textit{{Características del relleno}}}} \\[2pt]
Superficie específica         & $S_{{\text{{esp}}}} = {baf['sup_especifica_m2_m3']:.0f}$\,m²/m³ \\
Porosidad                     & $\varepsilon = {baf['porosidad_pct']:.0f}$\,\% \\
Material                      & Plástico modular \\
\end{{longtable}}

El dimensionamiento del BAF produce un reactor compacto de {baf['D_m']:.2f}\,m de diámetro y {baf['H_total_m']:.2f}\,m de altura total, con un volumen de lecho de {baf['V_lecho_m3']:.2f}\,m³ por unidad. El presente proyecto adopta la tecnología de biofiltro con lecho sumergido y aireación forzada, la cual opera con biomasa adherida al relleno plástico de alta superficie específica. Esta configuración tecnológica incorpora intrínsecamente la retención física de sólidos en el lecho, característica que en condiciones de diseño apropiadas permite obtener efluentes clarificados sin requerir una unidad de sedimentación secundaria independiente, diferenciándose así de los sistemas convencionales de lodos activados que sí necesitan sedimentador posterior.

{figura_latex}{texto_esquema}"""

    def generar_esquema_matplotlib(self, output_dir=None):
        """
        Genera un esquema técnico del reactor BAF (Biofiltro Biológico Aireado)
        en vista vertical (sección transversal de reactor cilíndrico).
        Basado exactamente en el estilo, paleta de colores, calidad visual y estructura
        del esquema UASB proporcionado, pero adaptado a la geometría y zonas del BAF:
        - Plenum inferior con difusores de agua y aire
        - Lecho de relleno plástico sumergido (con biofilm y burbujas)
        - Zona libre (headspace) + zona de acumulación para retrolavado
        - Bordo libre
        Usa los valores calculados en dimensionar_baf() sin fallbacks.
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon, FancyArrowPatch
        import numpy as np
        import os

        resultados_baf = self.datos

        # Extraer valores calculados (exactos del dimensionamiento BAF)
        D = resultados_baf['D_m']
        H_total = resultados_baf['H_total_m']
        H_plenum = resultados_baf['H_plenum_m']
        H_lecho = resultados_baf['H_lecho_m']
        H_headspace = resultados_baf['H_headspace_m']
        H_acumulacion = resultados_baf['H_acumulacion_m']
        H_bordo = resultados_baf['H_bordo_m']
        SAR = resultados_baf['SAR_m3_m2_h']
        Q_aire = resultados_baf['Q_aire_Nm3_h']
        Q_L_s = resultados_baf['Q_m3_h'] * 1000 / 3600
        sup_especifica = resultados_baf['sup_especifica_m2_m3']

        # Proporciones del esquema (vertical, como UASB)
        ancho = 5.0                     # Ancho fijo del tanque visual (estética)
        altura_total = 9.0              # Altura total del diagrama
        escala = altura_total / H_total

        # Coordenadas base
        x_centro = 5
        y_base = 1
        x_izq = x_centro - ancho / 2
        x_der = x_centro + ancho / 2

        # Alturas escaladas
        h_plenum = H_plenum * escala
        h_lecho = H_lecho * escala
        h_headspace = H_headspace * escala
        h_acumulacion = H_acumulacion * escala
        h_bordo = H_bordo * escala

        # Crear figura (vertical)
        fig, ax = plt.subplots(figsize=(8, 11))

        # Colores consistentes con esquema UASB
        c_plenum = '#C0C0C0'         # Gris claro (plenum / soporte)
        c_lecho = '#A8D5BA'          # Verde claro (relleno plástico + biofilm)
        c_liquido = '#E8F0F5'        # Azul muy pálido
        c_headspace = '#F0F0F0'      # Gris muy claro
        c_biogas = '#E8F5E9'         # Verde pálido (zona de aireación)
        c_gris_placa = '#C0C0C0'     # Gris para estructuras
        c_burbuja = '#81C784'        # Verde claro (burbujas de aire)

        # === DIBUJO DEL REACTOR ===
        y_bottom = y_base
        y_top = y_bottom + h_plenum + h_lecho + h_headspace + h_acumulacion + h_bordo
        reactor = FancyBboxPatch((x_izq, y_bottom), ancho, y_top - y_bottom,
                                 boxstyle="round,pad=0.15", 
                                 facecolor='white', edgecolor='#555555', linewidth=3)
        ax.add_patch(reactor)

        # 1. Plenum inferior (distribución agua + aire)
        y_plenum_top = y_bottom + h_plenum
        plenum = Rectangle((x_izq + 0.1, y_bottom), ancho - 0.2, h_plenum,
                           facecolor=c_plenum, edgecolor='none', alpha=0.95)
        ax.add_patch(plenum)

        # Difusores de aire (pequeños rectángulos horizontales en base del lecho)
        for i in range(6):
            x_diff = x_izq + 0.5 + i * (ancho - 1.0) / 5
            ax.add_patch(Rectangle((x_diff - 0.15, y_plenum_top - 0.15), 0.3, 0.08,
                                  facecolor='#555555', edgecolor='none'))

        # 2. Lecho de relleno (media biológica)
        y_lecho_bottom = y_plenum_top
        y_lecho_top = y_lecho_bottom + h_lecho
        lecho = Rectangle((x_izq + 0.1, y_lecho_bottom), ancho - 0.2, h_lecho,
                          facecolor=c_lecho, edgecolor='none', alpha=0.9)
        ax.add_patch(lecho)

        # Representación del relleno plástico modular (pequeños rectángulos apilados)
        np.random.seed(42)
        for _ in range(45):  # Muchos módulos para simular alta superficie específica
            cx = x_centro + np.random.uniform(-ancho/2 + 0.4, ancho/2 - 0.4)
            cy = y_lecho_bottom + np.random.uniform(0.2, h_lecho - 0.2)
            w = np.random.uniform(0.18, 0.28)
            h_mod = np.random.uniform(0.25, 0.35)
            ax.add_patch(Rectangle((cx - w/2, cy - h_mod/2), w, h_mod,
                                  facecolor='#6EBE8E', edgecolor='#4A8F6A', linewidth=0.6, alpha=0.85))

        # Biofilm (pequeños puntos verdes adheridos al relleno)
        for _ in range(35):
            cx = x_centro + np.random.uniform(-ancho/2 + 0.5, ancho/2 - 0.5)
            cy = y_lecho_bottom + np.random.uniform(0.3, h_lecho - 0.3)
            ax.add_patch(Circle((cx, cy), 0.04, facecolor='#2E8B57', edgecolor='none', alpha=0.7))

        # 3. Zona líquida + headspace + acumulación (sobre el lecho)
        y_liquido_bottom = y_lecho_top
        liquido = Rectangle((x_izq + 0.1, y_liquido_bottom), ancho - 0.2,
                            h_headspace + h_acumulacion,
                            facecolor=c_liquido, edgecolor='none', alpha=0.85)
        ax.add_patch(liquido)

        # 4. Bordo libre
        y_bordo_bottom = y_liquido_bottom + h_headspace + h_acumulacion
        bordo = Rectangle((x_izq + 0.1, y_bordo_bottom), ancho - 0.2, h_bordo,
                          facecolor=c_headspace, edgecolor='none', alpha=0.9)
        ax.add_patch(bordo)

        # === BURBUJAS DE AIRE (co-corriente ascendente a través del lecho) ===
        for _ in range(28):
            cx = x_centro + np.random.uniform(-ancho/2 + 0.6, ancho/2 - 0.6)
            cy_start = y_lecho_bottom + np.random.uniform(0.1, h_lecho * 0.8)
            cy = cy_start + np.random.uniform(0.4, h_lecho * 0.9)
            r = np.random.uniform(0.035, 0.085)
            ax.add_patch(Circle((cx, cy), r, facecolor=c_burbuja, edgecolor='none', alpha=0.65))

        # === FLECHAS DE FLUJO ===
        # Agua ascendente (up-flow)
        for fx in [x_centro - 1.1, x_centro, x_centro + 1.1]:
            ax.annotate('', xy=(fx, y_lecho_top + 0.4), 
                        xytext=(fx, y_plenum_top + 0.3),
                        arrowprops=dict(arrowstyle='->', color='#1565C0', lw=3.0, alpha=0.9))

        # Aire ascendente (co-corriente)
        ax.annotate('', xy=(x_centro + 0.8, y_lecho_top - 0.3), 
                    xytext=(x_centro + 0.8, y_plenum_top + 0.3),
                    arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=2.8, alpha=0.85))

        # Salida de efluente (derecha, nivel superior)
        y_salida = y_lecho_top + h_headspace * 0.6
        ax.plot([x_der, x_der + 1.2], [y_salida, y_salida], 'k-', linewidth=3)
        ax.annotate('', xy=(x_der + 1.1, y_salida), xytext=(x_der + 0.2, y_salida),
                    arrowprops=dict(arrowstyle='->', color='#1565C0', lw=3.5))

        # === ENTRADA Y AIREACIÓN ===
        # Entrada de afluente (izquierda, fondo plenum)
        y_entrada = y_bottom + 0.3
        ax.plot([x_izq - 1.6, x_izq], [y_entrada, y_entrada], 'k-', linewidth=3.5)
        ax.add_patch(Rectangle((x_izq - 0.35, y_entrada - 0.12), 0.7, 0.24,
                              facecolor=c_liquido, edgecolor='#555555'))
        ax.annotate('', xy=(x_izq, y_entrada), xytext=(x_izq - 1.3, y_entrada),
                    arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=3.5))

        # Entrada de aire (base, centro)
        y_aire = y_bottom + 0.15
        ax.plot([x_centro, x_centro], [y_bottom - 0.6, y_aire], 'k-', linewidth=3)
        ax.annotate('', xy=(x_centro, y_aire + 0.4), xytext=(x_centro, y_bottom - 0.4),
                    arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=3))

        # === LÍNEAS DIVISORIAS (punteadas) ===
        dash = dict(linestyle='--', color='#999999', linewidth=0.9, alpha=0.6)
        ax.axhline(y=y_plenum_top, xmin=0.18, xmax=0.82, **dash)
        ax.axhline(y=y_lecho_top, xmin=0.18, xmax=0.82, **dash)
        ax.axhline(y=y_lecho_top + h_headspace + h_acumulacion, xmin=0.18, xmax=0.82, **dash)

        # === LÍNEAS DE DIMENSIÓN VERTICALES (estilo UASB - alineadas) ===
        # Línea base vertical alineada para todas las cotas
        x_dim_base = x_izq - 2.0
        tick_long = 0.15
        
        def draw_cota(y1, y2, texto, align_right=True):
            """Dibuja una cota vertical con línea y texto alineado"""
            # Línea vertical principal
            ax.plot([x_dim_base, x_dim_base], [y1, y2], 'k-', linewidth=0.9)
            # Ticks horizontales en extremos
            ax.plot([x_dim_base - tick_long/2, x_dim_base + tick_long/2], [y1, y1], 'k-', linewidth=0.9)
            ax.plot([x_dim_base - tick_long/2, x_dim_base + tick_long/2], [y2, y2], 'k-', linewidth=0.9)
            # Texto alineado a la derecha de la línea
            if align_right:
                ax.text(x_dim_base - 0.15, (y1 + y2) / 2, texto, 
                       ha='right', va='center', fontsize=8, linespacing=0.9)

        # Cotas individuales (alineadas)
        draw_cota(y_bottom, y_plenum_top, f'{H_plenum:.2f} m\n(plenum)')
        draw_cota(y_plenum_top, y_lecho_top, f'{H_lecho:.2f} m\n(lecho)')
        draw_cota(y_lecho_top, y_lecho_top + h_headspace + h_acumulacion,
                  f'{H_headspace + H_acumulacion:.2f} m\n(headspace +\nacumulación)')
        draw_cota(y_lecho_top + h_headspace + h_acumulacion, y_top,
                  f'{H_bordo:.2f} m\n(bordo libre)')

        # Altura total (línea más externa, con ticks como las demás)
        x_dim_total = x_izq - 3.8
        ax.plot([x_dim_total, x_dim_total], [y_bottom, y_top], 'k-', linewidth=0.9)
        # Ticks horizontales en extremos (igual que cotas individuales)
        ax.plot([x_dim_total - tick_long/2, x_dim_total + tick_long/2], [y_bottom, y_bottom], 'k-', linewidth=0.9)
        ax.plot([x_dim_total - tick_long/2, x_dim_total + tick_long/2], [y_top, y_top], 'k-', linewidth=0.9)
        ax.text(x_dim_total - 0.15, (y_bottom + y_top) / 2,
                f'H = {H_total:.2f} m', ha='right', va='center',
                fontsize=9, fontweight='bold')

        # Diámetro (abajo) - con líneas verticales de marca
        y_dim_bottom = y_bottom - 0.9
        tick_vert = 0.15
        ax.plot([x_izq, x_der], [y_dim_bottom, y_dim_bottom], 'k-', linewidth=0.9)
        # Líneas verticales en los extremos
        ax.plot([x_izq, x_izq], [y_dim_bottom - tick_vert/2, y_dim_bottom + tick_vert/2], 'k-', linewidth=0.9)
        ax.plot([x_der, x_der], [y_dim_bottom - tick_vert/2, y_dim_bottom + tick_vert/2], 'k-', linewidth=0.9)
        ax.text(x_centro, y_dim_bottom - 0.35, f'Ø {D:.2f} m', ha='center', va='top',
                fontsize=9, fontweight='bold')

        # === ETIQUETAS TÉCNICAS ===
        offset_derecho = x_der + 0.8

        # Etiquetas de zonas (derecha)
        ax.text(offset_derecho + 0.5, y_lecho_top + (h_headspace + h_acumulacion) / 2,
                'Zona libre +\nacumulación\n(retrolavado)', ha='left', va='center', 
                fontsize=8, linespacing=0.9)
        ax.text(offset_derecho, y_lecho_bottom + h_lecho / 2,
                f'Lecho sumergido\nSAR = {SAR:.1f} m³/m²·h', ha='left', va='center',
                fontsize=9, fontweight='bold')
        ax.text(offset_derecho, (y_bottom + y_plenum_top) / 2,
                'Plenum +\ndifusores\naire + agua', ha='left', va='center', 
                fontsize=8, linespacing=0.9)
        
        # Etiquetas de flujos
        ax.text(x_izq - 1.0, y_entrada - 0.5, f'Afluente\n{Q_L_s:.1f} L/s',
                ha='center', va='top', fontsize=9, fontweight='bold', color='#2E7D32')
        ax.text(x_der + 1.4, y_salida + 0.5, 'Efluente\ntratado',
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1565C0')
        ax.text(x_centro + 0.3, y_top + 0.55, f'Aire\n{Q_aire:.1f} Nm³/h',
                ha='left', va='bottom', fontsize=9, fontweight='bold', color='#2E7D32')

        # Título
        ax.text(x_centro, y_top + 1.4, 'REACTOR BAF – Esquema de Funcionamiento',
                ha='center', va='bottom', fontsize=13, fontweight='bold')

        # Configuración final
        ax.set_xlim(x_izq - 4.2, x_der + 3.5)
        ax.set_ylim(y_bottom - 1.3, y_top + 2.0)
        ax.set_aspect('equal')
        ax.axis('off')

        # Guardar
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados', 'figuras')
        os.makedirs(output_dir, exist_ok=True)

        fig_path = os.path.join(output_dir, 'Esquema_BAF.png')
        fig.savefig(fig_path, dpi=220, bbox_inches='tight', facecolor='white', pad_inches=0.3)
        plt.close()

        return fig_path


# =============================================================================
# TEST DEL GENERADOR
# =============================================================================

if __name__ == "__main__":
    sys.path.insert(0, _base_dir)
    from ptar_dimensionamiento import ConfigDiseno, dimensionar_baf

    print("=" * 70)
    print("TEST - GENERADOR MODULAR DE BAF")
    print("=" * 70)

    cfg = ConfigDiseno()
    print(f"\n[1] Q_linea = {cfg.Q_linea_L_s} L/s")
    print(f"[1] T_agua = {cfg.T_agua_C} °C")
    print(f"[2] DBO entrada al BAF = {cfg.baf_DBO_entrada_mg_L} mg/L")

    print("\n" + "=" * 70)
    print("DIMENSIONAMIENTO BAF")
    print("=" * 70)

    baf = dimensionar_baf(cfg)
    print(f"[3] Dimensiones: D={baf['D_m']:.2f}m, H={baf['H_total_m']:.2f}m")
    print(f"[3] Volumen lecho: {baf['V_lecho_m3']:.2f} m³")
    print(f"[3] HLR: {baf['HLR_real_m3_m2_h']:.2f} m³/m²·h")
    print(f"[3] EBCT: {baf['EBCT_h']:.2f} h")
    print(f"[3] OLR: {baf['OLR_kgDBO_m3_d']:.2f} kg/m³·d")
    print(f"[3] Q_aire: {baf['Q_aire_Nm3_h']:.1f} Nm³/h")

    output_dir = os.path.join(_base_dir, 'resultados', 'test_modular')
    os.makedirs(output_dir, exist_ok=True)
    
    figuras_dir = os.path.join(output_dir, 'figuras')
    os.makedirs(figuras_dir, exist_ok=True)
    
    gen = GeneradorBAF(cfg, baf, ruta_figuras=figuras_dir)
    latex = gen.generar_completo()

    print(f"\n[4] LaTeX generado: {len(latex)} chars")

    tex_path = os.path.join(output_dir, 'baf_test.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    print(f"[5] Guardado en: {tex_path}")

    # Documento completo para prueba de compilación
    doc_completo = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish]{babel}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{booktabs,longtable,float}
\usepackage{caption}
\usepackage{graphicx}
\usepackage{geometry}
\geometry{margin=2.5cm}

\newcommand{\captionequation}[1]{\vspace{-0.5em}\caption*{#1}\vspace{0.5em}}

\begin{document}

""" + latex + r"""

\end{document}"""

    doc_path = os.path.join(output_dir, 'baf_test_completo.tex')
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(doc_completo)
    print(f"[6] Documento completo: {doc_path}")

    # Intentar compilar PDF
    import subprocess
    try:
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, doc_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            print(f"[7] PDF generado: {os.path.join(output_dir, 'baf_test_completo.pdf')}")
        else:
            print("[7] Error compilando PDF (ver log)")
    except Exception as e:
        print(f"[7] No se pudo compilar PDF: {e}")

    print("\n" + "=" * 70)
    print("TEST COMPLETADO")
    print("=" * 70)
