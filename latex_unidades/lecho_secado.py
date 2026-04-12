#!/usr/bin/env python3
"""
Generador LaTeX para Lecho de Secado de Lodos
Reorganizado en 3 subsections: Dimensionamiento, Verificacion, Resultados
"""

import os
import sys

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GeneradorLechoSecado:
    """Generador LaTeX para unidad Lecho de Secado de Lodos."""
    
    def __init__(self, cfg, datos, ruta_figuras='figuras'):
        self.cfg = cfg
        self.datos = datos
        self.ruta_figuras = ruta_figuras
    
    def generar_completo(self) -> str:
        """Genera todo el contenido LaTeX del lecho de secado en 3 subsections."""
        return "\n\n".join([
            self.generar_descripcion(),
            self.generar_verificacion(),
            self.generar_resultados()
        ])
    
    def generar_esquema(self, output_dir=None):
        """Genera PNG del lecho de secado con vista en planta y seccion."""
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
        
        def dibujar_cota_horizontal(draw, x1, x2, y, texto, fuente, color=(50, 50, 50)):
            draw.line([(x1, y), (x2, y)], fill=color, width=1)
            tick_len = 6
            draw.line([(x1, y - tick_len), (x1, y + tick_len)], fill=color, width=1)
            draw.line([(x2, y - tick_len), (x2, y + tick_len)], fill=color, width=1)
            bbox = draw.textbbox((0, 0), texto, font=fuente)
            ancho_texto = bbox[2] - bbox[0]
            centro_x = (x1 + x2) // 2
            draw.text((centro_x - ancho_texto//2, y + 6), texto, font=fuente, fill=color)
        
        def dibujar_cota_vertical(draw, y1, y2, x, texto, fuente, color=(50, 50, 50)):
            draw.line([(x, y1), (x, y2)], fill=color, width=1)
            tick_len = 6
            draw.line([(x - tick_len, y1), (x + tick_len, y1)], fill=color, width=1)
            draw.line([(x - tick_len, y2), (x + tick_len, y2)], fill=color, width=1)
            bbox = draw.textbbox((0, 0), texto, font=fuente)
            alto_texto = bbox[3] - bbox[1]
            centro_y = (y1 + y2) // 2
            draw.text((x - 8, centro_y - alto_texto//2), texto, font=fuente, fill=color, anchor='rm')
        
        l = self.datos
        if output_dir is None:
            output_dir = os.path.join(_base_dir, 'resultados', 'figuras')
        os.makedirs(output_dir, exist_ok=True)
        
        num_bloques = l['num_lineas']
        largo = l['largo_m']
        ancho = l['ancho_m']
        
        img = Image.new('RGB', (1800, 1000), 'white')
        draw = ImageDraw.Draw(img)
        f_titulo = cargar_fuente('arialbd.ttf', 32)
        f_subtitulo = cargar_fuente('arialbd.ttf', 22)
        f_texto = cargar_fuente('arial.ttf', 20)
        f_cota = cargar_fuente('arial.ttf', 18)
        
        c_muro = (85, 85, 85)
        c_concreto = (220, 220, 220)
        c_arena = (238, 203, 140)
        c_grava = (180, 180, 180)
        c_drenaje = (100, 100, 100)
        c_texto = (35, 35, 35)
        
        # Titulo principal
        draw.text((70, 35), 'Lecho de Secado de Lodos', font=f_titulo, fill=c_texto)
        
        # Vista en planta - mostrar bloques
        x0 = 150
        y0 = 100
        sep_bloques = 20
        
        # Dibujar los bloques (uno por linea)
        for i in range(num_bloques):
            x_bloque = x0 + i * (largo * 30 + sep_bloques)
            y_bloque = y0
            
            # Rectangulo del lecho
            draw.rectangle(
                (x_bloque, y_bloque, x_bloque + largo * 30, y_bloque + ancho * 30),
                fill=c_arena, outline=c_muro, width=3
            )
            
            # Texto interno
            texto_centrado(draw, 
                (x_bloque + largo * 15, y_bloque + ancho * 15),
                f'Bloque {i+1}\nLecho de Secado',
                f_texto, fill=c_texto)
            
            # Etiqueta de linea
            draw.text((x_bloque + largo * 15, y_bloque - 25), 
                     f'Linea {i+1}', font=f_texto, fill=c_texto, anchor='mm')
        
        # Cotas de la vista en planta
        x_ultimo = x0 + (num_bloques - 1) * (largo * 30 + sep_bloques)
        ancho_total_dibujo = x_ultimo + largo * 30 - x0
        
        dibujar_cota_horizontal(draw, x0, x0 + largo * 30, y0 + ancho * 30 + 15,
                                f'L = {largo:.1f} m', f_cota)
        dibujar_cota_vertical(draw, y0, y0 + ancho * 30, x0 - 15,
                              f'B = {ancho:.1f} m', f_cota)
        
        # Titulo vista en planta
        draw.text((x0 + ancho_total_dibujo // 2, y0 + ancho * 30 + 45),
                 'Vista en planta (bloques por linea)', font=f_subtitulo, fill=c_texto, anchor='mm')
        
        # Seccion transversal del lecho
        sx = 200
        sy = 450
        sw = 600
        sh_total = 200
        
        # Capas del lecho (de abajo hacia arriba)
        h_drenaje = 20
        h_grava = 40
        h_arena = sh_total - h_drenaje - h_grava
        
        # Capa de drenaje (tubos)
        draw.rectangle((sx, sy + sh_total - h_drenaje, sx + sw, sy + sh_total),
                       fill=c_drenaje, outline=c_muro, width=2)
        # Tubos de drenaje
        for i in range(5):
            x_tubo = sx + 60 + i * 120
            draw.ellipse((x_tubo - 8, sy + sh_total - h_drenaje + 2, 
                         x_tubo + 8, sy + sh_total - 2),
                        fill=(60, 60, 60), outline=(40, 40, 40))
        
        # Capa de grava
        draw.rectangle((sx, sy + sh_total - h_drenaje - h_grava, sx + sw, sy + sh_total - h_drenaje),
                       fill=c_grava, outline=c_muro, width=2)
        
        # Capa de arena (lodo)
        draw.rectangle((sx, sy, sx + sw, sy + h_arena),
                       fill=c_arena, outline=c_muro, width=2)
        
        # Etiquetas de capas
        draw.text((sx + sw + 20, sy + h_arena // 2), 'Capa de arena\n(lodo aplicado)',
                 font=f_texto, fill=c_texto, anchor='lm')
        draw.text((sx + sw + 20, sy + h_arena + h_grava // 2), 'Capa de grava\n(soporte)',
                 font=f_texto, fill=c_texto, anchor='lm')
        draw.text((sx + sw + 20, sy + h_arena + h_grava + h_drenaje // 2), 'Drenaje',
                 font=f_texto, fill=c_texto, anchor='lm')
        
        # Cotas seccion transversal
        dibujar_cota_vertical(draw, sy, sy + sh_total, sx - 20,
                              f'H total', f_cota)
        dibujar_cota_horizontal(draw, sx, sx + sw, sy + sh_total + 15,
                                f'B = {ancho:.1f} m', f_cota)
        
        # Titulo seccion
        draw.text((sx + sw // 2, sy + sh_total + 45),
                 'Seccion transversal tipica', font=f_subtitulo, fill=c_texto, anchor='mm')
        
        # Info tecnica
        x_info = sx + sw + 250
        draw.text((x_info, sy), 'Parametros de diseno:', font=f_subtitulo, fill=c_texto)
        draw.text((x_info, sy + 40), f'Area por bloque: {l["A_bloque_m2"]:.1f} m2', font=f_texto, fill=c_texto)
        draw.text((x_info, sy + 70), f'Area total: {l["A_total_m2"]:.1f} m2', font=f_texto, fill=c_texto)
        draw.text((x_info, sy + 100), f'Numero de bloques: {num_bloques}', font=f_texto, fill=c_texto)
        draw.text((x_info, sy + 130), f'Tiempo de secado: {l["t_secado_d"]:.0f} dias', font=f_texto, fill=c_texto)
        
        fig_path = os.path.join(output_dir, 'Esquema_Lecho_Secado.png')
        img.save(fig_path, 'PNG', dpi=(200, 200))
        return fig_path
    
    def generar_descripcion(self) -> str:
        """Genera subsection Dimensionamiento con teoria y calculos."""
        cfg = self.cfg
        l = self.datos
        filas_lodos = "\n".join(
            f"{item['origen']} & {item['por_linea_kg_d']:.2f} & {item['total_kg_d']:.2f} \\\\"
            for item in l['desglose_lodos']
        )
        
        return rf"""\subsection{{Dimensionamiento}}

El lecho de secado es una unidad de manejo de lodos que utiliza procesos fisicos de drenaje gravitacional y evaporacion para reducir el contenido de humedad de los lodos generados en el tratamiento. Este sistema es ampliamente utilizado en plantas de tratamiento de pequeno y mediano tamano debido a su bajo consumo energetico y simplicidad operativa.

\textbf{{Mecanismos de secado}}

El proceso de deshidratación de lodos en el lecho se realiza mediante dos mecanismos fundamentales que actúan simultáneamente:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item \textbf{{Drenaje gravitacional:}} Durante las primeras horas o días después de la aplicación del lodo, el agua libre drena por gravedad a través del medio filtrante (arena y grava) hacia el sistema de drenaje inferior. Este mecanismo remueve aproximadamente el 30--50\% del agua inicial del lodo.
    
    \item \textbf{{Evaporación:}} Una vez agotado el drenaje libre, la humedad restante se pierde por evaporación al ambiente, favorecida por la exposición superficial del lodo y el clima local. En condiciones tropicales de Galápagos (temperatura promedio 24°C, insolación elevada), la evaporación es el mecanismo dominante durante la mayor parte del ciclo de secado.
\end{{itemize}}

\textit{{Nota:}} La literatura técnica (Metcalf \& Eddy, 2014; OPS/CEPIS, 2005) reporta proporciones variables entre estos mecanismos según el clima local, con rangos típicos de 1/3 drenaje y 2/3 evaporación en climas cálidos y secos, hasta proporciones inversas en climas húmedos. Para el diseño del presente proyecto se considera el efecto combinado de ambos mecanismos sin asignar proporciones fijas, dado que el tiempo de secado adoptado ({l['t_secado_d']:.0f} días) se basa en criterios operativos conservadores de la región.

\textbf{{Estructura física del lecho}}

El lecho de secado consiste en una estructura impermeabilizada con capas estratificadas que permiten el drenaje y soporte del lodo:

\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item \textbf{{Capa de arena (superior):}} Espesor de {l['h_arena_m']:.2f} m. Constituye el medio de filtración principal donde se aplica el lodo. La arena fina retiene las partículas de lodo mientras permite el paso del agua. Debe tener granulometría uniforme (típicamente 0.25--1.0 mm) para maximizar la retención de sólidos sin colmatarse rápidamente.
    
    \item \textbf{{Capa de grava (intermedia):}} Espesor de {l['h_grava_m']:.2f} m. Proporciona soporte estructural a la capa de arena y distribuye uniformemente el agua drenada hacia el sistema de drenaje. La granulometría es mayor que la arena (típicamente 10--30 mm) para crear un medio permeable y estable.
    
    \item \textbf{{Sistema de drenaje (inferior):}} Compuesto por tuberías perforadas o zanjas de drenaje que recolectan el agua filtrada (liquiado) y la conducen a un punto de descarga o recolección. El gradiente de drenaje debe ser suficiente (mínimo 1--2\%) para evitar estancamiento y garantizar el flujo continuo.
\end{{itemize}}

\textbf{{Ciclo operativo y destino del lodo}}

El lecho opera mediante ciclos alternados de carga y descarga:

\begin{{enumerate}}[noitemsep,leftmargin=2em]
    \item \textbf{{Aplicación:}} El lodo húmedo se distribuye uniformemente sobre la superficie del lecho con un espesor de aproximadamente {l['h_lodo_m']:.2f} m.
    \item \textbf{{Secado:}} El lodo permanece en reposo durante {l['t_secado_d']:.0f} días, período durante el cual pierde humedad por drenaje y evaporación.
    \item \textbf{{Retiro:}} Una vez alcanzado el contenido de humedad objetivo (típicamente 40--60\% de sólidos), el lodo seco se retira manualmente o con equipos ligeros.
\end{{enumerate}}

El lodo seco resultante tiene dos destinos principales según su calidad y la normativa local:
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item \textbf{{Disposición en relleno sanitario:}} Es la opción más común para lodos de PTAR municipales. El lodo estabilizado y deshidratado cumple con los criterios de manejabilidad para disposición final controlada.
    \item \textbf{{Uso agrícola condicionado:}} Solo si el lodo cumple con requisitos de estabilización, ausencia de metales pesados y patógenos reducidos, según normativa sanitaria aplicable ( Ministerio de Salud, Ministerio del Ambiente). Requiere análisis periódicos y autorización expresa de la autoridad competente.
\end{{itemize}}

\textbf{{Parámetro de diseño: Carga superficial de sólidos ($\rho_S$)}}

El parámetro que controla el área requerida del lecho es la carga superficial de sólidos ($\rho_S$), definida como la masa de sólidos totales (SST) aplicada por unidad de área del lecho por año de operación. Este parámetro integra la producción de lodos con la capacidad de secado del sistema:

\begin{{equation}}
\rho_S = \frac{{M_{{SST}} \times 365}}{{A_{{total}}}}
\end{{equation}}
\captionequation{{Carga superficial de solidos -- parametro de control del area}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$\rho_S$] = Carga superficial de sólidos (kg SST/m²·año)
    \item[$M_{{SST}}$] = Masa diaria de sólidos a tratar (kg SST/d)
    \item[$A_{{total}}$] = Área superficial total del lecho (m²)
\end{{itemize}}

La carga superficial $\rho_S$ es crítica porque determina la frecuencia de aplicación de lodos y la eficiencia del secado. Valores elevados de $\rho_S$ implican mayor frecuencia de carga y mayor demanda de área. Los rangos típicos según Metcalf \& Eddy (2014) y OPS/CEPIS (2005) son {l['rango_rho_S_texto']}, dependiendo del tipo de lodo, clima y disponibilidad de área.

\textbf{{Criterios de diseno}}

\begin{{table}}[H]
\centering
\caption{{Parametros de diseno del lecho de secado}}
\small
\begin{{tabular}}{{lccl}}
\toprule
Parametro & Rango recomendado & Valor adoptado & Fuente \\
\midrule
Carga superficial de solidos & {l['rango_rho_S_texto']} & {l['rho_S_kgSST_m2_año']:.0f} kg/m$^2$·anio & Metcalf \& Eddy \cite{{metcalf2014}} \\
Concentracion de lodos & {l['rango_C_SST_texto']} & {l['C_SST_kg_m3']:.0f} kg/m$^3$ & OPS/CEPIS \cite{{ops2005}} \\
Tiempo de secado & {l['rango_t_secado_texto']} & {l['t_secado_d']:.0f} dias & OPS/CEPIS \\
Espesor de aplicacion & {l['rango_h_lodo_texto']} & {l['h_lodo_m']:.2f} m & Metcalf \& Eddy \\
Relacion Largo/Ancho & {l['rango_relacion_L_A_texto']} & {l['relacion_L_A']:.0f}:1 & Practica comun \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Produccion de lodos}}

La produccion de lodos se toma del balance encadenado del tren de tratamiento. Para los lodos anaerobios del UASB se emplea un factor de produccion de {cfg.lecho_factor_produccion_lodos:.2f} kg SST/kg DBO removida, mientras que las contribuciones de unidades posteriores se reportan segun el tren evaluado.

\textbf{{Balance de produccion de lodos:}}

\begin{{table}}[H]
\centering
\caption{{Produccion de lodos por linea y total planta}}
\begin{{tabular}}{{lcc}}
\toprule
\textbf{{Origen}} & \textbf{{Por linea (kg SST/d)}} & \textbf{{Total planta ({l['num_lineas']:.0f} lineas) (kg SST/d)}} \\
\midrule
{filas_lodos}
\midrule
\textbf{{Total}} & \textbf{{{l['lodos_total_kg_d_por_linea']:.2f}}} & \textbf{{{l['lodos_total_kg_d']:.2f}}} \\
\bottomrule
\end{{tabular}}
\end{{table}}

\textbf{{Ecuaciones de diseno}}

El volumen diario de lodo a tratar se determina mediante:

\begin{{equation}}
V_{{lodo}} = \frac{{M_{{SST}}}}{{C_{{SST}}}}
\end{{equation}}
\captionequation{{Volumen diario de lodo a tratar}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$V_{{lodo}}$] = Volumen diario de lodo (m$^3$/d)
    \item[$M_{{SST}}$] = Masa de solidos producidos TOTAL ({l['lodos_total_kg_d']:.2f} kg SST/d)
    \item[$C_{{SST}}$] = Concentracion de solidos ({l['C_SST_kg_m3']:.0f} kg/m$^3$)
\end{{itemize}}

\begin{{equation}}
V_{{lodo}} = \frac{{{l['lodos_total_kg_d']:.2f}}}{{{l['C_SST_kg_m3']:.0f}}} = {l['V_lodo_m3_d']:.3f} \text{{ m}}^3\text{{/d}}
\end{{equation}}

\textbf{{Dimensionamiento del area}}

El area requerida se calcula considerando el volumen de lodo, el tiempo de secado y el espesor de aplicacion:

\begin{{equation}}
A_{{total}} = \frac{{V_{{lodo}} \cdot t_s}}{{h_{{lodo}}}}
\end{{equation}}
\captionequation{{Area superficial total del lecho de secado}}

\textit{{Donde:}}
\begin{{itemize}}[noitemsep,leftmargin=2em]
    \item[$A_{{total}}$] = Area superficial total requerida (m$^2$)
    \item[$t_s$] = Tiempo de secado ({l['t_secado_d']:.0f} dias)
    \item[$h_{{lodo}}$] = Espesor de aplicacion ({l['h_lodo_m']:.2f} m)
    \item[$n_{{celdas}}$] = Numero de celdas ({l['n_celdas']:.0f}) (subdivision interna)
\end{{itemize}}

\begin{{equation}}
A_{{total}} = \frac{{{l['V_lodo_m3_d']:.3f} \times {l['t_secado_d']:.0f}}}{{{l['h_lodo_m']:.2f}}} = {l['A_total_m2']:.1f} \text{{ m}}^2
\end{{equation}}

\textbf{{Distribucion por tren de tratamiento}}

El area total se distribuye en bloques independientes, uno al final de cada tren de tratamiento:

\begin{{equation}}
A_{{bloque}} = \frac{{A_{{total}}}}{{n_{{lineas}}}} = \frac{{{l['A_total_m2']:.1f}}}{{{l['num_lineas']:.0f}}} = {l['A_bloque_m2']:.1f} \text{{ m}}^2 \text{{ por bloque}}
\end{{equation}}

\textbf{{Subdivision interna en celdas}}

Cada bloque se subdivide internamente en celdas para operacion por rotacion:

\begin{{equation}}
A_{{celda}} = \frac{{A_{{total}}}}{{n_{{celdas}}}} = \frac{{{l['A_total_m2']:.1f}}}{{{l['n_celdas']:.0f}}} = {l['A_celda_m2']:.1f} \text{{ m}}^2 \text{{ por celda}}
\end{{equation}}

Con una relacion largo/ancho de {l['relacion_L_A']:.0f}:1, las dimensiones de cada bloque son {l['largo_m']:.1f} m de largo por {l['ancho_m']:.1f} m de ancho."""

    def generar_verificacion(self) -> str:
        """Genera subsection Verificacion con carga superficial."""
        l = self.datos
        
        return rf"""\subsection{{Verificacion}}

\textbf{{Verificacion de carga superficial}}

La carga superficial de solidos se verifica mediante:

\begin{{equation}}
\rho_S = \frac{{M_{{SST}} \times 365}}{{A_{{total}}}} = \frac{{{l['lodos_total_kg_d']:.2f} \times 365}}{{{l['A_total_m2']:.1f}}} = {l['rho_S_kgSST_m2_año']:.1f} \text{{ kg SST/m}}^2\text{{·anio}}
\end{{equation}}

{l['texto_carga_solidos']}

\textbf{{Notas de operacion}}

{l['texto_operacion_lecho']}"""

    def generar_resultados(self) -> str:
        """Genera subsection Resultados con tabla y figura."""
        l = self.datos
        
        # Generar figura
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
\caption{{Lecho de secado de lodos: vista en planta de los bloques por linea de tratamiento y seccion transversal tipica mostrando capas de arena, grava y sistema de drenaje.}}
\label{{fig:lecho_secado}}
\end{{figure}}

"""
        else:
            figura_latex = ""
        
        return rf"""\subsection{{Resultados}}

\begingroup
\small
\begin{{longtable}}{{ll}}
\caption{{Resumen del dimensionamiento del lecho de secado}}\\
\toprule
Parametro & Valor \\
\midrule
\endfirsthead
\caption[]{{Resumen del dimensionamiento del lecho de secado (continuación)}}\\
\toprule
Parametro & Valor \\
\midrule
\endhead
\midrule
\multicolumn{{2}}{{r}}{{\textit{{Continúa en la siguiente página}}}} \\
\endfoot
\bottomrule
\endlastfoot
Area total requerida & {l['A_total_m2']:.1f} m$^2$ \\
Numero de bloques (uno por tren) & {l['num_lineas']:.0f} \\
Area por bloque & {l['A_bloque_m2']:.1f} m$^2$ \\
Dimensiones de cada bloque (L$\times$A) & {l['largo_m']:.1f} m $\times$ {l['ancho_m']:.1f} m \\
Numero total de celdas & {l['n_celdas']:.0f} \\
Tiempo de secado & {l['t_secado_d']:.0f} dias \\
Carga de solidos & {l['rho_S_kgSST_m2_año']:.1f} kg SST/m$^2$·anio \\
Produccion total de lodos & {l['lodos_total_kg_d']:.2f} kg SST/d \\
\end{{longtable}}
\endgroup

{figura_latex}El lecho de secado ha sido dimensionado para tratar {l['lodos_total_kg_d']:.2f} kg SST/d de lodos generados en el proceso de tratamiento, distribuidos en {l['num_lineas']:.0f} bloques independientes (uno por tren de tratamiento). Cada bloque opera con un ciclo de {l['t_secado_d']:.0f} dias de secado."""


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_dir)
    
    from ptar_dimensionamiento import ConfigDiseno, calcular_tren_A
    import subprocess
    
    print("=" * 60)
    print("TEST - GENERADOR MODULAR DE LECHO DE SECADO")
    print("=" * 60)
    
    cfg = ConfigDiseno()
    print(f"\n[1] Q_linea = {cfg.Q_linea_L_s} L/s")
    print(f"    num_lineas = {cfg.num_lineas}")
    
    # Usar el caso real del Tren A para evitar dimensiones de prueba inventadas.
    resultados_tren = calcular_tren_A(cfg)
    datos = resultados_tren['lecho_secado']
    
    print(f"[2] Dimensiones: {datos['largo_m']:.1f}m x {datos['ancho_m']:.1f}m, Area total={datos['A_total_m2']:.1f}m2")
    
    resultados_dir = os.path.join(base_dir, 'resultados', 'test_modular')
    figuras_dir = os.path.join(resultados_dir, 'figuras')
    os.makedirs(figuras_dir, exist_ok=True)
    
    gen = GeneradorLechoSecado(cfg, datos, ruta_figuras=figuras_dir)
    latex = gen.generar_completo()
    print(f"[3] LaTeX generado: {len(latex)} chars")
    
    tex_path = os.path.join(resultados_dir, 'lecho_secado_test.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex)
    
    doc_path = os.path.join(resultados_dir, 'lecho_secado_test_completo.tex')
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

\section{Lecho de Secado de Lodos}

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
        pdf_path = os.path.join(resultados_dir, 'lecho_secado_test_completo.pdf')
        if os.path.exists(pdf_path):
            print(f"    PDF generado: {pdf_path}")
    except Exception as e:
        print(f"    ERROR: {e}")
    
    print("=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
