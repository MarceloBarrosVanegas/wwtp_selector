# -*- coding: utf-8 -*-
"""Script para arreglar la tabla del humedal vertical"""

import re

# Leer el archivo
with open('latex_unidades/humedal_vertical.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar el inicio y fin de la tabla a modificar
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'La Tabla~\\ref{{tab:resumen_hafv}}' in line:
        # Buscar hacia atrás el return rf
        for j in range(i, max(0, i-10), -1):
            if 'return rf"""\\subsection{{Resultados}}' in lines[j]:
                start_idx = j
                break
    if start_idx and '\\end{{table}}' in line and i > start_idx + 10:
        end_idx = i
        break

if start_idx is None or end_idx is None:
    print(f"No se encontro la tabla. start={start_idx}, end={end_idx}")
else:
    print(f"Tabla encontrada: lineas {start_idx+1} a {end_idx+1}")
    
    # Nuevo contenido de la tabla
    new_table = '''        return rf"""\\subsection{{Resultados}}

La Tabla~\\ref{{tab:resumen_hafv}} concentra los parametros geometricos, hidraulicos, de carga y calidad del efluente.

\\begin{{table}}[H]
\\centering
\\small
\\caption{{Resumen de resultados -- Humedal Artificial de Flujo Vertical (HAFV)}}
\\label{{tab:resumen_hafv}}
\\begin{{tabular}}{{p{{3.6cm}}p{{3.8cm}}c}}
\\toprule
\\textbf{{Parametro}} & \\textbf{{Descripcion}} & \\textbf{{Valor}} \\\\
\\midrule
\\multicolumn{{3}}{{l}}{{\\textit{{Metodologia y configuracion}}}} \\\\
\\quad Sistema adoptado & Metodologia de diseno & {sistema} (Ruta {ruta}) \\\\
\\quad Criterio controlante & Factor limitante & {criterio} \\\\
\\quad N celdas (alternancia) & Unidades en operacion alterna & {n_filtros} \\\\
\\quad Ciclo alim./reposo & Rotacion por celda & {ciclo_alim:.1f}/{ciclo_reposo:.1f} d \\\\
\\midrule
\\multicolumn{{3}}{{l}}{{\\textit{{Geometria del sistema}}}} \\\\
\\quad Area total construida & Superficie total celdas & {A_total:.1f}\\,m2 \\\\
\\quad Area celda activa & Superficie por celda & {A_operando:.1f}\\,m2 \\\\
\\quad Dimensiones por celda & Largo $\\times$ Ancho & {dims[0]:.1f}$\\times${dims[1]:.1f}\\,m \\\\
\\quad Profundidad del medio & Espesor lecho filtrante & 0.85\\,m \\\\
\\quad Altura total & Incluye borde libre & 1.50\\,m \\\\
\\midrule
\\multicolumn{{3}}{{l}}{{\\textit{{Parametros de carga}}}} \\\\
\\quad OLR real (celda activa) & Carga organica superficial & {OLR:.1f}\\,g DQO/m2·d \\\\
\\quad HLR real (celda activa) & Carga hidraulica superficial & {HLR:.3f}\\,m/d \\\\
\\quad PE equivalente & Habitantes equivalentes & {PE:.0f}\\,PE \\\\
\\midrule
\\multicolumn{{3}}{{l}}{{\\textit{{Calidad del efluente}}}} \\\\
\\quad DBO5 calculada (k-C*) & Concentracion estimada & {DBO_salida:.1f}\\,mg/L \\\\
\\quad Limite TULSMA T12 & Objetivo de diseno & $\\leq$ {r[\'DBO_objetivo_mg_L\']:.0f}\\,mg/L \\\\
\\quad Cumplimiento & Estado vs. limite & {r[\'texto_cumplimiento_kC\'].split(\'.\')[0]} \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}"""
'''
    
    # Reemplazar las lineas
    new_lines = lines[:start_idx]
    new_lines.append(new_table)
    new_lines.extend(lines[end_idx+1:])
    
    # Guardar
    with open('latex_unidades/humedal_vertical.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Tabla actualizada exitosamente!")
