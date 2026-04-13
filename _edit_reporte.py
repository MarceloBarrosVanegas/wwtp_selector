import re

path = 'latex_unidades/reporte_resultados.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Agregar _UNIDADES_RESUMEN antes de _fila_dimension_unidad
old_block = '''def _fila_dimension_unidad(unidad: str, r: Dict[str, Any], cfg) -> str:
    """Genera una fila de la tabla de dimensionamiento para una unidad."""'''

new_block = '''# Conjunto de unidades reconocidas para tablas de resumen
_UNIDADES_RESUMEN = {
    'rejillas', 'desarenador', 'uasb', 'abr_rap', 'humedal_vertical',
    'filtro_percolador', 'sedimentador_sec', 'baf', 'taf', 'cloro', 'desinfeccion', 'lecho_secado'
}


def _fila_dimension_unidad(unidad: str, r: Dict[str, Any], cfg) -> str:
    """Genera una fila de la tabla de dimensionamiento para una unidad."""'''

content = content.replace(old_block, new_block)

# 2. Corregir filas de taf y abr_rap
content = content.replace(
    """    elif unidad == 'taf':
        return (f\"TAF & {u.get('largo_m', 0):.1f} $\\\\times$ {u.get('ancho_m', 0):.1f} & {num_lineas} & \"
                f\"Área: {u.get('A_sup_m2', 0):.1f} m$^2$ \\\\\")""",
    """    elif unidad == 'taf':
        return (f\"TAF & D = {u.get('D_bf_m', 0):.2f}, H = {u.get('H_total_m', 0):.1f} & {num_lineas} & \"
                f\"CHS = {u.get('CHS_m3_m2_h', 0):.2f} m$^3$/m$^2$·h \\\\\")"""
)

content = content.replace(
    """    elif unidad == 'abr_rap':
        return (f\"ABR-RAP & {u.get('largo_m', 0):.1f} $\\\\times$ {u.get('ancho_m', 0):.1f} & {num_lineas} & \"
                f\"v$_{{up}}$ = {u.get('v_up_m_h', 0):.2f} m/h \\\\\")""",
    """    elif unidad == 'abr_rap':
        return (f\"ABR-RAP & {u.get('L_total_m', u.get('largo_layout_m', 0)):.1f} $\\\\times$ {u.get('W_m', u.get('ancho_layout_m', 0)):.2f} & {num_lineas} & \"
                f\"v$_{{up}}$ = {u.get('v_up_calc_m_h', 0):.2f} m/h \\\\\")"""
)

# 3. Reemplazar _filas_dimensionamiento para orden dinámico
old_fdim = '''def _filas_dimensionamiento(resultados: Dict[str, Any], cfg) -> str:
    """Genera las filas de la tabla de dimensionamiento dinámicamente."""
    orden = ['rejillas', 'desarenador', 'uasb', 'abr_rap', 'humedal_vertical',
             'filtro_percolador', 'sedimentador_sec', 'baf', 'taf', 'cloro', 'desinfeccion', 'lecho_secado']
    filas = []
    for u in orden:
        if u in resultados:
            fila = _fila_dimension_unidad(u, resultados, cfg)
            if fila:
                filas.append(fila)
    return "\\n".join(filas)'''

new_fdim = '''def _filas_dimensionamiento(resultados: Dict[str, Any], cfg) -> str:
    """Genera las filas de la tabla de dimensionamiento respetando el orden real del tren."""
    filas = []
    for u in resultados:
        if u in _UNIDADES_RESUMEN:
            fila = _fila_dimension_unidad(u, resultados, cfg)
            if fila:
                filas.append(fila)
    return "\\n".join(filas)'''

content = content.replace(old_fdim, new_fdim)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Ediciones aplicadas')
