#!/usr/bin/env python3
"""
================================================================================
CLASE BASE PARA GENERADORES LaTeX POR UNIDAD

Define el contrato común que todas las unidades deben implementar.

Formato documental obligatorio (5 secciones):
1. Descripción general y teoría general
2. Parámetros de diseño  
3. Componente - dimensionamiento
4. Componente - verificación
5. Resultados

Ejemplo de implementación:
    class GeneradorRejillas(GeneradorUnidadBase):
        def __init__(self, cfg, resultados_unidad):
            super().__init__(cfg, resultados_unidad)
        
        @property
        def identificador(self) -> str:
            return "rejillas"
        
        @property
        def titulo(self) -> str:
            return "Canal de Desbaste con Rejillas"
        
        @property
        def titulo_corto(self) -> str:
            return "Rejillas"
        
        def generar_descripcion(self) -> str:
            return r"subsection{Descripcion General} Las rejillas..."
        
        # ... y asi para las otras 4 secciones
================================================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ptar_dimensionamiento import ConfigDiseno


class GeneradorUnidadBase(ABC):
    """
    Clase base abstracta para generadores LaTeX de unidades de tratamiento.
    
    Cada unidad (rejillas, desarenador, UASB, humedal, etc.) debe implementar
    esta interfaz para garantizar consistencia documental.
    
    Las 5 secciones obligatorias estan mapeadas a metodos abstractos que 
    deben ser implementados por las subclases.
    """
    
    def __init__(self, cfg: ConfigDiseno, datos: Dict[str, Any]):
        """
        Inicializa el generador con configuracion y datos de la unidad.
        
        Args:
            cfg: Configuracion global del proyecto (ConfigDiseno)
            datos: Resultados del dimensionamiento de esta unidad especifica
        """
        self.cfg = cfg
        self.datos = datos
    
    # ==========================================================================
    # PROPIEDADES OBLIGATORIAS (identificacion)
    # ==========================================================================
    
    @property
    @abstractmethod
    def identificador(self) -> str:
        """
        Identificador unico de la unidad (snake_case).
        
        Ejemplos: "rejillas", "desarenador", "uasb", "humedal_vertical"
        """
        pass
    
    @property
    @abstractmethod
    def titulo(self) -> str:
        """
        Titulo completo de la unidad para el documento.
        
        Ejemplo: "Canal de Desbaste con Rejillas"
        """
        pass
    
    @property
    @abstractmethod
    def titulo_corto(self) -> str:
        """
        Titulo corto para referencias y tablas.
        
        Ejemplo: "Rejillas"
        """
        pass
    
    # ==========================================================================
    # SECCIONES OBLIGATORIAS (Las 5 del formato estandar)
    # ==========================================================================
    
    @abstractmethod
    def generar_descripcion(self) -> str:
        """
        SECCION 1: Descripcion general y teoria general
        
        Debe incluir:
        - Explicacion del funcionamiento de la unidad
        - Marco teorico y principios fisicos/quimicos/biologicos
        - Referencias bibliograficas clave
        - Justificacion de su inclusion en el tren de tratamiento
        
        Returns:
            String LaTeX con la subseccion completa
        """
        pass
    
    @abstractmethod
    def generar_parametros(self) -> str:
        """
        SECCION 2: Parametros de diseno
        
        Debe incluir:
        - Tabla de parametros con: nombre, valor adoptado, rango recomendado, fuente
        - Explicacion de criterios de seleccion
        - Notas sobre condiciones especificas del proyecto
        
        Returns:
            String LaTeX con la subseccion completa
        """
        pass
    
    @abstractmethod
    def generar_dimensionamiento(self) -> str:
        """
        SECCION 3: Componente - dimensionamiento
        
        Debe incluir:
        - Ecuaciones fundamentales
        - Sustitucion de valores
        - Desarrollo paso a paso
        - Dimensiones resultantes
        - Esquemas o figuras cuando aplique
        
        Returns:
            String LaTeX con la subseccion completa
        """
        pass
    
    @abstractmethod
    def generar_verificacion(self) -> str:
        """
        SECCION 4: Componente - verificacion
        
        Debe incluir:
        - Criterios de verificacion aplicables
        - Calculos de condiciones extremas (pico, minimo)
        - Comparacion con limites recomendados
        - Estado de cumplimiento (OK, monitoreo, no admisible)
        
        Returns:
            String LaTeX con la subseccion completa
        """
        pass
    
    @abstractmethod
    def generar_resultados(self) -> str:
        """
        SECCION 5: Resultados
        
        Debe incluir:
        - Tabla resumen de dimensiones finales
        - Parametros clave de operacion
        - Referencias cruzadas a ecuaciones
        - Notas constructivas si aplica
        
        Returns:
            String LaTeX con la subseccion completa
        """
        pass
    
    # ==========================================================================
    # METODOS CONCRETOS (helpers comunes)
    # ==========================================================================
    
    def generar_completo(self, incluir_titulo: bool = True) -> str:
        """
        Genera la unidad completa con las 5 secciones en orden.
        
        Args:
            incluir_titulo: Si True, agrega subsection{titulo} al inicio
        
        Returns:
            String LaTeX con la unidad completa
        """
        partes = []
        
        if incluir_titulo:
            partes.append(r"\subsection{" + self.titulo + "}")
        
        partes.extend([
            self.generar_descripcion(),
            self.generar_parametros(),
            self.generar_dimensionamiento(),
            self.generar_verificacion(),
            self.generar_resultados()
        ])
        
        return "\n\n".join(partes)
    
    def generar_resumen_ejecutivo(self) -> str:
        """
        Genera un parrafo resumen de la unidad para el resumen ejecutivo.
        
        Puede sobrescribirse en subclases para personalizar.
        Por defecto devuelve un placeholder.
        
        Returns:
            String LaTeX con parrafo resumen
        """
        return (
            "La unidad de " + self.titulo_corto + " fue dimensionada "
            "segun criterios establecidos en la literatura tecnica. "
            "Los resultados se detallan en la Seccion " + self.referencia_cruzada + "."
        )
    
    def get_dato(self, clave: str, default: Any = None) -> Any:
        """
        Helper para acceder a datos de la unidad de forma segura.
        
        Args:
            clave: Clave del diccionario datos
            default: Valor por defecto si no existe
        
        Returns:
            Valor del dato o default
        """
        return self.datos.get(clave, default)
    
    def formatear_numero(self, valor: float, decimales: int = 2) -> str:
        """
        Formatea numero para LaTeX (coma decimal, separador de miles).
        
        Args:
            valor: Numero a formatear
            decimales: Cantidad de decimales
        
        Returns:
            String formateado
        """
        if valor is None:
            return "--"
        fmt = f"{{:,.{decimales}f}}"
        resultado = fmt.format(valor)
        # Reemplazar para LaTeX: punto -> coma, coma -> \,
        return resultado.replace(",", "\\\\,").replace(".", ",")
    
    @property
    def referencia_cruzada(self) -> str:
        """
        Genera referencia cruzada LaTeX para esta unidad.
        
        Returns:
            String tipo ref{sec:identificador}
        """
        return "\\\\ref{sec:" + self.identificador + "}"


# ==============================================================================
# EXCEPCION ESPECIFICA DEL PAQUETE
# ==============================================================================

class GeneradorError(Exception):
    """Excepcion base para errores en generadores de unidades."""
    pass


class DatosInsuficientesError(GeneradorError):
    """Error cuando faltan datos necesarios para generar la unidad."""
    pass
