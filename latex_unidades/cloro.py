#!/usr/bin/env python3
"""
Generador LaTeX para Desinfección con Cloro - Modular
Estructura: Dimensionamiento, Verificación, Resultados
"""

import os
import sys

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GeneradorCloro:
    """Generador LaTeX para unidad Desinfección con Cloro."""
    
    def __init__(self, cfg, datos, ruta_figuras='figuras'):
        self.cfg = cfg
        self.datos = datos
        self.ruta_figuras = ruta_figuras
    
    def generar_completo(self) -> str:
        """Genera todo el contenido LaTeX del módulo de cloro en 3 subsections."""
        return "\n\n".join([
            self.generar_descripcion(),
            self.generar_verificacion(),
            self.generar_resultados()
        ])
    
    def generar_esquema(self, output_dir=None):
        """Genera PNG de la camara de contacto con cloro en planta y seccion.
        
        Returns:
            str: Path del archivo generado, o None si falla.
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            print("[WARNING] PIL no disponible, figura no generada")
            return None

        def cargar_fuente(nombre, tamano):
            ruta = os.path.join(os.environ['WINDIR'], 'Fonts', nombre)
            try:
                return ImageFont.truetype(ruta, tamano)
            except OSError:
                return ImageFont.load_default()
        def texto_centrado(draw, xy, texto, fuente, fill=(35, 35, 35)):
            bbox = draw.textbbox((0, 0), texto, font=fuente)
            ancho = bbox[2] - bbox[0]
            alto = bbox[3] - bbox[1]
            draw.text((xy[0] - ancho / 2, xy[1] - alto / 2), texto, font=fuente, fill=fill)

        def flecha(draw, p0, p1, fill, width=5):
            draw.line([p0, p1], fill=fill, width=width)
            dx = p1[0] - p0[0]
            dy = p1[1] - p0[1]
            longitud = max((dx * dx + dy * dy) ** 0.5, 1.0)
            ux = dx / longitud
            uy = dy / longitud
            px = -uy
            py = ux
            tam = 16
            punta = [
                p1,
                (p1[0] - ux * tam + px * tam * 0.55, p1[1] - uy * tam + py * tam * 0.55),
                (p1[0] - ux * tam - px * tam * 0.55, p1[1] - uy * tam - py * tam * 0.55),
            ]
            draw.polygon(punta, fill=fill)

        def dibujar_cota_horizontal(draw, x1, x2, y, texto, fuente, color=(50, 50, 50)):
            """Dibuja cota horizontal estilo UASB: linea limpia con ticks verticales."""
            # Linea principal
            draw.line([(x1, y), (x2, y)], fill=color, width=1)
            # Ticks verticales en extremos (como en UASB)
            tick_len = 6
            draw.line([(x1, y - tick_len), (x1, y + tick_len)], fill=color, width=1)
            draw.line([(x2, y - tick_len), (x2, y + tick_len)], fill=color, width=1)
            # Texto centrado debajo
            bbox = draw.textbbox((0, 0), texto, font=fuente)
            ancho_texto = bbox[2] - bbox[0]
            centro_x = (x1 + x2) // 2
            draw.text((centro_x - ancho_texto//2, y + 6), texto, font=fuente, fill=color)

        def dibujar_cota_vertical(draw, y1, y2, x, texto, fuente, color=(50, 50, 50)):
            """Dibuja cota vertical estilo UASB: linea limpia con ticks horizontales."""
            # Linea principal
            draw.line([(x, y1), (x, y2)], fill=color, width=1)
            # Ticks horizontales en extremos (como en UASB)
            tick_len = 6
            draw.line([(x - tick_len, y1), (x + tick_len, y1)], fill=color, width=1)
            draw.line([(x - tick_len, y2), (x + tick_len, y2)], fill=color, width=1)
            # Texto a la izquierda centrado
            bbox = draw.textbbox((0, 0), texto, font=fuente)
            alto_texto = bbox[3] - bbox[1]
            centro_y = (y1 + y2) // 2
            draw.text((x - 8, centro_y - alto_texto//2), texto, font=fuente, fill=color, anchor='rm')

        c = self.datos
        if output_dir is None:
            output_dir = os.path.join(_base_dir, 'resultados', 'figuras')
        os.makedirs(output_dir, exist_ok=True)

        largo = c['largo_m']
        ancho_total = c['ancho_m']
        ancho_canal = c['ancho_canal_m']
        n = int(c['n_canales_serpentin'])
        espesor_bafle = c['espesor_bafle_m']
        h_util = c['h_tanque_m']
        h_total = c['h_total_m']
        h_bordo = h_total - h_util

        img = Image.new('RGB', (1800, 1120), 'white')
        draw = ImageDraw.Draw(img)
        f_titulo = cargar_fuente('arialbd.ttf', 36)
        f_subtitulo = cargar_fuente('arialbd.ttf', 22)  # Reducido para consistencia
        f_texto = cargar_fuente('arial.ttf', 24)
        f_texto_bold = cargar_fuente('arialbd.ttf', 24)
        f_peq = cargar_fuente('arial.ttf', 20)
        f_cota = cargar_fuente('arial.ttf', 18)

        c_muro = (85, 85, 85)
        c_concreto = (248, 248, 248)
        c_agua = (219, 238, 248)
        c_bafle = (144, 164, 174)
        c_bafle_borde = (96, 125, 139)
        c_entrada = (46, 125, 50)
        c_salida = (21, 101, 192)
        c_cloro = (249, 168, 37)
        c_texto = (35, 35, 35)

        # Info general arriba
        draw.text((70, 35), 'Camara de contacto de cloracion tipo culebrin', font=f_titulo, fill=c_texto)
        draw.text((70, 82), f'{n} pasos | recorrido = {c["longitud_recorrido_m"]:.1f} m | relacion recorrido/ancho = {c["relacion_recorrido_ancho"]:.1f}:1',
                  font=f_texto, fill=(70, 70, 70))

        # Vista en planta.
        x0 = 210
        y0 = 140  # Subido para dar espacio a cotas
        Lp = 1120
        Wp = 465
        margen = 28
        canal_h = (Wp - 2 * margen) / n

        draw.rounded_rectangle((x0, y0, x0 + Lp, y0 + Wp), radius=16,
                               fill=c_concreto, outline=c_muro, width=5)
        draw.rounded_rectangle((x0 + margen, y0 + margen, x0 + Lp - margen, y0 + Wp - margen),
                               radius=10, fill=c_agua, outline=(180, 205, 220), width=2)

        # Dibujar bafles para crear n pasos (n-1 bafles)
        gap = 80  # Reducido para bafles mas largos
        baffle_h = max(16, int(espesor_bafle / max(ancho_canal, 0.01) * canal_h * 0.9))
        for i in range(1, n):
            y_b = int(y0 + margen + i * canal_h)
            if i % 2 == 1:
                # Bafle desde izquierda (deja paso a la derecha)
                x_a, x_b = x0 + margen, x0 + Lp - margen - gap
            else:
                # Bafle desde derecha (deja paso a la izquierda)
                x_a, x_b = x0 + margen + gap, x0 + Lp - margen
            draw.rectangle((x_a, y_b - baffle_h // 2, x_b, y_b + baffle_h // 2),
                           fill=c_bafle, outline=c_bafle_borde, width=2)

        puntos = []
        for i in range(n):
            y_c = int(y0 + margen + canal_h * (i + 0.5))
            if i % 2 == 0:
                puntos.append((x0 + margen + 55, y_c))
                puntos.append((x0 + Lp - margen - 55, y_c))
            else:
                puntos.append((x0 + Lp - margen - 55, y_c))
                puntos.append((x0 + margen + 55, y_c))
            if i < n - 1:
                x_turn = x0 + Lp - margen - 55 if i % 2 == 0 else x0 + margen + 55
                y_next = int(y0 + margen + canal_h * (i + 1.5))
                puntos.append((x_turn, y_next))

        for i in range(len(puntos) - 1):
            draw.line((puntos[i], puntos[i + 1]), fill=c_salida, width=6)
        for i in range(1, len(puntos), 3):
            if i < len(puntos):
                flecha(draw, puntos[i - 1], puntos[i], c_salida, width=6)

        y_in = int(y0 + margen + canal_h * 0.5)
        flecha(draw, (x0 - 140, y_in), (x0 + margen + 45, y_in), c_entrada, width=7)
        draw.text((x0 - 180, y_in - 68), 'Entrada\nefluente tratado', font=f_peq, fill=c_entrada)
        draw.ellipse((x0 + margen + 65, y_in - 18, x0 + margen + 101, y_in + 18),
                     fill=c_cloro, outline=(120, 90, 0), width=3)
        x_dosis = x0 + margen + 115
        y_dosis = y_in - 86
        draw.rounded_rectangle((x_dosis - 8, y_dosis - 6, x_dosis + 285, y_dosis + 54),
                               radius=8, fill=(255, 255, 255), outline=(238, 196, 93), width=1)
        draw.text((x_dosis, y_dosis),
                  f'Dosificacion NaOCl\nDosis = {c["dosis_cloro_mg_L"]:.1f} mg/L',
                  font=f_peq, fill=(109, 76, 0))

        y_out = int(y0 + margen + canal_h * (n - 0.5))
        x_out = x0 + Lp - margen - 55 if (n - 1) % 2 == 0 else x0 + margen + 55
        flecha(draw, (x_out, y_out), (x_out + 150, y_out), c_salida, width=7)
        draw.text((x_out + 160, y_out - 55), 'Salida\ndesinfectada', font=f_peq, fill=c_salida)

        # Cotas vista en planta
        # Cota horizontal (largo) - abajo, recortada para que no se extienda tanto
        dibujar_cota_horizontal(draw, x0 + 5, x0 + Lp - 5, y0 + Wp + 15, f'L = {largo:.1f} m', f_cota)
        # Cota vertical (ancho) - izquierda
        dibujar_cota_vertical(draw, y0 + 5, y0 + Wp - 5, x0 - 12, f'B = {ancho_total:.1f} m', f_cota)

        # Titulo de la vista (abajo, separado de las cotas)
        draw.text((x0 + Lp//2, y0 + Wp + 48), 'Vista en planta', font=f_subtitulo, fill=c_texto, anchor='mm')

        # Seccion transversal.
        sx = 210
        sy = 700  # Subido para dar mas espacio
        sw = 850
        sh_agua = 215
        sh_bordo = 42
        
        draw.rounded_rectangle((sx, sy, sx + sw, sy + sh_agua + sh_bordo), radius=12,
                               fill=c_concreto, outline=c_muro, width=5)
        draw.rectangle((sx + 25, sy + sh_bordo, sx + sw - 25, sy + sh_bordo + sh_agua - 20),
                       fill=c_agua, outline=(180, 205, 220), width=2)
        draw.line((sx + 25, sy + sh_bordo, sx + sw - 25, sy + sh_bordo),
                  fill=c_salida, width=3)
        for k in range(1, n):
            x_b = int(sx + 25 + k * (sw - 50) / n)
            draw.rectangle((x_b - 5, sy + sh_bordo + 8, x_b + 5, sy + sh_bordo + sh_agua - 30),
                           fill=c_bafle, outline=c_bafle_borde)

        # Cotas seccion transversal - solo altura total y ancho
        x_cotas = sx - 30  # Posicion X para cota vertical (mas a la izquierda)
        
        # Solo altura total (H)
        dibujar_cota_vertical(draw, sy, sy + sh_agua + sh_bordo, x_cotas,
                              f'H = {h_total:.2f} m', f_cota)
        # Cota horizontal (ancho del tanque)
        dibujar_cota_horizontal(draw, sx + 5, sx + sw - 5, sy + sh_agua + sh_bordo + 18, f'B = {ancho_total:.1f} m', f_cota)

        # Titulo de la seccion (abajo, separado de las cotas)
        draw.text((sx + sw//2, sy + sh_agua + sh_bordo + 55), 'Seccion transversal', font=f_subtitulo, fill=c_texto, anchor='mm')

        # Info tecnica a la derecha de la seccion
        x_txt = sx + sw + 40
        draw.text((x_txt, sy + 35), f'Profundidad util = {h_util:.1f} m', font=f_texto_bold, fill=c_texto)
        draw.text((x_txt, sy + 75), f'Bordo libre = {h_bordo:.2f} m', font=f_texto, fill=c_texto)
        draw.text((x_txt, sy + 115), f'Volumen util = {c["V_contacto_m3"]:.1f} m3', font=f_texto, fill=c_texto)
        draw.text((x_txt, sy + 155), f'TRH real = {c["TRH_real_min"]:.1f} min', font=f_texto, fill=c_texto)
        draw.text((x_txt, sy + 195), f'CT = {c["CT_mg_min_L"]:.1f} mg min/L', font=f_texto, fill=(109, 76, 0))

        fig_path = os.path.join(output_dir, 'Esquema_Camara_Contacto_Cloro.png')
        img.save(fig_path, 'PNG', dpi=(200, 200))
        
        return fig_path

    def generar_esquema_matplotlib(self, output_dir=None):
        """Wrapper para compatibilidad con generar_tren.py"""
        return self.generar_esquema(output_dir)

    def generar_descripcion(self) -> str:
        """Genera subsection Dimensionamiento con teoría y cálculos."""
        cfg = self.cfg
        c = self.datos
        
        return rf"""



La desinfección constituye la etapa final del proceso de tratamiento de aguas residuales, cuyo objetivo es la inactivación de microorganismos patógenos (bacterias, virus y protozoos) presentes en el efluente tratado, garantizando que su descarga al cuerpo receptor no represente riesgo para la salud pública ni para los ecosistemas acuáticos. En el contexto de la normativa ecuatoriana, la TULSMA (Texto Unificado de Legislación Secundaria del Ministerio del Ambiente) establece un límite máximo de {c['limite_TULSMA_CF_NMP']:.0f} NMP/100mL para coliformes fecales en vertimientos de aguas residuales tratadas.

El mecanismo de desinfección con compuestos clorados se fundamenta en la oxidación de componentes celulares esenciales de los microorganismos. El hipoclorito de sodio (NaOCl), al disolverse en agua, establece un equilibrio químico que genera ácido hipocloroso (HOCl) según la siguiente reacción:

\begin{{equation}}
\text{{NaOCl}} + \text{{H}}_2\text{{O}} \rightleftharpoons \text{{HOCl}} + \text{{Na}}^+ + \text{{OH}}^-
\end{{equation}}
\captionequation{{Disolución del hipoclorito de sodio en agua}}

El ácido hipocloroso (HOCl) es la especie biocida predominante y efectiva, siendo aproximadamente 80--100 veces más potente como desinfectante que el ion hipoclorito (OCl$^-$). La especiación entre HOCl y OCl$^-$ depende críticamente del pH del agua, según el siguiente equilibrio:

\begin{{equation}}
\text{{HOCl}} \rightleftharpoons \text{{H}}^+ + \text{{OCl}}^- \quad (\text{{pKa}} \approx 7,5 \text{{ a 25°C}})
\end{{equation}}
\captionequation{{Equilibrio ácido-base del ácido hipocloroso}}

A pH inferior a 7,5 predomina el HOCl (forma más efectiva), mientras que a pH superior a 7,5 predomina el OCl$^-$. Para el rango típico de pH de aguas residuales tratadas (6,5--8,5), se asegura una fracción significativa de HOCl que garantiza la eficacia desinfectante. La temperatura del agua también afecta este equilibrio: a mayor temperatura, el valor de pKa disminuye ligeramente, favoreciendo la forma HOCl.

\textbf{{Mecanismos de inactivación microbiana}}

La acción biocida del cloro se ejerce mediante múltiples mecanismos simultáneos: (1) \textit{{oxidación de la pared celular}}, alterando la permeabilidad y causando lisis celular; (2) \textit{{denaturación de enzimas}}, particularmente aquellas con grupos sulfhidrilo (-SH) que son oxidados a disulfuros; (3) \textit{{daño al material genético}}, mediante reacción con bases nitrogenadas del ADN y ARN; y (4) \textit{{alteración del metabolismo celular}}, inhibiendo la síntesis de ATP y otras funciones energéticas.

La susceptibilidad de los microorganismos al cloro varía significativamente. Las bacterias (incluyendo coliformes fecales) son generalmente las más susceptibles, con valores CT de 0,1--5 mg$\cdot$min/L para 2-log de reducción. Los virus requieren CT mayores (5--20 mg$\cdot$min/L), mientras que los protozoos como \textit{{Giardia}} y \textit{{Cryptosporidium}} son los más resistentes, requiriendo CT de 30--100 mg$\cdot$min/L o alternativas como UV o ozono.

\textbf{{El concepto CT como parámetro de diseño}}

El producto concentración-tiempo (CT) constituye el parámetro fundamental para el dimensionamiento de sistemas de desinfección. Fue desarrollado por la USEPA como criterio regulatorio y ha sido adoptado internacionalmente. Físicamente, el CT representa la exposición acumulada de los microorganismos al desinfectante, integrando tanto la concentración residual como el tiempo de contacto efectivo.

El CT requerido depende de: (a) el microorganismo objetivo y la reducción logarítmica deseada, (b) la temperatura del agua (a mayor temperatura, menor CT requerido debido a cinética más rápida), (c) el pH (afecta la especiación del cloro), y (d) la presencia de materia orgánica y otros consumidores de cloro (demanda).

Según Metcalf \& Eddy \cite{{metcalf2014}} y la USEPA \cite{{usepa2003}}, los valores CT típicos para inactivación de coliformes en efluentes secundarios son:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item CT = 5--10 mg$\cdot$min/L: 2--3 log de reducción (99--99,9\%)
    \item CT = 10--20 mg$\cdot$min/L: 3--4 log de reducción (99,9--99,99\%)
    \item CT = 20--40 mg$\cdot$min/L: 4--5 log de reducción (99,99--99,999\%)
\end{{itemize}}

\textbf{{Criterio de disenio basado en CF objetivo}}

El dimensionamiento del sistema de desinfección se fundamenta en un criterio de diseño explícito basado en la concentración de coliformes fecales (CF) objetivo. A diferencia de un enfoque de dosis fija, este método garantiza que el sistema sea capaz de alcanzar el nivel de inactivación microbiológica requerido, partiendo de la carga de coliformes de entrada y definiendo la reducción logarítmica necesaria para cumplir con el objetivo de calidad del efluente.

Para este diseño, se establece un CF objetivo de {c['CF_objetivo_NMP']:.0f} NMP/100mL, correspondiente al límite establecido por la TULSMA para vertimiento de aguas residuales tratadas. Con una concentración de entrada de {c['CF_entrada_NMP']:.0f} NMP/100mL, la reducción logarítmica requerida es:

\begin{{equation}}
\text{{Log reducción}}_{{\text{{req}}}} = \log_{{10}}\left(\frac{{CF_{{\text{{entrada}}}}}}{{CF_{{\text{{objetivo}}}}}}\right) = \log_{{10}}\left(\frac{{{c['CF_entrada_NMP']:.0f}}}{{{c['CF_objetivo_NMP']:.0f}}}\right) = {c['log_reduccion_requerida']:.2f} \text{{ log}}
\end{{equation}}
\captionequation{{Log reduccion requerida para cumplir CF objetivo}}

El CT requerido para lograr esta reducción se calcula mediante el coeficiente de inactivación adoptado:

\begin{{equation}}
CT_{{\text{{req}}}} = \frac{{\text{{Log reducción}}_{{\text{{req}}}}}}{{k}} = \frac{{{c['log_reduccion_requerida']:.2f}}}{{{c['k_log_red']:.2f}}} = {c['CT_requerido']:.1f} \text{{ mg$\cdot$min/L}}
\end{{equation}}
\captionequation{{CT requerido para alcanzar la reduccion logaritmica objetivo}}

\textbf{{Filosofía de diseño adoptada: TRH base + Residual calculado}}

El diseño adopta una filosofía de tiempo de contacto base y residual calculado. Primero se dimensiona el tanque de contacto con un TRH base de referencia ({c['TRH_base_config']:.0f} min), obteniéndose un TRH real de {c['TRH_real_min']:.1f} min según las dimensiones constructivas adoptadas. Posteriormente, se calcula el residual requerido para alcanzar el CT objetivo con ese TRH real:

\begin{{equation}}
C_{{\text{{req}}}} = \frac{{CT_{{\text{{req}}}}}}{{TRH_{{\text{{real}}}}}} = \frac{{{c['CT_requerido']:.1f}}}{{{c['TRH_real_min']:.1f}}} = {c['residual_requerido']:.2f} \text{{ mg/L}}
\end{{equation}}
\captionequation{{Residual requerido para alcanzar CT objetivo con TRH real}}

El residual adoptado corresponde al valor requerido calculado, optimizando la dosis para cumplir justo con el objetivo de desinfección:

\begin{{equation}}
C_{{\text{{adoptado}}}} = C_{{\text{{req}}}} = {c['cloro_residual_mg_L']:.2f} \text{{ mg/L}}
\end{{equation}}
\captionequation{{Residual adoptado para cumplir CF objetivo}}

\textit{{Nota operativa:}} El residual calculado ({c['residual_requerido']:.2f} mg/L) es inferior al mínimo operativo recomendado ({c['residual_minimo_operativo']:.1f} mg/L) para garantizar margen de seguridad en la operación. Se recomienda monitorear periódicamente para asegurar que el residual efectivo se mantenga en el rango de {c['rango_residual_monitoreo_mg_L_texto']}.

El CT real alcanzado con el residual adoptado y el TRH real es:

\begin{{equation}}
CT_{{\text{{real}}}} = C_{{\text{{adoptado}}}} \times TRH_{{\text{{real}}}} = {c['cloro_residual_mg_L']:.2f} \times {c['TRH_real_min']:.1f} = {c['CT_mg_min_L']:.1f} \text{{ mg$\cdot$min/L}}
\end{{equation}}
\captionequation{{CT real alcanzado}}

Como criterio adicional de verificación, se establece un CT mínimo de {c['CT_min_recomendado']:.0f} mg$\cdot$min/L, valor conservador que asegura el cumplimiento del límite de coliformes fecales establecido por la TULSMA, considerando las variaciones operativas esperadas.

\textbf{{Demanda de cloro y dosificación}}

La demanda de cloro representa la cantidad de cloro consumida por reacciones con sustancias presentes en el agua antes de que quede disponible cloro residual libre para desinfección. Los principales consumidores son: amoníaco (formando cloraminas), materia orgánica reducida, compuestos férricos y manganesos, y sulfuros. En efluentes secundarios tratados (post-filtro percolador), la demanda típica adoptada para referencia de diseño varía entre {c['rango_demanda_cloro_mg_L_texto']} dependiendo de la calidad del efluente.

El cloro residual es la concentración que permanece después de satisfacer la demanda y es la que ejerce el efecto desinfectante. El diseño debe garantizar un residual mínimo de {c['cloro_residual_mg_L']:.1f} mg/L al final del tiempo de contacto para asegurar eficacia. La dosis total a aplicar es:

\begin{{equation}}
\text{{Dosis total}} = \text{{Demanda}} + \text{{Residual objetivo}}
\end{{equation}}
\captionequation{{Descomposición de la dosis de cloro}}

\textbf{{Diseño del tanque de contacto}}

El tanque de contacto se dimensiona para proporcionar un tiempo de retención hidráulico (TRH) adecuado que permita alcanzar el CT objetivo con el residual calculado. El TRH efectivo es el tiempo que permanece el agua en el tanque, calculado como el cociente entre el volumen útil y el caudal. Según Metcalf \& Eddy, para desinfección de efluentes secundarios se recomienda un TRH de {c['rango_TRH_min_texto']}; para este caso, se parte de un TRH base de {c['TRH_base_config']:.0f} min para el dimensionamiento geométrico.

La geometría del tanque debe favorecer el flujo en pistón (plug flow) para evitar cortocircuitos hidráulicos que reduzcan el tiempo efectivo de contacto. Por ello, el volumen de contacto se organiza como una cámara con bafles alternados tipo culebrín, de modo que el recorrido hidráulico aumente y la relación recorrido/ancho del canal sea verificable.

\textbf{{Parámetros de diseño adoptados}}

El sistema se dimensiona considerando los siguientes parámetros fundamentales, establecidos según criterios bibliográficos y normativos:

\begin{{table}}[H]
\centering
\caption{{Parámetros de diseño de la desinfección}}
\small
\begin{{tabular}}{{@{{}}p{{0.28\textwidth}}p{{0.18\textwidth}}p{{0.22\textwidth}}p{{0.18\textwidth}}@{{}}}}
\toprule
\textbf{{Parámetro}} & \textbf{{Valor adoptado}} & \textbf{{Rango/Unidad}} & \textbf{{Fuente}} \\
\midrule
Demanda de cloro & {c['demanda_cloro_mg_L']:.1f} mg/L & {c['rango_demanda_cloro_mg_L_texto']} & Estimado efluente post-sedimentador \\
Residual requerido & {c['residual_requerido']:.2f} mg/L & -- & Cálculo desde CT \\
Residual adoptado & {c['cloro_residual_mg_L']:.2f} mg/L & $>${c['residual_requerido']:.2f} mg/L & Para cumplir CF objetivo \\
Dosis total & {c['dosis_cloro_mg_L']:.1f} mg/L & {c['rango_dosis_cloro_mg_L_texto']} & Metcalf \& Eddy \cite{{metcalf2014}} \\
TRH base de diseño & {c['TRH_base_config']:.0f} min & {c['rango_TRH_min_texto']} & Configuración \\
TRH real del tanque & {c['TRH_real_min']:.1f} min & $\geq$ {c['TRH_base_config']:.0f} min & Dimensionado \\
Relación recorrido/ancho & {c['relacion_recorrido_ancho']:.1f}:1 & $\geq$ {c['relacion_recorrido_ancho_min']:.0f}:1 & Criterio de flujo pistón \\
CT requerido & {c['CT_requerido']:.1f} mg$\cdot$min/L & -- & Desde log reducción \\
CT real & {c['CT_mg_min_L']:.1f} mg$\cdot$min/L & $\geq$ {c['CT_min_recomendado']:.0f} mg$\cdot$min/L & Residual $\times$ TRH \\
\bottomrule
\end{{tabular}}
\end{{table}}

La dosis total de cloro se descompone en la demanda del efluente (consumida por amoníaco y materia orgánica) más el residual requerido para desinfección:

\begin{{equation}}
\text{{Dosis total}} = \text{{Demanda}} + \text{{Residual}} = {c['demanda_cloro_mg_L']:.1f} + {c['cloro_residual_mg_L']:.1f} = {c['dosis_cloro_mg_L']:.1f} \text{{ mg/L}}
\end{{equation}}
\captionequation{{Dosis total de cloro}}

\textbf{{Cálculo del producto CT}}

La eficacia de la desinfección se cuantifica mediante el parámetro CT:

\begin{{equation}}
CT = C \times t
\end{{equation}}
\captionequation{{Producto concentracion-tiempo CT}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$CT$] = Producto concentración-tiempo (mg$\cdot$min/L)
    \item[$C$] = Cloro residual ({c['cloro_residual_mg_L']:.1f} mg/L)
    \item[$t$] = Tiempo de contacto real en la cámara ({c['TRH_real_min']:.1f} min)
\end{{itemize}}

\begin{{equation}}
CT = {c['cloro_residual_mg_L']:.2f} \times {c['TRH_real_min']:.1f} = {c['CT_mg_min_L']:.1f} \text{{ mg$\cdot$min/L}}
\end{{equation}}

La reducción de coliformes se estima mediante una relación empírica simplificada, válida como aproximación preliminar de diseño para efluentes secundarios típicos:

\begin{{equation}}
\text{{Log reducción}} \approx {cfg.desinfeccion_coef_log_red:.2f} \times CT
\end{{equation}}
\captionequation{{Estimacion empirica de log-reduccion (simplificacion para diseño preliminar)}}

\textit{{Nota metodológica:}} Esta relación lineal es una simplificación empírica calibrada para condiciones típicas de aguas residuales tratadas (pH 6.5--8.5, temperatura 20--25°C, baja materia orgánica residual). El modelo cinético formal de inactivación microbiana es el de Chick-Watson: $N/N_0 = e^{{-k \cdot C^n \cdot t}}$, donde $k$ es la constante de inactivación específica para cada microorganismo y $n$ es el coeficiente de dilución (típicamente $n \approx 1$ para cloro libre). La forma lineal utilizada es práctica para diseño preliminar pero debe verificarse con ensayos de desinfección específicos si se requiere precisión rigurosa.

\begin{{equation}}
\text{{Log reducción}} \approx {cfg.desinfeccion_coef_log_red:.2f} \times {c['CT_mg_min_L']:.0f} = {c['log_reduccion']:.1f} \text{{ log}}
\end{{equation}}

Los coliformes finales se calculan como:

\begin{{equation}}
CF_{{final}} = \frac{{CF_{{inicial}}}}{{10^{{\text{{Log reduccion}}}}}} = \frac{{{c['CF_entrada_NMP']:.0f}}}{{10^{{{c['log_reduccion']:.1f}}}}} = {c['CF_final_NMP']:.0f} \text{{ NMP/100mL}}
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
    \item[$Q$] = Caudal ({c['Q_m3_d']:.1f} m³/d = {c['Q_m3_d']/24/60:.3f} m³/min)
    \item[$t$] = Tiempo de contacto base ({c['TRH_base_config']:.0f} min)
\end{{itemize}}

\begin{{equation}}
V_{{min}} = {c['Q_m3_d']/24/60:.3f} \times {c['TRH_base_config']:.0f} = {c['V_contacto_min_m3']:.1f} \text{{ m}}^3
\end{{equation}}

{c['texto_volumen_contacto']}

La cámara se resuelve con {c['n_canales_serpentin']} canales en culebrín, ancho hidráulico de {c['ancho_canal_m']:.2f} m por canal, bafles de {c['espesor_bafle_m']:.2f} m y un recorrido hidráulico total de {c['longitud_recorrido_m']:.1f} m. Las dimensiones en planta resultantes son {c['largo_m']:.1f} m de largo por {c['ancho_m']:.1f} m de ancho.

\textbf{{Consumo de cloro y requerimientos de producto comercial}}

El consumo de cloro activo (como Cl$_2$) se calcula como:

\begin{{equation}}
\text{{Consumo Cl}}_2 = \frac{{D \times Q}}{{1000}} = \frac{{{c['dosis_cloro_mg_L']:.1f} \times {c['Q_m3_d']:.1f}}}{{1000}} = {c['consumo_cloro_kg_d']:.2f} \text{{ kg Cl}}_2\text{{/d}}
\end{{equation}}

\textbf{{Conversión a hipoclorito de sodio comercial (NaOCl):}}

El hipoclorito de sodio se comercializa típicamente al {c['rango_NaOCl_comercial_pct_texto']} de cloro disponible. La conversión se realiza mediante:

\begin{{equation}}
\text{{Consumo NaOCl}} = \frac{{\text{{Consumo Cl}}_2}}{{[\% \text{{ NaOCl}}]}} = \frac{{{c['consumo_cloro_kg_d']:.2f}}}{{{c['concentracion_NaOCl_pct']:.0f}\%}} = {c['consumo_NaOCl_kg_d']:.1f} \text{{ kg NaOCl/d}}
\end{{equation}}
\captionequation{{Conversion a hipoclorito de sodio comercial}}

Considerando una densidad de {cfg.desinfeccion_densidad_NaOCl:.2f} kg/L para la solución al {c['concentracion_NaOCl_pct']:.0f}\%:

\begin{{equation}}
\text{{Volumen NaOCl}} = \frac{{{c['consumo_NaOCl_kg_d']:.1f} \text{{ kg/d}}}}{{{cfg.desinfeccion_densidad_NaOCl:.2f} \text{{ kg/L}}}} = {c['volumen_NaOCl_L_d']:.1f} \text{{ L/d}} \approx {c['volumen_almacenamiento_L']:.0f} \text{{ L/mes}}
\end{{equation}}

El volumen de almacenamiento en bodega se recomienda para {c['dias_almacenamiento']:.0f} días de operación: {c['volumen_almacenamiento_L']:.0f} L (equivalente a {c['volumen_almacenamiento_L']/1000:.1f} m³).

\textbf{{Nota sobre subproductos de la desinfección}}

La cloración de aguas residuales puede generar subproductos de desinfección (DBPs, por sus siglas en inglés), principalmente trihalometanos (THMs) y ácidos haloacéticos (HAAs), como resultado de la reacción del cloro con la materia orgánica residual presente en el efluente tratado.

Para plantas de tratamiento de pequeña escala como la proyectada, la formación de THMs puede controlarse mediante:
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item \textbf{{Control de dosis:}} Aplicar la dosis mínima efectiva que garantice el residual requerido, evitando sobredosis innecesaria.
    \item \textbf{{Monitoreo de residual:}} Mantener el residual combinado en el rango de {c['cloro_residual_mg_L']:.1f}--1.0 mg/L, evitando valores superiores que favorecen la formación de DBPs.
    \item \textbf{{Calidad del efluente previo:}} Asegurar que el tratamiento biológico previo (HAFV) remueva adecuadamente la materia orgánica, ya que menor DQO/DBO residual implica menor potencial de formación de THMs.
    \item \textbf{{Monitoreo periódico:}} Realizar análisis trimestral de THMs totales en el efluente final si la autoridad ambiental lo requiere; para vertimiento a cuerpos receptores no destinados a consumo humano, los requisitos son menos estrictos que para agua potable.
\end{{itemize}}

Para el presente diseño, el riesgo de formación de THMs se considera manejable mediante la operación adecuada del sistema de dosificación y el control de residual, dado que el efluente del HAFV tiene baja concentración de materia orgánica precursora y la dosis de cloro aplicada es moderada."""

    def generar_verificacion(self) -> str:
        """Genera subsection Verificación con comprobaciones de cumplimiento."""
        c = self.datos
        t = c['comparacion_tulsma']
        
        # Precalcular límites formateados (maneja None)
        def fmt_limite(val):
            return f"{int(val)}" if val is not None else "---"
        
        lim_agua_dulce = fmt_limite(t['agua_dulce']['limite_CF'])
        lim_agua_marina = fmt_limite(t['agua_marina']['limite_CF'])
        lim_alcant = fmt_limite(t['alcantarillado']['limite_CF'])
        lim_flora = fmt_limite(t['flora_fauna']['limite_CF'])
        lim_agric = fmt_limite(t['agricola_riego']['limite_CF'])
        lim_pec = fmt_limite(t['pecuario']['limite_CF'])
        lim_rec_pri = fmt_limite(t['recreativo_primario']['limite_CF'])
        lim_rec_sec = fmt_limite(t['recreativo_secundario']['limite_CF'])
        lim_cons_hum = fmt_limite(t['consumo_humano']['limite_CF'])
        
        return rf"""\subsection{{Verificación}}

\textbf{{Verificación de cumplimiento normativo}}

El sistema de desinfección se verifica contra los criterios establecidos en la TULSMA y las recomendaciones de Metcalf \& Eddy para asegurar la eficacia del proceso.


El Texto Unificado de Legislación Secundaria del Ministerio del Ambiente (TULSMA) establece diferentes límites de coliformes fecales según el uso receptor del agua. La siguiente tabla compara el valor calculado de coliformes finales ({c['CF_final_NMP']:.0f} NMP/100mL) con los límites establecidos para cada categoría de uso:

\begin{{table}}[H]
\centering
\caption{{Comparación con límites TULSMA por uso del agua}}
\small
\begin{{tabular}}{{@{{}}llcc@{{}}}}
\toprule
\textbf{{Uso / Tabla TULSMA}} & \textbf{{CF (límite)}} & \textbf{{CF calculado}} & \textbf{{Dictamen}} \\
\midrule
Agua dulce -- {t['agua_dulce']['tabla']} & $\leq${lim_agua_dulce} & {t['agua_dulce']['CF_calculado']:.0f} & \textbf{{{t['agua_dulce']['dictamen']}}} \\
Agua marina -- {t['agua_marina']['tabla']} & $\leq${lim_agua_marina} & {t['agua_marina']['CF_calculado']:.0f} & \textbf{{{t['agua_marina']['dictamen']}}} \\
Alcantarillado -- {t['alcantarillado']['tabla']} & {lim_alcant} & {t['alcantarillado']['CF_calculado']:.0f} & \textbf{{{t['alcantarillado']['dictamen']}}} \\
Flora y fauna -- {t['flora_fauna']['tabla']} & $\leq${lim_flora} & {t['flora_fauna']['CF_calculado']:.0f} & \textbf{{{t['flora_fauna']['dictamen']}}} \\
Agrícola/riego -- {t['agricola_riego']['tabla']} & $\leq${lim_agric} & {t['agricola_riego']['CF_calculado']:.0f} & \textbf{{{t['agricola_riego']['dictamen']}}} \\
Pecuario -- {t['pecuario']['tabla']} & $\leq${lim_pec} & {t['pecuario']['CF_calculado']:.0f} & \textbf{{{t['pecuario']['dictamen']}}} \\
Recreativo primario -- {t['recreativo_primario']['tabla']} & $\leq${lim_rec_pri} & {t['recreativo_primario']['CF_calculado']:.0f} & \textbf{{{t['recreativo_primario']['dictamen']}}} \\
Recreativo secundario -- {t['recreativo_secundario']['tabla']} & $\leq${lim_rec_sec} & {t['recreativo_secundario']['CF_calculado']:.0f} & \textbf{{{t['recreativo_secundario']['dictamen']}}} \\
Consumo humano -- {t['consumo_humano']['tabla']} & $\leq${lim_cons_hum} & {t['consumo_humano']['CF_calculado']:.0f} & \textbf{{{t['consumo_humano']['dictamen']}}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

{c['verif_TULSMA_texto']}

El producto CT es indicativo de la eficacia de la desinfección. Un valor CT adecuado garantiza la reducción suficiente de microorganismos patógenos.

\begin{{table}}[H]
\centering
\caption{{Verificación del producto CT}}
\begin{{tabular}}{{@{{}}lcc@{{}}}}
\toprule
\textbf{{Parámetro}} & \textbf{{Valor calculado}} & \textbf{{Valor recomendado}} \\
\midrule
CT calculado & {c['CT_mg_min_L']:.0f} mg$\cdot$min/L & $\geq$ {c['CT_min_recomendado']:.0f} mg$\cdot$min/L \\
Estado & \multicolumn{{2}}{{c}}{{\textbf{{{c['estado_CT']}}}}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

{c['verif_CT_texto']}


\textbf{{Notas de operación}}

{c['texto_operacion_cloro']}

La reducción logarítmica alcanzada es de {c['log_reduccion']:.1f} log, lo que representa una reducción porcentual del {c['pct_reduccion']:.1f}\% de los coliformes presentes en el efluente."""

    def generar_resultados(self) -> str:
        """Genera subsection Resultados con resumen de dimensiones, parámetros y figura."""
        c = self.datos
        
        # Generar figura (igual que en sedimentador_secundario.py)
        if os.path.isabs(self.ruta_figuras):
            output_dir = self.ruta_figuras
            latex_ruta_base = 'figuras'
        else:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados', self.ruta_figuras)
            latex_ruta_base = self.ruta_figuras
        
        fig_path = self.generar_esquema(output_dir)
        
        if fig_path:
            fig_relativa = (latex_ruta_base + '/' + os.path.basename(fig_path)).replace('\\', '/')
            figura_latex = rf"""\begin{{figure}}[H]
\centering
\includegraphics[width=0.95\textwidth]{{{fig_relativa}}}
\caption{{Cámara de contacto de cloración tipo culebrín: planta con bafles alternados y sección transversal. Recorrido hidráulico: {c['longitud_recorrido_m']:.1f} m; relación recorrido/ancho: {c['relacion_recorrido_ancho']:.1f}:1; volumen útil adoptado: {c['V_contacto_m3']:.1f} m³.}}
\label{{fig:camara_contacto_cloro}}
\end{{figure}}

"""
        else:
            figura_latex = ""
        
        return rf"""\subsection{{Resultados}}

\begingroup
\small
\begin{{longtable}}{{@{{}}lc@{{}}}}
\caption{{Resumen de dimensiones y parámetros de la desinfección}}\\
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} \\
\midrule
\endfirsthead
\caption[]{{Resumen de dimensiones y parámetros de la desinfección (continuación)}}\\
\toprule
\textbf{{Parámetro}} & \textbf{{Valor}} \\
\midrule
\endhead
\midrule
\multicolumn{{2}}{{r}}{{\textit{{Continúa en la siguiente página}}}} \\
\endfoot
\bottomrule
\endlastfoot
\multicolumn{{2}}{{l}}{{\textit{{Dimensiones del tanque}}}} \\
\midrule
Largo & {c['largo_m']:.1f} m \\
Ancho & {c['ancho_m']:.1f} m \\
Canales del culebrin & {c['n_canales_serpentin']} pasos de {c['ancho_canal_m']:.2f} m \\
Recorrido hidraulico & {c['longitud_recorrido_m']:.1f} m ({c['relacion_recorrido_ancho']:.1f}:1) \\
Profundidad útil & {c['h_tanque_m']:.1f} m \\
Altura total & {c['h_total_m']:.2f} m \\
Volumen útil & {c['V_contacto_m3']:.1f} m³ \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Parámetros de desinfección}}}} \\
\midrule
Demanda de cloro & {c['demanda_cloro_mg_L']:.1f} mg/L \\
Cloro residual & {c['cloro_residual_mg_L']:.1f} mg/L \\
Dosis total & {c['dosis_cloro_mg_L']:.1f} mg/L \\
TRH base & {c['TRH_base_config']:.0f} min \\
TRH real & {c['TRH_real_min']:.1f} min \\
CT & {c['CT_mg_min_L']:.0f} mg$\cdot$min/L \\
Log reducción & {c['log_reduccion']:.1f} log \\
CF final & {c['CF_final_NMP']:.0f} NMP/100mL \\
\midrule
\multicolumn{{2}}{{l}}{{\textit{{Consumo de productos}}}} \\
\midrule
Consumo Cl$_2$ activo & {c['consumo_cloro_kg_d']:.2f} kg/d \\
Concentración NaOCl & {c['concentracion_NaOCl_pct']:.0f} \% \\
Consumo NaOCl & {c['consumo_NaOCl_kg_d']:.1f} kg/d \\
Volumen NaOCl & {c['volumen_NaOCl_L_d']:.1f} L/d ({c['volumen_almacenamiento_L']:.0f} L/mes) \\
Almacenamiento ({c['dias_almacenamiento']:.0f} d) & {c['volumen_almacenamiento_L']:.0f} L ({c['volumen_almacenamiento_L']/1000:.1f} m³) \\
\end{{longtable}}
\endgroup

El sistema de desinfección con hipoclorito de sodio ha sido dimensionado para tratar un caudal de {c['Q_m3_d']:.1f} m³/d, logrando una reducción de {c['pct_reduccion']:.1f}\% de coliformes fecales. El cumplimiento respecto a los límites de la TULSMA depende de la categoría de uso receptor específica del proyecto, conforme al dictamen técnico presentado en la tabla de verificación anterior.\

{figura_latex}

{c['texto_camara_contacto']}

"""


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    import sys
    import subprocess
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_dir)
    
    from ptar_dimensionamiento import ConfigDiseno, dimensionar_desinfeccion_cloro
    
    print("=" * 60)
    print("TEST - GENERADOR MODULAR DE DESINFECCIÓN CON CLORO")
    print("=" * 60)
    
    cfg = ConfigDiseno()
    print(f"\n[1] Q_linea = {cfg.Q_linea_L_s} L/s")
    
    # Coliformes de entrada típicos post-sedimentador secundario
    cf_entrada = 5_000_000  # NMP/100mL
    
    datos = dimensionar_desinfeccion_cloro(cfg, CF_entrada_NMP=cf_entrada)
    print(f"[2] Dimensiones: {datos['largo_m']:.1f}m x {datos['ancho_m']:.1f}m, V={datos['V_contacto_m3']:.1f}m³")
    print(f"    CT={datos['CT_mg_min_L']:.0f} mg·min/L, Log={datos['log_reduccion']:.1f}, CF_final={datos['CF_final_NMP']:.0f} NMP/100mL")
    
    resultados_dir = os.path.join(base_dir, 'resultados', 'test_modular')
    os.makedirs(resultados_dir, exist_ok=True)
    
    figuras_dir = os.path.join(resultados_dir, 'figuras')
    os.makedirs(figuras_dir, exist_ok=True)
    
    gen = GeneradorCloro(cfg, datos, ruta_figuras=figuras_dir)
    latex = gen.generar_completo()
    print(f"[3] LaTeX generado: {len(latex)} chars, {len(latex.split(chr(10)))} lines")
    
    # Guardar solo el contenido (subsections)
    tex_path = os.path.join(resultados_dir, 'cloro_test.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    print(f"[4] Guardado (modular): {tex_path}")
    
    # Generar documento completo para compilación
    doc_latex = r"""\documentclass[12pt,a4paper]{article}
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

\section{Desinfección con Hipoclorito de Sodio}

""" + latex + r"""

\end{document}"""
    
    doc_path = os.path.join(resultados_dir, 'cloro_test_compilable.tex')
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(doc_latex)
    print(f"[5] Guardado (compilable): {doc_path}")
    
    # Compilar PDF
    print("[6] Compilando PDF...")
    try:
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', resultados_dir, doc_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        pdf_path = os.path.join(resultados_dir, 'cloro_test_compilable.pdf')
        if os.path.exists(pdf_path):
            print(f"[7] PDF generado: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
        else:
            print(f"[7] ERROR: PDF no generado")
            print("    stderr:", result.stderr[-300:] if result.stderr else "N/A")
    except Exception as e:
        print(f"[7] ERROR: {e}")
    
    print("=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
