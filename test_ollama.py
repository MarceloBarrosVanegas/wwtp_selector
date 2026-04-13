#!/usr/bin/env python3
"""Prueba rápida de generación de texto con Ollama."""

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "deepseek-r1:latest"

# Datos de entrada del proyecto actual
datos = {
    "caudal_total_L_s": 17.31,
    "num_lineas": 3,
    "unidades": ["Rejillas", "Desarenador", "UASB", "Humedal Vertical", "Desinfección con Cloro", "Lecho de Secado"],
    "area_predio_ha": 1.33,
    "efluente_DBO5": 58.9,
    "efluente_DQO": 140.8,
    "efluente_SST": 15.1,
    "efluente_CF": 1,
    "cumple_TULSMA": "Sí",
}

prompt_resumen = f"""Eres un ingeniero ambiental redactando un resumen ejecutivo para un informe técnico de una Planta de Tratamiento de Aguas Residuales (PTAR).

Datos del proyecto:
- Caudal de diseño: {datos['caudal_total_L_s']} L/s distribuidos en {datos['num_lineas']} líneas paralelas.
- Unidades de tratamiento: {', '.join(datos['unidades'])}.
- Área total estimada del predio: {datos['area_predio_ha']} ha.
- Efluente final estimado: DBO5={datos['efluente_DBO5']} mg/L, DQO={datos['efluente_DQO']} mg/L, SST={datos['efluente_SST']} mg/L, CF={datos['efluente_CF']} NMP/100mL.
- Cumple con los límites de vertimiento de la TULSMA: {datos['cumple_TULSMA']}.

Redacta un párrafo técnico de aproximadamente 80-120 palabras en español que sirva como resumen ejecutivo del proyecto. No uses viñetas, solo texto narrativo fluido.
"""

print("=" * 60)
print(f"Probando modelo: {MODEL}")
print("=" * 60)

try:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt_resumen,
            "stream": False,
            "options": {"temperature": 0.4, "num_predict": 300}
        },
        timeout=120
    )
    response.raise_for_status()
    data = response.json()
    texto = data.get("response", "")
    
    # Limpiar posible bloque <think> de deepseek-r1
    if "</think>" in texto:
        texto = texto.split("</think>")[-1].strip()
    elif texto.startswith("<") and ">" in texto:
        # Heurística simple
        texto = texto.split(">", 1)[-1].strip()
    
    print("\n--- TEXTO GENERADO ---\n")
    print(texto)
    print("\n--- FIN ---")
    print(f"\nLongitud: {len(texto.split())} palabras")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nPosibles causas:")
    print("1. Ollama server no está corriendo.")
    print("2. El modelo no está descargado.")
    print("3. Problema de red con localhost:11434.")
