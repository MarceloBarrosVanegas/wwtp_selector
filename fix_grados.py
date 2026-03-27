#!/usr/bin/env python
"""Script para arreglar los símbolos de grados en generar_latex_A.py"""

with open('generar_latex_A.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar todos los símbolos de grados y circunflejos problemáticos
# Usar un marcador temporal
content = content.replace('^{\circ}', 'GRADOS_SYM')
content = content.replace('^{{\circ}}', 'GRADOS_SYM')
content = content.replace('^{{{\circ}}}', 'GRADOS_SYM')
content = content.replace('^{{{{\circ}}}}', 'GRADOS_SYM')
content = content.replace('^{{{{{{\circ}}}}}}', 'GRADOS_SYM')
content = content.replace('^{{{{{{{{\circ}}}}}}}}', 'GRADOS_SYM')

# Reemplazar el símbolo de grados directo por texto
content = content.replace('°', ' grados C')

# Reemplazar el marcador por el formato LaTeX correcto (escapado para Python)
content = content.replace('GRADOS_SYM', '$^{\\circ}$C')

# Arreglar backslashes duplicados en comandos LaTeX
content = content.replace('\\\\cdot', '\\cdot')
content = content.replace('\\\\sin', '\\sin')
content = content.replace('\\\\theta', '\\theta')
content = content.replace('\\\\geq', '\\geq')

with open('generar_latex_A.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Archivo arreglado")
