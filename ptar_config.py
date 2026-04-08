#!/usr/bin/env python3
"""
PTAR CONFIG - Configuración centralizada
Puerto Baquerizo Moreno, Galápagos
"""

from dataclasses import dataclass
from typing import Dict, List
import os

# Directorio base - automáticamente detecta donde está este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# CONFIGURACIÓN DE LAYOUT
# =============================================================================

SEP_UNIDADES = 1.2  # m entre unidades
SEP_LINEAS = 3.0    # m entre líneas paralelas
MARGEN = 2.0        # m margen perimetral

# Lecho compartido (UNA sola celda)
LECHO_LARGO = 6.0   # m
LECHO_ANCHO = 5.0   # m

# Colores por tipo de unidad
COLORES = {
    'pretratamiento': '#FFB6C1',
    'tratamiento_primario': '#90EE90',
    'tratamiento_secundario': '#87CEEB',
    'sedimentacion': '#DDA0DD',
    'terciario': '#F0E68C',
    'manejo_lodos': '#DEB887',
}

# Colores para ranking de alternativas (A-F)
COLORES_TECH = {
    "A": "#2E8B57",  # Verde
    "B": "#4169E1",  # Azul
    "C": "#DAA520",  # Dorado
    "D": "#CD853F",  # Marrón
    "E": "#DC143C",  # Rojo
    "F": "#8A2BE2",  # Púrpura
}

# Dimensiones de todas las unidades
DIMENSIONES = {
    'Rejillas': {'tipo': 'pretratamiento', 'largo': 2.0, 'ancho': 0.9, 'geom': 'rect'},
    'Desarenador': {'tipo': 'pretratamiento', 'largo': 11.2, 'ancho': 1.0, 'geom': 'rect'},
    'Pre_Sedimentador': {'tipo': 'sedimentacion', 'diametro': 5.5, 'geom': 'circ'},
    'UASB': {'tipo': 'tratamiento_primario', 'diametro': 4.8, 'geom': 'circ'},
    'EGSB': {'tipo': 'tratamiento_primario', 'diametro': 1.4, 'geom': 'circ'},
    'Filtro_Percolador': {'tipo': 'tratamiento_secundario', 'diametro': 5.4, 'geom': 'circ'},
    'Biofiltro': {'tipo': 'tratamiento_secundario', 'diametro': 4.5, 'geom': 'circ'},
    'Lodos_Activados': {'tipo': 'tratamiento_secundario', 'largo': 12.0, 'ancho': 8.0, 'geom': 'rect'},
    'Sedimentador_Secundario': {'tipo': 'sedimentacion', 'diametro': 7.0, 'geom': 'circ'},
    'Decantador': {'tipo': 'sedimentacion', 'diametro': 6.0, 'geom': 'circ'},
    'Sedimentador': {'tipo': 'tratamiento_secundario', 'diametro': 4.8, 'geom': 'circ'},
    'UV': {'tipo': 'terciario', 'largo': 3.0, 'ancho': 1.0, 'geom': 'rect'},
    'Cloro': {'tipo': 'terciario', 'largo': 4.2, 'ancho': 1.1, 'geom': 'rect'},
    'Desinfeccion': {'tipo': 'terciario', 'largo': 8.0, 'ancho': 2.0, 'geom': 'rect'},
    'Humedal_Vertical': {'tipo': 'tratamiento_secundario', 'largo': 25.0, 'ancho': 10.0, 'geom': 'rect'},
}

# =============================================================================
# CONFIGURACIÓN DE MATRIZ DE SELECCIÓN
# =============================================================================

@dataclass
class Criterio:
    nombre: str
    peso: float
    tipo: str

CRITERIOS = [
    Criterio("Disponibilidad de Area", 0.15, "min"),
    Criterio("Consumo Energetico", 0.20, "min"),
    Criterio("Complejidad Operativa", 0.15, "min"),
    Criterio("Robustez Hidraulica", 0.12, "max"),
    Criterio("Impacto Ambiental", 0.15, "min"),
    Criterio("Dependencia Importaciones", 0.12, "min"),
    Criterio("Generacion Lodos", 0.08, "min"),
    Criterio("Costo Total 20 anos", 0.03, "min"),
]

TECNOLOGIAS = [
    {"codigo": "A", "nombre": "Alternativa UASB + Filtro Percolador + Cloro",
     "valores": {"Disponibilidad de Area": 7, "Consumo Energetico": 9, "Complejidad Operativa": 8,
                "Robustez Hidraulica": 8, "Impacto Ambiental": 8, "Dependencia Importaciones": 7,
                "Generacion Lodos": 8, "Costo Total 20 anos": 8}, "area": 1834, "energia": 0.021},
    
    {"codigo": "B", "nombre": "EGSB + Filtro Percolador + UV",
     "valores": {"Disponibilidad de Area": 9, "Consumo Energetico": 8, "Complejidad Operativa": 6,
                "Robustez Hidraulica": 8, "Impacto Ambiental": 8, "Dependencia Importaciones": 5,
                "Generacion Lodos": 7, "Costo Total 20 anos": 6}, "area": 1779, "energia": 0.023},
    
    {"codigo": "C", "nombre": "UASB + Humedal Vertical + Cloro",
     "valores": {"Disponibilidad de Area": 3, "Consumo Energetico": 10, "Complejidad Operativa": 9,
                "Robustez Hidraulica": 9, "Impacto Ambiental": 9, "Dependencia Importaciones": 9,
                "Generacion Lodos": 8, "Costo Total 20 anos": 9}, "area": 6377, "energia": 0.012},
    
    {"codigo": "D", "nombre": "Lodos Activados (ASP) + UV",
     "valores": {"Disponibilidad de Area": 4, "Consumo Energetico": 4, "Complejidad Operativa": 5,
                "Robustez Hidraulica": 7, "Impacto Ambiental": 5, "Dependencia Importaciones": 6,
                "Generacion Lodos": 4, "Costo Total 20 anos": 5}, "area": 3500, "energia": 0.045},
    
    {"codigo": "E", "nombre": "Biofiltro (BF) + UV",
     "valores": {"Disponibilidad de Area": 6, "Consumo Energetico": 7, "Complejidad Operativa": 7,
                "Robustez Hidraulica": 7, "Impacto Ambiental": 7, "Dependencia Importaciones": 7,
                "Generacion Lodos": 7, "Costo Total 20 anos": 7}, "area": 2200, "energia": 0.028},
    
    {"codigo": "F", "nombre": "UASB + Biofiltro + UV",
     "valores": {"Disponibilidad de Area": 6, "Consumo Energetico": 8, "Complejidad Operativa": 7,
                "Robustez Hidraulica": 8, "Impacto Ambiental": 8, "Dependencia Importaciones": 7,
                "Generacion Lodos": 7, "Costo Total 20 anos": 7}, "area": 2000, "energia": 0.025},
]

# Configuración de fuentes para layouts (AUMENTADO para mejor visibilidad)
FONT_CONFIG = {
    'unidad': 14,      # Nombres de unidades
    'acotacion': 15,   # Dimensiones
    'entrada': 14,     # Labels "Línea 1/2"
    'leyenda': 16,     # Leyenda
    'titulo': 20,      # Título del layout
}

# Figsize estándar para todos los layouts (AUMENTADO)
FIGSIZE = (28, 18)
