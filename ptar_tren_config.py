#!/usr/bin/env python3
"""
PTAR TREN CONFIG - Configuración y validación de trenes de tratamiento

Este módulo define la estructura de entrada para trenes de tratamiento
individuales. El usuario define el tren mediante un diccionario, no
mediante alternativas fijas A/B/C.

Ejemplo de uso:
    from ptar_tren_config import TrenConfig, validar_config_tren
    
    entrada = {
        "nombre_tren": "Tren UASB + Humedal + Cloro",
        "caudal_total_lps": 10.0,
        "num_lineas": 2,
        "afluente": {
            "DBO5_mg_L": 250.0,
            "DQO_mg_L": 500.0,
            "SST_mg_L": 220.0,
            "CF_NMP_100mL": 1.0e7,
            "temperatura_C": 24.0,
        },
        "unidades": [
            "rejillas",
            "desarenador", 
            "uasb",
            "humedal_vertical",
            "cloro",
            "lecho_secado"
        ]
    }
    
    config = TrenConfig.from_dict(entrada)
    validar_config_tren(config)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import warnings

# =============================================================================
# UNIDADES SOPORTADAS Y SU MAPEO
# =============================================================================

UNIDADES_SOPORTADAS = {
    # Pretratamiento
    "rejillas": {
        "nombre_display": "Rejillas",
        "tipo": "pretratamiento",
        "modulo_dimensionamiento": "dimensionar_rejillas",
        "modulo_latex": "rejillas",
    },
    "desarenador": {
        "nombre_display": "Desarenador",
        "tipo": "pretratamiento", 
        "modulo_dimensionamiento": "dimensionar_desarenador",
        "modulo_latex": "desarenador",
    },
    # Tratamiento primario
    "uasb": {
        "nombre_display": "Reactor UASB",
        "tipo": "tratamiento_primario",
        "modulo_dimensionamiento": "dimensionar_uasb",
        "modulo_latex": "uasb",
    },
    "abr": {
        "nombre_display": "Reactor ABR/RAP",
        "tipo": "tratamiento_primario",
        "modulo_dimensionamiento": "dimensionar_abr_rap",
        "modulo_latex": "abr_rap",
    },
    # Tratamiento secundario
    "filtro_percolador": {
        "nombre_display": "Filtro Percolador",
        "tipo": "tratamiento_secundario",
        "modulo_dimensionamiento": "dimensionar_filtro_percolador",
        "modulo_latex": "filtro_percolador",
    },
    "taf": {
        "nombre_display": "Trickling Filter (TAF)",
        "tipo": "tratamiento_secundario",
        "modulo_dimensionamiento": "dimensionar_biofiltro_carga_mecanizada_hidraulica",
        "modulo_latex": "taf",
    },
    "baf": {
        "nombre_display": "Biofiltro Aireado (BAF)",
        "tipo": "tratamiento_secundario",
        "modulo_dimensionamiento": "dimensionar_baf",
        "modulo_latex": "baf",
    },
    "humedal_vertical": {
        "nombre_display": "Humedal Artificial Vertical",
        "tipo": "tratamiento_secundario",
        "modulo_dimensionamiento": "dimensionar_humedal_vertical",
        "modulo_latex": "humedal_vertical",
    },
    "sedimentador_secundario": {
        "nombre_display": "Sedimentador Secundario",
        "tipo": "sedimentacion",
        "modulo_dimensionamiento": "dimensionar_sedimentador_sec",
        "modulo_latex": "sedimentador_secundario",
    },
    # Terciario / Desinfección
    "cloro": {
        "nombre_display": "Desinfección con Cloro",
        "tipo": "terciario",
        "modulo_dimensionamiento": "dimensionar_desinfeccion_cloro",
        "modulo_latex": "cloro",
    },
    "uv": {
        "nombre_display": "Desinfección UV",
        "tipo": "terciario",
        "modulo_dimensionamiento": "dimensionar_uv",
        "modulo_latex": None,  # No tiene módulo LaTeX aún
    },
    # Manejo de lodos
    "lecho_secado": {
        "nombre_display": "Lecho de Secado",
        "tipo": "manejo_lodos",
        "modulo_dimensionamiento": "dimensionar_lecho_secado",
        "modulo_latex": "lecho_secado",
    },
}

# Secuencias lógicas típicas (orientativas, no restrictivas)
SECUENCIAS_TIPO = {
    "pretratamiento": ["rejillas", "desarenador"],
    "primario": ["uasb", "abr"],
    "secundario": ["filtro_percolador", "taf", "baf", "humedal_vertical"],
    "sedimentacion": ["sedimentador_secundario"],
    "terciario": ["cloro", "uv"],
    "lodos": ["lecho_secado"],
}


# =============================================================================
# ESTRUCTURAS DE DATOS
# =============================================================================

@dataclass
class AfluenteConfig:
    """Configuración del afluente al tren."""
    DBO5_mg_L: float = 250.0
    DQO_mg_L: float = 500.0
    SST_mg_L: float = 220.0
    CF_NMP_100mL: float = 1.0e7
    temperatura_C: float = 24.0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AfluenteConfig":
        """Crea instancia desde diccionario."""
        return cls(
            DBO5_mg_L=data.get("DBO5_mg_L", 250.0),
            DQO_mg_L=data.get("DQO_mg_L", 500.0),
            SST_mg_L=data.get("SST_mg_L", 220.0),
            CF_NMP_100mL=data.get("CF_NMP_100mL", 1.0e7),
            temperatura_C=data.get("temperatura_C", 24.0),
        )


@dataclass  
class TrenConfig:
    """Configuración completa de un tren de tratamiento."""
    nombre_tren: str
    caudal_total_lps: float
    num_lineas: int
    afluente: AfluenteConfig
    unidades: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def caudal_por_linea_lps(self) -> float:
        """Caudal por línea de tratamiento."""
        return self.caudal_total_lps / self.num_lineas
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrenConfig":
        """Crea instancia desde diccionario de entrada."""
        return cls(
            nombre_tren=data.get("nombre_tren", "Tren sin nombre"),
            caudal_total_lps=data.get("caudal_total_lps", 10.0),
            num_lineas=data.get("num_lineas", 2),
            afluente=AfluenteConfig.from_dict(data.get("afluente", {})),
            unidades=data.get("unidades", []),
            metadata=data.get("metadata", {}),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "nombre_tren": self.nombre_tren,
            "caudal_total_lps": self.caudal_total_lps,
            "num_lineas": self.num_lineas,
            "afluente": {
                "DBO5_mg_L": self.afluente.DBO5_mg_L,
                "DQO_mg_L": self.afluente.DQO_mg_L,
                "SST_mg_L": self.afluente.SST_mg_L,
                "CF_NMP_100mL": self.afluente.CF_NMP_100mL,
                "temperatura_C": self.afluente.temperatura_C,
            },
            "unidades": self.unidades,
            "metadata": self.metadata,
        }


# =============================================================================
# FUNCIONES DE VALIDACIÓN
# =============================================================================

def validar_config_tren(config: TrenConfig, strict: bool = False) -> List[str]:
    """
    Valida la configuración de un tren.
    
    Args:
        config: Configuración del tren
        strict: Si True, eleva warnings a errores
        
    Returns:
        Lista de advertencias/errores encontrados
    """
    errores = []
    
    # Validar caudal
    if config.caudal_total_lps <= 0:
        errores.append(f"Caudal total debe ser positivo: {config.caudal_total_lps}")
    
    # Validar número de líneas
    if config.num_lineas < 1:
        errores.append(f"Número de líneas debe ser >= 1: {config.num_lineas}")
    
    # Validar que haya unidades
    if not config.unidades:
        errores.append("El tren debe tener al menos una unidad")
    
    # Validar que las unidades existan
    unidades_desconocidas = []
    for unidad in config.unidades:
        if unidad not in UNIDADES_SOPORTADAS:
            unidades_desconocidas.append(unidad)
    
    if unidades_desconocidas:
        errores.append(f"Unidades no soportadas: {unidades_desconocidas}")
        errores.append(f"Unidades soportadas: {list(UNIDADES_SOPORTADAS.keys())}")
    
    # Validar pretratamiento mínimo (advertencia)
    tiene_rejillas = "rejillas" in config.unidades
    tiene_desarenador = "desarenador" in config.unidades
    
    if not tiene_rejillas:
        msg = "El tren no incluye rejillas (pretratamiento mínimo recomendado)"
        if strict:
            errores.append(msg)
        else:
            warnings.warn(msg, UserWarning)
    
    # Validar desinfección (advertencia)
    tiene_cloro = "cloro" in config.unidades
    tiene_uv = "uv" in config.unidades
    
    if not (tiene_cloro or tiene_uv):
        msg = "El tren no incluye desinfección (requerida por normativa)"
        if strict:
            errores.append(msg)
        else:
            warnings.warn(msg, UserWarning)
    
    return errores


def obtener_info_unidad(codigo_unidad: str) -> Optional[Dict[str, Any]]:
    """Obtiene información de una unidad por su código."""
    return UNIDADES_SOPORTADAS.get(codigo_unidad)


def listar_unidades_por_tipo(tipo: str) -> List[str]:
    """Lista unidades de un tipo específico."""
    return [
        codigo for codigo, info in UNIDADES_SOPORTADAS.items()
        if info["tipo"] == tipo
    ]


# =============================================================================
# EJEMPLOS DE TRENES PILOTO
# =============================================================================

def get_tren_piloto_humedal() -> Dict[str, Any]:
    """Retorna configuración del tren piloto con humedal vertical."""
    return {
        "nombre_tren": "Tren UASB + Humedal Vertical + Cloro",
        "caudal_total_lps": 10.0,
        "num_lineas": 2,
        "afluente": {
            "DBO5_mg_L": 250.0,
            "DQO_mg_L": 500.0,
            "SST_mg_L": 220.0,
            "CF_NMP_100mL": 1.0e7,
            "temperatura_C": 24.0,
        },
        "unidades": [
            "rejillas",
            "desarenador",
            "uasb",
            "humedal_vertical",
            "cloro",
            "lecho_secado"
        ],
        "metadata": {
            "descripcion": "Tren con tratamiento anaerobio + humedal vertical",
            "referencia": "Similar a Alternativa C pero configurable",
        }
    }


def get_tren_piloto_fp() -> Dict[str, Any]:
    """Retorna configuración del tren piloto con filtro percolador."""
    return {
        "nombre_tren": "Tren UASB + Filtro Percolador + Cloro",
        "caudal_total_lps": 10.0,
        "num_lineas": 2,
        "afluente": {
            "DBO5_mg_L": 250.0,
            "DQO_mg_L": 500.0,
            "SST_mg_L": 220.0,
            "CF_NMP_100mL": 1.0e7,
            "temperatura_C": 24.0,
        },
        "unidades": [
            "rejillas",
            "desarenador",
            "uasb",
            "filtro_percolador",
            "sedimentador_secundario",
            "cloro",
            "lecho_secado"
        ],
        "metadata": {
            "descripcion": "Tren con tratamiento anaerobio + filtro percolador",
            "referencia": "Similar a Alternativa A pero configurable",
        }
    }


def get_tren_piloto_baf() -> Dict[str, Any]:
    """Retorna configuración del tren piloto con BAF."""
    return {
        "nombre_tren": "Tren UASB + BAF + Cloro",
        "caudal_total_lps": 10.0,
        "num_lineas": 2,
        "afluente": {
            "DBO5_mg_L": 250.0,
            "DQO_mg_L": 500.0,
            "SST_mg_L": 220.0,
            "CF_NMP_100mL": 1.0e7,
            "temperatura_C": 24.0,
        },
        "unidades": [
            "rejillas",
            "desarenador",
            "uasb",
            "baf",
            "cloro",
            "lecho_secado"
        ],
        "metadata": {
            "descripcion": "Tren con tratamiento anaerobio + biofiltro aireado",
            "nota": "BAF no requiere sedimentador secundario",
        }
    }


# =============================================================================
# MAIN - PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PTAR TREN CONFIG - Validación de configuraciones")
    print("=" * 60)
    
    # Probar tren piloto humedal
    print("\n[1] Tren piloto - Humedal Vertical:")
    entrada = get_tren_piloto_humedal()
    config = TrenConfig.from_dict(entrada)
    print(f"    Nombre: {config.nombre_tren}")
    print(f"    Caudal: {config.caudal_total_lps} L/s ({config.caudal_por_linea_lps} L/s por línea)")
    print(f"    Unidades: {config.unidades}")
    
    errores = validar_config_tren(config)
    if errores:
        print(f"    [!] Advertencias: {errores}")
    else:
        print(f"    [OK] Configuracion valida")
    
    # Probar tren piloto filtro percolador
    print("\n[2] Tren piloto - Filtro Percolador:")
    entrada = get_tren_piloto_fp()
    config = TrenConfig.from_dict(entrada)
    print(f"    Nombre: {config.nombre_tren}")
    print(f"    Unidades: {config.unidades}")
    
    errores = validar_config_tren(config)
    if errores:
        print(f"    [!] Advertencias: {errores}")
    else:
        print(f"    [OK] Configuracion valida")
    
    # Probar tren piloto BAF
    print("\n[3] Tren piloto - BAF:")
    entrada = get_tren_piloto_baf()
    config = TrenConfig.from_dict(entrada)
    print(f"    Nombre: {config.nombre_tren}")
    print(f"    Unidades: {config.unidades}")
    
    errores = validar_config_tren(config)
    if errores:
        print(f"    [!] Advertencias: {errores}")
    else:
        print(f"    [OK] Configuracion valida")
    
    # Listar unidades disponibles
    print("\n[4] Unidades disponibles:")
    for tipo in ["pretratamiento", "tratamiento_primario", "tratamiento_secundario", "terciario", "manejo_lodos"]:
        unidades = listar_unidades_por_tipo(tipo)
        print(f"    {tipo}: {unidades}")
    
    print("\n" + "=" * 60)
    print("Validación completada")
    print("=" * 60)
