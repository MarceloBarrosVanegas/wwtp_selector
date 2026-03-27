#!/usr/bin/env python3
"""
SCRIPT MAESTRO - Dimensiona y genera reporte para la alternativa ESCOGIDA
Uso: python dimensionar_escogida.py [A|B|C|D|E|F]
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ptar_dimensionamiento import ConfigDiseno, calcular_balance_calidad_agua
from generar_latex_A import generar_latex_alternativa_A
from ptar_layout_graficador import generar_layout_con_resultados


def crear_configuracion_real():
    """
    Configuracion con valores reales del estudio.
    
    Limites de efluente segun TULSMA (Tabla 11):
        DBO5_ef_mg_L = 100 mg/L (limite legal)
        SST_ef_mg_L = 100 mg/L (limite legal)
    """
    return ConfigDiseno(
        Q_total_L_s=10.0,
        Q_linea_L_s=5.0,
        num_lineas=2,
        T_agua_C=25.6,
        T_min_C=21.0,
        DBO5_mg_L=243.10,
        DQO_mg_L=498.00,
        SST_mg_L=156.00,
        DBO5_ef_mg_L=100.00,  # Limite TULSMA (mg/L)
        SST_ef_mg_L=100.00,   # Limite TULSMA (mg/L)
        CS_area=2.0,
        CS_volumen=1.50
    )


def dimensionar_alternativa_A(cfg):
    """Dimensiona Alternativa A: UASB + Filtro Percolador + UV"""
    from ptar_dimensionamiento import (
        dimensionar_rejillas, dimensionar_desarenador, dimensionar_uasb,
        dimensionar_filtro_percolador, dimensionar_lecho_secado
    )
    
    resultados = {}
    
    print("\n1. Dimensionando REJILLAS...")
    resultados['rejillas'] = dimensionar_rejillas(cfg)
    print(f"   - Largo: {resultados['rejillas']['largo_layout_m']} m")
    
    print("\n2. Dimensionando DESARENADOR...")
    resultados['desarenador'] = dimensionar_desarenador(cfg)
    print(f"   - Largo: {resultados['desarenador']['L_diseno_m']} m")
    
    print("\n3. Dimensionando UASB...")
    resultados['uasb'] = dimensionar_uasb(cfg)
    print(f"   - Diametro: {resultados['uasb']['D_m']} m")
    
    print("\n4. Dimensionando FILTRO PERCOLADOR...")
    # Usar eficiencia REAL calculada por el UASB (ajustada por temperatura)
    eta_DBO_real = resultados['uasb']['eta_DBO']
    DBO_tras_uasb = cfg.DBO5_mg_L * (1 - eta_DBO_real)
    resultados['filtro_percolador'] = dimensionar_filtro_percolador(cfg, DBO_entrada_mg_L=DBO_tras_uasb)
    print(f"   - DBO entrada: {DBO_tras_uasb:.1f} mg/L (efluente UASB, eta={eta_DBO_real*100:.0f}%)")
    print(f"   - Diametro: {resultados['filtro_percolador']['D_filtro_m']} m")
    
    print("\n5. Dimensionando SEDIMENTADOR...")
    from ptar_dimensionamiento import dimensionar_sedimentador_sec
    # Pasar DBO removida por el FP y DBO de entrada al sedimentador (encadenado)
    DBO_removida_fp_kg_d = resultados['filtro_percolador']['DBO_removida_kg_d']
    DBO_entrada_sed = resultados['filtro_percolador']['DBO_salida_Germain_mg_L']
    resultados['sedimentador'] = dimensionar_sedimentador_sec(
        cfg, 
        DBO_entrada_mg_L=DBO_entrada_sed,
        DBO_removida_fp_kg_d=DBO_removida_fp_kg_d
    )
    print(f"   - Diametro: {resultados['sedimentador']['D_m']} m")
    print(f"   - DBO salida: {resultados['sedimentador']['DBO_salida_mg_L']:.1f} mg/L")
    
    print("\n6. Dimensionando DESINFECCION CON CLORO...")
    from ptar_dimensionamiento import dimensionar_desinfeccion_cloro
    # Estimar CF de entrada (post-sedimentador)
    CF_entrada = 5e6  # NMP/100mL típico post-sedimentador
    resultados['desinfeccion'] = dimensionar_desinfeccion_cloro(cfg, CF_entrada_NMP=CF_entrada)
    d = resultados['desinfeccion']
    print(f"   - Tanque: {d['largo_m']} m x {d['ancho_m']} m")
    print(f"   - Tiempo contacto: {d['TRH_min']} min")
    print(f"   - CT: {d['CT_mg_min_L']} mg.min/L")
    print(f"   - Log reduccion: {d['log_reduccion']}")
    print(f"   - CF final: {d['CF_final_NMP']:.0f} NMP/100mL")
    print(f"   - Cumple TULSMA: {'SI' if d['cumple_TULSMA'] else 'NO'}")
    
    print("\n7. Dimensionando LECHO DE SECADO...")
    # Calcular producción total de lodos del sistema (UASB + FP)
    # UASB: lodos anaerobios (factor de producción desde config)
    DBO_removida_uasb_kg_d = cfg.Q_linea_m3_d * (cfg.DBO5_mg_L / 1000) * resultados['uasb']['eta_DBO']
    lodos_uasb_kg_d = cfg.lecho_factor_produccion_lodos * DBO_removida_uasb_kg_d
    # Filtro Percolador: humus (ya calculado en el dimensionamiento del FP)
    lodos_fp_kg_d = resultados['filtro_percolador']['DBO_removida_kg_d']
    # Producción total de lodos
    lodos_total_kg_d = lodos_uasb_kg_d + lodos_fp_kg_d
    resultados['lecho_secado'] = dimensionar_lecho_secado(cfg, lodos_kg_SST_d=lodos_total_kg_d)
    print(f"   - Lodos UASB: {lodos_uasb_kg_d:.2f} kg SST/d")
    print(f"   - Lodos FP (humus): {lodos_fp_kg_d:.2f} kg SST/d")
    print(f"   - Total lodos: {lodos_total_kg_d:.2f} kg SST/d")
    print(f"   - Area lecho: {resultados['lecho_secado']['A_lecho_m2']} m2")
    
    # Calcular balance completo de calidad
    print("\n8. Calculando BALANCE DE CALIDAD DEL AGUA...")
    balance = calcular_balance_calidad_agua(cfg, resultados)
    resultados['balance_calidad'] = balance
    
    # Imprimir resumen del balance
    print("\n   BALANCE DE CALIDAD DEL AGUA:")
    print("   " + "-" * 66)
    print(f"   {'Parametro':<15} {'Afluente':>12} {'Post-UASB':>12} {'Post-FP':>12} {'Efluente':>12}")
    print("   " + "-" * 66)
    
    # DBO5
    dbos = balance['afluente']['DBO5_mg_L']
    dbos_uasb = balance['tras_uasb']['DBO5_mg_L']
    dbos_fp = balance['tras_fp']['DBO5_mg_L']
    dbos_final = balance['efluente_final']['DBO5_mg_L']
    print(f"   {'DBO5 (mg/L)':<15} {dbos:>12.1f} {dbos_uasb:>12.1f} {dbos_fp:>12.1f} {dbos_final:>12.1f}")
    
    # DQO
    dqos = balance['afluente']['DQO_mg_L']
    dqos_uasb = balance['tras_uasb']['DQO_mg_L']
    dqos_fp = balance['tras_fp']['DQO_mg_L']
    dqos_final = balance['efluente_final']['DQO_mg_L']
    print(f"   {'DQO (mg/L)':<15} {dqos:>12.1f} {dqos_uasb:>12.1f} {dqos_fp:>12.1f} {dqos_final:>12.1f}")
    
    # SST
    ssts = balance['afluente']['SST_mg_L']
    ssts_uasb = balance['tras_uasb']['SST_mg_L']
    ssts_fp = balance['tras_fp']['SST_mg_L']
    ssts_final = balance['efluente_final']['SST_mg_L']
    print(f"   {'SST (mg/L)':<15} {ssts:>12.1f} {ssts_uasb:>12.1f} {ssts_fp:>12.1f} {ssts_final:>12.1f}")
    
    # CF
    cfs = balance['afluente']['CF_NMP']
    cfs_uasb = balance['tras_uasb']['CF_NMP']
    cfs_fp = balance['tras_fp']['CF_NMP']
    cfs_final = balance['efluente_final']['CF_NMP']
    print(f"   {'CF (NMP/100mL)':<15} {cfs:>12.0f} {cfs_uasb:>12.0f} {cfs_fp:>12.0f} {cfs_final:>12.0f}")
    
    print("   " + "-" * 66)
    
    # Eficiencias totales
    print("\n   EFICIENCIAS TOTALES:")
    ef = balance['eficiencias_totales']
    print(f"     DBO5: {ef['DBO5_pct']:.1f}% | DQO: {ef['DQO_pct']:.1f}% | SST: {ef['SST_pct']:.1f}% | CF: {ef['CF_pct']:.1f}%")
    
    # Cumplimiento TULSMA
    print("\n   CUMPLIMIENTO TULSMA:")
    cumple = balance['cumplimiento_TULSMA']
    print(f"     DBO5 <= 100 mg/L: {'CUMPLE' if cumple['DBO5'] else 'NO CUMPLE'}")
    print(f"     SST <= 100 mg/L:  {'CUMPLE' if cumple['SST'] else 'NO CUMPLE'}")
    print(f"     CF <= 3000 NMP/100mL: {'CUMPLE' if cumple['CF'] else 'NO CUMPLE'}")
    
    return resultados


def main():
    """Funcion principal."""
    
    if len(sys.argv) < 2:
        print("Uso: python dimensionar_escogida.py [A|B|C|D|E|F]")
        print("Ejemplo: python dimensionar_escogida.py A")
        return
    
    alt_id = sys.argv[1].upper()
    
    print("=" * 70)
    print(f"DIMENSIONAMIENTO ALTERNATIVA {alt_id}")
    print("=" * 70)
    
    # Crear configuracion
    cfg = crear_configuracion_real()
    print(f"\nParametros de entrada:")
    print(f"  - Caudal total: {cfg.Q_total_L_s} L/s")
    print(f"  - DBO5: {cfg.DBO5_mg_L} mg/L")
    print(f"  - Temperatura: {cfg.T_agua_C} C")
    
    # Dimensionar segun la alternativa
    if alt_id == 'A':
        resultados = dimensionar_alternativa_A(cfg)
    else:
        print(f"\n[ADVERTENCIA] Alternativa {alt_id} aun no implementada.")
        print("Usando Alternativa A como ejemplo...")
        resultados = dimensionar_alternativa_A(cfg)
    
    # Crear directorios de salida
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')
    os.makedirs(output_dir, exist_ok=True)
    
    # PASO 1: Generar Layout PRIMERO (para que exista cuando compile el PDF)
    print("\n" + "=" * 70)
    print("GENERANDO LAYOUT...")
    print("=" * 70)
    
    area_m2 = None
    try:
        unidades = ['Rejillas', 'Desarenador', 'UASB', 'Filtro_Percolador', 'Sedimentador', 'Desinfeccion']
        x, y = generar_layout_con_resultados(
            alt_id, unidades, f'Alternativa {alt_id}', resultados, output_dir,
            caudal_L_s=cfg.Q_linea_L_s
        )
        area_m2 = round(x * y)
        print(f"\n   - Layout generado: {x:.1f} m x {y:.1f} m")
        print(f"   - Area total: {area_m2} m2")
        print(f"   - Guardado en: {output_dir}/Layout_{alt_id}_2lineas.png")
    except Exception as e:
        print(f"\n   [ADVERTENCIA] Error generando layout: {e}")
    
    # PASO 2: Generar LaTeX
    print("\n" + "=" * 70)
    print("GENERANDO REPORTE LATEX...")
    print("=" * 70)
    
    latex_path = os.path.join(output_dir, f'seleccion_alternativa_{alt_id}.tex')
    balance_calidad = resultados.get('balance_calidad')
    generar_latex_alternativa_A(cfg, resultados, latex_path, area_m2=area_m2, balance_calidad=balance_calidad)
    
    # PASO 3: Compilar PDF (ahora el layout ya existe)
    print("\n   Intentando compilar a PDF...")
    try:
        from compilar_latex import compilar
        exito, mensaje, pdf_path = compilar(latex_path, output_dir)
        if exito:
            print(f"   [OK] PDF generado: {pdf_path}")
        else:
            print(f"   [INFO] {mensaje}")
    except Exception as e:
        print(f"   [INFO] No se pudo compilar: {e}")
    
    print("\n" + "=" * 70)
    print(f"PROCESO COMPLETADO - Alternativa {alt_id}")
    print("=" * 70)


if __name__ == "__main__":
    main()
