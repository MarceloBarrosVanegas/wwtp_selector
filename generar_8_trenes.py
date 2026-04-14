#!/usr/bin/env python3
"""
Genera las 8 alternativas de trenes comparativos solicitadas,
organizadas en carpetas separadas bajo resultados/trenes_comparativos_8_alternativas/.
"""

import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generar_tren import generar_documento_tren

# Parámetros base comunes para todas las alternativas
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
    {
        "codigo": "T1",
        "carpeta": "T1_uasb_fp_sed_cloro",
        "nombre": "T1 – Rejillas + Desarenador + UASB + Filtro Percolador + Sedimentador Secundario + Cloro + Lecho de Secado",
        "unidades": [
            "rejillas",
            "desarenador",
            "uasb",
            "filtro_percolador",
            "sedimentador_sec",
            "cloro",
            "lecho_secado",
        ],
    },
    {
        "codigo": "T2",
        "carpeta": "T2_uasb_humedal_cloro",
        "nombre": "T2 – Rejillas + Desarenador + UASB + Humedal Vertical + Cloro + Lecho de Secado",
        "unidades": [
            "rejillas",
            "desarenador",
            "uasb",
            "humedal_vertical",
            "cloro",
            "lecho_secado",
        ],
    },
    {
        "codigo": "T3",
        "carpeta": "T3_uasb_baf_cloro",
        "nombre": "T3 – Rejillas + Desarenador + UASB + BAF + Cloro + Lecho de Secado",
        "unidades": [
            "rejillas",
            "desarenador",
            "uasb",
            "baf",
            "cloro",
            "lecho_secado",
        ],
    },
    {
        "codigo": "T4",
        "carpeta": "T4_uasb_taf_sed_cloro",
        "nombre": "T4 – Rejillas + Desarenador + UASB + TAF + Sedimentador Secundario + Cloro + Lecho de Secado",
        "unidades": [
            "rejillas",
            "desarenador",
            "uasb",
            "taf",
            "sedimentador_sec",
            "cloro",
            "lecho_secado",
        ],
    },
    {
        "codigo": "T5",
        "carpeta": "T5_abr_fp_sed_cloro",
        "nombre": "T5 – Rejillas + Desarenador + ABR-RAP + Filtro Percolador + Sedimentador Secundario + Cloro + Lecho de Secado",
        "unidades": [
            "rejillas",
            "desarenador",
            "abr_rap",
            "filtro_percolador",
            "sedimentador_sec",
            "cloro",
            "lecho_secado",
        ],
    },
    {
        "codigo": "T6",
        "carpeta": "T6_abr_humedal_cloro",
        "nombre": "T6 – Rejillas + Desarenador + ABR-RAP + Humedal Vertical + Cloro + Lecho de Secado",
        "unidades": [
            "rejillas",
            "desarenador",
            "abr_rap",
            "humedal_vertical",
            "cloro",
            "lecho_secado",
        ],
    },
    {
        "codigo": "T7",
        "carpeta": "T7_abr_baf_cloro",
        "nombre": "T7 – Rejillas + Desarenador + ABR-RAP + BAF + Cloro + Lecho de Secado",
        "unidades": [
            "rejillas",
            "desarenador",
            "abr_rap",
            "baf",
            "cloro",
            "lecho_secado",
        ],
    },
    {
        "codigo": "T8",
        "carpeta": "T8_abr_taf_sed_cloro",
        "nombre": "T8 – Rejillas + Desarenador + ABR-RAP + TAF + Sedimentador Secundario + Cloro + Lecho de Secado",
        "unidades": [
            "rejillas",
            "desarenador",
            "abr_rap",
            "taf",
            "sedimentador_sec",
            "cloro",
            "lecho_secado",
        ],
    },
]

RAIZ = "resultados/trenes_comparativos_8_alternativas"


def main():
    os.makedirs(RAIZ, exist_ok=True)
    resumen = []

    for t in TRENES:
        print(f"\n{'='*70}")
        print(f"Generando {t['codigo']} ...")
        print(f"{'='*70}")

        entrada = {
            **PARAMETROS_BASE,
            "nombre_tren": t["nombre"],
            "unidades": t["unidades"],
        }

        output_dir = os.path.join(RAIZ, t["carpeta"])
        nombre_archivo = t["carpeta"]

        tex_ok = False
        pdf_ok = False
        error_msg = ""

        try:
            tex_path = generar_documento_tren(
                entrada=entrada,
                output_dir=output_dir,
                nombre_archivo=nombre_archivo,
                compilar_pdf=True,
                usar_ia=False,
            )
            tex_ok = os.path.exists(tex_path)
            pdf_path = os.path.splitext(tex_path)[0] + ".pdf"
            pdf_ok = os.path.exists(pdf_path)
        except Exception as e:
            error_msg = str(e)
            traceback.print_exc()

        resumen.append({
            "codigo": t["codigo"],
            "nombre_corto": t["carpeta"],
            "unidades": " -> ".join(t["unidades"]),
            "carpeta_salida": output_dir,
            "tex": tex_ok,
            "pdf": pdf_ok,
            "error": error_msg,
        })

    # Imprimir resumen
    print(f"\n\n{'='*70}")
    print("RESUMEN DE GENERACIÓN")
    print(f"{'='*70}")
    print(f"{'Cod':<5} {'Carpeta':<25} {'TeX':>4} {'PDF':>4} {'Error':<30}")
    print("-" * 70)
    for r in resumen:
        tex_str = "SÍ" if r["tex"] else "NO"
        pdf_str = "SÍ" if r["pdf"] else "NO"
        err_str = r["error"] if r["error"] else "-"
        print(f"{r['codigo']:<5} {r['nombre_corto']:<25} {tex_str:>4} {pdf_str:>4} {err_str:<30}")

    print(f"\n{'='*70}")
    print("Generación finalizada.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
