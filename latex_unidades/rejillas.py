#!/usr/bin/env python3
"""
GENERADOR LaTeX - UNIDAD: REJILLAS

Contenido copiado directamente de generar_latex_A.py (lineas 279-394)
Organizado en 3 secciones grandes: Teoria, Verificacion, Resultados
"""

import os
import sys

# Ajustar path para imports (funciona como modulo y como script)
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _base_dir not in sys.path:
    sys.path.insert(0, _base_dir)

from latex_unidades.base import GeneradorUnidadBase


class GeneradorRejillas(GeneradorUnidadBase):
    """Generador LaTeX para Rejillas - contenido de A organizado en 3 secciones grandes.

    Args:
        cfg: Configuracion de diseno
        datos: Resultados del dimensionamiento
        ruta_figuras: Ruta base donde se guardan las figuras (default: 'figuras')
                       Puede ser ruta relativa al .tex o absoluta
    """

    def __init__(self, cfg, datos, ruta_figuras='figuras'):
        super().__init__(cfg, datos)
        self.ruta_figuras = ruta_figuras

    @property
    def identificador(self) -> str:
        return "rejillas"

    @property
    def titulo(self) -> str:
        return "Canal de Desbaste con Rejillas"
    
    def generar_completo(self, incluir_titulo: bool = True) -> str:
        """Genera las 3 subsections: Teoria, Verificacion, Resultados."""
        partes = [
            self.generar_descripcion(),
            self.generar_parametros(),
            self.generar_dimensionamiento(),
            self.generar_verificacion(),
            self.generar_resultados()
        ]
        return "\n\n".join(partes)

    @property
    def titulo_corto(self) -> str:
        return "Rejillas"

    def generar_descripcion(self) -> str:
        """SECCION 1: Dimensionamiento - Contiene descripcion, parametros y dimensionamiento."""
        cfg = self.cfg
        r = self.datos
        v_canal = cfg.rejillas_v_canal_m_s
        h_tirante = cfg.rejillas_h_tirante_m
        beta = cfg.rejillas_beta
        ancho_minimo_constructivo_m = r['ancho_minimo_constructivo_m']
        hL_criterio_cm = r['hL_criterio_m'] * 100

        return rf"""\subsection{{Dimensionamiento}}

Las rejillas constituyen la primera barrera de proteccion del sistema, reteniendo solidos gruesos como plasticos, ramas y papel que podrian danar equipos o causar obstrucciones en tuberias aguas abajo. El diseno hidraulico de esta unidad debe garantizar velocidades suficientes para arrastrar solidos sedimentables, pero no tan elevadas que dificulten el paso del agua a traves de las barras.

Segun los criterios establecidos por Metcalf y Eddy \cite{{metcalf2014}}, las velocidades de diseno en canales con rejillas deben mantenerse entre {cfg.rejillas_v_canal_min_m_s:.2f} y {cfg.rejillas_v_canal_max_m_s:.2f}~m/s. Para este proyecto se adopta un valor intermedio de {v_canal:.2f}~m/s, lo cual resulta apropiado considerando el caudal de diseno. El tirante hidraulico se establece en {h_tirante:.2f}~m, valor que permite una velocidad de flujo uniforme en la seccion del canal y evita la sedimentacion de solidos organicos antes de la rejilla, segun los criterios de Metcalf y Eddy \cite{{metcalf2014}}.

La perdida de carga en rejillas limpias se calcula mediante la formula de Kirschmer (1926), que relaciona la geometria de las barras con las caracteristicas del flujo. Los parametros que determinan esta perdida son: el espaciado entre barras ($b$), el espesor de las barras ($w$), la velocidad del flujo ($v$) y el angulo de inclinacion ($\theta$):

\begin{{equation}}
h_L = \beta \cdot \left(\frac{{w}}{{b}}\right)^{{4/3}} \cdot \frac{{v^2}}{{2g}} \cdot \sin\theta
\end{{equation}}
\captionequation{{Perdida de carga en rejillas limpias - Formula de Kirschmer}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$h_L$] = Perdida de carga en rejillas limpias (m)
    \item[$\beta$] = Factor de forma de la barra ({beta:.2f} para barras rectangulares)
    \item[$w$] = Espesor de la barra ({cfg.rejillas_w_barra_m*1000:.0f} mm)
    \item[$b$] = Espaciado entre barras ({cfg.rejillas_b_barra_m*1000:.0f} mm)
    \item[$v$] = Velocidad del flujo en el canal (m/s)
    \item[$g$] = Aceleracion de la gravedad (9,81 m/s\textsuperscript{{2}})
    \item[$\theta$] = Angulo de inclinacion de las barras ({cfg.rejillas_angulo_grados:.0f}\textdegree)
\end{{itemize}}

\begin{{table}}[H]
\centering
\caption{{Parametros de diseno -- Rejillas}}
\begin{{tabular}}{{llcc}}
\toprule
Parametro & Descripcion & Valor adoptado & Fuente \\
\midrule
Velocidad en canal & Velocidad de paso & {cfg.rejillas_v_canal_m_s:.2f} m/s & Metcalf y Eddy \\
Tirante hidraulico & Altura de agua en canal & {cfg.rejillas_h_tirante_m:.2f} m & Criterio tecnico \\
Angulo de rejilla & Inclinacion barras & {cfg.rejillas_angulo_grados:.0f}\textdegree & Practica comun \\
Espaciado entre barras & Abertura libre & {cfg.rejillas_b_barra_m*1000:.0f} mm & OPS/CEPIS \\
Espesor de barras & Seccion barra & {cfg.rejillas_w_barra_m*1000:.0f} mm & Constructivo \\
Factor de forma & Barras rectangulares & {beta:.2f} & Kirschmer \\
\bottomrule
\end{{tabular}}
\end{{table}}

El caudal de diseno por linea es {cfg.Q_linea_L_s:.1f} L/s. La seccion transversal del canal se determina aplicando la ecuacion de continuidad:

\begin{{equation}}
A_{{{{canal}}}} = \frac{{Q}}{{v}} = \frac{{{cfg.Q_linea_m3_s:.5f}}}{{{v_canal:.2f}}} = {r['A_canal_m2']:.5f} \text{{ m}}^2
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_{{{{canal}}}}$] = Seccion transversal del canal (m\textsuperscript{{2}})
    \item[$Q$] = Caudal de diseno por linea ({cfg.Q_linea_m3_s:.5f} m\textsuperscript{{3}}/s)
    \item[$v$] = Velocidad de diseno adoptada ({v_canal:.2f} m/s)
\end{{itemize}}

Despejando el ancho del canal de la ecuacion $A = b \times h$, con $h = {h_tirante:.2f}$ m:

\begin{{equation}}
b = \frac{{A_{{{{canal}}}}}}{{h}} = \frac{{{r['A_canal_m2']:.5f}}}{{{h_tirante:.2f}}} = {r['b_canal_teorico_m']:.3f} \text{{ m}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$b$] = Ancho teorico del canal (m)
    \item[$A_{{{{canal}}}}$] = Seccion transversal del canal ({r['A_canal_m2']:.5f} m\textsuperscript{{2}})
    \item[$h$] = Tirante hidraulico ({h_tirante:.2f} m)
\end{{itemize}}

Este ancho teorico de {r['b_canal_teorico_m']:.3f} m es inferior al minimo constructivo practico. Se adopta un ancho de {ancho_minimo_constructivo_m:.2f} m como dimension minima constructiva segun criterios de OPS/CEPIS \cite{{ops2005}} y SENAGUA \cite{{senagua2012}}, que establecen un ancho minimo de {ancho_minimo_constructivo_m:.2f} m para permitir la operacion adecuada, el acceso para limpieza y la aplicacion de herramientas de mantenimiento. Verificando la velocidad real con este ancho:

\begin{{equation}}
v_{{{{real}}}} = \frac{{Q}}{{A_{{{{real}}}}}} = \frac{{{cfg.Q_linea_m3_s:.5f}}}{{{r['ancho_layout_m']:.2f} \times {h_tirante:.2f}}} = {r['v_canal_real_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$v_{{{{real}}}}$] = Velocidad real verificada con ancho constructivo (m/s)
    \item[$Q$] = Caudal de diseno ({cfg.Q_linea_m3_s:.5f} m\textsuperscript{{3}}/s)
    \item[$A_{{{{real}}}}$] = Seccion real con ancho constructivo adoptado ({r['ancho_layout_m']:.2f} $\times$ {h_tirante:.2f} m\textsuperscript{{2}})
\end{{itemize}}

La velocidad real de {r['v_canal_real_m_s']:.3f} m/s es el resultado de adoptar el ancho minimo constructivo. La perdida de carga calculada con esta velocidad real resulta $h_L = {r['perdida_carga_real_m']*100:.4f}$ cm, menor al umbral de {hL_criterio_cm:.0f} cm que Metcalf y Eddy \cite{{metcalf2014}} indican como referencia para sistemas de limpieza mecanica.

La longitud de {r['largo_layout_m']:.1f} m y el ancho de {r['ancho_layout_m']:.2f} m responden a criterios constructivos y operativos. El ancho de {ancho_minimo_constructivo_m:.2f} m es la dimension minima constructiva segun OPS/CEPIS \cite{{ops2005}} y SENAGUA \cite{{senagua2012}}, que permite la operacion adecuada de la rejilla, el acceso para limpieza y la aplicacion de herramientas de mantenimiento. La longitud contempla el espacio de la rejilla propiamente dicha mas las zonas de transicion necesarias para la operacion."""

    def generar_parametros(self) -> str:
        """SECCION 2: Parametros - Ahora vacio porque esta en Teoria."""
        return ""

    def generar_dimensionamiento(self) -> str:
        """SECCION 3: Dimensionamiento - Ahora vacio porque esta en Teoria."""
        return ""

    def generar_verificacion(self) -> str:
        """SECCION 4: Verificacion - Seccion grande independiente."""
        cfg = self.cfg
        r = self.datos
        limite_advertencia = cfg.rejillas_v_max_advertencia_m_s
        limite_destructivo = cfg.rejillas_v_max_destructivo_m_s

        return rf"""\subsection{{Verificacion}}

\textbf{{Verificacion para Caudal Maximo Horario}}

Se verifica el comportamiento hidraulico para el caudal maximo horario, aplicando un factor de pico tipico de {r['factor_pico']:.1f} sobre el caudal medio:

\begin{{equation}}
Q_{{{{max}}}} = {r['factor_pico']:.1f} \times Q_{{{{medio}}}} = {r['factor_pico']:.1f} \times {cfg.Q_linea_L_s:.1f} = {r['Q_max_L_s']:.1f} \text{{ L/s}}
\end{{equation}}

A caudal maximo, la velocidad horizontal resulta:

\begin{{equation}}
v_{{{{max}}}} = \frac{{Q_{{{{max}}}}}}{{A_{{{{real}}}}}} = \frac{{{r['Q_max_L_s']:.3f}/1000}}{{{r['ancho_layout_m']:.2f} \times {r['h_tirante_m']:.2f}}} = {r['v_max_m_s']:.3f} \text{{ m/s}}
\end{{equation}}

\textbf{{Criterios de verificacion de velocidad}} (segun Metcalf y Eddy \cite{{metcalf2014}}):

La velocidad calculada $v_{{{{max}}}} = {r['v_max_m_s']:.3f}$~m/s se evalua segun:

\begin{{equation}}
\text{{Estado}} = \begin{{cases}}
    \text{{OPTIMO}} & \text{{si }} v_{{{{max}}}} \leq {limite_advertencia:.1f} \text{{ m/s}} \quad \text{{(sin riesgo)}} \\
    \text{{ACEPTABLE}} & \text{{si }} {limite_advertencia:.1f} < v_{{{{max}}}} \leq {limite_destructivo:.1f} \text{{ m/s}} \quad \text{{(monitoreo)}} \\
    \text{{NO ADMISIBLE}} & \text{{si }} v_{{{{max}}}} > {limite_destructivo:.1f} \text{{ m/s}} \quad \text{{(dano seguro)}}
\end{{cases}}
\end{{equation}}
\captionequation{{Criterios de verificacion de velocidad en rejillas}}

Con la velocidad calculada $v_{{{{max}}}} = {r['v_max_m_s']:.3f}$~m/s, la unidad se clasifica como \textbf{{{r['estado_velocidad']}}}. En terminos de cumplimiento, la verificacion de velocidad \textbf{{{r['estado_velocidad_norma']}}} porque {r['texto_velocidad_verificacion']}.

Respecto a la perdida de carga, el valor maximo calculado es {r['hL_max_m']*100:.4f}~cm. Por tanto, la verificacion de perdida de carga \textbf{{{r['estado_perdida']}}}, ya que {r['texto_perdida_verificacion']}."""

    def generar_esquema_matplotlib(self, output_dir: str = None) -> str:
        """Genera un esquema tecnico de rejillas y guarda como PNG."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.patches import Arc
            import numpy as np
        except ImportError:
            return None

        r = self.datos
        cfg = self.cfg

        h = r['h_tirante_m']
        b = r['ancho_layout_m']
        L = r['largo_layout_m']
        altura_libre = max(0.15, 0.35 * h)
        theta = cfg.rejillas_angulo_grados
        espaciamiento_mm = cfg.rejillas_b_barra_m * 1000
        espesor_mm = cfg.rejillas_w_barra_m * 1000

        fig, (ax1, ax2) = plt.subplots(
            1,
            2,
            figsize=(16, 7),
            gridspec_kw={'width_ratios': [1.05, 1.75]},
            constrained_layout=True,
        )

        # Factor de escala para labels y flechas (1.0 = normal, 1.5 = 50% mas grande)
        escala = 1.2
        
        color_agua = '#DCEEFF'
        color_muro = '#D9D9D9'
        color_rejilla = '#1F1F1F'
        color_flujo = '#0B66C3'
        color_cota = '#444444'

        canal_altura = h + altura_libre
        ax1.add_patch(
            patches.Rectangle(
                (0, 0), b, canal_altura,
                facecolor=color_muro, edgecolor=color_rejilla, linewidth=2.2 * escala
            )
        )
        ax1.add_patch(
            patches.Rectangle((0, 0), b, h, facecolor=color_agua, edgecolor='none')
        )
        ax1.plot([0, b], [h, h], linestyle='--', color=color_flujo, linewidth=1.8 * escala)

        paso = cfg.rejillas_b_barra_m + cfg.rejillas_w_barra_m
        x_barra = cfg.rejillas_w_barra_m * 0.4
        while x_barra < b - cfg.rejillas_w_barra_m:
            ax1.add_patch(
                patches.Rectangle(
                    (x_barra, 0.02 * canal_altura),
                    cfg.rejillas_w_barra_m,
                    canal_altura * 0.92,
                    facecolor=color_rejilla,
                    edgecolor='none',
                    alpha=0.92
                )
            )
            x_barra += paso

        # Cota h - linea simple con marcas
        x_cota_h = -0.12
        ax1.plot([x_cota_h, x_cota_h], [0, h], color=color_cota, lw=1.0)
        ax1.plot([x_cota_h-0.02, x_cota_h+0.02], [0, 0], color=color_cota, lw=1.0)
        ax1.plot([x_cota_h-0.02, x_cota_h+0.02], [h, h], color=color_cota, lw=1.0)
        ax1.text(
            x_cota_h - 0.04,
            h / 2,
            f'$h = {h:.2f}$ m',
            ha='right',
            va='center',
            fontsize=int(16 * escala),
        )

        # Cota b - linea simple con marcas
        y_cota_b = -0.10
        ax1.plot([0, b], [y_cota_b, y_cota_b], color=color_cota, lw=1.0)
        ax1.plot([0, 0], [y_cota_b-0.02, y_cota_b+0.02], color=color_cota, lw=1.0)
        ax1.plot([b, b], [y_cota_b-0.02, y_cota_b+0.02], color=color_cota, lw=1.0)
        ax1.text(
            b / 2,
            y_cota_b - 0.04,
            f'$b = {b:.2f}$ m',
            ha='center',
            va='top',
            fontsize=int(20 * escala),
        )

        ax1.text(
            b / 2,
            canal_altura + 0.08,
            f'Barras rectangulares\nespesor = {espesor_mm:.0f} mm  |  luz = {espaciamiento_mm:.0f} mm',
            ha='center',
            va='bottom',
            fontsize=int(16 * escala),
        )
        ax1.text(
            b / 2,
            -0.35,
            'Seccion transversal',
            fontsize=int(21 * escala),
            ha='center',
            va='top',
        )

        ax1.set_xlim(-0.15, 0.75)
        ax1.set_ylim(-0.25, 0.65)
        # Escala ajustada para coincidir con el segundo subplot
        ax1.axis('off')

        canal_altura_long = h + altura_libre
        ax2.add_patch(
            patches.Rectangle(
                (0, 0), L, canal_altura_long,
                facecolor=color_muro, edgecolor=color_rejilla, linewidth=2.2 * escala
            )
        )
        ax2.add_patch(
            patches.Rectangle((0, 0), L, h, facecolor=color_agua, edgecolor='none')
        )
        ax2.plot([0, L], [h, h], linestyle='--', color=color_flujo, linewidth=1.6 * escala)

        base_x = 0.32 * L
        altura_rej = canal_altura_long * 0.92
        dx = altura_rej / np.tan(np.radians(theta))
        top_x = base_x + dx
        top_y = altura_rej
        separacion_panel = max(0.012, cfg.rejillas_w_barra_m * 0.55)
        num_barras = 6

        for i in range(num_barras):
            offset = i * separacion_panel
            ax2.plot(
                [base_x + offset, top_x + offset],
                [0, top_y],
                color=color_rejilla,
                linewidth=2.4 * escala,
                solid_capstyle='round',
            )

        ax2.plot([base_x - 0.015, top_x - 0.015], [0, top_y], color=color_rejilla, linewidth=1.4 * escala)
        ax2.plot(
            [base_x + separacion_panel * (num_barras - 1) + 0.015, top_x + separacion_panel * (num_barras - 1) + 0.015],
            [0, top_y],
            color=color_rejilla,
            linewidth=1.4 * escala,
        )

        y_flujo = h * 0.52
        ax2.annotate(
            '',
            xy=(base_x - 0.06, y_flujo),
            xytext=(0.06, y_flujo),
            arrowprops=dict(arrowstyle='->', color=color_flujo, lw=4.5 * escala, mutation_scale=30 * escala),
        )
        ax2.annotate(
            '',
            xy=(L - 0.06, y_flujo),
            xytext=(top_x + separacion_panel * num_barras + 0.05, y_flujo),
            arrowprops=dict(arrowstyle='->', color=color_flujo, lw=4.5 * escala, mutation_scale=30 * escala),
        )

        # Labels superiores eliminados - solo titulos inferiores

        # Cota L - linea simple con marcas
        y_cota_L = -0.10
        ax2.plot([0, L], [y_cota_L, y_cota_L], color=color_cota, lw=1.0)
        ax2.plot([0, 0], [y_cota_L-0.02, y_cota_L+0.02], color=color_cota, lw=1.0)
        ax2.plot([L, L], [y_cota_L-0.02, y_cota_L+0.02], color=color_cota, lw=1.0)
        ax2.text(L / 2, y_cota_L - 0.04, f'$L = {L:.1f}$ m', ha='center', va='top', fontsize=int(21 * escala), fontweight='bold')

        radio_arco = min(0.24, L * 0.12)
        ax2.add_patch(
            Arc(
                (base_x, 0),
                2 * radio_arco,
                2 * radio_arco,
                angle=0,
                theta1=0,
                theta2=theta,
                color=color_cota,
                lw=1.4 * escala,
            )
        )
        ax2.text(base_x + 0.22, 0.11, rf'$\theta = {theta:.0f}^\circ$', fontsize=int(20 * escala), ha='left', va='bottom')

        ax2.text(
            L / 2,
            -0.35,
            'Perfil longitudinal',
            fontsize=int(21 * escala),
            ha='center',
            va='top',
        )

        ax2.set_xlim(-0.15, 2.15)
        ax2.set_ylim(-0.25, 0.65)
        # Escala ajustada
        ax2.axis('off')

        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados', 'figuras')
        os.makedirs(output_dir, exist_ok=True)

        filename = f"rejillas_{self.identificador}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=180, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

        return filepath

    def generar_resultados(self) -> str:
        """SECCION 5: Resultados - Seccion grande independiente."""
        cfg = self.cfg
        r = self.datos
        ancho_criterio_tabla_m = r['ancho_criterio_tabla_m']
        ancho_minimo_constructivo_m = r['ancho_minimo_constructivo_m']

        # Generar figura en la ruta configurada
        if os.path.isabs(self.ruta_figuras):
            # Si es ruta absoluta, usarla directamente para guardar
            output_dir = self.ruta_figuras
            # Para LaTeX, usar ruta relativa simple (figuras/nombre.png)
            latex_ruta_base = 'figuras'
        else:
            # Si es ruta relativa, construir ruta completa
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados', self.ruta_figuras)
            latex_ruta_base = self.ruta_figuras

        fig_path = self.generar_esquema_matplotlib(output_dir)

        if fig_path:
            # Para LaTeX, usar ruta relativa siempre
            fig_relativa = (latex_ruta_base + '/' + os.path.basename(fig_path)).replace('\\', '/')
            figura_latex = rf"""\begin{{figure}}[H]
\centering
\includegraphics[width=0.9\textwidth]{{{fig_relativa}}}
\caption{{Esquema del canal de desbaste con rejillas (dimensiones en metros)}}
\label{{fig:rejillas}}
\end{{figure}}

"""
        else:
            figura_latex = ""

        return rf"""\subsection{{Resultados}}

\begin{{table}}[H]
\centering
\caption{{Verificacion de criterios de diseno - Rejillas}}
\begin{{tabular}}{{lccc}}
\toprule
Parametro & Valor calculado & Criterio & Estado \\
\midrule
Velocidad de diseno & {r['v_canal_adoptada_m_s']:.2f} m/s & {cfg.rejillas_v_canal_min_m_s:.2f} -- {cfg.rejillas_v_canal_max_m_s:.2f} m/s & {r['estado_velocidad_diseno']} \\
Velocidad real & {r['v_canal_real_m_s']:.3f} m/s & Ancho minimo constructivo$^a$ & Aplicado \\
Perdida de carga (Qmax) & {r['hL_max_m']*100:.4f} cm & $<$ {r['hL_criterio_m']*100:.0f} cm & {r['estado_perdida_qmax']} \\
Ancho constructivo & {r['ancho_layout_m']:.2f} m & $\geq$ {ancho_criterio_tabla_m:.2f} m & {r['estado_ancho_constructivo']} \\
\bottomrule
\end{{tabular}}
\small
$^a$ Para caudales pequenos ({cfg.Q_linea_L_s:.1f} L/s) el ancho minimo constructivo ({ancho_minimo_constructivo_m:.2f} m) domina sobre el criterio de velocidad.
\end{{table}}

{figura_latex}\textbf{{Manejo de solidos retenidos}}

Las rejillas retienen solidos gruesos presentes en el agua residual que podrian danar equipos o causar obstrucciones en el sistema. El manejo adecuado de estos residuos incluye:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item \textbf{{Tipos de solidos retenidos:}} Plasticos, ramas, papel, trapos y otros desechos flotantes de tamano superior al espaciado entre barras ({cfg.rejillas_b_barra_m*1000:.0f} mm).
    \item \textbf{{Frecuencia de limpieza:}} Diaria o segun acumulacion observada. La perdida de carga calculada de {r['perdida_carga_real_m']*100:.4f} cm (limpio) indica que la limpieza puede ser manual dado que es inferior al umbral de {r['hL_criterio_m']*100:.0f} cm recomendado para sistemas mecanizados.
    \item \textbf{{Metodo de limpieza:}} Manual mediante rastrillos o ganchos desde la plataforma de operacion. El angulo de inclinacion de {cfg.rejillas_angulo_grados:.0f}\textdegree\ facilita el retiro de solidos hacia la parte superior del canal.
    \item \textbf{{Disposicion final:}} Los solidos retenidos deben depositarse en contenedores impermeables y transportarse a un relleno sanitario autorizado. \textit{{No son aptos para compostaje directo}} debido a la presencia de plasticos y materiales no biodegradables.
\end{{itemize}}

\textit{{Nota sobre cantidades:}} El presente dimensionamiento no estima la masa o volumen diario de residuos de cribado. Segun Metcalf y Eddy \cite{{metcalf2014}}, la produccion tipica de residuos de rejillas finas en aguas residuales municipales varia entre 0.005--0.02 m\textsuperscript{{3}}/1000 m\textsuperscript{{3}} de agua tratada. Para el caudal de diseno, esto representaria aproximadamente 0.02--0.09 m\textsuperscript{{3}}/d (total planta), sujeto a caracterizacion local.

Las dimensiones finales del canal con rejillas son: ancho {r['ancho_layout_m']:.2f} m, tirante {r['h_tirante_m']:.2f} m y longitud {r['largo_layout_m']:.1f} m. Se requieren dos unidades, una por cada linea de tratamiento."""


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_dir)
    
    from ptar_dimensionamiento import ConfigDiseno, dimensionar_rejillas
    import subprocess
    
    print("=" * 60)
    print("TEST - GENERADOR MODULAR DE REJILLAS")
    print("=" * 60)
    
    cfg = ConfigDiseno()
    cfg.Q_linea_L_s = 5.0
    cfg.Q_linea_m3_s = 0.005
    print(f"\n[1] Q_linea = {cfg.Q_linea_L_s} L/s")
    
    datos = dimensionar_rejillas(cfg)
    print(f"[2] Dimensiones: L={datos['largo_layout_m']:.1f}m, b={datos['ancho_layout_m']:.2f}m, H={datos['h_tirante_m']:.2f}m")
    
    resultados_dir = os.path.join(base_dir, 'resultados', 'test_modular')
    figuras_dir = os.path.join(resultados_dir, 'figuras')
    os.makedirs(figuras_dir, exist_ok=True)
    
    gen = GeneradorRejillas(cfg, datos, ruta_figuras=figuras_dir)
    latex = gen.generar_completo()
    print(f"[3] LaTeX generado: {len(latex)} chars")
    
    tex_path = os.path.join(resultados_dir, 'rejillas_test.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    
    doc_path = os.path.join(resultados_dir, 'rejillas_test_completo.tex')
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

\section{Unidad de Rejillas}

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
        pdf_path = os.path.join(resultados_dir, 'rejillas_test_completo.pdf')
        if os.path.exists(pdf_path):
            print(f"    PDF generado: {pdf_path}")
    except Exception as e:
        print(f"    ERROR: {e}")
    
    print("=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
