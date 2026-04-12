#!/usr/bin/env python3
"""
GENERADOR LaTeX - UNIDAD: BIOFILTRO DE CARGA MECANIZADA HIDRÁULICA (TAF)

Metodología Dual: Ruta A (Carga Hidráulica Convencional - NRC)
                  Ruta B (Carga Mecanizada de Alta Carga - Germain)

Organizado en 3 subsections: Dimensionamiento, Verificación, Resultados
"""

import os
import sys

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GeneradorBiofiltroCargaMecanizadaHidraulica:
    """Generador LaTeX para Biofiltro TAF con selección dual de metodología.

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
        """Genera todo el contenido LaTeX del biofiltro en 3 subsections."""
        return "\n\n".join([
            self.generar_descripcion(),
            self.generar_verificacion(),
            self.generar_resultados()
        ])

    def generar_esquema_matplotlib(self, output_dir=None):
        """Genera esquema técnico del biofiltro TAF en matplotlib.

        Dibuja corte transversal con:
          - Distribuidor rotatorio (brazos + boquillas)
          - Medio filtrante plástico estructurado con biopelícula
          - Sistema underdrain con aberturas de ventilación
          - Conexiones de afluente/efluente
          - Recirculación externa (sólo Ruta B)
          - Líneas de cota y etiquetas

        Returns:
            str | None: ruta absoluta del PNG generado, o None si falla.
        """
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from matplotlib.patches import Rectangle, Circle, Polygon
            import numpy as np
        except ImportError:
            return None

        bf   = self.datos
        ruta = bf['ruta_diseno']

        # ── dimensiones principales ────────────────────────────────────
        D        = bf['D_bf_m']
        H_total  = bf['H_total_m']
        D_medio  = bf['D_medio_m']
        H_dist   = bf['H_distribucion_m']
        H_under  = bf['H_underdrain_m']
        H_bordo  = bf['H_bordo_libre_m']
        num_brazos = int(bf['num_brazos'])

        # ── datos de operación ────────────────────────────────────────
        Q_m3_h    = bf.get('Q_m3_h', bf['Q_m3_d'] / 24.0)
        Q_aplic   = bf.get('Q_aplicado_m3_h', Q_m3_h)
        CHS       = bf['CHS_m3_m2_h']
        E         = bf['E_calculada']
        Se        = bf['Se_calculada_mg_L']
        DBO0      = bf['DBO_entrada_mg_L']
        n_boquillas = int(bf.get('num_boquillas_por_brazo', 3))

        # ── paleta de colores ─────────────────────────────────────────
        c_muro      = '#90A4AE'   # hormigón
        c_fondo     = '#CFD8DC'   # base
        c_underdrain= '#E0E0E0'   # zona underdrain
        c_bloque    = '#BDBDBD'   # bloques underdrain
        c_media     = '#F5E6C8'   # medio filtrante
        c_media_borde = '#C8A96E' # hatch medio
        c_biofilm   = '#A5D6A7'   # biopelícula
        c_pivot     = '#616161'   # columna distribuidora
        c_verde     = '#2E7D32'   # afluente
        c_azul      = '#1565C0'   # efluente
        c_aire      = '#1E88E5'   # ventilación aire
        c_naranja   = '#E65100'   # recirculación
        c_agua_caida= '#5B9BD5'   # agua percolando

        # ── geometría del eje ─────────────────────────────────────────
        x_centro     = 0.0
        x_izq        = -D / 2.0
        x_der        =  D / 2.0
        e_muro       = max(0.15, D * 0.025)   # espesor muro

        y_bottom     = 0.0
        y_under_top  = H_under
        y_media_top  = H_under + D_medio
        y_dist_top   = y_media_top + H_dist
        y_top        = H_total

        # ── figura ────────────────────────────────────────────────────
        fig_w = 11.0
        aspect = H_total / max(D, 0.1)
        fig_h  = max(7.0, fig_w * aspect * 0.75)
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))

        # ==============================================================
        # 1. BASE DE HORMIGÓN
        # ==============================================================
        ax.add_patch(Rectangle(
            (x_izq - e_muro, y_bottom - 0.28),
            D + 2*e_muro, 0.28,
            facecolor=c_fondo, edgecolor='#546E7A', linewidth=1.2
        ))

        # ==============================================================
        # 2. MUROS LATERALES
        # ==============================================================
        for x0 in [x_izq - e_muro, x_der]:
            ax.add_patch(Rectangle(
                (x0, y_bottom), e_muro, H_total,
                facecolor=c_muro, edgecolor='#546E7A', linewidth=1.2
            ))

        # ==============================================================
        # 3. ZONA UNDERDRAIN
        # ==============================================================
        ax.add_patch(Rectangle(
            (x_izq, y_bottom), D, H_under,
            facecolor=c_underdrain, edgecolor='none'
        ))

        # bloques de soporte (underdrain blocks)
        n_bloq    = max(4, int(D / 1.4))
        blk_w     = D * 0.07
        blk_h     = H_under * 0.38
        blk_y     = y_bottom + H_under * 0.12
        for i in range(n_bloq):
            xb = x_izq + (i + 0.5) * (D / n_bloq) - blk_w / 2
            ax.add_patch(Rectangle(
                (xb, blk_y), blk_w, blk_h,
                facecolor=c_bloque, edgecolor='#9E9E9E', linewidth=0.7
            ))

        # canal central de recolección
        cw = D * 0.11
        ch = H_under * 0.28
        ax.add_patch(Rectangle(
            (x_centro - cw/2, y_bottom), cw, ch,
            facecolor='#78909C', edgecolor='#546E7A', linewidth=0.8
        ))

        # aberturas de ventilación en los muros (lateral izq y der)
        vent_h = H_under * 0.28
        vent_w = e_muro * 0.65
        vent_y = y_bottom + H_under * 0.42
        for x0, dir_ in [(x_izq - e_muro, +1), (x_der + e_muro - vent_w, -1)]:
            ax.add_patch(Rectangle(
                (x0, vent_y), vent_w, vent_h,
                facecolor='white', edgecolor='#546E7A', linewidth=0.8
            ))
        # flechas de aire entrando
        y_aire = vent_y + vent_h / 2
        ax.annotate('', xy=(x_izq + 0.12, y_aire),
                    xytext=(x_izq - e_muro - 0.32, y_aire),
                    arrowprops=dict(arrowstyle='->', color=c_aire, lw=1.6))
        ax.annotate('', xy=(x_der - 0.12, y_aire),
                    xytext=(x_der + e_muro + 0.32, y_aire),
                    arrowprops=dict(arrowstyle='->', color=c_aire, lw=1.6))

        # ==============================================================
        # 4. MEDIO FILTRANTE
        # ==============================================================
        ax.add_patch(Rectangle(
            (x_izq, y_under_top), D, D_medio,
            facecolor=c_media, edgecolor='none'
        ))
        # textura hatch (simula medio plástico estructurado)
        ax.add_patch(Rectangle(
            (x_izq, y_under_top), D, D_medio,
            facecolor='none', edgecolor=c_media_borde,
            linewidth=0.4, hatch='////'
        ))

        # biopelícula en los bordes (verde)
        bf_w = max(0.08, D * 0.04)
        for x0 in [x_izq, x_der - bf_w]:
            ax.add_patch(Rectangle(
                (x0, y_under_top), bf_w, D_medio,
                facecolor=c_biofilm, edgecolor='none', alpha=0.85
            ))

        # flechas de agua percolando hacia abajo (dentro del medio)
        n_fl = min(5, max(3, int(D / 1.5)))
        for i in range(n_fl):
            fx   = x_izq + (i + 0.5) * (D / n_fl)
            y1   = y_media_top - D_medio * 0.08
            y2   = y_under_top + D_medio * 0.08
            ax.annotate('', xy=(fx, y2), xytext=(fx, y1),
                        arrowprops=dict(arrowstyle='->', color=c_agua_caida,
                                        lw=1.6, alpha=0.65))

        # líneas divisorias del medio
        for y_lin, ls in [(y_media_top, '-'), (y_under_top, '--')]:
            ax.plot([x_izq, x_der], [y_lin, y_lin],
                    color='#8D6E63', linewidth=0.9, linestyle=ls, alpha=0.6)

        # ==============================================================
        # 5. ZONA LIBRE PARA EL DISTRIBUIDOR
        # ==============================================================
        ax.add_patch(Rectangle(
            (x_izq, y_media_top), D, H_dist,
            facecolor='#EEF5FF', edgecolor='none', alpha=0.55
        ))

        # ==============================================================
        # 6. DISTRIBUIDOR ROTATORIO
        # ==============================================================
        y_brazos  = y_media_top + H_dist * 0.52
        piv_w     = max(0.07, D * 0.028)
        piv_h     = H_dist * 0.82

        # columna pivote
        ax.add_patch(Rectangle(
            (x_centro - piv_w/2, y_media_top + H_dist * 0.06),
            piv_w, piv_h,
            facecolor=c_pivot, edgecolor='#212121', linewidth=0.9
        ))

        # brazos (sólo los que caen en el plano de corte)
        L_brazo = D / 2.0 - e_muro * 0.4
        for ang in ([0, 180] if num_brazos == 2 else [0, 90, 180, 270]):
            rad   = np.radians(float(ang))
            dx    = np.cos(rad)
            if abs(abs(ang) - 90) > 5:           # brazos en plano del corte
                x_fin = x_centro + dx * L_brazo
                ax.plot([x_centro, x_fin], [y_brazos, y_brazos],
                        '-', color='#37474F', linewidth=2.8, solid_capstyle='round')

                # boquillas a lo largo del brazo
                n_show = min(n_boquillas, 5)
                for j in range(n_show):
                    t   = (j + 1) / (n_show + 1)
                    x_n = x_centro + dx * L_brazo * t
                    ax.add_patch(Circle(
                        (x_n, y_brazos), piv_w * 0.42,
                        facecolor='#37474F', edgecolor='#111', linewidth=0.5
                    ))
                    # spray pequeño hacia abajo
                    ax.annotate('', xy=(x_n + dx * 0.05, y_brazos - 0.11),
                                xytext=(x_n, y_brazos - 0.01),
                                arrowprops=dict(arrowstyle='->', color=c_azul,
                                                lw=0.8, alpha=0.8))

        # indicador de rotación (arco punteado)
        r_arc      = L_brazo * 0.32
        theta_arc  = np.linspace(0.12, np.pi * 0.75, 35)
        ax.plot(x_centro + r_arc * np.cos(theta_arc),
                y_brazos + r_arc * np.sin(theta_arc) * 0.28,
                color='#78909C', linewidth=0.9, linestyle='--', alpha=0.7)
        ax.annotate('',
                    xy=(x_centro + r_arc * np.cos(theta_arc[-1]),
                        y_brazos + r_arc * np.sin(theta_arc[-1]) * 0.28),
                    xytext=(x_centro + r_arc * np.cos(theta_arc[-2]),
                            y_brazos + r_arc * np.sin(theta_arc[-2]) * 0.28),
                    arrowprops=dict(arrowstyle='->', color='#78909C', lw=0.9))

        # borde superior de la estructura
        ax.plot([x_izq - e_muro, x_der + e_muro], [y_top, y_top],
                '-', color='#546E7A', linewidth=1.5)

        # ==============================================================
        # 7. TUBERÍA DE AFLUENTE (entra desde arriba al pivote)
        # ==============================================================
        ax.plot([x_centro, x_centro], [y_top, y_media_top + H_dist * 0.88],
                'k-', linewidth=2.8)
        ax.plot([x_centro, x_centro], [y_top + 0.1, y_top + 0.85],
                'k-', linewidth=2.8)
        ax.annotate('', xy=(x_centro, y_top + 0.25),
                    xytext=(x_centro, y_top + 0.82),
                    arrowprops=dict(arrowstyle='->', color=c_verde, lw=2.8))

        # ==============================================================
        # 8. TUBERÍA DE EFLUENTE (sale lateral derecho, zona underdrain)
        # ==============================================================
        y_sal = y_bottom + H_under * 0.16
        ax.plot([x_der + e_muro, x_der + e_muro + 1.6], [y_sal, y_sal],
                'k-', linewidth=2.5)
        ax.plot([x_der + e_muro, x_der + e_muro], [y_sal - 0.14, y_sal + 0.14],
                'k-', linewidth=2.0)
        ax.annotate('', xy=(x_der + e_muro + 1.6, y_sal),
                    xytext=(x_der + e_muro + 0.3, y_sal),
                    arrowprops=dict(arrowstyle='->', color=c_azul, lw=2.5))

        # ==============================================================
        # 9. RECIRCULACIÓN (solo Ruta B)
        # ==============================================================
        if ruta == "B":
            R     = bf.get('R_recirculacion', 1.0)
            Q_rec = bf.get('Q_R_m3_d', Q_m3_h * R * 24.0)

            x_rec   = x_izq - e_muro - 1.25
            y_bomba = y_sal - 0.55

            # conexión desde efluente a bomba (corre por fuera a la izquierda)
            # horizontal inferior desde efluente
            ax.plot([x_der + e_muro + 1.6, x_der + e_muro + 1.6],
                    [y_sal, y_bomba],
                    color=c_naranja, linewidth=1.6, linestyle='--')
            ax.plot([x_der + e_muro + 1.6, x_rec],
                    [y_bomba, y_bomba],
                    color=c_naranja, linewidth=1.6, linestyle='--')

            # bomba (círculo con P)
            ax.add_patch(Circle(
                (x_rec, y_bomba), 0.26,
                facecolor='#FFF3E0', edgecolor=c_naranja, linewidth=1.8
            ))
            ax.text(x_rec, y_bomba, 'P', ha='center', va='center',
                    fontsize=9, fontweight='bold', color=c_naranja)

            # tubería de recirculación sube hasta la entrada del afluente
            y_rec_top = y_top + 0.55
            ax.plot([x_rec, x_rec], [y_bomba + 0.26, y_rec_top],
                    color=c_naranja, linewidth=1.6, linestyle='--')
            ax.plot([x_rec, x_centro - 0.08], [y_rec_top, y_rec_top],
                    color=c_naranja, linewidth=1.6, linestyle='--')
            # flecha ascendente
            ax.annotate('', xy=(x_rec, y_rec_top - 0.4),
                        xytext=(x_rec, y_rec_top - 0.75),
                        arrowprops=dict(arrowstyle='->', color=c_naranja, lw=1.6))

        # ==============================================================
        # 10. LÍNEAS DE COTA
        # ==============================================================
        extra_izq = 1.3 if ruta == "A" else 2.2
        x_dim = x_izq - e_muro - extra_izq

        def draw_dim(y1, y2, x_pos, lbl):
            if abs(y2 - y1) < 0.05:
                return
            ax.plot([x_pos]*2, [y1, y2], 'k-', linewidth=0.8)
            ax.plot([x_pos - 0.1, x_pos + 0.1], [y1, y1], 'k-', linewidth=0.8)
            ax.plot([x_pos - 0.1, x_pos + 0.1], [y2, y2], 'k-', linewidth=0.8)
            if y2 - y1 > 0.14:
                ax.annotate('', xy=(x_pos, y2 - 0.04), xytext=(x_pos, y2 - 0.22),
                            arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
                ax.annotate('', xy=(x_pos, y1 + 0.04), xytext=(x_pos, y1 + 0.22),
                            arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
            ax.text(x_pos - 0.15, (y1 + y2) / 2, lbl,
                    ha='right', va='center', fontsize=7)

        draw_dim(y_bottom,     y_under_top,  x_dim, f'{H_under:.1f} m')
        draw_dim(y_under_top,  y_media_top,  x_dim, f'{D_medio:.1f} m')
        draw_dim(y_media_top,  y_dist_top,   x_dim, f'{H_dist:.2f} m')
        if H_bordo > 0.08:
            draw_dim(y_dist_top, y_top,      x_dim, f'{H_bordo:.2f} m')

        # cota de altura total (más a la izquierda)
        x_tot = x_dim - 0.9
        ax.plot([x_tot]*2, [y_bottom, y_top], 'k-', linewidth=0.8)
        ax.plot([x_tot - 0.1, x_tot + 0.1], [y_bottom, y_bottom], 'k-', linewidth=0.8)
        ax.plot([x_tot - 0.1, x_tot + 0.1], [y_top,    y_top],    'k-', linewidth=0.8)
        ax.text(x_tot - 0.15, (y_bottom + y_top) / 2,
                f'H = {H_total:.1f} m',
                ha='right', va='center', fontsize=8, fontweight='bold')

        # cota de diámetro (abajo)
        y_dbot = y_bottom - 0.58
        ax.plot([x_izq, x_der], [y_dbot]*2, 'k-', linewidth=0.8)
        ax.plot([x_izq, x_izq], [y_dbot - 0.1, y_dbot + 0.1], 'k-', linewidth=0.8)
        ax.plot([x_der, x_der], [y_dbot - 0.1, y_dbot + 0.1], 'k-', linewidth=0.8)
        ax.annotate('', xy=(x_izq + 0.28, y_dbot), xytext=(x_izq + 0.05, y_dbot),
                    arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
        ax.annotate('', xy=(x_der - 0.28, y_dbot), xytext=(x_der - 0.05, y_dbot),
                    arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
        ax.text(x_centro, y_dbot - 0.14, f'Ø {D:.1f} m',
                ha='center', va='top', fontsize=8)

        # ==============================================================
        # 11. ETIQUETAS
        # ==============================================================
        off_x = x_der + e_muro + 0.55

        # zona underdrain - posicionado a la derecha, más abajo para evitar superposición con recirculación
        ax.text(x_der + e_muro + 0.55, y_bottom - 0.52,
                'Sistema\nunderdrain',
                ha='left', va='top', fontsize=7.5)

        # zona medio
        ax.text(off_x, y_under_top + D_medio / 2,
                f'Medio filtrante\nplástico estructurado\n{D_medio:.1f} m profundidad',
                ha='left', va='center', fontsize=8, fontweight='bold')

        # zona distribución (solo si hay espacio suficiente)
        if H_dist > 0.25:
            ax.text(off_x, y_media_top + H_dist / 2,
                    f'Distribuidor\n({num_brazos} brazos)',
                    ha='left', va='center', fontsize=8)

        # bordo libre - posicionado más arriba para evitar superposición
        if H_bordo > 0.1:
            ax.text(off_x, y_dist_top + H_bordo * 0.5,
                    f'Bordo libre\n{H_bordo:.2f} m',
                    ha='left', va='center', fontsize=7.5)

        # afluente
        ax.text(x_centro + 0.25, y_top + 0.65,
                f'Afluente\n{Q_aplic:.1f} m³/h · DBO₅: {DBO0:.0f} mg/L',
                ha='left', va='center', fontsize=9, fontweight='bold', color=c_verde)

        # efluente
        ax.text(x_der + e_muro + 1.75, y_sal + 0.12,
                f'Efluente → Sed. secundario\nDBO₅: {Se:.0f} mg/L  (E = {E*100:.0f}%)',
                ha='left', va='bottom', fontsize=9, fontweight='bold', color=c_azul)

        # eficiencia dentro del medio
        ax.text(x_centro, y_under_top + D_medio * 0.5,
                f'CHS = {CHS:.2f} m³/m²·h\nE = {E*100:.0f}%',
                ha='center', va='center', fontsize=9, fontweight='bold',
                color='#4E342E',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.75))

        # etiqueta aire - ajustada para no superponerse con underdrain
        ax.text(x_izq - e_muro - 0.42, y_aire,
                'Aire\n↑', ha='center', va='center', fontsize=7, color=c_aire)
        ax.text(x_der + e_muro + 0.42, y_aire,
                'Aire\n↑', ha='center', va='center', fontsize=7, color=c_aire)

        # biopelícula
        ax.text(x_izq + bf_w + 0.06, y_under_top + D_medio * 0.14,
                'Biopelícula\n(biofilm)', ha='left', va='bottom',
                fontsize=6.5, color='#1B5E20')

        # recirculación (label debajo de la bomba)
        if ruta == "B":
            R = bf.get('R_recirculacion', 1.0)
            ax.text(x_rec, y_bomba - 0.55,
                    f'Recirculación\nR = {R:.1f}',
                    ha='center', va='top', fontsize=8, color=c_naranja)

        # ==============================================================
        # 12. LÍMITES Y GUARDADO
        # ==============================================================
        x_min = (x_tot - 0.8) if ruta == "A" else min(x_tot - 0.8, x_rec - 1.2)
        x_max = off_x + 4.2
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_bottom - 1.05, y_top + 1.9)
        ax.set_aspect('equal')
        ax.axis('off')

        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'resultados', 'figuras'
            )
        os.makedirs(output_dir, exist_ok=True)

        fig_path = os.path.join(
            output_dir, f'Esquema_Biofiltro_TAF_Ruta{ruta}.png'
        )
        fig.savefig(fig_path, dpi=200, bbox_inches='tight',
                    facecolor='white', pad_inches=0.2)
        plt.close()
        return fig_path

    def generar_descripcion(self) -> str:
        """Genera subsection Dimensionamiento con teoría y cálculos."""
        cfg = self.cfg
        bf = self.datos
        ruta = bf['ruta_diseno']

        return rf"""\subsection{{Dimensionamiento}}

El biofiltro percolador de carga mecanizada hidráulica, conocido internacionalmente como Trickling Filter (TF) o biofiltro de goteo, constituye uno de los procesos biológicos más antiguos y probados para el tratamiento secundario de aguas residuales. Su principio de funcionamiento se basa en el contacto intermitente entre el agua residual y una biopelícula aerobia adherida a un medio de relleno estructurado, permitiendo la oxidación de la materia orgánica biodegradable mediante procesos biológicos aerobios.

El término ``carga mecanizada hidráulica'' hace referencia a que el afluente se aplica sobre el medio mediante un sistema de distribución rotatorio accionado hidráulicamente, en contraste con los sistemas de alimentación por gravedad simple. Esta configuración garantiza una distribución uniforme del agua residual sobre toda la superficie del medio, promoviendo el desarrollo homogéneo de la biopelícula y maximizando la eficiencia de transferencia de oxígeno y substrato.

\subsubsection*{{Fundamentos del Proceso y Desarrollo de la Biopelícula}}

El biofiltro opera como un reactor biológico de película fija (\textit{{attached growth}}) donde los microorganismos forman una capa biológica (biopelícula o \textit{{biofilm}}) de aproximadamente 0.1 a 0.5 mm de espesor sobre la superficie del medio de relleno. Esta biopelícula está compuesta por una comunidad microbiana compleja que incluye bacterias aerobias, hongos, protozoos y metazoos (principalmente rotíferos y nemátodos), organizada en capas funcionales distintas.

La capa externa de la biopelícula, en contacto directo con el aire que circula por el medio, mantiene condiciones estrictamente aerobias y es donde ocurre la oxidación de la materia orgánica. La capa interna, adyacente a la superficie del medio, puede desarrollar condiciones anaerobias o anóxicas, particularmente cuando el espesor de la biopelícula excede los 0.3 mm. El aire circula por el biofiltro mediante convección natural, impulsado por la diferencia de temperatura entre el aire ambiente y el interior del filtro, proporcionando el oxígeno necesario para mantener la actividad aerobia de los microorganismos.

El agua residual distribuida sobre el medio percola gravitacionalmente a través de los intersticios del relleno, entrando en contacto con la biopelícula. Durante este contacto, los contaminantes orgánicos se adsorben en la superficie de la biopelícula y son metabolizados por los microorganismos. Simultáneamente, el oxígeno disuelto en el afluente y el transferido desde la fase gaseosa es consumido en la respiración aerobia de la biomasa. El exceso de biomasa producida (lodo biológico o \textit{{sloughings}}) se desprende periódicamente de la superficie del medio por efecto del arrastre hidráulico, siendo recolectado en el sistema de drenaje inferior y requiriendo separación en un sedimentador secundario.

\subsubsection*{{Selección de la Metodología de Diseño}}

El manual técnico establece dos rutas de diseño fundamentales para el dimensionamiento de biofiltros percoladores, cada una aplicable a condiciones específicas de carga orgánica, disponibilidad de energía y requisitos de efluente:

\textbf{{Ruta A -- Carga Hidráulica Convencional (modelo NRC):}} Esta metodología se aplica cuando la carga orgánica superficial es moderada, típicamente para cargas orgánicas volumétricas menores o iguales a {cfg.bf_cmh_COS_limite_ruta_A:.2f} kg DBO/m³·d. La Ruta A no utiliza recirculación del efluente tratado, operando en flujo simple (\textit{{once-through}}). El modelo de diseño es el desarrollado por el National Research Council (NRC) de Estados Unidos, derivado del análisis estadístico de datos operacionales de instalaciones militares durante la Segunda Guerra Mundial. Este modelo es conservador y ha demostrado su eficacia en instalaciones con cargas moderadas y requisitos de efluente estándar.

\textbf{{Ruta B -- Carga Mecanizada de Alta Carga (modelo Germain):}} Esta metodología se selecciona cuando la carga orgánica superficial excede el umbral de {cfg.bf_cmh_COS_limite_ruta_A:.2f} kg DBO/m³·d, cuando se requiere una eficiencia de remoción superior, o cuando se dispone de energía para bombeo de recirculación. La Ruta B incorpora la recirculación del efluente tratado hacia la entrada del biofiltro, con relaciones de recirculación típicas entre $R = 0.5$ y $R = 4.0$. El modelo de diseño es el propuesto por Germain (1966) para medios plásticos estructurados, que describe la cinética de remoción mediante una ecuación de primer orden modificada que incorpora el efecto de la recirculación sobre la concentración afluente.

\begin{{table}}[H]
\centering
\caption{{Criterios de selección entre Rutas de diseño para biofiltros TAF}}
\label{{tab:seleccion_ruta_taf}}
\begin{{tabular}}{{p{{4.5cm}}p{{5cm}}p{{5cm}}}}
\toprule
\textbf{{Criterio}} & \textbf{{Ruta A (NRC)}} & \textbf{{Ruta B (Germain)}} \\
\midrule
Carga orgánica volumétrica (COS) & $\leq {cfg.bf_cmh_COS_limite_ruta_A:.2f}$ kg/m³·d & $> {cfg.bf_cmh_COS_limite_ruta_A:.2f}$ kg/m³·d \\
Recirculación & No (flujo simple) & Sí ($R = 0.5$--$4.0$) \\
Requerimiento energético & Mínimo (solo distribución) & Moderado (bombeo recirculación) \\
Eficiencia típica DBO$_5$ & 60--80\% & 70--90\% (con $R$ óptimo) \\
Modelo matemático & NRC (empírico) & Germain (cinético) \\
Aplicación típica & Cargas moderadas, área disponible & Alta carga, estricto efluente \\
\bottomrule
\end{{tabular}}
\end{{table}}

El algoritmo de selección evalúa la carga orgánica preliminar estimada para determinar la ruta más adecuada al proyecto:

\begin{{equation}}
\text{{COS}}_{{\text{{prelim}}}} = \frac{{W}}{{V_{{\text{{estimado}}}}}} = \frac{{Q \cdot S_0}}{{V_{{\text{{estimado}}}}}}
\end{{equation}}

Para este proyecto, {bf['texto_ruta']} El criterio de selección adoptado garantiza que la metodología de diseño es coherente con las condiciones de carga y los objetivos de calidad del efluente establecidos.

\subsubsection*{{Parámetros de Diseño y Rangos de Operación}}

El diseño del biofiltro TAF se fundamenta en parámetros que han sido establecidos a través de décadas de experiencia operacional en instalaciones a escala real. La Tabla~\ref{{tab:parametros_taf}} consolida los parámetros principales con sus rangos típicos y los valores adoptados para este proyecto.

\begin{{table}}[H]
\centering
\caption{{Parámetros de diseño para biofiltro TAF -- Ruta {ruta}}}
\label{{tab:parametros_taf}}
\begin{{tabular}}{{p{{4cm}}ccc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Rango típico}} & \textbf{{Valor adoptado}} & \textbf{{Fuente}} \\
\midrule
Profundidad medio $D$ & {cfg.bf_cmh_D_medio_min_m:.1f}--{cfg.bf_cmh_D_medio_max_m:.1f} m & {bf['D_medio_m']:.2f} m & Metcalf \& Eddy \\
Constante cinética $k_{{20}}$ & 0.06--0.10 m/h & {bf['k_20_m_h']:.3f} m/h & Germain (1966) \\
Coeficiente temperatura $\theta$ & 1.03--1.06 & {bf['theta']:.3f} & Arrhenius modificado \\
Exponente modelo $n$ (plástico) & 0.50 & {str(bf['n_germain'] or 'N/A')} & WEF MOP-8 \\
Carga hidráulica superficial CHS & {cfg.bf_cmh_CHS_min_m3_m2_h:.1f}--{cfg.bf_cmh_CHS_max_m3_m2_h:.1f} m³/m²·h & {bf['CHS_m3_m2_h']:.3f} m³/m²·h & Proyecto \\
\bottomrule
\end{{tabular}}
\end{{table}}

La profundidad del medio de {bf['D_medio_m']:.2f} m seleccionada se encuentra dentro del rango recomendado para biofiltros con medio plástico estructurado. Profundidades mayores aumentan el tiempo de contacto y la eficiencia de remoción, pero incrementan la carga estructural sobre el medio y el costo de construcción. La profundidad adoptada representa un compromiso óptimo entre eficiencia de tratamiento y viabilidad constructiva.

La constante cinética $k_{{20}} = {bf['k_20_m_h']:.3f}$ m/h corresponde al valor recomendado por Metcalf \& Eddy (2014) para medios plásticos aleatorios modernos con superficie específica de aproximadamente 100 m²/m³. Este valor ha sido validado en múltiples instalaciones y representa una estimación conservadora para condiciones de operación normales.

\subsubsection*{{Caracterización del Afluente}}

El biofiltro recibe el efluente del tratamiento primario (UASB o sedimentador primario), con una carga orgánica residual que requiere remoción biológica aerobia. La Tabla~\ref{{tab:entrada_taf}} presenta los parámetros de entrada característicos del afluente al biofiltro.

\begin{{table}}[H]
\centering
\caption{{Caracterización del afluente -- Biofiltro TAF}}
\label{{tab:entrada_taf}}
\begin{{tabular}}{{llll}}
\toprule
\textbf{{Parámetro}} & \textbf{{Símbolo}} & \textbf{{Valor}} & \textbf{{Unidad}} \\
\midrule
Caudal promedio diario & $Q$ & {bf['Q_m3_d']:.1f} & m³/d \\
Caudal máximo horario & $Q_{{\text{{max}}}}$ & {bf['Q_max_m3_d']:.1f} & m³/d \\
Factor de pico & -- & {cfg.factor_pico_Qmax:.1f} & -- \\
DBO₅ afluente & $S_0$ & {bf['DBO_entrada_mg_L']:.1f} & mg/L \\
SST afluente & $\text{{SST}}_0$ & {bf['SST_entrada_mg_L']:.1f} & mg/L \\
Temperatura del agua & $T$ & {bf['T_agua_C']:.1f} & °C \\

\bottomrule
\end{{tabular}}
\end{{table}}

\subsubsection*{{Carga Orgánica Afluente}}

La carga orgánica afluente al biofiltro, calculada como el producto del caudal por la concentración de DBO₅, resulta:

\begin{{equation}}
W = Q \cdot S_0 = {bf['Q_m3_d']:.1f}\ \text{{m}}^3\text{{/d}} \times {bf['DBO_entrada_mg_L']:.1f}\ \text{{g/m}}^3 \times 10^{{-3}} = {bf['W_kg_d']:.2f}\ \text{{kg DBO/d}}
\end{{equation}}
\captionequation{{Carga orgánica diaria afluente al biofiltro TAF}}

Esta carga orgánica representa la masa de contaminante biodegradable que debe ser removida por la biopelícula aerobia desarrollada en el medio filtrante.""" + (rf"""

\subsubsection*{{Modelo de Diseño NRC -- Ruta A (sin recirculación)}}

Para la Ruta A se utiliza el modelo empírico desarrollado por el National Research Council (NRC), derivado del análisis estadístico de datos operacionales de biofiltros de roca y medio plástico en instalaciones militares. El modelo establece una relación entre la eficiencia de remoción de DBO$_5$ y la carga orgánica aplicada por unidad de volumen del medio, incorporando el efecto de la recirculación mediante un factor de corrección.

La ecuación fundamental del modelo NRC para una etapa simple es:

\begin{{equation}}
E = \frac{{1}}{{1 + 0.4432 \sqrt{{\dfrac{{W}}{{V \cdot F}}}}}}
\end{{equation}}
\captionequation{{Modelo NRC para eficiencia de biofiltro -- Ruta A}}

En esta expresión, $E$ representa la fracción de DBO$_5$ removida (eficiencia), $W$ es la carga orgánica diaria afluente en kg DBO/d, $V$ es el volumen del medio filtrante en m³, y $F$ es el factor de recirculación que corrige el efecto de la dilución. Para la Ruta A, sin recirculación, el factor $F = 1.0$.

El término $W/(V \cdot F)$ representa la carga orgánica volumétrica efectiva aplicada al sistema. El modelo predice que la eficiencia de remoción disminuye conforme aumenta esta carga, lo cual es consistente con la cinética de sistemas biológicos donde la capacidad de remoción se satura a altas cargas de substrato.

Para el dimensionamiento, se establece una carga orgánica volumétrica de diseño $C_v = {bf['Cv_diseno_kg_m3_d']:.2f}$ kg DBO/m³·d, valor conservador dentro del rango recomendado para biofiltros con medio plástico operando a temperaturas tropicales. El volumen de medio requerido resulta:

\begin{{equation}}
V = \frac{{W}}{{C_v}} = \frac{{{bf['W_kg_d']:.2f}}}{{{bf['Cv_diseno_kg_m3_d']:.2f}}} = {bf['V_medio_m3']:.1f}\ \text{{m}}^3
\end{{equation}}
\captionequation{{Volumen de medio filtrante por criterio de carga orgánica -- Ruta A}}

Con una profundidad de medio $D = {bf['D_medio_m']:.2f}$ m, el área superficial del biofiltro y su diámetro equivalente resultan:

\begin{{equation}}
A_s = \frac{{V}}{{D}} = \frac{{{bf['V_medio_m3']:.1f}}}{{{bf['D_medio_m']:.2f}}} = {bf['A_sup_m2']:.2f}\ \text{{m}}^2 \quad \Rightarrow \quad D_{{\text{{bf}}}} = \sqrt{{\frac{{4A_s}}{{\pi}}}} = {bf['D_bf_m']:.2f}\ \text{{m}}
\end{{equation}}

La carga hidráulica superficial, definida como el caudal aplicado por unidad de área, resulta:

\begin{{equation}}
\text{{CHS}} = \frac{{Q}}{{A_s}} = \frac{{{bf['Q_m3_d']:.1f}}}{{{bf['A_sup_m2']:.2f} \times 24}} = {bf['CHS_m3_m2_h']:.3f}\ \text{{m}}^3\text{{/m}}^2\text{{·h}}
\end{{equation}}
\captionequation{{Carga hidráulica superficial del biofiltro -- Ruta A}}

Este valor de CHS se encuentra dentro del rango operacional recomendado de {cfg.bf_cmh_CHS_min_m3_m2_h:.1f} a {cfg.bf_cmh_CHS_max_m3_m2_h:.1f} m³/m²·h, garantizando una distribución uniforme del afluente y un riego adecuado de la biopelícula sin producir arrastre excesivo de biomasa.""" if ruta == "A" else rf"""

\subsubsection*{{Modelo de Diseño Germain -- Ruta B (con recirculación)}}

Para la Ruta B se utiliza el modelo cinético desarrollado por Germain (1966) para biofiltros con medio plástico estructurado y recirculación. Este modelo describe la remoción de DBO$_5$ mediante una cinética de primer orden que incorpora el efecto de la recirculación sobre la concentración afluente diluida y la carga hidráulica total aplicada.

El modelo Germain parte de la observación experimental de que la remoción de substrato en biofiltros con medio plástico sigue una cinética proporcional a la concentración remanente, pero modulada por la tasa hidráulica. La forma matemática del modelo es:

\begin{{equation}}
\frac{{S_e}}{{S_0'}} = \exp\!\left(-\frac{{k_T \cdot D}}{{Q_T^n}}\right)
\end{{equation}}
\captionequation{{Modelo de Germain para biofiltro con recirculación -- Ruta B}}

Donde $S_e$ es la concentración de DBO$_5$ en el efluente, $S_0'$ es la concentración afluente diluida por la recirculación, $k_T$ es la constante cinética corregida por temperatura, $D$ es la profundidad del medio, $Q_T$ es la carga hidráulica superficial total (con recirculación), y $n$ es un exponente empírico que depende del tipo de medio ($n = 0.50$ para medio plástico).

La recirculación cumple tres funciones fundamentales en el biofiltro: (1) diluye la concentración de DBO$_5$ del afluente crudo, reduciendo la carga orgánica puntual y previniendo la sobrecarga del sistema; (2) aumenta la carga hidráulica superficial, promoviendo un riego más uniforme de la biopelícula y previniendo su desecación durante períodos de bajo caudal; y (3) mejora la distribución del flujo a través del medio, reduciendo la formación de canales preferenciales.

La concentración afluente diluida por efecto de la recirculación se calcula como:

\begin{{equation}}
S_0' = \frac{{S_0}}{{1 + R}} = \frac{{{bf['DBO_entrada_mg_L']:.1f}}}{{1 + {bf['R_recirculacion']:.1f}}} = {bf['S0_prima_mg_L']:.1f}\ \text{{mg/L}}
\end{{equation}}
\captionequation{{Concentración afluente diluida por recirculación}}

La relación de recirculación adoptada $R = {bf['R_recirculacion']:.1f}$ significa que por cada unidad de caudal afluente, se recircula {bf['R_recirculacion']:.1f} unidades de efluente tratado, resultando en un caudal total aplicado al filtro de:

\begin{{equation}}
Q_T = Q \cdot (1 + R) = {bf['Q_m3_h']:.2f} \times {1+bf['R_recirculacion']:.1f} = {bf['Q_T_m3_h']:.2f}\ \text{{m}}^3\text{{/h}} = {bf['Q_R_m3_d']:.1f}\ \text{{m}}^3\text{{/d}}
\end{{equation}}
\captionequation{{Caudal total aplicado incluyendo recirculación}}

El caudal de recirculación requiere bombeo desde la salida del biofiltro (o del clarificador secundario) hacia la entrada del distribuidor rotatorio. La potencia requerida para este bombeo debe considerarse en el balance energético de la planta.

Para el dimensionamiento, se establece una carga orgánica volumétrica de diseño $C_v = {bf['Cv_diseno_kg_m3_d']:.2f}$ kg DBO/m³·d, apropiada para biofiltros de alta carga con recirculación. El volumen de medio resulta:

\begin{{equation}}
V = \frac{{W}}{{C_v}} = \frac{{{bf['W_kg_d']:.2f}}}{{{bf['Cv_diseno_kg_m3_d']:.2f}}} = {bf['V_medio_m3']:.1f}\ \text{{m}}^3
\end{{equation}}
\captionequation{{Volumen de medio filtrante por criterio de carga orgánica -- Ruta B}}

El área superficial y el diámetro equivalente del biofiltro resultan:

\begin{{equation}}
A_s = \frac{{V}}{{D}} = \frac{{{bf['V_medio_m3']:.1f}}}{{{bf['D_medio_m']:.2f}}} = {bf['A_sup_m2']:.2f}\ \text{{m}}^2 \quad \Rightarrow \quad D_{{\text{{bf}}}} = \sqrt{{\frac{{4A_s}}{{\pi}}}} = {bf['D_bf_m']:.2f}\ \text{{m}}
\end{{equation}}

La carga hidráulica superficial total, considerando el caudal con recirculación, es:

\begin{{equation}}
\text{{CHS}} = \frac{{Q_T}}{{A_s}} = \frac{{{bf['Q_T_m3_h']:.2f}}}{{{bf['A_sup_m2']:.2f}}} = {bf['CHS_m3_m2_h']:.3f}\ \text{{m}}^3\text{{/m}}^2\text{{·h}}
\end{{equation}}
\captionequation{{Carga hidráulica superficial total con recirculación}}

Este valor de CHS garantiza un riego intensivo del medio, manteniendo la biopelícula húmeda y activa incluso durante períodos de bajo caudal.""") + rf"""

\subsubsection*{{Geometría Completa del Biofiltro}}

La altura total del biofiltro incluye componentes constructivas adicionales al medio filtrante, necesarias para el funcionamiento hidráulico y la operación del sistema. El desglose de alturas se presenta en la Tabla~\ref{{tab:alturas_taf}}.

\begin{{table}}[H]
\centering
\caption{{Desglose de alturas constructivas -- Biofiltro TAF}}
\label{{tab:alturas_taf}}
\begin{{tabular}}{{lccc}}
\toprule
\textbf{{Componente}} & \textbf{{Símbolo}} & \textbf{{Altura (m)}} & \textbf{{Función}} \\
\midrule
Espacio distribuidor--medio & $H_{{\text{{dist}}}}$ & {bf['H_distribucion_m']:.2f} & Distribución hidráulica \\
Profundidad del medio & $D$ & {bf['D_medio_m']:.2f} & Soporte biopelícula \\
Sistema underdrain & $H_{{\text{{under}}}}$ & {bf['H_underdrain_m']:.2f} & Drenaje y ventilación \\
Bordo libre & $H_{{\text{{borde}}}}$ & {bf['H_bordo_libre_m']:.2f} & Seguridad operacional \\
\midrule
\textbf{{Altura total}} & $\mathbf{{H_{{\text{{total}}}}}}$ & $\mathbf{{{bf['H_total_m']:.2f}}}$ & -- \\
\bottomrule
\end{{tabular}}
\end{{table}}

El espacio entre el distribuidor rotatorio y la superficie del medio ($H_{{\text{{dist}}}} = {bf['H_distribucion_m']:.2f}$ m) permite que el agua se distribuya en forma de abanico antes de contactar el medio, garantizando un mojado uniforme. El sistema underdrain ($H_{{\text{{under}}}} = {bf['H_underdrain_m']:.2f}$ m) recolecta el efluente tratado y permite la entrada de aire para ventilación natural. El bordo libre ($H_{{\text{{borde}}}} = {bf['H_bordo_libre_m']:.2f}$ m) proporciona seguridad contra salpicaduras y alberga el crecimiento de biopelícula en la superficie.

\subsubsection*{{Sistema de Distribución Rotatorio}}

El sistema de distribución rotatorio es el componente que aplica el agua residual uniformemente sobre la superficie del medio filtrante. Consiste en una columna central hueca (pivot) conectada a brazos radiales que giran por acción de la fuerza de reacción del agua al salir por las boquillas.

Para este diseño se utilizan {bf['num_brazos']:.0f} brazos distribuidores, seleccionados en función del diámetro del biofiltro. El caudal total que llega al distribuidor es $Q_{{\text{{aplicado}}}} = {bf['Q_aplicado_m3_h']:.2f}$ m³/h, resultando en un caudal por brazo de:

\begin{{equation}}
Q_{{\text{{brazo}}}} = \frac{{Q_{{\text{{aplicado}}}}}}{{N_{{\text{{brazos}}}}}} = \frac{{{bf['Q_aplicado_m3_h']:.2f}}}{{{bf['num_brazos']:.0f}}} = {bf['Q_por_brazo_m3_h']:.2f}\ \text{{m}}^3\text{{/h}} = {bf['Q_por_brazo_m3_h']/3.6:.2f}\ \text{{L/s}}
\end{{equation}}
\captionequation{{Caudal por brazo del distribuidor rotatorio}}

La longitud de cada brazo corresponde al radio del biofiltro:

\begin{{equation}}
L_{{\text{{brazo}}}} = \frac{{D_{{\text{{bf}}}}}}{{2}} = \frac{{{bf['D_bf_m']:.2f}}}{{2}} = {bf['L_brazo_m']:.2f}\ \text{{m}}
\end{{equation}}

Cada brazo dispone de {bf['num_boquillas_por_brazo']:.0f} boquillas distribuidas uniformemente, con un caudal por boquilla de {bf['Q_por_boquilla_L_s']:.2f} L/s. El diámetro de orificio calculado para una velocidad de salida de {bf['v_boquilla_m_s']:.1f} m/s resulta $d_{{\text{{orificio}}}} = {bf['diam_orificio_mm']:.1f}$ mm, valor dentro del rango constructivo estándar para este tipo de distribuidores.

La velocidad de rotación del distribuidor depende del caudal aplicado y del par de reacción generado por las boquillas. Velocidades típicas oscilan entre 0.5 y 2.0 rpm, garantizando una distribución uniforme sin generar salpicaduras excesivas."""

    def generar_verificacion(self) -> str:
        """Genera subsection Verificación con todas las verificaciones."""
        cfg = self.cfg
        bf = self.datos
        ruta = bf['ruta_diseno']
        verifs = bf['verificaciones']

        return rf"""\subsection{{Verificación}}

\subsubsection*{{Verificación de Eficiencia de Remoción}}

El dimensionamiento por carga orgánica volumétrica establece el tamaño del biofiltro a partir de criterios empíricos, pero no garantiza por sí solo que el sistema alcanzará la calidad de efluente requerida. Por esta razón, es obligatoria la verificación de eficiencia mediante el modelo cinético correspondiente (NRC para Ruta A, Germain para Ruta B), que incorpora explícitamente la temperatura, la profundidad del medio y la tasa hidráulica aplicada.
""" + (rf"""
Para la Ruta A, aplicando el modelo NRC con los parámetros del diseño:

\begin{{equation}}
E_{{\text{{calculada}}}} = \frac{{1}}{{1 + 0.4432 \sqrt{{\dfrac{{W}}{{V \cdot F}}}}}} = \frac{{1}}{{1 + 0.4432 \sqrt{{\dfrac{{{bf['W_kg_d']:.2f}}}{{{bf['V_medio_m3']:.1f} \times {bf['F_recirculacion']:.3f}}}}}}} = {bf['E_calculada']:.3f}
\end{{equation}}
\captionequation{{Eficiencia de remoción calculada por modelo NRC}}

La concentración de DBO$_5$ en el efluente estimada resulta:

\begin{{equation}}
S_e = S_0 \cdot (1 - E) = {bf['DBO_entrada_mg_L']:.1f} \times (1 - {bf['E_calculada']:.3f}) = {bf['Se_calculada_mg_L']:.1f}\ \text{{mg/L}}
\end{{equation}}

La eficiencia calculada de {bf['E_calculada']*100:.1f}\% indica la capacidad de remoción del biofiltro para la carga aplicada.""" if ruta == "A" else rf"""
Para la Ruta B, aplicando el modelo de Germain con los parámetros del diseño, primero se corrige la constante cinética por temperatura:

\begin{{equation}}
k_T = k_{{20}} \cdot \theta^{{(T-20)}} = {bf['k_20_m_h']:.3f} \times {bf['theta']:.3f}^{{({bf['T_agua_C']:.1f}-20)}} = {bf['k_T_m_h']:.4f}\ \text{{m/h}}
\end{{equation}}
\captionequation{{Corrección de constante cinética por temperatura}}

La constante cinética corregida $k_T = {bf['k_T_m_h']:.4f}$ m/h refleja el aumento de la actividad microbiana a la temperatura de operación de {bf['T_agua_C']:.1f}°C, representando aproximadamente un {((bf['k_T_m_h']/bf['k_20_m_h']-1)*100):.1f}\% de incremento respecto al valor de referencia a 20°C.

Aplicando el modelo de Germain:

\begin{{equation}}
S_e = S_0' \cdot \exp\!\left(-\frac{{k_T \cdot D}}{{Q_T^n}}\right) = {bf['S0_prima_mg_L']:.1f} \times \exp\!\left(-\frac{{{bf['k_T_m_h']:.4f} \times {bf['D_medio_m']:.2f}}}{{({bf['CHS_m3_m2_h']:.3f})^{{{str(bf['n_germain'] or 'N/A')}}}}}\right) = {bf['Se_calculada_mg_L']:.1f}\ \text{{mg/L}}
\end{{equation}}
\captionequation{{Concentración efluente estimada por modelo de Germain}}

La eficiencia global del sistema, considerando la recirculación, resulta:

\begin{{equation}}
E = \frac{{S_0 - S_e}}{{S_0}} = \frac{{{bf['DBO_entrada_mg_L']:.1f} - {bf['Se_calculada_mg_L']:.1f}}}{{{bf['DBO_entrada_mg_L']:.1f}}} = {bf['E_calculada']:.3f} \approx {bf['E_calculada']*100:.1f}\%
\end{{equation}}

La eficiencia calculada de {bf['E_calculada']*100:.1f}\% refleja el desempeño esperado del biofiltro con los parámetros de diseño adoptados.""") + rf"""

\textbf{{Resultado de verificación:}} {bf['texto_eficiencia']}

\subsubsection*{{Verificación de Carga Orgánica Superficial}}

La carga orgánica superficial (COS) representa la masa de DBO$_5$ aplicada por unidad de volumen del medio por día. Es un parámetro crítico porque determina la densidad de biomasa que puede mantenerse activa en el sistema y el riesgo de colmatación por acumulación excesiva de biopelícula.

\begin{{equation}}
\text{{COS}} = \frac{{W}}{{V}} = \frac{{{bf['W_kg_d']:.2f}}}{{{bf['V_medio_m3']:.1f}}} = {bf['COS_kg_m3_d']:.3f}\ \text{{kg DBO/m}}^3\text{{·d}}
\end{{equation}}
\captionequation{{Carga orgánica superficial del biofiltro}}

El valor calculado de COS = {bf['COS_kg_m3_d']:.3f} kg/m³·d se encuentra {'dentro' if verifs['COS']['cumple'] else 'fuera'} del rango recomendado para biofiltros con medio plástico (hasta {cfg.bf_cmh_COS_max_kgDBO_m3_d:.2f} kg/m³·d). {'Esta carga garantiza el desarrollo de una biopelícula activa sin riesgo de colmatación prematura del medio.' if verifs['COS']['cumple'] else 'Se recomienda revisar el diseño para evitar sobrecarga orgánica del sistema.'}

\subsubsection*{{Verificación de Carga Hidráulica Superficial}}

La carga hidráulica superficial (CHS) determina la frecuencia de contacto entre el agua residual y la biopelícula, así como la velocidad de percolación a través del medio. Valores bajos pueden causar desecación de la biopelícula durante períodos de bajo caudal, mientras que valores altos pueden producir arrastre de biomasa y canalización del flujo.

\begin{{equation}}
\text{{CHS}} = \frac{{Q_{{\text{{aplicado}}}}}}{{A_s}} = {bf['CHS_m3_m2_h']:.3f}\ \text{{m}}^3\text{{/m}}^2\text{{·h}} = {bf['CHS_m3_m2_d']:.2f}\ \text{{m}}^3\text{{/m}}^2\text{{·d}}
\end{{equation}}
\captionequation{{Carga hidráulica superficial del biofiltro}}

La CHS calculada de {bf['CHS_m3_m2_h']:.3f} m³/m²·h ({bf['CHS_m3_m2_d']:.2f} m/d) se encuentra {'dentro' if verifs['CHS']['cumple'] else 'fuera'} del rango operacional recomendado ({cfg.bf_cmh_CHS_min_m3_m2_h:.1f}--{cfg.bf_cmh_CHS_max_m3_m2_h:.1f} m³/m²·h). {'Este valor garantiza un riego adecuado del medio y mantiene la biopelícula húmeda y activa.' if verifs['CHS']['cumple'] else 'Se recomienda ajustar el área o la recirculación para alcanzar valores dentro del rango óptimo.'}

\subsubsection*{{Tiempo de Retención Hidráulico}}

El tiempo de retención hidráulico (TRH) representa el tiempo medio que el agua residual permanece en contacto con la biopelícula. Aunque en biofiltros el TRH es corto (típicamente menos de 1 hora), este parámetro es indicativo de la intensidad del contacto entre el sustrato y los microorganismos.

\begin{{equation}}
\text{{TRH}} = \frac{{V}}{{Q_{{\text{{aplicado}}}}}} = \frac{{{bf['V_medio_m3']:.1f}}}{{{bf['Q_aplicado_m3_h']:.2f}}} = {bf['HRT_h']:.2f}\ \text{{h}}
\end{{equation}}
\captionequation{{Tiempo de retención hidráulico en el biofiltro}}

El TRH de {bf['HRT_h']:.2f} horas es característico de biofiltros de medio plástico con las cargas hidráulicas y orgánicas de este proyecto. A pesar de ser relativamente corto, la alta densidad de biopelícula y la eficiente transferencia de masa en el medio estructurado permiten lograr las eficiencias de remoción verificadas.

\subsubsection*{{Producción de Lodos Biológicos}}

El biofiltro genera lodos biológicos (humus) por el desprendimiento periódico de la biopelícula excedente. Esta producción de sólidos debe considerarse en el diseño del sedimentador secundario y en el manejo de lodos de la planta.

La producción de humus puede estimarse como una fracción de la DBO$_5$ removida:

\begin{{equation}}
P_{{\text{{humus}}}} = Y \cdot \Delta\text{{DBO}} = {cfg.bf_cmh_factor_produccion_humus:.2f} \times {bf['DBO_removida_kg_d']:.2f} = {bf['solidos_humus_kg_d']:.2f}\ \text{{kg SST/d}}
\end{{equation}}
\captionequation{{Producción de humus en el biofiltro TAF}}

Donde $Y = {cfg.bf_cmh_factor_produccion_humus:.2f}$ kg SST/kg DBO es el coeficiente de producción de humus típico para biofiltros, y $\Delta\text{{DBO}} = {bf['DBO_removida_kg_d']:.2f}$ kg/d es la DBO$_5$ removida en el sistema.

El lodo de humus producido en el biofiltro es relativamente estable aeróbicamente y puede ser manejado junto con los lodos del sedimentador secundario. La producción estimada de {bf['solidos_humus_kg_d']:.2f} kg SST/d representa una carga adicional de sólidos que debe acumularse o disponerse adecuadamente."""

    def generar_resultados(self) -> str:
        """Genera subsection Resultados con tabla consolidada y figura."""
        cfg = self.cfg
        bf = self.datos
        ruta = bf['ruta_diseno']

        # ── ruta de figura ──────────────────────────────────────────
        if os.path.isabs(self.ruta_figuras):
            output_dir      = self.ruta_figuras
            latex_ruta_base = 'figuras'
        else:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'resultados', self.ruta_figuras
            )
            latex_ruta_base = self.ruta_figuras

        fig_path = self.generar_esquema_matplotlib(output_dir)

        if fig_path:
            fig_relativa = (latex_ruta_base + '/' + os.path.basename(fig_path)).replace('\\', '/')
        else:
            fig_relativa = None

        # ── filas específicas según ruta ───────────────────────────
        if ruta == "B":
            filas_ruta = rf"""\midrule
\multicolumn{{2}}{{l}}{{\textit{{Parámetros de recirculación (Ruta B)}}}} \\
Razón de recirculación & $R = {bf['R_recirculacion']:.1f}$ \\
DBO afluente diluida & $S_0' = {bf['S0_prima_mg_L']:.1f}$ mg/L \\
Caudal de recirculación & $Q_R = {bf['Q_R_m3_d']:.1f}$ m³/d \\
Caudal total aplicado & $Q_T = {bf['Q_T_m3_h']:.2f}$ m³/h \\
"""
        else:
            filas_ruta = ""

        # ── bloque de figura ───────────────────────────────────────
        if fig_relativa:
            ruta_label = "A -- NRC (sin recirculación)" if ruta == "A" \
                         else "B -- Germain (con recirculación)"
            bloque_fig = rf"""
La figura siguiente presenta el corte transversal del biofiltro TAF, con sus componentes principales: distribuidor rotatorio, medio filtrante con biopelícula, sistema underdrain con ventilación natural y{',' if ruta == 'B' else ''} conexiones hidráulicas{' y bomba de recirculación' if ruta == 'B' else ''}.

\begin{{figure}}[H]
\centering
\includegraphics[width=\textwidth]{{{fig_relativa}}}
\caption{{Esquema del biofiltro TAF -- Ruta {ruta_label}. Diámetro: {bf['D_bf_m']:.2f}~m, profundidad de medio: {bf['D_medio_m']:.2f}~m, altura total: {bf['H_total_m']:.2f}~m, CHS: {bf['CHS_m3_m2_h']:.3f}~m³/m²·h, eficiencia DBO$_5$: {bf['E_calculada']*100:.0f}\%.}}
\label{{fig:esquema_biofiltro_taf_ruta{ruta.lower()}}}
\end{{figure}}

El esquema ilustra el recorrido del agua residual desde su entrada al distribuidor rotatorio, la percolación descendente a través del medio filtrante con biopelícula aerobia, y la recolección del efluente tratado en el sistema underdrain. Las aberturas laterales permiten la circulación natural de aire de abajo hacia arriba, manteniendo las condiciones aerobias necesarias para la biopelícula.{' La bomba de recirculación devuelve una fracción $R=' + str(bf.get('R_recirculacion','')) + '$ del efluente a la entrada del distribuidor, diluyendo el afluente y aumentando la carga hidráulica sobre el medio.' if ruta == 'B' else ''}"""
        else:
            bloque_fig = r"\textit{(Figura del biofiltro no generada -- verificar instalación de matplotlib.)}"

        return rf"""\subsection{{Resultados}}

La Tabla~\ref{{tab:resumen_taf}} consolida los parámetros geométricos, hidráulicos, de carga y de calidad del efluente del biofiltro TAF dimensionado, permitiendo una lectura integrada de los resultados del diseño.

\begingroup
\small
\begin{{longtable}}{{ll}}
\caption{{Resumen de resultados del dimensionamiento -- Biofiltro TAF (Ruta {ruta})}}
\label{{tab:resumen_taf}}\\
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} \\
\midrule
\endfirsthead
\caption[]{{Resumen de resultados del dimensionamiento -- Biofiltro TAF (Ruta {ruta}) (continuación)}}\\
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} \\
\midrule
\endhead
\midrule
\multicolumn{{2}}{{r}}{{\textit{{Continúa en la siguiente página}}}} \\
\endfoot
\bottomrule
\endlastfoot
\multicolumn{{2}}{{l}}{{\textit{{Características del afluente}}}} \\
Caudal promedio & {bf['Q_m3_d']:.1f} m³/d \\
Caudal máximo horario & {bf['Q_max_m3_d']:.1f} m³/d \\
DBO$_5$ afluente & {bf['DBO_entrada_mg_L']:.1f} mg/L \\
Carga orgánica & {bf['W_kg_d']:.2f} kg DBO/d \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Metodología de diseño}}}} \\
Ruta seleccionada & {ruta} ({bf['modelo_usado']}) \\
Criterio de selección & {bf['criterio_seleccion']} \\
{filas_ruta}\midrule
\multicolumn{{2}}{{l}}{{\textit{{Dimensionamiento}}}} \\
Volumen de medio & {bf['V_medio_m3']:.1f} m³ \\
Área superficial & {bf['A_sup_m2']:.2f} m² \\
Diámetro & {bf['D_bf_m']:.2f} m \\
Profundidad del medio & {bf['D_medio_m']:.2f} m \\
Altura total & {bf['H_total_m']:.2f} m \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Cargas de operación}}}} \\
Carga orgánica volumétrica (COS) & {bf['COS_kg_m3_d']:.3f} kg/m³·d \\
Carga hidráulica superficial (CHS) & {bf['CHS_m3_m2_h']:.3f} m³/m²·h \\
Tiempo de retención hidráulico & {bf['HRT_h']:.2f} h \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Desempeño esperado}}}} \\
Eficiencia de remoción DBO$_5$ & {bf['E_calculada']*100:.1f}\% \\
DBO$_5$ efluente calculada & {bf['Se_calculada_mg_L']:.1f} mg/L \\
DBO$_5$ removida & {bf['DBO_removida_kg_d']:.2f} kg/d \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Sistema de distribución}}}} \\
Número de brazos & {bf['num_brazos']:.0f} \\
Caudal por brazo & {bf['Q_por_brazo_m3_h']:.2f} m³/h \\
Longitud de brazo & {bf['L_brazo_m']:.2f} m \\
Número de boquillas/brazo & {bf['num_boquillas_por_brazo']:.0f} \\
Diámetro de orificio & {bf['diam_orificio_mm']:.1f} mm \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Producción de lodos}}}} \\
Humus generado & {bf['solidos_humus_kg_d']:.2f} kg SST/d \\
SST efluente estimado & {bf['SST_efluente_estimado_mg_L']:.1f} mg/L \\
\end{{longtable}}
\endgroup

\subsubsection*{{Conclusiones del Diseño}}

El biofiltro de carga mecanizada hidráulica ha sido dimensionado siguiendo la \textbf{{Ruta {ruta}}} del manual técnico, utilizando el {bf['modelo_usado']}. La geometría principal del sistema resulta:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item Diámetro: {bf['D_bf_m']:.2f} m
    \item Altura total: {bf['H_total_m']:.2f} m
    \item Volumen de medio filtrante: {bf['V_medio_m3']:.1f} m³
    \item Área superficial: {bf['A_sup_m2']:.2f} m²
\end{{itemize}}

El desempeño esperado del sistema, verificado mediante el modelo cinético correspondiente, indica:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item Eficiencia de remoción de DBO$_5$: {bf['E_calculada']*100:.1f}\%
    \item DBO$_5$ del efluente: {bf['Se_calculada_mg_L']:.1f} mg/L

\end{{itemize}}

{bf['texto_eficiencia']} El sistema incluye distribución rotatoria con {bf['num_brazos']:.0f} brazos, sistema underdrain para drenaje y ventilación natural, y produce aproximadamente {bf['solidos_humus_kg_d']:.2f} kg SST/d de humus que requiere separación en sedimentador secundario.

{bloque_fig}"""


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    import sys
    import subprocess
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_dir)

    from ptar_dimensionamiento import ConfigDiseno, dimensionar_biofiltro_carga_mecanizada_hidraulica

    print("=" * 70)
    print("TEST - GENERADOR MODULAR DE BIOFILTRO TAF")
    print("=" * 70)

    cfg = ConfigDiseno()
    print(f"\n[1] Q_linea = {cfg.Q_linea_L_s} L/s")
    print(f"[1] T_agua = {cfg.T_agua_C} °C")

    # DBO de entrada tipica tras UASB (70% remocion)
    DBO_in = cfg.DBO5_mg_L * 0.30
    print(f"[2] DBO entrada al TAF = {DBO_in:.1f} mg/L")

    resultados_dir = os.path.join(base_dir, 'resultados', 'test_modular')
    figuras_dir    = os.path.join(resultados_dir, 'figuras')
    os.makedirs(figuras_dir, exist_ok=True)

    # Probar ambas rutas
    for ruta in ["A", "B"]:
        print(f"\n{'='*70}")
        print(f"RUTA {ruta}")
        print(f"{'='*70}")

        datos = dimensionar_biofiltro_carga_mecanizada_hidraulica(
            cfg,
            DBO_entrada_mg_L=DBO_in,
            ruta_diseno=ruta
        )

        print(f"[3] Ruta: {datos['ruta_diseno']} - {datos['modelo_usado']}")
        print(f"[3] Criterio: {datos['criterio_seleccion']}")
        print(f"[3] Dimensiones: D={datos['D_bf_m']:.2f}m, H={datos['H_total_m']:.2f}m")
        print(f"[3] Volumen medio: {datos['V_medio_m3']:.1f} m³")
        print(f"[3] COS: {datos['COS_kg_m3_d']:.3f} kg/m³·d")
        print(f"[3] CHS: {datos['CHS_m3_m2_h']:.3f} m³/m²·h")
        print(f"[3] Eficiencia: {datos['E_calculada']*100:.1f}%")
        print(f"[3] Se calculada: {datos['Se_calculada_mg_L']:.1f} mg/L")

        # Generar figura directamente para test
        gen = GeneradorBiofiltroCargaMecanizadaHidraulica(cfg, datos,
                                                          ruta_figuras=figuras_dir)
        fig_path = gen.generar_esquema_matplotlib(figuras_dir)
        if fig_path:
            print(f"[4] Figura generada: {fig_path}")
        else:
            print("[4] Figura no generada (matplotlib no disponible)")

        # Generar LaTeX
        latex = gen.generar_completo()

        tex_path = os.path.join(resultados_dir, f'biofiltro_taf_ruta_{ruta.lower()}_test.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex)
        print(f"[5] LaTeX generado: {len(latex)} chars -> {tex_path}")

        # Documento completo para compilación
        doc_path = os.path.join(resultados_dir,
                                f'biofiltro_taf_ruta_{ruta.lower()}_test_completo.tex')
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

\newcommand{\captionequation}[1]{}

\begin{document}

\section{Biofiltro de Carga Mecanizada Hidraulica (TAF) - Ruta """ + ruta + r"""}

""" + latex + r"""

\end{document}""")
        print(f"[6] Documento completo: {doc_path}")

        # Compilar PDF
        print("[7] Compilando PDF...")
        try:
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode',
                 '-output-directory', resultados_dir, doc_path],
                capture_output=True, text=True, timeout=30
            )
            pdf_path = os.path.join(
                resultados_dir,
                f'biofiltro_taf_ruta_{ruta.lower()}_test_completo.pdf'
            )
            if os.path.exists(pdf_path):
                print(f"    PDF generado: {pdf_path}")
        except Exception as e:
            print(f"    ERROR: {e}")

    print("\n" + "=" * 70)
    print("TEST COMPLETADO")
    print("=" * 70)
