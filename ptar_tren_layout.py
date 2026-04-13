#!/usr/bin/env python3
"""
PTAR TREN LAYOUT - Generador de layouts para trenes de tratamiento

Genera layouts visuales a partir de una lista de unidades, sin depender
de alternativas fijas A/B/C.

Uso:
    from ptar_tren_config import get_tren_piloto_humedal, TrenConfig
    from ptar_tren_integrador import integrar_tren
    from ptar_tren_layout import generar_layout_tren
    
    entrada = get_tren_piloto_humedal()
    config = TrenConfig.from_dict(entrada)
    resultado = integrar_tren(config)
    
    layout = generar_layout_tren(
        unidades=config.unidades,
        resultados=resultado["unidades"],
        num_lineas=config.num_lineas,
        output_dir="resultados/layouts"
    )
"""

import os
import sys
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ptar_config import COLORES, FONT_CONFIG, FIGSIZE, SEP_UNIDADES, SEP_LINEAS, MARGEN
from ptar_layout_graficador import (
    NOMBRES_DISPLAY,
    dibujar_unidad_layout,
    dibujar_flecha_flujo,
    dibujar_lecho_compartido,
    get_unidad_right_center,
    get_unidad_left_center,
)

# =============================================================================
# MAPEO DE CÓDIGOS DE UNIDADES A NOMBRES DE LAYOUT
# =============================================================================

MAPEO_UNIDADES_LAYOUT = {
    "rejillas": "Rejillas",
    "desarenador": "Desarenador",
    "uasb": "UASB",
    "abr": "UASB",  # Usar dimensiones similares a UASB
    "filtro_percolador": "Filtro_Percolador",
    "taf": "Filtro_Percolador",  # Similar
    "baf": "Biofiltro",
    "humedal_vertical": "Humedal_Vertical",
    "sedimentador_secundario": "Sedimentador",
    "cloro": "Desinfeccion",
    "uv": "UV",
    "lecho_secado": None,  # Manejado separado
}


# =============================================================================
# FUNCIONES PARA OBTENER DIMENSIONES REALES
# =============================================================================

def obtener_dimensiones_unidad(codigo_unidad: str, resultados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Obtiene las dimensiones reales de una unidad desde sus resultados.
    
    Args:
        codigo_unidad: Código de la unidad
        resultados: Diccionario con resultados de todas las unidades
        
    Returns:
        Dict con dimensiones {tipo, largo, ancho, diametro}
    """
    if codigo_unidad not in resultados:
        return {"tipo": "rect", "largo": 5.0, "ancho": 3.0}  # Default
    
    res = resultados[codigo_unidad]
    dim = {"tipo": "rect", "largo": 5.0, "ancho": 3.0}
    
    # Intentar extraer dimensiones según el tipo de unidad
    if codigo_unidad == "rejillas":
        # Rejillas: usar ancho de canal
        dim = {"tipo": "rect", "largo": 2.0, "ancho": res.get("b_m", 0.6)}
        
    elif codigo_unidad == "desarenador":
        # Desarenador: rectangular
        dim = {"tipo": "rect", "largo": res.get("L_total_m", 11.2), "ancho": res.get("b_total_m", 1.2)}
        
    elif codigo_unidad in ["uasb", "abr"]:
        # UASB/ABR: circular
        if "D_m" in res:
            dim = {"tipo": "circ", "diametro": res["D_m"]}
        elif "L_total_m" in res and "W_m" in res:
            dim = {"tipo": "rect", "largo": res["L_total_m"], "ancho": res["W_m"]}
        else:
            dim = {"tipo": "circ", "diametro": 4.8}
            
    elif codigo_unidad in ["filtro_percolador", "taf"]:
        # Filtro percolador: circular
        dim = {"tipo": "circ", "diametro": res.get("D_filtro_m", 5.4)}
        
    elif codigo_unidad == "baf":
        # BAF: circular
        dim = {"tipo": "circ", "diametro": res.get("D_m", 4.5)}
        
    elif codigo_unidad == "humedal_vertical":
        # Humedal: rectangular
        dim = {"tipo": "rect", "largo": res.get("largo_m", 25.0), "ancho": res.get("ancho_m", 10.0)}
        
    elif codigo_unidad == "sedimentador_secundario":
        # Sedimentador: circular
        dim = {"tipo": "circ", "diametro": res.get("D_m", 7.0)}
        
    elif codigo_unidad in ["cloro", "uv"]:
        # Desinfección: rectangular
        dim = {"tipo": "rect", "largo": res.get("L_total_m", 8.0), "ancho": res.get("W_total_m", 2.0)}
    
    return dim


def obtener_color_unidad(codigo_unidad: str) -> str:
    """Obtiene el color correspondiente a una unidad."""
    colores_map = {
        "rejillas": COLORES["pretratamiento"],
        "desarenador": COLORES["pretratamiento"],
        "uasb": COLORES["tratamiento_primario"],
        "abr": COLORES["tratamiento_primario"],
        "filtro_percolador": COLORES["tratamiento_secundario"],
        "taf": COLORES["tratamiento_secundario"],
        "baf": COLORES["tratamiento_secundario"],
        "humedal_vertical": COLORES["tratamiento_secundario"],
        "sedimentador_secundario": COLORES["sedimentacion"],
        "cloro": COLORES["terciario"],
        "uv": COLORES["terciario"],
        "lecho_secado": COLORES["manejo_lodos"],
    }
    return colores_map.get(codigo_unidad, "#CCCCCC")


# =============================================================================
# GENERADOR DE LAYOUT
# =============================================================================

def generar_layout_tren(
    unidades: List[str],
    resultados: Dict[str, Dict],
    num_lineas: int,
    output_dir: str = "resultados/layouts",
    nombre_archivo: str = "layout_tren.png"
) -> Dict[str, Any]:
    """
    Genera el layout del tren y lo guarda como imagen.
    
    Args:
        unidades: Lista de códigos de unidades en orden
        resultados: Resultados del dimensionamiento por unidad
        num_lineas: Número de líneas paralelas
        output_dir: Directorio de salida
        nombre_archivo: Nombre del archivo de salida
        
    Returns:
        Dict con información del layout generado
    """
    print(f"[Layout] Generando layout para {len(unidades)} unidades...")
    
    # Crear figura
    fig, ax = plt.subplots(figsize=FIGSIZE)
    
    # Calcular posiciones
    x_pos = MARGEN
    y_linea1 = MARGEN + 10  # Línea 1
    y_linea2 = y_linea1 + 15  # Línea 2 (si aplica)
    
    # Dimensiones totales
    max_x = x_pos
    max_y = y_linea1
    
    # Dibujar cada unidad
    posiciones_unidades = {}
    
    for i, codigo_unidad in enumerate(unidades):
        # Obtener dimensiones reales
        dims = obtener_dimensiones_unidad(codigo_unidad, resultados)
        color = obtener_color_unidad(codigo_unidad)
        
        # Calcular posición
        if num_lineas == 2:
            # Dos líneas paralelas
            y_pos = y_linea1 if i % 2 == 0 else y_linea2
        else:
            y_pos = y_linea1
        
        # Dibujar unidad
        if dims["tipo"] == "circ":
            diam = dims["diametro"]
            radio = diam / 2
            circle = Circle((x_pos + radio, y_pos + radio), radio,
                          facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(circle)
            
            # Nombre
            nombre = NOMBRES_DISPLAY.get(codigo_unidad, codigo_unidad.replace('_', '\n'))
            ax.text(x_pos + radio, y_pos + radio, nombre,
                   ha='center', va='center', fontsize=FONT_CONFIG['unidad'], fontweight='bold')
            
            # Acotación
            ax.annotate('', xy=(x_pos + diam, y_pos - 0.6), xytext=(x_pos, y_pos - 0.6),
                       arrowprops=dict(arrowstyle='<->', color='black', lw=1))
            ax.text(x_pos + diam/2, y_pos - 1.1, f'Ø{diam:.1f}m',
                   ha='center', fontsize=FONT_CONFIG['acotacion'])
            
            ancho_unidad = diam
            alto_unidad = diam
            
        else:  # Rectangular
            largo = dims["largo"]
            ancho = dims["ancho"]
            
            rect = Rectangle((x_pos, y_pos), largo, ancho,
                           facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            
            # Nombre
            nombre = NOMBRES_DISPLAY.get(codigo_unidad, codigo_unidad.replace('_', '\n'))
            ax.text(x_pos + largo/2, y_pos + ancho/2, nombre,
                   ha='center', va='center', fontsize=FONT_CONFIG['unidad'], fontweight='bold')
            
            # Acotaciones
            ax.annotate('', xy=(x_pos + largo, y_pos - 0.6), xytext=(x_pos, y_pos - 0.6),
                       arrowprops=dict(arrowstyle='<->', color='black', lw=1))
            ax.text(x_pos + largo/2, y_pos - 1.1, f'{largo:.1f}m',
                   ha='center', fontsize=FONT_CONFIG['acotacion'])
            
            ancho_unidad = largo
            alto_unidad = ancho
        
        # Guardar posición
        posiciones_unidades[codigo_unidad] = {
            "x": x_pos,
            "y": y_pos,
            "ancho": ancho_unidad,
            "alto": alto_unidad,
        }
        
        # Actualizar máximos
        max_x = max(max_x, x_pos + ancho_unidad)
        max_y = max(max_y, y_pos + alto_unidad)
        
        # Avanzar posición X
        x_pos += ancho_unidad + SEP_UNIDADES
    
    # Dibujar flechas de flujo entre unidades
    for i in range(len(unidades) - 1):
        codigo_actual = unidades[i]
        codigo_siguiente = unidades[i + 1]
        
        if codigo_actual in posiciones_unidades and codigo_siguiente in posiciones_unidades:
            pos_actual = posiciones_unidades[codigo_actual]
            pos_siguiente = posiciones_unidades[codigo_siguiente]
            
            # Punto de salida (derecha de unidad actual)
            x1 = pos_actual["x"] + pos_actual["ancho"]
            y1 = pos_actual["y"] + pos_actual["alto"] / 2
            
            # Punto de entrada (izquierda de unidad siguiente)
            x2 = pos_siguiente["x"]
            y2 = pos_siguiente["y"] + pos_siguiente["alto"] / 2
            
            # Dibujar flecha
            dibujar_flecha_flujo(ax, x1, y1, x2, y2)
    
    # Configurar ejes
    ax.set_xlim(0, max_x + MARGEN * 3)
    ax.set_ylim(0, max_y + MARGEN * 3)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Título
    ax.set_title(f"Layout del Tren de Tratamiento", 
                fontsize=FONT_CONFIG['titulo'], fontweight='bold', pad=20)
    
    # Leyenda
    leyenda_items = [
        (COLORES["pretratamiento"], "Pretratamiento"),
        (COLORES["tratamiento_primario"], "Tratamiento Primario"),
        (COLORES["tratamiento_secundario"], "Tratamiento Secundario"),
        (COLORES["sedimentacion"], "Sedimentación"),
        (COLORES["terciario"], "Terciario"),
    ]
    
    leyenda_patches = [mpatches.Patch(color=color, label=label) 
                      for color, label in leyenda_items]
    ax.legend(handles=leyenda_patches, loc='upper right', 
             fontsize=FONT_CONFIG['leyenda'], framealpha=0.9)
    
    # Guardar
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, nombre_archivo)
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"[Layout] Guardado en: {output_path}")
    
    # Calcular área total aproximada
    area_total_m2 = (max_x + MARGEN * 3) * (max_y + MARGEN * 3)
    
    return {
        "ruta_imagen": output_path,
        "dimensiones": {
            "ancho_m": max_x + MARGEN * 3,
            "alto_m": max_y + MARGEN * 3,
            "area_m2": area_total_m2,
        },
        "posiciones_unidades": posiciones_unidades,
        "num_unidades": len(unidades),
    }


# =============================================================================
# MAIN - PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PTAR TREN LAYOUT - Prueba de generación")
    print("=" * 60)
    
    from ptar_tren_config import get_tren_piloto_humedal, TrenConfig
    from ptar_tren_integrador import integrar_tren
    
    # Probar con tren piloto
    print("\n[1] Generando layout para tren piloto:")
    entrada = get_tren_piloto_humedal()
    config = TrenConfig.from_dict(entrada)
    
    # Integrar tren
    resultado = integrar_tren(config)
    
    # Generar layout
    layout = generar_layout_tren(
        unidades=config.unidades,
        resultados=resultado["unidades"],
        num_lineas=config.num_lineas,
        output_dir="resultados/layouts",
        nombre_archivo="layout_tren_humedal.png"
    )
    
    print(f"\n  Layout generado:")
    print(f"    - Ruta: {layout['ruta_imagen']}")
    print(f"    - Dimensiones: {layout['dimensiones']['ancho_m']:.1f}m x {layout['dimensiones']['alto_m']:.1f}m")
    print(f"    - Área: {layout['dimensiones']['area_m2']:.1f} m²")
    print(f"    - Unidades: {layout['num_unidades']}")
    
    print("\n" + "=" * 60)
    print("Generación completada")
    print("=" * 60)
