#!/usr/bin/env python3
"""
================================================================================
PAQUETE: latex_unidades

Generadores LaTeX modulares por unidad de tratamiento.

Cada unidad implementa la interfaz GeneradorUnidadBase con las 5 secciones:
1. Descripción general y teoría general
2. Parámetros de diseño
3. Componente - dimensionamiento
4. Componente - verificación
5. Resultados

Uso:
    from latex_unidades import GeneradorUnidadBase
    from latex_unidades.rejillas import GeneradorRejillas
    
    generador = GeneradorRejillas(cfg, resultados['rejillas'])
    latex_completo = generador.generar_completo()
    
    # O solo una sección:
    latex_desc = generador.generar_descripcion()

Arquitectura:
    - Base: clase abstracta con contrato común
    - Implementaciones: una por unidad
    - Ensamblador: puede combinar unidades arbitrarias
================================================================================
"""

from .base import GeneradorUnidadBase
from .rejillas import GeneradorRejillas
from .desarenador import GeneradorDesarenador
from .uasb import GeneradorUASB
from .filtro_percolador import GeneradorFiltroPercolador
from .sedimentador_secundario import GeneradorSedimentadorSecundario
from .cloro import GeneradorCloro

__all__ = ['GeneradorUnidadBase', 'GeneradorRejillas', 'GeneradorDesarenador', 'GeneradorUASB', 'GeneradorFiltroPercolador', 'GeneradorSedimentadorSecundario', 'GeneradorCloro']
