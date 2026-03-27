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


def dibujar_unidad_layout(ax, x: float, y: float, unidad: str, color: str, font_scale: float = 1.0, DIM: dict = None):
    """Dibuja una unidad en el layout con acotaciones"""
    dim_dict = DIM if DIM else DIMENSIONES
    props = dim_dict[unidad]
    
    fontsize = FONT_CONFIG['unidad']
    acot_fontsize = FONT_CONFIG['acotacion']
    
    offset_linea = 0.6
    offset_texto = 1.1
    
    if props['geom'] == 'circ':
        diam = props['diametro']
        radio = diam / 2
        circle = Circle((x + radio, y + radio), radio, 
                       facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        
        nombre = unidad.replace('_', '\n')
        ax.text(x + radio, y + radio, nombre, ha='center', va='center', 
               fontsize=fontsize, fontweight='bold')
        
        # Acotación
        ax.annotate('', xy=(x + diam, y - offset_linea), xytext=(x, y - offset_linea),
                   arrowprops=dict(arrowstyle='<->', color='black', lw=1))
        ax.text(x + diam/2, y - offset_texto, f'Ø{diam:.1f}m', ha='center', fontsize=acot_fontsize, 
               color='black')
        
        return diam, diam
    else:
        largo = props['largo']
        ancho = props['ancho']
        
        rect = Rectangle((x, y), largo, ancho, facecolor=color, 
                        edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        
        nombre = unidad.replace('_', '\n')
        ax.text(x + largo/2, y + ancho/2, nombre, ha='center', va='center',
               fontsize=fontsize, fontweight='bold')
        
        # Acotaciones horizontales (largo)
        ax.annotate('', xy=(x + largo, y - offset_linea), xytext=(x, y - offset_linea),
                   arrowprops=dict(arrowstyle='<->', color='black', lw=1))
        ax.text(x + largo/2, y - offset_texto, f'{largo:.1f}m', ha='center', fontsize=acot_fontsize,
               color='black')
        
        return largo, ancho


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
        'sedimentador': 'Sedimentador',
        'sedimentador_sec': 'Sedimentador',
        'uv': 'UV',
        'lecho_secado': None,  # Se maneja separado
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
            diam = res.get('D_m', res.get('diametro_m', 5.0))
            dim[key_layout] = {
                'tipo': 'tratamiento_primario',
                'diametro': diam,
                'geom': 'circ'
            }
        elif key_res == 'filtro_percolador':
            diam = res.get('D_filtro_m', res.get('diametro_m', 5.0))
            dim[key_layout] = {
                'tipo': 'tratamiento_secundario',
                'diametro': diam,
                'geom': 'circ'
            }
        elif key_res == 'sedimentador':
            diam = res.get('D_m', res.get('diametro_m', 5.0))
            dim[key_layout] = {
                'tipo': 'sedimentacion',
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
    
    # ============ LECHO COMPARTIDO ============
    # Usar dimensiones calculadas - DEBEN venir en lecho_dimensiones
    if lecho_dimensiones is None:
        raise ValueError("Faltan dimensiones del lecho de secado. Asegúrate de pasar lecho_dimensiones desde los resultados del dimensionamiento.")
    
    lecho_largo, lecho_ancho = lecho_dimensiones
    
    if lecho_largo <= 0 or lecho_ancho <= 0:
        raise ValueError(f"Dimensiones del lecho inválidas: largo={lecho_largo}, ancho={lecho_ancho}. Deben ser > 0.")
    
    x_lecho = MARGEN + largo_linea + SEP_UNIDADES
    y_centro_lecho = (centro_linea1 + centro_linea2) / 2 - lecho_ancho / 2
    
    # =============================================================================
    # FLECHAS DE CONEXIÓN DE LODOS AL LECHO DE SECADO
    # =============================================================================
    # NOTA CONCEPTUAL: El lecho de secado recibe LODOS (sólidos), no efluente tratado.
    # Las fuentes de lodos son:
    #   1. UASB: lodo anaerobio excedente del manto de lodos
    #   2. Sedimentador Secundario: humus (lodos biológicos del filtro percolador)
    # 
    # El efluente del UV va directamente al cuerpo receptor (no al lecho de secado).
    # 
    # NOTA DE DISEÑO: El lecho se dibuja GIRADO 90° para que su lado largo (12.1m) 
    # quede en posición VERTICAL, permitiendo flechas de lodos más cortas y directas.
    
    # Girar el lecho 90°: intercambiar largo y ancho para el dibujo
    # El lecho queda con 4.0m de ancho (horizontal) y 12.1m de alto (vertical)
    lecho_ancho_draw = lecho_ancho  # 4.0m (ahora es la dimensión horizontal)
    lecho_alto_draw = lecho_largo   # 12.1m (ahora es la dimensión vertical)
    
    # Recalcular posición Y para centrar el lecho verticalmente
    y_lecho = (centro_linea1 + centro_linea2) / 2 - lecho_alto_draw / 2
    
    # Redibujar lecho girado
    rect = Rectangle((x_lecho, y_lecho), lecho_ancho_draw, lecho_alto_draw, 
                     facecolor=COLORES['manejo_lodos'], 
                     edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    
    # Texto del lecho
    fontsize = FONT_CONFIG['unidad']
    ax.text(x_lecho + lecho_ancho_draw/2, y_lecho + lecho_alto_draw/2, 
           'Lecho de\nSecado', 
           ha='center', va='center', fontsize=fontsize, fontweight='bold')
    
    # Encontrar índices de UASB y Sedimentador en las líneas
    def encontrar_indice_unidad(posiciones, nombre_unidad):
        for i, (x, y, unidad, ancho, alto) in enumerate(posiciones):
            if nombre_unidad in unidad:
                return i
        return None
    
    idx_uasb_l1 = encontrar_indice_unidad(posiciones_linea1, 'UASB')
    idx_sed_l1 = encontrar_indice_unidad(posiciones_linea1, 'Sedimentador')
    idx_uasb_l2 = encontrar_indice_unidad(posiciones_linea2, 'UASB')
    idx_sed_l2 = encontrar_indice_unidad(posiciones_linea2, 'Sedimentador')
    
    # Radio típico de unidades circulares (para cálculo de puntos de salida)
    radio_uasb = DIM['UASB'].get('diametro', 5.0) / 2
    radio_sed = DIM['Sedimentador'].get('diametro', 5.0) / 2
    
    # Función auxiliar para obtener punto en el borde del círculo (más cercano al lecho)
    # El lecho está a la derecha, así que tomamos el punto derecho del círculo
    def get_unidad_lodos_exit(x, y, unidad, DIM, radio, offset_y=0):
        """Obtiene punto en el borde derecho del círculo para salida de lodos"""
        centro_x = x + radio
        centro_y = y + radio
        # Punto en el borde derecho, con offset vertical
        return (centro_x + radio, centro_y + offset_y)
    
    # Flechas de lodos desde UASB -> Lecho (lado izquierdo del lecho)
    # Línea 1 (abajo): UASB superior -> parte inferior del lecho
    if idx_uasb_l1 is not None:
        x_uasb_l1, y_uasb_l1, _, _, _ = posiciones_linea1[idx_uasb_l1]
        # Punto de salida: parte inferior del UASB
        start_uasb_l1 = get_unidad_lodos_exit(x_uasb_l1, y_uasb_l1, 'UASB', DIM, radio_uasb, offset_y=-radio_uasb*0.5)
        # Punto de llegada: parte inferior del lecho (lado izquierdo)
        end_uasb_l1 = (x_lecho, y_lecho + lecho_alto_draw * 0.25)
        dibujar_flecha_lodos(ax, start_uasb_l1[0], start_uasb_l1[1], 
                             end_uasb_l1[0], end_uasb_l1[1])
    
    # Línea 2 (arriba): UASB inferior -> parte superior del lecho
    if idx_uasb_l2 is not None:
        x_uasb_l2, y_uasb_l2, _, _, _ = posiciones_linea2[idx_uasb_l2]
        # Punto de salida: parte superior del UASB
        start_uasb_l2 = get_unidad_lodos_exit(x_uasb_l2, y_uasb_l2, 'UASB', DIM, radio_uasb, offset_y=radio_uasb*0.5)
        # Punto de llegada: parte superior del lecho (lado izquierdo)
        end_uasb_l2 = (x_lecho, y_lecho + lecho_alto_draw * 0.75)
        dibujar_flecha_lodos(ax, start_uasb_l2[0], start_uasb_l2[1], 
                             end_uasb_l2[0], end_uasb_l2[1])
    
    # Flechas de lodos desde Sedimentador -> Lecho
    # Línea 1: Sedimentador -> parte media-baja del lecho
    if idx_sed_l1 is not None:
        x_sed_l1, y_sed_l1, _, _, _ = posiciones_linea1[idx_sed_l1]
        start_sed_l1 = get_unidad_lodos_exit(x_sed_l1, y_sed_l1, 'Sedimentador', DIM, radio_sed, offset_y=-radio_sed*0.3)
        end_sed_l1 = (x_lecho, y_lecho + lecho_alto_draw * 0.40)
        dibujar_flecha_lodos(ax, start_sed_l1[0], start_sed_l1[1], 
                             end_sed_l1[0], end_sed_l1[1])
    
    # Línea 2: Sedimentador -> parte media-alta del lecho
    if idx_sed_l2 is not None:
        x_sed_l2, y_sed_l2, _, _, _ = posiciones_linea2[idx_sed_l2]
        start_sed_l2 = get_unidad_lodos_exit(x_sed_l2, y_sed_l2, 'Sedimentador', DIM, radio_sed, offset_y=radio_sed*0.3)
        end_sed_l2 = (x_lecho, y_lecho + lecho_alto_draw * 0.60)
        dibujar_flecha_lodos(ax, start_sed_l2[0], start_sed_l2[1], 
                             end_sed_l2[0], end_sed_l2[1])
    
    # Calcular dimensiones del área
    max_x = x_lecho + lecho_largo + MARGEN
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
    text_fontsize = 9
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
    for tipo_nombre, color in COLORES.items():
        if any(DIM[u]['tipo'] == tipo_nombre for u in unidades_linea) or tipo_nombre == 'manejo_lodos':
            label = tipo_nombre.replace('_', ' ').title()
            leyenda_items.append(mpatches.Patch(color=color, label=label))
    
    legend_fontsize = FONT_CONFIG['leyenda']
    ax.legend(handles=leyenda_items, loc='upper left', fontsize=legend_fontsize, 
             framealpha=0.9, edgecolor='gray')
    
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
