#!/usr/bin/env python3
"""
GENERADOR LaTeX - UNIDAD: HUMEDAL ARTIFICIAL DE FLUJO VERTICAL (HAFV)

Metodología Unificada: Sistema Clásico (Ruta A) y Sistema Francés Tropical (Ruta B)
Verificación k-C* obligatoria en ambas rutas (Kadlec & Wallace, 2009)

Organizado en 3 subsections: Dimensionamiento, Verificación, Resultados
"""

import os
import sys
import math

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GeneradorHumedalVertical:
    """Generador LaTeX para Humedal Artificial de Flujo Vertical (HAFV).

    Args:
        cfg: Configuracion de diseno
        datos: Resultados del dimensionamiento
        ruta_figuras: Ruta base donde se guardan las figuras (default: 'resultados/figuras')
    """

    def __init__(self, cfg, datos, ruta_figuras='resultados/figuras'):
        self.cfg = cfg
        self.datos = datos
        self.ruta_figuras = ruta_figuras

    def generar_completo(self) -> str:
        """Genera todo el contenido LaTeX del humedal en 3 subsections."""
        return "\n\n".join([
            self.generar_descripcion(),
            self.generar_verificacion(),
            self.generar_resultados()
        ])

    def _generar_esquema_png_old(self):
        """Genera el esquema técnico profesional del humedal como imagen PNG."""
        try:
            from PIL import Image, ImageDraw, ImageFont

            os.makedirs(self.ruta_figuras, exist_ok=True)
            ruta_salida = os.path.join(self.ruta_figuras, 'humedal_vertical_esquema.png')

            # Dimensiones de imagen más grandes para mejor calidad
            width, height = 1200, 900
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)

            # Colores profesionales
            c_negro = (0, 0, 0)
            c_gris_oscuro = (60, 60, 60)
            c_verde_planta = (34, 139, 34)
            c_verde_claro = (144, 238, 144)
            c_gris_claro = (220, 220, 220)
            c_gris = (150, 150, 150)
            c_gris_medio = (180, 180, 180)
            c_marron_claro = (210, 180, 140)
            c_marron = (139, 119, 101)
            c_marron_oscuro = (101, 67, 33)
            c_azul = (70, 130, 180)
            c_azul_claro = (173, 216, 230)
            c_naranja = (255, 165, 0)
            c_rojo = (220, 20, 60)
            c_pvc = (50, 50, 50)

            r = self.datos
            n_filtros = r['n_filtros_resultados']
            ciclo_alim = r['ciclo_alim_resultados_dias']
            ciclo_reposo = r['ciclo_reposo_resultados_dias']
            estados_filtros = r['estados_filtros_esquema']
            dims = r['dimensiones_por_filtro_m']

            # ============================================
            # VISTA EN PLANTA (parte superior)
            # ============================================
            y_planta = 100
            alto_filtro = 160
            ancho_filtro = 200
            separacion = 80

            ancho_total_filtros = n_filtros * ancho_filtro + (n_filtros - 1) * separacion
            inicio_x = (width - ancho_total_filtros) // 2

            # Título de vista en planta
            draw.text((width//2 - 200, 30),
                     f"VISTA EN PLANTA - {r['sistema'].upper()}",
                     fill=c_negro)
            draw.text((width//2 - 150, 55),
                     f"({n_filtros} filtros en operación alternada)",
                     fill=c_gris_oscuro)

            # Dibujar filtros
            for i in range(n_filtros):
                x1 = inicio_x + i * (ancho_filtro + separacion)
                y1 = y_planta
                x2 = x1 + ancho_filtro
                y2 = y1 + alto_filtro

                # Borde del filtro (muro de contención)
                draw.rectangle([x1, y1, x2, y2], outline=c_negro, width=3)

                # Relleno con patrón de vegetación
                for y in range(y1 + 5, y2 - 5, 8):
                    for x in range(x1 + 5, x2 - 5, 12):
                        # Dibujar pequeñas "plantas" como líneas verticales
                        draw.line([(x, y), (x, y-6)], fill=c_verde_planta, width=2)
                        # Hojas
                        draw.line([(x-2, y-3), (x+2, y-3)], fill=c_verde_claro, width=1)

                # Líneas diagonales de patrón
                for j in range(0, alto_filtro, 20):
                    draw.line([(x1+5, y1+j), (x2-5, y1+j+15)],
                             fill=(100, 180, 100), width=1)

                # Número de filtro
                draw.rectangle([x1 + ancho_filtro//2 - 35, y1 + 5,
                               x1 + ancho_filtro//2 + 35, y1 + 30],
                              fill='white', outline=c_negro, width=1)
                draw.text((x1 + ancho_filtro//2 - 25, y1 + 10),
                         f"MÓDULO {i+1}", fill=c_negro)

                # Estado del filtro
                estado_filtro = estados_filtros[i]
                estado = estado_filtro['estado']
                dias = f"{estado_filtro['duracion_dias']:.1f} dias"
                if estado == "ALIMENTANDO":
                    color_estado = c_azul
                    # Flecha azul indicando alimentación
                    draw.polygon([(x1 + ancho_filtro//2, y1 - 25),
                                 (x1 + ancho_filtro//2 - 10, y1 - 10),
                                 (x1 + ancho_filtro//2 + 10, y1 - 10)],
                                fill=c_azul)
                else:
                    color_estado = c_naranja

                # Indicador de estado (círculo coloreado)
                cy = y1 + 50
                draw.ellipse([x1 + 15, cy - 8, x1 + 31, cy + 8],
                            fill=color_estado, outline=c_negro, width=1)
                draw.text((x1 + 40, cy - 6), estado, fill=color_estado)
                draw.text((x1 + 40, cy + 8), dias, fill=c_gris_oscuro)

                # Dimensiones del filtro
                draw.text((x1 + 20, y2 - 40),
                         f"{dims[0]:.1f} m x {dims[1]:.1f} m",
                         fill=c_gris_oscuro)

                # Sistema de distribución (tubería)
                draw.rectangle([x1 + 20, y1 + alto_filtro//2 - 3,
                               x2 - 20, y1 + alto_filtro//2 + 3],
                              fill=c_pvc, outline=c_negro, width=1)
                # Boquillas
                for bx in range(x1 + 30, x2 - 20, 25):
                    draw.ellipse([bx - 3, y1 + alto_filtro//2 - 5,
                                 bx + 3, y1 + alto_filtro//2 + 5],
                                fill=c_azul_claro, outline=c_azul, width=1)

            # Flecha de entrada principal
            flecha_x = inicio_x - 100
            flecha_y = y_planta + alto_filtro//2
            # Cuerpo de la flecha
            draw.polygon([(flecha_x, flecha_y-12),
                         (flecha_x+40, flecha_y),
                         (flecha_x, flecha_y+12)], fill=c_azul, outline=c_negro)
            # Línea de flujo
            draw.line([(flecha_x - 60, flecha_y), (flecha_x, flecha_y)],
                     fill=c_azul, width=3)
            draw.text((flecha_x - 110, flecha_y - 8),
                     "Entrada\nagua residual", fill=c_negro)

            # Colector de distribución
            draw.rectangle([inicio_x - 20, flecha_y - 8,
                           inicio_x + 10, flecha_y + 8],
                          fill=c_gris, outline=c_negro, width=2)

            # Flecha de salida
            fin_x = inicio_x + ancho_total_filtros
            draw.polygon([(fin_x + 60, flecha_y-12),
                         (fin_x + 20, flecha_y),
                         (fin_x + 60, flecha_y+12)],
                        fill=(50, 150, 50), outline=c_negro)
            draw.line([(fin_x + 60, flecha_y), (fin_x + 100, flecha_y)],
                     fill=(50, 150, 50), width=3)
            draw.text((fin_x + 105, flecha_y - 8),
                     "Salida\nagua tratada", fill=c_negro)

            # Leyenda de operación
            leyenda_y = y_planta + alto_filtro + 30
            draw.text((width//2 - 250, leyenda_y),
                     r['texto_operacion_figura'],
                     fill=c_negro)

            # ============================================
            # SECCIÓN TRANSVERSAL (parte inferior)
            # ============================================
            y_seccion = leyenda_y + 60

            draw.text((width//2 - 220, y_seccion - 30),
                     "SECCIÓN TRANSVERSAL TÍPICA (ESCALA NO UNIFORME)", fill=c_negro)

            # Dimensiones del corte
            sec_x1 = 150
            sec_x2 = width - 150
            sec_ancho = sec_x2 - sec_x1

            # Alturas de cada capa (en píxeles, proporcional)
            h_borde_libre = 50
            h_grava_fina = 80   # ~0.30-0.40m
            h_grava_media = 60  # ~0.30m
            h_grava_drenaje = 50 # ~0.25m
            h_base = 20

            y_techo = y_seccion + 20
            y_base_total = y_techo + h_borde_libre + h_grava_fina + h_grava_media + h_grava_drenaje + h_base

            # Dibujar capas de abajo hacia arriba

            # 1. Capa de drenaje (grava gruesa 20-60mm)
            y1 = y_base_total - h_base
            y2 = y1 - h_grava_drenaje
            for y in range(int(y2), int(y1), 4):
                for x in range(sec_x1, sec_x2, 6):
                    # Piedras irregulares
                    tam = 3 + (x % 4)
                    color_piedra = (100 + (x*y)%40, 100 + (x*y)%40, 100 + (x*y)%40)
                    draw.ellipse([x, y, x+tam, y+tam], fill=color_piedra, outline=c_gris_oscuro)
            draw.rectangle([sec_x1, y2, sec_x2, y1], outline=c_negro, width=2)

            # Tubo colector de drenaje
            tubo_y = (y1 + y2) // 2
            draw.rectangle([sec_x1 + 30, tubo_y - 8, sec_x2 - 30, tubo_y + 8],
                          fill=c_pvc, outline=c_negro, width=2)
            # Perforaciones del tubo
            for px in range(sec_x1 + 40, sec_x2 - 30, 20):
                draw.ellipse([px - 2, tubo_y - 3, px + 2, tubo_y + 3], fill=c_azul)
            draw.text((sec_x2 - 200, tubo_y - 6), "Tubo colector drenaje Ø50mm", fill='white')

            # Etiqueta capa drenaje
            draw.text((sec_x2 + 10, (y1 + y2)//2 - 8),
                     "Capa drenaje\nGrava 20-60mm\n(0.25m)", fill=c_gris_oscuro)

            # 2. Capa de transición (grava media 5-15mm)
            y3 = y2 - h_grava_media
            for y in range(int(y3), int(y2), 3):
                for x in range(sec_x1, sec_x2, 5):
                    tam = 2 + (x % 3)
                    color_piedra = (130 + (x*y)%30, 130 + (x*y)%30, 130 + (x*y)%30)
                    draw.ellipse([x, y, x+tam, y+tam], fill=color_piedra, outline=c_gris)
            draw.rectangle([sec_x1, y3, sec_x2, y2], outline=c_negro, width=2)
            draw.text((sec_x2 + 10, (y2 + y3)//2 - 8),
                     "Capa media\nGrava 5-15mm\n(0.30m)", fill=c_gris_oscuro)

            # 3. Capa de filtración (grava fina 2-6mm)
            y4 = y3 - h_grava_fina
            for y in range(int(y4), int(y3), 2):
                for x in range(sec_x1, sec_x2, 4):
                    tam = 1 + (x % 2)
                    color_piedra = (160 + (x*y)%20, 150 + (x*y)%20, 130 + (x*y)%20)
                    draw.ellipse([x, y, x+tam, y+tam], fill=color_piedra, outline=c_marron)
            draw.rectangle([sec_x1, y4, sec_x2, y3], outline=c_negro, width=2)
            draw.text((sec_x2 + 10, (y3 + y4)//2 - 15),
                     "Capa filtración\nGrava 2-6mm\n(0.30-0.40m)", fill=c_gris_oscuro)

            # Sistema de distribución superior
            y_dist = y4 - 10
            draw.rectangle([sec_x1 + 20, y_dist - 5, sec_x2 - 20, y_dist + 5],
                          fill=c_pvc, outline=c_negro, width=2)
            # Boquillas de goteo
            for bx in range(sec_x1 + 40, sec_x2 - 20, 30):
                draw.line([(bx, y_dist + 5), (bx, y_dist + 12)], fill=c_azul, width=2)
                draw.ellipse([bx - 2, y_dist + 10, bx + 2, y_dist + 16], fill=c_azul_claro)
            draw.text((sec_x1 + 50, y_dist - 20),
                     "Sistema de distribución - Tubería PVC con boquillas de goteo", fill=c_negro)

            # Flechas de percolación vertical
            for fx in range(sec_x1 + 60, sec_x2 - 40, 80):
                # Flecha descendente
                draw.polygon([(fx, y_dist + 25), (fx - 4, y_dist + 35), (fx + 4, y_dist + 35)],
                            fill=c_azul)
                draw.line([(fx, y_dist + 20), (fx, y_dist + 50)], fill=c_azul, width=2)

            # Borde libre superior
            draw.rectangle([sec_x1, y_techo, sec_x2, y4],
                          fill=(240, 248, 255), outline=c_negro, width=2)
            draw.text((sec_x1 + 10, y_techo + 10),
                     "Borde libre (0.50-0.55m)", fill=c_gris_oscuro)

            # Línea de tierra exterior
            draw.line([(sec_x1 - 30, y_base_total), (sec_x1, y_base_total)],
                     fill=c_marron_oscuro, width=3)
            draw.line([(sec_x2, y_base_total), (sec_x2 + 30, y_base_total)],
                     fill=c_marron_oscuro, width=3)

            # Geomembrana (línea gruesa en el fondo)
            draw.line([(sec_x1, y_base_total), (sec_x2, y_base_total)],
                     fill=(30, 30, 30), width=4)
            draw.text((sec_x1 + 50, y_base_total + 5),
                     "Geomembrana impermeable", fill=c_gris_oscuro)

            # Vegetación (líneas verdes desde arriba)
            for vx in range(sec_x1 + 10, sec_x2 - 10, 15):
                altura_planta = 25 + (vx % 15)
                # Tallo
                draw.line([(vx, y_techo), (vx, y_techo - altura_planta)],
                         fill=c_verde_planta, width=2)
                # Hojas
                draw.line([(vx - 5, y_techo - altura_planta//2),
                          (vx + 5, y_techo - altura_planta//2 - 5)],
                         fill=c_verde_claro, width=2)
                draw.line([(vx - 5, y_techo - altura_planta//2 - 5),
                          (vx + 5, y_techo - altura_planta//2)],
                         fill=c_verde_claro, width=2)

            # Indicador de flujo
            draw.text((sec_x2 + 50, (y_dist + y_base_total)//2),
                     "Flujo\nvertical\ndescendente", fill=c_azul)
            draw.polygon([(sec_x2 + 40, (y_dist + y_base_total)//2 + 40),
                         (sec_x2 + 50, (y_dist + y_base_total)//2 + 55),
                         (sec_x2 + 60, (y_dist + y_base_total)//2 + 40)],
                        fill=c_azul)

            # Escalas
            escala_y = y_base_total + 40
            # Escala gráfica 0-2m
            draw.line([(sec_x1, escala_y), (sec_x1 + 200, escala_y)], fill=c_negro, width=2)
            for i in range(5):
                x = sec_x1 + i * 50
                h = 8 if i % 2 == 0 else 5
                draw.line([(x, escala_y), (x, escala_y + h)], fill=c_negro, width=2)
            draw.text((sec_x1, escala_y + 12), "0", fill=c_negro)
            draw.text((sec_x1 + 95, escala_y + 12), "1m", fill=c_negro)
            draw.text((sec_x1 + 190, escala_y + 12), "2m", fill=c_negro)
            draw.text((sec_x1 + 80, escala_y + 28), "ESCALA", fill=c_gris_oscuro)

            ruta_salida = os.path.join(self.ruta_figuras, 'humedal_vertical_esquema.png')
            img.save(ruta_salida, dpi=(150, 150))
            return ruta_salida

        except Exception as e:
            raise RuntimeError(f"Error generando figura de humedal vertical: {e}") from e

    def generar_descripcion(self) -> str:
        """Genera subsection Dimensionamiento con teoría y cálculos."""
        cfg = self.cfg
        r = self.datos

        ruta = r['ruta']

        renderizadores = {
            'B': self._generar_dimensionamiento_ruta_B,
            'A': self._generar_dimensionamiento_ruta_A,
        }
        return renderizadores[ruta](cfg, r)

    def _generar_dimensionamiento_ruta_B(self, cfg, r) -> str:
        """Dimensionamiento para Sistema Francés Tropical (Ruta B)."""
        OLR_adoptada = cfg.humedal_frances_OLR_gDQO_m2_d
        HLR_adoptada = cfg.humedal_frances_HLR_m_d
        area_por_PE = r['A_PE_m2'] / r['PE_carga']
        
        # Textos condicionales basados en temperatura
        T = r['T_agua_C']
        T_limite = cfg.humedal_temp_limite_transicion_C
        
        if T >= T_limite:
            texto_umbral = "que supera el umbral de"
            texto_sistema = "Sistema Francés Tropical"
            texto_actividad = "suficientemente intensa"
            texto_descripcion = "mineralizar el lodo superficial acumulado durante los ciclos de alimentación en tan solo 3.5 días de reposo, evitando la colmatación del lecho y permitiendo sostener cargas orgánicas e hidráulicas considerablemente más altas que en clima templado"
            texto_referencia = "10 a 15 años en sistemas franceses tropicales (Molle et al., 2015; Lombard-Latune et al., 2018)"
        else:
            texto_umbral = "inferior al umbral de"
            texto_sistema = "Sistema Clásico (Ruta A)"
            texto_actividad = "más lenta"
            texto_descripcion = "requerir períodos de reposo más prolongados (7 días o más por filtro). La configuración de dos etapas en serie distribuye la carga de forma decreciente: la primera etapa, más cargada, remueve la fracción principal de la DBO$_5$ soluble y suspendida; la segunda etapa actúa como unidad de pulido"
            texto_referencia = "instalaciones de clima templado (Cooper et al., 1996; ÖNORM B 2505, 2009)"

        return rf"""


El Humedal Artificial de Flujo Vertical (HAFV) es un sistema de tratamiento biológico extensivo en el que el agua residual percola verticalmente a través de un medio filtrante granular estratificado, dentro del cual se desarrolla una biopelícula microbiana densa responsable de la degradación de la materia orgánica carbonácea y la oxidación del nitrógeno amoniacal. A diferencia de los sistemas de flujo horizontal subsuperficial (HFHS), donde el agua atraviesa el lecho en sentido horizontal y predominan condiciones anóxicas, el HAFV opera en modo intermitente, alternando períodos de saturación del medio con períodos de drenaje y re-aireación natural. Este ciclo es el mecanismo fundamental que distingue al sistema y le confiere sus características de rendimiento.

Durante el pulso de alimentación, el agua residual se distribuye uniformemente sobre la superficie del filtro mediante un sistema de tuberías perforadas y percola gravitacionalmente hacia la capa de drenaje inferior. Durante este tránsito, los microorganismos del biofilm oxidan la materia orgánica en condiciones aerobias, consumen el oxígeno disuelto remanente y promueven la nitrificación del amonio. Concluido el pulso, el medio drena libremente y el aire penetra desde los tubos de ventilación del fondo y desde la superficie, restaurando las condiciones aerobias en el interior del lecho. Esta re-aireación pasiva, que ocurre sin ningún aporte de energía, es el rasgo que hace al HAFV un sistema energéticamente eficiente y operativamente robusto.

La vegetación macrófita (\textit{{Phragmites australis}} o equivalentes tropicales) que se establece sobre el lecho cumple una función auxiliar pero no menor: su sistema radicular crea micrositios aerobios en la zona superficial del medio, transfiere pequeñas cantidades de oxígeno hacia la rizosfera, previene la compactación de las capas superiores y contribuye al soporte estructural del lecho filtrante. Su contribución directa a la remoción de contaminantes es secundaria respecto a la actividad del biofilm, pero su rol en la estabilidad física y biológica del sistema a largo plazo es fundamental.

Los mecanismos de remoción de contaminantes en el HAFV, sus eficiencias típicas y los parámetros responsables se resumen en la Tabla~\ref{{tab:mecanismos_hafv}}.

\begin{{table}}[H]
\centering
\caption{{Mecanismos de remoción y eficiencias típicas en el HAFV (Kadlec \& Wallace, 2009; Cooper et al., 1996)}}
\label{{tab:mecanismos_hafv}}
\begin{{tabular}}{{p{{2.2cm}}p{{6.5cm}}cc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Mecanismo principal}} & \textbf{{Eficiencia típica}} & \textbf{{Unidad}} \\
\midrule
DBO$_5$ / DQO & Degradación aerobia y anóxica en biopelícula & 70 -- 90 & \% \\
SST & Filtración física en el medio granular & 80 -- 95 & \% \\
NH$_4$-N & Nitrificación aerobia (\textit{{Nitrosomonas/Nitrobacter}}) & 50 -- 80 & \% \\
NO$_3$-N & Limitada (condiciones principalmente aerobias) & 10 -- 30 & \% \\
Colif. fecales & Filtración, adsorción, radiación UV, oxidación & 1 -- 3 & log \\
Fósforo total & Adsorción en el medio (limitada a largo plazo) & 20 -- 40 & \% \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsubsection*{{Criterio de Selección del Sistemacon base a la  Temperatura}}

La selección entre las dos metodologías de diseño disponibles para el HAFV, el Sistema Clásico de doble etapa y el Sistema Francés Tropical de etapa única, se fundamenta en la temperatura del agua residual como criterio primario e indelegable. Esta dependencia no es arbitraria: la temperatura determina directamente la cinética de las reacciones biológicas en la biopelícula, la velocidad de mineralización aerobia de los sólidos retenidos en la capa superficial del filtro y, en consecuencia, la capacidad del sistema para soportar cargas orgánicas e hidráulicas elevadas sin colmatarse prematuramente.

El Sistema Clásico, documentado por Cooper et al. (1996) y la norma austriaca ÖNORM B 2505 (2009), fue desarrollado para condiciones de clima templado y frío (temperatura del agua residual entre 10 y 20\,°C), donde la mineralización del lodo superficial es lenta y obliga a aplicar cargas conservadoras y ciclos de reposo prolongados. Requiere configuración de dos etapas en serie, con tres filtros en paralelo en la primera etapa y dos en la segunda, y áreas de diseño del orden de 2 a 3\,m²/PE.

El Sistema Francés Tropical, desarrollado por el IRSTEA (\textit{{Institut National de Recherche en Sciences et Technologies pour l'Environnement et l'Agriculture}}) y validado mediante seguimientos de largo plazo en territorios tropicales de ultramar (Mayotte, Guayana Francesa, Reunión, Polinesia Francesa), aprovecha la alta temperatura para operar con una sola etapa de filtración, ciclos de reposo cortos de 3.5 días y cargas orgánicas e hidráulicas hasta tres veces superiores a las del sistema clásico. El resultado es un sistema hasta 70\,\% más compacto, con áreas del orden de 0.8 a 1.2\,m²/PE en clima tropical (Molle et al., 2015). La Tabla~\ref{{tab:comparacion_sistemas}} sintetiza las diferencias fundamentales entre ambas metodologías.

\begin{{table}}[H]
\centering
\caption{{Comparación de los sistemas de diseño del HAFV (Cooper et al., 1996; Molle et al., 2015)}}
\label{{tab:comparacion_sistemas}}
\begin{{tabular}}{{p{{4.8cm}}p{{4.2cm}}p{{4.2cm}}}}
\toprule
\textbf{{Característica}} & \textbf{{Sistema Clásico}} & \textbf{{Sistema Francés Tropical}} \\
\midrule
Temperatura de diseño & 10 -- 20\,°C & $>$ 20\,°C (óptimo 23 -- 30\,°C) \\
Número de etapas & 2 (1.ª + 2.ª) & 1 (etapa única) \\
Filtros por etapa & 3 en 1.ª, 2 en 2.ª & 2 en paralelo (mínimo) \\
Área por PE & 2.0 -- 3.0\,m²/PE & 0.8 -- 1.2\,m²/PE \\
COS de diseño & 20 -- 60\,g\,DBO$_5$/m²·d & 200 -- 350\,g\,DQO/m²·d \\
HLR de diseño & 0.02 -- 0.08\,m/d & 0.50 -- 0.75\,m/d \\
Ciclo alimentación/reposo & 3.5\,d\,/\,7\,d & 3.5\,d\,/\,3.5\,d \\
Mineralización del lodo & Lenta (clima frío) & Rápida (alta temperatura) \\
Referencia principal & Cooper (1996), ÖNORM & Molle et al. (2015) \\
\bottomrule
\end{{tabular}}
\end{{table}}

Para la temperatura del agua residual de \textbf{{{r['T_agua_C']:.1f}\,°C}} del presente proyecto, {texto_umbral} {cfg.humedal_temp_limite_transicion_C:.0f}\,°C, corresponde aplicar el \textbf{{{texto_sistema}}}. A esta temperatura, la actividad microbiana es {texto_actividad} para {texto_descripcion}. Esta elección está respaldada por los resultados de seguimientos de {texto_referencia}.

\subsubsection*{{Configuración del Sistema y Ciclo de Operación}}

El diseño contempla \textbf{{{r['n_filtros']} celdas por línea}} operando en modo alternado (operación alterna). Durante cada ciclo, una celda recibe el caudal completo de la línea ({cfg.Q_linea_L_s:.1f} L/s) mientras la otra permanece en reposo completo, con drenaje total del medio y libre circulación de aire desde el fondo hacia la superficie. El caudal no se divide entre las celdas: toda el agua va a la celda activa, y la celda en reposo recibe cero caudal durante su período de recuperación. Este esquema de operación alterna sirve tres propósitos complementarios: permite la re-aireación pasiva del lecho, facilita la mineralización aerobia de los sólidos acumulados en la capa superficial durante la alimentación, y distribuye el desgaste biológico y físico entre las celdas, extendiendo la vida útil del sistema. Cada celda está dimensionada con el área completa ($A_\text{{operando}}$) porque debe ser capaz de tratar todo el caudal de la línea cuando le corresponde operar.

El fundamento del ciclo de {r['ciclo_dias']}\,días totales ({r['ciclo_alim_dias']:.1f}\,días de alimentación y {r['ciclo_reposo_dias']:.1f}\,días de reposo por filtro) ha sido validado experimentalmente por Molle et al. (2015) en instalaciones de clima tropical con temperaturas medias del agua superiores a 22\,°C. A estas temperaturas, la tasa de mineralización aerobia del lodo superficial es suficiente para recuperar la permeabilidad del medio en el período de reposo disponible. El agua residual se aplica mediante pulsos intermitentes de corta duración (del orden de 10 minutos), a razón de 15 pulsos por día, lo que garantiza una distribución uniforme sobre toda la superficie del filtro, evita la formación de canales preferentes de flujo y provoca el efecto de succión-expulsión de aire que contribuye a la re-aireación interna del lecho.

Los parámetros de diseño adoptados para este proyecto, basados en los rangos validados para el sistema francés tropical (Molle et al., 2015), se presentan en la Tabla~\ref{{tab:parametros_frances}}.

\begin{{table}}[H]
\centering
\caption{{Parámetros de diseño adoptados -- Sistema Francés Tropical (Molle et al., 2015)}}
\label{{tab:parametros_frances}}
\begin{{tabular}}{{p{{5.0cm}}p{{5.2cm}}cc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Descripción}} & \textbf{{Valor adoptado}} & \textbf{{Unidad}} \\
\midrule
OLR & Carga orgánica superficial máxima (filtro activo) & {OLR_adoptada:.0f} & g\,DQO/m²·d \\
HLR & Carga hidráulica superficial máxima (filtro activo) & {HLR_adoptada:.2f} & m/d \\
$N_\text{{filtros}}$ & Número de filtros en paralelo & {r['n_filtros']} & -- \\
Ciclo alim./reposo & Período de rotación por filtro & {r['ciclo_alim_dias']:.1f}\,/\,{r['ciclo_reposo_dias']:.1f} & d \\
Área de referencia & Área mínima por habitante equivalente & {area_por_PE:.1f} & m²/PE \\
Profundidad del medio & Espesor total del lecho filtrante & 0.85 & m \\
Pulsos por día & Frecuencia de aplicación durante alimentación & 15 & pulsos/d \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsubsection*{{Medio Filtrante: Composición y Función de Cada Capa}}

El medio filtrante es el componente estructural y biológico central del HAFV. Su correcto diseño determina la permeabilidad hidráulica del sistema, el área específica disponible para el desarrollo de la biopelícula, la capacidad de retención de sólidos y la resistencia a la colmatación a largo plazo. Para el sistema francés tropical se adopta una configuración estratificada de tres capas, diferente a la del sistema clásico en su granulometría superficial:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item \textbf{{Capa superior de grava fina (2 -- 6\,mm, espesor 0.30\,m):}} Constituye la zona de contacto primario con el agua residual y de retención de sólidos. A diferencia del sistema clásico que usa arena en esta capa, el sistema francés emplea grava fina para mantener permeabilidad aun con acumulación superficial de lodo. La conductividad hidráulica saturada de esta capa (10 -- 90\,m/d) supera ampliamente el HLR de diseño ($\times$10 mínimo recomendado), garantizando percolación libre sin encharcamiento. Es también la zona de mayor densidad de biopelícula.
    \item \textbf{{Capa intermedia de grava media (5 -- 15\,mm, espesor 0.30\,m):}} Actúa como zona de transición hidráulica y soporte biológico secundario. Su mayor conductividad (90 -- 900\,m/d) facilita la percolación uniforme desde la capa superior hacia el drenaje. Alberga una biopelícula menos densa pero activa en la degradación de compuestos orgánicos recalcitrantes.
    \item \textbf{{Capa inferior de grava gruesa (20 -- 60\,mm, espesor 0.25\,m):}} Funciona como pleno de drenaje, recolectando el efluente percolado y distribuyéndolo hacia las tuberías de salida. Su alta conductividad hidráulica ($>$900\,m/d) garantiza el drenaje completo del sistema en pocas horas de reposo. Los tubos de ventilación vertical conectados a esta capa permiten la entrada de aire durante el período de reposo, completando el ciclo de re-aireación.
\end{{itemize}}

\subsubsection*{{Dimensionamiento por Criterio de Carga Orgánica Superficial (OLR)}}

La carga orgánica superficial (OLR, \textit{{Organic Loading Rate}}) es la masa de demanda química de oxígeno (DQO) aplicada por unidad de área del filtro activo y por día. Constituye el primer criterio de dimensionamiento del sistema francés tropical, ya que limita la capacidad de degradación de la biopelícula: si la OLR supera la capacidad de asimilación del biofilm, la materia orgánica no degradada se acumula en el lecho, agravando la colmatación. El valor máximo de {OLR_adoptada:.0f}\,g\,DQO/m²·d adoptado es conservador dentro del rango validado de 200 -- 350\,g\,DQO/m²·d (Molle et al., 2015) y garantiza un margen de seguridad ante variaciones de carga. El área de filtro en operación requerida por este criterio resulta:

\begin{{equation}}
A_\text{{op,OLR}} = \frac{{Q \cdot S_{{0,\text{{DQO}}}}}}{{\text{{OLR}}}} = \frac{{{r['Q_m3_d']:.1f} \times {r['DQO_entrada_mg_L']:.0f} \times 10^{{-3}}}}{{{OLR_adoptada:.0f} \times 10^{{-3}}}} = {r['A_op_OLR_m2']:.1f}\ \text{{m}}^2
\end{{equation}}
\captionequation{{Área del filtro activo por criterio de carga orgánica superficial (OLR) -- HAFV}}

\subsubsection*{{Dimensionamiento por Criterio de Carga Hidráulica Superficial (HLR)}}

La carga hidráulica superficial (HLR, \textit{{Hydraulic Loading Rate}}) expresa el caudal aplicado por unidad de área del filtro activo. Controla la velocidad de percolación del agua a través del medio filtrante y, por tanto, el tiempo de contacto entre el agua residual y la biopelícula: a mayor HLR, menor tiempo de residencia y menor eficiencia de remoción. El HLR también determina la frecuencia de saturación del medio y la intensidad de los pulsos, lo que afecta directamente la distribución hidráulica sobre la superficie del filtro. El valor adoptado de {HLR_adoptada:.2f}\,m/d corresponde al límite superior del rango para el sistema francés tropical, aplicable cuando el afluente proviene de un proceso de tratamiento primario (reactor anaerobio) que ha reducido previamente la carga orgánica. El área requerida por este criterio es:

\begin{{equation}}
A_\text{{op,HLR}} = \frac{{Q}}{{\text{{HLR}}}} = \frac{{{r['Q_m3_d']:.1f}}}{{{HLR_adoptada:.2f}}} = {r['A_op_HLR_m2']:.1f}\ \text{{m}}^2
\end{{equation}}
\captionequation{{Área del filtro activo por criterio de carga hidráulica superficial (HLR) -- HAFV}}

\subsubsection*{{Determinación del Área de Diseño}}

El dimensionamiento del sistema debe satisfacer ambos criterios de carga en forma simultánea. Si el área requerida por el criterio orgánico (OLR) supera la del criterio hidráulico (HLR), el sistema está \textit{{biológicamente limitado}}: la biopelícula no puede procesar la carga orgánica en el área disponible. Si por el contrario prevalece el criterio hidráulico, el sistema está \textit{{hidráulicamente limitado}}: el tiempo de contacto entre el agua y el biofilm es insuficiente independientemente de la capacidad metabólica del sistema. En ambos casos, el área de diseño corresponde al valor más restrictivo:

\begin{{equation}}
A_\text{{operando}} = \max\!\left(A_\text{{op,OLR}}\ ;\ A_\text{{op,HLR}}\right) = \max\!\left({r['A_op_OLR_m2']:.1f}\ ;\ {r['A_op_HLR_m2']:.1f}\right) = {r['A_operando_m2']:.1f}\ \text{{m}}^2
\end{{equation}}
\captionequation{{Área del filtro activo adoptada -- criterio dominante: \textbf{{{r['criterio_controla']}}}}}

En este proyecto el criterio determinante es el \textbf{{{r['criterio_controla']}}}. Cuando el HLR controla el diseño, como es frecuente en sistemas que reciben efluente de un proceso de tratamiento primario donde la carga orgánica ya fue parcialmente removida, la OLR real resultante es significativamente inferior al límite máximo, lo que representa un margen adicional de seguridad frente a variaciones de carga o eventos de pico.

Con {r['n_filtros']} celdas por línea operando en alternancia (una alimentando con el caudal completo mientras la otra descansa), el área total por línea es:

\begin{{equation}}
A_\text{{total}} = A_\text{{operando}} \times N_\text{{filtros}} = {r['A_operando_m2']:.1f} \times {r['n_filtros']} = {r['A_total_m2']:.1f}\ \text{{m}}^2
\end{{equation}}
\captionequation{{Área total construida del sistema HAFV}}

\subsubsection*{{Verificación por Habitante Equivalente (PE)}}

El criterio del habitante equivalente (PE) proporciona una verificación empírica e independiente del dimensionamiento, conectando el área calculada con la carga poblacional atendida. La unidad PE (Persona Equivalente) se define en el estándar europeo como la carga equivalente a 60\,g\,DBO$_5$/hab·d, valor representativo de la generación per cápita de materia orgánica biodegradable en aguas residuales domésticas.

Un aspecto crítico en sistemas donde el HAFV recibe efluente de un tratamiento primario previo (como el reactor anaerobio de flujo ascendente) es el criterio para calcular el PE equivalente. Utilizar el PE basado en el caudal per cápita (PE\textsubscript{{caudal}} = Q/0.15) sobreestimaría la carga orgánica real, ya que el tratamiento primario ha removido previamente del 65 al 70\,\% de la DBO$_5$ original. El procedimiento correcto consiste en calcular el PE en función de la carga real de DBO$_5$ que llega al HAFV:

\begin{{equation}}
\text{{PE}}_\text{{carga}} = \frac{{Q \times S_{{0,\text{{DBO5}}}}}}{{60 \times 10^{{-3}}}} = \frac{{{r['Q_m3_d']:.1f} \times {r['DBO_entrada_mg_L']:.0f} \times 10^{{-3}}}}{{60 \times 10^{{-3}}}} = {r['PE_carga']:.0f}\ \text{{hab. eq.}}
\end{{equation}}
\captionequation{{Habitante equivalente calculado a partir de la carga real de DBO$_5$ en el afluente al HAFV}}

El área de referencia correspondiente, con una dotación de {area_por_PE:.1f}\,m²/PE para temperatura del agua residual de {r['T_agua_C']:.1f}\,°C (rango tropical, $T > 22$\,°C según Molle et al., 2015), es:

\begin{{equation}}
A_\text{{PE}} = \frac{{A_\text{{total}}}}{{\text{{PE}}_\text{{carga}}}} \times \text{{PE}}_\text{{carga}} = {area_por_PE:.1f} \times {r['PE_carga']:.0f} = {r['A_PE_m2']:.1f}\ \text{{m}}^2
\end{{equation}}
\captionequation{{Área de referencia por criterio de habitante equivalente}}

{r['texto_criterio_PE']} El área definitiva adoptada para el dimensionamiento geométrico es $A_\text{{total}} = \mathbf{{{r['A_total_m2']:.1f}\ \text{{m}}^2}}$.

\subsubsection*{{Geometría de los Filtros}}

La configuración geométrica de los filtros adopta una relación largo:ancho de {r['relacion_L_A']:.1f}:1, que optimiza la distribución hidráulica al tiempo que mantiene proporciones constructivas racionales. Cada una de las {r['n_filtros']} celdas tiene el área completa de {r['A_total_m2']/r['n_filtros']:.1f}\,m² (capaz de tratar todo el caudal de {cfg.Q_linea_L_s:.1f} L/s cuando está activa) y dimensiones de \textbf{{{r['dimensiones_por_filtro_m'][0]:.1f}\,m $\times$ {r['dimensiones_por_filtro_m'][1]:.1f}\,m}}. El área total corresponde a la suma de ambas celdas, ya que operan en alternancia y cada una debe poder manejar el caudal completo de la línea. La altura total de construcción es de 1.50\,m, incluyendo 0.85\,m de medio filtrante, una capa de distribución superficial de 0.10\,m de grava gruesa y una altura libre de 0.55\,m para alojar la acumulación progresiva de lodo superficial durante la vida útil del sistema (estimada en 12 a 20 años bajo condiciones tropicales, según Molle et al., 2015).
"""

    def _generar_dimensionamiento_ruta_A(self, cfg, r) -> str:
        """Dimensionamiento para Sistema Clásico (Ruta A)."""
        area_por_PE_clasico = cfg.humedal_clasico_area_por_PE_m2
        return rf"""\subsection{{Dimensionamiento}}

\subsubsection*{{Principios de Funcionamiento del Humedal Artificial de Flujo Vertical}}

El Humedal Artificial de Flujo Vertical (HAFV) opera mediante percolación gravitacional del agua residual a través de un medio filtrante granular estratificado, donde se desarrolla biopelícula aerobia responsable de la degradación de materia orgánica y nitrificación. La alimentación intermitente genera ciclos de saturación y drenaje que re-airean pasivamente el lecho, favoreciendo la estabilización de sólidos retenidos.

Durante la fase de alimentación, el agua residual se distribuye sobre la superficie del filtro mediante un sistema de tuberías perforadas y percola hacia las capas inferiores, donde es recolectada por las tuberías de drenaje. Durante el período de reposo subsiguiente, el medio drena libremente y el aire penetra por convección natural desde los tubos de ventilación del fondo y desde la superficie expuesta, restaurando las condiciones aerobias en el interior del lecho. Este ciclo de saturación-drenaje-re-aireación, además de proveer el oxígeno necesario para las reacciones biológicas, permite la descomposición aerobia progresiva de los sólidos acumulados en la capa superficial del filtro, retardando la colmatación y extendiendo la vida útil del sistema sin necesidad de intervenciones frecuentes.

Los mecanismos de remoción y las eficiencias típicas del HAFV se presentan en la Tabla~\ref{{tab:mecanismos_hafv_a}}.

\begin{{table}}[H]
\centering
\caption{{Mecanismos de remoción y eficiencias típicas en el HAFV -- Sistema Clásico (Kadlec \& Wallace, 2009; Cooper et al., 1996)}}
\label{{tab:mecanismos_hafv_a}}
\begin{{tabular}}{{p{{2.2cm}}p{{6.5cm}}cc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Mecanismo principal}} & \textbf{{Eficiencia típica}} & \textbf{{Unidad}} \\
\midrule
DBO$_5$ / DQO & Degradación aerobia y anóxica en biopelícula & 70 -- 85 & \% \\
SST & Filtración física en el medio granular & 80 -- 90 & \% \\
NH$_4$-N & Nitrificación aerobia (\textit{{Nitrosomonas/Nitrobacter}}) & 40 -- 60 & \% \\
Colif. fecales & Filtración, adsorción, oxidación biológica & 1 -- 2 & log \\
Fósforo total & Adsorción en el medio (limitada) & 20 -- 40 & \% \\
\bottomrule
\end{{tabular}}
\end{{table}}

\subsubsection*{{Criterio de Selección del Sistema: Sistema Clásico en Clima Templado-Frío}}

La selección entre las dos metodologías de diseño disponibles para el HAFV se fundamenta en la temperatura del agua residual como criterio primario. A temperaturas inferiores a {cfg.humedal_temp_limite_clasico_C:.0f}\,°C, la cinética de mineralización aerobia del lodo superficial es insuficiente para sostener ciclos de reposo cortos sin riesgo de colmatación prematura. En consecuencia, el diseño debe ser conservador en cargas y generoso en períodos de reposo.

Para la temperatura de \textbf{{{r['T_agua_C']:.1f}\,°C}} del presente proyecto, inferior al umbral de {cfg.humedal_temp_limite_transicion_C:.0f}\,°C, corresponde aplicar el \textbf{{Sistema Clásico (Ruta A)}}, conforme a la metodología de Cooper et al. (1996) y la norma austriaca ÖNORM B 2505 (2009). A esta temperatura, la actividad microbiana es más lenta y la mineralización del lodo superficial requiere períodos de reposo más prolongados (7 días o más por filtro). La configuración de dos etapas en serie distribuye la carga de forma decreciente: la primera etapa, más cargada, remueve la fracción principal de la DBO$_5$ soluble y suspendida; la segunda etapa actúa como unidad de pulido, tratando el efluente de la primera con cargas menores y produciendo una calidad superior a la que podría alcanzar una etapa única.

\subsubsection*{{Configuración en Dos Etapas y Ciclo de Operación}}

La disposición en dos etapas en serie es característica del Sistema Clásico. La primera etapa opera con {r['n_filtros_1etapa']} filtros en paralelo bajo un ciclo de {r['ciclo_alim_1etapa_dias']:.1f} días de alimentación por {r['ciclo_reposo_1etapa_dias']:.1f} días de reposo, con lo cual en todo momento hay un solo filtro recibiendo caudal mientras los otros dos se recuperan. La segunda etapa opera con {r['n_filtros_2etapa']} filtros en paralelo bajo ciclos de 7 días de alimentación por 7 días de reposo. Esta diferencia en los ciclos refleja la mayor carga de la primera etapa y la necesidad de períodos de recuperación más extensos a menor temperatura.

El medio filtrante del Sistema Clásico difiere del sistema francés en su capa superficial: mientras el sistema francés emplea grava fina (2 -- 6\,mm), el clásico utiliza arena gruesa (0 -- 4\,mm) en la capa superior, seguida de grava media (4 -- 8\,mm) en la capa principal y grava gruesa (16 -- 32\,mm) en la capa de drenaje. La arena superficial proporciona mayor área específica de contacto con el agua y favorece la retención de sólidos, pero requiere ciclos de reposo largos para su mineralización a temperaturas bajas.

\subsubsection*{{Dimensionamiento por Carga Orgánica Superficial (COS)}}

La Carga Orgánica Superficial (COS) expresa la masa de DBO$_5$ aplicada por unidad de área del filtro activo por día. Es el criterio de dimensionamiento principal del Sistema Clásico, dado que a bajas temperaturas el control biológico del proceso es el factor limitante. El valor adoptado de {r['COS_gDBO_m2_d']:.0f}\,g\,DBO$_5$/m²·d corresponde al rango recomendado para la primera etapa en clima templado (Cooper et al., 1996), y garantiza que la biopelícula dispone de suficiente tiempo de contacto para degradar la carga recibida incluso bajo condiciones de menor actividad metabólica. El área de la primera etapa por este criterio es:

\begin{{equation}}
A_{{1a}} = \frac{{Q \times S_{{0,\text{{DBO5}}}} \times 10^{{-3}}}}{{\text{{COS}}_1}} = \frac{{{r['Q_m3_d']:.1f} \times {r['DBO_entrada_mg_L']:.0f} \times 10^{{-3}}}}{{{r['COS_gDBO_m2_d']:.0f} \times 10^{{-3}}}} = {r['A_1etapa_m2']:.1f}\ \text{{m}}^2
\end{{equation}}
\captionequation{{Área de la primera etapa por criterio de carga orgánica superficial (COS) -- HAFV Sistema Clásico}}

La segunda etapa recibe el efluente de la primera con carga ya parcialmente removida. Su área de diseño se establece en el 50\,\% del área de la primera etapa, lo que refleja la menor carga orgánica recibida y los menores requerimientos de tiempo de contacto para el pulido final:

\begin{{equation}}
A_{{2a}} = 0.50 \times A_{{1a}} = 0.50 \times {r['A_1etapa_m2']:.1f} = {r['A_2etapa_m2']:.1f}\ \text{{m}}^2
\end{{equation}}
\captionequation{{Área de la segunda etapa (50\,\% de la primera etapa) -- HAFV Sistema Clásico}}

El área total del sistema es la suma de ambas etapas:

\begin{{equation}}
A_\text{{total}} = A_{{1a}} + A_{{2a}} = {r['A_1etapa_m2']:.1f} + {r['A_2etapa_m2']:.1f} = {r['A_total_m2']:.1f}\ \text{{m}}^2
\end{{equation}}
\captionequation{{Área total del sistema HAFV Sistema Clásico (suma de etapas)}}

\subsubsection*{{Verificación por Habitante Equivalente (PE)}}

El criterio del habitante equivalente constituye una verificación empírica independiente del dimensionamiento. La unidad PE se define como 60\,g\,DBO$_5$/hab·d (estándar europeo), y permite relacionar la carga real del proyecto con referencias de diseño derivadas de la experiencia en instalaciones similares. En sistemas donde el HAFV recibe efluente de un proceso de tratamiento primario, el PE debe calcularse a partir de la carga real de DBO$_5$ al HAFV y no del caudal per cápita, para no sobredimensionar el sistema:

\begin{{equation}}
\text{{PE}}_\text{{carga}} = \frac{{Q \times S_{{0,\text{{DBO5}}}}}}{{60 \times 10^{{-3}}}} = \frac{{{r['Q_m3_d']:.1f} \times {r['DBO_entrada_mg_L']:.0f} \times 10^{{-3}}}}{{60 \times 10^{{-3}}}} = {r['PE_carga']:.0f}\ \text{{hab. eq.}}
\end{{equation}}
\captionequation{{Habitante equivalente calculado a partir de la carga real de DBO$_5$ en el afluente al HAFV}}

Con un área de referencia de {area_por_PE_clasico:.1f}\,m²/PE para la primera etapa en clima templado (Cooper et al., 1996), el área total del sistema por este criterio resulta:

\begin{{equation}}
A_\text{{PE}} = 1.50 \times a_1 \times \text{{PE}}_\text{{carga}} = 1.50 \times {area_por_PE_clasico:.1f} \times {r['PE_carga']:.0f} = {r['A_PE_m2']:.1f}\ \text{{m}}^2
\end{{equation}}
\captionequation{{Área de referencia por criterio de habitante equivalente -- Sistema Clásico}}

{r['texto_criterio_PE']} El área definitiva de diseño adoptada es $A_\text{{total}} = \mathbf{{{r['A_total_m2']:.1f}\ \text{{m}}^2}}$.

\subsubsection*{{Geometría de los Filtros}}

Las unidades de la primera etapa presentan dimensiones de \textbf{{{r['dimensiones_por_filtro_m'][0]:.1f}\,m $\times$ {r['dimensiones_por_filtro_m'][1]:.1f}\,m}} por filtro (relación largo:ancho de {r['relacion_L_A']:.1f}:1), con una profundidad de medio filtrante de 0.60 a 0.80\,m conforme a lo recomendado por Cooper et al. (1996) para la primera etapa del sistema clásico. La altura libre sobre el medio (0.50\,m) permite acomodar la acumulación de lodo superficial durante la vida útil estimada de 10 a 15 años.
"""

    def generar_verificacion(self) -> str:
        """Genera subsection Verificación - Modelo k-C* y cumplimiento."""
        cfg = self.cfg
        r = self.datos

        vkc = r['verificacion_kC']
        k_20 = vkc['k_20_m_d']
        k_T = vkc['k_T_m_d']
        theta = vkc['theta']
        q = vkc['q_m_d']
        C_star = vkc['C_star_mg_L']
        DBO_entrada = vkc['DBO_entrada_mg_L']
        DBO_salida_calc = vkc['DBO_salida_calc_mg_L']
        eficiencia = vkc['eficiencia_DBO_pct']

        DBO_objetivo = r['DBO_objetivo_mg_L']

        return rf"""\subsection{{Verificación}}

\subsubsection*{{Fundamento del Modelo Cinético k-C*}}

El dimensionamiento por carga orgánica e hidráulica superficial determina el área del sistema a partir de criterios empíricos derivados de la experiencia en instalaciones reales. Sin embargo, este enfoque no garantiza por sí solo que el sistema producirá la calidad de efluente requerida, ya que no incorpora explícitamente la cinética del proceso biológico ni las condiciones específicas de temperatura del proyecto. Por esta razón, toda propuesta de HAFV debe complementarse con una verificación de eficiencia mediante el modelo cinético de primer orden con concentración de fondo, conocido como modelo k-C* (Kadlec \& Wallace, 2009).

El modelo k-C* es el estándar de referencia internacional para la verificación de eficiencia en humedales construidos, adoptado por la guía EPA para humedales de tratamiento (US~EPA, 2000) y ampliamente validado en instalaciones de clima templado y tropical. Su formulación matematiza dos observaciones fundamentales de la práctica en humedales: en primer lugar, que la remoción de contaminantes sigue una cinética de primer orden en cuanto a la concentración activa del contaminante (fracción por encima de la concentración de fondo); y en segundo lugar, que existe una concentración mínima irreducible, denominada concentración de fondo o \textit{{background concentration}} ($C^*$), por debajo de la cual el sistema no puede reducir la concentración del efluente independientemente del área disponible. Esta concentración de fondo refleja la DBO$_5$ soluble de naturaleza recalcitrante, la demanda endógena generada por la propia biomasa del sistema y la resuspensión de material orgánico particulado.

La ecuación del modelo, en su forma para un reactor de flujo pistón (aproximación válida para HAFV de geometría rectangular), es:

\begin{{equation}}
C_e = C^* + (C_i - C^*) \cdot \exp\!\left(\frac{{-k_{{A,T}}}}{{q}}\right)
\label{{eq:kC_star}}
\end{{equation}}
\captionequation{{Modelo cinético k-C* para humedales de flujo vertical -- Kadlec \& Wallace (2009)}}

donde los términos de la ecuación tienen el siguiente significado físico:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$C_e$] = Concentración de DBO$_5$ en el efluente calculada por el modelo [mg/L]
    \item[$C_i$] = Concentración de DBO$_5$ en el afluente al HAFV ({DBO_entrada:.1f}\,mg/L en este proyecto)
    \item[$C^*$] = Concentración de fondo (\textit{{background concentration}}): mínimo inalcanzable del sistema, fijado en {C_star:.1f}\,mg\,DBO$_5$/L según Kadlec \& Wallace (2009) para HAFV con afluente municipal
    \item[$k_{{A,T}}$] = Constante cinética de remoción de primer orden a la temperatura $T$ del proyecto [m/d], que cuantifica la capacidad de remoción de la biopelícula por unidad de área y de carga hidráulica
    \item[$q$] = Carga hidráulica superficial del filtro activo [m/d], igual a $Q / A_\text{{operando}}$
\end{{itemize}}

El cociente $k_{{A,T}}/q$ es el argumento del exponencial y representa el número de unidades cinéticas de remoción disponibles: a mayor área (menor $q$) o mayor temperatura (mayor $k_{{A,T}}$), la remoción es más intensa. Cuando $k_{{A,T}}/q \gg 1$, la concentración de salida tiende asintóticamente hacia $C^*$; cuando $k_{{A,T}}/q \ll 1$, la remoción es mínima.

\subsubsection*{{Corrección de la Constante Cinética por Temperatura}}

La constante cinética $k_A$ depende fuertemente de la temperatura del agua residual, dado que la velocidad de las reacciones enzimáticas en la biopelícula es una función exponencial de la temperatura. Kadlec \& Wallace (2009) proponen la corrección mediante el modelo de Arrhenius modificado:

\begin{{equation}}
k_{{A,T}} = k_{{A,20}} \cdot \theta^{{(T-20)}}
\label{{eq:arrhenius}}
\end{{equation}}
\captionequation{{Corrección de la constante cinética por temperatura -- Ecuación de Arrhenius modificada (Kadlec \& Wallace, 2009)}}

En esta expresión, $k_{{A,20}}$ es la constante cinética de referencia a 20\,°C, determinada estadísticamente a partir de datos de seguimiento de numerosas instalaciones reales. Para la remoción de DBO$_5$ en humedales de flujo vertical tratando aguas residuales municipales, Kadlec \& Wallace (2009) establecen $k_{{A,20}} = {k_20:.3f}$\,m/d. El coeficiente de temperatura $\theta = {theta:.2f}$ cuantifica la sensibilidad de la reacción a los cambios térmicos: por cada grado centígrado de aumento en la temperatura del agua, la constante cinética aumenta aproximadamente un {(theta-1)*100:.0f}\,\%.

La Tabla~\ref{{tab:kAT_temperatura}} ilustra la variación de la constante cinética con la temperatura para el parámetro DBO$_5$, permitiendo apreciar el efecto cuantitativo de la temperatura en el rendimiento del sistema.

\begin{{table}}[H]
\centering
\caption{{Valores de $k_{{A,T}}$ para DBO$_5$ en función de la temperatura ($k_{{A,20}} = {k_20:.3f}$\,m/d; $\theta = {theta:.2f}$)}}
\label{{tab:kAT_temperatura}}
\begin{{tabular}}{{ccc}}
\toprule
\textbf{{Temperatura (°C)}} & \textbf{{Factor $\theta^{{(T-20)}}$}} & \textbf{{$k_{{A,T}}$ (m/d)}} \\
\midrule
10 & 0.558 & 0.052 \\
15 & 0.747 & 0.069 \\
18 & 0.890 & 0.083 \\
20 & 1.000 & {k_20:.3f} \\
22 & 1.124 & 0.105 \\
25 & 1.338 & 0.124 \\
{cfg.T_agua_C:.1f} & {theta:.2f}$^{{({cfg.T_agua_C:.1f}-20)}}$ & \textbf{{{k_T:.4f}}} \\
28 & 1.594 & 0.148 \\
30 & 1.791 & 0.167 \\
\bottomrule
\end{{tabular}}
\end{{table}}

Para la temperatura de diseño del proyecto ($T = {cfg.T_agua_C:.1f}$\,°C), la constante cinética corregida resulta:

\begin{{equation}}
k_{{A,T}} = {k_20:.3f} \times {theta:.2f}^{{({cfg.T_agua_C:.1f} - 20)}} = {k_20:.3f} \times {theta:.2f}^{{{cfg.T_agua_C:.1f} - 20:.1f}} = {k_T:.4f}\ \text{{m/d}}
\end{{equation}}
\captionequation{{Constante cinética de remoción de DBO$_5$ corregida a $T = {cfg.T_agua_C:.1f}$\,°C}}

\subsubsection*{{Aplicación del Modelo y Estimación del Efluente}}

La carga hidráulica superficial sobre el filtro activo, considerando únicamente el área en operación simultánea ($A_\text{{operando}}$), es:

\begin{{equation}}
q = \frac{{Q}}{{A_\text{{operando}}}} = \frac{{{vkc['Q_m3_d']:.1f}}}{{{vkc['A_operando_m2']:.1f}}} = {q:.4f}\ \text{{m/d}}
\end{{equation}}
\captionequation{{Carga hidráulica superficial del filtro activo ($q$) -- parámetro de entrada del modelo k-C*}}

Sustituyendo en la ecuación del modelo~\eqref{{eq:kC_star}} con los valores del proyecto:

\begin{{equation}}
C_e = {C_star:.1f} + ({DBO_entrada:.1f} - {C_star:.1f}) \cdot \exp\!\left(\frac{{-{k_T:.4f}}}{{{q:.4f}}}\right) = {C_star:.1f} + {DBO_entrada - C_star:.1f} \cdot \exp(-{k_T/q:.4f}) = {DBO_salida_calc:.1f}\ \text{{mg/L}}
\end{{equation}}
\captionequation{{Concentración estimada de DBO$_5$ en el efluente del HAFV -- Modelo k-C*}}

La eficiencia de remoción de DBO$_5$ en el HAFV resulta:

\begin{{equation}}
\eta = \frac{{C_i - C_e}}{{C_i}} \times 100 = \frac{{{DBO_entrada:.1f} - {DBO_salida_calc:.1f}}}{{{DBO_entrada:.1f}}} \times 100 = {eficiencia:.1f}\ \%
\end{{equation}}
\captionequation{{Eficiencia de remoción de DBO$_5$ en el HAFV}}

La Tabla~\ref{{tab:verificacion_kC}} consolida los parámetros y resultados de la verificación cinética.

\begin{{table}}[H]
\centering
\caption{{Resultados de la verificación cinética k-C* -- Humedal Artificial de Flujo Vertical}}
\label{{tab:verificacion_kC}}
\begin{{tabular}}{{lccc}}
\toprule
\textbf{{Parámetro}} & \textbf{{Símbolo}} & \textbf{{Valor}} & \textbf{{Unidad}} \\
\midrule
Constante cinética de referencia a 20\,°C & $k_{{A,20}}$ & {k_20:.3f} & m/d \\
Coeficiente de temperatura & $\theta$ & {theta:.2f} & -- \\
Temperatura del agua residual & $T$ & {cfg.T_agua_C:.1f} & °C \\
Constante cinética corregida por temperatura & $k_{{A,T}}$ & {k_T:.4f} & m/d \\
Concentración de fondo & $C^*$ & {C_star:.1f} & mg\,DBO$_5$/L \\
Carga hidráulica del filtro activo & $q$ & {q:.4f} & m/d \\
Relación $k_{{A,T}} / q$ & -- & {k_T/q:.4f} & -- \\
DBO$_5$ del afluente & $C_i$ & {DBO_entrada:.1f} & mg/L \\
DBO$_5$ del efluente estimada (modelo k-C*) & $C_e$ & {DBO_salida_calc:.1f} & mg/L \\
Eficiencia de remoción de DBO$_5$ en HAFV & $\eta$ & {eficiencia:.1f} & \% \\
\bottomrule
\end{{tabular}}
\end{{table}}


\subsubsection*{{Retención de Sólidos, Producción de Lodo y Mantenimiento}}

El HAFV retiene los sólidos suspendidos del afluente mediante filtración física en la capa superficial del medio granular. Este material, denominado lodo superficial, se acumula progresivamente sobre la grava de la capa superior durante los ciclos de alimentación. La clave del sistema para evitar la colmatación radica en la mineralización aerobia de este lodo durante los períodos de reposo: a temperatura del agua residual de {cfg.T_agua_C:.1f}\,°C, la actividad microbiana degrada la fracción orgánica del lodo acumulado, reduciendo su volumen y manteniendo la permeabilidad del medio.

La producción neta de sólidos retenidos puede estimarse como:

\begin{{equation}}
P_\text{{sólidos}} = Q \times (S_{{0,\text{{SST}}}} - C_{{e,\text{{SST}}}}) \times 10^{{-3}}\ \text{{[kg\,SST/d]}}
\end{{equation}}
\captionequation{{Producción de sólidos retenidos en el medio filtrante del HAFV}}

En condiciones tropicales ($T > 20$\,°C), la acumulación neta de lodo superficial, una vez descontada la mineralización durante el reposo, es del orden de 0.5 a 1.0\,cm/año (Molle et al., 2015). Con una altura libre sobre el medio de 0.55\,m, el sistema puede operar sin retiro de lodo por períodos superiores a 10 años antes de requerir una evaluación de colmatación. El lodo eventualmente extraído durante el mantenimiento mayor tiene carácter de biosólido estabilizado aerobiamente y puede recibir disposición controlada sin requerir tratamiento adicional.

El programa de mantenimiento preventivo incluye inspección diaria de los sistemas de distribución y control de la alternancia de filtros, revisión semanal del drenaje completo durante el período de reposo, muestreo mensual del efluente para DBO$_5$, SST y coliformes fecales, cosecha semestral parcial de la vegetación macrófita (no más del 50\,\% de la biomasa aérea para no estresar las plantas), e inspección anual del espesor de lodo acumulado sobre el medio filtrante.
"""

    def generar_resultados(self) -> str:
        """Genera subsection Resultados - Tabla resumen y figura."""
        cfg = self.cfg
        r = self.datos

        ruta_fig = self._generar_esquema_png()
        ruta_fig_latex = ruta_fig.replace('\\', '/')

        sistema = r['sistema']
        ruta = r['ruta']
        criterio = r['criterio_resultados']
        A_total = r['A_total_m2']
        A_total_sistema = r['A_total_sistema_m2']
        A_operando = r['A_operando_resultados_m2']
        n_filtros = r['n_filtros_resultados']
        dims = r['dimensiones_por_filtro_m']
        ciclo_alim = r['ciclo_alim_resultados_dias']
        ciclo_reposo = r['ciclo_reposo_resultados_dias']
        DBO_salida = r['DBO_salida_mg_L']
        OLR = r['carga_organica_resultados_valor']
        HLR = r['HLR_resultados_m_d']
        PE = r['PE_carga']
        estado_kc = r['estado_verificacion_kC'].capitalize()

        return rf"""\subsection{{Resultados}}

La Tabla~\ref{{tab:resumen_hafv}} concentra los parámetros geométricos, hidráulicos, de carga y de calidad del efluente del sistema dimensionado, permitiendo una lectura integrada de los resultados del diseño y facilitando su verificación cruzada con los criterios de diseño aplicados.

\begingroup
\small
\setlength{{\tabcolsep}}{{4pt}}
\renewcommand{{\arraystretch}}{{1.12}}
\begin{{longtable}}{{p{{4.1cm}}p{{4.8cm}}p{{4.2cm}}}}
\caption{{Resumen de resultados del dimensionamiento -- Humedal Artificial de Flujo Vertical (HAFV)}}\label{{tab:resumen_hafv}}\\
\toprule
\textbf{{Parámetro}} & \textbf{{Descripción}} & \textbf{{Valor}} \\
\midrule
\endfirsthead
\caption[]{{Resumen de resultados del dimensionamiento -- Humedal Artificial de Flujo Vertical (HAFV) (continuación)}}\\
\toprule
\textbf{{Parámetro}} & \textbf{{Descripción}} & \textbf{{Valor}} \\
\midrule
\endhead
\midrule
\multicolumn{{3}}{{r}}{{\textit{{Continúa en la siguiente página}}}}\\
\endfoot
\bottomrule
\endlastfoot
\multicolumn{{3}}{{l}}{{\textit{{Metodología y configuración}}}} \\
\quad Sistema adoptado & Metodología & {sistema} (Ruta {ruta}) \\
\quad Criterio controlante & Factor limitante & {criterio} \\
\quad N° celdas (alternancia) & Unidades en operación alterna & {n_filtros} \\
\quad Ciclo alimentación / reposo & Rotación por unidad & {ciclo_alim:.1f}\,/\,{ciclo_reposo:.1f}\,días \\
\midrule
\multicolumn{{3}}{{l}}{{\textit{{Geometría del sistema}}}} \\
\quad Área total por línea & Superficie celdas por línea & {A_total:.1f}\,m² \\
\quad Área total sistema & Superficie celdas ({r['num_lineas']} líneas) & {A_total_sistema:.1f}\,m² \\
\quad Área celda activa & Superficie celda en operación & {A_operando:.1f}\,m² \\
\quad Dimensiones por celda & Largo $\times$ Ancho & {dims[0]:.1f}$\times${dims[1]:.1f}\,m \\
\quad Profundidad del medio & Espesor lecho filtrante & {r['h_lecho_m']:.2f}\,m \\
\quad Altura total & Incluye borde libre & {r['H_total_m']:.2f}\,m \\
\midrule
\multicolumn{{3}}{{l}}{{\textit{{Parámetros de carga}}}} \\
\quad OLR real (celda activa) & Carga orgánica superficial & {OLR:.1f}\,g DQO/m²·d \\
\quad HLR real (celda activa) & Carga hidráulica superficial & {HLR:.3f}\,m/d \\
\quad PE equivalente & Habitantes equivalentes & {PE:.0f}\,PE \\
\midrule
\multicolumn{{3}}{{l}}{{\textit{{Calidad del efluente estimada}}}} \\
\quad DBO$_5$ calculada (k-C*) & Concentración estimada & {DBO_salida:.1f}\,mg/L \\
\end{{longtable}}
\endgroup

El área total por línea de {A_total:.1f}\,m² resulta del criterio de diseño dominante (\textbf{{{criterio}}}), lo que implica que el factor limitante del sistema es de naturaleza {'hidráulica: el tiempo de contacto entre el agua residual y la biopelícula es el parámetro que acota el rendimiento, y la carga orgánica real sobre el filtro activo permanece holgadamente por debajo del límite máximo admisible. Esta situación es típica en sistemas HAFV que reciben efluente de un proceso de tratamiento primario, donde el tratamiento anaerobio previo ha reducido ya la carga orgánica en un 60 a 70\\,\\%' if criterio == 'HLR' else 'orgánica: la capacidad de degradación de la biopelícula es el factor que determina el área, y la carga hidráulica resultante se sitúa dentro del rango admisible para el sistema seleccionado'}. En conjunto, los parámetros de carga reales verifican el cumplimiento de los rangos validados para el sistema {sistema} (Molle et al., 2015).

La concentración de DBO$_5$ estimada en el efluente mediante el modelo k-C* es {DBO_salida:.1f}\,mg/L. Es importante señalar que la eficiencia de remoción de DBO$_5$ en el propio HAFV puede parecer moderada en sistemas con tratamiento primario previo, dado que el reactor anaerobio ya ha removido la fracción principal de la carga orgánica; la eficiencia total del tren de tratamiento es sustancialmente mayor.

Con respecto a la remoción de sólidos suspendidos, el HAFV presenta eficiencias típicas del 80 al 95\,\% por filtración física en el medio granular. Los coliformes fecales se reducen entre 1 y 3 unidades logarítmicas; si es necesario reducir más la concentración de coliformes fecales, se deberá incorporar una etapa de desinfección posterior (radiación ultravioleta o hipoclorito de sodio).

La Figura~\ref{{fig:humedal_vertical}} presenta el esquema del sistema con la vista en planta del arreglo de filtros en operación alternada y la sección transversal simplificada que ilustra la composición estratificada del medio filtrante y la ubicación del sistema de drenaje inferior.

\begin{{figure}}[H]
\centering
\includegraphics[width=0.85\textwidth]{{{ruta_fig_latex}}}
\caption{{Esquema del Humedal Artificial de Flujo Vertical -- {sistema}. \textit{{Arriba:}} vista en planta con los {n_filtros} filtros en operación alternada (alimentando / reposo). \textit{{Abajo:}} sección transversal simplificada con las capas del medio filtrante (grava fina superior, grava media intermedia y grava gruesa de drenaje) y el sistema de tuberías de drenaje inferior con tubos de ventilación.}}
\label{{fig:humedal_vertical}}
\end{{figure}}

\subsubsection*{{Ciclo de Operación y Esquema de Rotación}}

El esquema de operación alternada asegura que, mientras {n_filtros - 1} unidad(es) permanece(n) en período de reposo durante {ciclo_reposo:.1f} días, el filtro activo recibe la totalidad del caudal de diseño durante {ciclo_alim:.1f} días. Al término del ciclo de alimentación, los roles se invierten automáticamente mediante temporizador o sistema básico de control. Esta rotación distribuye el desgaste biológico entre las unidades, permite la recuperación aerobia completa del medio filtrante en cada ciclo y minimiza el riesgo de colmatación progresiva.

Durante el período de reposo, el drenaje completo del lecho es condición necesaria e indispensable: solo con el medio drenado pueden penetrar el oxígeno y el aire desde la superficie libre y los tubos de ventilación del fondo, habilitando la mineralización aerobia del lodo superficial. Cualquier obstrucción de los tubos de drenaje que impida el vaciado completo del sistema compromete directamente la eficiencia del proceso de regeneración y, a mediano plazo, conduce a la colmatación del filtro.

\subsubsection*{{Vegetación Macrófita: Establecimiento y Manejo}}

La vegetación macrófita (\textit{{Phragmites australis}} o especies tropicales equivalentes nativas) se establece sobre el lecho filtrante antes de la puesta en marcha del sistema, a una densidad de 4 a 6 plantas por metro cuadrado. Su sistema radicular, a medida que se desarrolla durante los primeros meses de operación, cumple funciones complementarias que contribuyen a la estabilidad del sistema. Entre estas funciones se encuentra el mantenimiento de la permeabilidad superficial del medio filtrante al impedir la compactación de las capas superiores, la creación de micrositios aerobios localizados en la rizosfera que amplían la diversidad de condiciones redox disponibles para las comunidades microbianas, la transferencia de pequeñas cantidades de oxígeno hacia las zonas profundas del lecho a través de los aerénquimas radiculares, y la contribución a la integración paisajística del sistema en el entorno natural del proyecto.

Durante los primeros 6 a 12 meses de operación, correspondientes al período de establecimiento de la biopelícula y de la vegetación, se recomienda operar el sistema con una carga reducida al 30 a 50\,\% de la carga de diseño, incrementándola gradualmente hasta alcanzar las condiciones nominales. Este período de arranque permite el desarrollo de la biopelícula, el acondicionamiento del medio filtrante y la estabilización de la vegetación antes de enfrentar la carga plena.
"""

    def generar_esquema_linea_humedal_2celdas(self, output_dir=None):
        """
        Esquema técnico estilo UASB para UNA LÍNEA de humedal vertical.
        Cada celda procesa TODO el caudal de la línea cuando le toca alimentar.
        Usa los valores reales de diseño desde self.datos y self.cfg.
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon, FancyArrowPatch
        import numpy as np
        import os
        
        # Usar valores reales de diseño
        cfg = self.cfg
        r = self.datos
        
        Q_Ls = cfg.Q_linea_L_s                          # caudal real por línea
        area_celda_m2 = r.get('A_operando_m2', 720.0)   # Área operando real
        # Calcular dimensiones aproximadas desde el área
        import math
        ancho_celda_m = math.sqrt(area_celda_m2 / 1.2)  # Relación largo:ancho ≈ 1.2:1
        largo_celda_m = area_celda_m2 / ancho_celda_m
        # Valores estándar Molle et al. 2015 para sistema francés tropical
        H_drenaje = 0.15   # Capa drenaje 20-60 mm
        H_media = 0.25     # Capa media 5-15 mm
        H_fina = 0.60      # Capa filtrante 2-6 mm (aumentada)
        H_borde_libre = 0.50  # Borde libre aumentado
        H_total_lecho_m = H_drenaje + H_media + H_fina  # = 1.00 m

        # ====================== FIGURA ======================
        fig, ax = plt.subplots(figsize=(14, 14))
        ax.set_xlim(0, 70)
        ax.set_ylim(0, 60)
        ax.axis('off')
        fig.suptitle(f'LÍNEA DE TRATAMIENTO TERCIARIO - {Q_Ls:.1f} L/s\n'
                     'Humedal Vertical con 2 celdas en operación alternada',
                     fontsize=16, fontweight='bold', y=0.96)

        # ====================== VISTA EN PLANTA (arriba) ======================
        y_planta = 42
        # Marco de la línea completa
        ax.add_patch(FancyBboxPatch((5, y_planta), 60, 12, boxstyle="round,pad=0.3",
                                   facecolor='#E6F3FF', edgecolor='black', linewidth=3))

        ax.text(35, y_planta + 13, f'VISTA EN PLANTA - 2 CELDAS DE LA LÍNEA ({Q_Ls:.1f} L/s)',
                ha='center', fontsize=13, fontweight='bold')

        # Celda 1 (izquierda - alimentando)
        x1 = 10
        ax.add_patch(Rectangle((x1, y_planta+1), 24, 10, facecolor='#90EE90', edgecolor='black', linewidth=2.5))
        # Grilla plantas
        for dx in range(0, 25, 3):
            ax.plot([x1+dx, x1+dx], [y_planta+1, y_planta+11], color='#228B22', lw=0.8)
        for dy in range(1, 11, 3):
            ax.plot([x1, x1+24], [y_planta+dy, y_planta+dy], color='#228B22', lw=0.8)
        ax.text(x1+12, y_planta+14.5, 'CELDA 1\nALIMENTANDO\n3.5 días', ha='center',
                fontsize=11, color='blue', fontweight='bold')
        ax.scatter(x1+12, y_planta+6, s=300, color='blue', zorder=5)

        # Celda 2 (derecha - reposo)
        x2 = 39
        ax.add_patch(Rectangle((x2, y_planta+1), 24, 10, facecolor='#90EE90', edgecolor='black', linewidth=2.5))
        for dx in range(0, 25, 3):
            ax.plot([x2+dx, x2+dx], [y_planta+1, y_planta+11], color='#228B22', lw=0.8)
        for dy in range(1, 11, 3):
            ax.plot([x2, x2+24], [y_planta+dy, y_planta+dy], color='#228B22', lw=0.8)
        ax.text(x2+12, y_planta+14.5, 'CELDA 2\nREPOSO\n3.5 días', ha='center',
                fontsize=11, color='orange', fontweight='bold')
        ax.scatter(x2+12, y_planta+6, s=300, color='orange', zorder=5)

        # Flechas de entrada y salida
        ax.arrow(6, y_planta+6, 3, 0, head_width=1, head_length=1.5, fc='blue', ec='blue', lw=4)
        ax.text(2, y_planta+7, f'Entrada {Q_Ls:.1f} L/s', fontsize=11, color='blue', fontweight='bold')
        ax.arrow(65, y_planta+6, 3, 0, head_width=1, head_length=1.5, fc='green', ec='green', lw=4)
        ax.text(67, y_planta+7, 'Salida tratada', fontsize=11, color='green', fontweight='bold')

        # ====================== SECCIÓN TRANSVERSAL (abajo) ======================
        y_sec = 2
        ax.text(35, y_sec + 32, 'SECCIÓN TRANSVERSAL TÍPICA DE UNA CELDA',
                ha='center', fontsize=14, fontweight='bold')

        # Cuerpo del lecho (rectángulo redondeado) - altura total aumentada
        # Escala visual: 1 m de altura real = 12 unidades de dibujo aprox
        h_visual_total = 28  # altura visual total del cuerpo
        ax.add_patch(FancyBboxPatch((15, y_sec), 40, h_visual_total, boxstyle="round,pad=0.4",
                                   facecolor='white', edgecolor='#333333', linewidth=3))

        # Factores de escala visual (proporcional a las alturas reales)
        escala = 16  # unidades visuales por metro

        # 1. Drenaje (fondo) - 0.15 m
        h_drenaje_v = H_drenaje * escala  # ~2.4 unidades
        y_drenaje = y_sec + 2
        ax.add_patch(Rectangle((17, y_drenaje), 36, h_drenaje_v, facecolor='#A9A9A9', edgecolor='black', hatch='///'))
        ax.text(57, y_drenaje + h_drenaje_v/2, f'Capa drenaje\nGrava 20-60 mm\n({H_drenaje:.2f} m)', fontsize=10)

        # Tubo colector
        ax.add_patch(Rectangle((19, y_drenaje + 1), 30, 1.2, facecolor='#333333'))
        for xt in np.arange(20, 48, 4):
            ax.plot([xt, xt], [y_drenaje + 1, y_drenaje + 2.2], color='#00BFFF', lw=8)
        ax.text(57, y_drenaje + 0.5, 'Tubo colector drenaje Ø150 mm', fontsize=10)

        # 2. Grava media - 0.25 m
        h_media_v = H_media * escala  # ~4 unidades
        y_media = y_drenaje + h_drenaje_v
        ax.add_patch(Rectangle((17, y_media), 36, h_media_v, facecolor='#C0C0C0', edgecolor='black', hatch='...'))
        ax.text(57, y_media + h_media_v/2, f'Capa media\nGrava 5-15 mm\n({H_media:.2f} m)', fontsize=10)

        # 3. Grava fina - 0.60 m (capa principal)
        h_fina_v = H_fina * escala  # ~9.6 unidades
        y_fina = y_media + h_media_v
        ax.add_patch(Rectangle((17, y_fina), 36, h_fina_v, facecolor='#E5D5B8', edgecolor='black', hatch='|||'))
        ax.text(57, y_fina + h_fina_v/2, f'Capa filtrante\nGrava fina 2-6 mm\n({H_fina:.2f} m)', fontsize=10)

        # Flechas de percolación vertical (flujo descendente)
        for fx in [22, 32, 42]:
            ax.arrow(fx, y_fina + h_fina_v - 2, 0, -8, head_width=1, head_length=2, fc='blue', ec='blue', lw=2.5)

        # 4. Borde libre + distribución - 0.50 m
        h_borde_v = H_borde_libre * escala  # ~8 unidades
        y_borde = y_fina + h_fina_v
        ax.add_patch(Rectangle((17, y_borde), 36, h_borde_v, facecolor='#E0F0FF', edgecolor='black', alpha=0.7))
        ax.text(57, y_borde + h_borde_v/2, f'Borde libre\n({H_borde_libre:.2f} m)', fontsize=10)

        # Tubería de distribución superior (dentro del borde libre)
        y_tuberia = y_borde + h_borde_v - 1  # cerca de la parte superior del borde libre
        ax.plot([17, 53], [y_tuberia, y_tuberia], color='black', lw=6)
        for p in [20, 27, 34, 41, 48]:
            ax.plot([p, p], [y_tuberia - 1, y_tuberia + 1], color='#1E90FF', lw=5)

        # Plantas emergentes (tallos con hojas) - desde superficie del lecho (nivel y_borde)
        ax.text(35, y_borde + 3, 'Plantas emergentes (Phragmites australis)', ha='center',
                fontsize=11, color='darkgreen', fontweight='bold')
        # Dibujar tallos verticales con hojas desde superficie del lecho (nivel y_borde, línea café)
        for px in [22, 26, 30, 34, 38, 42, 46, 50]:
            # Tallo principal (desde superficie del lecho y_borde hacia arriba)
            ax.plot([px, px], [y_borde, y_borde + 2.5], color='darkgreen', lw=2.5)
            # Hojas laterales
            ax.plot([px, px-1.2], [y_borde + 0.8, y_borde + 2], color='forestgreen', lw=2)
            ax.plot([px, px+1.2], [y_borde + 0.8, y_borde + 2], color='forestgreen', lw=2)
            ax.plot([px, px-1.0], [y_borde + 1.5, y_borde + 2.5], color='forestgreen', lw=2)
            ax.plot([px, px+1.0], [y_borde + 1.5, y_borde + 2.5], color='forestgreen', lw=2)

        # ====================== DIMENSIONES LATERALES ======================
        x_dim = 8
        # Línea vertical total (ajustada a nueva altura) - desde base hasta borde superior
        y_top_total = y_borde + h_borde_v
        ax.plot([x_dim, x_dim], [y_drenaje, y_top_total], 'k-', lw=1.2)
        # Ticks en las interfaces de capas (sin tick en la base)
        y_ticks = [y_drenaje, y_media, y_fina, y_borde, y_top_total]
        for y_tick in y_ticks:
            ax.plot([x_dim-0.3, x_dim+0.3], [y_tick, y_tick], 'k-', lw=1.2)
        # Etiquetas de altura - posicionadas correctamente en cada capa
        # 0.15 m - capa drenaje (abajo)
        ax.text(x_dim-1.5, y_drenaje + h_drenaje_v/2, f'{H_drenaje:.2f} m', ha='right', fontsize=9)
        # 0.25 m - capa media
        ax.text(x_dim-1.5, y_media + h_media_v/2, f'{H_media:.2f} m', ha='right', fontsize=9)
        # 0.60 m - capa filtrante (la más grande)
        ax.text(x_dim-1.5, y_fina + h_fina_v/2, f'{H_fina:.2f} m', ha='right', fontsize=9)
        # 0.50 m - borde libre (arriba)
        ax.text(x_dim-1.5, y_borde + h_borde_v/2, f'{H_borde_libre:.2f} m', ha='right', fontsize=9)
        # H total de construcción (desde base hasta borde superior)
        H_total_construccion = H_total_lecho_m + H_borde_libre
        ax.text(x_dim-5, (y_sec + y_top_total)/2, f'H = {H_total_construccion:.2f} m', ha='right', fontsize=10, fontweight='bold')

        # ====================== GUARDAR ======================
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados', 'figuras')
        os.makedirs(output_dir, exist_ok=True)

        fig_path = os.path.join(output_dir, f'Esquema_Linea_Humedal_{Q_Ls:.1f}Ls_2celdas.png')
        fig.savefig(fig_path, dpi=250, bbox_inches='tight', facecolor='white')
        plt.close()

        return fig_path

    def generar_esquema_humedal_matplotlib(self, caudal_Ls=5.0, n_modulos=3, output_dir=None):
        """
        Esquema técnico profesional para caudal real (Sistema Clásico).
        3 filtros de 20 m × 12 m cada uno.
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import os

        Q_m3d = caudal_Ls * 86400 / 1000  # m³/día
        area_por_filtro_m2 = 240.0        # calculado con HLR=0.6 m/d

        fig, axs = plt.subplots(2, 1, figsize=(14, 11), gridspec_kw={'height_ratios': [1, 1.3]})
        fig.suptitle(f'HUMEDAL ARTIFICIAL DE FLUJO VERTICAL (HAFV) - SISTEMA CLÁSICO\n{caudal_Ls:.1f} L/s ({Q_m3d:.0f} m³/día)',
                     fontsize=16, fontweight='bold', y=0.98)

        # ====================== VISTA EN PLANTA ======================
        ax1 = axs[0]
        ax1.set_title('VISTA EN PLANTA - 3 FILTROS EN OPERACIÓN ALTERNADA\n'
                      f'(Cada filtro: 20 m × 12 m  |  Área operando por filtro: {area_por_filtro_m2:.0f} m²)',
                      fontsize=13, pad=15)
        ax1.set_xlim(0, n_modulos * 28 + 10)
        ax1.set_ylim(0, 18)
        ax1.axis('off')

        for i in range(n_modulos):
            x = i * 28 + 3
            # Filtro (escala 1 unidad = 1 metro)
            rect = patches.Rectangle((x, 3), 20, 12, linewidth=3, edgecolor='black', facecolor='#90EE90')
            ax1.add_patch(rect)

            # Grilla de plantas
            for dx in range(0, 21, 2):
                ax1.plot([x+dx, x+dx], [3, 15], color='#228B22', linewidth=0.8, alpha=0.5)
            for dy in range(3, 16, 2):
                ax1.plot([x, x+20], [dy, dy], color='#228B22', linewidth=0.8, alpha=0.5)

            # Tubería de distribución
            ax1.plot([x+2, x+18], [13, 13], color='black', linewidth=5)
            for p in range(3, 19, 3):
                ax1.plot([x+p, x+p], [12, 14], color='#1E90FF', linewidth=4)

            ax1.text(x + 10, 16.5, f'FILTRO {i+1}', ha='center', fontsize=12, fontweight='bold')

            if i == 0:
                ax1.text(x + 10, 8, 'ALIMENTANDO\n3.5 días', ha='center', fontsize=11,
                         color='blue', fontweight='bold', bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.5'))
                ax1.scatter(x + 10, 13, s=300, color='blue', zorder=5)
            else:
                ax1.text(x + 10, 8, 'REPOSO\n3.5 días', ha='center', fontsize=11,
                         color='orange', fontweight='bold', bbox=dict(facecolor='white', edgecolor='orange', boxstyle='round,pad=0.5'))
                ax1.scatter(x + 10, 13, s=300, color='orange', zorder=5)

        # Flechas
        ax1.arrow(0, 9, 2.5, 0, head_width=0.8, head_length=1, fc='blue', ec='blue', linewidth=4)
        ax1.text(1, 11, f'Entrada\nagua residual ({caudal_Ls:.1f} L/s)', fontsize=11, color='blue')

        ax1.arrow(x + 20 + 2, 9, 2.5, 0, head_width=0.8, head_length=1, fc='green', ec='green', linewidth=4)
        ax1.text(x + 23, 11, 'Salida\nagua tratada', fontsize=11, color='green')

        ax1.text( (n_modulos*28)/2 , 1,
                  'Ciclo de operación: 3.5 días ALIMENTANDO / 3.5 días REPOSO por filtro',
                  ha='center', fontsize=12, fontweight='bold')

        # ====================== SECCIÓN TRANSVERSAL ======================
        ax2 = axs[1]
        ax2.set_title('SECCIÓN TRANSVERSAL TÍPICA DE UN FILTRO (escala real)', fontsize=14, pad=15)
        ax2.set_xlim(0, 25)
        ax2.set_ylim(0, 110)
        ax2.axis('off')

        # Capas (de abajo hacia arriba)
        ax2.add_patch(patches.Rectangle((3, 5), 18, 3, facecolor='black', edgecolor='black'))  # geomembrana
        ax2.text(22, 6, 'Geomembrana impermeable', fontsize=10)

        # Drenaje
        ax2.add_patch(patches.Rectangle((3, 8), 18, 15, facecolor='#A9A9A9', edgecolor='black', hatch='///'))
        ax2.text(22, 18, 'Capa drenaje\nGrava 20-60 mm\n(0.15 m)', fontsize=10)

        # Tubo colector
        ax2.add_patch(patches.Rectangle((5, 13), 14, 3, facecolor='#333333'))
        for xt in range(6, 18, 3):
            ax2.plot([xt, xt], [13, 16], color='#00BFFF', linewidth=7)
        ax2.text(22, 13, 'Tubo colector drenaje Ø150 mm', fontsize=10)

        # Grava media
        ax2.add_patch(patches.Rectangle((3, 23), 18, 25, facecolor='#C0C0C0', edgecolor='black', hatch='...'))
        ax2.text(22, 38, 'Capa media\nGrava 5-15 mm\n(0.25 m)', fontsize=10)

        # Grava fina
        ax2.add_patch(patches.Rectangle((3, 48), 18, 35, facecolor='#E5D5B8', edgecolor='black', hatch='|||'))
        ax2.text(22, 68, 'Capa filtrante\nGrava fina 2-6 mm\n(0.35 m)', fontsize=10)

        # Flujo vertical
        for fx in [6, 11, 16]:
            ax2.arrow(fx, 80, 0, -22, head_width=1, head_length=4, fc='blue', ec='blue', linewidth=2.5)

        # Borde libre
        ax2.add_patch(patches.Rectangle((3, 83), 18, 18, facecolor='#E0F0FF', edgecolor='black', alpha=0.7))
        ax2.text(22, 90, 'Borde libre\n(0.18 m)', fontsize=10)

        # Plantas
        ax2.text(12, 103, 'Plantas emergentes\n(Phragmites australis)', ha='center', fontsize=12, color='darkgreen')

        # Distribución superior
        ax2.plot([3, 21], [96, 96], color='black', linewidth=6)
        for p in [5, 9, 13, 17]:
            ax2.plot([p, p], [94, 98], color='#1E90FF', linewidth=5)

        # Escala
        ax2.plot([3, 21], [2, 2], color='black', linewidth=3)
        ax2.text(3, 0, '0 m', fontsize=10)
        ax2.text(12, 0, '9 m', fontsize=10)
        ax2.text(21, 0, '18 m', fontsize=10)

        plt.tight_layout()
        
        # Usar output_dir si se proporciona, sino usar self.ruta_figuras
        if output_dir is None:
            output_dir = self.ruta_figuras
        os.makedirs(output_dir, exist_ok=True)
        
        # Nombre de archivo con el caudal real
        ruta_salida = os.path.join(output_dir, f'humedal_vertical_{caudal_Ls:.1f}Ls_esquema.png')
        plt.savefig(ruta_salida, dpi=300, bbox_inches='tight')
        plt.close()

        return ruta_salida

    def generar_esquema_matplotlib(self, output_dir=None):
        """
        Genera el esquema del humedal vertical según la ruta de diseño (A o B).
        Ruta B (Francés Tropical): 2 celdas en paralelo, ciclos 3.5d/3.5d
        Ruta A (Clásico): 3+2 filtros en 2 etapas, ciclos más largos
        """
        cfg = self.cfg
        ruta = self.datos['ruta']  # Dato obligatorio, no usar fallback
        Q_Ls = cfg.Q_linea_L_s  # Caudal real por línea
        
        if ruta == 'B':
            # Sistema Francés Tropical - 2 celdas en operación alterna
            return self.generar_esquema_linea_humedal_2celdas(output_dir)
        else:
            # Sistema Clásico - 2 etapas (3+2 filtros)
            return self.generar_esquema_humedal_matplotlib(Q_Ls, n_modulos=3, output_dir=output_dir)
    
    def _generar_esquema_png(self):
        """Genera el esquema de la línea de humedal vertical usando los valores reales de diseño."""
        return self.generar_esquema_matplotlib()


if __name__ == "__main__":
    import sys
    import os
    import subprocess

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_dir)

    from ptar_dimensionamiento import ConfigDiseno, dimensionar_humedal_vertical

    print("=" * 60)
    print("TEST - Generador Humedal Vertical")
    print("=" * 60)

    print("[1] Creando configuracion...")
    cfg = ConfigDiseno()

    print("[2] Dimensionando humedal vertical...")
    datos = dimensionar_humedal_vertical(cfg)
    print(f"    Ruta: {datos['ruta']}")
    print(f"    Sistema: {datos['sistema']}")
    print(f"    Area total: {datos['A_total_m2']:.1f} m2")
    print(f"    DBO salida: {datos['DBO_salida_mg_L']:.1f} mg/L")

    print("[3] Creando generador LaTeX...")
    gen = GeneradorHumedalVertical(cfg, datos)

    print("[4] Generando contenido LaTeX...")
    latex = gen.generar_completo()
    print(f"    Caracteres generados: {len(latex)}")

    resultados_dir = os.path.join(base_dir, 'resultados', 'test_modular')
    os.makedirs(resultados_dir, exist_ok=True)

    tex_path = os.path.join(resultados_dir, 'humedal_vertical_test.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex)

    doc_path = os.path.join(resultados_dir, 'humedal_vertical_test_completo.tex')
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
\usepackage{float}
\usepackage{xcolor}
\usepackage{hyperref}

\geometry{margin=2.5cm}

\newcommand{\captionequation}[1]{}

\begin{document}

\section{Humedal Artificial de Flujo Vertical (HAFV)}

""" + latex + r"""

\end{document}""")

    print(f"[5] Archivos guardados en: {resultados_dir}")

    print("[6] Compilando PDF...")
    try:
        subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', resultados_dir, doc_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        pdf_path = os.path.join(resultados_dir, 'humedal_vertical_test_completo.pdf')
        if os.path.exists(pdf_path):
            print(f"    PDF generado: {pdf_path}")
    except Exception as e:
        print(f"    ERROR: {e}")

    print("=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
