# Sistema de Dimensionamiento PTAR

Código para dimensionar la planta de tratamiento de aguas residuales (PTAR) de Puerto Baquerizo Moreno, Galápagos.

## Archivos Principales

### Uso Principal
- **`dimensionar_escogida.py`** - Script principal. Ejecutar este para dimensionar cualquier alternativa (A-F).
  ```bash
  python dimensionar_escogida.py A
  ```
  Genera: reporte LaTeX, PDF compilado, y layout PNG en la carpeta `resultados/`.

### Módulos (no se ejecutan directamente)
- **`ptar_dimensionamiento.py`** - Fórmulas de ingeniería para calcular cada unidad de tratamiento.
- **`ptar_config.py`** - Configuración de alternativas de tratamiento (A, B, C, D, E, F).
- **`ptar_layout_graficador.py`** - Genera el diagrama/layout de la planta en PNG.
- **`compilar_latex.py`** - Compila archivos LaTeX a PDF usando MiKTeX.

### Generadores de Reporte
- **`generar_latex.py`** - Genera reporte para Alternativa A (UASB + Filtro Percolador + UV).
- **`generador_latex_general.py`** - Generador genérico para cualquier alternativa.

## Uso Rápido

```bash
# Dimensionar Alternativa A (UASB + Filtro Percolador + UV)
python dimensionar_escogida.py A

# Dimensionar Alternativa B
python dimensionar_escogida.py B
```

Los resultados se guardan en `resultados/`:
- `dimensionamiento_A_reporte.pdf` - Reporte completo con cálculos
- `layout_ptar_A.png` - Layout/diagrama de la planta

## Datos de Diseño

- **Caudal**: 10 L/s total (2 líneas paralelas × 5 L/s)
- **DBO₅ entrada**: 243.1 mg/L
- **Temperatura**: 25.6°C
- **Eficiencia requerida**: 85% (DBO₅ salida ≤ 36 mg/L)





