#!/usr/bin/env python3
"""
PTAR LAYOUT GRAFICADOR - Módulo exclusivo para graficación de layouts
Puerto Baquerizo Moreno, Galápagos

Funciones para generar layouts visuales de plantas de tratamiento.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle
from typing import Tuple
import os

# Importar configuración
from ptar_config import (
    DIMENSIONES, COLORES, LECHO_LARGO, LECHO_ANCHO,
    SEP_UNIDADES, SEP_LINEAS, MARGEN, FONT_CONFIG, FIGSIZE
)

# Mapeo de nombres de unidades a nombres de display
NOMBRES_DISPLAY = {
    'Rejillas': 'Rejillas',
    'Desarenador': 'Desarenador',
    'UASB': 'UASB',
    'Filtro_Percolador': 'Filtro\nPercolador',
    'Sedimentador': 'Sedimentador\nSecundario',
    'Sedimentador_Secundario': 'Sedimentador\nSecundario',
    'Cloro': 'Desinfeccion\nCloro',
    'Desinfeccion': 'Desinfeccion',
    'Desinfeccion_Cloro': 'Desinfeccion\nCloro',
    'UV': 'UV',
    'Humedal_Vertical': 'Humedal\nVertical',
    'Humedal_Horizontal': 'Humedal\nHorizontal',
    'Lodos_Activados': 'Lodos\nActivados',
    'Reactor_Anaerobico': 'Reactor\nAnaerobico',
}

# Mapeo de unidades a números para layout tipo arquitectura
NUMEROS_UNIDADES = {
    'Rejillas': '1',
    'Desarenador': '2',
    'UASB': '3',
    'ABR_RAP': '3',
    'Filtro_Percolador': '4',
    'Sedimentador': '4',
    'Sedimentador_Secundario': '4',
    'Humedal_Vertical': '4',
    'BAF': '4',
    'Biofiltro': '4',
    'Desinfeccion': '5',
    'Cloro': '5',
    'Desinfeccion_Cloro': '5',
    'UV': '5',
    'Lecho de Secado': '6',
}

# Nombres completos para la leyenda
NOMBRES_LEYENDA = {
    '1': 'Rejillas',
    '2': 'Desarenador',
    '3': 'UASB / ABR',
    '4': 'Tratamiento Secundario',
    '5': 'Desinfección',
    '6': 'Lecho de Secado',
}


def get_unidad_altura(unidad: str, DIM: dict = None) -> float:
    """Obtiene la altura/ancho de una unidad"""
    dim_dict = DIM if DIM else DIMENSIONES
    props = dim_dict[unidad]
    if props['geom'] == 'circ':
        return props['diametro']
    else:
        return props['ancho']


def get_unidad_right_center(x: float, y: float, unidad: str, DIM: dict = None) -> Tuple[float, float]:
    """Obtiene el punto derecho central de una unidad (para salida)"""
    dim_dict = DIM if DIM else DIMENSIONES
    props = dim_dict[unidad]
    if props['geom'] == 'circ':
        diam = props['diametro']
        return (x + diam, y + diam/2)
    else:
        ancho = props['ancho']
        return (x + props['largo'], y + ancho/2)


def get_unidad_left_center(x: float, y: float, unidad: str, DIM: dict = None) -> Tuple[float, float]:
    """Obtiene el punto izquierdo central de una unidad (para entrada)"""
    dim_dict = DIM if DIM else DIMENSIONES
    props = dim_dict[unidad]
    if props['geom'] == 'circ':
        diam = props['diametro']
        return (x, y + diam/2)
    else:
        ancho = props['ancho']
        return (x, y + ancho/2)


def dibujar_unidad_layout(ax, x: float, y: float, unidad: str, color: str, font_scale: float = 1.0, DIM: dict = None, linea_idx: int = 0, total_lineas: int = 1, usar_numeros: bool = False):
    """Dibuja una unidad en el layout. Sin números internos (van arriba con línea guía)."""
    dim_dict = DIM if DIM else DIMENSIONES
    props = dim_dict[unidad]
    
    fontsize = FONT_CONFIG['unidad'] * font_scale
    
    if props['geom'] == 'circ':
        diam = props['diametro']
        radio = diam / 2
        circle = Circle((x + radio, y + radio), radio, 
                       facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        
        # Sin texto interno - los números van arriba con línea guía
        
        return diam, diam, f'Ø{diam:.1f}m'
    else:
        largo = props['largo']
        ancho = props['ancho']
        
        rect = Rectangle((x, y), largo, ancho, facecolor=color, 
                        edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        
        # Sin texto interno - los números van arriba con línea guía
        
        # Formato de dimensiones: Largo x Ancho
        return largo, ancho, f'{largo:.1f}m x {ancho:.1f}m'


def dibujar_flecha_flujo(ax, x1: float, y1: float, x2: float, y2: float, color='black'):
    """Dibuja una flecha de flujo entre dos puntos"""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
               arrowprops=dict(arrowstyle='->', color=color, lw=2,
                              connectionstyle='arc3,rad=0'))


def dibujar_flecha_lodos(ax, x1: float, y1: float, x2: float, y2: float):
    """Dibuja una flecha de lodos (roja punteada) entre dos puntos"""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
               arrowprops=dict(arrowstyle='->', color='darkred', lw=2.5,
                              connectionstyle='arc3,rad=0',
                              linestyle='--'))


def generar_caption_layout(unidades_presentes: list) -> str:
    """
    Genera automáticamente el texto de caption/descripción para el layout.
    Incluye la numeración de unidades y sus nombres completos.
    
    Args:
        unidades_presentes: Lista de unidades que aparecen en el layout
        
    Returns:
        str: Texto formateado para usar como caption en LaTeX
    """
    # Mapeo completo de nombres para el caption
    NOMBRES_COMPLETOS = {
        '1': 'Rejillas',
        '2': 'Desarenador', 
        '3': 'Reactor UASB (Reactor Anaerobio de Flujo Ascendente)',
        '4': 'Humedal Artificial de Flujo Vertical (HAFV)',
        '5': 'Cámara de Desinfección con Cloro',
        '6': 'Lecho de Secado de Lodos',
    }
    
    # Obtener números únicos presentes
    numeros_presentes = set()
    for unidad in unidades_presentes:
        num = NUMEROS_UNIDADES.get(unidad)
        if num:
            numeros_presentes.add(num)
    
    # Ordenar y construir lista
    items = []
    for num in sorted(numeros_presentes):
        nombre = NOMBRES_COMPLETOS.get(num, NOMBRES_LEYENDA.get(num, 'Unidad'))
        items.append(f"\\textbf{{{num}}}={nombre}")
    
    return "Distribución de unidades: " + "; ".join(items) + "."


def dibujar_numeros_arquitectura(ax, posiciones_unidades: dict, max_y: float):
    """
    Dibuja números en la parte superior con líneas guía dashed.
    Estilo arquitectura profesional - las líneas no llegan hasta las dimensiones.
    
    Args:
        ax: Eje de matplotlib
        posiciones_unidades: Dict {unidad: (x_centro, y_centro, ancho, alto)}
        max_y: Altura máxima del layout
    """
    y_numeros = max_y + 2.5  # Posición Y para los números (arriba)
    y_fin_linea = 2.0  # Donde terminan las líneas dashed (por encima de las dimensiones que están en -5)
    fontsize_num = 14
    
    for unidad, (x_c, y_c, ancho, alto) in posiciones_unidades.items():
        numero = NUMEROS_UNIDADES.get(unidad, '?')
        
        # Dibujar número arriba centrado
        ax.text(x_c, y_numeros, numero, ha='center', va='bottom',
               fontsize=fontsize_num, fontweight='bold', color='black')
        
        # Línea guía dashed desde el número hasta y_fin_linea (no llega a las dimensiones)
        ax.plot([x_c, x_c], [y_numeros - 0.5, y_fin_linea], 'k--', lw=1.5, alpha=0.6)

def dibujar_leyenda_numerada(ax, unidades_presentes: list, max_x: float, max_y: float):
    """
    Dibuja una leyenda con numeración tipo arquitectura en esquina superior derecha.
    
    Args:
        ax: Eje de matplotlib
        unidades_presentes: Lista de unidades que aparecen en el layout
        max_x: Ancho máximo del layout
        max_y: Altura máxima del layout
    """
    fontsize = 12
    line_height = 0.9
    box_width = 6.5
    margin_right = 2.0
    margin_top = 2.0
    
    # Obtener números únicos presentes
    numeros_presentes = set()
    for unidad in unidades_presentes:
        num = NUMEROS_UNIDADES.get(unidad)
        if num:
            numeros_presentes.add(num)
    
    numeros_ordenados = sorted(numeros_presentes)
    box_height = len(numeros_ordenados) * line_height + 1.0
    
    # Posicionar en esquina superior derecha (considerando margen)
    x_pos = max_x - box_width - margin_right
    y_pos = max_y - margin_top
    
    # Fondo de la leyenda
    legend_bg = Rectangle((x_pos, y_pos - box_height), box_width, box_height,
                          facecolor='white', edgecolor='black', linewidth=2,
                          alpha=0.98, zorder=100)
    ax.add_patch(legend_bg)
    
    # Título
    ax.text(x_pos + box_width/2, y_pos - 0.3, 'ÍNDICE', ha='center', va='top',
           fontsize=fontsize + 2, fontweight='bold', zorder=101)
    
    # Línea separadora
    ax.plot([x_pos + 0.4, x_pos + box_width - 0.4], [y_pos - 0.55, y_pos - 0.55], 
           'k-', linewidth=1.5, zorder=101)
    
    # Ordenar y dibujar entradas
    for i, num in enumerate(numeros_ordenados):
        y_text = y_pos - 0.9 - i * line_height
        nombre = NOMBRES_LEYENDA.get(num, 'Desconocido')
        
        # Círculo con número (más grande)
        circle = Circle((x_pos + 0.5, y_text), 0.25, facecolor='lightgray', 
                       edgecolor='black', linewidth=2, zorder=101)
        ax.add_patch(circle)
        ax.text(x_pos + 0.5, y_text, num, ha='center', va='center',
               fontsize=fontsize, fontweight='bold', zorder=102)
        
        # Nombre
        ax.text(x_pos + 1.0, y_text, nombre, ha='left', va='center',
               fontsize=fontsize, zorder=101)


def dibujar_flecha_lodos(ax, x1: float, y1: float, x2: float, y2: float):
    """Dibuja una flecha de lodos (roja punteada) entre dos puntos"""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
               arrowprops=dict(arrowstyle='->', color='darkred', lw=2.5,
                              connectionstyle='arc3,rad=0',
                              linestyle='--'))


def dibujar_lecho_compartido(ax, x: float, y: float, largo: float, ancho: float, font_scale: float = 1.0):
    """Dibuja el lecho de secado compartido con dimensiones calculadas"""
    fontsize = FONT_CONFIG['unidad']
    acot_fontsize = FONT_CONFIG['acotacion']
    
    offset_linea = 0.6
    offset_texto = 1.1
    offset_linea_v = 0.6  # Offset para línea vertical
    offset_texto_v = 1.1  # Offset para texto vertical
    
    rect = Rectangle((x, y), largo, ancho, 
                     facecolor=COLORES['manejo_lodos'], 
                     edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    
    ax.text(x + largo/2, y + ancho/2, 'Lecho de\nSecado', 
           ha='center', va='center', fontsize=fontsize, fontweight='bold')
    
    # Acotación horizontal (largo)
    ax.annotate('', xy=(x + largo, y - offset_linea), xytext=(x, y - offset_linea),
               arrowprops=dict(arrowstyle='<->', color='black', lw=1))
    ax.text(x + largo/2, y - offset_texto, f'{largo:.1f}m', ha='center', fontsize=acot_fontsize,
           color='black', fontweight='bold')
    
    # Acotación vertical (ancho) - a la derecha del lecho
    ax.annotate('', xy=(x + largo + offset_linea_v, y + ancho), xytext=(x + largo + offset_linea_v, y),
               arrowprops=dict(arrowstyle='<->', color='black', lw=1))
    ax.text(x + largo + offset_texto_v, y + ancho/2, f'{ancho:.1f}m', ha='left', va='center', 
           fontsize=acot_fontsize, color='black', fontweight='bold', rotation=90)
    
    return largo, ancho


def convertir_resultados_a_dimensiones(resultados: dict) -> dict:
    """
    Convierte los resultados del dimensionamiento al formato de DIMENSIONES.
    
    Args:
        resultados: Diccionario con resultados de cada unidad (de dimensionar_escogida.py)
    
    Returns:
        dict: Dimensiones en formato compatible con el layout
    """
    dim = {}
    
    # Mapeo de nombres de resultados a nombres de unidades en el layout
    mapeo = {
        'rejillas': 'Rejillas',
        'desarenador': 'Desarenador',
        'uasb': 'UASB',
        'filtro_percolador': 'Filtro_Percolador',
        'sedimentador_sec': 'Sedimentador',  # Clave única para sedimentador secundario
        'uv': 'UV',
        'cloro': 'Desinfeccion',
        'desinfeccion': 'Desinfeccion',
        'lecho_secado': None,  # Se maneja separado
        'humedal_vertical': 'Humedal_Vertical',
        'baf': 'BAF',
        'abr_rap': 'ABR_RAP',
        'bf_cmh': 'Biofiltro',  # Biofiltro carga mecanizada/hidráulica
    }
    
    for key_res, key_layout in mapeo.items():
        if key_res not in resultados or key_layout is None:
            continue
        
        res = resultados[key_res]
        
        if key_res == 'rejillas':
            dim[key_layout] = {
                'tipo': 'pretratamiento',
                'largo': res.get('largo_layout_m', 2.0),
                'ancho': res.get('ancho_layout_m', 0.9),
                'geom': 'rect'
            }
        elif key_res == 'desarenador':
            dim[key_layout] = {
                'tipo': 'pretratamiento',
                'largo': res.get('largo_layout_m', res.get('L_diseno_m', 3.0)),
                'ancho': res.get('ancho_layout_m', res.get('b_canal_m', 1.0)),
                'geom': 'rect'
            }
        elif key_res in ['uasb', 'egsb']:
            diam = res.get('diametro_layout_m', res.get('D_m', res.get('diametro_m', 5.0)))
            dim[key_layout] = {
                'tipo': 'tratamiento_primario',
                'diametro': diam,
                'geom': 'circ'
            }
        elif key_res == 'filtro_percolador':
            diam = res.get('diametro_layout_m', res.get('D_filtro_m', res.get('diametro_m', 5.0)))
            dim[key_layout] = {
                'tipo': 'tratamiento_secundario',
                'diametro': diam,
                'geom': 'circ'
            }
        elif key_res == 'sedimentador_sec':
            diam = res.get('diametro_layout_m', res.get('D_m', res.get('diametro_m', 5.0)))
            dim[key_layout] = {
                'tipo': 'tratamiento_secundario',
                'diametro': diam,
                'geom': 'circ'
            }
        elif key_res == 'uv':
            dim[key_layout] = {
                'tipo': 'terciario',
                'largo': res.get('largo_m', 3.0),
                'ancho': res.get('ancho_m', 1.0),
                'geom': 'rect'
            }
        elif key_res == 'desinfeccion':
            dim[key_layout] = {
                'tipo': 'terciario',
                'largo': res.get('largo_layout_m', res.get('largo_m', 8.0)),
                'ancho': res.get('ancho_layout_m', res.get('ancho_m', 2.0)),
                'geom': 'rect'
            }
        elif key_res == 'cloro':
            # Desinfeccion con cloro - usar dimensiones de layout (incluyen margen)
            dim[key_layout] = {
                'tipo': 'terciario',
                'largo': res.get('largo_layout_m', res.get('largo_m', 8.0)),
                'ancho': res.get('ancho_layout_m', res.get('ancho_m', 2.0)),
                'geom': 'rect'
            }
        elif key_res == 'humedal_vertical':
            # El humedal tiene 2 celdas en serie (una tras otra)
            # Usar dimensiones totales: largo = 29.1*2, ancho = 22.4
            largo = res.get('largo_total_m', res.get('largo_layout_m', 58.2))
            ancho = res.get('ancho_total_m', res.get('ancho_layout_m', 22.4))
            
            # Asegurar que largo sea la dimensión mayor (horizontal)
            if ancho > largo:
                largo, ancho = ancho, largo
            
            dim[key_layout] = {
                'tipo': 'tratamiento_secundario',
                'largo': largo,
                'ancho': ancho,
                'geom': 'rect'
            }
        elif key_res == 'baf':
            diam = res.get('diametro_layout_m', res.get('D_m', 4.0))
            dim[key_layout] = {
                'tipo': 'tratamiento_secundario',
                'diametro': diam,
                'geom': 'circ'
            }
        elif key_res == 'abr_rap':
            dim[key_layout] = {
                'tipo': 'tratamiento_primario',
                'largo': res.get('largo_layout_m', res.get('L_total_m', 8.0)),
                'ancho': res.get('ancho_layout_m', res.get('W_m', 3.0)),
                'geom': 'rect'
            }
        elif key_res == 'bf_cmh':
            diam = res.get('diametro_layout_m', res.get('D_bf_m', 4.0))
            dim[key_layout] = {
                'tipo': 'tratamiento_secundario',
                'diametro': diam,
                'geom': 'circ'
            }
    
    return dim


def generar_layout_con_resultados(tipo: str, unidades_linea: list, nombre_alt: str,
                                  resultados: dict, output_dir: str,
                                  caudal_L_s: float = None):
    """
    Genera layout usando las dimensiones reales calculadas.
    
    Args:
        tipo: Código de la alternativa (A, B, C, etc.)
        unidades_linea: Lista de unidades en cada línea
        nombre_alt: Nombre descriptivo de la alternativa
        resultados: Diccionario con resultados calculados del dimensionamiento
        output_dir: Directorio de salida
    
    Returns:
        Tuple con dimensiones (max_x, max_y)
    """
    # Convertir resultados al formato de dimensiones
    dim_reales = convertir_resultados_a_dimensiones(resultados)
    
    # Extraer dimensiones del lecho de secado calculadas - DEBEN existir
    if 'lecho_secado' not in resultados:
        raise KeyError("Falta 'lecho_secado' en los resultados del dimensionamiento")
    
    lecho_data = resultados['lecho_secado']
    
    if 'largo_layout_m' not in lecho_data:
        raise KeyError("Falta 'largo_layout_m' en resultados['lecho_secado']")
    if 'ancho_layout_m' not in lecho_data:
        raise KeyError("Falta 'ancho_layout_m' en resultados['lecho_secado']")
    
    lecho_largo = lecho_data['largo_layout_m']
    lecho_ancho = lecho_data['ancho_layout_m']
    lecho_dimensiones = (lecho_largo, lecho_ancho)
    
    # Llamar al generador de layout con dimensiones reales
    # El área se calcula automáticamente dentro de la función
    return generar_layout_2lineas(
        tipo=tipo,
        unidades_linea=unidades_linea,
        nombre_alt=nombre_alt,
        output_dir=output_dir,
        dimensiones_personalizadas=dim_reales,
        lecho_dimensiones=lecho_dimensiones,
        caudal_L_s=caudal_L_s
    )


def generar_layout_2lineas(tipo: str, unidades_linea: list, nombre_alt: str, 
                           output_dir: str, 
                           dimensiones_personalizadas: dict = None,
                           lecho_dimensiones: tuple = None,
                           caudal_L_s: float = None):
    """
    Genera layout con dos líneas paralelas, lecho compartido y flechas de flujo.
    
    Args:
        tipo: Código de la alternativa (A, B, C, etc.)
        unidades_linea: Lista de unidades en cada línea
        nombre_alt: Nombre descriptivo de la alternativa
        area_total: Área total en m²
        output_dir: Directorio de salida
        dimensiones_personalizadas: Diccionario opcional con dimensiones calculadas
    
    Returns:
        Tuple con dimensiones (max_x, max_y)
    """
    # Combinar dimensiones personalizadas con las del config (las personalizadas tienen prioridad)
    DIM = DIMENSIONES.copy()
    if dimensiones_personalizadas:
        DIM.update(dimensiones_personalizadas)
    
    fig, ax = plt.subplots(figsize=FIGSIZE)
    
    # Calcular altura máxima de las unidades para alinear centros
    max_altura_unidad = max(get_unidad_altura(u, DIM) for u in unidades_linea)
    
    # Calcular posiciones Y de los centros de cada línea
    centro_linea1 = MARGEN + max_altura_unidad / 2
    centro_linea2 = centro_linea1 + max_altura_unidad + SEP_LINEAS
    
    # Usar font_scale fijo
    font_scale = 1.0
    
    # ============ LÍNEA 1 (abajo) ============
    x_pos = MARGEN
    posiciones_linea1 = []
    
    for unidad in unidades_linea:
        color = COLORES[DIM[unidad]['tipo']]
        altura_unidad = get_unidad_altura(unidad, DIM)
        y_pos = centro_linea1 - altura_unidad / 2
        
        ancho, alto = dibujar_unidad_layout(ax, x_pos, y_pos, unidad, color, font_scale, DIM)
        posiciones_linea1.append((x_pos, y_pos, unidad, ancho, alto))
        x_pos += ancho + SEP_UNIDADES
    
    largo_linea = x_pos - MARGEN - SEP_UNIDADES
    
    # Dibujar flechas de flujo Línea 1
    for i in range(len(posiciones_linea1) - 1):
        x1, y1, unidad1, ancho1, alto1 = posiciones_linea1[i]
        x2, y2, unidad2, ancho2, alto2 = posiciones_linea1[i+1]
        
        start = get_unidad_right_center(x1, y1, unidad1, DIM)
        end = get_unidad_left_center(x2, y2, unidad2, DIM)
        dibujar_flecha_flujo(ax, start[0], start[1], end[0], end[1])
    
    # ============ LÍNEA 2 (arriba) ============
    x_pos = MARGEN
    posiciones_linea2 = []
    
    for unidad in unidades_linea:
        color = COLORES[DIM[unidad]['tipo']]
        altura_unidad = get_unidad_altura(unidad, DIM)
        y_pos = centro_linea2 - altura_unidad / 2
        
        ancho, alto = dibujar_unidad_layout(ax, x_pos, y_pos, unidad, color, font_scale, DIM)
        posiciones_linea2.append((x_pos, y_pos, unidad, ancho, alto))
        x_pos += ancho + SEP_UNIDADES
    
    # Dibujar flechas de flujo Línea 2
    for i in range(len(posiciones_linea2) - 1):
        x1, y1, unidad1, ancho1, alto1 = posiciones_linea2[i]
        x2, y2, unidad2, ancho2, alto2 = posiciones_linea2[i+1]
        
        start = get_unidad_right_center(x1, y1, unidad1, DIM)
        end = get_unidad_left_center(x2, y2, unidad2, DIM)
        dibujar_flecha_flujo(ax, start[0], start[1], end[0], end[1])
    
    # ============ LECHOS DE SECADO (UNO AL FINAL DE CADA LÍNEA) ============
    # Usar dimensiones calculadas - DEBEN venir en lecho_dimensiones
    if lecho_dimensiones is None:
        raise ValueError("Faltan dimensiones del lecho de secado. Asegúrate de pasar lecho_dimensiones desde los resultados del dimensionamiento.")
    
    lecho_largo, lecho_ancho = lecho_dimensiones
    
    if lecho_largo <= 0 or lecho_ancho <= 0:
        raise ValueError(f"Dimensiones del lecho inválidas: largo={lecho_largo}, ancho={lecho_ancho}. Deben ser > 0.")
    
    # Posición X: separado de la línea de tratamiento (no justo después del Cloro)
    # Separación mínima entre el último elemento y los lechos
    SEP_LECHOS = 1.5  # metros de separación mínima entre Cloro y Lechos
    x_lecho = MARGEN + largo_linea + SEP_UNIDADES + SEP_LECHOS
    
    fontsize = FONT_CONFIG['unidad']
    acot_fontsize = FONT_CONFIG['acotacion']
    offset_acot = 0.8
    
    # Calcular el centro vertical entre las dos líneas de tratamiento
    y_centro_lechos = (centro_linea1 + centro_linea2) / 2
    
    # Separación horizontal entre los dos lechos
    SEP_ENTRE_LECHOS = 1.0  # 1 metro de separación entre lechos
    
    # Dibujar Lecho 1 (alineado con Línea 1) - a la izquierda
    # Centrado verticalmente en y_centro_lechos
    y_lecho1 = y_centro_lechos - lecho_largo / 2
    x_lecho1 = x_lecho
    
    rect1 = Rectangle((x_lecho1, y_lecho1), lecho_ancho, lecho_largo, 
                     facecolor=COLORES['manejo_lodos'], 
                     edgecolor='black', linewidth=2)
    ax.add_patch(rect1)
    
    ax.text(x_lecho1 + lecho_ancho/2, y_lecho1 + lecho_largo/2, 
           'Lecho de\nSecado', 
           ha='center', va='center', fontsize=fontsize, fontweight='bold')
    
    # Acotación horizontal (ancho) - Lecho 1
    ax.annotate('', xy=(x_lecho1 + lecho_ancho, y_lecho1 - offset_acot), 
               xytext=(x_lecho1, y_lecho1 - offset_acot),
               arrowprops=dict(arrowstyle='<->', color='black', lw=1))
    ax.text(x_lecho1 + lecho_ancho/2, y_lecho1 - offset_acot - 0.4, 
           f'{lecho_ancho:.1f}m', ha='center', fontsize=acot_fontsize,
           color='black', fontweight='bold')
    
    # Dibujar Lecho 2 (alineado con Línea 2) - a la derecha del Lecho 1
    # Misma altura vertical (y_centro_lechos), desplazado horizontalmente
    y_lecho2 = y_centro_lechos - lecho_largo / 2
    x_lecho2 = x_lecho + lecho_ancho + SEP_ENTRE_LECHOS
    
    rect2 = Rectangle((x_lecho2, y_lecho2), lecho_ancho, lecho_largo, 
                     facecolor=COLORES['manejo_lodos'], 
                     edgecolor='black', linewidth=2)
    ax.add_patch(rect2)
    
    ax.text(x_lecho2 + lecho_ancho/2, y_lecho2 + lecho_largo/2, 
           'Lecho de\nSecado', 
           ha='center', va='center', fontsize=fontsize, fontweight='bold')
    
    # Acotación horizontal (ancho) - Lecho 2
    ax.annotate('', xy=(x_lecho2 + lecho_ancho, y_lecho2 - offset_acot), 
               xytext=(x_lecho2, y_lecho2 - offset_acot),
               arrowprops=dict(arrowstyle='<->', color='black', lw=1))
    ax.text(x_lecho2 + lecho_ancho/2, y_lecho2 - offset_acot - 0.4, 
           f'{lecho_ancho:.1f}m', ha='center', fontsize=acot_fontsize,
           color='black', fontweight='bold')
    
    # Acotación vertical (largo) compartida para ambos lechos - al lado derecho del Lecho 2
    ax.annotate('', xy=(x_lecho2 + lecho_ancho + offset_acot, y_lecho2 + lecho_largo), 
               xytext=(x_lecho2 + lecho_ancho + offset_acot, y_lecho2),
               arrowprops=dict(arrowstyle='<->', color='black', lw=1))
    ax.text(x_lecho2 + lecho_ancho + offset_acot + 0.4, y_lecho2 + lecho_largo/2, 
           f'{lecho_largo:.1f}m', ha='left', va='center', 
           fontsize=acot_fontsize, color='black', fontweight='bold', rotation=90)
    
    # NOTA: Las flechas desde Cloro a los lechos se han eliminado
    # Los lechos de secado son unidades independientes de manejo de lodos,
    # no reciben flujo hidráulico directo desde la línea de tratamiento
    
    # Para cálculo de dimensiones totales
    # Ahora hay dos lechos uno al lado del otro
    lecho_ancho_draw = (lecho_ancho * 2) + SEP_ENTRE_LECHOS  # ancho total de ambos lechos + separación
    lecho_alto_draw = lecho_largo
    
    # NOTA: Las flechas de lodos se han eliminado para simplificar el diagrama
    # El lecho de secado recibe lodos del UASB y Sedimentador (línea de lodos)
    
    # Calcular dimensiones del área
    max_x = x_lecho2 + lecho_ancho + MARGEN  # x_lecho2 es la posición del segundo lecho
    max_y = centro_linea2 + max_altura_unidad/2 + MARGEN + 1
    
    # Calcular área REAL del terreno ocupado (no hardcodeada)
    area_real_m2 = max_x * max_y
    
    # Flechas de entrada horizontales
    alto_rejillas = DIM['Rejillas']['ancho'] if 'Rejillas' in DIM else DIMENSIONES['Rejillas']['ancho']
    x_rejillas_l2 = posiciones_linea2[0][0]
    y_rejillas_l2 = posiciones_linea2[0][1]
    y_centro_rejillas_l2 = y_rejillas_l2 + alto_rejillas/2
    
    x_rejillas_l1 = posiciones_linea1[0][0]
    y_rejillas_l1 = posiciones_linea1[0][1]
    y_centro_rejillas_l1 = y_rejillas_l1 + alto_rejillas/2
    
    # Espacio para flecha
    espacio_flecha = 2.2
    x_texto = x_rejillas_l2 - espacio_flecha - 0.1
    x_inicio_flecha = x_texto + 0.1
    
    label_fontsize = FONT_CONFIG['entrada']
    
    # Usar caudal de configuración o fallar si no se proporciona
    if caudal_L_s is None:
        raise ValueError("Falta caudal_L_s. Debe proporcionarse el caudal por línea desde ConfigDiseno.")
    
    # Línea 2
    ax.text(x_texto, y_centro_rejillas_l2, f'Línea 2\n({caudal_L_s:.1f} L/s)', ha='right', va='center',
           fontsize=label_fontsize, fontweight='bold', color='blue',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.6, edgecolor='blue', pad=0.3))
    ax.annotate('', xy=(x_rejillas_l2, y_centro_rejillas_l2), 
               xytext=(x_inicio_flecha, y_centro_rejillas_l2),
               arrowprops=dict(arrowstyle='->', color='blue', lw=2.5))
    
    # Línea 1
    ax.text(x_texto, y_centro_rejillas_l1, f'Línea 1\n({caudal_L_s:.1f} L/s)', ha='right', va='center',
           fontsize=label_fontsize, fontweight='bold', color='blue',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.6, edgecolor='blue', pad=0.3))
    ax.annotate('', xy=(x_rejillas_l1, y_centro_rejillas_l1), 
               xytext=(x_inicio_flecha, y_centro_rejillas_l1),
               arrowprops=dict(arrowstyle='->', color='blue', lw=2.5))
    
    # Separación entre líneas - desde el inicio (x=0)
    text_fontsize = 11  # Tamaño aumentado para la etiqueta
    mid_x = MARGEN / 2  # Cerca del borde izquierdo
    ax.annotate('', xy=(mid_x, centro_linea2 - max_altura_unidad/2), 
               xytext=(mid_x, centro_linea1 + max_altura_unidad/2),
               arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
    ax.text(mid_x + 0.3, (centro_linea1 + centro_linea2)/2, 
           f'{SEP_LINEAS}m\nentre\nlineas', ha='left', va='center', fontsize=text_fontsize,
           color='purple', fontweight='bold')
    
    # Acotaciones generales
    dim_fontsize = FONT_CONFIG['acotacion']
    
    y_dim_horizontal = -3.5
    ax.annotate('', xy=(max_x, y_dim_horizontal), xytext=(0, y_dim_horizontal),
               arrowprops=dict(arrowstyle='<->', color='black', lw=2))
    ax.text(max_x/2, y_dim_horizontal - 0.6, f'{max_x:.1f} m', 
           ha='center', fontsize=dim_fontsize, color='black', fontweight='bold')
    
    x_dim_vertical = max_x + 1.0
    ax.annotate('', xy=(x_dim_vertical, max_y), xytext=(x_dim_vertical, 0),
               arrowprops=dict(arrowstyle='<->', color='black', lw=2))
    ax.text(x_dim_vertical + 0.8, max_y/2, f'{max_y:.1f} m', 
           ha='center', va='center', fontsize=dim_fontsize, color='black', fontweight='bold', rotation=90)
    
    # Leyenda
    leyenda_items = []
    # Dibujar leyenda numerada tipo arquitectura
    todas_unidades = list(unidades_linea) + ['Lecho de Secado']
    dibujar_leyenda_numerada(ax, todas_unidades, max_x, max_y)
    
    # Configuración del plot
    ax.set_xlim(-5, max_x + 2)
    ax.set_ylim(-5, max_y + 2)
    ax.set_aspect('equal')
    ax.set_xlabel('Distancia (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Distancia (m)', fontsize=12, fontweight='bold')
    ax.set_title(f'{tipo}: {nombre_alt} — Área Total: {area_real_m2:,.0f} m²', 
                fontsize=FONT_CONFIG['titulo'], fontweight='bold', pad=15)
    
    # Grid y estilo
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('white')
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Guardar
    fig_path = os.path.join(output_dir, f'Layout_{tipo}_2lineas.png')
    fig.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return max_x, max_y


def generar_layout(
    tren_id: str,
    unidades: list,
    resultados: dict,
    output_dir: str,
    num_lineas: int = 2,
    incluir_lecho_secado: bool = True,
    caudal_L_s: float = None,
    nombre_tren: str = None
) -> dict:
    """
    Genera layout generalizado para cualquier tren de tratamiento.
    
    Función unificada que genera layouts para cualquier número de líneas paralelas
    (1, 2, 3, etc.) con los parámetros de separación correctos:
    - Separación entre unidades: 2.1m
    - Separación entre líneas: 3.0m
    - Margen perimetral: 3.0m
    
    Args:
        tren_id: Identificador único del tren (ej: "C", "piloto", "custom_1")
        unidades: Lista de claves de unidades en orden (ej: ["rejillas", "desarenador", "uasb", ...])
        resultados: Diccionario con resultados del dimensionamiento por unidad
        output_dir: Directorio de salida para la figura
        num_lineas: Número de líneas paralelas (1, 2, 3, ...)
        incluir_lecho_secado: Si True, incluye lechos de secado al final
        caudal_L_s: Caudal por línea en L/s (opcional, para etiquetas)
        nombre_tren: Nombre descriptivo del tren (opcional)
    
    Returns:
        dict: {
            'fig_path': str, ruta de la figura generada
            'ancho_total_m': float, ancho total del layout en metros
            'largo_total_m': float, largo total del layout en metros
            'area_layout_m2': float, área envolvente del layout
            'unidades_dibujadas': list, lista de unidades efectivamente dibujadas
        }
    """
    # Convertir resultados a formato de dimensiones
    dim_reales = convertir_resultados_a_dimensiones(resultados)
    
    # Mapear nombres de unidades de entrada a nombres del layout
    mapeo_nombres = {
        'rejillas': 'Rejillas',
        'desarenador': 'Desarenador',
        'uasb': 'UASB',
        'filtro_percolador': 'Filtro_Percolador',
        'sedimentador_sec': 'Sedimentador',
        'cloro': 'Desinfeccion',
        'desinfeccion': 'Desinfeccion',
        'uv': 'UV',
        'humedal_vertical': 'Humedal_Vertical',
        'baf': 'BAF',
        'abr_rap': 'ABR_RAP',
        'bf_cmh': 'Biofiltro',
    }
    
    # Construir lista de unidades en formato del layout
    unidades_layout = []
    for u in unidades:
        nombre_layout = mapeo_nombres.get(u)
        if nombre_layout and nombre_layout in dim_reales:
            unidades_layout.append(nombre_layout)
    
    if not unidades_layout:
        raise ValueError(f"No se pudieron mapear unidades válidas para el tren {tren_id}")
    
    # Extraer dimensiones del lecho de secado
    lecho_dimensiones = None
    if incluir_lecho_secado:
        if 'lecho_secado' in resultados:
            lecho_data = resultados['lecho_secado']
            lecho_largo = lecho_data.get('largo_layout_m', lecho_data.get('largo_m', 6.0))
            lecho_ancho = lecho_data.get('ancho_layout_m', lecho_data.get('ancho_m', 5.0))
            lecho_dimensiones = (lecho_largo, lecho_ancho)
        else:
            lecho_dimensiones = (LECHO_LARGO, LECHO_ANCHO)
    
    nombre_display = nombre_tren or f"Tren {tren_id}"
    
    # === INICIO DEL DIBUJO GENERALIZADO ===
    DIM = DIMENSIONES.copy()
    if dim_reales:
        DIM.update(dim_reales)
    
    # Calcular dimensiones para determinar tamaño de figura
    max_altura_unidad = max(get_unidad_altura(u, DIM) for u in unidades_layout)
    ancho_linea = sum(get_unidad_altura(u, DIM) if DIM[u]['geom'] == 'circ' else DIM[u].get('largo', 5.0) for u in unidades_layout)
    ancho_linea += SEP_UNIDADES * (len(unidades_layout) - 1)
    
    # Dimensiones totales del layout
    alto_total = num_lineas * max_altura_unidad + (num_lineas - 1) * SEP_LINEAS + 2 * MARGEN
    ancho_total = ancho_linea + 2 * MARGEN
    
    # Ajustar tamaño de figura (escala automática)
    fig_width = max(16, min(32, ancho_total * 0.4 + 6))
    fig_height = max(10, min(24, alto_total * 0.5 + 4))
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # Calcular posiciones Y de los centros de cada línea
    posiciones_lineas_y = []
    for i in range(num_lineas):
        y_centro = MARGEN + max_altura_unidad/2 + i * (max_altura_unidad + SEP_LINEAS)
        posiciones_lineas_y.append(y_centro)
    
    # Dibujar cada línea
    todas_posiciones = []  # Lista de listas, una por línea
    posiciones_unidades_dict = {}  # Para números arquitectura: {unidad: (x_c, y_c, ancho, alto)}
    
    for linea_idx in range(num_lineas):
        y_centro = posiciones_lineas_y[linea_idx]
        x_pos = MARGEN
        posiciones_esta_linea = []
        
        # Dibujar unidades (sin números internos - van arriba con línea guía)
        for idx, unidad in enumerate(unidades_layout):
            color = COLORES[DIM[unidad]['tipo']]
            altura_unidad = get_unidad_altura(unidad, DIM)
            y_pos = y_centro - altura_unidad / 2
            
            ancho, alto, dim_texto = dibujar_unidad_layout(ax, x_pos, y_pos, unidad, color, 1.0, DIM, linea_idx, num_lineas)
            posiciones_esta_linea.append((x_pos, y_pos, unidad, ancho, alto, dim_texto))
            
            # Guardar posición central para números arquitectura (solo primera línea)
            if linea_idx == 0:
                x_c = x_pos + ancho / 2
                y_c = y_pos + alto / 2
                posiciones_unidades_dict[unidad] = (x_c, y_c, ancho, alto)
            
            x_pos += ancho + SEP_UNIDADES
        
        todas_posiciones.append(posiciones_esta_linea)
        
        # Dibujar flechas de flujo en esta línea
        for i in range(len(posiciones_esta_linea) - 1):
            x1, y1, unidad1, ancho1, alto1, _ = posiciones_esta_linea[i]
            x2, y2, unidad2, ancho2, alto2, _ = posiciones_esta_linea[i+1]
            start = get_unidad_right_center(x1, y1, unidad1, DIM)
            end = get_unidad_left_center(x2, y2, unidad2, DIM)
            dibujar_flecha_flujo(ax, start[0], start[1], end[0], end[1])
    
    largo_linea = x_pos - MARGEN - SEP_UNIDADES
    
    # Dibujar lechos de secado (uno al final de cada línea)
    SEP_LECHOS = 2.5  # Separación entre última unidad y lechos
    x_inicio_lecho = MARGEN + largo_linea + SEP_UNIDADES + SEP_LECHOS
    
    if incluir_lecho_secado and lecho_dimensiones:
        lecho_largo, lecho_ancho = lecho_dimensiones
        
        # Calcular posición X única para todos los lechos (alineados verticalmente)
        x_lecho = x_inicio_lecho
        
        for linea_idx in range(num_lineas):
            y_centro = posiciones_lineas_y[linea_idx]
            y_lecho = y_centro - lecho_largo / 2
            
            rect = Rectangle((x_lecho, y_lecho), lecho_ancho, lecho_largo,
                             facecolor=COLORES['manejo_lodos'],
                             edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            
            # Guardar posición del lecho para número arquitectura (solo primera línea)
            if linea_idx == 0:
                x_c_lecho = x_lecho + lecho_ancho / 2
                y_c_lecho = y_lecho + lecho_largo / 2
                posiciones_unidades_dict['Lecho de Secado'] = (x_c_lecho, y_c_lecho, lecho_ancho, lecho_largo)
            
            # Acotación vertical del lecho (solo en la última línea) - a la derecha
            if linea_idx == num_lineas - 1:
                # Línea vertical de dimensión
                ax.annotate('', xy=(x_lecho + lecho_ancho + 1.0, y_lecho + lecho_largo),
                           xytext=(x_lecho + lecho_ancho + 1.0, y_lecho),
                           arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
                # Texto de dimensión vertical
                ax.text(x_lecho + lecho_ancho + 1.8, y_lecho + lecho_largo/2,
                       f'{lecho_largo:.1f}m', ha='left', va='center', fontsize=FONT_CONFIG['acotacion'],
                       color='black', fontweight='bold', rotation=90)
        
        max_x_layout = x_lecho + lecho_ancho + MARGEN
    else:
        max_x_layout = x_pos + MARGEN
    
    max_y_layout = posiciones_lineas_y[-1] + max_altura_unidad/2 + MARGEN
    
    acot_fontsize = FONT_CONFIG['acotacion']
    
    # Flechas de entrada para cada línea
    if caudal_L_s:
        for linea_idx in range(num_lineas):
            x_inicio = todas_posiciones[linea_idx][0][0]
            y_inicio = todas_posiciones[linea_idx][0][1]
            alto_primera = todas_posiciones[linea_idx][0][4]
            y_centro = y_inicio + alto_primera/2
            
            espacio_entrada = 3.5
            ax.text(x_inicio - espacio_entrada - 0.2, y_centro,
                   f'Línea {linea_idx + 1}\n({caudal_L_s:.1f} L/s)',
                   ha='right', va='center', fontsize=FONT_CONFIG['entrada'],
                   fontweight='bold', color='blue',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.6, edgecolor='blue', pad=0.3))
            ax.annotate('', xy=(x_inicio, y_centro),
                       xytext=(x_inicio - espacio_entrada + 0.5, y_centro),
                       arrowprops=dict(arrowstyle='->', color='blue', lw=2.5))
    
    # Indicación de separación entre líneas (solo si hay más de 1)
    if num_lineas > 1:
        mid_x = MARGEN / 2
        # Usar primera y segunda línea para mostrar separación
        y_linea_inferior = posiciones_lineas_y[0] + max_altura_unidad/2
        y_linea_superior = posiciones_lineas_y[1] - max_altura_unidad/2
        ax.annotate('', xy=(mid_x, y_linea_superior),
                   xytext=(mid_x, y_linea_inferior),
                   arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
        ax.text(mid_x + 0.5, (y_linea_inferior + y_linea_superior)/2,
               f'{SEP_LINEAS}m\nentre\nlineas',
               ha='left', va='center', fontsize=9, color='purple', fontweight='bold')
    
    # === ACOTACIONES HORIZONTALES ALINEADAS EN PARALELO ===
    # Todas las dimensiones horizontales en la misma línea, paralelas a la general
    y_acot_unidades = -5.0  # Nivel único para todas las acotaciones de unidades
    
    # Lista de todas las unidades incluyendo lecho de secado
    todas_unidades_con_lecho = list(unidades_layout)
    if incluir_lecho_secado:
        todas_unidades_con_lecho.append('Lecho de Secado')
    
    # NOTA: La leyenda se omite del layout y se incluye en el caption de LaTeX
    
    for unidad in todas_unidades_con_lecho:
        # Calcular posición X centrada en la unidad
        x_centros = []
        ancho_unidad = None
        dim_horizontal = None
        
        if unidad == 'Lecho de Secado':
            # Todos los lechos están alineados en la misma X (uno tras otro verticalmente)
            x_centros.append(x_inicio_lecho + lecho_ancho/2)
            ancho_unidad = lecho_ancho
            dim_horizontal = f'{lecho_ancho:.1f}m'
        else:
            for linea_idx in range(num_lineas):
                for pos in todas_posiciones[linea_idx]:
                    if pos[2] == unidad:
                        x_centros.append(pos[0] + pos[3]/2)
                        if ancho_unidad is None:
                            ancho_unidad = pos[3]
                            dim_texto = pos[5]
                            if 'Ø' in dim_texto:
                                dim_horizontal = dim_texto
                            elif 'x' in dim_texto:
                                dim_horizontal = dim_texto.split('x')[0].strip()
                            else:
                                dim_horizontal = dim_texto
        
        if x_centros and ancho_unidad and dim_horizontal:
            x_centro_unidad = sum(x_centros) / len(x_centros)
            
            # Dibujar línea de dimensión horizontal (todas al mismo nivel)
            ax.annotate('', xy=(x_centro_unidad + ancho_unidad/2, y_acot_unidades),
                       xytext=(x_centro_unidad - ancho_unidad/2, y_acot_unidades),
                       arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
            
            # Texto ARRIBA de la línea
            ax.text(x_centro_unidad, y_acot_unidades + 0.8, dim_horizontal,
                   ha='center', va='bottom', fontsize=acot_fontsize,
                   fontweight='bold', color='black')
    
    # Acotación horizontal total (más abajo, separada de las unidades)
    y_dim_horizontal = y_acot_unidades - 4.5  # Más separación
    ax.annotate('', xy=(max_x_layout, y_dim_horizontal), xytext=(0, y_dim_horizontal),
               arrowprops=dict(arrowstyle='<->', color='black', lw=2))
    ax.text(max_x_layout/2, y_dim_horizontal - 1.5, f'{max_x_layout:.1f} m',
           ha='center', fontsize=acot_fontsize + 1, color='black', fontweight='bold')
    
    # Acotación vertical total (a la derecha)
    x_dim_vertical = max_x_layout + 2.5
    ax.annotate('', xy=(x_dim_vertical, max_y_layout), xytext=(x_dim_vertical, 0),
               arrowprops=dict(arrowstyle='<->', color='black', lw=2))
    ax.text(x_dim_vertical + 1.0, max_y_layout/2, f'{max_y_layout:.1f} m',
           ha='center', va='center', fontsize=acot_fontsize + 1, color='black', fontweight='bold', rotation=90)
    
    max_x_con_acot = max_x_layout + 5
    
    # Dibujar números arquitectura en la parte superior con líneas guía
    if posiciones_unidades_dict:
        dibujar_numeros_arquitectura(ax, posiciones_unidades_dict, max_y_layout)
    
    # Leyenda de colores (tipo de tratamiento) - esquina superior izquierda
    leyenda_items = []
    for tipo_nombre, color in COLORES.items():
        if any(DIM[u]['tipo'] == tipo_nombre for u in unidades_layout) or tipo_nombre == 'manejo_lodos':
            label = tipo_nombre.replace('_', ' ').title()
            leyenda_items.append(mpatches.Patch(color=color, label=label))
    
    legend_fontsize = FONT_CONFIG['leyenda']
    # Posicionar leyenda más arriba para que no tape los números
    ax.legend(handles=leyenda_items, loc='upper left', fontsize=legend_fontsize, 
             framealpha=0.9, edgecolor='gray', bbox_to_anchor=(0.02, 1.06))
    
    # Configuración final
    ax.set_xlim(-6, max_x_con_acot)
    ax.set_ylim(-11, max_y_layout + 8)  # Extender más para los números arriba
    ax.set_aspect('equal')
    ax.set_xlabel('Distancia (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Distancia (m)', fontsize=12, fontweight='bold')
    ax.set_title(f'Distribución de Tratamiento (Área = {max_x_layout * max_y_layout:,.0f} m²)',
                fontsize=FONT_CONFIG['titulo'], fontweight='bold', pad=15)
    
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('white')
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Guardar figura
    sufijo_lineas = "linea" if num_lineas == 1 else "lineas"
    fig_path = os.path.join(output_dir, f'Layout_{tren_id}_{num_lineas}{sufijo_lineas}.png')
    fig.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # Generar caption automático para LaTeX
    caption = generar_caption_layout(todas_unidades_con_lecho)
    
    return {
        'fig_path': fig_path,
        'ancho_total_m': round(max_x_layout, 1),
        'largo_total_m': round(max_y_layout, 1),
        'area_layout_m2': round(max_x_layout * max_y_layout, 0),
        'unidades_dibujadas': unidades_layout,
        'caption': caption
    }


def generar_esquema_uasb(resultados_uasb: dict, output_dir: str = "resultados") -> str:
    """
    Genera un esquema técnico del reactor UASB con proporciones verticales.
    Basado en esquema de referencia con ancho fijo y altura proporcional.
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, Polygon, Circle, FancyArrowPatch, Rectangle
    import numpy as np
    
    # Extraer valores
    D = resultados_uasb.get('D_m', 7.3)
    H_total = resultados_uasb.get('H_total_construccion_m', 5.5)
    H_reaccion = resultados_uasb.get('H_zona_reaccion_m', 3.0)
    H_GLS = resultados_uasb.get('H_GLS_m', 1.0)
    H_distribucion = resultados_uasb.get('H_distribucion_m', 0.3)
    H_sed = resultados_uasb.get('H_sed_m', 1.5)
    H_bordo = resultados_uasb.get('H_bordo_libre_m', 0.5)
    
    v_up = resultados_uasb.get('v_up_m_h', 0.43)
    TRH = resultados_uasb.get('TRH_h', 7.0)
    biogas = resultados_uasb.get('biogaz_m3_d', 48.9)
    Q_L_s = resultados_uasb.get('Q_m3_h', 18.0) * 1000 / 3600
    n_puntos = resultados_uasb.get('num_puntos_distribucion', 17)
    
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
    
    h_lecho = h_reac * 0.4  # 40% lecho granular
    h_manto = h_reac * 0.6  # 60% manto expandido
    
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
    
    # Parámetros del GLS
    angulo_gls = 52  # grados - valor típico dentro del rango 45-60°
    rad = np.radians(angulo_gls)
    traslape = 0.15  # 15 cm de traslape
    espesor_placa = 0.06  # espesor visual de la placa
    
    # Longitud horizontal de la placa desde la pared
    dx = (h_gls - 0.1) / np.tan(rad)
    
    # Placa izquierda (triángulo que sobresale desde la pared)
    x_placa_izq_base = x_izq + 0.1
    x_placa_izq_punta = x_placa_izq_base + dx
    y_placa_izq_abajo = y_gls_bottom + 0.05
    y_placa_izq_arriba = y_gls_bottom + h_gls - 0.05
    
    # Dibujar placa izquierda más delgada y angulada
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
                  f'{H_reaccion * 0.4:.1f} m')
    
    # Manto de lodos
    draw_dim_line(y_manto_bottom, y_manto_bottom + h_manto, x_dim_izq,
                  f'{H_reaccion * 0.6:.1f} m')
    
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
    fig_path = os.path.join(output_dir, 'Esquema_UASB.png')
    fig.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white', 
                pad_inches=0.2)
    plt.close()
    
    return fig_path


def generar_esquema_filtro_percolador(resultados_fp: dict, output_dir: str = "resultados") -> str:
    """
    Genera un esquema técnico del filtro percolador en sección vertical.
    Muestra distribuidor superior, medio filtrante, underdrain, ventilación
    y sentido general de flujo de agua/aire.
    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
    import numpy as np

    D = resultados_fp.get('D_filtro_m', 6.2)
    H_total = resultados_fp.get('H_total_m', 4.5)
    H_medio = resultados_fp.get('D_medio_m', 3.5)
    H_distribucion = resultados_fp.get('H_distribucion_m', 0.2)
    H_underdrain = resultados_fp.get('H_underdrain_m', 0.5)
    H_bordo = resultados_fp.get('H_bordo_libre_m', 0.3)
    R = resultados_fp.get('R_recirculacion', 1.5)
    qA = resultados_fp.get('Q_A_real_m3_m2_h', 1.5)
    qA_min = resultados_fp.get('qA_min_m3_m2_h', 0.6)
    qA_max = resultados_fp.get('Q_A_max_m3_m2_h', 3.8)
    Se = resultados_fp.get('DBO_salida_Germain_mg_L', 58.0)
    cumple_Se = resultados_fp.get('se_cumple_objetivo_Germain', False)
    S0 = resultados_fp.get('DBO_entrada_mg_L', 73.0)
    num_brazos = resultados_fp.get('num_brazos', 2)
    Q_brazo = resultados_fp.get('Q_por_brazo_m3_h', 27.0)
    Q_ap_total = resultados_fp.get('Q_ap_m3_h', Q_brazo * num_brazos)
    Q_underdrain = resultados_fp.get('Q_underdrain_diseno_m3_h', Q_ap_total * 2)
    Q_canal = resultados_fp.get('Q_canal_capacidad_m3_h', 0.0)
    llenado_canal = resultados_fp.get('llenado_canal_pct', 0.0)
    pendiente_underdrain = resultados_fp.get('pendiente_underdrain_pct', 1.0)
    area_vent = resultados_fp.get('area_ventilacion_requerida_m2', 0.3)
    num_aperturas = resultados_fp.get('num_aperturas_ventilacion', 6)

    ancho = 6.0
    altura_total = 8.5
    escala = altura_total / max(H_total, 0.1)

    x_centro = 6.0
    y_base = 1.0
    x_izq = x_centro - ancho / 2
    x_der = x_centro + ancho / 2

    h_bordo = H_bordo * escala
    h_dist = H_distribucion * escala
    h_medio = H_medio * escala
    h_under = H_underdrain * escala

    y_under = y_base
    y_medio = y_under + h_under
    y_dist = y_medio + h_medio
    y_top = y_dist + h_dist + h_bordo

    fig, ax = plt.subplots(figsize=(10, 11))

    c_medio = '#C9B28C'
    c_agua = '#DCEEF8'
    c_under = '#D5D5D5'
    c_tanque = '#FFFFFF'
    c_header = '#EAF4E2'
    c_air = '#7FB3D5'
    c_flow = '#2E7D32'
    c_recir = '#9C27B0'

    tanque = FancyBboxPatch(
        (x_izq, y_base), ancho, y_top - y_base,
        boxstyle="round,pad=0.12",
        facecolor=c_tanque, edgecolor='#555555', linewidth=2
    )
    ax.add_patch(tanque)

    underdrain = Rectangle(
        (x_izq + 0.1, y_under), ancho - 0.2, h_under,
        facecolor=c_under, edgecolor='#777777', linewidth=1.2
    )
    ax.add_patch(underdrain)

    # Rejilla de soporte del medio sobre el underdrain
    ax.plot([x_izq + 0.1, x_der - 0.1], [y_medio, y_medio], color='#8D8D8D', linewidth=1.2)
    for x_sup in np.linspace(x_izq + 0.35, x_der - 0.35, 10):
        ax.add_patch(Rectangle((x_sup - 0.10, y_medio - 0.03), 0.20, 0.03,
                               facecolor='#B0BEC5', edgecolor='#78909C', linewidth=0.4))

    # Canal central colector dentro del underdrain
    canal_ancho = ancho * 0.24
    canal_alto = h_under * 0.42
    canal_x = x_centro - canal_ancho / 2
    canal_y = y_under + 0.06
    y_canal_ref = canal_y + canal_alto * 0.68
    y_canal_desc = canal_y + canal_alto * 0.56

    medio = Rectangle(
        (x_izq + 0.1, y_medio), ancho - 0.2, h_medio,
        facecolor=c_medio, edgecolor='none', alpha=0.95
    )
    ax.add_patch(medio)
    for x_flow in np.linspace(x_izq + 1.1, x_der - 1.1, 5):
        ax.annotate(
            '', xy=(x_flow, y_medio + h_medio * 0.24),
            xytext=(x_flow, y_medio + h_medio * 0.82),
            arrowprops=dict(arrowstyle='-|>', color='#2E7D32', lw=2.4, mutation_scale=16, alpha=0.78)
        )

    agua_sup = Rectangle(
        (x_izq + 0.1, y_dist), ancho - 0.2, h_dist,
        facecolor=c_agua, edgecolor='none', alpha=0.85
    )
    ax.add_patch(agua_sup)

    camara_superior = Rectangle(
        (x_izq + 0.1, y_dist + h_dist), ancho - 0.2, h_bordo,
        facecolor=c_header, edgecolor='none', alpha=0.9
    )
    ax.add_patch(camara_superior)

    np.random.seed(24)
    for _ in range(80):
        cx = x_centro + np.random.uniform(-ancho / 2 + 0.35, ancho / 2 - 0.35)
        cy = y_medio + np.random.uniform(0.08, max(h_medio - 0.08, 0.1))
        r = np.random.uniform(0.05, 0.11)
        color = '#B8946F' if np.random.rand() > 0.25 else '#D8C3A5'
        ax.add_patch(Circle((cx, cy), r, facecolor=color, edgecolor='#8D6E63', alpha=0.85))

    x_col = x_centro
    y_brazo = y_dist + h_dist * 0.72
    ax.plot([x_col, x_col], [y_top + 0.45, y_brazo - 0.15], color='#444444', linewidth=2.2)
    ax.add_patch(Circle((x_col, y_brazo), 0.16, facecolor='#B0BEC5', edgecolor='#455A64', linewidth=1.2))

    brazo_largo = ancho * 0.36
    ax.plot([x_col - brazo_largo, x_col + brazo_largo], [y_brazo, y_brazo], color='#616161', linewidth=3)
    if num_brazos >= 4:
        ax.plot([x_col, x_col], [y_brazo - brazo_largo * 0.55, y_brazo + brazo_largo * 0.55], color='#616161', linewidth=2.2)

    for side in (-1, 1):
        for frac in (0.25, 0.55, 0.85):
            x_noz = x_col + side * brazo_largo * frac
            ax.add_patch(Circle((x_noz, y_brazo), 0.038, facecolor='#455A64', edgecolor='white', linewidth=0.5))
            ax.plot([x_noz, x_noz], [y_brazo, y_brazo - 0.06], color='#455A64', linewidth=1.0)
            ax.annotate(
                '', xy=(x_noz, y_brazo - 0.55), xytext=(x_noz, y_brazo - 0.06),
                arrowprops=dict(arrowstyle='->', color=c_flow, lw=1.8)
            )

    ax.plot([x_izq - 1.4, x_col], [y_top + 0.45, y_top + 0.45], color='#444444', linewidth=2)
    ax.annotate('', xy=(x_izq - 0.2, y_top + 0.45), xytext=(x_izq - 1.2, y_top + 0.45),
                arrowprops=dict(arrowstyle='->', color=c_recir, lw=2.5))
    ax.text(x_izq - 1.45, y_top + 0.66, f'Afluente + recirculación\nQap = {Q_ap_total:.1f} m³/h\nR = {R:.1f}',
            ha='left', va='bottom', fontsize=8.6, color=c_recir, fontweight='bold')

    for x_air in np.linspace(x_izq + 0.55, x_der - 0.55, min(max(num_aperturas, 3), 6)):
        ax.add_patch(Rectangle((x_air - 0.16, y_under + 0.05), 0.32, 0.12,
                               facecolor='#90CAF9', edgecolor='#1565C0', linewidth=0.8))
        ax.annotate('', xy=(x_air, y_under + h_under + 0.55), xytext=(x_air, y_under + 0.18),
                    arrowprops=dict(arrowstyle='->', color=c_air, lw=1.8, alpha=0.9))

    y_salida = canal_y + canal_alto * 0.36
    ax.plot([x_der, x_der + 1.45], [y_salida, y_salida], color='#444444', linewidth=2.2)
    ax.annotate('', xy=(x_der + 1.45, y_salida), xytext=(x_der + 0.15, y_salida),
                arrowprops=dict(arrowstyle='->', color='#1565C0', lw=2.5))
    ax.text(x_der + 0.60, y_salida + 0.10, 'Efluente a sedimentador', ha='left', va='bottom',
            fontsize=8.2, color='#1565C0', fontweight='bold')

    dash = dict(linestyle='--', color='#999999', linewidth=0.8, alpha=0.7)
    ax.axhline(y=y_medio, xmin=0.18, xmax=0.82, **dash)
    ax.axhline(y=y_dist, xmin=0.18, xmax=0.82, **dash)
    ax.axhline(y=y_dist + h_dist, xmin=0.18, xmax=0.82, **dash)

    x_dim = x_izq - 1.9

    def draw_dim(y1, y2, x_pos, label):
        ax.plot([x_pos, x_pos], [y1, y2], 'k-', linewidth=0.8)
        ax.plot([x_pos - 0.1, x_pos + 0.1], [y1, y1], 'k-', linewidth=0.8)
        ax.plot([x_pos - 0.1, x_pos + 0.1], [y2, y2], 'k-', linewidth=0.8)
        ax.annotate('', xy=(x_pos, y2 - 0.05), xytext=(x_pos, y2 - 0.24),
                    arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
        ax.annotate('', xy=(x_pos, y1 + 0.05), xytext=(x_pos, y1 + 0.24),
                    arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
        ax.text(x_pos - 0.28, (y1 + y2) / 2, label, ha='right', va='center', fontsize=8)

    draw_dim(y_under, y_medio, x_dim, f'{H_underdrain:.2f} m')
    draw_dim(y_medio, y_dist, x_dim, f'{H_medio:.2f} m')
    draw_dim(y_dist, y_dist + h_dist, x_dim, f'{H_distribucion:.2f} m')
    if h_bordo > 0.15:
        draw_dim(y_dist + h_dist, y_top, x_dim, f'{H_bordo:.2f} m')

    y_dim = y_base - 0.75
    ax.plot([x_izq, x_der], [y_dim, y_dim], 'k-', linewidth=0.8)
    ax.plot([x_izq, x_izq], [y_dim - 0.1, y_dim + 0.1], 'k-', linewidth=0.8)
    ax.plot([x_der, x_der], [y_dim - 0.1, y_dim + 0.1], 'k-', linewidth=0.8)
    ax.annotate('', xy=(x_izq + 0.25, y_dim), xytext=(x_izq + 0.05, y_dim),
                arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
    ax.annotate('', xy=(x_der - 0.25, y_dim), xytext=(x_der - 0.05, y_dim),
                arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
    ax.text(x_centro, y_dim - 0.16, f'Ø {D:.1f} m', ha='center', va='top', fontsize=8)

    x_dim_total = x_izq - 2.75
    ax.plot([x_dim_total, x_dim_total], [y_base, y_top], 'k-', linewidth=0.8)
    ax.plot([x_dim_total - 0.1, x_dim_total + 0.1], [y_base, y_base], 'k-', linewidth=0.8)
    ax.plot([x_dim_total - 0.1, x_dim_total + 0.1], [y_top, y_top], 'k-', linewidth=0.8)
    ax.text(x_dim_total - 0.28, (y_base + y_top) / 2, f'H = {H_total:.2f} m',
            ha='right', va='center', fontsize=8, fontweight='bold')

    offset_x = x_der + 0.55
    ax.text(offset_x, y_dist + h_dist + h_bordo / 2 + 0.02, 'Bordo libre y cámara\ndel distribuidor', ha='left', va='center', fontsize=8)
    ax.text(offset_x, y_dist + h_dist * 0.45, f'Distribuidor rotatorio\n{num_brazos:.0f} brazos | {Q_brazo:.1f} m³/h por brazo',
            ha='left', va='center', fontsize=8, fontweight='bold')
    ax.text(offset_x, y_medio + h_medio * 0.55, f'Medio plástico\nqA = {qA:.2f} m³/m²·h\nS₀ = {S0:.1f} mg/L',
            ha='left', va='center', fontsize=8, fontweight='bold')

    ax.text(x_izq - 1.02, y_under + 0.15, 'Entrada de aire\nnatural', ha='center', va='bottom',
            fontsize=8, color=c_air, fontweight='bold')

    ax.set_xlim(x_izq - 3.0, x_der + 3.15)
    ax.set_ylim(y_base - 1.1, y_top + 1.2)
    ax.set_aspect('equal')
    ax.axis('off')

    fig_path = os.path.join(output_dir, 'Esquema_Filtro_Percolador.png')
    fig.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white', pad_inches=0.2)
    plt.close()

    return fig_path


def generar_esquema_sedimentador_secundario(resultados_sed: dict, output_dir: str = "resultados") -> str:
    """
    Genera un esquema técnico del sedimentador secundario en sección vertical.
    Muestra zona líquida, fondo en tolva, vertedero perimetral, entrada central
    y salida de efluente clarificado.
    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle

    D = resultados_sed.get('D_m', 5.9)
    H_lateral = resultados_sed.get('h_sed_m', 3.5)
    H_tolva = 0.50
    H_bordo = 0.30
    H_total = H_lateral + H_tolva + H_bordo
    Q = resultados_sed.get('Q_m3_d', 432.0)
    Qmax = resultados_sed.get('Q_max_m3_d', 1080.0)
    SOR = resultados_sed.get('SOR_m3_m2_d', 16.0)
    SORmax = resultados_sed.get('SOR_max_m3_m2_d', 40.0)
    TRH = resultados_sed.get('TRH_h', 5.2)
    weir = resultados_sed.get('weir_loading_m3_m_d', 23.5)

    ancho = 5.8
    altura_total = 8.0
    escala = altura_total / max(H_total, 0.1)

    x_centro = 5.8
    y_base = 1.0
    x_izq = x_centro - ancho / 2
    x_der = x_centro + ancho / 2

    h_tolva = H_tolva * escala
    h_lateral = H_lateral * escala
    h_bordo = H_bordo * escala

    y_tolva_top = y_base + h_tolva
    y_liq_top = y_tolva_top + h_lateral
    y_top = y_liq_top + h_bordo

    fig, ax = plt.subplots(figsize=(9, 10))

    c_tanque = '#FFFFFF'
    c_agua = '#DCEEF8'
    c_lodos = '#D5B48C'
    c_tolva = '#CFCFCF'
    c_vertedero = '#B0BEC5'
    c_flow = '#1565C0'
    c_influente = '#2E7D32'
    c_lodos_flow = '#8D6E63'

    tanque = FancyBboxPatch(
        (x_izq, y_base), ancho, y_top - y_base,
        boxstyle="round,pad=0.12",
        facecolor=c_tanque, edgecolor='#555555', linewidth=2
    )
    ax.add_patch(tanque)

    agua = Rectangle(
        (x_izq + 0.1, y_tolva_top), ancho - 0.2, h_lateral,
        facecolor=c_agua, edgecolor='none', alpha=0.9
    )
    ax.add_patch(agua)

    tolva = Polygon(
        [
            (x_izq + 0.15, y_tolva_top),
            (x_der - 0.15, y_tolva_top),
            (x_centro + 0.45, y_base + 0.12),
            (x_centro - 0.45, y_base + 0.12),
        ],
        closed=True, facecolor=c_tolva, edgecolor='#777777', linewidth=1.2
    )
    ax.add_patch(tolva)

    # Lodo acumulado en la tolva
    lodos = Polygon(
        [
            (x_izq + 0.6, y_tolva_top),
            (x_der - 0.6, y_tolva_top),
            (x_centro + 0.30, y_base + 0.22),
            (x_centro - 0.30, y_base + 0.22),
        ],
        closed=True, facecolor=c_lodos, edgecolor='none', alpha=0.95
    )
    ax.add_patch(lodos)

    # Sólidos suspendidos suaves
    import numpy as np
    np.random.seed(31)
    for _ in range(35):
        cx = np.random.uniform(x_izq + 0.45, x_der - 0.45)
        cy = np.random.uniform(y_tolva_top + 0.15, y_liq_top - 0.2)
        r = np.random.uniform(0.03, 0.08)
        ax.add_patch(Circle((cx, cy), r, facecolor='#C7A17A', edgecolor='#9C7B5C', alpha=0.55))

    # Pozo y tubería de entrada central
    x_feed = x_centro
    y_feed = y_liq_top - h_lateral * 0.12
    ax.plot([x_feed, x_feed], [y_top + 0.45, y_feed], color='#444444', linewidth=2.3)
    ax.add_patch(Circle((x_feed, y_feed), 0.16, facecolor='#B0BEC5', edgecolor='#455A64', linewidth=1.1))
    ax.plot([x_izq - 1.3, x_feed], [y_top + 0.45, y_top + 0.45], color='#444444', linewidth=2.1)
    ax.annotate('', xy=(x_izq - 0.15, y_top + 0.45), xytext=(x_izq - 1.05, y_top + 0.45),
                arrowprops=dict(arrowstyle='->', color=c_influente, lw=2.5))
    ax.text(x_izq - 1.35, y_top + 0.62, f'Efluente FP\nQ = {Q/24:.2f} m³/h',
            ha='left', va='bottom', fontsize=8.4, color=c_influente, fontweight='bold')

    # Flechas de sedimentación
    for x_s in np.linspace(x_izq + 1.0, x_der - 1.0, 4):
        ax.annotate('', xy=(x_s, y_tolva_top + h_lateral * 0.18), xytext=(x_s, y_liq_top - 0.55),
                    arrowprops=dict(arrowstyle='-|>', color=c_lodos_flow, lw=2.0, alpha=0.8))

    # Flecha de extracción de lodos
    ax.annotate('', xy=(x_centro, y_base - 0.25), xytext=(x_centro, y_base + 0.35),
                arrowprops=dict(arrowstyle='->', color='#6D4C41', lw=2.4))
    ax.text(x_centro + 0.28, y_base - 0.02, 'Purga de lodos', ha='left', va='center',
            fontsize=8.0, color='#6D4C41', fontweight='bold')

    # Vertedero y salida
    y_salida = y_liq_top - h_lateral * 0.18
    ax.add_patch(Rectangle((x_der - 0.22, y_salida - 0.20), 0.22, 0.40,
                           facecolor=c_vertedero, edgecolor='#607D8B', linewidth=1.0))
    ax.plot([x_der, x_der + 1.35], [y_salida, y_salida], color='#444444', linewidth=2.0)
    ax.annotate('', xy=(x_der + 1.35, y_salida), xytext=(x_der + 0.15, y_salida),
                arrowprops=dict(arrowstyle='->', color=c_flow, lw=2.5))
    ax.text(x_der + 1.00, y_salida + 0.05, 'Efluente clarificado',
            ha='left', va='bottom', fontsize=8.3, color=c_flow, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.9, pad=0.08))

    dash = dict(linestyle='--', color='#999999', linewidth=0.8, alpha=0.65)
    ax.axhline(y=y_tolva_top, xmin=0.18, xmax=0.82, **dash)
    ax.axhline(y=y_liq_top, xmin=0.18, xmax=0.82, **dash)

    x_dim = x_izq - 1.95

    def draw_dim(y1, y2, x_pos, label):
        ax.plot([x_pos, x_pos], [y1, y2], 'k-', linewidth=0.8)
        ax.plot([x_pos - 0.1, x_pos + 0.1], [y1, y1], 'k-', linewidth=0.8)
        ax.plot([x_pos - 0.1, x_pos + 0.1], [y2, y2], 'k-', linewidth=0.8)
        ax.annotate('', xy=(x_pos, y2 - 0.05), xytext=(x_pos, y2 - 0.24),
                    arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
        ax.annotate('', xy=(x_pos, y1 + 0.05), xytext=(x_pos, y1 + 0.24),
                    arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
        ax.text(x_pos - 0.32, (y1 + y2) / 2, label, ha='right', va='center', fontsize=8)

    draw_dim(y_base, y_tolva_top, x_dim, f'{H_tolva:.2f} m')
    draw_dim(y_tolva_top, y_liq_top, x_dim, f'{H_lateral:.2f} m')
    draw_dim(y_liq_top, y_top, x_dim, f'{H_bordo:.2f} m')

    x_dim_total = x_izq - 3.05
    ax.plot([x_dim_total, x_dim_total], [y_base, y_top], 'k-', linewidth=0.8)
    ax.plot([x_dim_total - 0.1, x_dim_total + 0.1], [y_base, y_base], 'k-', linewidth=0.8)
    ax.plot([x_dim_total - 0.1, x_dim_total + 0.1], [y_top, y_top], 'k-', linewidth=0.8)
    ax.text(x_dim_total - 0.45, (y_base + y_top) / 2, f'H = {H_total:.2f} m',
            ha='right', va='center', fontsize=8, fontweight='bold')

    y_dim = y_base - 0.72
    ax.plot([x_izq, x_der], [y_dim, y_dim], 'k-', linewidth=0.8)
    ax.plot([x_izq, x_izq], [y_dim - 0.1, y_dim + 0.1], 'k-', linewidth=0.8)
    ax.plot([x_der, x_der], [y_dim - 0.1, y_dim + 0.1], 'k-', linewidth=0.8)
    ax.annotate('', xy=(x_izq + 0.25, y_dim), xytext=(x_izq + 0.05, y_dim),
                arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
    ax.annotate('', xy=(x_der - 0.25, y_dim), xytext=(x_der - 0.05, y_dim),
                arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
    ax.text(x_centro, y_dim - 0.16, f'Ø {D:.1f} m', ha='center', va='top', fontsize=8)

    offset_x = x_der + 0.58
    ax.text(offset_x, y_liq_top - h_lateral * 0.04, 'Vertedero perimetral\ny salida de efluente',
            ha='left', va='center', fontsize=8)
    ax.text(offset_x, y_tolva_top + h_lateral * 0.56,
            f'Zona de clarificación\nSOR = {SOR:.1f} m³/m²·d\nTRH = {TRH:.1f} h',
            ha='left', va='center', fontsize=8, fontweight='bold')
    ax.text(offset_x, y_base + h_tolva * 0.55,
            f'Tolva de lodos\nSOR máx = {SORmax:.1f} m³/m²·d\nq vert. = {weir:.1f} m³/m·d',
            ha='left', va='center', fontsize=8)

    ax.set_xlim(x_izq - 3.60, x_der + 3.8)
    ax.set_ylim(y_base - 1.0, y_top + 1.25)
    ax.set_aspect('equal')
    ax.axis('off')

    fig_path = os.path.join(output_dir, 'Esquema_Sedimentador_Secundario.png')
    fig.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white', pad_inches=0.2)
    plt.close()

    return fig_path


def generar_esquema_desarenador(resultados_des: dict, output_dir: str = "resultados") -> str:
    """
    Genera un esquema técnico del desarenador con dos vistas:
    perfil longitudinal y vista en planta.
    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Polygon

    L = resultados_des.get('L_diseno_m', 3.0)
    B = resultados_des.get('b_canal_m', 0.60)
    H_util = resultados_des.get('H_util_m', 0.40)
    H_arena = 0.20
    H_bordo = 0.30
    H_total = H_util + H_arena + H_bordo
    Q_L_s = resultados_des.get('Q_linea_L_s', 5.0)
    v_h = resultados_des.get('v_h_real_m_s', 0.021)
    t_r = resultados_des.get('t_r_real_s', 144.0)
    v_s = resultados_des.get('v_s_m_s', 0.021)
    v_c = resultados_des.get('v_c_scour_m_s', 0.339)
    Qmax = resultados_des.get('Q_max_L_s', 45.0)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 6))

    c_muro = '#555555'
    c_concreto = '#FBFBFB'
    c_agua = '#DCEEF8'
    c_arena = '#D5B48C'
    c_losa = '#D0D0D0'
    c_influente = '#2E7D32'
    c_efluente = '#1565C0'
    c_particula = '#8D6E63'
    c_bafle = '#90A4AE'
    dash = dict(linestyle='--', color='#999999', linewidth=0.8, alpha=0.7)

    # === PERFIL LONGITUDINAL ===
    x0 = 1.2
    y0 = 1.0
    espesor = 0.06
    escala_x = 2.1
    escala_y = 2.0
    largo = L * escala_x
    h_agua = H_util * escala_y
    h_arena = H_arena * escala_y
    h_bordo = H_bordo * escala_y
    largo_in = largo * 0.18
    largo_rampa = largo * 0.14
    largo_camara = largo * 0.48
    largo_salida = largo - largo_in - largo_rampa - largo_camara
    x_in_end = x0 + largo_in
    x_rampa_end = x_in_end + largo_rampa
    x_camara_end = x_rampa_end + largo_camara
    x_out_end = x0 + largo

    y_base_in = y0 + h_arena * 0.85
    y_base_camara = y0
    y_superficie = y_base_camara + h_arena + h_agua
    y_top = y_superficie + h_bordo

    # muros y losa
    ax1.add_patch(Rectangle((x0, y_base_in), espesor, y_top - y_base_in, facecolor=c_concreto, edgecolor=c_muro, linewidth=1.8))
    ax1.add_patch(Rectangle((x_out_end - espesor, y_base_camara), espesor, y_top - y_base_camara, facecolor=c_concreto, edgecolor=c_muro, linewidth=1.8))
    ax1.plot([x0, x_in_end], [y_base_in, y_base_in], color=c_muro, linewidth=2.0)
    ax1.plot([x_in_end, x_rampa_end], [y_base_in, y_base_camara], color=c_muro, linewidth=2.0)
    ax1.plot([x_rampa_end, x_camara_end], [y_base_camara, y_base_camara], color=c_muro, linewidth=2.0)
    ax1.plot([x_camara_end, x_out_end], [y_base_camara, y_base_camara], color=c_muro, linewidth=2.0)
    ax1.plot([x0, x0], [y_base_in, y_top], color=c_muro, linewidth=2.0)
    ax1.plot([x_out_end, x_out_end], [y_base_camara, y_top], color=c_muro, linewidth=2.0)

    # agua
    agua_pts = [
        (x0 + espesor, y_base_in + H_arena * 0.25 * escala_y),
        (x_in_end, y_base_in + H_arena * 0.25 * escala_y),
        (x_rampa_end, y_base_camara + h_arena),
        (x_out_end - espesor, y_base_camara + h_arena),
        (x_out_end - espesor, y_superficie),
        (x0 + espesor, y_superficie),
    ]
    ax1.add_patch(Polygon(agua_pts, closed=True, facecolor=c_agua, edgecolor='none', alpha=0.92))

    # arena / depósito
    arena_pts = [
        (x_in_end - 0.04, y_base_in),
        (x_rampa_end, y_base_camara),
        (x_camara_end, y_base_camara),
        (x_out_end - espesor, y_base_camara),
        (x_out_end - espesor, y_base_camara + h_arena),
        (x_rampa_end, y_base_camara + h_arena),
        (x_in_end, y_base_in + h_arena * 0.15),
    ]
    ax1.add_patch(Polygon(arena_pts, closed=True, facecolor=c_arena, edgecolor='none', alpha=0.95))
    ax1.add_patch(Rectangle((x0 + 0.10, y_base_in + 0.02), largo - 0.20, 0.04, facecolor=c_losa, edgecolor='none'))

    # flujo
    for frac in (0.25, 0.52, 0.78):
        y_flow = y_base_camara + h_arena + h_agua * frac
        ax1.annotate('', xy=(x_out_end - 1.05, y_flow), xytext=(x_in_end + 0.40, y_flow),
                     arrowprops=dict(arrowstyle='->', color=c_influente, lw=2.2))

    # partículas sedimentando
    xs = [x_rampa_end + largo_camara * 0.15, x_rampa_end + largo_camara * 0.40,
          x_rampa_end + largo_camara * 0.65, x_rampa_end + largo_camara * 0.86]
    for x_part in xs:
        ax1.annotate('', xy=(x_part, y_base_camara + h_arena * 0.55), xytext=(x_part, y_base_camara + h_arena + h_agua * 0.74),
                     arrowprops=dict(arrowstyle='-|>', color=c_particula, lw=1.8, alpha=0.8))

    # estructura de salida
    ax1.add_patch(Rectangle((x_camara_end + 0.10, y_base_camara + h_arena + h_agua * 0.40), 0.10, h_agua * 0.55,
                            facecolor=c_bafle, edgecolor='#607D8B', linewidth=1.0))
    ax1.add_patch(Rectangle((x_camara_end + 0.27, y_base_camara), 0.16, h_arena + h_agua * 0.95,
                            facecolor='none', edgecolor=c_muro, linewidth=1.2))
    y_salida = y_base_camara + h_arena + h_agua * 0.60
    ax1.plot([x_out_end, x_out_end + 1.00], [y_salida, y_salida], color='#444444', linewidth=2.0)
    ax1.annotate('', xy=(x_out_end + 1.00, y_salida), xytext=(x_out_end + 0.16, y_salida),
                 arrowprops=dict(arrowstyle='->', color=c_efluente, lw=2.5))
    ax1.text(x_out_end + 0.66, y_salida + 0.16, 'Salida',
             ha='left', va='bottom', fontsize=8.2, color=c_efluente, fontweight='bold',
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.92, pad=0.1))

    # entrada
    y_entrada = y_base_camara + h_arena + h_agua * 0.52
    ax1.plot([x0 - 0.95, x0], [y_entrada, y_entrada], color='#444444', linewidth=2.0)
    ax1.annotate('', xy=(x0 - 0.02, y_entrada), xytext=(x0 - 0.78, y_entrada),
                 arrowprops=dict(arrowstyle='->', color=c_influente, lw=2.5))
    ax1.text(x0 + 0.62, y_superficie + 0.10, f'Afluente\nQ = {Q_L_s:.1f} L/s',
             ha='center', va='bottom', fontsize=8.6, color=c_influente, fontweight='bold',
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.92, pad=0.1))

    # cotas y niveles
    y_agua = y_base_camara + h_arena
    ax1.axhline(y=y_agua, xmin=0.12, xmax=0.86, **dash)
    ax1.axhline(y=y_superficie, xmin=0.12, xmax=0.86, **dash)
    x_dim = x0 - 1.02
    x_dim_total = x0 - 2.08

    def draw_dim(ax, y1, y2, x_pos, label):
        ax.plot([x_pos, x_pos], [y1, y2], 'k-', linewidth=0.8)
        ax.plot([x_pos - 0.08, x_pos + 0.08], [y1, y1], 'k-', linewidth=0.8)
        ax.plot([x_pos - 0.08, x_pos + 0.08], [y2, y2], 'k-', linewidth=0.8)
        ax.annotate('', xy=(x_pos, y2 - 0.03), xytext=(x_pos, y2 - 0.20),
                    arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
        ax.annotate('', xy=(x_pos, y1 + 0.03), xytext=(x_pos, y1 + 0.20),
                    arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
        ax.text(x_pos - 0.16, (y1 + y2) / 2, label, ha='right', va='center', fontsize=8)

    draw_dim(ax1, y_base_camara, y_agua, x_dim, f'{H_arena:.2f} m')
    draw_dim(ax1, y_agua, y_superficie, x_dim, f'{H_util:.2f} m')
    draw_dim(ax1, y_superficie, y_top, x_dim, f'{H_bordo:.2f} m')
    draw_dim(ax1, y_base_camara, y_top, x_dim_total, f'H = {H_total:.2f} m')

    y_dim = y_base_camara - 0.24
    ax1.plot([x_rampa_end, x_out_end], [y_dim, y_dim], 'k-', linewidth=0.8)
    ax1.plot([x_rampa_end, x_rampa_end], [y_dim - 0.08, y_dim + 0.08], 'k-', linewidth=0.8)
    ax1.plot([x_out_end, x_out_end], [y_dim - 0.08, y_dim + 0.08], 'k-', linewidth=0.8)
    ax1.text((x_rampa_end + x_out_end) / 2, y_dim - 0.14, f'Lcd = {L:.1f} m', ha='center', va='top', fontsize=8)

    ax1.text(x_out_end + 0.30, y_base_camara + h_arena + h_agua * 0.22,
             'Zona de flujo',
             ha='left', va='center', fontsize=8, fontweight='bold',
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.92, pad=0.1))
    ax1.text(x_out_end + 0.30, y_base_camara + h_arena * 0.06,
             'Deposito de arena',
             ha='left', va='center', fontsize=8,
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.92, pad=0.1))
    ax1.set_title('Perfil longitudinal', fontsize=11, fontweight='bold', pad=8)
    ax1.set_xlim(x0 - 1.65, x_out_end + 2.45)
    ax1.set_ylim(y_base_camara - 0.8, y_top + 0.75)
    ax1.set_aspect('equal')
    ax1.axis('off')

    # === VISTA EN PLANTA ===
    x0c = 1.0
    y0c = 1.0
    escala_px = 1.50
    escala_py = 4.4
    largo_p = L * escala_px
    ancho_p = B * escala_py
    margen = 0.07
    largo_in_p = largo_p * 0.18
    largo_conv_p = largo_p * 0.18
    largo_cam_p = largo_p * 0.46
    largo_out_p = largo_p * 0.18
    x_in_p = x0c
    x_conv1_p = x_in_p + largo_in_p
    x_cam1_p = x_conv1_p + largo_conv_p
    x_cam2_p = x_cam1_p + largo_cam_p
    x_out_p = x0c + largo_p
    b_in = ancho_p * 0.42
    y_mid = y0c + ancho_p * 0.50
    y_top_ch = y0c + ancho_p

    contorno = [
        (x_in_p, y_mid + b_in / 2),
        (x_conv1_p, y_mid + b_in / 2),
        (x_cam1_p, y_top_ch),
        (x_cam2_p, y_top_ch),
        (x_out_p - largo_out_p * 0.45, y_mid + b_in / 2),
        (x_out_p, y_mid + b_in / 2),
        (x_out_p, y_mid - b_in / 2),
        (x_out_p - largo_out_p * 0.45, y_mid - b_in / 2),
        (x_cam2_p, y0c),
        (x_cam1_p, y0c),
        (x_conv1_p, y_mid - b_in / 2),
        (x_in_p, y_mid - b_in / 2),
    ]
    ax2.add_patch(Polygon(contorno, closed=True, facecolor=c_concreto, edgecolor=c_muro, linewidth=2.0))

    agua_contorno = [
        (x_in_p + margen, y_mid + b_in / 2 - margen),
        (x_conv1_p, y_mid + b_in / 2 - margen),
        (x_cam1_p + margen * 0.4, y_top_ch - margen),
        (x_cam2_p - margen * 0.4, y_top_ch - margen),
        (x_out_p - largo_out_p * 0.45, y_mid + b_in / 2 - margen),
        (x_out_p - margen, y_mid + b_in / 2 - margen),
        (x_out_p - margen, y_mid - b_in / 2 + margen),
        (x_out_p - largo_out_p * 0.45, y_mid - b_in / 2 + margen),
        (x_cam2_p - margen * 0.4, y0c + margen),
        (x_cam1_p + margen * 0.4, y0c + margen),
        (x_conv1_p, y_mid - b_in / 2 + margen),
        (x_in_p + margen, y_mid - b_in / 2 + margen),
    ]
    ax2.add_patch(Polygon(agua_contorno, closed=True, facecolor=c_agua, edgecolor='none', alpha=0.92))

    # líneas de flujo en planta
    y_tracks = [y0c + ancho_p * 0.22, y0c + ancho_p * 0.50, y0c + ancho_p * 0.78]
    for y_track in y_tracks:
        ax2.annotate('', xy=(x_out_p - largo_out_p * 0.55, y_track), xytext=(x_cam1_p + 0.22, y_track),
                     arrowprops=dict(arrowstyle='->', color=c_influente, lw=2.0))

    # zona central / depósito
    ax2.add_patch(Rectangle((x_cam1_p + 0.12, y0c + ancho_p * 0.16),
                            (x_cam2_p - x_cam1_p) - 0.24, ancho_p * 0.68,
                            facecolor='none', edgecolor='#B8946F', linewidth=1.0, linestyle='--', alpha=0.9))

    # entrada y salida
    ax2.plot([x_in_p - 0.95, x_in_p], [y_mid, y_mid], color='#444444', linewidth=2.0)
    ax2.annotate('', xy=(x_in_p - 0.02, y_mid), xytext=(x_in_p - 0.80, y_mid),
                 arrowprops=dict(arrowstyle='->', color=c_influente, lw=2.5))
    ax2.text(x_in_p - 1.82, y_mid + 0.30, 'Afluente',
             ha='left', va='bottom', fontsize=8.4, color=c_influente, fontweight='bold',
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.92, pad=0.1))

    ax2.plot([x_out_p, x_out_p + 0.95], [y_mid, y_mid], color='#444444', linewidth=2.0)
    ax2.annotate('', xy=(x_out_p + 0.95, y_mid), xytext=(x_out_p + 0.15, y_mid),
                 arrowprops=dict(arrowstyle='->', color=c_efluente, lw=2.5))
    ax2.text(x_out_p + 0.12, y_mid + 0.14, 'Salida',
             ha='left', va='bottom', fontsize=8.4, color=c_efluente, fontweight='bold',
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.92, pad=0.1))

    y_dim_c = y0c - 0.46
    ax2.plot([x_cam1_p, x_cam2_p], [y_dim_c, y_dim_c], 'k-', linewidth=0.8)
    ax2.plot([x_cam1_p, x_cam1_p], [y_dim_c - 0.08, y_dim_c + 0.08], 'k-', linewidth=0.8)
    ax2.plot([x_cam2_p, x_cam2_p], [y_dim_c - 0.08, y_dim_c + 0.08], 'k-', linewidth=0.8)
    ax2.text((x_cam1_p + x_cam2_p) / 2, y_dim_c - 0.14, f'Lcd = {L:.1f} m', ha='center', va='top', fontsize=8)

    x_dim_c = x_out_p + 1.05
    ax2.plot([x_dim_c, x_dim_c], [y0c, y_top_ch], 'k-', linewidth=0.8)
    ax2.text(x_dim_c + 0.06, y_top_ch + 0.06, f'B = {B:.2f} m',
             ha='left', va='bottom', fontsize=8,
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.92, pad=0.08))

    ax2.set_title('Vista en planta', fontsize=11, fontweight='bold', pad=8)
    ax2.text(x_cam2_p - 0.04, y0c + 0.34,
             'Zona de deposito de arena', ha='center', va='center', fontsize=8,
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.85, pad=0.08))
    ax2.set_xlim(x_in_p - 1.10, x_out_p + 1.90)
    ax2.set_ylim(y0c - 0.8, y_top_ch + 0.8)
    ax2.set_aspect('equal')
    ax2.axis('off')

    fig_path = os.path.join(output_dir, 'Esquema_Desarenador.png')
    fig.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white', pad_inches=0.2)
    plt.close()

    return fig_path


