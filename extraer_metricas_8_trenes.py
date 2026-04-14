#!/usr/bin/env python3
"""Extrae métricas clave de los 8 trenes para comparación."""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generar_tren import ConfigTren, crear_configuracion, dimensionar_tren
from ptar_layout_graficador import generar_layout

PARAMETROS_BASE = {
    "caudal_total_lps": 17.31,
    "num_lineas": 3,
    "afluente": {
        "DBO5_mg_L": 243.10,
        "DQO_mg_L": 498.0,
        "SST_mg_L": 156.0,
        "CF_NMP_100mL": 3300.0,
        "temperatura_C": 25.6,
    },
    "factor_maximo_horario": 2.77,
}

TRENES = [
    ("T1", "T1_uasb_fp_sed_cloro", "T1 – Rejillas + Desarenador + UASB + Filtro Percolador + Sedimentador Secundario + Cloro + Lecho de Secado",
     ["rejillas","desarenador","uasb","filtro_percolador","sedimentador_sec","cloro","lecho_secado"]),
    ("T2", "T2_uasb_humedal_cloro", "T2 – Rejillas + Desarenador + UASB + Humedal Vertical + Cloro + Lecho de Secado",
     ["rejillas","desarenador","uasb","humedal_vertical","cloro","lecho_secado"]),
    ("T3", "T3_uasb_baf_cloro", "T3 – Rejillas + Desarenador + UASB + BAF + Cloro + Lecho de Secado",
     ["rejillas","desarenador","uasb","baf","cloro","lecho_secado"]),
    ("T4", "T4_uasb_taf_sed_cloro", "T4 – Rejillas + Desarenador + UASB + TAF + Sedimentador Secundario + Cloro + Lecho de Secado",
     ["rejillas","desarenador","uasb","taf","sedimentador_sec","cloro","lecho_secado"]),
    ("T5", "T5_abr_fp_sed_cloro", "T5 – Rejillas + Desarenador + ABR-RAP + Filtro Percolador + Sedimentador Secundario + Cloro + Lecho de Secado",
     ["rejillas","desarenador","abr_rap","filtro_percolador","sedimentador_sec","cloro","lecho_secado"]),
    ("T6", "T6_abr_humedal_cloro", "T6 – Rejillas + Desarenador + ABR-RAP + Humedal Vertical + Cloro + Lecho de Secado",
     ["rejillas","desarenador","abr_rap","humedal_vertical","cloro","lecho_secado"]),
    ("T7", "T7_abr_baf_cloro", "T7 – Rejillas + Desarenador + ABR-RAP + BAF + Cloro + Lecho de Secado",
     ["rejillas","desarenador","abr_rap","baf","cloro","lecho_secado"]),
    ("T8", "T8_abr_taf_sed_cloro", "T8 – Rejillas + Desarenador + ABR-RAP + TAF + Sedimentador Secundario + Cloro + Lecho de Secado",
     ["rejillas","desarenador","abr_rap","taf","sedimentador_sec","cloro","lecho_secado"]),
]

metricas = []

for cod, carpeta, nombre, unidades in TRENES:
    entrada = {
        **PARAMETROS_BASE,
        "nombre_tren": nombre,
        "unidades": unidades,
    }
    cfg_tren = ConfigTren.from_dict(entrada)
    cfg = crear_configuracion(cfg_tren)
    resultados = dimensionar_tren(cfg_tren)
    
    # Calidad
    aff = resultados.get("_calidad_afluente", {})
    eff = resultados.get("_calidad_efluente", {})
    
    # Lodos
    lodos = resultados.get("_lodos_acumulados_kg_SST_d", 0)
    
    # Layout
    area_layout = None
    ancho = None
    largo = None
    try:
        os.makedirs("resultados/_temp_layouts", exist_ok=True)
        unidades_con_layout = [u for u in cfg_tren.unidades if u in resultados and u != 'lecho_secado']
        layout_info = generar_layout(
            tren_id=carpeta.lower(),
            unidades=unidades_con_layout,
            resultados=resultados,
            output_dir="resultados/_temp_layouts",
            num_lineas=cfg_tren.num_lineas,
            incluir_lecho_secado='lecho_secado' in cfg_tren.unidades,
            caudal_L_s=cfg_tren.caudal_lps / cfg_tren.num_lineas if cfg_tren.num_lineas > 0 else None,
            nombre_tren=cfg_tren.nombre,
        )
        area_layout = layout_info.get("area_layout_m2", 0)
        ancho = layout_info.get("ancho_total_m", 0)
        largo = layout_info.get("largo_total_m", 0)
    except Exception as e:
        area_layout = f"ERROR: {e}"
    
    # Extraer dimensiones clave de unidades principales
    dims = {}
    for u in unidades:
        if u in resultados and isinstance(resultados[u], dict):
            r = resultados[u]
            if u == "uasb":
                dims[u] = f"D={r.get('D_m',0):.1f}m, H={r.get('H_total_construccion_m',0):.1f}m"
            elif u == "abr_rap":
                dims[u] = f"L={r.get('L_total_m',0):.1f}m, W={r.get('W_m',0):.2f}m"
            elif u == "filtro_percolador":
                dims[u] = f"D={r.get('D_filtro_m',0):.1f}m, H={r.get('H_total_m',0):.1f}m"
            elif u == "humedal_vertical":
                dims[u] = f"Área={r.get('A_total_m2',0):.0f}m²"
            elif u == "baf":
                dims[u] = f"{r.get('largo_m',0):.1f}x{r.get('ancho_m',0):.1f}m"
            elif u == "taf":
                dims[u] = f"D={r.get('D_bf_m',0):.1f}m, H={r.get('H_total_m',0):.1f}m"
            elif u == "sedimentador_sec":
                dims[u] = f"D={r.get('D_m',0):.1f}m, H={r.get('h_sed_m',0):.1f}m"
            elif u == "lecho_secado":
                dims[u] = f"Área={r.get('A_total_m2',0):.0f}m²"
            else:
                dims[u] = "OK"
    
    metricas.append({
        "codigo": cod,
        "nombre": nombre,
        "unidades": unidades,
        "afluente_dbo": aff.get("DBO5_mg_L"),
        "afluente_sst": aff.get("SST_mg_L"),
        "efluente_dbo": eff.get("DBO5_mg_L"),
        "efluente_dqo": eff.get("DQO_mg_L"),
        "efluente_sst": eff.get("SST_mg_L"),
        "efluente_cf": eff.get("CF_NMP_100mL"),
        "lodos_kg_SST_d": lodos,
        "area_layout_m2": area_layout,
        "ancho_m": ancho,
        "largo_m": largo,
        "dimensiones": dims,
    })

# Guardar JSON
with open("resultados/metricas_8_trenes.json", "w", encoding="utf-8") as f:
    json.dump(metricas, f, indent=2, ensure_ascii=False)

# Imprimir tabla resumen
print(f"\n{'='*120}")
print(f"{'Cod':<5} {'DBO5 ef':<8} {'DQO ef':<8} {'SST ef':<8} {'CF ef':<8} {'Lodos':<10} {'Área layout':<15} {'Dims clave'}")
print("-"*120)
for m in metricas:
    area_str = f"{m['area_layout_m2']:.0f} m²" if isinstance(m['area_layout_m2'], (int, float)) else str(m['area_layout_m2'])
    dims_str = " | ".join([f"{k}: {v}" for k, v in m['dimensiones'].items() if k in ['uasb','abr_rap','humedal_vertical','baf','taf','filtro_percolador','sedimentador_sec']])
    print(f"{m['codigo']:<5} {m['efluente_dbo']:<8.1f} {m['efluente_dqo']:<8.1f} {m['efluente_sst']:<8.1f} {m['efluente_cf']:<8.1f} {m['lodos_kg_SST_d']:<10.1f} {area_str:<15} {dims_str}")
print(f"{'='*120}\n")
