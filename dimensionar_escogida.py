#!/usr/bin/env python3
"""
SCRIPT MAESTRO - Dimensiona y genera reporte para la alternativa ESCOGIDA
Uso: python dimensionar_escogida.py [A|B|C|D|E|F]
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ptar_dimensionamiento import ConfigDiseno
from generar_latex_A import generar_latex_alternativa_A
from ptar_layout_graficador import generar_layout_con_resultados


def crear_configuracion_real():
    """Configuracion con valores reales del estudio."""
    return ConfigDiseno(
        Q_total_L_s=10.0,
        Q_linea_L_s=5.0,
        num_lineas=2,
        T_agua_C=25.6,
        T_min_C=21.0,
        DBO5_mg_L=243.10,
        DQO_mg_L=498.00,
        SST_mg_L=156.00,
        DBO5_ef_mg_L=68.00,
        SST_ef_mg_L=80.00,
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
    # Calcular DBO real del efluente UASB (no usar valor hardcodeado)
    DBO_tras_uasb = cfg.DBO5_mg_L * (1 - cfg.uasb_eta_DBO)
    resultados['filtro_percolador'] = dimensionar_filtro_percolador(cfg, DBO_entrada_mg_L=DBO_tras_uasb)
    print(f"   - DBO entrada: {DBO_tras_uasb:.1f} mg/L (efluente UASB)")
    print(f"   - Diametro: {resultados['filtro_percolador']['D_filtro_m']} m")
    
    print("\n5. Dimensionando SEDIMENTADOR...")
    from ptar_dimensionamiento import dimensionar_sedimentador_sec
    resultados['sedimentador'] = dimensionar_sedimentador_sec(cfg)
    print(f"   - Diametro: {resultados['sedimentador']['D_m']} m")
    
    print("\n6. Dimensionando UV...")
    from ptar_dimensionamiento import dimensionar_uv
    resultados['uv'] = dimensionar_uv(cfg)
    print(f"   - Largo: {resultados['uv']['largo_m']} m")
    print(f"   - Dosis: {resultados['uv']['dosis_efectiva_mj_cm2']} mJ/cm2")
    print(f"   - Lamparas: {resultados['uv']['n_lamparas']}")
    
    print("\n7. Dimensionando LECHO DE SECADO...")
    resultados['lecho_secado'] = dimensionar_lecho_secado(cfg)
    print(f"   - Area: {resultados['lecho_secado']['A_lecho_m2']} m2")
    
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
        unidades = ['Rejillas', 'Desarenador', 'UASB', 'Filtro_Percolador', 'Sedimentador', 'UV']
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
    generar_latex_alternativa_A(cfg, resultados, latex_path, area_m2=area_m2)
    
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
