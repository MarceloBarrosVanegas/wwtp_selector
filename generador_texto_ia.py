#!/usr/bin/env python3
"""
GENERADOR DE TEXTO CON IA (Ollama local)
Genera resumenes narrativos en espanol tecnico para el documento LaTeX.
"""

import os
import sys
from typing import Dict, Any, List, Optional


def _llamar_ollama(prompt: str, modelo: str = "qwen2.5:3b", temperature: float = 0.2) -> str:
    """Llama al modelo local via libreria ollama."""
    try:
        import ollama
        response = ollama.chat(
            model=modelo,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un ingeniero sanitario redactando una memoria de calculo. "
                        "Escribe en espanol tecnico, tercera persona, tono profesional, objetivo y conciso. "
                        "Evita adjetivos superfluos o valoraciones no cuantificadas (ej. 'eficiente', 'robusto', 'innovador'). "
                        "Usa hechos, cifras y relaciones causales. "
                        "No uses listas con vinetas; redacta parrafos con saltos de linea entre ellos. "
                        "No incluyas encabezados ni titulos; solo el cuerpo del texto."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            options={"temperature": temperature, "num_predict": 900},
        )
        return response["message"]["content"].strip()
    except Exception as e:
        error_msg = str(e)
        if "Connection refused" in error_msg or "No connection adapters" in error_msg or "not found" in error_msg.lower():
            return (
                "[ATENCION: No se pudo conectar con Ollama. "
                "Asegurate de tener Ollama instalado y ejecutandose. "
                "Para instalar el modelo necesario, ejecuta en tu terminal:  "
                "ollama pull qwen2.5:3b  ]"
            )
        return f"[Error generando texto con IA: {e}]"


def generar_resumen_proyecto_ia(
    nombre_tren: str,
    caudal_lps: float,
    num_lineas: int,
    afluente: Dict[str, float],
    unidades: List[str],
    nombres_unidades: Dict[str, str],
) -> str:
    """
    Genera un texto exhaustivo que describe el proyecto, el tren de tratamiento
    y los datos iniciales, usando el modelo local de Ollama.
    """
    nombres = [nombres_unidades.get(u, u) for u in unidades]
    secuencia_texto = " -> ".join(nombres)

    prompt = f"""Redacta entre 3 y 4 parrafos cortos (total minimo 200 palabras) para la seccion 'Resumen del Proyecto' de una memoria de calculo de ingenieria sanitaria.

Datos del proyecto:
- Nombre: {nombre_tren}
- Caudal de diseno: {caudal_lps} L/s
- Numero de lineas paralelas: {num_lineas}
- Caudal por linea: {caudal_lps / num_lineas:.2f} L/s
- Caracteristicas del afluente: DBO5 = {afluente.get('DBO5_mg_L', 'N/A')} mg/L, DQO = {afluente.get('DQO_mg_L', 'N/A')} mg/L, SST = {afluente.get('SST_mg_L', 'N/A')} mg/L, Coliformes fecales = {afluente.get('CF_NMP_100mL', 'N/A'):.0e} NMP/100mL, Temperatura = {afluente.get('temperatura_C', 'N/A')} C.
- Secuencia de unidades del tren: {secuencia_texto}.

Estructura obligatoria (usa saltos de linea dobles entre parrafos):
- Primer parrafo: Proposito del sistema, caudal total, numero de lineas y caudal por linea. Explica brevemente que la configuracion en lineas paralelas permite mantener el tratamiento si una linea sale de servicio.
- Segundo parrafo: Descripcion del afluente. Menciona los valores de DBO5, DQO, SST y coliformes fecales como indicadores de la carga contaminante.
- Tercer parrafo: Logica del tren de tratamiento. Justifica el orden de las unidades segun su funcion (pretratamiento, tratamiento primario/secundario, terciario, manejo de lodos).
- Cuarto parrafo (obligatorio, corto): Objetivo final del proyecto. Debe mencionar explicitamente que el efluente tratado debe cumplir con los limites de descarga establecidos en el TULSMA (Texto Unificado de Legislacion Secundaria del Ministerio del Ambiente del Ecuador).

Restricciones estrictas:
- NO escribas "Parrafo 1:", "Parrafo 2:" ni ninguna etiqueta de parrafo. Comienza directamente con el texto.
- No uses vinetas ni listas numeradas.
- No uses adjetivos valorativos sin soporte numerico.
- Separa cada parrafo con una linea en blanco (doble salto de linea).
- No agregues titulos ni encabezados.
"""
    return _llamar_ollama(prompt)


def generar_conclusiones_resultados_ia(
    nombre_tren: str,
    resultados: Dict[str, Any],
    calidad_efluente: Dict[str, float],
    area_m2: Optional[float] = None,
    cfg=None,
) -> str:
    """
    Genera un texto de conclusiones al final de la seccion Resultados.
    """
    area_txt = f"{area_m2:.1f} m2" if area_m2 else "no calculada"

    # Extraer limites TULSMA de la configuracion si esta disponible
    if cfg is not None:
        lim_dbo = getattr(cfg, 'DBO5_ef_mg_L', 100.0)
        lim_dqo = getattr(cfg, 'DQO_ef_mg_L', 250.0)
        lim_sst = getattr(cfg, 'SST_ef_mg_L', 100.0)
        lim_cf = getattr(cfg, 'CF_ef_NMP', 3000.0)
    else:
        lim_dbo, lim_dqo, lim_sst, lim_cf = 100.0, 250.0, 100.0, 3000.0

    dbo_ef = calidad_efluente.get('DBO5_mg_L', 'N/A')
    dqo_ef = calidad_efluente.get('DQO_mg_L', 'N/A')
    sst_ef = calidad_efluente.get('SST_mg_L', 'N/A')
    cf_ef = calidad_efluente.get('CF_NMP_100mL', 'N/A')

    # Determinar dictamen rapidamente
    dictamen_t12 = "CUMPLE" if (isinstance(dbo_ef, (int, float)) and isinstance(dqo_ef, (int, float)) and isinstance(sst_ef, (int, float)) and isinstance(cf_ef, (int, float)) and dbo_ef <= lim_dbo and dqo_ef <= lim_dqo and sst_ef <= lim_sst and cf_ef <= lim_cf) else "NO CUMPLE"

    prompt = f"""Redacta entre 2 y 3 parrafos cortos (total minimo 150 palabras) de conclusiones para la seccion de Resultados de una memoria de calculo de ingenieria sanitaria.

Datos:
- Nombre del sistema: {nombre_tren}
- Calidad final del efluente estimada: DBO5 = {dbo_ef} mg/L, DQO = {dqo_ef} mg/L, SST = {sst_ef} mg/L, Coliformes fecales = {cf_ef:.0e} NMP/100mL.
- Limites TULSMA (Tabla 12 - descarga a cuerpo de agua dulce): DBO5 <= {lim_dbo:.0f} mg/L, DQO <= {lim_dqo:.0f} mg/L, SST <= {lim_sst:.0f} mg/L, Coliformes fecales <= {lim_cf:.0f} NMP/100mL.
- Dictamen contra TULSMA Tabla 12: {dictamen_t12}.
- Area de ocupacion del layout aproximada: {area_txt}.

Estructura obligatoria (usa saltos de linea dobles entre parrafos):
- Primer parrafo: Desempeno del tren en remocion de materia organica, solidos y microorganismos indicadores. Compara cada parametro de efluente contra los limites TULSMA proporcionados. Menciona explicitamente si el efluente cumple o no con la norma ecuatoriana.
- Segundo parrafo: Ocupacion de terreno y viabilidad espacial. Comenta si el area requerida es razonable para la capacidad del sistema.
- Tercer parrafo (opcional, corto): Confiabilidad operativa derivada de la configuracion en lineas paralelas.

Restricciones estrictas:
- NO escribas "Parrafo 1:", "Parrafo 2:" ni ninguna etiqueta de parrafo. Comienza directamente con el texto.
- No uses vinetas ni listas numeradas.
- No uses adjetivos valorativos sin soporte numerico.
- Separa cada parrafo con una linea en blanco (doble salto de linea).
- No agregues titulos ni encabezados.
"""
    return _llamar_ollama(prompt)
