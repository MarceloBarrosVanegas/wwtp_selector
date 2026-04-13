path = 'latex_unidades/reporte_resultados.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "elif unidad == 'taf':" in line:
        lines[i+1] = '        return (f"TAF & D = {u.get(\'D_bf_m\', 0):.2f}, H = {u.get(\'H_total_m\', 0):.1f} & {num_lineas} & "\n'
        lines[i+2] = '                f"CHS = {u.get(\'CHS_m3_m2_h\', 0):.2f} m$^3$/m$^2$·h \\")\n'
    if "elif unidad == 'abr_rap':" in line:
        lines[i+1] = '        return (f"ABR-RAP & {u.get(\'L_total_m\', u.get(\'largo_layout_m\', 0)):.1f} $\\\\times$ {u.get(\'W_m\', u.get(\'ancho_layout_m\', 0)):.2f} & {num_lineas} & "\n'
        lines[i+2] = '                f"v$_{{up}}$ = {u.get(\'v_up_calc_m_h\', 0):.2f} m/h \\")\n'

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Lineas corregidas')
