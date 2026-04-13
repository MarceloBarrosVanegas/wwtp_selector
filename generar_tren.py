#!/usr/bin/env python3
"""
GENERADOR TREN SIMPLE - Genera un documento LaTeX para un tren personalizado

Uso simple:
    from generar_tren_simple import generar_documento_tren
    
    entrada = {
        "nombre_tren": "Mi Tren Personalizado",
        "caudal_total_lps": 17.0,
        "num_lineas": 3,
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
    
    generar_documento_tren(entrada, output_dir="resultados/mis_trenes")
"""

import os
import sys
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar dimensionadores
from ptar_dimensionamiento import (
    ConfigDiseno,
    dimensionar_rejillas,
    dimensionar_desarenador,
    dimensionar_uasb,
    dimensionar_humedal_vertical,
    dimensionar_desinfeccion_cloro,
    dimensionar_lecho_secado,
)

# Importar generadores LaTeX
from latex_unidades.rejillas import GeneradorRejillas
from latex_unidades.desarenador import GeneradorDesarenador
from latex_unidades.uasb import GeneradorUASB
from latex_unidades.humedal_vertical import GeneradorHumedalVertical
from latex_unidades.cloro import GeneradorCloro
from latex_unidades.lecho_secado import GeneradorLechoSecado


# =============================================================================
# BIBLIOGRAFIA
# =============================================================================

def _generar_bibliografia(output_dir):
    """Genera el archivo .bib con las referencias bibliograficas"""
    bib_content = r'''%% Archivo de referencias bibliograficas
%% Generado automaticamente

@book{metcalf2014,
    author    = {Metcalf and Eddy, Inc.},
    title     = {Wastewater Engineering: Treatment and Resource Recovery},
    edition   = {5th},
    publisher = {McGraw-Hill Education},
    year      = {2014},
    address   = {New York, NY},
    isbn      = {978-0073401188}
}

@techreport{ops2005,
    author      = {{OPS/CEPIS}},
    title       = {Guia para el diseno de plantas de tratamiento de aguas residuales},
    institution = {Organizacion Panamericana de la Salud / Centro Panamericano de Ingenieria Sanitaria y Ciencias del Ambiente},
    year        = {2005},
    address     = {Lima, Peru},
    type        = {Guia Tecnica}
}

@techreport{senagua2012,
    author      = {{SENAGUA}},
    title       = {Normativa para el diseno de sistemas de tratamiento de aguas residuales},
    institution = {Secretaria Nacional del Agua del Ecuador},
    year        = {2012},
    address     = {Quito, Ecuador},
    type        = {Norma Tecnica}
}

@book{vanhaandel1994,
    author    = {Van Haandel, A. C. and Lettinga, G.},
    title     = {Anaerobic Sewage Treatment: A Practical Guide for Regions with a Hot Climate},
    publisher = {John Wiley & Sons},
    year      = {1994},
    address   = {Chichester, UK},
    isbn      = {978-0471951055}
}

@book{sperling2007,
    author    = {von Sperling, M.},
    title     = {Activated Sludge and Aerobic Biofilm Reactors},
    series    = {Biological Wastewater Treatment Series},
    volume    = {5},
    publisher = {IWA Publishing},
    year      = {2007},
    address   = {London, UK},
    isbn      = {978-1843391651}
}

@book{chernicharo2007,
    author    = {Chernicharo, C. A. L.},
    title     = {Biological Wastewater Treatment in Warm Climate Regions},
    volume    = {2},
    publisher = {IWA Publishing},
    year      = {2007},
    address   = {London, UK},
    isbn      = {978-1843391613}
}

@book{wef_mop8_2010,
    author    = {{Water Environment Federation}},
    title     = {Design of Municipal Wastewater Treatment Plants},
    edition   = {5th},
    series    = {Manual of Practice No. 8},
    publisher = {McGraw-Hill Education},
    year      = {2010},
    address   = {New York, NY},
    isbn      = {978-0071663601}
}

@techreport{usepa2003,
    author      = {{U.S. Environmental Protection Agency}},
    title       = {Manual de Disinfeccion de Aguas Residuales},
    institution = {EPA},
    year        = {2003},
    address     = {Washington, DC},
    type        = {Manual Tecnico}
}
'''
    bib_path = os.path.join(output_dir, 'referencias.bib')
    with open(bib_path, 'w', encoding='utf-8') as f:
        f.write(bib_content)
    return bib_path


# =============================================================================
# CONFIGURACION DEL TREN
# =============================================================================

@dataclass
class ConfigTren:
    """Configuracion simple de un tren."""
    nombre: str
    caudal_lps: float
    num_lineas: int
    dbo: float
    dqo: float
    sst: float
    cf: float
    temperatura: float
    unidades: List[str]
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ConfigTren":
        afluente = data.get("afluente", {})
        return cls(
            nombre=data.get("nombre_tren", "Tren sin nombre"),
            caudal_lps=data.get("caudal_total_lps", 10.0),
            num_lineas=data.get("num_lineas", 2),
            dbo=afluente.get("DBO5_mg_L", 250.0),
            dqo=afluente.get("DQO_mg_L", 500.0),
            sst=afluente.get("SST_mg_L", 220.0),
            cf=afluente.get("CF_NMP_100mL", 1.0e7),
            temperatura=afluente.get("temperatura_C", 24.0),
            unidades=data.get("unidades", []),
        )


# =============================================================================
# MAPEO DE UNIDADES
# =============================================================================

DIMENSIONADORES = {
    "rejillas": dimensionar_rejillas,
    "desarenador": dimensionar_desarenador,
    "uasb": dimensionar_uasb,
    "humedal_vertical": dimensionar_humedal_vertical,
    "cloro": dimensionar_desinfeccion_cloro,
    "lecho_secado": dimensionar_lecho_secado,
}

GENERADORES_LATEX = {
    "rejillas": GeneradorRejillas,
    "desarenador": GeneradorDesarenador,
    "uasb": GeneradorUASB,
    "humedal_vertical": GeneradorHumedalVertical,
    "cloro": GeneradorCloro,
    "lecho_secado": GeneradorLechoSecado,
}

NOMBRES_UNIDADES = {
    "rejillas": "Canal de Desbaste con Rejillas",
    "desarenador": "Desarenador de Flujo Horizontal",
    "uasb": "Reactor Anaerobio de Flujo Ascendente con Manto de Lodos (UASB)",
    "humedal_vertical": "Humedal Artificial de Flujo Vertical (HAFV)",
    "cloro": "Sistema de Desinfeccion con Hipoclorito de Sodio",
    "lecho_secado": "Lechos de Secado de Lodos",
}


# =============================================================================
# FUNCIONES PRINCIPALES
# =============================================================================

def crear_configuracion(cfg_tren: ConfigTren) -> ConfigDiseno:
    """Crea ConfigDiseno a partir de ConfigTren."""
    cfg = ConfigDiseno()
    cfg.Q_total_L_s = cfg_tren.caudal_lps
    cfg.Q_linea_L_s = cfg_tren.caudal_lps / cfg_tren.num_lineas
    cfg.num_lineas = cfg_tren.num_lineas
    cfg.DBO5_mg_L = cfg_tren.dbo
    cfg.DQO_mg_L = cfg_tren.dqo
    cfg.SST_mg_L = cfg_tren.sst
    cfg.CF_NMP = cfg_tren.cf
    cfg.T_agua_C = cfg_tren.temperatura
    
    # Recalcular valores derivados del caudal (que se calculan en __post_init__)
    # ya que al cambiar Q_linea_L_s despues de crear el objeto, estos no se actualizan
    cfg.Q_linea_m3_d = cfg.Q_linea_L_s * 86.4
    cfg.Q_total_m3_d = cfg.Q_total_L_s * 86.4
    cfg.Q_linea_m3_h = cfg.Q_linea_m3_d / 24.0
    cfg.Q_linea_m3_s = cfg.Q_linea_L_s / 1000.0
    
    return cfg


def dimensionar_tren(cfg_tren: ConfigTren) -> Dict[str, Any]:
    """Dimensiona todas las unidades del tren."""
    print(f"\nDimensionando tren: {cfg_tren.nombre}")
    print(f"Caudal: {cfg_tren.caudal_lps} L/s en {cfg_tren.num_lineas} lineas")
    
    cfg = crear_configuracion(cfg_tren)
    resultados = {}
    
    # Acumulador de lodos para lecho de secado
    lodos_total_kg_SST_d = 0.0
    desglose_lodos = []  # Lista de diccionarios con origen y cantidad
    
    for unidad in cfg_tren.unidades:
        print(f"  - {unidad}...", end=" ")
        if unidad in DIMENSIONADORES:
            try:
                # Para humedal necesitamos DBO de entrada
                if unidad == "humedal_vertical":
                    resultado = DIMENSIONADORES[unidad](cfg, DBO_entrada_mg_L=cfg_tren.dbo * 0.30)
                # Para cloro necesitamos CF de entrada
                elif unidad == "cloro":
                    resultado = DIMENSIONADORES[unidad](cfg, CF_entrada_NMP=cfg_tren.cf)
                # Para lecho de secado necesitamos los lodos acumulados
                elif unidad == "lecho_secado":
                    if lodos_total_kg_SST_d > 0:
                        resultado = DIMENSIONADORES[unidad](cfg, lodos_kg_SST_d=lodos_total_kg_SST_d)
                        # Actualizar el desglose con información real de las unidades
                        if desglose_lodos:
                            filas_desglose = []
                            for item in desglose_lodos:
                                filas_desglose.append({
                                    "origen": item["nombre"],
                                    "por_linea_kg_d": round(item["kg_SST_d"] / cfg.num_lineas, 2),
                                    "total_kg_d": round(item["kg_SST_d"], 2)
                                })
                            resultado["desglose_lodos"] = filas_desglose
                    else:
                        raise ValueError("No se han acumulado lodos de las unidades anteriores para dimensionar el lecho de secado")
                else:
                    resultado = DIMENSIONADORES[unidad](cfg)
                resultados[unidad] = resultado
                
                # Acumular lodos de cada unidad (excepto lecho de secado que los recibe)
                if unidad != "lecho_secado":
                    lodos_unidad = extraer_lodos_unidad(resultado, unidad)
                    if lodos_unidad > 0:
                        lodos_total_kg_SST_d += lodos_unidad
                        # Agregar al desglose
                        nombre_unidad = NOMBRES_UNIDADES.get(unidad, unidad)
                        desglose_lodos.append({
                            "unidad": unidad,
                            "nombre": nombre_unidad,
                            "kg_SST_d": lodos_unidad
                        })
                        print(f"OK (lodos: {lodos_unidad:.1f} kg SST/d)")
                    else:
                        print("OK")
                else:
                    print("OK")
            except Exception as e:
                print(f"ERROR: {e}")
                resultados[unidad] = {"error": str(e)}
        else:
            print("NO SOPORTADA")
            resultados[unidad] = {"error": "Unidad no soportada"}
    
    # Si hay lecho de secado en el tren, pasarle los lodos acumulados
    if "lecho_secado" in cfg_tren.unidades and lodos_total_kg_SST_d > 0:
        print(f"\n  Total lodos para lecho de secado: {lodos_total_kg_SST_d:.2f} kg SST/d")
        # Guardar para usar cuando se dimensione el lecho
        resultados["_lodos_acumulados_kg_SST_d"] = lodos_total_kg_SST_d
        # Guardar también el desglose por unidad
        resultados["_desglose_lodos"] = desglose_lodos
    
    return resultados


def extraer_lodos_unidad(resultado: Dict, unidad: str) -> float:
    """
    Extrae la producción de lodos (kg SST/d) del resultado de una unidad.
    Busca recursivamente en todo el diccionario para encontrar valores de lodos.
    """
    lodos_kg_d = 0.0
    
    # Campos específicos conocidos por nombre
    campos_directos = [
        "lodos_kg_SST_d",
        "lodos_total_kg_d",
        "solidos_humus_kg_d",
        "solidos_biologicos_kg_d",
        "produccion_humus_kg_d",
        "lodos_kg_SSV_d",
    ]
    
    for campo in campos_directos:
        if campo in resultado and resultado[campo]:
            valor = resultado[campo]
            # Si es SSV, convertir a SST (asumir 80% SSV/SST típico)
            if "SSV" in campo:
                valor = valor / 0.80
            lodos_kg_d += valor
    
    # Si no encontramos directamente, buscar en estructura "lodos"
    if "lodos" in resultado and isinstance(resultado["lodos"], list):
        for item in resultado["lodos"]:
            if isinstance(item, dict):
                # Buscar kg_SST_d, kg_d, kg_SSV_d
                if "kg_SST_d" in item:
                    lodos_kg_d += item.get("kg_SST_d", 0)
                elif "kg_d" in item and "SSV" not in str(item):
                    lodos_kg_d += item.get("kg_d", 0)
                elif "kg_SSV_d" in item:
                    lodos_kg_d += item.get("kg_SSV_d", 0) / 0.80
    
    # Si aún no hay nada, hacer búsqueda recursiva en todo el dict
    if lodos_kg_d == 0:
        lodos_kg_d = _buscar_lodos_recursivo(resultado)
    
    return lodos_kg_d


def _buscar_lodos_recursivo(obj, profundidad_max=3, profundidad=0):
    """
    Búsqueda recursiva de valores de lodos en cualquier estructura de datos.
    Busca claves que contengan 'lodos', 'solidos', 'produccion' + 'kg'
    """
    if profundidad >= profundidad_max:
        return 0.0
    
    total = 0.0
    
    if isinstance(obj, dict):
        for clave, valor in obj.items():
            clave_lower = str(clave).lower()
            # Si la clave parece ser de lodos
            if any(x in clave_lower for x in ["lodos", "solidos", "produccion", "humus"]):
                if isinstance(valor, (int, float)) and valor > 0:
                    # Convertir SSV a SST si es necesario
                    if "ssv" in clave_lower:
                        total += valor / 0.80
                    else:
                        total += valor
                elif isinstance(valor, (dict, list)):
                    total += _buscar_lodos_recursivo(valor, profundidad_max, profundidad + 1)
            # También buscar dentro de sub-estructuras
            elif isinstance(valor, (dict, list)):
                total += _buscar_lodos_recursivo(valor, profundidad_max, profundidad + 1)
    
    elif isinstance(obj, list):
        for item in obj:
            total += _buscar_lodos_recursivo(item, profundidad_max, profundidad + 1)
    
    return total


def generar_latex_unidad(unidad: str, resultado: Dict, cfg: ConfigDiseno, figuras_dir: str) -> str:
    """Genera el LaTeX para una unidad, convirtiendo subsections internos a subsubsections."""
    if unidad not in GENERADORES_LATEX:
        return f"\\subsubsection{{{NOMBRES_UNIDADES.get(unidad, unidad)}}}\nUnidad no disponible en LaTeX.\n\n"
    
    try:
        generador_class = GENERADORES_LATEX[unidad]
        # Pasar ruta de figuras al generador
        generador = generador_class(cfg, resultado, ruta_figuras='figuras')
        contenido = generador.generar_completo()
        
        # Convertir \subsection a \subsubsection para que no aparezcan en el indice
        # Esto hace que Dimensionamiento, Verificacion, Resultados sean 1.1.1, 1.1.2, etc.
        contenido = contenido.replace(r'\subsection{', r'\subsubsection{')
        contenido = contenido.replace(r'\subsection*{', r'\subsubsection*{')
        
        return contenido
    except Exception as e:
        return f"\\subsubsection{{{NOMBRES_UNIDADES.get(unidad, unidad)}}}\nError: {e}\n\n"


def generar_documento_tren(
    entrada: Dict,
    output_dir: str = "resultados/trenes",
    nombre_archivo: Optional[str] = None,
    compilar_pdf: bool = False
) -> str:
    """
    Genera un documento LaTeX completo para el tren.
    
    Args:
        entrada: Diccionario con configuracion del tren
        output_dir: Directorio de salida
        nombre_archivo: Nombre del archivo (sin extension)
        compilar_pdf: Si True, intenta compilar a PDF
        
    Returns:
        Ruta al archivo .tex generado
    """
    # Crear configuracion
    cfg_tren = ConfigTren.from_dict(entrada)
    cfg = crear_configuracion(cfg_tren)
    
    # Dimensionar
    resultados = dimensionar_tren(cfg_tren)
    
    # Crear directorios: principal y figuras
    os.makedirs(output_dir, exist_ok=True)
    figuras_dir = os.path.join(output_dir, "figuras")
    os.makedirs(figuras_dir, exist_ok=True)
    
    # Generar nombre de archivo
    if nombre_archivo is None:
        nombre_archivo = cfg_tren.nombre.lower().replace(" ", "_").replace("+", "_")
    
    tex_path = os.path.join(output_dir, f"{nombre_archivo}.tex")
    
    # Generar documento LaTeX
    print(f"\nGenerando documento LaTeX: {tex_path}")
    
    # Encabezado
    latex_parts = []
    latex_parts.append(r"\documentclass[12pt,a4paper]{article}")
    latex_parts.append(r"\usepackage[utf8]{inputenc}")
    latex_parts.append(r"\usepackage[spanish]{babel}")
    latex_parts.append(r"\usepackage{geometry}")
    latex_parts.append(r"\usepackage{amsmath}")
    latex_parts.append(r"\usepackage{amssymb}")
    latex_parts.append(r"\usepackage{booktabs}")
    latex_parts.append(r"\usepackage{longtable}")
    latex_parts.append(r"\usepackage{graphicx}")
    latex_parts.append(r"\usepackage{enumitem}")
    latex_parts.append(r"\usepackage{float}")
    latex_parts.append(r"\usepackage{xcolor}")
    latex_parts.append(r"\usepackage{fancyhdr}")
    latex_parts.append(r"\usepackage{caption}")
    latex_parts.append(r"\usepackage[numbers]{natbib}")
    latex_parts.append(r"\usepackage[colorlinks=true,linkcolor=black,citecolor=blue,urlcolor=blue]{hyperref}")
    latex_parts.append("")
    latex_parts.append(r"\geometry{margin=2.5cm}")
    latex_parts.append("")
    latex_parts.append(r"\pagestyle{fancy}")
    latex_parts.append(r"\fancyhf{}")
    latex_parts.append(r"\fancyhead[L]{" + cfg_tren.nombre + r"}")
    latex_parts.append(r"\fancyhead[R]{\thepage}")
    latex_parts.append("")
    latex_parts.append(r"\setcounter{tocdepth}{2}")  # Indice hasta subsection
    latex_parts.append("")
    latex_parts.append(r"\begin{document}")
    latex_parts.append("")
    
    # Caratula profesional
    latex_parts.append(r"\begin{titlepage}")
    latex_parts.append(r"\centering")
    latex_parts.append(r"\vspace*{2cm}")
    latex_parts.append("")
    latex_parts.append(r"{\Huge\bfseries Memoria de Cálculo\par}")
    latex_parts.append(r"\vspace{1.5cm}")
    latex_parts.append("")
    latex_parts.append(r"{\Large\itshape Dimensionamiento de:\par}")
    latex_parts.append(r"\vspace{0.5cm}")
    latex_parts.append("")
    latex_parts.append(r"{\LARGE\bfseries " + cfg_tren.nombre + r"\par}")
    latex_parts.append(r"\vspace{2cm}")
    latex_parts.append("")
    latex_parts.append(r"{\large Caudal de diseño: " + f"{cfg_tren.caudal_lps}" + r" L/s\par}")
    latex_parts.append(r"{\large Número de líneas: " + f"{cfg_tren.num_lineas}" + r"\par}")
    latex_parts.append(r"\vfill")
    latex_parts.append(r"{\large\today\par}")
    latex_parts.append(r"\end{titlepage}")
    latex_parts.append("")
    
    # Indices (todos juntos en la misma pagina)
    latex_parts.append(r"\tableofcontents")
    latex_parts.append("")
    latex_parts.append(r"\listoffigures")
    latex_parts.append("")
    latex_parts.append(r"\listoftables")
    latex_parts.append("")
    
    # Resumen en nueva pagina
    latex_parts.append(r"\newpage")
    latex_parts.append(r"\section{Resumen del Proyecto}")
    latex_parts.append("")
    latex_parts.append(f"Este documento presenta el dimensionamiento detallado del {cfg_tren.nombre}, diseñado para tratar un caudal de {cfg_tren.caudal_lps} L/s distribuido en {cfg_tren.num_lineas} líneas paralelas ({cfg_tren.caudal_lps / cfg_tren.num_lineas:.2f} L/s por línea).")
    latex_parts.append("")
    latex_parts.append(r"\textbf{Características del afluente:}")
    latex_parts.append(r"\begin{itemize}")
    latex_parts.append(f"    \\item DBO$_5$: {cfg_tren.dbo} mg/L")
    latex_parts.append(f"    \\item DQO: {cfg_tren.dqo} mg/L")
    latex_parts.append(f"    \\item SST: {cfg_tren.sst} mg/L")
    latex_parts.append(f"    \\item Coliformes fecales: {cfg_tren.cf:.0e} NMP/100mL")
    latex_parts.append(f"    \\item Temperatura: {cfg_tren.temperatura}°C")
    latex_parts.append(r"\end{itemize}")
    latex_parts.append("")
    latex_parts.append(r"\textbf{Secuencia de unidades del tren:} ")
    latex_parts.append(r" $\rightarrow$ ".join([NOMBRES_UNIDADES.get(u, u) for u in cfg_tren.unidades]))
    latex_parts.append("")
    
    # Seccion de dimensionamiento
    latex_parts.append(r"\section{Dimensionamiento de Unidades}")
    latex_parts.append("")
    
    # Generar cada unidad con titulo claro
    for i, unidad in enumerate(cfg_tren.unidades, 1):
        if unidad in resultados:
            # Nueva pagina para cada unidad
            latex_parts.append(r"\newpage")
            latex_parts.append("")
            
            # Agregar titulo de la unidad (sin "Unidad X:" para que quede como en el ejemplo)
            nombre_unidad = NOMBRES_UNIDADES.get(unidad, unidad)
            latex_parts.append(f"\\subsection{{{nombre_unidad}}}")
            latex_parts.append("")
            
            # Contenido LaTeX de la unidad (con ruta de figuras)
            latex_unidad = generar_latex_unidad(unidad, resultados[unidad], cfg, figuras_dir)
            latex_parts.append(latex_unidad)
            latex_parts.append("")
    
    # Bibliografia
    latex_parts.append("")
    latex_parts.append(r"\newpage")
    latex_parts.append(r"\section{Referencias Bibliograficas}")
    latex_parts.append(r"\bibliographystyle{plain}")
    latex_parts.append(r"\bibliography{referencias}")
    latex_parts.append("")
    
    # Cierre
    latex_parts.append(r"\end{document}")
    
    # Guardar
    documento = "\n".join(latex_parts)
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(documento)
    
    # Generar figuras para cada unidad
    print(f"\nGenerando figuras en: {figuras_dir}")
    for unidad in cfg_tren.unidades:
        if unidad in resultados and unidad in GENERADORES_LATEX:
            try:
                generador_class = GENERADORES_LATEX[unidad]
                generador = generador_class(cfg, resultados[unidad], ruta_figuras='figuras')
                # Intentar generar esquema si existe el método
                if hasattr(generador, 'generar_esquema_matplotlib'):
                    generador.generar_esquema_matplotlib(figuras_dir)
                    print(f"  - Figura {unidad}: OK")
            except Exception as e:
                print(f"  - Figura {unidad}: {e}")
    
    # Generar archivo de bibliografia
    _generar_bibliografia(output_dir)
    print(f"Bibliografia generada: {os.path.join(output_dir, 'referencias.bib')}")
    
    print(f"Documento guardado: {tex_path}")
    print(f"Tamano: {len(documento)} caracteres")
    
    # Compilar PDF si se solicita
    if compilar_pdf:
        print("Compilando PDF...")
        try:
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            pdf_path = tex_path.replace('.tex', '.pdf')
            if os.path.exists(pdf_path):
                print(f"PDF generado: {pdf_path}")
        except Exception as e:
            print(f"Error compilando PDF: {e}")
    
    return tex_path


# =============================================================================
# MAIN - PRUEBA
# =============================================================================

if __name__ == "__main__":
    import subprocess
    
    print("=" * 60)
    print("GENERADOR TREN")
    print("=" * 60)
    
    # Ejemplo de uso
    entrada = {
        "nombre_tren": "Sistema de Tratamiento Anaerobio-Aerobio con Reactor de Flujo Ascendente y Humedal Vertical",
        "caudal_total_lps": 17.0,
        "num_lineas": 3,
        "afluente": {
            "DBO5_mg_L": 250.0,
            "DQO_mg_L": 500.0,
            "SST_mg_L": 220.0,
            "CF_NMP_100mL": 1.0e7,
            "temperatura_C": 24.2,
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
    
    print("\nGenerando documento con el tren de ejemplo...")
    tex_path = generar_documento_tren(
        entrada,
        output_dir="resultados/mis_trenes",
        nombre_archivo="tren_ejemplo",
        compilar_pdf=False  # Se compila manualmente abajo para mostrar progreso
    )
    
    print(f"\nArchivo LaTeX generado: {tex_path}")
    
    # Compilar PDF (2 veces para indices)
    print("\n" + "=" * 60)
    print("[5] Compilando PDF (2 pasadas para indices)...")
    print("=" * 60)
    try:
        output_dir = "resultados/mis_trenes"
        tex_name = os.path.basename(tex_path)
        
        # Primera pasada
        print("  Primera pasada...")
        subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
            capture_output=True,
            timeout=60
        )
        
        # BibTeX para referencias
        print("  Ejecutando BibTeX...")
        subprocess.run(
            ['bibtex', tex_name.replace('.tex', '')],
            cwd=output_dir,
            capture_output=True,
            timeout=60
        )
        
        # Segunda pasada (para indices y refs)
        print("  Segunda pasada (indices)...")
        subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
            capture_output=True,
            timeout=60
        )
        
        # Tercera pasada (para resolver refs cruzadas)
        print("  Tercera pasada (referencias)...")
        subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
            capture_output=True,
            timeout=60
        )
        
        pdf_path = tex_path.replace('.tex', '.pdf')
        if os.path.exists(pdf_path):
            print(f"PDF generado: {pdf_path}")
        else:
            print("PDF no generado (posible error en compilacion)")
    except Exception as e:
        print(f"Error compilando PDF: {e}")
    
    print("\n" + "=" * 60)
    print("Generacion completada")
    print("=" * 60)
    print("=" * 60)
