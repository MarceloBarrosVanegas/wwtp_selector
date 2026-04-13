path = 'latex_unidades/reporte_resultados.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

lines[190] = '                f"CHS = {u.get(\'CHS_m3_m2_h\', 0):.2f} m$^3$/m$^2$·h \\\\\")\n'
lines[193] = '                f"v$_{{up}}$ = {u.get(\'v_up_calc_m_h\', 0):.2f} m/h \\\\\")\n'

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Done')
