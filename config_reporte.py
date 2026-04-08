"""
Configuración central del reporte de selección de alternativas.

Aquí defines qué alternativas incluir en el documento final.
Cada alternativa puede tener opciones adicionales.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConfigAlternativa:
    """Configuración para una alternativa específica."""
    incluir: bool                      # ¿Incluir en el reporte?
    caudal_lps: float                  # Caudal por línea (L/s)
    nombre: str                        # Nombre descriptivo
    descripcion: Optional[str] = None  # Descripción corta


# ============================================================================
# CONFIGURACIÓN PRINCIPAL - Edita aquí qué alternativas incluir
# ============================================================================

CONFIG_REPORTE = {
    # Información general del proyecto
    "proyecto": {
        "nombre": "Planta de Tratamiento de Aguas Residuales",
        "ubicacion": "Por definir",
        "caudal_total_lps": 10.0,
        "dias_diseno": 20,
    },
    
    # Selección de alternativas a incluir
    "alternativas": {
        # Alternativa A: UASB + Filtro Percolador
        "A": ConfigAlternativa(
            incluir=True,
            caudal_lps=5.0,
            nombre="Alternativa UASB + Filtro Percolador + Cloro",
            descripcion="Tratamiento primario anaerobio UASB + tratamiento secundario con filtro percolador de piedra graduada"
        ),
        
        # Alternativa B: UASB + MBBR
        "B": ConfigAlternativa(
            incluir=False,  # Cambiar a True cuando esté implementada
            caudal_lps=5.0,
            nombre="UASB + MBBR + Sedimentación",
            descripcion="Tratamiento primario UASB + reactor biológico de lecho móvil (MBBR)"
        ),
        
        # Alternativa C: UASB + Humedal Vertical
        "C": ConfigAlternativa(
            incluir=False,
            caudal_lps=5.0,
            nombre="UASB + Humedal Vertical + Cloro",
            descripcion="Tratamiento primario UASB + humedal vertical de flujo subsuperficial + desinfeccion con cloro"
        ),
        
        # Alternativa D: Lodos Activados (Aireación Extendida)
        "D": ConfigAlternativa(
            incluir=False,
            caudal_lps=5.0,
            nombre="Lodos Activados (Aireación Extendida)",
            descripcion="Sistema convencional de lodos activados con aireación extendida"
        ),
        
        # Alternativa E: Reactor Anaerobio de Flujo Ascendente + Humedal
        "E": ConfigAlternativa(
            incluir=False,
            caudal_lps=5.0,
            nombre="UASB + Humedal Artificial",
            descripcion="Tratamiento primario UASB + tratamiento terciario en humedal artificial"
        ),
        
        # Alternativa F: SBR (Sequencing Batch Reactor)
        "F": ConfigAlternativa(
            incluir=False,
            caudal_lps=5.0,
            nombre="Reactor por Lotes (SBR)",
            descripcion="Reactor biológico secuencial por lotes (SBR)"
        ),
    },
    
    # Secciones adicionales del reporte
    "secciones": {
        "portada": True,
        "introduccion": True,
        "bases_diseno": True,
        "caracterizacion_agua": True,
        "matriz_comparativa": True,      # Tabla comparando alternativas
        "analisis_costos": False,        # Análisis preliminar de costos
        "seleccion_final": True,         # Justificación de la selección
        "conclusiones": True,
    },
    
    # Configuración de salida
    "salida": {
        "nombre_archivo": "Seleccion_Alternativas_PTAR",
        "incluir_layouts": True,
        "calidad_imagen_dpi": 300,
    }
}


def obtener_alternativas_activas():
    """Retorna lista de IDs de alternativas marcadas para incluir."""
    return [
        alt_id 
        for alt_id, config in CONFIG_REPORTE["alternativas"].items() 
        if config.incluir
    ]


def verificar_configuracion():
    """Verifica que la configuración sea válida."""
    activas = obtener_alternativas_activas()
    
    if not activas:
        raise ValueError("¡Error! No hay alternativas seleccionadas en config_reporte.py")
    
    print(f"Alternativas activas: {', '.join(activas)}")
    print(f"Total de secciones a generar: {sum(CONFIG_REPORTE['secciones'].values())}")
    
    return activas


if __name__ == "__main__":
    # Test de configuración
    print("="*60)
    print("CONFIGURACIÓN DEL REPORTE")
    print("="*60)
    verificar_configuracion()
    print("\nDetalle de alternativas seleccionadas:")
    for alt_id, config in CONFIG_REPORTE["alternativas"].items():
        if config.incluir:
            print(f"  [{alt_id}] {config.nombre}")
            print(f"      -> {config.descripcion}")
