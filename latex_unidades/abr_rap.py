#!/usr/bin/env python3
"""
Generador LaTeX para Reactor Anaerobio con Pantallas (ABR / RAP)

Módulo de renderizado LaTeX para el Reactor Anaerobio con Pantallas,
también conocido como ABR (Anaerobic Baffled Reactor). Este reactor es
un sistema de tratamiento biológico anaerobio de aguas residuales que
opera mediante flujo a través de una serie de compartimentos separados
por pantallas o tabiques verticales (bafles).

Estructura del módulo:
    - 3 subsections: Dimensionamiento, Verificación, Resultados
    - Esquema gráfico matplotlib opcional (vista longitudinal)
    - Texto técnico completo basado en manual_ABR_RAP.txt
    - Tabla de resultados con longtable

Nomenclatura:
    ABR = Anaerobic Baffled Reactor (término internacional)
    RAP = Reactor Anaerobio con Pantallas (término hispanohablante/OPS-OMS)
    Ambos términos son sinónimos exactos en el contexto de este proyecto.
"""

import os
from typing import Dict, Any


class GeneradorABR_RAP:
    """
    Generador LaTeX para unidad Reactor ABR/RAP.
    
    Genera tres subsections:
        1. Dimensionamiento: teoría, principio de funcionamiento, cálculos
        2. Verificación: verificaciones hidráulicas y geométricas
        3. Resultados: tabla consolidada con parámetros de diseño
    """
    
    def __init__(self, cfg, datos: Dict[str, Any], ruta_figuras: str = 'figuras'):
        """
        Inicializa el generador ABR/RAP.
        
        Args:
            cfg: Configuración del proyecto (ConfigDiseno)
            datos: Resultados del dimensionamiento ABR de ptar_dimensionamiento.py
            ruta_figuras: Ruta base para figuras (no usada en fase 1)
        """
        self.cfg = cfg
        self.datos = datos
        self.ruta_figuras = ruta_figuras
    
    def generar_completo(self) -> str:
        """Genera todo el contenido LaTeX del ABR en 3 subsections."""
        return "\n\n".join([
            self.generar_dimensionamiento(),
            self.generar_verificacion(),
            self.generar_resultados()
        ])
    
    def generar_dimensionamiento(self) -> str:
        """
        Genera subsection Dimensionamiento con teoría y cálculos.
        
        Incluye:
            - Explicación técnica narrativa del ABR/RAP
            - Principio de funcionamiento por compartimentos
            - Papel de las pantallas o bafles
            - Mecanismos de remoción anaerobia
            - Criterios de diseño adoptados
            - Desarrollo de ecuaciones de dimensionamiento
        """
        cfg = self.cfg
        a = self.datos
        
        # Extraer valores con acceso directo (sin .get() con fallback)
        n_comp = a["n_compartimentos"]
        TRH_h = a["TRH_diseno_h"]
        v_up_diseno = a["v_up_diseno_m_h"]
        H_util = a["H_util_m"]
        
        return rf"""\subsection{{Dimensionamiento}}

\textbf{{Nomenclatura del reactor:}} En la literatura técnica internacional, el reactor objeto de este manual se denomina ABR (\textit{{Anaerobic Baffled Reactor}}). En la literatura hispanohablante y en particular en los manuales de la OPS/OMS para saneamiento en países de desarrollo, se utiliza con frecuencia la sigla RAP (Reactor Anaerobio con Pantallas), que traduce literalmente el mismo concepto. Este documento adopta la denominación ABR como nombre principal del documento y del módulo de cálculo, por ser el término de uso universal en la bibliografía técnica de referencia. La sigla RAP se utiliza en paralelo en los títulos y encabezados del documento —de ahí la denominación compuesta "ABR / RAP"— con el fin de garantizar la trazabilidad con los manuales de la OPS/OMS que sirven de referencia complementaria en este proyecto.

\textbf{{¿Qué es un Reactor Anaerobio con Pantallas (ABR / RAP)?}}

El Reactor Anaerobio con Pantallas —ABR por sus siglas en inglés— es un sistema de tratamiento biológico anaerobio de aguas residuales que opera mediante flujo a través de una serie de compartimentos separados por pantallas o tabiques verticales (bafles). El agua residual entra por un extremo del reactor y recorre, en serie, cada uno de los compartimentos hasta llegar al extremo opuesto donde descarga el efluente tratado. En cada compartimento, el flujo sigue un patrón alternado de ascenso y descenso determinado por la posición y configuración de las pantallas.

El ABR fue desarrollado y descrito formalmente por McCarty y colaboradores en la Universidad de Stanford (Bachmann et al., 1985) como una evolución simplificada de los reactores anaerobios de lecho de lodos. Su gran ventaja conceptual sobre el reactor UASB (\textit{{Upflow Anaerobic Sludge Blanket}}) es la ausencia de un separador trifásico: la retención de la biomasa se logra por medios puramente hidráulicos y gravitacionales, aprovechando el hecho de que el flujo ascendente en cada compartimento es suficientemente lento como para mantener el manto de lodos en posición estable.

El ABR ocupa una posición intermedia entre el tanque séptico y el UASB en cuanto a complejidad constructiva y eficiencia de tratamiento. Es más eficiente que el tanque séptico porque el tratamiento ocurre en múltiples etapas en serie, cada una con su propia comunidad microbiana especializada. Es más simple que el UASB porque no requiere el separador trifásico, que es el componente más costoso y delicado de ese reactor. Esta combinación de buena eficiencia y simplicidad constructiva lo convierte en una opción especialmente adecuada para sistemas de saneamiento descentralizados, comunidades rurales y pequeñas cabeceras parroquiales en países de ingresos medios y bajos.

\textbf{{Rol en el tren de tratamiento del proyecto:}}

En el presente proyecto, el ABR se diseña como unidad de tratamiento primario anaerobio, situada aguas abajo del pretratamiento (cribado y desarenado) y aguas arriba de las unidades de tratamiento complementario o secundario. Su función principal es la remoción de materia orgánica en condiciones anaerobias, la estabilización parcial de los sólidos sedimentables y la acumulación y digestión \textit{{in situ}} de los lodos generados.

En la configuración típica del proyecto, el ABR reemplaza o complementa al tanque séptico convencional en situaciones donde se requiere un mayor nivel de remoción de DBO y DQO en la etapa anaerobia, con mayor control del proceso y sin la necesidad de un sistema mecánico de aireación. El efluente del ABR puede destinarse a un campo de infiltración, a un humedal de flujo subsuperficial, a un filtro anaerobio de flujo ascendente (FAFA) o, según el nivel de tratamiento requerido, a una etapa de tratamiento aerobio posterior (biofiltro, lodos activados, etc.).

\textbf{{Principio de funcionamiento por compartimentos:}}

El ABR es un reactor rectangular dividido internamente en una serie de compartimentos por medio de tabiques o pantallas verticales. Los tabiques no llegan completamente al fondo ni completamente a la superficie: dejan aberturas alternadas para forzar el recorrido del agua a través de toda la altura de cada compartimento.

En la configuración adoptada en este proyecto, los tabiques tienen una abertura en la parte inferior. El agua entra por el primer compartimento por el fondo, sube a través de él, desborda por encima del tabique intermedio o pasa por una abertura superior, desciende hasta el fondo del segundo compartimento, vuelve a subir, y así sucesivamente hasta el último compartimento. Este patrón de flujo ascendente-descendente garantiza que el agua atraviese toda la profundidad del manto de lodos en cada compartimento, maximizando el contacto entre el sustrato y la biomasa.

\textbf{{Retención de biomasa sin separador trifásico:}}

La clave del funcionamiento del ABR es la velocidad ascensional relativamente baja en el interior de cada compartimento. El manto de lodos anaerobio se mantiene en posición porque la velocidad ascendente del flujo no es suficiente para arrastrar los gránulos o flóculos de lodo hacia el compartimento siguiente. Esta retención es fundamentalmente diferente a la del UASB, donde se requiere un separador trifásico para capturar los sólidos que el flujo ascendente tiende a arrastrar hacia la superficie: en el ABR, la propia geometría del sistema asegura que la velocidad ascensional se mantenga por debajo del umbral de arrastre del lodo, sin necesidad de separadores mecánicos adicionales.

La consecuencia práctica es que en el ABR cada compartimento acumula su propia población microbiana, y esa población se adapta progresivamente a la calidad del agua que recibe: el primer compartimento, que recibe el agua cruda más concentrada, contiene predominantemente bacterias hidrolíticas y acidogénicas; los compartimentos intermedios tienen una mezcla de acidogénicos y acetogénicos; y el último compartimento, que recibe un agua ya considerablemente tratada, tiene condiciones más propicias para los metanogénicos. Esta separación funcional a lo largo del reactor es uno de los factores que explican la robustez del ABR frente a variaciones de carga.

\textbf{{Mecanismos principales de remoción:}}

Los mecanismos de remoción en el ABR son los propios del tratamiento anaerobio en cuatro etapas clásicas:

\textit{{Hidrólisis:}} Las moléculas orgánicas complejas (proteínas, grasas, hidratos de carbono) son fraccionadas en monómeros y dímeros por enzimas extracelulares producidas por las bacterias hidrolíticas. Esta etapa es generalmente la limitante del proceso para residuales con alta concentración de sólidos particulados.

\textit{{Acidogénesis:}} Los productos de la hidrólisis son fermentados por bacterias acidogénicas a ácidos grasos volátiles (AGV), alcoholes, dióxido de carbono e hidrógeno. Esta etapa es generalmente rápida en comparación con la hidrólisis y con la metanogénesis.

\textit{{Acetogénesis:}} Los ácidos grasos volátiles de cadena corta (propionato, butirato) son convertidos a acetato, CO$_2$ e H$_2$ por bacterias acetogénicas. Esta etapa es termodinámicamente desfavorable a concentraciones altas de H$_2$ y solo ocurre de forma eficiente cuando el hidrógeno es consumido rápidamente por organismos hidrogenotróficos (sintrofía obligada).

\textit{{Metanogénesis:}} El acetato y el H$_2$/CO$_2$ son convertidos a metano y CO$_2$ por las arqueas metanogénicas. Esta etapa es la más sensible a variaciones de pH y temperatura, y la que limita la tasa global del proceso cuando el sistema está correctamente operado.

Adicionalmente, en el ABR ocurre sedimentación de sólidos suspendidos por efecto de la reducción de velocidad dentro de cada compartimento: los sólidos gruesos que no se degradan rápidamente sedimentan en el fondo del primer compartimento o de los primeros compartimentos, donde se acumulan y se digieren lentamente. Esta función es análoga a la del tanque séptico, pero con la ventaja de que el tratamiento biológico activo ocurre en paralelo y de forma mucho más eficiente.

\textbf{{Criterios de diseño adoptados por el proyecto:}}

Los siguientes parámetros han sido seleccionados como criterios de diseño para el reactor ABR, basados en la bibliografía técnica y adaptados a las condiciones del proyecto:

\begin{{table}}[H]
\centering
\caption{{Parámetros seleccionados para el diseño ABR / RAP}}
\begin{{tabular}}{{p{{6cm}}cc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Valor adoptado}} & \textbf{{Rango recomendado}} \\
\midrule
Tiempo de retención hidráulico (TRH) & {TRH_h:.0f} h & 24--72 h \\
Número de compartimentos ($n$) & {n_comp} & 2--8 (recomendado: 4--6) \\
Velocidad ascensional de diseño ($v_{{up}}$) & {v_up_diseno:.1f} m/h & 0,2--1,5 m/h \\
Profundidad útil del líquido ($H$) & {H_util:.1f} m & 1,5--3,0 m \\
Zona de acumulación de lodos & {a["H_zona_lodos_m"]:.2f} m & 0,2--0,5 m \\
Bordo libre & {a["H_bordo_m"]:.2f} m & $\geq$ 0,30 m \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textit{{Nota: Estos valores son criterios adoptados por el proyecto basados en Barber \& Stuckey (1999), Foxon et al. (2004) y OPS/OMS (2005). No son límites normativos impuestos por la TULSMA ni por normas ecuatorianas específicas para reactores anaerobios.}}

\textbf{{Ecuaciones de dimensionamiento:}}

El dimensionamiento del ABR se fundamenta en el criterio del tiempo de retención hidráulico (TRH) y en la verificación de la velocidad ascensional. Las ecuaciones fundamentales son las siguientes:

\textbf{{[Ecuación 1] Volumen total del reactor:}}

\begin{{equation}}
V_{{total}} = Q_{{medio}} \times TRH
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$V_{{total}}$] = Volumen total del reactor (m³)
    \item[$Q_{{medio}}$] = Caudal medio diario de diseño ({a["Q_m3_d"]:.1f} m³/d = {a["Q_m3_h"]:.2f} m³/h)
    \item[$TRH$] = Tiempo de retención hidráulico adoptado ({TRH_h:.0f} h = {TRH_h/24:.2f} d)
\end{{itemize}}

Sustituyendo los valores del proyecto:

\begin{{equation}}
V_{{total}} = {a["Q_m3_d"]:.1f} \times {TRH_h/24:.3f} = {a["V_total_m3"]:.1f} \text{{ m}}^3
\end{{equation}}

\textbf{{[Ecuación 2] Volumen por compartimento:}}

\begin{{equation}}
V_{{comp}} = \frac{{V_{{total}}}}{{n}} = \frac{{{a["V_total_m3"]:.1f}}}{{{n_comp}}} = {a["V_comp_m3"]:.2f} \text{{ m}}^3
\end{{equation}}

\textbf{{[Ecuación 3] Área de sección transversal por velocidad ascensional:}}

La velocidad ascensional es el parámetro crítico que controla la retención de la biomasa en el reactor. Para que el ABR funcione correctamente, la velocidad ascensional debe ser inferior a la velocidad de sedimentación de los flóculos de lodo.

\begin{{equation}}
A_{{transversal}} = \frac{{Q_{{medio}}}}{{v_{{up, dise\tilde{{n}}o}}}} = \frac{{{a["Q_m3_h"]:.2f}}}{{{v_up_diseno:.1f}}} = {a["A_transversal_m2"]:.2f} \text{{ m}}^2
\end{{equation}}

\textbf{{[Ecuación 4] Dimensiones del reactor:}}

A partir del área de sección transversal y la profundidad útil adoptada, se obtienen las dimensiones geométricas:

\begin{{equation}}
W = \frac{{A_{{transversal}}}}{{H}} = \frac{{{a["A_transversal_m2"]:.2f}}}{{{H_util:.1f}}} = {a["W_m"]:.2f} \text{{ m}} \quad \text{{(ancho)}}
\end{{equation}}

\begin{{equation}}
L_{{comp}} = \frac{{V_{{comp}}}}{{W \times H}} = \frac{{{a["V_comp_m3"]:.2f}}}{{{a["W_m"]:.2f} \times {H_util:.1f}}} = {a["L_comp_m"]:.2f} \text{{ m}} \quad \text{{(largo por compartimento)}}
\end{{equation}}

\begin{{equation}}
L_{{total}} = n \times L_{{comp}} = {n_comp} \times {a["L_comp_m"]:.2f} = {a["L_total_m"]:.2f} \text{{ m}} \quad \text{{(largo total)}}
\end{{equation}}

La profundidad total de construcción incluye la profundidad útil del líquido, la zona de acumulación de lodos y el bordo libre:

\begin{{equation}}
H_{{total}} = H + H_{{lodos}} + H_{{bordo}} = {H_util:.1f} + {a["H_zona_lodos_m"]:.2f} + {a["H_bordo_m"]:.2f} = {a["H_total_m"]:.2f} \text{{ m}}
\end{{equation}}

\textbf{{[Ecuación 5] Altura de abertura en los bafles (slot inferior):}}

Cada pantalla o bafle interno no ocupa toda la altura del compartimento: deja una abertura en su parte inferior (slot) por la que el flujo debe pasar antes de ascender en el compartimento siguiente. La altura de este slot es un parámetro de diseño que determina la velocidad puntual del flujo en la transición entre compartimentos. Según OPS/OMS (2005) y Foxon et al. (2004), esta abertura se define como una fracción de la profundidad útil, típicamente entre el 15\,\% y el 25\,\% de $H$. Adoptando el valor central de la bibliografía ($f_{{slot}} = 0.20$):

\begin{{equation}}
h_{{slot}} = f_{{slot}} \times H = 0.20 \times {H_util:.1f} = {0.20 * a["H_util_m"]:.2f} \text{{ m}}
\end{{equation}}

\textbf{{[Ecuación 6] Velocidad en la abertura de los bafles:}}

La velocidad del flujo al atravesar la abertura inferior de cada bafle (\textit{{slot velocity}}) es significativamente mayor que la velocidad ascensional media del compartimento, porque el área de paso queda reducida a $W \times h_{{slot}}$. Este parámetro es crítico: un valor excesivo genera turbulencia local en el fondo del compartimento siguiente, resuspende los lodos sedimentados y puede provocar su arrastre hacia el efluente. La bibliografía recomienda mantener esta velocidad por debajo de 1.0~m/h a caudal medio:

\begin{{equation}}
v_{{slot}} = \frac{{Q_{{medio}}}}{{W \times h_{{slot}}}} = \frac{{{a["Q_m3_h"]:.3f}}}{{{a["W_m"]:.2f} \times {0.20 * a["H_util_m"]:.2f}}} = {a["Q_m3_h"] / (a["W_m"] * 0.20 * a["H_util_m"]):.2f} \text{{ m/h}}
\end{{equation}}

\textbf{{Limitaciones del método actual:}}

El presente dimensionamiento cubre el cálculo del volumen total, número y tamaño de compartimentos, geometría del reactor, verificaciones hidráulicas y parámetros de carga. No cubre, en esta versión del cálculo: el modelado de la eficiencia de remoción de DBO en función del TRH (que requeriría un modelo cinético calibrado), el cálculo de la producción de biogás, el diseño del sistema de ventilación del biogás, el balance detallado de lodos en estado estacionario, ni el dimensionamiento de tuberías de entrada, salida y extracción de lodos."""

    def generar_verificacion(self) -> str:
        """
        Genera subsection Verificación con verificaciones hidráulicas y geométricas.

        Verificaciones obligatorias:
            V-1: Rango bibliográfico de velocidad ascensional de diseño (reformulada)
            V-2: Velocidad ascensional a caudal máximo (pico)
            V-3: TRH verificado por geometría
            V-4: Largo mínimo de compartimento (criterio dual constructivo+bibliográfico)
            V-5: Velocidad en abertura de bafle (slot velocity) — NUEVA
            V-6: Relación profundidad/ancho (H/W) — NUEVA
        Verificaciones complementarias:
            V-7: Relación L_comp/W
            V-8: Número de compartimentos mínimo
        Parámetros informativos:
            V-9: Carga orgánica volumétrica (COV) con explicación de unidades
            V-10: Estimación de producción de lodos y frecuencia de purga — NUEVA
        """
        cfg = self.cfg
        a = self.datos
        verifs = a["verificaciones"]

        # Extraer estados de verificaciones existentes
        v_up_max   = verifs["v_up_max"]
        TRH        = verifs["TRH"]
        L_comp     = verifs["L_comp"]
        relacion_LW = verifs["relacion_LW"]
        n_comp     = verifs["n_comp"]

        # --- Calcular verificaciones nuevas localmente ---

        # V-5: Velocidad en abertura de bafle (slot velocity)
        # La abertura inferior de cada bafle es el 20 % de H_util
        # según OPS/OMS (2005) y Foxon et al. (2004): f_slot = 0.20 (rango 0.15-0.25)
        f_slot      = 0.20
        h_slot      = f_slot * a["H_util_m"]
        v_slot_med  = a["Q_m3_h"] / (a["W_m"] * h_slot)
        v_slot_max  = a["Q_max_m3_h"] / (a["W_m"] * h_slot)
        v_slot_lim  = 1.0   # m/h, límite bibliográfico para caudal medio
        v_slot_ok   = v_slot_med <= v_slot_lim
        v_slot_est  = "CUMPLE" if v_slot_ok else "NO CUMPLE"

        # V-6: Relación H/W
        HW_ratio     = a["H_util_m"] / a["W_m"]
        HW_min, HW_max = 0.5, 2.0
        HW_ok        = HW_min <= HW_ratio <= HW_max
        HW_est       = "CUMPLE" if HW_ok else "NO CUMPLE"

        # V-1: verificar que v_up_diseno esté dentro del rango bibliográfico
        v_up_dis = a["v_up_diseno_m_h"]
        v_up_rango_ok = 0.2 <= v_up_dis <= 1.5
        v_up_rango_est = "CUMPLE" if v_up_rango_ok else "NO CUMPLE"

        # V-4 criterio dual
        L_comp_min = max(a["H_util_m"], 1.0)
        L_comp_ok  = a["L_comp_m"] >= L_comp_min

        # V-10: Estimación producción de lodos (OPS/OMS 2005, Capítulo 6)
        # Y_obs ≈ 0.10 kg SSV / kg DBO removida (digestión anaerobia doméstica)
        # eta_ref = 75 % eficiencia de referencia bibliográfica
        eta_ref    = 0.75
        Y_obs      = 0.10
        DBO_rem    = eta_ref * a["DBO_entrada_mg_L"] * a["Q_m3_d"] / 1000.0  # kg DBO/d
        P_lodos    = Y_obs * DBO_rem  # kg SSV/d
        densidad_lodos  = 1040.0   # kg/m³ (lodos anaerobios espesados)
        vol_lodos_anual = P_lodos * 365.0 / densidad_lodos  # m³/año
        vol_zona_lodos  = a["L_total_m"] * a["W_m"] * a["H_zona_lodos_m"]
        # meses hasta llenado al 80 % de la zona de lodos:
        meses_purga = (vol_zona_lodos * 0.80 / vol_lodos_anual) * 12.0

        # --- Generar resumen local de verificaciones obligatorias ---
        checks = [
            ("V-1 Rango v\\_up diseño",          v_up_rango_ok,
             f'{v_up_dis:.1f} m/h $\\in$ [0.2--1.5] m/h'),
            ("V-2 v\\_up caudal máximo",          v_up_max["estado"] == "CUMPLE",
             f'{a["v_up_max_calc_m_h"]:.2f} m/h $\\leq$ {cfg.abr_v_up_max_admisible_m_h:.1f} m/h'),
            ("V-3 TRH verificado",                TRH["estado"] == "CUMPLE",
             f'{a["TRH_calc_h"]:.1f} h $\\geq$ {a["TRH_diseno_h"]:.0f} h'),
            ("V-4 Largo mínimo compartimento",    L_comp_ok,
             f'L\\_comp = {a["L_comp_m"]:.2f} m $\\geq$ {L_comp_min:.1f} m'),
            ("V-5 Velocidad abertura bafle",      v_slot_ok,
             f'{v_slot_med:.2f} m/h $\\leq$ {v_slot_lim:.1f} m/h'),
            ("V-6 Relación H/W",                  HW_ok,
             f'{HW_ratio:.2f} $\\in$ [{HW_min:.1f}--{HW_max:.1f}]'),
        ]
        filas_resumen = " \\\\\n".join(
            rf"{nombre} & {'\\checkmark' if ok else '\\texttimes'} & {detalle}"
            for nombre, ok, detalle in checks
        ) + " \\\\"
        todas_ok = all(ok for _, ok, _ in checks)
        if todas_ok:
            estado_general_str = r"Todas las verificaciones obligatorias \textbf{CUMPLEN}."
        else:
            fallidas = [n for n, ok, _ in checks if not ok]
            estado_general_str = (
                r"\textbf{ATENCIÓN:} las siguientes verificaciones NO cumplen y requieren "
                r"revisión del diseño: " + ", ".join(fallidas) + "."
            )

        return rf"""\subsection{{Verificación}}

La subsección de verificación evalúa de forma sistemática si el reactor dimensionado satisface los criterios hidráulicos y geométricos de la bibliografía de referencia. Para cada verificación se describe primero el fenómeno físico que la motiva, después se desarrolla el cálculo con los valores del proyecto y, finalmente, se emite el juicio de cumplimiento. Se distinguen verificaciones \textbf{{obligatorias}} ---cuyo incumplimiento invalida el diseño--- de \textbf{{complementarias}} ---que orientan sobre la calidad del diseño sin invalidarlo--- y de \textbf{{parámetros informativos}} ---que no tienen criterio de cumplimiento en este nivel de diseño---.

\textbf{{Verificaciones obligatorias:}}

\textbf{{[V-1] Rango bibliográfico de la velocidad ascensional de diseño}}

El primer parámetro que debe justificarse es la propia elección de la velocidad ascensional de diseño $v_{{up,dise\tilde{{n}}o}} = {v_up_dis:.1f}$~m/h. Este valor no es un resultado del cálculo sino una decisión del proyectista: determina el área transversal del reactor (Ecuación~3) y, a través de ella, todas las demás dimensiones geométricas. Su validez depende de que se encuentre dentro del rango operativo aceptable reportado en la bibliografía técnica.

Las razones de este límite son físicas: velocidades demasiado altas generan shear suficiente para arrastrar los flóculos de lodo anaerobio hacia el efluente, empobreciendo progresivamente la biomasa activa del reactor; velocidades demasiado bajas producen reactores sobredimensionados sin mejora proporcional en la eficiencia biológica, pues el limitante del proceso pasa a ser la cinética de la metanogénesis y no el tiempo de contacto. Según Foxon et al. (2004) y Barber \& Stuckey (1999), el rango operativo aceptable para aguas residuales domésticas a temperatura ambiente es:

\begin{{equation}}
0.2 \text{{ m/h}} \leq v_{{up,dise\tilde{{n}}o}} \leq 1.5 \text{{ m/h}}
\end{{equation}}

El valor adoptado en este proyecto es $v_{{up,dise\tilde{{n}}o}} = {v_up_dis:.1f}$~m/h.

\textit{{Nota importante sobre la verificación de la velocidad a caudal medio:}} la velocidad ascensional calculada a caudal medio ($v_{{up,calc}} = Q_{{medio}} / (W \times H)$) coincide por construcción con $v_{{up,dise\tilde{{n}}o}}$, puesto que el ancho $W$ se obtuvo directamente como $W = Q_{{medio}} / (v_{{up,dise\tilde{{n}}o}} \times H)$. No existe por tanto una verificación numérica independiente a caudal medio: la verificación real y crítica de la velocidad ascensional es la del caudal pico (V-2), que sí puede superar el límite admisible.

Estado V-1: \textbf{{{v_up_rango_est}}} ($0.2 \leq {v_up_dis:.1f} \leq 1.5$~m/h)

\textbf{{[V-2] Velocidad ascensional a caudal máximo horario}}

Esta es la verificación hidráulica más crítica del diseño. Durante los picos de consumo ---generalmente en las mañanas y mediodías en sistemas domésticos--- el caudal supera al medio en un factor de pico $f_p$. Si en esas condiciones la velocidad ascensional rebasa el umbral de arrastre, la biomasa abandona el reactor con el efluente y el rendimiento de depuración se deteriora progresivamente. A diferencia del UASB, el ABR carece de separador trifásico que retenga los sólidos en esas condiciones: la única salvaguarda es que la geometría garantice una velocidad admisible incluso en pico.

El caudal pico horario se obtiene aplicando el factor de pico al caudal medio de diseño:

\begin{{equation}}
Q_{{max}} = f_p \times Q_{{medio}} = {a["factor_pico"]:.1f} \times {a["Q_m3_h"]:.3f} = {a["Q_max_m3_h"]:.3f} \text{{ m}}^3\text{{/h}}
\end{{equation}}

Con este caudal, la velocidad ascensional en pico resulta:

\begin{{equation}}
v_{{up,max}} = \frac{{Q_{{max}}}}{{W \times H}} = \frac{{{a["Q_max_m3_h"]:.3f}}}{{{a["W_m"]:.2f} \times {a["H_util_m"]:.1f}}} = {a["v_up_max_calc_m_h"]:.2f} \text{{ m/h}}
\end{{equation}}

El límite bibliográfico para caudal pico, según Barber \& Stuckey (1999), es de {cfg.abr_v_up_max_admisible_m_h:.1f}~m/h. Por encima de este umbral se ha observado exportación significativa de sólidos hacia el efluente en reactores piloto y a escala real.

Criterio: $v_{{up,max}} \leq {cfg.abr_v_up_max_admisible_m_h:.1f}$~m/h

Estado V-2: \textbf{{{v_up_max["estado"]}}} ({a["v_up_max_calc_m_h"]:.2f}~m/h ${"\\leq" if v_up_max["estado"] == "CUMPLE" else ">"}$ {cfg.abr_v_up_max_admisible_m_h:.1f}~m/h)

\textbf{{[V-3] Verificación del tiempo de retención hidráulico por geometría}}

El TRH de diseño fija el volumen total del reactor (Ecuación~1). Sin embargo, las dimensiones finales resultan de una cadena de operaciones aritméticas ---división por área, multiplicación por número de compartimentos--- que en la práctica pueden ajustarse a valores constructivos enteros. Esta verificación confirma que el volumen efectivo de la geometría adoptada reproduce, o supera, el TRH de diseño. Si el TRH calculado resultara inferior al de diseño, significaría que las dimensiones son insuficientes y que el tiempo de contacto nominal no se alcanzaría en la práctica.

\begin{{equation}}
TRH_{{calc}} = \frac{{L_{{total}} \times W \times H_{{util}}}}{{Q_{{medio}}}} \times 24 = \frac{{{a["L_total_m"]:.2f} \times {a["W_m"]:.2f} \times {a["H_util_m"]:.1f}}}{{{a["Q_m3_d"]:.1f}}} \times 24 = {a["TRH_calc_h"]:.1f} \text{{ h}}
\end{{equation}}

Criterio: $TRH_{{calc}} \geq {a["TRH_diseno_h"]:.0f}$~h

Estado V-3: \textbf{{{TRH["estado"]}}} ({a["TRH_calc_h"]:.1f}~h ${"\\geq" if TRH["estado"] == "CUMPLE" else "<"}$ {a["TRH_diseno_h"]:.0f}~h)

\textbf{{[V-4] Largo mínimo de compartimento}}

El largo de cada compartimento ($L_{{comp}}$) debe satisfacer dos criterios independientes que responden a razones diferentes. El criterio constructivo establece un mínimo absoluto de 1.0~m: por debajo de esta dimensión el compartimento es impracticable desde el punto de vista de la ejecución de obra, la inspección y la extracción de lodos. El criterio hidráulico-bibliográfico, según OPS/OMS (2005), establece que $L_{{comp}} \geq H_{{util}}$: esta condición garantiza que el recorrido horizontal del flujo sea suficiente para que los sólidos gruesos no degradados sedimenten antes de alcanzar el bafle siguiente, evitando cortocircuitos hidráulicos. Ambos criterios deben cumplirse simultáneamente, por lo que el largo mínimo efectivo es el mayor de los dos valores:

\begin{{equation}}
L_{{comp,min}} = \max\!\left(H_{{util}},\; 1.0\right) = \max\!\left({a["H_util_m"]:.1f},\; 1.0\right) = {L_comp_min:.1f} \text{{ m}}
\end{{equation}}

Valor calculado: $L_{{comp}} = {a["L_comp_m"]:.2f}$~m

Estado V-4: \textbf{{{L_comp["estado"]}}} ($L_{{comp}} = {a["L_comp_m"]:.2f}$~m ${"\\geq" if L_comp_ok else "<"}$ {L_comp_min:.1f}~m)

\textbf{{[V-5] Velocidad en la abertura inferior de los bafles (\textit{{slot velocity}})}}

Cada pantalla interna del ABR deja una abertura en su parte inferior (denominada \textit{{slot}} en la bibliografía anglosajona) a través de la cual el flujo pasa de un compartimento al siguiente antes de ascender. Dado que el área de esta abertura ($W \times h_{{slot}}$) es sustancialmente menor que el área transversal total del compartimento ($W \times H$), la velocidad puntual del flujo en el slot es notablemente mayor que la velocidad ascensional media.

Esta aceleración local tiene dos efectos negativos cuando supera el umbral admisible: primero, genera turbulencia en el fondo del compartimento receptor, resuspendiendo los flóculos de lodo ya sedimentados; segundo, puede crear zonas de mezcla intensa que cortocircuitan la separación funcional entre compartimentos, que es uno de los fundamentos del buen rendimiento del ABR. OPS/OMS (2005) y Foxon et al. (2004) recomiendan definir la abertura como el 20\,\% de la profundidad útil ($f_{{slot}} = 0.20$) y mantener la velocidad en el slot por debajo de 1.0~m/h a caudal medio:

\begin{{equation}}
h_{{slot}} = f_{{slot}} \times H_{{util}} = 0.20 \times {a["H_util_m"]:.1f} = {h_slot:.2f} \text{{ m}}
\end{{equation}}

La velocidad en la abertura a caudal medio resulta:

\begin{{equation}}
v_{{slot}} = \frac{{Q_{{medio}}}}{{W \times h_{{slot}}}} = \frac{{{a["Q_m3_h"]:.3f}}}{{{a["W_m"]:.2f} \times {h_slot:.2f}}} = {v_slot_med:.2f} \text{{ m/h}}
\end{{equation}}

A modo informativo, a caudal máximo:

\begin{{equation}}
v_{{slot,max}} = \frac{{Q_{{max}}}}{{W \times h_{{slot}}}} = \frac{{{a["Q_max_m3_h"]:.3f}}}{{{a["W_m"]:.2f} \times {h_slot:.2f}}} = {v_slot_max:.2f} \text{{ m/h}}
\end{{equation}}

Criterio: $v_{{slot}} \leq {v_slot_lim:.1f}$~m/h (caudal medio)

Estado V-5: \textbf{{{v_slot_est}}} ({v_slot_med:.2f}~m/h ${"\\leq" if v_slot_ok else ">"}$ {v_slot_lim:.1f}~m/h)

\textbf{{[V-6] Relación profundidad útil / ancho del reactor ($H/W$)}}

La relación $H/W$ describe la forma de la sección transversal de cada compartimento. Su importancia es reconocida en la bibliografía reciente (Sinha et al., 2009): valores extremos en cualquier sentido comprometen la uniformidad del flujo vertical ascendente. Un reactor excesivamente ancho en relación con su profundidad ($H/W < 0.5$) tiende a tener distribución no uniforme del flujo en el plano transversal, con zonas muertas en los extremos laterales donde la velocidad ascensional es insuficiente para mantener el manto de lodos en suspensión activa. Por el contrario, un reactor excesivamente estrecho ($H/W > 2.0$) dificulta la distribución uniforme del afluente en el ancho y puede crear flujos preferenciales en la zona central que reducen el contacto efectivo entre el sustrato y la biomasa. El rango recomendado es:

\begin{{equation}}
0.5 \leq \frac{{H_{{util}}}}{{W}} \leq 2.0
\end{{equation}}

El valor calculado para este diseño es:

\begin{{equation}}
\frac{{H_{{util}}}}{{W}} = \frac{{{a["H_util_m"]:.1f}}}{{{a["W_m"]:.2f}}} = {HW_ratio:.2f}
\end{{equation}}

Estado V-6: \textbf{{{HW_est}}} ($0.5 \leq {HW_ratio:.2f} \leq 2.0$)

\textbf{{Verificaciones complementarias:}}

\textbf{{[V-7] Relación largo / ancho del compartimento ($L_{{comp}} / W$)}}

La relación $L_{{comp}} / W$ describe la esbeltez en planta de cada compartimento. Compartimentos muy alargados ($L_{{comp}} / W > {cfg.abr_relacion_Lcomp_W_max:.1f}$) pueden presentar distribución no uniforme del afluente a lo largo del ancho; compartimentos muy cuadrados o anchos ($L_{{comp}} / W < {cfg.abr_relacion_Lcomp_W_min:.1f}$) tienden hacia un comportamiento de mezcla completa en el plano horizontal, reduciendo la eficiencia de la separación en serie entre compartimentos. El rango orientativo recomendado por la OPS/OMS (2005) es:

\begin{{equation}}
{cfg.abr_relacion_Lcomp_W_min:.1f} \leq \frac{{L_{{comp}}}}{{W}} \leq {cfg.abr_relacion_Lcomp_W_max:.1f}
\end{{equation}}

Valor calculado: $L_{{comp}} / W = {a["L_comp_m"]:.2f} / {a["W_m"]:.2f} = {relacion_LW["valor"]:.2f}$

Estado V-7: \textbf{{{relacion_LW["estado"]}}} (verificación complementaria)

\textbf{{[V-8] Número mínimo de compartimentos}}

El número de compartimentos determina el grado de separación funcional entre las fases del proceso anaerobio. Con un solo compartimento el ABR no tiene ventaja sobre un digestor de mezcla completa. A partir de cuatro compartimentos se logra una separación razonablemente clara entre las comunidades hidrolítico-acidogénicas (primer y segundo compartimento) y las metanogénicas (últimos compartimentos). La OPS/OMS (2005) establece un mínimo de {cfg.abr_num_compartimentos_min} compartimentos para aplicaciones de saneamiento doméstico descentralizado:

\begin{{equation}}
n \geq {cfg.abr_num_compartimentos_min}
\end{{equation}}

Valor adoptado: $n = {n_comp["valor"]}$

Estado V-8: \textbf{{{n_comp["estado"]}}}

\textbf{{Parámetros informativos:}}

\textbf{{[V-9] Carga orgánica volumétrica (COV)}}

La carga orgánica volumétrica expresa la cantidad de materia orgánica que ingresa por unidad de volumen y por día. Es el parámetro de referencia más utilizado en la bibliografía de reactores anaerobios para comparar diseños y evaluar si el reactor opera en un régimen compatible con el mantenimiento de una biomasa estable. No constituye un criterio obligatorio en este diseño, pero permite situar el proyecto en el contexto de experiencias reportadas.

La DBO se expresa en mg/L, unidad equivalente a g/m³; dividirla entre 1\,000 convierte g a kg. La expresión completa con sus unidades explícitas es:

\begin{{equation}}
COV = \frac{{Q_{{medio}} \,[\text{{m}}^3/\text{{d}}] \times DBO_{{entrada}} \,[\text{{g/m}}^3] \,/\, 1\,000}}{{V_{{total}} \,[\text{{m}}^3]}} = \frac{{{a["Q_m3_d"]:.1f} \times {a["DBO_entrada_mg_L"]:.0f} / 1\,000}}{{{a["V_total_m3"]:.1f}}} = {a["COV_kgDBO_m3_d"]:.2f} \text{{ kg\,DBO/(m}}^3\!\cdot\!\text{{d)}}
\end{{equation}}

Rango bibliográfico para ABR doméstico a temperatura ambiente: {cfg.abr_COV_referencial_min:.1f}--{cfg.abr_COV_referencial_max:.1f}~kg\,DBO/(m³·d) (Barber \& Stuckey, 1999; OPS/OMS, 2005).

\textbf{{[V-10] Estimación de la producción de lodos y frecuencia de purga}}

La zona de acumulación de lodos reservada en el dimensionamiento ($H_{{lodos}} = {a["H_zona_lodos_m"]:.2f}$~m) debe ser coherente con la tasa real de producción de biomasa anaerobia en el reactor. Sin esta comprobación, el espacio reservado para lodos es solo un criterio empírico desconectado de las condiciones reales del proyecto. La OPS/OMS (2005, Capítulo~6) proporciona la siguiente expresión para una estimación de orden de magnitud:

\begin{{equation}}
P_{{lodos}} = Y_{{obs}} \times DBO_{{rem}}
\end{{equation}}

Donde $Y_{{obs}} \approx 0.10$~kg\,SSV/kg\,DBO\,removida es el rendimiento observado en digestión anaerobia mesofílica de aguas residuales domésticas (Rittmann \& McCarty, 2001), y $DBO_{{rem}}$ es la DBO removida diariamente. Adoptando la eficiencia de referencia bibliográfica del 75\,\%:

\begin{{equation}}
DBO_{{rem}} = \eta_{{ref}} \times DBO_{{entrada}} \times \frac{{Q_{{medio}}}}{{1\,000}} = 0.75 \times {a["DBO_entrada_mg_L"]:.0f} \times \frac{{{a["Q_m3_d"]:.1f}}}{{1\,000}} = {DBO_rem:.2f} \text{{ kg\,DBO/d}}
\end{{equation}}

\begin{{equation}}
P_{{lodos}} = 0.10 \times {DBO_rem:.2f} = {P_lodos:.2f} \text{{ kg\,SSV/d}}
\end{{equation}}

Adoptando una densidad de lodos húmedos anaerobios espesados de $\rho = 1\,040$~kg/m³, el volumen acumulado anualmente es:

\begin{{equation}}
V_{{lodos,año}} = \frac{{P_{{lodos}} \times 365}}{{\rho}} = \frac{{{P_lodos:.2f} \times 365}}{{1\,040}} = {vol_lodos_anual:.2f} \text{{ m}}^3\text{{/año}}
\end{{equation}}

El volumen disponible en la zona de lodos del reactor es:

\begin{{equation}}
V_{{zona\,lodos}} = L_{{total}} \times W \times H_{{lodos}} = {a["L_total_m"]:.2f} \times {a["W_m"]:.2f} \times {a["H_zona_lodos_m"]:.2f} = {vol_zona_lodos:.2f} \text{{ m}}^3
\end{{equation}}

Esto implica una frecuencia indicativa de purga de lodos de aproximadamente \textbf{{{meses_purga:.0f} meses}}, asumiendo extracción cuando la zona de acumulación alcanza el 80\,\% de su capacidad. Este valor es una estimación de orden de magnitud y deberá ajustarse en la puesta en marcha del sistema en función de las mediciones reales de producción de lodos.

\textbf{{Resumen de verificaciones:}}

\begin{{table}}[H]
\centering
\caption{{Resumen de verificaciones del reactor ABR / RAP}}
\begin{{tabular}}{{llp{{5.5cm}}}}
\toprule
\textbf{{Verificación}} & \textbf{{Estado}} & \textbf{{Valor calculado vs. criterio}} \\
\midrule
{filas_resumen}
\bottomrule
\end{{tabular}}
\end{{table}}

{estado_general_str}

\textit{{Notas: (a) El proyecto NO calcula la eficiencia de remoción de DBO a partir de parámetros operacionales. Las eficiencias del 70--95\,\% reportadas en la bibliografía para ABR con TRH de {a["TRH_diseno_h"]:.0f}~h son referencias y no predicciones garantizadas. (b) La estimación de producción de lodos (V-10) adopta una eficiencia de referencia del 75\,\%; el valor real dependerá de las condiciones de operación.}}"""

    def generar_resultados(self, incluir_esquema: bool = True) -> str:
        """
        Genera subsection Resultados con tabla consolidada y figura opcional.
        
        Args:
            incluir_esquema: Si True, genera e incluye el esquema matplotlib
        
        Returns:
            String LaTeX con la subsection Resultados completa
        """
        import warnings
        
        cfg = self.cfg
        a = self.datos
        
        # Determinar estado general
        estado_general = "ACEPTABLE" if a["todas_verificaciones_cumplen"] else "REQUIERE REVISIÓN"
        
        # Generar figura si se solicita
        figura_latex = ""
        figura_generada = False
        if incluir_esquema:
            try:
                # Generar esquema matplotlib
                if os.path.isabs(self.ruta_figuras):
                    output_dir = self.ruta_figuras
                    ruta_completa = os.path.join(self.ruta_figuras, 'Esquema_ABR.png')
                    latex_ruta_figura = ruta_completa.replace('\\', '/')
                else:
                    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados', self.ruta_figuras)
                    latex_ruta_figura = self.ruta_figuras + '/Esquema_ABR.png'
                
                self.generar_esquema_matplotlib(output_dir)
                figura_latex = rf"""\begin{{figure}}[H]
\centering
\includegraphics[width=0.95\textwidth]{{{latex_ruta_figura}}}
\caption{{Esquema del Reactor Anaerobio con Pantallas (ABR / RAP) -- vista longitudinal}}
\label{{fig:esquema_abr}}
\end{{figure}}

"""
                figura_generada = True
            except Exception as e:
                figura_generada = False
                warnings.warn(f"[ABR] No se pudo generar el esquema matplotlib: {e}", RuntimeWarning)
        
        # Texto descriptivo condicional
        if figura_generada:
            texto_esquema = "El esquema muestra la configuración típica del ABR con flujo en zigzag (\\textit{up-flow} y \\textit{down-flow}) a través de los compartimentos, las pantallas internas (\\textit{baffles}) que dirigen el flujo, las zonas de lodos, líquida y biogás, así como los puntos de entrada, salida y ventilación."
        else:
            texto_esquema = "La configuración del reactor consiste en una serie de compartimentos rectangulares con flujo en zigzag (\\textit{up-flow} y \\textit{down-flow}) dirigido por pantallas internas (\\textit{baffles}), con zonas de lodos, líquida y biogás."
        
        return rf"""\subsection{{Resultados}}

{figura_latex}El dimensionamiento del Reactor Anaerobio con Pantallas (ABR / RAP) ha producido las siguientes dimensiones y parámetros de operación:

{texto_esquema}

\begin{{longtable}}{{p{{6cm}}p{{3cm}}p{{5cm}}}}
\caption{{Resultados del dimensionamiento ABR / RAP}} \\
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} & \textbf{{Observación}} \\
\midrule
\endfirsthead
\multicolumn{{3}}{{c}}{{
    {{\bfseries \tablename\ \thetable{{}} -- continuación de la página anterior}}
}} \\
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} & \textbf{{Observación}} \\
\midrule
\endhead
\midrule
\multicolumn{{3}}{{r}}{{Continúa en la siguiente página...}} \\
\endfoot
\bottomrule
\endlastfoot

\multicolumn{{3}}{{l}}{{\textit{{Parámetros de entrada:}}}} \\
Caudal medio ($Q_{{medio}}$) & {a["Q_m3_d"]:.1f} m³/d & Caudal por línea de tratamiento \\
Caudal máximo ($Q_{{max}}$) & {a["Q_max_m3_d"]:.1f} m³/d & Factor pico: {a["factor_pico"]:.1f} \\
DBO afluente & {a["DBO_entrada_mg_L"]:.0f} mg/L & Caracterización afluente \\
\midrule

\multicolumn{{3}}{{l}}{{\textit{{Criterios de diseño adoptados:}}}} \\
Tiempo retención hidráulico (TRH) & {a["TRH_diseno_h"]:.0f} h & Criterio del proyecto \\
Número de compartimentos ($n$) & {a["n_compartimentos"]} & {cfg.abr_num_compartimentos_recomendado}--{cfg.abr_num_compartimentos_max} recomendado \\
Velocidad ascensional diseño & {a["v_up_diseno_m_h"]:.1f} m/h & $\leq$ {cfg.abr_v_up_max_admisible_m_h:.1f} m/h límite pico \\
Profundidad útil ($H$) & {a["H_util_m"]:.1f} m & {cfg.abr_profundidad_min_m:.1f}--{cfg.abr_profundidad_max_m:.1f} m rango \\
\midrule

\multicolumn{{3}}{{l}}{{\textit{{Dimensiones geométricas:}}}} \\
Volumen total ($V_{{total}}$) & {a["V_total_m3"]:.1f} m³ & Calculado por TRH \\
Volumen por compartimento & {a["V_comp_m3"]:.2f} m³ & Distribución uniforme \\
Área sección transversal & {a["A_transversal_m2"]:.2f} m² & Por velocidad ascensional \\
Ancho del reactor ($W$) & {a["W_m"]:.2f} m & Geometría transversal \\
Largo por compartimento & {a["L_comp_m"]:.2f} m & $L_{{comp}} \geq H$ verificado \\
Largo total ($L_{{total}}$) & {a["L_total_m"]:.2f} m & $n \times L_{{comp}}$ \\
Profundidad total construcción & {a["H_total_m"]:.2f} m & $H + H_{{lodos}} + H_{{bordo}}$ \\
Área en planta total & {a["A_planta_m2"]:.2f} m² & $L_{{total}} \times W$ \\
\midrule

\multicolumn{{3}}{{l}}{{\textit{{Parámetros hidráulicos:}}}} \\
Velocidad ascensional (caudal medio) & {a["v_up_calc_m_h"]:.2f} m/h & {a["verificaciones"]["v_up_medio"]["estado"]} \\
Velocidad ascensional (caudal máximo) & {a["v_up_max_calc_m_h"]:.2f} m/h & {a["verificaciones"]["v_up_max"]["estado"]} \\
TRH calculado & {a["TRH_calc_h"]:.1f} h & {a["verificaciones"]["TRH"]["estado"]} \\
Carga hidráulica superficial (CHS) & {a["CHS_m_d"]:.2f} m/d & Parámetro informativo \\
\midrule

\multicolumn{{3}}{{l}}{{\textit{{Parámetros de proceso (informativos):}}}} \\
Carga orgánica volumétrica (COV) & {a["COV_kgDBO_m3_d"]:.2f} kg/m³·d & Rango ref: {cfg.abr_COV_referencial_min:.1f}--{cfg.abr_COV_referencial_max:.1f} \\
\midrule

\multicolumn{{3}}{{l}}{{\textit{{Estado de verificaciones:}}}} \\
Verificación velocidad (medio) & {a["verificaciones"]["v_up_medio"]["estado"]} & Criterio: $\leq$ {cfg.abr_v_up_diseno_m_h:.1f} m/h \\
Verificación velocidad (máx) & {a["verificaciones"]["v_up_max"]["estado"]} & Criterio: $\leq$ {cfg.abr_v_up_max_admisible_m_h:.1f} m/h \\
Verificación TRH & {a["verificaciones"]["TRH"]["estado"]} & Criterio: $\geq$ {a["TRH_diseno_h"]:.0f} h \\
Verificación largo comp. & {a["verificaciones"]["L_comp"]["estado"]} & Criterio: $L_{{comp}} \geq H$ \\
\bottomrule
\multicolumn{{3}}{{l}}{{\textbf{{Estado general del diseño:}} \textbf{{{estado_general}}}}} \\
\end{{longtable}}

\textbf{{Notas sobre los resultados:}}

El reactor ABR / RAP dimensionado consta de {a["n_compartimentos"]} compartimentos idénticos con una geometría rectangular de {a["L_total_m"]:.2f}~m de largo total, {a["W_m"]:.2f}~m de ancho y {a["H_total_m"]:.2f}~m de profundidad total de construcción. La profundidad útil del líquido es de {a["H_util_m"]:.1f}~m, con una zona adicional de {a["H_zona_lodos_m"]:.2f}~m reservada para acumulación de lodos y {a["H_bordo_m"]:.2f}~m de bordo libre.

El diseño opera con una velocidad ascensional de {a["v_up_calc_m_h"]:.2f}~m/h a caudal medio, valor que se eleva hasta {a["v_up_max_calc_m_h"]:.2f}~m/h durante los picos de caudal. Ambos valores se mantienen dentro de los límites establecidos para la retención efectiva de la biomasa anaerobia sin requerir separador trifásico.

El tiempo de retención hidráulico de {a["TRH_calc_h"]:.1f}~h ({a["TRH_calc_h"]/24:.2f}~días) proporciona el tiempo de contacto necesario entre el agua residual y la biomasa anaerobia para la degradación de la materia orgánica. Este valor se encuentra dentro del rango recomendado de 24--72 horas para reactores ABR tratando aguas residuales domésticas.

\textbf{{Alcance y limitaciones declaradas:}}

Este dimensionamiento cubre el volumen del reactor, la geometría básica y las verificaciones hidráulicas fundamentales. No incluye: (a) predicción de la eficiencia de remoción de DBO o DQO mediante modelos cinéticos; (b) cálculo de la producción de biogás ni dimensionamiento del sistema de ventilación; (c) balance detallado de producción de lodos y frecuencia de extracción; (d) diseño de las pantallas internas (altura, espesor, configuración de aberturas); (e) dimensionamiento de tuberías de entrada, salida y extracción de lodos. Estos elementos constituyen extensiones futuras del diseño que deben desarrollarse según las condiciones específicas del proyecto."""

    def generar_esquema_matplotlib(self, output_dir=None):
        """
        Genera un esquema técnico del reactor ABR (Reactor Anaerobio de Pantallas / RAP)
        en vista longitudinal (sección transversal a lo largo del flujo).
        Basado en el estilo y calidad visual del esquema UASB, pero adaptado a la geometría
        rectangular y flujo en zigzag del ABR (compartimentos up-flow / down-flow).
        Usa los valores calculados en dimensionar_abr_rap() sin fallbacks.
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Circle, FancyArrowPatch
        import numpy as np
        import os
        import warnings

        resultados_abr = self.datos

        try:
            # Extraer valores calculados (exactos del dimensionamiento ABR)
            L_total = resultados_abr['L_total_m']
            W = resultados_abr['W_m']
            H_total = resultados_abr['H_total_construccion_m']
            H_lodos = resultados_abr['H_zona_lodos_m']
            H_liquida = resultados_abr['H_zona_liquida_m']
            H_biogas = resultados_abr['H_zona_biogas_m']
            H_bordo = resultados_abr['H_bordo_libre_m']
            N_comp = resultados_abr['num_compartimentos']
            L_comp = L_total / N_comp
            Vup = resultados_abr['Vup_m_h']
            TRH = resultados_abr['TRH_h']
            Q_L_s = resultados_abr['Q_m3_h'] * 1000 / 3600
        except KeyError as e:
            warnings.warn(f"[ABR] Falta clave en datos para esquema: {e}", RuntimeWarning)
            raise

        # Proporciones del esquema (horizontal, amplio como referencia ABR)
        ancho_visual = 14.0          # Longitud visual del reactor (unidades de plot)
        altura_visual = 6.5          # Altura visual total
        escala_x = ancho_visual / L_total
        escala_y = altura_visual / H_total

        # Coordenadas base
        x_izq = 1.0
        y_base = 1.0
        x_der = x_izq + ancho_visual

        # Alturas escaladas
        h_lodos = H_lodos * escala_y
        h_liquida = H_liquida * escala_y
        h_biogas = H_biogas * escala_y
        h_bordo = H_bordo * escala_y
        h_total_util = h_lodos + h_liquida + h_biogas

        # Crear figura (horizontal, amplia)
        fig, ax = plt.subplots(figsize=(16, 8))

        # Colores consistentes con esquema UASB (suaves, técnicos)
        c_lodos = '#D4A574'          # Marrón lodo
        c_liquido = '#E8F0F5'        # Azul pálido
        c_biogas = '#E8F5E9'         # Verde pálido
        c_baffle = '#555555'         # Gris oscuro para pantallas
        c_flecha = '#1565C0'         # Azul flujo

        # === CUERPO PRINCIPAL DEL REACTOR ===
        reactor = FancyBboxPatch((x_izq, y_base), ancho_visual, h_total_util + h_bordo,
                                 boxstyle="round,pad=0.2", facecolor='white',
                                 edgecolor='#333333', linewidth=3)
        ax.add_patch(reactor)

        # === ZONAS INTERNAS POR COMPARTIMENTO ===
        for i in range(N_comp):
            x_comp_izq = x_izq + i * (L_comp * escala_x)
            x_comp_der = x_comp_izq + (L_comp * escala_x)

            # 1. Zona de lodos (fondo de cada compartimento up-flow)
            lodos = Rectangle((x_comp_izq + 0.15, y_base), 
                             L_comp * escala_x - 0.3, h_lodos,
                             facecolor=c_lodos, edgecolor='none', alpha=0.95)
            ax.add_patch(lodos)

            # Gránulos / flóculos de lodo (pequeños círculos marrones)
            np.random.seed(42 + i)
            for _ in range(12):
                cx = x_comp_izq + np.random.uniform(0.4, L_comp * escala_x - 0.4)
                cy = y_base + np.random.uniform(0.1, h_lodos - 0.2)
                r = np.random.uniform(0.06, 0.11)
                ax.add_patch(Circle((cx, cy), r, facecolor='#B8956A', edgecolor='#8B5A2B', alpha=0.85))

            # 2. Zona líquida (sobre lodos)
            liquido = Rectangle((x_comp_izq + 0.15, y_base + h_lodos), 
                               L_comp * escala_x - 0.3, h_liquida,
                               facecolor=c_liquido, edgecolor='none', alpha=0.85)
            ax.add_patch(liquido)

            # 3. Zona de biogás / headspace
            biogas_zone = Rectangle((x_comp_izq + 0.15, y_base + h_lodos + h_liquida), 
                                   L_comp * escala_x - 0.3, h_biogas,
                                   facecolor=c_biogas, edgecolor='none', alpha=0.75)
            ax.add_patch(biogas_zone)

            # Burbujas de biogás (pequeñas en headspace)
            for _ in range(6):
                cx = x_comp_izq + np.random.uniform(0.5, L_comp * escala_x - 0.5)
                cy = y_base + h_lodos + h_liquida + np.random.uniform(0.1, h_biogas - 0.15)
                r = np.random.uniform(0.04, 0.08)
                ax.add_patch(Circle((cx, cy), r, facecolor='#81C784', edgecolor='#4CAF50', alpha=0.7))

        # === PANTALLAS / BAFFLES (configuración estándar ABR: alternando hanging y standing) ===
        baffle_grosor = 0.18
        gap_abajo = 0.18 * escala_y          # Gap inferior típico ~15-20% altura
        gap_arriba = 0.22 * escala_y         # Gap superior

        for i in range(1, N_comp):
            x_baffle = x_izq + i * (L_comp * escala_x) - baffle_grosor / 2

            if i % 2 == 1:  # Baffle hanging (desde techo, gap abajo) → down-flow previo
                # Hanging baffle (vertical desde arriba)
                baffle_h = Rectangle((x_baffle, y_base + h_lodos + h_liquida + h_biogas - gap_abajo),
                                     baffle_grosor, h_total_util + h_bordo - (h_lodos + h_liquida + h_biogas - gap_abajo),
                                     facecolor=c_baffle, edgecolor='#222222', linewidth=1.5)
                ax.add_patch(baffle_h)
                # Indicador de gap inferior (flecha down-flow)
                ax.annotate('', xy=(x_baffle + baffle_grosor/2, y_base + h_lodos * 0.6),
                           xytext=(x_baffle + baffle_grosor/2, y_base + h_lodos + 0.3),
                           arrowprops=dict(arrowstyle='->', color=c_flecha, lw=2.2, shrinkA=0, shrinkB=0))

            else:  # Baffle standing (desde fondo, gap arriba) → up-flow
                # Standing baffle (vertical desde abajo)
                baffle_s = Rectangle((x_baffle, y_base),
                                     baffle_grosor, H_total * escala_y - gap_arriba,
                                     facecolor=c_baffle, edgecolor='#222222', linewidth=1.5)
                ax.add_patch(baffle_s)
                # Indicador de gap superior (flecha over-flow)
                ax.annotate('', xy=(x_baffle + baffle_grosor/2, y_base + h_total_util - 0.2),
                           xytext=(x_baffle + baffle_grosor/2, y_base + h_total_util + 0.4),
                           arrowprops=dict(arrowstyle='->', color=c_flecha, lw=2.2))

        # === FLECHAS DE FLUJO EN ZIGZAG (up-flow / down-flow) ===
        for i in range(N_comp):
            x_comp_centro = x_izq + (i * L_comp + L_comp / 2) * escala_x
            # Up-flow en compartimento
            ax.annotate('', xy=(x_comp_centro, y_base + h_lodos + h_liquida * 0.9),
                       xytext=(x_comp_centro, y_base + h_lodos * 0.1),
                       arrowprops=dict(arrowstyle='->', color=c_flecha, lw=2.8, alpha=0.9))
            # Conexión down-flow entre compartimentos (curva simple)
            if i < N_comp - 1:
                x_next = x_izq + ((i + 1) * L_comp) * escala_x
                ax.plot([x_comp_centro + 0.4, x_next - 0.8],
                        [y_base + h_lodos + h_liquida * 0.9, y_base + h_lodos + h_liquida * 0.9],
                        color=c_flecha, lw=1.8, linestyle='--', alpha=0.7)
                ax.annotate('', xy=(x_next - 0.6, y_base + h_lodos + h_liquida * 0.9),
                           xytext=(x_comp_centro + 0.6, y_base + h_lodos + h_liquida * 0.9),
                           arrowprops=dict(arrowstyle='->', color=c_flecha, lw=2.5))

        # === ENTRADA Y SALIDA ===
        # Entrada (izquierda, fondo)
        y_entrada = y_base + 0.4
        ax.plot([x_izq - 1.8, x_izq], [y_entrada, y_entrada], 'k-', linewidth=3.5)
        ax.add_patch(Rectangle((x_izq - 0.3, y_entrada - 0.12), 0.6, 0.24,
                              facecolor='#E8F0F5', edgecolor='#333333'))
        ax.annotate('', xy=(x_izq, y_entrada), xytext=(x_izq - 1.4, y_entrada),
                    arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=3.5))

        # Salida (derecha, nivel líquido)
        y_salida = y_base + h_lodos + h_liquida * 0.65
        ax.plot([x_der, x_der + 1.8], [y_salida, y_salida], 'k-', linewidth=3)
        ax.add_patch(Rectangle((x_der + 0.1, y_salida - 0.12), 0.4, 0.24,
                              facecolor=c_liquido, edgecolor='#333333'))
        ax.annotate('', xy=(x_der + 1.6, y_salida), xytext=(x_der + 0.3, y_salida),
                    arrowprops=dict(arrowstyle='->', color='#1565C0', lw=3.5))

        # Salida de biogás (arriba, múltiples puntos o colector central)
        y_chim = y_base + h_total_util + h_bordo + 0.3
        for i in [0.25, 0.5, 0.75]:
            x_chim = x_izq + ancho_visual * i
            ax.plot([x_chim, x_chim], [y_base + h_total_util + h_bordo - 0.1, y_chim], 'k-', linewidth=2.2)
        ax.add_patch(Rectangle((x_izq + ancho_visual * 0.4, y_chim - 0.15), ancho_visual * 0.2, 0.3,
                              facecolor='#E0E0E0', edgecolor='#333333'))
        ax.annotate('', xy=(x_izq + ancho_visual * 0.5, y_chim + 0.4),
                    xytext=(x_izq + ancho_visual * 0.5, y_chim - 0.1),
                    arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=2.5))

        # === LÍNEAS DIVISORIAS Y DIMENSIONES ===
        # Líneas horizontales divisorias (punteadas)
        dash = dict(linestyle='--', color='#777777', linewidth=0.9, alpha=0.6)
        ax.axhline(y=y_base + h_lodos, xmin=0.08, xmax=0.92, **dash)
        ax.axhline(y=y_base + h_lodos + h_liquida, xmin=0.08, xmax=0.92, **dash)
        ax.axhline(y=y_base + h_lodos + h_liquida + h_biogas, xmin=0.08, xmax=0.92, **dash)

        # Dimensiones verticales (izquierda)
        x_dim_izq = x_izq - 2.2
        def draw_dim_line(y1, y2, label):
            ax.plot([x_dim_izq, x_dim_izq], [y1, y2], 'k-', linewidth=0.9)
            ax.plot([x_dim_izq - 0.12, x_dim_izq + 0.12], [y1, y1], 'k-', linewidth=0.9)
            ax.plot([x_dim_izq - 0.12, x_dim_izq + 0.12], [y2, y2], 'k-', linewidth=0.9)
            ax.text(x_dim_izq - 0.3, (y1 + y2) / 2, label, ha='right', va='center', fontsize=9)

        draw_dim_line(y_base, y_base + h_lodos, f'{H_lodos:.1f} m\n(zona lodos)')
        draw_dim_line(y_base + h_lodos, y_base + h_lodos + h_liquida, f'{H_liquida:.1f} m\n(zona líquida)')
        draw_dim_line(y_base + h_lodos + h_liquida, y_base + h_lodos + h_liquida + h_biogas, f'{H_biogas:.1f} m\n(biogás)')
        draw_dim_line(y_base + h_lodos + h_liquida + h_biogas, y_base + h_total_util + h_bordo, f'{H_bordo:.1f} m\n(bordo libre)')
        # Altura total completa
        ax.plot([x_dim_izq - 1.1, x_dim_izq - 1.1], [y_base, y_base + h_total_util + h_bordo], 'k-', linewidth=1.1)
        ax.text(x_dim_izq - 1.4, (y_base + h_total_util + h_bordo) / 2,
                f'H = {H_total:.1f} m', ha='right', va='center', fontsize=10, fontweight='bold')

        # Dimensión horizontal (abajo)
        y_dim_abajo = y_base - 1.1
        ax.plot([x_izq, x_der], [y_dim_abajo, y_dim_abajo], 'k-', linewidth=1.0)
        ax.text(x_izq + ancho_visual / 2, y_dim_abajo - 0.45,
                f'L = {L_total:.0f} m  ({N_comp} comp. × {L_comp:.1f} m)', ha='center', va='top', fontsize=10, fontweight='bold')

        # === ETIQUETAS TÉCNICAS ===
        offset_derecho = x_der + 0.6
        y_etiqueta_base = y_base + h_total_util / 2

        ax.text(offset_derecho, y_etiqueta_base + 1.8, 'Zona de biogás\nrecolección CH₄', ha='left', va='center', fontsize=9)
        ax.text(offset_derecho, y_etiqueta_base + 0.4, f'Zona líquida\nvup = {Vup:.2f} m/h', ha='left', va='center', fontsize=9, fontweight='bold')
        ax.text(offset_derecho, y_etiqueta_base - 1.2, f'Zona de lodos\nTRH = {TRH:.0f} h', ha='left', va='center', fontsize=9, fontweight='bold')
        ax.text(offset_derecho - 1.2, y_base - 0.6, f'Afluente\n{Q_L_s:.1f} L/s', ha='center', va='top', fontsize=10, fontweight='bold', color='#2E7D32')
        ax.text(x_der + 1.9, y_salida + 0.3, 'Efluente\ntratado', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1565C0')

        # Título
        ax.text(x_izq + ancho_visual / 2, y_base + h_total_util + h_bordo + 1.1,
                'REACTOR ABR / RAP – Esquema de Funcionamiento', ha='center', va='bottom',
                fontsize=13, fontweight='bold')

        # Configuración final
        ax.set_xlim(x_izq - 3.5, x_der + 4.0)
        ax.set_ylim(y_base - 1.8, y_base + h_total_util + h_bordo + 2.2)
        ax.set_aspect('equal')
        ax.axis('off')

        # Guardar
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados', 'figuras')
        os.makedirs(output_dir, exist_ok=True)

        fig_path = os.path.join(output_dir, 'Esquema_ABR.png')
        fig.savefig(fig_path, dpi=220, bbox_inches='tight', facecolor='white', pad_inches=0.3)
        plt.close()

        return fig_path


def _formatear_numero(valor: float, decimales: int = 2) -> str:
    """Formatea número para LaTeX (coma decimal)."""
    if valor is None:
        return "--"
    fmt = f"{{:,.{decimales}f}}"
    resultado = fmt.format(valor)
    return resultado.replace(",", "\\,").replace(".", ",")


# =============================================================================
# MAIN - PRUEBA DEL MÓDULO
# =============================================================================

if __name__ == "__main__":
    """
    Prueba del generador ABR / RAP.
    
    Ejecutar desde línea de comandos:
        python latex_unidades/abr_rap.py
    
    Genera:
        - Esquema matplotlib: resultados/figuras/Esquema_ABR.png
        - Código LaTeX: resultados/test_modular/abr_test.tex
        - PDF compilado: resultados/test_modular/abr_test.pdf (si pdflatex disponible)
    """
    import sys
    import os
    import subprocess
    
    print("=" * 60)
    print("TEST GENERADOR ABR / RAP")
    print("=" * 60)
    
    # Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    
    print("[1] Importando módulos...")
    from ptar_dimensionamiento import ConfigDiseno, dimensionar_abr_rap
    
    print("[2] Ejecutando dimensionamiento ABR...")
    cfg = ConfigDiseno()
    resultados = dimensionar_abr_rap(cfg)
    
    print(f"    Volumen total: {resultados['V_total_m3']:.1f} m³")
    print(f"    Largo total: {resultados['L_total_m']:.1f} m")
    print(f"    Ancho: {resultados['W_m']:.1f} m")
    print(f"    Compartimentos: {resultados['num_compartimentos']}")
    print(f"    Velocidad ascensional: {resultados['Vup_m_h']:.2f} m/h")
    print(f"    TRH: {resultados['TRH_h']:.1f} h")
    print(f"    Verificaciones cumplen: {resultados['todas_verificaciones_cumplen']}")
    
    # Directorios
    resultados_dir = os.path.join(parent_dir, 'resultados', 'test_modular')
    figuras_dir = os.path.join(parent_dir, 'resultados', 'figuras')
    os.makedirs(resultados_dir, exist_ok=True)
    os.makedirs(figuras_dir, exist_ok=True)
    
    print("[3] Generando LaTeX...")
    # Usar ruta relativa correcta para el PDF (../figuras/ desde test_modular/)
    gen = GeneradorABR_RAP(cfg, resultados, ruta_figuras='../figuras')
    latex = gen.generar_completo()
    
    print(f"    Código LaTeX generado: {len(latex)} caracteres")
    
    tex_path = os.path.join(resultados_dir, 'abr_test.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
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

\newcommand{\captionequation}[1]{}

\begin{document}

\section{Reactor ABR / RAP}

""" + latex + r"""

\end{document}""")
    
    print(f"    Archivo LaTeX: {tex_path}")
    
    # Generar esquema matplotlib
    print("[4] Generando esquema matplotlib...")
    try:
        fig_path = gen.generar_esquema_matplotlib(figuras_dir)
        print(f"    Esquema PNG: {fig_path}")
    except Exception as e:
        print(f"    ERROR generando esquema: {e}")
    
    # Compilar PDF
    print("[5] Compilando PDF...")
    try:
        subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', resultados_dir, tex_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        pdf_path = os.path.join(resultados_dir, 'abr_test.pdf')
        if os.path.exists(pdf_path):
            print(f"    PDF generado: {pdf_path}")
    except Exception as e:
        print(f"    ERROR compilando PDF: {e}")
    
    print("=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
