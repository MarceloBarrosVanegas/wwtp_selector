#!/usr/bin/env python3
"""
PTAR TREN PREDIO - Cálculo de áreas de tratamiento y predio

Calcula áreas de tratamiento, áreas complementarias y área total del predio
a partir de un layout de tren. Prepara la sección "Disposición de la Planta
y Áreas de Predio".

Uso:
    from ptar_tren_integrador import integrar_tren
    from ptar_tren_layout import generar_layout_tren
    from ptar_tren_predio import calcular_areas_predio
    
    resultado = integrar_tren(config)
    layout = generar_layout_tren(...)
    
    areas = calcular_areas_predio(
        area_tratamiento_m2=layout["dimensiones"]["area_m2"],
        num_unidades=len(config.unidades),
        config_tren=config
    )
"""

import os
import sys
from typing import Dict, Any, List
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ptar_dimensionamiento import ConfigDiseno
from ptar_tren_integrador import crear_config_diseno

# Factores de layout desde ConfigDiseno
def get_layout_factors(cfg: ConfigDiseno = None):
    """Obtiene factores de layout desde configuración."""
    if cfg is None:
        cfg = ConfigDiseno()
    return {
        'amortiguacion': cfg.layout_factor_amortiguacion,
        'complementaria': cfg.layout_factor_complementaria,
        'zona_verde': cfg.layout_factor_zona_verde,
        'caminos': cfg.layout_factor_caminos,
        'min_bodega': cfg.layout_area_min_bodega_quimicos_m2,
        'min_laboratorio': cfg.layout_area_min_laboratorio_m2,
        'min_caseta': cfg.layout_area_min_caseta_operacion_m2,
        'min_estacionamiento': cfg.layout_area_min_estacionamiento_m2,
        'min_camiones': cfg.layout_area_min_zona_camiones_m2,
    }
from ptar_tren_config import TrenConfig


# =============================================================================
# ESTRUCTURAS DE DATOS
# =============================================================================

@dataclass
class AreaComplementaria:
    """Representa un área complementaria del predio."""
    nombre: str
    area_m2: float
    criterio: str  # Descripción del cálculo
    tipo: str      # 'minima', 'factor', 'adoptada'


# =============================================================================
# FUNCIONES DE CÁLCULO
# =============================================================================

def calcular_areas_complementarias(
    area_tratamiento_m2: float,
    num_unidades: int,
    cfg: ConfigDiseno = None
) -> List[AreaComplementaria]:
    """
    Calcula las áreas complementarias del predio.
    
    Args:
        area_tratamiento_m2: Área ocupada por las unidades de tratamiento
        num_unidades: Número de unidades en el tren
        cfg: Configuración de diseño (opcional)
        
    Returns:
        Lista de áreas complementarias
    """
    factors = get_layout_factors(cfg)
    areas = []
    
    # Área de amortiguación (zona de seguridad alrededor de tratamiento)
    area_amortiguacion = area_tratamiento_m2 * factors['amortiguacion']
    areas.append(AreaComplementaria(
        nombre="Zona de amortiguación",
        area_m2=area_amortiguacion,
        criterio=f"{factors['amortiguacion']*100:.0f}% del área de tratamiento",
        tipo="factor"
    ))
    
    # Área complementaria (bodegas, laboratorio, caseta)
    area_complementaria = area_tratamiento_m2 * factors['complementaria']
    areas.append(AreaComplementaria(
        nombre="Áreas complementarias (bodegas, laboratorio, caseta)",
        area_m2=area_complementaria,
        criterio=f"{factors['complementaria']*100:.0f}% del área de tratamiento",
        tipo="factor"
    ))
    
    # Caminos y vías internas
    area_caminos = area_tratamiento_m2 * factors['caminos']
    areas.append(AreaComplementaria(
        nombre="Caminos y vías internas",
        area_m2=area_caminos,
        criterio=f"{factors['caminos']*100:.0f}% del área de tratamiento",
        tipo="factor"
    ))
    
    # Zona verde
    area_verde = area_tratamiento_m2 * factors['zona_verde']
    areas.append(AreaComplementaria(
        nombre="Zona verde y paisajismo",
        area_m2=area_verde,
        criterio=f"{factors['zona_verde']*100:.0f}% del área de tratamiento",
        tipo="factor"
    ))
    
    # Áreas mínimas específicas
    areas_minimas = [
        ("Bodega de químicos", factors['min_bodega']),
        ("Laboratorio", factors['min_laboratorio']),
        ("Caseta de operación", factors['min_caseta']),
        ("Estacionamiento", factors['min_estacionamiento']),
        ("Zona de maniobra de camiones", factors['min_camiones']),
    ]
    
    for nombre, area_min in areas_minimas:
        areas.append(AreaComplementaria(
            nombre=nombre,
            area_m2=area_min,
            criterio=f"Área mínima constructiva",
            tipo="minima"
        ))
    
    return areas


def calcular_areas_predio(
    area_tratamiento_m2: float,
    num_unidades: int,
    config_tren: TrenConfig,
    factor_total: float = 1.35  # Factor de expansión total del predio
) -> Dict[str, Any]:
    """
    Calcula todas las áreas del predio para un tren.
    
    Args:
        area_tratamiento_m2: Área ocupada por unidades de tratamiento
        num_unidades: Número de unidades
        config_tren: Configuración del tren
        factor_total: Factor de expansión total (tratamiento + complementarias)
        
    Returns:
        Dict con desglose completo de áreas
    """
    print(f"[Predio] Calculando áreas para tren: {config_tren.nombre_tren}")
    
    # Áreas complementarias
    areas_complementarias = calcular_areas_complementarias(
        area_tratamiento_m2, num_unidades
    )
    
    # Sumar áreas complementarias
    area_complementaria_total = sum(a.area_m2 for a in areas_complementarias)
    
    # Área total de predio (tratamiento + complementarias con factor)
    area_subtotal = area_tratamiento_m2 + area_complementaria_total
    area_total_predio = area_subtotal * factor_total
    
    # Margen para expansión futura
    area_expansion = area_total_predio * 0.10  # 10% adicional
    
    resultado = {
        "area_tratamiento_m2": area_tratamiento_m2,
        "area_tratamiento_ha": area_tratamiento_m2 / 10000,
        
        "areas_complementarias": [
            {
                "nombre": a.nombre,
                "area_m2": a.area_m2,
                "area_ha": a.area_m2 / 10000,
                "criterio": a.criterio,
                "tipo": a.tipo,
            }
            for a in areas_complementarias
        ],
        
        "area_complementaria_total_m2": area_complementaria_total,
        "area_complementaria_total_ha": area_complementaria_total / 10000,
        
        "area_subtotal_m2": area_subtotal,
        "area_subtotal_ha": area_subtotal / 10000,
        
        "factor_expansion_predio": factor_total,
        "area_total_predio_m2": area_total_predio,
        "area_total_predio_ha": area_total_predio / 10000,
        
        "area_expansion_futura_m2": area_expansion,
        "area_expansion_futura_ha": area_expansion / 10000,
        
        "resumen": {
            "tratamiento_ha": round(area_tratamiento_m2 / 10000, 2),
            "complementarias_ha": round(area_complementaria_total / 10000, 2),
            "total_predio_ha": round(area_total_predio / 10000, 2),
        }
    }
    
    print(f"[Predio] Áreas calculadas:")
    print(f"  - Tratamiento: {resultado['resumen']['tratamiento_ha']:.2f} ha")
    print(f"  - Complementarias: {resultado['resumen']['complementarias_ha']:.2f} ha")
    print(f"  - Total predio: {resultado['resumen']['total_predio_ha']:.2f} ha")
    
    return resultado


def generar_tabla_areas_latex(areas: Dict[str, Any]) -> str:
    """
    Genera la tabla de áreas en formato LaTeX.
    
    Args:
        areas: Resultado de calcular_areas_predio()
        
    Returns:
        Código LaTeX de la tabla
    """
    lineas = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Desglose de áreas del predio}",
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r"\textbf{Descripción} & \textbf{m²} & \textbf{ha} \\",
        r"\midrule",
    ]
    
    # Área de tratamiento
    lineas.append(f"Área de tratamiento & {areas['area_tratamiento_m2']:,.0f} & {areas['resumen']['tratamiento_ha']:.2f} \\\\")
    lineas.append(r"\midrule")
    
    # Áreas complementarias
    for comp in areas['areas_complementarias'][:5]:  # Primeras 5 principales
        lineas.append(f"{comp['nombre']} & {comp['area_m2']:,.0f} & {comp['area_ha']:.2f} \\\\")
    
    lineas.append(r"\midrule")
    lineas.append(f"Subtotal áreas & {areas['area_subtotal_m2']:,.0f} & {areas['resumen']['complementarias_ha']:.2f} \\\\")
    lineas.append(f"Factor de expansión predio & \multicolumn{{2}}{{c}}{{×{areas['factor_expansion_predio']:.2f}}} \\\\")
    lineas.append(r"\midrule")
    lineas.append(f"\textbf{{Área total del predio}} & \textbf{{{areas['area_total_predio_m2']:,.0f}}} & \textbf{{{areas['resumen']['total_predio_ha']:.2f}}} \\\\")
    lineas.append(r"\bottomrule")
    lineas.append(r"\end{tabular}")
    lineas.append(r"\end{table}")
    
    return "\n".join(lineas)


# =============================================================================
# MAIN - PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PTAR TREN PREDIO - Prueba de cálculo de áreas")
    print("=" * 60)
    
    from ptar_tren_config import get_tren_piloto_humedal, TrenConfig
    from ptar_tren_integrador import integrar_tren
    from ptar_tren_layout import generar_layout_tren
    
    # Configurar tren piloto
    entrada = get_tren_piloto_humedal()
    config = TrenConfig.from_dict(entrada)
    
    # Integrar y generar layout
    resultado = integrar_tren(config)
    layout = generar_layout_tren(
        unidades=config.unidades,
        resultados=resultado["unidades"],
        num_lineas=config.num_lineas,
        output_dir="resultados/layouts",
        nombre_archivo="layout_predio_test.png"
    )
    
    # Calcular áreas
    print("\n[1] Calculando áreas del predio:")
    areas = calcular_areas_predio(
        area_tratamiento_m2=layout["dimensiones"]["area_m2"],
        num_unidades=len(config.unidades),
        config_tren=config
    )
    
    # Generar tabla LaTeX
    print("\n[2] Tabla LaTeX generada:")
    tabla_latex = generar_tabla_areas_latex(areas)
    print(tabla_latex[:500] + "...")
    
    print("\n" + "=" * 60)
    print("Cálculo completado")
    print("=" * 60)
