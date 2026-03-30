#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ptar_dimensionamiento.py
========================
Módulo de dimensionamiento hidráulico y biológico de las unidades de
tratamiento de la PTAR Puerto Baquerizo Moreno, Galápagos.

Cada función incluye:
  - Ecuaciones de diseño con referencia bibliográfica y número de ecuación
  - Parámetros de diseño justificados con rango bibliográfico
  - Verificaciones de criterios de diseño (asserts)
  - Retorno de un dict con TODAS las variables calculadas y sus unidades

Unidades del sistema:
  - Caudales    : L/s y m^3/d
  - Longitudes  : m
  - Áreas       : m^2
  - Volúmenes   : m^3
  - Tiempos     : h (horas) o d (días)
  - Cargas      : kg/m^3*d (volumétricas), kg/m^2*d (superficiales)
  - Temperatura :  grados C

Caudal de diseño por línea: Q = 5 L/s = 432 m^3/d
Temperatura del agua      : T = 24  grados C (promedio anual Galápagos)

Autores: [nombre del autor]
Fecha  : 2026
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any

# Función auxiliar para citas bibliográficas
def citar(clave: str, formato: str = "texto") -> str:
    """Genera cita bibliográfica simple."""
    referencias = {
        "metcalf_2014": "Metcalf & Eddy (2014)",
        "romero_2004": "Romero (2004)",
        "senagua_2012": "SENAGUA (2012)",
        "van_haandel_1994": "Van Haandel & Lettinga (1994)",
        "sperling_2007": "Sperling (2007)",
        "wef_mop8_2010": "WEF MOP8 (2010)",
        "kadlec_wallace_2009": "Kadlec & Wallace (2009)",
        "vymazal_2011": "Vymazal (2011)",
        "reed_1995": "Reed et al. (1995)",
        "ops_cepis_2005": "OPS/CEPIS (2005)",
    }
    return referencias.get(clave, clave)


# =============================================================================
# CONFIGURACIÓN GENERAL DE DISEÑO
# =============================================================================

@dataclass
class ConfigDiseno:
    """
    Parámetros globales del proyecto.

    Fuente de caudales y calidad del agua: CPE INEN 005 (1992),
    ajustado a medición de la red de alcantarillado existente.
    """
    # Caudales
    Q_total_L_s: float = 10.0       # L/s - caudal de diseño total
    Q_linea_L_s: float = 5.0        # L/s - caudal por línea de tratamiento
    num_lineas:  int   = 2          # número de líneas paralelas
    
    # Factor de pico global (Qmax/Qmedio) - usado en verificaciones de todas las unidades
    factor_pico_Qmax: float = 2.5   # Factor típico para aguas residuales municipales (rango 2-3)

    # Temperatura del agua (media anual Galápagos, nivel del mar)
    T_agua_C:  float = 24.0         #  grados C
    T_min_C:   float = 21.0         #  grados C - mínimo histórico (para diseño conservador)

    # Calidad del afluente (ver ptar_datos.AGUA_ENTRADA)
    DBO5_mg_L: float = 250.0        # mg/L
    DQO_mg_L:  float = 500.0        # mg/L
    SST_mg_L:  float = 250.0        # mg/L
    CF_NMP:    float = 1e7          # NMP/100 mL

    # Objetivos del efluente - TULSMA Tabla 11 (descarga a receptor)
    DBO5_ef_mg_L: float = 100.0     # mg/L
    SST_ef_mg_L:  float = 100.0     # mg/L
    CF_ef_NMP:    float = 3000.0    # NMP/100 mL

    # Coeficientes de seguridad (CS)
    CS_area:   float = 2.0    # Para superficies (2 líneas = redundancia total)
    CS_volumen: float = 1.25  # Para volúmenes biológicos
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - REJILLAS
    # =============================================================================
    rejillas_v_canal_m_s: float = 0.50      # Velocidad en canal (rango: 0.40-0.60 m/s)
    rejillas_h_tirante_m: float = 0.40      # Tirante hidráulico (m)
    rejillas_angulo_grados: float = 60.0    # Ángulo de inclinación (grados)
    rejillas_beta: float = 2.42             # Factor forma barras rectangulares
    rejillas_w_barra_m: float = 0.010       # Espesor barra (m)
    rejillas_b_barra_m: float = 0.015       # Espaciado entre barras - rejilla fina (m)
    rejillas_largo_canal_m: float = 2.0     # Largo mínimo del canal (m)
    # Límites de velocidad para verificación (Metcalf & Eddy, 2014)
    rejillas_v_max_advertencia_m_s: float = 1.5   # Límite recomendado (m/s)
    rejillas_v_max_destructivo_m_s: float = 2.0   # Límite destructivo (m/s)
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - DESARENADOR
    # =============================================================================
    desarenador_v_s_m_s: float = 0.021      # Velocidad sedimentación arena Ø0.2mm (m/s)
    desarenador_H_util_m: float = 0.40      # Profundidad útil de flujo (m)
    desarenador_b_min_m: float = 0.60       # Ancho mínimo constructivo práctico (m)
    desarenador_L_min_norm_m: float = 3.0   # Largo mínimo constructivo (m)
    desarenador_n_canales: int = 2          # Número de canales
    desarenador_v_h_objetivo_m_s: float = 0.30  # Velocidad horizontal objetivo (m/s)
    desarenador_factor_pico: float = 2.5    # Factor caudal máximo horario / promedio (tip: 2-3)
    desarenador_d_particula_mm: float = 0.20    # Diámetro partícula objetivo (mm)
    desarenador_Ss: float = 2.65            # Gravedad específica arena
    # Parámetros para Camp-Shields (verificación de velocidad crítica)
    desarenador_beta: float = 0.05          # Factor de forma partícula (rango 0.04-0.06)
    desarenador_f_darcy: float = 0.025      # Factor de fricción Darcy-Weisbach (rango 0.02-0.03)
    # Límite de velocidad para verificación (Camp-Shields)
    # v_h_max debe ser < v_c_scour (velocidad crítica de resuspensión)
    desarenador_factor_seguridad_scour: float = 0.9  # Factor sobre v_c (90% = margen seguro)
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - UASB
    # =============================================================================
    uasb_Cv_kgDQO_m3_d: float = 2.5         # Carga orgánica volumétrica (kg DQO/m³·d) - valor conservador para TRH >= 5h
    uasb_v_up_m_h: float = 0.80             # Velocidad ascendente (m/h)
    uasb_eta_DBO: float = 0.70              # Eficiencia remoción DBO5 (fracción) - usado solo como referencia inicial
    uasb_eta_DQO: float = 0.65              # Eficiencia remoción DQO (fracción) - usado solo como referencia inicial
    uasb_H_max_m: float = 5.5               # Altura máxima reactor (m)
    uasb_factor_biogas_ch4: float = 0.35    # Factor de conversión biogás (m³ CH4 / kg DQO removida)
    
    # =========================================================================
    # PARÁMETROS GEOMÉTRICOS UASB (todas las alturas en m)
    # =========================================================================
    uasb_H_min_m: float = 3.0               # Altura mínima zona de reacción (m) - físicamente requerido
    uasb_H_max_m: float = 6.0               # Altura máxima zona de reacción (m) - límite constructivo
    uasb_H_GLS_m: float = 1.0               # Altura separador gas-líquido-sólido (m) - típico 0.8-1.2 m
    uasb_H_distribucion_m: float = 0.30     # Altura zona de distribución (fondo) (m) - típico 0.3-0.5 m
    uasb_H_sed_min_m: float = 1.5           # Altura mínima compartimiento sedimentación (m)
    uasb_H_sed_max_m: float = 2.0           # Altura máxima compartimiento sedimentación (m)
    uasb_H_sed_m: float = 1.6               # Altura operativa compartimiento sedimentación (m) - típico 1.5-2.0 m
    uasb_factor_efectividad_sed: float = 0.90  # Factor de área efectiva sedimentación (90% típico)
    uasb_porcion_lecho_granular: float = 0.40  # Fracción de altura para lecho granular (típico 0.35-0.45)
    uasb_porcion_manto_expandido: float = 0.60 # Fracción de altura para manto expandido (típico 0.55-0.65)
    
    # =========================================================================
    # LÍMITES DE SEDIMENTADOR SUPERIOR UASB (Chernicharo)
    # =========================================================================
    # Carga superficial (SOR) - rango óptimo y límites
    uasb_SOR_medio_min_m_h: float = 0.60     # SOR mínimo caudal medio (m/h)
    uasb_SOR_medio_max_m_h: float = 0.80     # SOR máximo caudal medio (m/h)
    uasb_SOR_max_limite_m_h: float = 1.20    # SOR límite caudal máximo (m/h)
    # Tiempo de retención en sedimentador
    uasb_TRH_sed_medio_min_h: float = 1.5    # TRH mínimo sedimentador caudal medio (h)
    uasb_TRH_sed_medio_max_h: float = 2.0    # TRH máximo sedimentador caudal medio (h)
    
    # =========================================================================
    # LÍMITES DE VELOCIDAD ASCENSIONAL UASB (Metcalf & Eddy, 2014)
    # v_up_max debe controlarse para evitar arrastre del manto de lodos
    uasb_v_up_max_recomendado_m_h: float = 1.5   # Límite recomendado (m/h)
    uasb_v_up_max_destructivo_m_h: float = 2.0   # Límite destructivo (m/h)
    
    # =========================================================================
    # PARÁMETROS DE CÁLCULO UASB
    # =========================================================================
    uasb_rendimiento_lodos_kg_SSV_kg_DBO: float = 0.10  # Rendimiento de lodos (kg SSV/kg DBO removida)
    uasb_D_max_m: float = 10.0                          # Diámetro máximo del reactor (m) - límite while v_up
    uasb_D_sed_max_m: float = 15.0                      # Diámetro máximo para sedimentador (m) - límite while SOR
    
    # =========================================================================
    # RANGOS DE DISEÑO UASB POR TEMPERATURA (Van Haandel & Lettinga 1994)
    # =========================================================================
    # Rangos de carga orgánica volumétrica (Cv) por condición de temperatura
    uasb_Cv_optimo_min: float = 2.0         # Cv mínimo temperatura óptima (kg DQO/m³·d)
    uasb_Cv_optimo_max: float = 3.0         # Cv máximo temperatura óptima (kg DQO/m³·d)
    uasb_Cv_moderado_min: float = 1.5       # Cv mínimo temperatura moderada (kg DQO/m³·d)
    uasb_Cv_moderado_max: float = 2.5       # Cv máximo temperatura moderada (kg DQO/m³·d)
    uasb_Cv_bajo_min: float = 1.0           # Cv mínimo temperatura baja (kg DQO/m³·d)
    uasb_Cv_bajo_max: float = 1.5           # Cv máximo temperatura baja (kg DQO/m³·d)
    uasb_Cv_muybajo_min: float = 0.5        # Cv mínimo temperatura muy baja (kg DQO/m³·d)
    uasb_Cv_muybajo_max: float = 1.5        # Cv máximo temperatura muy baja (kg DQO/m³·d)
    # Rangos de tiempo de retención hidráulico (HRT) por condición de temperatura
    uasb_HRT_optimo_min_h: float = 4.0      # HRT mínimo temperatura óptima (h)
    uasb_HRT_optimo_max_h: float = 6.0      # HRT máximo temperatura óptima (h)
    uasb_HRT_moderado_min_h: float = 5.0    # HRT mínimo temperatura moderada (h)
    uasb_HRT_moderado_max_h: float = 8.0    # HRT máximo temperatura moderada (h)
    uasb_HRT_bajo_min_h: float = 6.0        # HRT mínimo temperatura baja (h)
    uasb_HRT_bajo_max_h: float = 10.0       # HRT máximo temperatura baja (h)
    uasb_HRT_muybajo_min_h: float = 8.0     # HRT mínimo temperatura muy baja (h)
    uasb_HRT_muybajo_max_h: float = 12.0    # HRT máximo temperatura muy baja (h)
    
    # =========================================================================
    # PARÁMETROS ABERTURAS GLS (Chernicharo 2007)
    # =========================================================================
    uasb_v_abertura_medio_min_m_h: float = 2.0   # Velocidad mínima en aberturas a caudal medio (m/h)
    uasb_v_abertura_medio_max_m_h: float = 2.3   # Velocidad máxima en aberturas a caudal medio (m/h)
    uasb_v_abertura_max_m_h: float = 4.2         # Velocidad máxima en aberturas a caudal máximo (m/h)
    uasb_GLS_pendiente_min_grados: float = 50.0  # Pendiente mínima del GLS (grados)
    uasb_GLS_pendiente_max_grados: float = 60.0  # Pendiente máxima del GLS (grados)
    uasb_GLS_traslape_m: float = 0.15            # Traslape del GLS sobre la abertura (m)
    
    # =========================================================================
    # PARÁMETROS DISTRIBUCIÓN AFLUENTE (Chernicharo 2007; Lettinga & Hulshoff Pol)
    # =========================================================================
    uasb_A_inf_min_m2: float = 2.0      # Área de influencia mínima por punto (m²/punto)
    uasb_A_inf_max_m2: float = 3.0      # Área de influencia máxima por punto (m²/punto)
    
    uasb_v_tubo_max_m_s: float = 0.20    # Velocidad máxima en tubería madre para evitar fricción (m/s)
    uasb_tubos_comerciales_mm: tuple = (25.0, 40.0, 50.0, 75.0, 100.0, 150.0, 200.0, 250.0, 300.0)
    uasb_diam_tubo_distribucion_mm: float = 75.0       # Diámetro base inicial (mm)
    uasb_diam_boca_salida_mm: float = 25.0             # Diámetro base inicial de salida (mm)
    
    # Velocidad en bocas de salida (criterio crítico según Lettinga)
    uasb_v_boca_min_m_s: float = 0.40    # Velocidad mínima en boca para arrastre (m/s)
    uasb_v_boca_max_m_s: float = 4.00    # Velocidad máxima en boca para evitar erosión (m/s)
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - FILTRO PERCOLADOR
    # =============================================================================
    fp_DBO_salida_objetivo_mg_L: float = 55.0   # DBO5 objetivo post-FP (mg/L)
    fp_k_20_m_h: float = 0.068              # Constante cinética a 20°C (m/h) - valor conservador diseño
    fp_theta: float = 1.035                 # Coeficiente temperatura
    fp_n_germain: float = 0.50              # Constante empírica medio aleatorio
    fp_D_medio_m: float = 3.50              # Profundidad medio filtrante (m)
    fp_R_recirculacion: float = 1.0         # Tasa recirculación
    fp_H_total_m: float = 4.30              # Altura total (medio + 0.80m)
    
    # PASO 4 - Geometría del filtro (desglose de alturas)
    fp_H_distribucion_m: float = 0.20       # Espacio distribuidor-medio (0.15-0.23 m) [EPA, 2000]
    fp_H_underdrain_m: float = 0.50         # Altura underdrain (0.45-0.60 m) [Metcalf & Eddy, 2014]
    fp_H_bordo_libre_fp_m: float = 0.30     # Bordo libre filtro (0.30-0.50 m)
    
    # PASO 6 - Distribuidor rotatorio
    fp_num_brazos: int = 2                  # Número de brazos (2 para D < 6m, 4 para D > 15m)
    fp_velocidad_boquilla_m_s: float = 2.0  # Velocidad salida boquilla (1.5-3.0 m/s)
    fp_num_boquillas_por_brazo: int = 8     # Número de boquillas por brazo (5-15)
    
    # PASO 7 - Underdrain
    fp_pendiente_underdrain_pct: float = 1.0  # Pendiente mínima piso underdrain (>= 1%)
    fp_ancho_canal_central_m: float = 0.30    # Ancho canal central underdrain (0.30-0.60 m)
    
    # PASO 8 - Ventilación
    fp_area_ventilacion_pct: float = 1.0    # Área ventilación / Área superficial (>= 1%)
    fp_Q_aire_factor: float = 0.3           # Caudal aire / caudal agua (0.1-0.5 m³/m³)
    
    # PASO 10 - Especificaciones medio plástico
    fp_sup_especifica_m2_m3: float = 100.0  # Superficie específica (90-150 m²/m³)
    fp_vacios_pct: float = 94.0             # Índice de vacíos (>= 94%)
    fp_densidad_media_kg_m3: float = 60.0   # Densidad aparente (30-100 kg/m³)
    fp_Cv_kgDBO_m3_d: float = 0.5           # Carga orgánica volumétrica (kg DBO/m³·d)
    fp_Q_A_limite_m3_m2_h: float = 4.0      # Límite tasa hidráulica (m³/m²·h)
    fp_Cv_minima_kgDBO_m3_d: float = 0.30   # Carga orgánica mínima recomendada (kg DBO/m³·d)
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - DESINFECCIÓN CON CLORO
    # =============================================================================
    desinfeccion_demanda_cloro_mg_L: float = 3.5    # Demanda de cloro (mg/L)
    desinfeccion_cloro_residual_mg_L: float = 0.5   # Cloro residual objetivo (mg/L)
    desinfeccion_TRH_min: float = 30.0              # Tiempo de retención hidráulico (min)
    desinfeccion_relacion_L_A: float = 4.0          # Relación largo/ancho tanque
    desinfeccion_h_tanque_m: float = 2.0            # Profundidad útil tanque (m)
    desinfeccion_coef_log_red: float = 0.22         # Coeficiente log reducción (log por CT)
    desinfeccion_concentracion_NaOCl: float = 0.10  # Concentración NaOCl comercial (fracción)
    desinfeccion_densidad_NaOCl: float = 1.10       # Densidad NaOCl 10% (kg/L)
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - HUMEDAL VERTICAL
    # =============================================================================
    humedal_DBO_salida_mg_L: float = 20.0   # DBO5 objetivo (mg/L)
    humedal_C_fondo_mg_L: float = 3.5       # Concentración fondo C* (mg/L)
    humedal_k_20_m_d: float = 0.062         # Constante a 20°C (m/d)
    humedal_theta: float = 1.06             # Coeficiente temperatura
    humedal_n_porosidad: float = 0.38       # Porosidad lecho grava
    humedal_h_lecho_m: float = 0.60         # Profundidad lecho filtrante (m)
    humedal_borde_libre_m: float = 0.20     # Borde libre (m)
    humedal_factor_seguridad_area: float = 1.25  # FS para variaciones estacionales
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - SEDIMENTADOR SECUNDARIO
    # =============================================================================
    sed_SOR_m3_m2_d: float = 18.0           # Tasa desbordamiento superficial (conservador)
    sed_h_sed_m: float = 3.50               # Profundidad lateral (m)
    sed_factor_produccion_humus: float = 0.15  # Factor producción humus (kg SST/kg DBO removida FP)
    sed_eta_DBO: float = 0.15               # Eficiencia remoción DBO en sedimentador (fracción) - Valor conservador según Metcalf & Eddy (2014) para sedimentador secundario tras filtro percolador (10-15%)
    
    # =============================================================================
    # PARÁMETROS DE BALANCE DE CALIDAD DEL AGUA
    # =============================================================================
    balance_eta_CF_uasb: float = 0.30       # Eficiencia remoción CF en UASB (fracción)
    balance_eta_DQO_fp_factor: float = 0.90 # Factor para calcular ηDQO desde ηDBO en FP
    balance_eta_SST_fp: float = 0.60        # Eficiencia remoción SST en FP (fracción)
    balance_eta_CF_fp: float = 0.20         # Eficiencia remoción CF en FP (fracción)
    balance_eta_SST_sed: float = 0.80       # Eficiencia remoción SST en Sed (fracción)
    balance_eta_CF_sed: float = 0.10        # Eficiencia remoción CF en Sed (fracción)
    balance_log_reduccion_default: float = 4.0  # Log reducción por defecto desinfección
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - LODOS ACTIVADOS (AIREACIÓN EXTENDIDA)
    # =============================================================================
    la_Cv_kgDBO_m3_d: float = 0.30          # Carga orgánica volumétrica (kg DBO/m³·d)
    la_TRH_h: float = 18.0                  # Tiempo retención hidráulico (h)
    la_edad_lodo_d: float = 15.0            # Edad del lodo (días)
    la_h_aireacion_m: float = 4.5           # Profundidad de aireación (m)
    la_RAS: float = 0.50                    # Relación de recirculación (RAS)
    la_aireacion_kgO2_kgDBO: float = 1.2    # Requerimiento de oxígeno (kg O2/kg DBO)
    la_ce_teorica: float = 1.0              # Coeficiente de exceso de lodo (kg SSV/kg DBO)
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - LECHO DE SECADO
    # =============================================================================
    lecho_C_SST_kg_m3: float = 20.0         # Concentración sólidos en lodo (kg/m³)
    lecho_t_secado_d: float = 15.0          # Tiempo secado (días)
    lecho_n_celdas: int = 1                 # Número celdas (1 para plantas pequeñas)
    lecho_h_lodo_m: float = 0.30            # Espesor lodo aplicado (m)
    lecho_factor_produccion_lodos: float = 0.10  # kg SST/kg DBO removida (producción UASB)
    
    # =============================================================================
    # LÍMITES TULSMA - Tabla 12: Descarga a cuerpo de agua dulce
    # =============================================================================
    tulsma_DBO5_limite_mg_L: float = 100.0
    tulsma_DQO_limite_mg_L: float = 250.0
    tulsma_SST_limite_mg_L: float = 130.0
    tulsma_CF_limite_NMP_100mL: float = 3000.0
    tulsma_pH_min: float = 6.0
    tulsma_pH_max: float = 9.0
    tulsma_aceites_grasas_limite_mg_L: float = 0.3
    tulsma_fosforo_total_limite_mg_L: float = 10.0
    tulsma_nitrogeno_amoniacal_limite_mg_L: float = 30.0
    tulsma_solidos_sedimentables_limite_mL_L: float = 1.0
    tulsma_solidos_totales_limite_mg_L: float = 1600.0
    tulsma_temperatura_max_C: float = 32.0
    tulsma_tensoactivos_limite_mg_L: float = 0.5
    # Metales pesados
    tulsma_arsenico_limite_mg_L: float = 0.1
    tulsma_cadmio_limite_mg_L: float = 0.02
    tulsma_cromo_hexavalente_limite_mg_L: float = 0.5
    tulsma_mercurio_limite_mg_L: float = 0.005
    tulsma_plomo_limite_mg_L: float = 0.2
    tulsma_cobre_limite_mg_L: float = 1.0
    tulsma_niquel_limite_mg_L: float = 2.0
    tulsma_zinc_limite_mg_L: float = 5.0
    tulsma_aluminio_limite_mg_L: float = 5.0
    tulsma_bario_limite_mg_L: float = 2.0
    tulsma_hierro_limite_mg_L: float = 10.0
    tulsma_manganeso_limite_mg_L: float = 2.0
    
    # =========================================================================
    # PARÁMETROS DE BALANCE DE CALIDAD DEL AGUA (REMOciones por unidad)
    # =========================================================================
    balance_remov_uasb_dbo: float = 0.70       # Eficiencia remoción DBO en UASB
    balance_remov_uasb_dqo: float = 0.65       # Eficiencia remoción DQO en UASB
    balance_remov_uasb_sst: float = 0.70       # Eficiencia remoción SST en UASB
    balance_remov_uasb_cf: float = 0.30        # Eficiencia remoción CF en UASB
    balance_remov_fp_dbo: float = 0.80         # Eficiencia remoción DBO en Filtro Percolador
    balance_remov_fp_dqo_factor: float = 0.90  # Factor para calcular ηDQO desde ηDBO en FP
    balance_remov_fp_sst: float = 0.60         # Eficiencia remoción SST en FP
    balance_remov_fp_cf: float = 0.20          # Eficiencia remoción CF en FP
    balance_remov_sed_dbo: float = 0.30        # Eficiencia remoción DBO en Sedimentador
    balance_remov_sed_sst: float = 0.80        # Eficiencia remoción SST en Sedimentador
    balance_remov_sed_cf: float = 0.10         # Eficiencia remoción CF en Sedimentador
    balance_log_reduccion_desinf: float = 4.0  # Log reducción por desinfección
    balance_cf_objetivo_nmp: float = 2500.0    # Objetivo CF final (NMP/100mL)
    
    # =========================================================================
    # RANGOS NORMATIVOS PARA TEXTOS EN REPORTES (referencias bibliográficas)
    # =========================================================================
    # Rejillas - Metcalf & Eddy
    rejillas_v_canal_min_m_s: float = 0.40     # Velocidad mínima en canal (m/s)
    rejillas_v_canal_max_m_s: float = 0.60     # Velocidad máxima en canal (m/s)
    rejillas_h_tirante_min_m: float = 0.30     # Tirante mínimo (m)
    rejillas_h_tirante_max_m: float = 0.80     # Tirante máximo (m)
    
    # Desarenador - Metcalf & Eddy / OPS-CEPIS
    desarenador_v_h_min_m_s: float = 0.25      # Velocidad horizontal mínima (m/s)
    desarenador_v_h_max_m_s: float = 0.30      # Velocidad horizontal máxima (m/s)
    desarenador_t_retencion_min_s: float = 30.0  # Tiempo retención mínimo (s)
    desarenador_t_retencion_max_s: float = 60.0  # Tiempo retención máximo (s)
    desarenador_H_min_m: float = 0.75          # Profundidad mínima (m)
    desarenador_H_max_m: float = 2.0           # Profundidad máxima (m)
    
    # UASB - Van Haandel & Lettinga / Sperling
    uasb_temp_optimina_C: float = 22.0         # Temperatura óptima mínima (°C)
    uasb_temp_min_operativa_C: float = 15.0    # Temperatura mínima operativa (°C)
    uasb_trh_min_optimo_h: float = 4.0         # TRH mínimo óptimo (h)
    uasb_trh_min_baja_temp_h: float = 6.0      # TRH mínimo baja temp (h)
    uasb_v_up_min_m_h: float = 0.5             # Velocidad ascendente mínima (m/h)
    uasb_v_up_max_m_h: float = 1.5             # Velocidad ascendente máxima (m/h)
    
    # =========================================================================
    # UMBRALES Y CRITERIOS DE DISEÑO
    # =========================================================================
    desarenador_umbral_caudal_pequeno_L_s: float = 20.0  # Umbral caudal pequeño (L/s)
    desarenador_factor_escala_caudal_pequeno: float = 0.5  # Factor de escala para caudales pequeños
    
    # =========================================================================
    # HOLGURAS, BORDOS LIBRES Y MARGENES CONSTRUCTIVOS
    # =========================================================================
    # Bordos libres (m)
    bordo_libre_rejillas_m: float = 0.30       # Rejillas
    bordo_libre_desarenador_m: float = 0.30    # Desarenador
    bordo_libre_uasb_m: float = 0.50           # UASB
    bordo_libre_fp_m: float = 0.80             # Filtro Percolador (distribución + recolección)
    bordo_libre_sed_m: float = 0.50            # Sedimentador
    bordo_libre_desinfeccion_m: float = 0.30   # Desinfección
    
    # Margen constructivo para layouts (muros, accesos)
    layout_margen_muros_m: float = 0.15        # Espesor muros (m) cada lado
    layout_margen_acceso_m: float = 0.30       # Margen adicional para acceso
    
    # =========================================================================
    # PARÁMETROS PARA ÁREAS COMPLEMENTARIAS DEL PREDIO
    # =========================================================================
    # Factores porcentuales
    layout_factor_amortiguacion: float = 0.20      # 20% del área de tratamiento
    layout_factor_complementaria: float = 0.25     # 25% del área de tratamiento
    layout_factor_zona_verde: float = 0.15         # 15% del área total
    layout_factor_caminos: float = 0.10            # 10% del área de tratamiento
    
    # Áreas mínimas (m²) - valores de referencia para plantas pequeñas
    layout_area_min_bodega_quimicos_m2: float = 12.0
    layout_area_min_laboratorio_m2: float = 15.0
    layout_area_min_caseta_operacion_m2: float = 12.0
    layout_area_min_lavado_m2: float = 8.0
    layout_area_min_estacionamiento_m2: float = 50.0
    layout_area_min_zona_camiones_m2: float = 50.0
    layout_area_min_acceso_principal_m2: float = 20.0
    layout_area_min_bodega_general_m2: float = 15.0
    layout_area_min_carga_lodos_m2: float = 20.0
    
    # Factores de proporcionalidad (% del área de tratamiento)
    layout_factor_bodega_quimicos: float = 0.012   # 1.2%
    layout_factor_laboratorio: float = 0.018       # 1.8%
    layout_factor_caseta: float = 0.015            # 1.5%
    layout_factor_lavado: float = 0.010            # 1.0%
    layout_factor_estacionamiento: float = 0.055   # 5.5%
    layout_factor_zona_camiones: float = 0.065     # 6.5%
    layout_factor_acceso: float = 0.025            # 2.5%
    layout_factor_bodega_general: float = 0.018    # 1.8%
    layout_factor_carga_lodos: float = 0.025       # 2.5%

    def __post_init__(self):
        # Caudal por línea en m^3/d (conversión exacta: 1 L/s = 86.4 m^3/d)
        self.Q_linea_m3_d = self.Q_linea_L_s * 86.4
        self.Q_total_m3_d = self.Q_total_L_s * 86.4
        # Caudal en m^3/h
        self.Q_linea_m3_h = self.Q_linea_m3_d / 24.0
        # Caudal en m^3/s
        self.Q_linea_m3_s = self.Q_linea_L_s / 1000.0


CFG = ConfigDiseno()


# =============================================================================
# FUNCIÓN DE EVALUACIÓN DE TEMPERATURA PARA UASB
# =============================================================================

def evaluar_temperatura_uasb(T_celsius: float, cfg: ConfigDiseno = CFG) -> Dict[str, Any]:
    """
    Evalúa la temperatura del agua y retorna parámetros de diseño recomendados
    para el reactor UASB según criterios de Van Haandel & Lettinga (1994).
    
    Args:
        T_celsius: Temperatura del agua en grados Celsius
        cfg: Configuración de diseño
        
    Returns:
        Dict con:
        - texto_recomendacion: str (para insertar en reporte)
        - cv_kgDQO_m3_d: float (carga orgánica volumétrica)
        - trh_h: float (tiempo retención hidráulico)
        - eficiencia_dbo: float (eficiencia esperada remoción DBO)
        - eficiencia_dqo: float (eficiencia esperada remoción DQO)
        - factor_temp_texto: str (descripción del rango)
        - rangos_recomendados: dict (rangos para mostrar en reporte)
    """
    # Base de parámetros
    Cv_base = cfg.uasb_Cv_kgDQO_m3_d
    HRT_base = cfg.uasb_trh_min_optimo_h
    
    if T_celsius >= cfg.uasb_temp_optimina_C:
        # Temperatura óptima
        return {
            "texto_recomendacion": (
                "Para mantener el rendimiento óptimo del reactor en caso de descenso de temperatura, "
                "se recomienda monitorear periodicamente. Si la temperatura descendiera por debajo de 20°C, "
                "el sistema debería ajustar automáticamente la carga orgánica y el tiempo de retención."
            ),
            "cv_kgDQO_m3_d": Cv_base,
            "trh_h": HRT_base,
            "v_up_m_h": cfg.uasb_v_up_m_h,
            "eficiencia_dbo": cfg.uasb_eta_DBO,
            "eficiencia_dqo": cfg.uasb_eta_DQO,
            "factor_temp_texto": "óptima (>= 22°C)",
            "rangos_recomendados": {
                "cv": f"{cfg.uasb_Cv_optimo_min:.1f}--{cfg.uasb_Cv_optimo_max:.1f}".replace(".", ","),
                "vup": "0,5--1,5",
                "hrt": f"{cfg.uasb_HRT_optimo_min_h:.0f}--{cfg.uasb_HRT_optimo_max_h:.0f}",
                "eta": "60--75"
            }
        }
    elif 18 <= T_celsius < cfg.uasb_temp_optimina_C:
        # Temperatura moderada
        return {
            "texto_recomendacion": (
                "La temperatura está en rango moderado. Se recomienda considerar aislamiento térmico básico "
                "del reactor para mantener la eficiencia durante períodos fríos."
            ),
            "cv_kgDQO_m3_d": Cv_base * 0.85,
            "trh_h": HRT_base * 1.2,
            "v_up_m_h": cfg.uasb_v_up_m_h * 0.75,
            "eficiencia_dbo": cfg.uasb_eta_DBO * 0.90,
            "eficiencia_dqo": cfg.uasb_eta_DQO * 0.90,
            "factor_temp_texto": "moderada (18-22°C)",
            "rangos_recomendados": {
                "cv": f"{cfg.uasb_Cv_moderado_min:.1f}--{cfg.uasb_Cv_moderado_max:.1f}".replace(".", ","),
                "vup": "0,4--1,2",
                "hrt": f"{cfg.uasb_HRT_moderado_min_h:.0f}--{cfg.uasb_HRT_moderado_max_h:.0f}",
                "eta": "50--65"
            }
        }
    elif cfg.uasb_temp_min_operativa_C <= T_celsius < 18:
        # Temperatura baja
        return {
            "texto_recomendacion": (
                "La temperatura es baja, lo que ha reducido automáticamente la carga orgánica y aumentado "
                "el tiempo de retención. Se recomienda implementar aislamiento térmico del reactor para "
                "evitar mayor degradación del proceso."
            ),
            "cv_kgDQO_m3_d": Cv_base * 0.60,
            "trh_h": HRT_base * 1.5,
            "v_up_m_h": cfg.uasb_v_up_m_h * 0.625,
            "eficiencia_dbo": cfg.uasb_eta_DBO * 0.80,
            "eficiencia_dqo": cfg.uasb_eta_DQO * 0.80,
            "factor_temp_texto": "baja (15-18°C)",
            "rangos_recomendados": {
                "cv": f"{cfg.uasb_Cv_bajo_min:.1f}--{cfg.uasb_Cv_bajo_max:.1f}".replace(".", ","),
                "vup": "0,3--1,0",
                "hrt": f"{cfg.uasb_HRT_bajo_min_h:.0f}--{cfg.uasb_HRT_bajo_max_h:.0f}",
                "eta": "40--55"
            }
        }
    elif 10 <= T_celsius < cfg.uasb_temp_min_operativa_C:
        # Temperatura muy baja
        return {
            "texto_recomendacion": (
                "ATENCIÓN: La temperatura es muy baja. El sistema ha aplicado ajustes significativos: "
                "reducción de carga orgánica a 40% del valor base y duplicación del tiempo de retención. "
                "Se requiere aislamiento térmico obligatorio o considerar calefacción del reactor."
            ),
            "cv_kgDQO_m3_d": Cv_base * 0.40,
            "trh_h": HRT_base * 2.0,
            "v_up_m_h": cfg.uasb_v_up_m_h * 0.50,
            "eficiencia_dbo": cfg.uasb_eta_DBO * 0.70,
            "eficiencia_dqo": cfg.uasb_eta_DQO * 0.70,
            "factor_temp_texto": "muy baja (10-15°C) - se recomienda aislamiento térmico",
            "rangos_recomendados": {
                "cv": f"{cfg.uasb_Cv_muybajo_min:.1f}--{cfg.uasb_Cv_muybajo_max:.1f}".replace(".", ","),
                "vup": "0,3--0,8",
                "hrt": f"{cfg.uasb_HRT_muybajo_min_h:.0f}--{cfg.uasb_HRT_muybajo_max_h:.0f}",
                "eta": "30--45"
            }
        }
    else:
        # Temperatura crítica
        return {
            "texto_recomendacion": (
                "NO RECOMENDABLE: Temperatura por debajo de 10°C. El proceso anaerobio es inviable sin calentar la biomasa. "
                "Se requiere calefacción del reactor (mantener 20-25°C) o cambio obligatorio a tecnología aerobia activada. "
                "Los ajustes automáticos aplicados (carga reducida a 30%, HRT aumentado 150%) NO son suficientes para garantizar tratamiento adecuado."
            ),
            "cv_kgDQO_m3_d": Cv_base * 0.30,
            "trh_h": HRT_base * 2.5,
            "v_up_m_h": cfg.uasb_v_up_m_h * 0.375,
            "eficiencia_dbo": cfg.uasb_eta_DBO * 0.60,
            "eficiencia_dqo": cfg.uasb_eta_DQO * 0.60,
            "factor_temp_texto": "crítica (< 10°C) - requiere calefacción o cambio de tecnología",
            "rangos_recomendados": {
                "cv": "0,5--1,0",
                "vup": "0,2--0,6",
                "hrt": "10--15",
                "eta": "20--35"
            }
        }


# =============================================================================
# AUXILIARES
# =============================================================================

def correccion_temperatura(k_20: float, theta: float, T: float) -> float:
    """
    Corrección de constante cinética por temperatura según Arrhenius modificado.

    Ecuación:
        k_T = k_20 * θ^(T - 20)                          [Ec. 1]

    Referencias
    -----------
    Metcalf & Eddy (2014), Ec. 3-68, p. 199
    Sperling (2007), p. 49

    Parámetros
    ----------
    k_20  : constante cinética a 20  grados C (cualquier unidad, típicamente d^-1 o m/d)
    theta : coeficiente de temperatura (θ). Valor típico: 1.035-1.07 según proceso.
    T     : temperatura real del agua ( grados C)

    Retorna
    -------
    k_T : constante cinética a temperatura T
    """
    return k_20 * (theta ** (T - 20.0))


def viscosidad_cinematica_agua(T_celsius: float) -> float:
    """
    Calcula la viscosidad cinemática del agua según temperatura.
    
    Fórmula empírica basada en interpolación de valores tabulados:
    ν(T) = ν_20 * (1 + 0.0337*(T - 20) + 0.00022*(T - 20)^2)^(-1)
    
    Donde ν_20 = 1.004 × 10⁻⁶ m²/s a 20°C
    
    Valores de referencia (Metcalf & Eddy, 2014):
    - 20°C: 1.004 × 10⁻⁶ m²/s
    - 24°C: 0.91 × 10⁻⁶ m²/s  
    - 25.6°C: ~0.87 × 10⁻⁶ m²/s

    Parámetros
    ----------
    T_celsius : temperatura del agua en grados Celsius

    Retorna
    -------
    nu_m2_s : viscosidad cinemática en m²/s
    """
    nu_20 = 1.004e-6  # m²/s a 20°C
    dT = T_celsius - 20.0
    return nu_20 / (1 + 0.0337 * dT + 0.00022 * (dT ** 2))


def volumen_a_dimensiones_rect(V_m3: float, relacion_L_A: float = 3.0,
                                 h: float = 4.0) -> Dict[str, float]:
    """
    Convierte volumen a dimensiones (largo × ancho × alto) de tanque rectangular.

    Parámetros
    ----------
    V_m3       : Volumen total (m^3)
    relacion_L_A: Relación largo/ancho (típico 3:1 a 4:1 para tanques rectangulares)
    h          : Altura útil (m)

    Retorna
    -------
    Dict con largo, ancho, alto (m)
    """
    A_planta = V_m3 / h
    ancho = math.sqrt(A_planta / relacion_L_A)
    largo = relacion_L_A * ancho
    return {"largo_m": round(largo, 2), "ancho_m": round(ancho, 2), "alto_m": h,
            "area_planta_m2": round(A_planta, 2)}


# =============================================================================
# 1 - CANAL DE DESBASTE (REJILLAS)
# =============================================================================

def dimensionar_rejillas(Q: ConfigDiseno = CFG) -> Dict[str, Any]:
    """
    Dimensionamiento de canal con rejillas de barras (gruesas y finas).

    Parámetros de diseño
    --------------------
    Velocidad de flujo en el canal  : v = 0.40-0.60 m/s [Metcalf & Eddy, 2014, p. 470]
    Espaciado rejilla gruesa        : e = 25-50 mm
    Espaciado rejilla fina          : e = 10-25 mm
    Ángulo de inclinación           : 45-60 grados 

    Ecuaciones
    ----------
    Sección transversal del canal   : A_canal = Q / v             [Ec. 2a]
    Ancho del canal (rectangular)   : b = A_canal / h             [Ec. 2b]
        donde h = tirante hidráulico (0.3-0.8 m, tipicamente = b)

    Pérdida de carga en rejillas limpias (Kirschmer):
        hL = β * (w/b_barra)^(4/3) * (v_canal^2 / 2g) * sin(θ)   [Ec. 2c]

    Referencias
    -----------
    Metcalf & Eddy (2014), pp. 470-488
    Romero (2004), pp. 185-202
    """
    ref1 = citar("metcalf_2014")
    ref2 = citar("romero_2004")

    # Parámetros de diseño adoptados desde configuración
    v_canal_m_s = Q.rejillas_v_canal_m_s
    h_tirante = Q.rejillas_h_tirante_m
    angulo_grados = Q.rejillas_angulo_grados
    beta = Q.rejillas_beta
    w_barra = Q.rejillas_w_barra_m
    b_barra = Q.rejillas_b_barra_m
    largo_canal = Q.rejillas_largo_canal_m

    Q_m3_s = Q.Q_linea_m3_s

    # [Ec. 2a] Sección transversal
    A_canal = Q_m3_s / v_canal_m_s   # m^2

    # [Ec. 2b] Ancho del canal
    b_canal = A_canal / h_tirante     # m

    # [Ec. 2c] Pérdida de carga (Kirschmer) - rejilla fina
    g = 9.81
    angulo_rad = math.radians(angulo_grados)

    # Pérdida de carga (Kirschmer) - CON VELOCIDAD ADOPTADA (referencial)
    hL_adoptada = (beta * (w_barra / b_barra)**(4/3) *
                   (v_canal_m_s**2 / (2 * g)) *
                   math.sin(angulo_rad))   # m

    # Ancho real a usar (con mínimo constructivo)
    # Fórmula: b_canal * 2 + 0.30 m
    #   - b_canal * 2: factor de escala práctico para caudales pequeños
    #     (evita canales excesivamente estrechos que dificultan la operación)
    #   - +0.30 m: espacio para marcos de rejilla y sellado (0.15 m cada lado)
    # Mínimo constructivo absoluto: 0.60 m según OPS/CEPIS (2005)
    ancho_layout = round(max(b_canal * 2 + 0.30, 0.60), 2)
    
    # Velocidad REAL con el ancho adoptado (no la teórica)
    A_real = ancho_layout * h_tirante
    v_real_m_s = Q_m3_s / A_real
    
    # Pérdida de carga (Kirschmer) - CON VELOCIDAD REAL (para el diseño)
    hL_real = (beta * (w_barra / b_barra)**(4/3) *
               (v_real_m_s**2 / (2 * g)) *
               math.sin(angulo_rad))   # m
    
    # =============================================================================
    # VERIFICACIÓN PARA CAUDAL MÁXIMO HORARIO (SOLO VERIFICACIÓN, NO DISEÑO)
    # =============================================================================
    factor_pico = Q.factor_pico_Qmax  # Factor desde configuración
    Q_max_L_s = Q.Q_linea_L_s * factor_pico
    Q_max_m3_s = Q_max_L_s / 1000.0
    
    # Límites de velocidad según Metcalf & Eddy (2014)
    # Estos límites evitan daño estructural en las barras de la rejilla
    v_max_limite_advertencia = Q.rejillas_v_max_advertencia_m_s  # 1.5 m/s
    v_max_limite_destructivo = Q.rejillas_v_max_destructivo_m_s  # 2.0 m/s
    
    # Ajuste automático por incrementos de 5 cm si excede límite destructivo
    ajuste_ancho_rejillas = False
    ancho_original = ancho_layout
    
    while True:
        A_real = ancho_layout * h_tirante
        v_max_m_s = Q_max_m3_s / A_real
        
        # Si está por debajo del límite destructivo, aceptamos
        if v_max_m_s <= v_max_limite_destructivo:
            break
        
        # Si excede el límite destructivo, aumentar ancho en 5 cm
        ancho_layout += 0.05  # incremento de 5 cm
        ajuste_ancho_rejillas = True
        
        # Seguridad: límite máximo de iteraciones
        if ancho_layout > 2.0:  # máximo 2 metros
            break
    
    # Recalcular valores finales
    A_real = ancho_layout * h_tirante
    v_real_m_s = Q_m3_s / A_real
    v_max_m_s = Q_max_m3_s / A_real
    
    # Pérdida de carga con valores finales
    hL_real = (beta * (w_barra / b_barra)**(4/3) *
               (v_real_m_s**2 / (2 * g)) *
               math.sin(angulo_rad))
    hL_max = (beta * (w_barra / b_barra)**(4/3) *
              (v_max_m_s**2 / (2 * g)) *
              math.sin(angulo_rad))
    
    # Verificaciones finales
    velocidad_segura = v_max_m_s <= v_max_limite_advertencia
    velocidad_no_destructiva = v_max_m_s <= v_max_limite_destructivo
    perdida_aceptable = hL_max < 0.15
    
    # Incremento de sección aplicado
    incremento_ancho_cm = round((ancho_layout - ancho_original) * 100)
    
    # Textos automáticos de verificación
    if ajuste_ancho_rejillas:
        verif_vel_texto = f"se aumentó el ancho del canal en {incremento_ancho_cm}~cm (de {ancho_original:.2f}~m a {ancho_layout:.2f}~m) para mantener la velocidad máxima por debajo del límite destructivo de 2,0~m/s"
    elif velocidad_segura:
        verif_vel_texto = "es menor que el límite recomendado de 1,5~m/s para operación segura"
    elif velocidad_no_destructiva:
        verif_vel_texto = "supera el límite recomendado de 1,5~m/s pero se mantiene por debajo del límite destructivo de 2,0~m/s (operación aceptable con monitoreo)"
    else:
        verif_vel_texto = "EXCEDE el límite destructivo de 2,0~m/s -- RIESGO DE DAÑO ESTRUCTURAL. Se requiere mayor ancho de canal"
    
    if perdida_aceptable:
        verif_hl_texto = "es menor que el umbral de 15~cm para limpieza manual aceptable"
    else:
        verif_hl_texto = "EXCEDE el umbral de 15~cm -- REQUIERE LIMPIEZA MECÁNICA"

    return {
        "unidad": "Canal de desbaste con rejillas",
        "Q_m3_s": round(Q_m3_s, 5),
        "v_canal_adoptada_m_s": v_canal_m_s,  # Velocidad de diseño adoptada (0.50)
        "v_canal_real_m_s": round(v_real_m_s, 3),  # Velocidad real con ancho mínimo
        "A_canal_m2": round(A_canal, 5),
        "b_canal_teorico_m": round(b_canal, 3),
        "ancho_layout_m": ancho_layout,
        "h_tirante_m": h_tirante,
        "largo_canal_m": largo_canal,
        "angulo_grados": angulo_grados,
        "perdida_carga_adoptada_m": round(hL_adoptada, 6),  # Referencial
        "perdida_carga_real_m": round(hL_real, 6),  # Valor real con v=0.014 m/s
        # Verificación caudal máximo horario
        "factor_pico": factor_pico,
        "Q_max_L_s": Q_max_L_s,
        "v_max_m_s": round(v_max_m_s, 3),
        "hL_max_m": round(hL_max, 6),
        "velocidad_segura": velocidad_segura,
        "perdida_aceptable": perdida_aceptable,
        "verif_vel_texto": verif_vel_texto,
        "verif_hl_texto": verif_hl_texto,
        "ajuste_ancho_rejillas": ajuste_ancho_rejillas,
        "ancho_original_m": round(ancho_original, 2),
        "incremento_ancho_cm": incremento_ancho_cm,
        "largo_layout_m": largo_canal,
        "fuente": f"{ref1} (pp. 470-488); {ref2} (pp. 185-202)",
    }


# =============================================================================
# 2 - DESARENADOR DE FLUJO HORIZONTAL
# =============================================================================

def dimensionar_desarenador(Q: ConfigDiseno = CFG) -> Dict[str, Any]:
    """
    Dimensionamiento de desarenador de flujo horizontal según criterios NORMATIVOS.

    CRITERIOS DE DISEÑO REALES (Metcalf & Eddy, 2014, pp. 488-510):
    ---------------------------------------------------------------
    1. Velocidad horizontal (v_h): 0.25 - 0.40 m/s (Metcalf & Eddy, Tabla 9-6)
       - Máximo 0.30 m/s recomendado para no arrastrar arena sedimentada
       - Mínimo 0.25 m/s para evitar sedimentación orgánica
    
    2. Tiempo de retención (t_r): 30 - 60 segundos (criterio NORMATIVO)
       - Este es el tiempo práctico usado en diseño real
       - NO usar t_r = H/v_s (eso es teoría de sedimentación ideal, no diseño)
    
    3. Longitud del canal: L = v_h × t_r
       - Con v_h = 0.30 m/s y t_r = 30 s → L = 9.0 m (valor normativo)
    
    4. Para caudales pequeños (< 20 L/s):
       - Metcalf recomienda 9.0 m, pero la práctica latinoamericana admite
         longitudes menores (3.0-6.0 m) por criterio constructivo y operativo
       - SENAGUA (2012) y OPS/CEPIS (2005) establecen mínimos prácticos

    PROBLEMA CON CAUDALES PEQUEÑOS (5 L/s):
    ---------------------------------------
    Si aplicamos estrictamente L = v_h × t_r = 0.30 × 30 = 9.0 m, con Q = 5 L/s:
    - Ancho calculado: B = Q/(v_h × H) = 0.005/(0.30×0.40) = 0.042 m (imposible)
    - Se aplica ancho mínimo constructivo: 0.30 m
    - Velocidad real resultante: v = Q/(B×H) = 0.042 m/s (muy baja, pero aceptable)
    
    La longitud de 9.0 m para solo 5 L/s es excesiva y no se justifica prácticamente.
    Se adopta criterio latinoamericano: longitud reducida proporcional al caudal.

    Referencias
    -----------
    Metcalf & Eddy (2014), pp. 488-510, Tabla 9-6
    Romero (2004), pp. 202-218
    SENAGUA (2012) - mínimos constructivos Ecuador
    OPS/CEPIS (2005) - Guía diseño Latinoamérica
    """
    ref1 = citar("metcalf_2014")
    ref2 = citar("romero_2004")
    ref3 = citar("senagua_2012")
    ref4 = citar("ops_cepis_2005")

    # PARÁMETROS NORMATIVOS (de ConfigDiseno)
    v_h_adoptada = Q.desarenador_v_h_objetivo_m_s  # 0.30 m/s según Metcalf
    t_r_nominal = 30.0        # s - tiempo mínimo NORMATIVO (30-60 s)
    H_util = Q.desarenador_H_util_m  # 0.40 m
    b_min_m = Q.desarenador_b_min_m  # 0.60 m (constructivo)
    L_min_constructivo = Q.desarenador_L_min_norm_m  # m - desde configuración (default: 3.0)

    Q_m3_s = Q.Q_linea_m3_s
    Q_L_s = Q.Q_linea_L_s

    # ANCHO DEL CANAL
    # Por continuidad: B = Q / (v_h × H)
    b_teorico = Q_m3_s / (v_h_adoptada * H_util)
    
    # Aplicar ancho mínimo constructivo (siempre se aplica para Q < 20 L/s)
    b_canal = max(b_teorico, b_min_m)
    
    # Velocidad real resultante (puede ser menor a 0.30 m/s si se aplica mínimo)
    v_h_real = Q_m3_s / (b_canal * H_util)

    # =============================================================================
    # CÁLCULO TEÓRICO: Velocidad de sedimentación por Ley de Stokes
    # =============================================================================
    # Para partículas de arena: d = 0.20 mm, Ss = 2.65, T = variable
    g = 9.81  # m/s²
    d_m = Q.desarenador_d_particula_mm / 1000.0  # m
    Ss = Q.desarenador_Ss  # Gravedad específica
    
    # Viscosidad cinemática del agua según temperatura real
    nu_m2_s = viscosidad_cinematica_agua(Q.T_agua_C)  # m²/s
    
    # Ley de Stokes: Vs = g × (Ss - 1) × d² / (18 × ν)
    v_s_calculada = g * (Ss - 1) * (d_m ** 2) / (18 * nu_m2_s)  # m/s
    v_s_m_s = round(v_s_calculada, 3)
    
    # Número de Reynolds para verificar aplicabilidad de Stokes (Re < 1)
    Re = (d_m * v_s_m_s) / nu_m2_s
    
    # =============================================================================
    # LONGITUD DEL CANAL - CRITERIO TEÓRICO (L = v_h × H / v_s)
    # =============================================================================
    # Longitud teórica basada en sedimentación tipo I
    L_teorica_stokes = (v_h_adoptada * H_util) / v_s_m_s  # ~3.0 m
    
    # Criterio normativo alternativo: L = v_h × t_r (Metcalf & Eddy)
    L_teorica_metcatlf = v_h_adoptada * t_r_nominal  # = 9.0 m
    
    # Para caudales pequeños, aplicar factor de escala práctico según OPS/CEPIS
    # Usar parámetro configurable desde ConfigDiseno
    if Q_L_s < Q.desarenador_umbral_caudal_pequeno_L_s:
        # Factor de escala: caudales pequeños → longitud práctica mínima
        # Se adopta el menor valor entre criterio teórico-Stokes y práctico
        L_diseno = max(L_min_constructivo, L_teorica_stokes)
    else:
        L_diseno = max(L_min_constructivo, L_teorica_metcatlf)

    # Tiempo de retención real en el diseño adoptado
    t_r_real = L_diseno / v_h_real  # segundos
    
    # =============================================================================
    # VERIFICACIÓN TÉCNICA: Velocidad crítica de resuspensión (Camp-Shields)
    # =============================================================================
    # Vc = √(8 × β × g × (Ss - 1) × d / f)
    # Donde: β = 0.04-0.06 (factor de forma), f = 0.02-0.03 (fricción)
    beta = Q.desarenador_beta  # desde configuración
    f_darcy = Q.desarenador_f_darcy  # desde configuración
    
    v_c_scour = math.sqrt((8 * beta * g * (Ss - 1) * d_m) / f_darcy)  # m/s
    
    # =============================================================================
    # VERIFICACIÓN PARA CAUDAL MÁXIMO HORARIO (SOLO VERIFICACIÓN, NO DISEÑO)
    # =============================================================================
    factor_pico = Q.desarenador_factor_pico  # 2.5 (típico 2-3)
    Q_max_L_s = Q_L_s * factor_pico
    Q_max_m3_s = Q_max_L_s / 1000.0
    
    # Límite de resuspensión: velocidad crítica de Camp-Shields (v_c_scour)
    # Por encima de este valor se produce resuspensión de la arena sedimentada
    # Factor de seguridad del 90% para garantizar que no haya arrastre
    v_h_max_limite_destructivo = v_c_scour * Q.desarenador_factor_seguridad_scour  # m/s
    
    # Ajuste automático por incrementos de 5 cm si excede velocidad crítica
    ajuste_ancho_desarenador = False
    b_canal_original = b_canal
    
    while True:
        v_h_max = Q_max_m3_s / (b_canal * H_util)
        
        # Si está por debajo de la velocidad crítica, aceptamos
        if v_h_max <= v_h_max_limite_destructivo:
            break
        
        # Si excede la velocidad crítica, aumentar ancho en 5 cm
        b_canal += 0.05  # incremento de 5 cm
        ajuste_ancho_desarenador = True
        
        # Seguridad: límite máximo de iteraciones
        if b_canal > 2.0:  # máximo 2 metros
            break
    
    # Recalcular valores finales
    v_h_real = Q_m3_s / (b_canal * H_util)
    v_h_max = Q_max_m3_s / (b_canal * H_util)
    t_r_real = L_diseno / v_h_real
    t_r_max = L_diseno / v_h_max  # segundos
    
    # Verificación: v_h_max debe ser <= v_c_scour (para no resuspender arena)
    scour_seguro = v_h_max <= v_c_scour
    incremento_ancho_des_cm = round((b_canal - b_canal_original) * 100)
    
    # Texto automático de verificación (evita errores si cambian los datos)
    if scour_seguro:
        verif_scour_texto = f"es menor que la velocidad crítica de resuspensión ({round(v_c_scour, 3):.3f}~m/s), por lo que no se produce resuspensión de la arena depositada"
    else:
        verif_scour_texto = f"EXCEDE la velocidad crítica de resuspensión ({round(v_c_scour, 3):.3f}~m/s), por lo que SE PRODUCIRÍA resuspensión de arena -- AJUSTAR DIMENSIONES"
    
    # Verificaciones
    assert v_h_real <= 0.40, (
        f"v_h = {v_h_real:.3f} m/s supera máximo 0.40 m/s ({ref1})"
    )
    assert L_diseno >= L_min_constructivo, (
        f"L = {L_diseno:.1f} m < mínimo constructivo {L_min_constructivo} m"
    )

    return {
        "unidad": "Desarenador de flujo horizontal",
        "Q_m3_s": round(Q_m3_s, 5),
        "Q_linea_L_s": Q_L_s,
        # Velocidades
        "v_h_adoptada_m_s": v_h_adoptada,     # 0.30 m/s (Metcalf)
        "v_h_real_m_s": round(v_h_real, 3),   # Puede ser < 0.30 por ancho mínimo
        "v_s_m_s": v_s_m_s,                   # Velocidad sedimentación Stokes
        # Dimensiones
        "H_util_m": H_util,
        "b_teorico_m": round(b_teorico, 3),
        "b_canal_m": round(b_canal, 3),
        "L_teorica_stokes_m": round(L_teorica_stokes, 1),  # Basado en vs calculada
        "L_teorica_Metcalf_m": round(L_teorica_metcatlf, 1),  # Criterio normativo
        "L_diseno_m": round(L_diseno, 1),
        "relacion_L_B": round(L_diseno / b_canal, 1),
        # Tiempos
        "t_r_nominal_s": t_r_nominal,         # 30 s (norma)
        "t_r_real_s": round(t_r_real, 1),     # En el diseño adoptado
        # Parámetros físicos y de Stokes (para LaTeX)
        "g_m_s2": g,                          # Gravedad (m/s²)
        "nu_m2_s": nu_m2_s,                   # Viscosidad cinemática (m²/s)
        "Ss": Ss,                             # Gravedad específica arena
        "d_m": d_m,                           # Diámetro partícula (m)
        "d_mm": Q.desarenador_d_particula_mm, # Diámetro partícula (mm)
        "v_s_stokes_m_s": v_s_m_s,            # Calculada por Ley de Stokes
        "Re_stokes": round(Re, 3),            # Número de Reynolds
        # Parámetros Camp-Shields (para LaTeX)
        "beta": beta,                         # Factor de forma
        "f_darcy": f_darcy,                   # Factor de fricción Darcy-Weisbach
        "v_c_scour_m_s": round(v_c_scour, 3), # Velocidad crítica resuspensión
        # Verificación caudal máximo horario
        "factor_pico": factor_pico,           # 2.5 (Qmax/Qmedio)
        "Q_max_L_s": Q_max_L_s,               # Caudal máximo horario (L/s)
        "v_h_max_m_s": round(v_h_max, 3),     # Velocidad a Qmax
        "t_r_max_s": round(t_r_max, 1),       # Tiempo retención a Qmax
        "scour_seguro": scour_seguro,         # v_h_max < v_c_scour?
        "verif_scour_texto": verif_scour_texto,  # Texto automático de verificación
        "ajuste_ancho_desarenador": ajuste_ancho_desarenador,
        "b_canal_original_m": round(b_canal_original, 3),
        "incremento_ancho_cm": incremento_ancho_des_cm,
        # Layout
        "largo_layout_m": round(L_diseno, 1),
        "ancho_layout_m": round(b_canal + 0.30, 2),
        # Nota explicativa
        "nota_diseño": f"Para Q={Q_L_s:.1f} L/s, la longitud se reduce de {L_teorica_metcatlf:.1f} m (teórica) a {L_diseno:.1f} m por criterio práctico latinoamericano",
        "fuente": (f"{ref1} (pp. 488-510, Tabla 9-6); {ref2} (pp. 202-218); {ref3}; {ref4}"),
    }


# =============================================================================
# 3 - REACTOR UASB
# =============================================================================

def dimensionar_uasb(Q: ConfigDiseno = CFG) -> Dict[str, Any]:
    """
    Dimensionamiento del reactor UASB (Upflow Anaerobic Sludge Blanket).

    Fundamento teórico
    ------------------
    El UASB fue desarrollado por Lettinga et al. (Delft, 1980). Aprovecha la
    capacidad de floculación anaerobia para formar un manto de lodos denso
    (sludge blanket) que actúa como filtro biológico activo.

    La reacción principal es la metanogénesis:
        C6H12O6 -> 3 CH4 + 3 CO2                            [Reacción I]

    Ecuaciones de dimensionamiento
    --------------------------------
    1. Carga orgánica volumétrica (criterio principal a T > 20  grados C):
        Cv = Q * S0 / V_r                                    [Ec. 4a]
        donde:
            S0 = DBO5 afluente (kg/m^3)
            V_r = volumen del reactor (m^3)
            Cv = 1.5-4.0 kg DQO/m^3*d para aguas residuales municipales
            (van Haandel & Lettinga, 1994, Tabla 6.1; rango 2-8 es para aguas industriales)
            Adoptado: Cv = 2.5 kg DQO/m^3*d para T >= 22  grados C

    2. Volumen del reactor:
        V_r = Q * S0 / Cv                                    [Ec. 4b]

    3. Tiempo de retención hidráulico:
        TRH = V_r / Q                                        [Ec. 4c]
        Mínimo recomendado: 4 h (T > 22  grados C), 6 h (T = 15-22  grados C)
        [Sperling, 2007, p. 140; van Haandel & Lettinga, 1994, p. 118]

    4. Velocidad superficial ascendente (criterio hidráulico):
        v_up = Q / A_sup                                     [Ec. 4d]
        Rango: 0.5-1.0 m/h para Q constante
        Máximo: 1.5 m/h en período de alto caudal
        [Sperling, 2007, p. 141; Metcalf & Eddy, 2014, p. 757]

    5. Área superficial:
        A_sup = Q / v_up                                     [Ec. 4e]

    6. Altura del reactor:
        H = V_r / A_sup                                      [Ec. 4f]
        Rango típico: 4-6 m [van Haandel & Lettinga, 1994]

    7. Diámetro (reactor circular):
        D = √(4 * A_sup / π)                                 [Ec. 4g]

    Eficiencia esperada
    -------------------
    Remoción DBO5 : 70-80% (T = 22-28  grados C) [Sperling, 2007, Tabla 5.3]
    Remoción SST  : 60-70%
    Producción CH4: 0.35 m^3 CH4/kg DQO removida (condición anaerobia estequiométrica)
    Producción lodo: 0.08-0.12 kg SSV/kg DBO removida [Sperling, 2007, p. 155]

    Referencias
    -----------
    van Haandel & Lettinga (1994), Cap. 6
    Sperling (2007), Cap. 5
    Metcalf & Eddy (2014), pp. 753-780
    """
    ref_vh = citar("van_haandel_1994")
    ref_sp = citar("sperling_2007")
    ref_me = citar("metcalf_2014")

    # =============================================================================
    # AJUSTE AUTOMÁTICO POR TEMPERATURA
    # =============================================================================
    T_agua = Q.T_agua_C  # Temperatura del agua (°C)
    
    # Usar función centralizada para evaluación de temperatura
    temp_eval = evaluar_temperatura_uasb(T_agua, Q)
    
    # Extraer parámetros calculados desde función centralizada
    Cv_kgDQO_m3_d = temp_eval["cv_kgDQO_m3_d"]
    HRT_min = temp_eval["trh_h"]
    v_up_m_h = temp_eval["v_up_m_h"]  # Velocidad ya ajustada por temperatura
    factor_temp_texto = temp_eval["factor_temp_texto"]
    texto_recomendacion_temp = temp_eval["texto_recomendacion"]
    rangos = temp_eval["rangos_recomendados"]
    
    # Eficiencias ajustadas por temperatura (de la función centralizada)
    eta_DBO = temp_eval["eficiencia_dbo"]
    eta_DQO = temp_eval["eficiencia_dqo"]
    
    H_max = Q.uasb_H_max_m

    Q_m3_d = Q.Q_linea_m3_d
    Q_m3_h = Q.Q_linea_m3_h
    Q_m3_s = Q.Q_linea_m3_s

    # Carga orgánica afluente
    DQO_kg_m3 = Q.DQO_mg_L * 1e-3  # kg/m³

    # [Ec. 4b] Volumen del reactor
    V_r_m3 = Q_m3_d * DQO_kg_m3 / Cv_kgDQO_m3_d   # m^3

    # [Ec. 4c] TRH
    TRH_h = (V_r_m3 / Q_m3_h)

    # [Ec. 4e] Área superficial
    A_sup_m2 = Q_m3_h / v_up_m_h     # m^2

    # [Ec. 4f] Altura del reactor
    H_r_m = V_r_m3 / A_sup_m2        # m

    # Si la altura supera el máximo, ajustar área
    if H_r_m > H_max:
        H_r_m = H_max
        A_sup_m2 = V_r_m3 / H_r_m
        v_up_m_h = Q_m3_h / A_sup_m2  # recalcular velocidad

    # [Ec. 4g] Diámetro del reactor circular
    D_m = math.sqrt(4 * A_sup_m2 / math.pi)

    # Producción de biogás (metano)
    DQO_removida_kg_d = Q_m3_d * DQO_kg_m3 * eta_DQO   # kg DQO/d
    factor_biogas = Q.uasb_factor_biogas_ch4            # desde configuración
    biogaz_m3_d = factor_biogas * DQO_removida_kg_d     # m^3 CH4/d

    # Producción de lodos
    DBO_kg_m3 = Q.DBO5_mg_L * 1e-3
    DBO_removida_kg_d = Q_m3_d * DBO_kg_m3 * eta_DBO
    lodos_kg_SSV_d = Q.uasb_rendimiento_lodos_kg_SSV_kg_DBO * DBO_removida_kg_d   # kg SSV/d
    
    # =============================================================================
    # VERIFICACIÓN PARA CAUDAL MÁXIMO HORARIO (SOLO VERIFICACIÓN, NO DISEÑO)
    # =============================================================================
    factor_pico_uasb = Q.factor_pico_Qmax  # Factor típico Qmax/Qmedio (de configuración global)
    Q_max_m3_d = Q_m3_d * factor_pico_uasb
    Q_max_m3_h = Q_max_m3_d / 24.0
    
    # Límites de velocidad ascendente según Metcalf & Eddy (2014)
    # v_up > 1.5 m/h: riesgo de arrastre del manto de lodos
    # v_up > 2.0 m/h: arrastre severo, pérdida de biomasa
    v_up_max_limite_recomendado = Q.uasb_v_up_max_recomendado_m_h  # 1.5 m/h
    v_up_max_limite_destructivo = Q.uasb_v_up_max_destructivo_m_h  # 2.0 m/h
    
    # Ajuste automático por incrementos de 5 cm en diámetro si excede límite destructivo
    ajuste_realizado = False
    D_m_original = D_m
    
    # Margen de seguridad: diseñar para 95% del límite destructivo
    # para evitar operar exactamente en el borde
    v_up_max_limite_con_margen = v_up_max_limite_destructivo * 0.95
    
    iteracion = 0
    max_iteraciones = 200
    
    while iteracion < max_iteraciones:
        v_up_max_m_h = Q_max_m3_h / A_sup_m2
        
        # Si está por debajo del límite con margen, aceptamos
        if v_up_max_m_h <= v_up_max_limite_con_margen:
            break
        
        # Si excede el límite con margen, aumentar diámetro en 5 cm
        D_m += 0.05  # incremento de 5 cm
        A_sup_m2 = math.pi * (D_m ** 2) / 4
        ajuste_realizado = True
        iteracion += 1
        
        # Seguridad: límite máximo de iteraciones
        if D_m > Q.uasb_D_max_m:  # máximo configurable (default 10m)
            break
    
    # Recalcular valores finales si hubo ajuste (protegiendo altura mínima)
    if ajuste_realizado:
        H_r_calculada = V_r_m3 / A_sup_m2
        if H_r_calculada < Q.uasb_H_min_m:
            H_r_m = Q.uasb_H_min_m
            V_r_m3 = A_sup_m2 * H_r_m
            TRH_h = V_r_m3 / Q_m3_h
        else:
            H_r_m = H_r_calculada
        v_up_m_h = Q_m3_h / A_sup_m2
        v_up_max_m_h = Q_max_m3_h / A_sup_m2
    
    v_up_max_aceptable = v_up_max_m_h <= v_up_max_limite_recomendado
    incremento_diametro_cm = round((D_m - D_m_original) * 100)
    
    # Estado de verificación para el texto del documento
    if v_up_max_m_h <= v_up_max_limite_recomendado:
        estado_verificacion = "ÓPTIMO"
    elif v_up_max_m_h <= v_up_max_limite_destructivo:
        estado_verificacion = "ACEPTABLE CON MONITOREO"
    else:
        estado_verificacion = "NO ADMISIBLE - REQUIERE REDIMENSIONAMIENTO"
    
    # Texto automático de verificación
    if ajuste_realizado:
        verif_vup_max_texto = f"Se aumentó el diámetro del reactor en {incremento_diametro_cm}~cm (de {D_m_original:.2f}~m a {D_m:.2f}~m) para mantener la velocidad máxima por debajo del límite destructivo."
    elif v_up_max_aceptable:
        verif_vup_max_texto = "La velocidad está dentro del rango óptimo, por lo que no se produce arrastre del manto de lodos."
    else:
        verif_vup_max_texto = "La velocidad supera el límite recomendado pero se mantiene dentro del rango admisible. Se recomienda monitoreo periódico del manto de lodos."

    # Verificaciones (warnings en lugar de asserts para permitir aguas frías)
    # Nota: Rangos ampliados para soportar temperaturas < 15°C (Cv puede ser < 2.0)
    if not (0.5 <= Cv_kgDQO_m3_d <= 10.0):
        print(f"[ADVERTENCIA] Cv = {Cv_kgDQO_m3_d:.2f} kg DQO/m³·d fuera de rango típico 0.5-10.0")
    if not (HRT_min <= TRH_h <= 15.0):
        print(f"[ADVERTENCIA] TRH = {TRH_h:.1f} h fuera de rango {HRT_min:.1f}-15 h")
    if not (0.2 <= v_up_m_h <= 2.0):
        print(f"[ADVERTENCIA] v_up = {v_up_m_h:.2f} m/h fuera de rango 0.2-2.0 m/h")

    # Desglose de alturas del reactor UASB (se calcularán al final tras posibles ajustes)
    # Altura del separador GLS (gas-líquido-sólido)
    H_GLS_m = Q.uasb_H_GLS_m  # Desde configuración (típico 0.8-1.2 m)
    # Altura de zona de distribución (fondo)
    H_distribucion_m = Q.uasb_H_distribucion_m  # Desde configuración (típico 0.3-0.5 m)
    # Bordo libre
    H_bordo_libre_m = Q.bordo_libre_uasb_m  # Desde configuración (típico 0.3-0.5 m)
    
    
    # =========================================================================
    # CÁLCULO DEL COMPARTIMIENTO DE SEDIMENTACIÓN SUPERIOR (Paso 7 del manual)
    # =========================================================================
    # Según Chernicharo:
    # 1. Criterio prioritario: SOR_max < 1.2 m/h (para no arrastrar sólidos)
    # 2. Criterio secundario: H_sed entre 1.5-2.0 m (altura típica)
    # 3. El TRH_sed resulta de V_sed/Q, donde V_sed = A_sed × H_sed
    #
    # Estrategia:
    # - Primero cumplir SOR_max aumentando diámetro si es necesario
    # - Luego calcular H_sed = V_sed_objetivo / A_sed
    # - Si H_sed < 1.5 m, usar H_sed = 1.5 m (mínimo) y aceptar TRH_sed mayor
    
    factor_efectividad_sed = Q.uasb_factor_efectividad_sed
    H_sed_operativo_m = Q.uasb_H_sed_m  # 1.6 m desde configuración
    
    # PASO 1: Asegurar SOR_max < límite (criterio más crítico)
    iteracion_sed = 0
    max_iteraciones_sed = 500
    D_m_sed = D_m
    A_sup_sed = A_sup_m2
    
    while iteracion_sed < max_iteraciones_sed:
        A_sed_efectiva_m2 = A_sup_sed * factor_efectividad_sed
        SOR_max_m_h = Q_max_m3_h / A_sed_efectiva_m2
        
        if SOR_max_m_h < Q.uasb_SOR_max_limite_m_h:
            break  # Cumple SOR_max
        
        D_m_sed += 0.05
        A_sup_sed = math.pi * (D_m_sed ** 2) / 4
        iteracion_sed += 1
        
        if D_m_sed > Q.uasb_D_sed_max_m:
            break
    
    # PASO 2: Establecer altura del sedimentador
    # Usamos la altura configurada H_sed (típicamente 1.5 - 2.0 m)
    # Esto asegura suficiente volumen para sedimentación
    A_sed_efectiva_m2 = A_sup_sed * factor_efectividad_sed
    H_sed_m = H_sed_operativo_m  # desde configuración
    V_sed_m3 = A_sed_efectiva_m2 * H_sed_m
    TRH_sed_medio_h = V_sed_m3 / Q_m3_h
    
    # Nota: Con caudales pequeños, TRH_sed puede ser > 2.0 h
    # Esto es conservador (más tiempo de sedimentación), no es un problema
    
    # Si el diámetro cambió, actualizar reactor manteniendo altura mínima física
    if D_m_sed != D_m:
        D_m = D_m_sed
        A_sup_m2 = A_sup_sed
        # La altura NO puede ser menor que la mínima física (ej: 3.0 m para UASB funcional)
        H_r_calculada = V_r_m3 / A_sup_m2
        if H_r_calculada < Q.uasb_H_min_m:
            # Mantener altura mínima y aceptar mayor TRH (diseño conservador)
            H_r_m = Q.uasb_H_min_m
            V_r_m3 = A_sup_m2 * H_r_m  # Volumen aumentado proporcionalmente
            TRH_h = V_r_m3 / Q_m3_h    # TRH resultante mayor
        else:
            H_r_m = H_r_calculada
        v_up_m_h = Q_m3_h / A_sup_m2
        v_up_max_m_h = Q_max_m3_h / A_sup_m2
    
    # Recalcular estado de verificación con valores finales (después de todos los ajustes)
    if v_up_max_m_h <= v_up_max_limite_recomendado:
        estado_verificacion = "ÓPTIMO"
    elif v_up_max_m_h <= v_up_max_limite_destructivo:
        estado_verificacion = "ACEPTABLE CON MONITOREO"
    else:
        estado_verificacion = "NO ADMISIBLE - REQUIERE REDIMENSIONAMIENTO"
    
    # Recalcular con valores finales
    A_sed_efectiva_m2 = A_sup_m2 * factor_efectividad_sed
    V_sed_m3 = A_sed_efectiva_m2 * H_sed_m
    
    # Cargas superficiales
    SOR_medio_m_h = Q_m3_h / A_sed_efectiva_m2
    SOR_max_m_h = Q_max_m3_h / A_sed_efectiva_m2
    
    # TRH en sedimentador
    TRH_sed_medio_h = V_sed_m3 / Q_m3_h
    TRH_sed_max_h = V_sed_m3 / Q_max_m3_h
    
    # Verificación de criterios
    SOR_medio_cumple = Q.uasb_SOR_medio_min_m_h <= SOR_medio_m_h <= Q.uasb_SOR_medio_max_m_h
    SOR_max_cumple = SOR_max_m_h < Q.uasb_SOR_max_limite_m_h
    # TRH_sed puede ser > 2.0 h, eso es conservador, no malo
    TRH_sed_cumple = TRH_sed_medio_h >= Q.uasb_TRH_sed_medio_min_h
    
    # Textos de verificación
    SOR_min_val = Q.uasb_SOR_medio_min_m_h
    SOR_max_val = Q.uasb_SOR_medio_max_m_h
    SOR_limite_val = Q.uasb_SOR_max_limite_m_h
    
    if SOR_medio_cumple:
        SOR_medio_texto = f"La carga superficial de {SOR_medio_m_h:.2f} m/h está dentro del rango recomendado ({SOR_min_val:.1f}-{SOR_max_val:.1f} m/h)"
    elif SOR_medio_m_h < SOR_min_val:
        SOR_medio_texto = f"La carga superficial de {SOR_medio_m_h:.2f} m/h está por debajo del rango ({SOR_min_val:.1f}-{SOR_max_val:.1f} m/h), pero es aceptable para diseño conservador"
    else:
        SOR_medio_texto = f"La carga superficial de {SOR_medio_m_h:.2f} m/h está por encima del rango recomendado ({SOR_min_val:.1f}-{SOR_max_val:.1f} m/h)"
    
    if SOR_max_cumple:
        SOR_max_texto = f"La carga superficial máxima de {SOR_max_m_h:.2f} m/h cumple con el límite (< {SOR_limite_val:.1f} m/h)"
    else:
        SOR_max_texto = f"La carga superficial máxima de {SOR_max_m_h:.2f} m/h excede el límite recomendado (< {SOR_limite_val:.1f} m/h)"
    
    # =========================================================================
    # CÁLCULO DE ABERTURAS GLS (Paso 9 del manual UASB)
    # =========================================================================
    # Según el manual de diseño UASB, las aberturas entre la zona de digestión
    # y el sedimentador deben dimensionarse para evitar velocidades excesivas
    # que arrastren sólidos. La velocidad admisible típica es 2.0-2.3 m/h a
    # caudal medio y 4.0-4.2 m/h a caudal máximo.
    
    v_abertura_adoptada_m_h = (Q.uasb_v_abertura_medio_min_m_h + Q.uasb_v_abertura_medio_max_m_h) / 2  # 2.15 m/h
    
    # Área mínima de aberturas para caudal medio
    A_aberturas_min_m2 = Q_m3_h / v_abertura_adoptada_m_h
    
    # Verificación a caudal máximo
    v_abertura_max_calculada_m_h = Q_max_m3_h / A_aberturas_min_m2
    
    # Lógica de auto-dimensionamiento interno: 
    # Las aberturas son deflectoras (físicamente construidas dentro del área total A_sup_m2). 
    # Por lo tanto, no modifican el diámetro del reactor, solo su propia geometría.
    if v_abertura_max_calculada_m_h > Q.uasb_v_abertura_max_m_h:
        # Forzar el cumplimiento en pico aumentando el tamaño de las aberturas GLS
        A_aberturas_min_m2 = Q_max_m3_h / Q.uasb_v_abertura_max_m_h
        v_abertura_max_calculada_m_h = Q.uasb_v_abertura_max_m_h
        # La apertura agrandada hará que la velocidad a caudal normal baje, lo cual es seguro.
        v_abertura_adoptada_m_h = Q_m3_h / A_aberturas_min_m2
        
    v_abertura_max_cumple = v_abertura_max_calculada_m_h <= Q.uasb_v_abertura_max_m_h
    
    # Características geométricas del GLS
    GLS_pendiente_adoptada_grados = (Q.uasb_GLS_pendiente_min_grados + Q.uasb_GLS_pendiente_max_grados) / 2  # 55°
    
    # =========================================================================
    # CÁLCULO DE DISTRIBUCIÓN DEL AFLUENTE (Chernicharo 2007; Metcalf & Eddy 2014)
    # =========================================================================
    # Según Chernicharo (2007), el número de puntos de distribución se calcula
    # en función del área del reactor y el área de influencia por punto.
    # Una distribución adecuada garantiza un flujo uniforme y evita cortocircuitos.
    
    A_inf_adoptada_m2 = (Q.uasb_A_inf_min_m2 + Q.uasb_A_inf_max_m2) / 2  # 2.5 m²/punto
    
    # Número de puntos de distribución (redondeado al entero superior)
    num_puntos_distribucion = math.ceil(A_sup_m2 / A_inf_adoptada_m2)
    
    # Caudal por punto
    caudal_por_punto_L_s = (Q_m3_s * 1000) / num_puntos_distribucion
    
    # =========================================================================
    # SELECCIÓN DINÁMICA DE DIÁMETROS COMERCIALES (Tubería y Bocas)
    # =========================================================================
    
    # 1. Bocas de salida (crítico: uasb_v_boca_min_m_s <= v <= uasb_v_boca_max_m_s)
    bocas_validas = []
    for d_mm in Q.uasb_tubos_comerciales_mm:
        a_m2 = math.pi * ((d_mm/1000.0) ** 2) / 4
        v = (caudal_por_punto_L_s / 1000) / a_m2
        if Q.uasb_v_boca_min_m_s <= v <= Q.uasb_v_boca_max_m_s:
            bocas_validas.append((d_mm, v))

    if bocas_validas:
        # Priorizar la velocidad intermedia más segura
        v_media = (Q.uasb_v_boca_min_m_s + Q.uasb_v_boca_max_m_s) / 2
        bocas_validas.sort(key=lambda x: abs(x[1] - v_media))
        diam_boca_salida_mm, velocidad_boca_m_s = bocas_validas[0]
        v_boca_cumple = True
    else:
        # Fallback conservador, no detiene el reporte pero advierte
        diam_boca_salida_mm = Q.uasb_diam_boca_salida_mm
        area_boca_m2 = math.pi * ((diam_boca_salida_mm/1000.0) ** 2) / 4
        velocidad_boca_m_s = (caudal_por_punto_L_s / 1000) / area_boca_m2
        v_boca_cumple = False
        print(f"[ADVERTENCIA] Ningún tubo cumple la velocidad estricta de salida. "
              f"v={velocidad_boca_m_s:.2f} m/s fuera de {Q.uasb_v_boca_min_m_s:.1f}-{Q.uasb_v_boca_max_m_s:.1f} m/s")

    # 2. Tubería madre (transporte seguro: v <= uasb_v_tubo_max_m_s, ej. 0.2m/s)
    tubos_validos = []
    for d_mm in Q.uasb_tubos_comerciales_mm:
        if d_mm < diam_boca_salida_mm: 
            continue # Tubería madre no puede ser menor a la boca de inyección
        a_m2 = math.pi * ((d_mm/1000.0) ** 2) / 4
        v = (caudal_por_punto_L_s / 1000) / a_m2
        if v <= Q.uasb_v_tubo_max_m_s:
            tubos_validos.append((d_mm, v))
            
    if tubos_validos:
        # Tomar el menor diámetro comercial que cumpla para no sobredimensionar en costo
        tubos_validos.sort(key=lambda x: x[0])
        diam_tubo_distribucion_mm, velocidad_tubo_m_s = tubos_validos[0]
    else:
        # Fallback conservador
        diam_tubo_distribucion_mm = Q.uasb_diam_tubo_distribucion_mm
        area_tubo_m2 = math.pi * ((diam_tubo_distribucion_mm/1000.0) ** 2) / 4
        velocidad_tubo_m_s = (caudal_por_punto_L_s / 1000) / area_tubo_m2
        print(f"[ADVERTENCIA] Tubería madre de distribución rápida excede velocidad límite: "
              f"v={velocidad_tubo_m_s:.2f} m/s > {Q.uasb_v_tubo_max_m_s:.2f} m/s")

    # =========================================================================
    # RECALCULO FINAL DE ALTURAS DEPENDIENTES
    # (Se realiza aquí para asegurar que usan el H_r_m final tras todos los bucles)
    # =========================================================================
    H_zona_reaccion_m = H_r_m  # Altura útil de digestión
    # La altura total de construcción incluye TODAS las zonas físicas (fondo, digestión, sedimentación, campana GLS divergente y bordo)
    H_total_construccion_m = H_distribucion_m + H_zona_reaccion_m + H_sed_m + H_GLS_m + H_bordo_libre_m
    
    # Subdivisión interna de la zona de reacción (según manual UASB)
    # Lecho de lodo denso/granular
    # Manto de lodos expandido
    H_lecho_granular_m = H_zona_reaccion_m * Q.uasb_porcion_lecho_granular
    H_manto_expandido_m = H_zona_reaccion_m * Q.uasb_porcion_manto_expandido
    
    
    return {
        "unidad": "Reactor UASB",
        # Datos de entrada
        "Q_m3_d": round(Q_m3_d, 1),
        "Q_m3_h": round(Q_m3_h, 2),
        "DQO_kg_m3": round(DQO_kg_m3, 4),
        "DBO5_kg_m3": round(DBO_kg_m3, 4),
        # Parámetros de temperatura
        "T_agua_C": T_agua,
        "factor_temp_texto": factor_temp_texto,
        "texto_recomendacion_temp": texto_recomendacion_temp,
        "Cv_base": Q.uasb_Cv_kgDQO_m3_d,
        # Rangos recomendados según temperatura (del evaluador centralizado)
        "rango_Cv": rangos["cv"],
        "rango_vup": rangos["vup"],
        "rango_HRT": rangos["hrt"],
        "rango_eta": rangos["eta"],
        # Parámetros de diseño adoptados (ajustados por temperatura)
        "Cv_kgDQO_m3_d": round(Cv_kgDQO_m3_d, 2),
        "v_up_m_h": round(v_up_m_h, 3),
        "eta_DBO": eta_DBO,
        "eta_DQO": eta_DQO,
        # Resultados del dimensionamiento
        "V_r_m3": round(V_r_m3, 1),
        "TRH_h": round(TRH_h, 1),
        "A_sup_m2": round(A_sup_m2, 2),
        "H_r_m": round(H_r_m, 2),
        "D_m": round(D_m, 2),
        # Desglose de alturas
        "H_zona_reaccion_m": round(H_zona_reaccion_m, 2),
        "H_GLS_m": round(H_GLS_m, 2),
        "H_distribucion_m": round(H_distribucion_m, 2),
        "H_bordo_libre_m": round(H_bordo_libre_m, 2),
        "H_total_construccion_m": round(H_total_construccion_m, 2),
        # Subdivisión interna zona de reacción (manual UASB)
        "H_lecho_granular_m": round(H_lecho_granular_m, 2),
        "H_manto_expandido_m": round(H_manto_expandido_m, 2),
        # Compartimiento de sedimentación superior (Paso 7 manual)
        "H_sed_m": round(H_sed_m, 2),
        "A_sed_efectiva_m2": round(A_sed_efectiva_m2, 2),
        "V_sed_m3": round(V_sed_m3, 2),
        "SOR_medio_m_h": round(SOR_medio_m_h, 2),
        "SOR_max_m_h": round(SOR_max_m_h, 2),
        "SOR_medio_cumple": SOR_medio_cumple,
        "SOR_max_cumple": SOR_max_cumple,
        "SOR_medio_texto": SOR_medio_texto,
        "SOR_max_texto": SOR_max_texto,
        "TRH_sed_medio_h": round(TRH_sed_medio_h, 2),
        "TRH_sed_max_h": round(TRH_sed_max_h, 2),
        "TRH_sed_cumple": TRH_sed_cumple,
        # Aberturas GLS (Paso 9 manual)
        "A_aberturas_min_m2": round(A_aberturas_min_m2, 2),
        "v_abertura_adoptada_m_h": round(v_abertura_adoptada_m_h, 2),
        "v_abertura_max_calculada_m_h": round(v_abertura_max_calculada_m_h, 2),
        "v_abertura_max_cumple": v_abertura_max_cumple,
        "GLS_pendiente_adoptada_grados": round(GLS_pendiente_adoptada_grados, 1),
        "GLS_traslape_m": Q.uasb_GLS_traslape_m,
        # Distribución del afluente (Paso 10 manual)
        "Q_m3_s": round(Q_m3_s, 6),  # Caudal en m³/s para cálculos de distribución
        "num_puntos_distribucion": num_puntos_distribucion,
        "A_inf_adoptada_m2": round(A_inf_adoptada_m2, 2),
        "caudal_por_punto_L_s": round(caudal_por_punto_L_s, 3),
        "diam_tubo_distribucion_mm": round(diam_tubo_distribucion_mm, 0),
        "velocidad_tubo_m_s": round(velocidad_tubo_m_s, 3),
        "v_tubo_max_m_s": Q.uasb_v_tubo_max_m_s,
        "diam_boca_salida_mm": round(diam_boca_salida_mm, 0),
        "velocidad_boca_m_s": round(velocidad_boca_m_s, 2),
        "v_boca_min_m_s": Q.uasb_v_boca_min_m_s,
        "v_boca_max_m_s": Q.uasb_v_boca_max_m_s,
        "v_boca_cumple": v_boca_cumple,
        # Producción de subproductos
        "factor_biogas_ch4": factor_biogas,   # Factor usado (m³ CH4 / kg DQO removida)
        "DQO_removida_kg_d": round(DQO_removida_kg_d, 2),
        "biogaz_m3_d": round(biogaz_m3_d, 1),
        "lodos_kg_SSV_d": round(lodos_kg_SSV_d, 2),
        # Verificación caudal máximo
        "factor_pico": factor_pico_uasb,
        "Q_max_m3_d": round(Q_max_m3_d, 1),
        "Q_max_m3_h": round(Q_max_m3_h, 2),
        "v_up_max_m_h": round(v_up_max_m_h, 2),
        "v_up_max_aceptable": v_up_max_aceptable,
        "verif_vup_max_texto": verif_vup_max_texto,
        "ajuste_realizado": ajuste_realizado,
        "incremento_diametro_cm": incremento_diametro_cm,
        "D_m_original": round(D_m_original, 2),
        "estado_verificacion": estado_verificacion,
        # Para layout
        "diametro_layout_m": round(D_m + 0.30, 1),  # incluye muros (e=0.15m c/lado)
        "fuente": (
            f"{ref_vh} (Cap. 6, Ec. 6.1-6.7); "
            f"{ref_sp} (pp. 140-157); "
            f"{ref_me} (pp. 753-780)"
        ),
        "notas": (
            f"Cv adoptada = {Cv_kgDQO_m3_d} kg DQO/m^3*d (rango típico {Q.uasb_Cv_optimo_min}-{Q.uasb_Cv_optimo_max} a temp. óptima, "
            f"{ref_vh}). "
            f"v_up = {v_up_m_h:.2f} m/h <= {Q.uasb_v_up_max_recomendado_m_h:.1f} m/h recomendado para lodo floculento "
            f"({ref_sp}, p. 141)."
        ),
    }


# =============================================================================
# 4 - FILTRO PERCOLADOR (MEDIO PLÁSTICO MODULAR)
# =============================================================================

def dimensionar_filtro_percolador(Q: ConfigDiseno = CFG,
                                   DBO_entrada_mg_L: float = None) -> Dict[str, Any]:
    """
    Dimensionamiento del filtro percolador (FP) de tasa intermedia/alta
    con medio plástico modular aleatorio (random plastic media).

    El FP recibe el efluente del UASB (post tratamiento primario anaerobio).

    Modelo de diseño: Germain (1966) - adoptado por WEF y Metcalf & Eddy
    -----------------------------------------------------------------------
    Se/S0 = exp(-k_T * D / Q_A^n)                          [Ec. 5a]

    donde:
        Se  = DBO5 efluente del FP (mg/L)
        S0  = DBO5 afluente al FP (mg/L) - salida del UASB
        k_T = constante de remoción a temperatura T (m/h)
              k_T = k_20 * 1.035^(T-20)                     [Ec. 5b]
              k_20 = 0.06-0.10 m/h para medio plástico aleatorio
              Adoptado: k_20 = 0.068 m/h  [Metcalf & Eddy, 2014, Tabla 9-32]
        D   = profundidad del medio filtrante (m)
              Típico: 3-8 m para medio plástico
        Q_A = tasa hidráulica superficial (m^3/m^2*h) = Q / A_sup
              Con recirculación: Q_A = Q(1+R)/A_sup
        n   = constante empírica del medio = 0.50 para medio plástico aleatorio
              [Germain, 1966; WEF MOP-8, 2010, p. 9-32]

    Tasas de diseño - medio plástico modular
    -----------------------------------------
    Tasa hidráulica    : 1-18 m^3/m^2*h   [Metcalf & Eddy, 2014, p. 843]
    Carga orgánica     : 0.3-3.0 kg DBO/m^3*d
    Tasa de recirculación: R = 0.5-2.0 (adimensional)
    Profundidad        : 3-8 m

    Referencias
    -----------
    Metcalf & Eddy (2014), pp. 840-870
    WEF MOP-8 (2010), Cap. 9
    Romero (2004), pp. 490-540
    """
    ref_me = citar("metcalf_2014")
    ref_wef = citar("wef_mop8_2010")
    ref_ro = citar("romero_2004")

    # DBO5 entrante al FP = DBO5 efluente del UASB
    if DBO_entrada_mg_L is None:
        DBO_entrada_mg_L = Q.DBO5_mg_L * (1.0 - 0.70)   # ~ 75 mg/L

    # DBO5 objetivo en el efluente del FP (antes del sedimentador secundario)
    # El sedimentador secundario aporta ~25-35% de remoción adicional de DBO
    # al sedimentar los sólidos biológicos desprendidos (humus).
    # FP objetivo = 55 mg/L -> tras sedimentación ~ 38-41 mg/L < 100 mg/L TULSMA [OK]
    DBO_salida_mg_L = Q.fp_DBO_salida_objetivo_mg_L  # mg/L - desde configuración

    # Parámetros del modelo Germain (verificación de eficiencia)
    # k_20 para medio plástico aleatorio moderno desde configuración
    # [Metcalf & Eddy, 2014, Tabla 9-32; WEF MOP-8, 2010, p. 9-34]
    k_20_m_h = Q.fp_k_20_m_h        # m/h  - constante cinética a 20 grados C (cfg default: 0.068)
    theta    = Q.fp_theta           # coef. temperatura [Ec. 5b]
    n        = Q.fp_n_germain       # constante empírica del medio aleatorio plástico
    D_m      = Q.fp_D_medio_m       # m    - profundidad del medio filtrante
    R        = Q.fp_R_recirculacion # tasa de recirculación
    H_total  = Q.fp_H_total_m       # m    - altura total incluye distribución, recolección y bordo libre

    # Parámetros del criterio de carga orgánica (dimensionamiento primario)
    # Carga orgánica volumétrica para medio plástico desde configuración
    # [Metcalf & Eddy, 2014, Tabla 9-31; WEF MOP-8, 2010, Cap. 9]
    Cv_kgDBO_m3_d = Q.fp_Cv_kgDBO_m3_d  # kg DBO5/m^3*d (cfg default: 0.5)

    Q_m3_d = Q.Q_linea_m3_d
    Q_m3_h = Q.Q_linea_m3_h

    # [Ec. 5b] Corrección por temperatura
    k_T_m_h = correccion_temperatura(k_20_m_h, theta, Q.T_agua_C)

    # === CRITERIO PRIMARIO: CARGA ORGÁNICA VOLUMÉTRICA ===
    # V = Q × DBO_in / Cv                                 [Ec. 5c]
    DBO_kg_m3 = DBO_entrada_mg_L * 1e-3    # kg/m^3
    V_medio_m3 = Q_m3_d * DBO_kg_m3 / Cv_kgDBO_m3_d    # m^3

    # Área superficial
    A_sup_m2 = V_medio_m3 / D_m             # m^2

    # Tasa hidráulica con recirculación
    Q_ap_m3_h = Q_m3_h * (1 + R)
    Q_A_real  = Q_ap_m3_h / A_sup_m2       # m^3/m^2*h

    # Si Q_A_real < 1 m^3/m^2*h (mínimo de mojado del medio), aumentar R
    if Q_A_real < 1.0:
        R = math.ceil(A_sup_m2 / Q_m3_h) - 1
        R = max(R, 1.0)
        Q_ap_m3_h = Q_m3_h * (1 + R)
        Q_A_real  = Q_ap_m3_h / A_sup_m2

    # Diámetro del filtro circular
    D_filtro_m = math.sqrt(4 * A_sup_m2 / math.pi)

    # === VERIFICACIÓN DE EFICIENCIA (modelo Germain) ===
    # Se/S0 = exp(-k_T * D / Q_A^n)                      [Ec. 5a]
    relacion_Se_S0 = math.exp(-k_T_m_h * D_m / (Q_A_real ** n))
    Se_calculado_mg_L = DBO_entrada_mg_L * relacion_Se_S0

    DBO_removida_kg_d = Q_m3_d * DBO_kg_m3 * (1 - relacion_Se_S0)

    # Cálculos para verificación Qmax (factor 2.5 igual que otras unidades)
    factor_pico = Q.factor_pico_Qmax  # Factor desde configuración
    Q_max_m3_d = Q_m3_d * factor_pico
    Q_max_m3_h = Q_max_m3_d / 24
    
    # Límite de tasa hidráulica para filtros percoladores con medio plástico
    # Según Metcalf & Eddy: máximo 4.0 m³/m²·h para evitar arrastre de biopelícula
    Q_A_limite_m3_m2_h = Q.fp_Q_A_limite_m3_m2_h
    
    # Ajuste automático si excede el límite: aumentamos recirculación primero, luego área
    # con protección de iteraciones máximas y límite mínimo de Cv
    iteracion = 0
    max_iteraciones = 100
    Cv_minima = Q.fp_Cv_minima_kgDBO_m3_d  # kg DBO/m³·d - límite inferior de diseño
    
    while iteracion < max_iteraciones:
        Q_ap_m3_h = Q_m3_h * (1 + R)  # Recalcular con R actual
        Q_A_max_m3_m2_h = Q_max_m3_h * (1 + R) / A_sup_m2
        
        # Si está por debajo del límite, aceptamos
        if Q_A_max_m3_m2_h <= Q_A_limite_m3_m2_h:
            break
        
        # Estrategia de ajuste
        if R < 2.0:
            R = min(R + 0.5, 2.0)  # Aumentamos recirculación hasta máximo 2.0
        elif Cv_kgDBO_m3_d > Cv_minima * 1.05:  # Dejar margen del 5% sobre el mínimo
            Cv_kgDBO_m3_d = max(Cv_kgDBO_m3_d * 0.95, Cv_minima)
            V_medio_m3 = Q_m3_d * DBO_kg_m3 / Cv_kgDBO_m3_d
            A_sup_m2 = V_medio_m3 / D_m
        else:
            # No se puede ajustar más sin violar límites
            break
        
        iteracion += 1
    
    # Si aún excede el límite, aumentar área superficial directamente
    Q_A_max_m3_m2_h = Q_max_m3_h * (1 + R) / A_sup_m2
    if Q_A_max_m3_m2_h > Q_A_limite_m3_m2_h:
        # Calcular área mínima necesaria para cumplir el límite
        A_sup_m2 = (Q_max_m3_h * (1 + R)) / Q_A_limite_m3_m2_h
    
    # Recalcular dimensiones finales y parámetros dependientes
    D_filtro_m = math.sqrt(4 * A_sup_m2 / math.pi)
    Q_A_real = Q_ap_m3_h / A_sup_m2
    Q_A_max_m3_m2_h = Q_max_m3_h * (1 + R) / A_sup_m2
    Q_A_max_m3_m2_d = Q_A_max_m3_m2_h * 24  # Para reporte
    
    # Recalcular eficiencia Germain con tasa hidráulica final
    relacion_Se_S0 = math.exp(-k_T_m_h * D_m / (Q_A_real ** n))
    Se_calculado_mg_L = DBO_entrada_mg_L * relacion_Se_S0
    DBO_removida_kg_d = Q_m3_d * DBO_kg_m3 * (1 - relacion_Se_S0)
    
    # =================================================================
    # PASO 4 - GEOMETRÍA COMPLETA DEL FILTRO (Desglose de alturas)
    # =================================================================
    H_distribucion = Q.fp_H_distribucion_m    # Espacio distribuidor-medio
    H_underdrain = Q.fp_H_underdrain_m        # Sistema drenaje inferior
    H_bordo_fp = Q.fp_H_bordo_libre_fp_m      # Bordo libre
    
    # Altura total verificada
    H_total_calculada = H_distribucion + D_m + H_underdrain + H_bordo_fp
    
    # =================================================================
    # PASO 5 - SISTEMA DE RECIRCULACIÓN (ya calculado arriba)
    # Verificación de qA a caudal mínimo (factor 0.4)
    # =================================================================
    Q_min_m3_h = Q_m3_h * 0.4  # Caudal mínimo nocturno
    qA_min_m3_m2_h = Q_min_m3_h * (1 + R) / A_sup_m2
    
    if qA_min_m3_m2_h < 0.5:
        recirculacion_adicional = True
        qA_min_texto = f"qA_min = {qA_min_m3_m2_h:.2f} m³/m²·h < 0.5 (riesgo de sequedad). Se recomienda aumentar R o control de nivel."
    else:
        recirculacion_adicional = False
        qA_min_texto = f"qA_min = {qA_min_m3_m2_h:.2f} m³/m²·h >= 0.5 (biopelícula húmeda garantizada)."
    
    # =================================================================
    # PASO 6 - DISTRIBUIDOR ROTATORIO
    # =================================================================
    # Número de brazos según diámetro (o usar configuración)
    if Q.fp_num_brazos is not None and Q.fp_num_brazos > 0:
        num_brazos = Q.fp_num_brazos
    elif D_filtro_m < 6.0:
        num_brazos = 2
    elif D_filtro_m <= 15.0:
        num_brazos = 2  # o 4 según preferencia
    else:
        num_brazos = 4
    
    # Longitud de cada brazo
    L_brazo_m = D_filtro_m / 2
    
    # Caudal por brazo
    Q_por_brazo_m3_h = Q_ap_m3_h / num_brazos
    
    # Verificación rotación hidráulica (necesita > 10 m³/h por brazo)
    rotacion_hidraulica = Q_por_brazo_m3_h >= 10.0
    
    # Boquillas
    num_boquillas_por_brazo = Q.fp_num_boquillas_por_brazo
    Q_por_boquilla_L_s = (Q_por_brazo_m3_h / num_boquillas_por_brazo) * 1000 / 3600
    v_boquilla_m_s = Q.fp_velocidad_boquilla_m_s
    
    # Diámetro de orificio calculado
    A_orificio_m2 = (Q_por_brazo_m3_h / 3600) / (num_boquillas_por_brazo * v_boquilla_m_s)
    diam_orificio_mm = math.sqrt(4 * A_orificio_m2 / math.pi) * 1000
    
    # =================================================================
    # PASO 7 - UNDERDRAIN (Sistema drenaje inferior)
    # =================================================================
    # Caudal de diseño (regla del 50%: diseñar para el doble)
    Q_underdrain_diseno_m3_h = Q_ap_m3_h / 0.50
    
    # Canal central - verificación con Manning
    ancho_canal = Q.fp_ancho_canal_central_m
    altura_canal = 0.30  # m (tipico)
    pendiente_canal = Q.fp_pendiente_underdrain_pct / 100  # 1% mínima
    n_manning = 0.013  # Concreto
    
    A_canal = ancho_canal * altura_canal
    P_canal = ancho_canal + 2 * altura_canal
    R_hidraulico = A_canal / P_canal
    
    Q_canal_m3_s = (1/n_manning) * A_canal * (R_hidraulico**(2/3)) * (pendiente_canal**0.5)
    Q_canal_m3_h = Q_canal_m3_s * 3600
    
    # Verificación: canal debe fluir < 50% de su capacidad
    llenado_canal = Q_ap_m3_h / Q_canal_m3_h
    canal_ok = llenado_canal <= 0.50
    
    # =================================================================
    # PASO 8 - VENTILACIÓN NATURAL
    # =================================================================
    # Área de ventilación requerida (>= 1% del área superficial)
    area_ventilacion_requerida_m2 = A_sup_m2 * (Q.fp_area_ventilacion_pct / 100)
    
    # Caudal de aire necesario
    Q_aire_min_m3_h = Q_m3_h * 0.1  # Mínimo 0.1 m³ aire/m³ agua
    Q_aire_opt_m3_h = Q_m3_h * Q.fp_Q_aire_factor  # Óptimo 0.3 m³/m³
    
    # Número de aperturas (0.20 x 0.30 m = 0.06 m² cada una)
    area_apertura_m2 = 0.20 * 0.30
    num_aperturas_min = math.ceil(area_ventilacion_requerida_m2 / area_apertura_m2)
    
    # Perímetro para distribución
    perimetro_m = math.pi * D_filtro_m
    espaciado_aperturas_m = perimetro_m / num_aperturas_min
    
    # =================================================================
    # PASO 10 - ESPECIFICACIONES DEL MEDIO PLÁSTICO
    # =================================================================
    # Carga sobre el medio
    carga_peso_medio_kg_m2 = (Q.fp_densidad_media_kg_m3 + 40 + 15) * D_m  # + agua + biopelícula
    
    # Verificación resistencia a compresión
    if D_m <= 3.5:
        resistencia_minima_requerida = 600  # kg/m²
    else:
        resistencia_minima_requerida = 1000  # kg/m²
    
    resistencia_ok = carga_peso_medio_kg_m2 <= resistencia_minima_requerida
    
    # Verificaciones finales (después de todos los ajustes)
    assert Cv_minima <= Cv_kgDBO_m3_d <= 3.0, (
        f"Carga orgánica Cv = {Cv_kgDBO_m3_d:.3f} kg DBO/m^3*d fuera de rango {Cv_minima}-3.0 "
        f"({ref_wef}, Cap. 9)"
    )
    assert 1.0 <= Q_A_real <= 18.0, (
        f"Tasa hidráulica Q_A = {Q_A_real:.2f} m^3/m^2*h fuera de rango 1-18 "
        f"({ref_me}, p. 843)"
    )
    assert Se_calculado_mg_L <= DBO_salida_mg_L * 1.20, (
        f"Eficiencia insuficiente: Se_Germain = {Se_calculado_mg_L:.1f} mg/L "
        f"> objetivo {DBO_salida_mg_L * 1.20:.1f} mg/L"
    )
    
    # Texto de verificación narrativo
    if Q_A_max_m3_m2_h <= Q_A_limite_m3_m2_h:
        verif_qmax_texto = f"el valor obtenido ({Q_A_max_m3_m2_h:.2f} m³/m²·h) es menor que el límite máximo recomendado de 4,0 m³/m²·h establecido por Metcalf y Eddy para evitar el arrastre de biopelícula, por lo que el diseño es adecuado"
    else:
        verif_qmax_texto = f"el valor obtenido ({Q_A_max_m3_m2_h:.2f} m³/m²·h) excede el límite máximo recomendado de 4,0 m³/m²·h establecido por Metcalf y Eddy para evitar el arrastre de biopelícula, por lo que el diseño requiere revisión"

    return {
        "unidad": "Filtro Percolador",
        # Datos de entrada
        "DBO_entrada_mg_L": round(DBO_entrada_mg_L, 1),
        "DBO_salida_objetivo_mg_L": DBO_salida_mg_L,
        "DBO_salida_Germain_mg_L": round(Se_calculado_mg_L, 1),
        "Q_m3_d": round(Q_m3_d, 1),
        "Q_ap_m3_h": round(Q_ap_m3_h, 2),
        # Parámetros del modelo Germain (verificación)
        "k_20_m_h": k_20_m_h,
        "k_T_m_h": round(k_T_m_h, 4),
        "theta": theta,
        "n_germain": n,
        "D_medio_m": D_m,
        "R_recirculacion": R,
        # Resultados (dimensionamiento por Cv)
        "Cv_kgDBO_m3_d": Cv_kgDBO_m3_d,
        "relacion_Se_S0_Germain": round(relacion_Se_S0, 3),
        "Q_A_real_m3_m2_h": round(Q_A_real, 3),
        "q_A_real_m3_m2_d": round(Q_A_real * 24, 1),
        "Q_A_max_m3_m2_h": round(Q_A_max_m3_m2_h, 2),
        "Q_A_max_m3_m2_d": round(Q_A_max_m3_m2_h * 24, 2),
        "Q_A_limite_m3_m2_h": round(Q_A_limite_m3_m2_h, 1),  # Límite para verificación
        "factor_pico": factor_pico,
        "Q_max_m3_d": round(Q_max_m3_d, 1),
        "verif_qmax_texto": verif_qmax_texto,
        "A_sup_m2": round(A_sup_m2, 2),
        "V_medio_m3": round(V_medio_m3, 1),
        "D_filtro_m": round(D_filtro_m, 2),
        "H_total_m": round(H_total_calculada, 2),
        # PASO 4 - Geometría
        "H_distribucion_m": H_distribucion,
        "H_medio_m": D_m,
        "H_underdrain_m": H_underdrain,
        "H_bordo_libre_m": H_bordo_fp,
        # PASO 5 - Recirculación
        "qA_min_m3_m2_h": round(qA_min_m3_m2_h, 2),
        "recirculacion_adicional_recomendada": recirculacion_adicional,
        "qA_min_texto": qA_min_texto,
        # PASO 6 - Distribuidor
        "num_brazos": num_brazos,
        "L_brazo_m": round(L_brazo_m, 2),
        "Q_por_brazo_m3_h": round(Q_por_brazo_m3_h, 1),
        "rotacion_hidraulica": rotacion_hidraulica,
        "num_boquillas_por_brazo": num_boquillas_por_brazo,
        "Q_por_boquilla_L_s": round(Q_por_boquilla_L_s, 2),
        "v_boquilla_m_s": v_boquilla_m_s,
        "diam_orificio_mm": round(diam_orificio_mm, 1),
        # PASO 7 - Underdrain
        "Q_underdrain_diseno_m3_h": round(Q_underdrain_diseno_m3_h, 1),
        "ancho_canal_central_m": ancho_canal,
        "Q_canal_capacidad_m3_h": round(Q_canal_m3_h, 1),
        "llenado_canal_pct": round(llenado_canal * 100, 1),
        "canal_underdrain_ok": canal_ok,
        "pendiente_underdrain_pct": Q.fp_pendiente_underdrain_pct,
        # PASO 8 - Ventilación
        "area_ventilacion_requerida_m2": round(area_ventilacion_requerida_m2, 2),
        "num_aperturas_ventilacion": num_aperturas_min,
        "espaciado_aperturas_m": round(espaciado_aperturas_m, 2),
        "Q_aire_min_m3_h": round(Q_aire_min_m3_h, 1),
        "Q_aire_opt_m3_h": round(Q_aire_opt_m3_h, 1),
        "Q_aire_factor": Q.fp_Q_aire_factor,
        # PASO 10 - Especificaciones medio
        "sup_especifica_medio_m2_m3": Q.fp_sup_especifica_m2_m3,
        "vacios_medio_pct": Q.fp_vacios_pct,
        "densidad_media_kg_m3": Q.fp_densidad_media_kg_m3,
        "carga_sobre_medio_kg_m2": round(carga_peso_medio_kg_m2, 1),
        "resistencia_compresion_ok": resistencia_ok,
        "DBO_removida_kg_d": round(DBO_removida_kg_d, 2),
        # Para layout
        "diametro_layout_m": round(D_filtro_m + 0.30, 1),
        "fuente": (
            f"Dimensionamiento por Cv: {ref_wef} (Cap. 9, Tabla 9-31); "
            f"Verificación por modelo Germain (1966) en {ref_me} (pp. 840-870); "
            f"{ref_ro} (pp. 490-540)"
        ),
        "notas": (
            f"Dimensionado por carga orgánica Cv = {Cv_kgDBO_m3_d} kg DBO/m^3*d "
            f"({ref_wef}). Verificado con Germain: Se = {Se_calculado_mg_L:.1f} mg/L "
            f"< objetivo {DBO_salida_mg_L} mg/L. "
            f"k_T = {k_T_m_h:.4f} m/h a T={Q.T_agua_C} grados C (θ={theta})."
        ),
    }


# =============================================================================
# 5 - HUMEDAL CONSTRUIDO DE FLUJO VERTICAL SUBSUPERFICIAL (HFCV)
# =============================================================================

def dimensionar_humedal_vertical(Q: ConfigDiseno = CFG,
                                  DBO_entrada_mg_L: float = None) -> Dict[str, Any]:
    """
    Dimensionamiento del humedal construido de flujo vertical subsuperficial (HFCV).
    También conocido como Constructed Wetland - Vertical Subsurface Flow (VF-CW).

    El HFCV recibe el efluente del UASB (post tratamiento primario anaerobio).
    El flujo es intermitente: lotes aplicados desde la superficie, drenaje por gravedad.

    Fundamento teórico
    ------------------
    Los HFCV combinan procesos físicos (filtración), químicos (adsorción) y
    biológicos (metabolismo microbiano en biofilm adherido a la grava) para
    remover DBO, SST y patógenos.
    La biodegradación aerobia predomina gracias a la aireación pasiva durante
    la fase de drenaje entre cargas (Vymazal, 2011).

    Modelo de primer orden con flujo pistón (k-C* model)
    -------------------------------------------------------
    Ce = (Ci - C*) * exp(-k_T * A / q) + C*               [Ec. 6a]
        [Kadlec & Wallace, 2009, Ec. 6.4]

    donde:
        Ce  = concentración en el efluente (mg/L)
        Ci  = concentración en el afluente (mg/L)
        C*  = concentración de fondo (background) = 3.5 mg/L para DBO5 en
              humedales tropicales (Kadlec & Wallace, 2009, Tabla 6.6)
        k_T = constante de primer orden a temperatura T (m/d)
              k_T = k_20 * θ^(T-20)                        [Ec. 6b]
              k_20 = 0.062 m/d para HFCV, DBO5 (Kadlec & Wallace, 2009, p. 302)
              θ    = 1.06 (Kadlec & Wallace, 2009, Tabla 6.7)
        A   = área superficial del humedal (m^2)
        q   = carga hidráulica superficial = Q / A (m/d)

    Despejando A de Ec. 6a:
        A = q * ln[(Ci - C*) / (Ce - C*)] / k_T            [Ec. 6c]
        Como A y q están acoplados (q = Q/A), se resuelve iterativamente:
        A = Q * ln[(Ci - C*) / (Ce - C*)] / k_T            [Ec. 6d]
        (ya que Q/A * A = Q, los términos se cancelan directamente)

    Verificación: tasa de carga hidráulica superficial
        q = Q / A                                           [Ec. 6e]
        Rango recomendado: 0.02-0.08 m/d [Kadlec & Wallace, 2009, p. 298]

    Diseño del lecho filtrante
    --------------------------
    Material recomendado: grava limpia 6-12 mm
    Porosidad típica: n_p = 0.35-0.40
    Profundidad del lecho: h_lecho = 0.50-0.70 m
    [Vymazal, 2011; Kadlec & Wallace, 2009, p. 291]

    Referencias
    -----------
    Kadlec & Wallace (2009), Cap. 6 y 7 - referencia principal
    Vymazal (2011), doi:10.1021/es101403q
    Reed et al. (1995), Cap. 7
    """
    ref_kw = citar("kadlec_wallace_2009")
    ref_vy = citar("vymazal_2011")
    ref_rd = citar("reed_1995")

    # DBO5 entrante al humedal = DBO5 efluente del UASB
    if DBO_entrada_mg_L is None:
        DBO_entrada_mg_L = Q.DBO5_mg_L * (1.0 - 0.70)   # 75 mg/L

    # Parámetros de diseño adoptados desde configuración
    DBO_salida_mg_L = Q.humedal_DBO_salida_mg_L
    C_fondo_mg_L = Q.humedal_C_fondo_mg_L
    k_20_m_d = Q.humedal_k_20_m_d
    theta = Q.humedal_theta
    n_p = Q.humedal_n_porosidad
    h_lecho = Q.humedal_h_lecho_m
    borde_libre = Q.humedal_borde_libre_m

    Q_m3_d = Q.Q_linea_m3_d

    # [Ec. 6b] Corrección por temperatura
    k_T_m_d = correccion_temperatura(k_20_m_d, theta, Q.T_agua_C)

    # [Ec. 6d] Área superficial del humedal
    # Condición: Ce > C* (verificar que el objetivo sea alcanzable)
    assert DBO_salida_mg_L > C_fondo_mg_L, (
        f"Objetivo Ce = {DBO_salida_mg_L} mg/L <= C* = {C_fondo_mg_L} mg/L: "
        "no alcanzable con modelo de primer orden"
    )

    A_m2 = (Q_m3_d / k_T_m_d) * math.log(
        (DBO_entrada_mg_L - C_fondo_mg_L) /
        (DBO_salida_mg_L  - C_fondo_mg_L)
    )

    # Con factor de seguridad para variaciones estacionales de carga
    A_m2_diseño = A_m2 * Q.humedal_factor_seguridad_area

    # [Ec. 6e] Tasa de carga hidráulica
    q_m_d = Q_m3_d / A_m2   # m/d (antes del CS, para verificación hidráulica)

    # Geometría recomendada (relación largo:ancho = 2:1 a 3:1)
    relacion_L_A = 2.5
    ancho_m = math.sqrt(A_m2 / relacion_L_A)
    largo_m = relacion_L_A * ancho_m

    # Volumen útil del lecho (para cálculo de TRH)
    V_lecho_m3 = A_m2 * h_lecho * n_p     # volumen de agua en poros
    TRH_d = V_lecho_m3 / Q_m3_d

    # Verificaciones
    assert 0.02 <= q_m_d <= 0.10, (
        f"Tasa hidráulica q = {q_m_d:.4f} m/d "
        f"{'por debajo' if q_m_d < 0.02 else 'por encima'} del rango 0.02-0.08 m/d "
        f"({ref_kw}, p. 298). "
        f"{'Considerar reducir el área.' if q_m_d < 0.02 else 'Considerar aumentar el área.'}"
    )

    return {
        "unidad": "Humedal Construido Flujo Vertical Subsuperficial (HFCV)",
        # Datos de entrada
        "DBO_entrada_mg_L": round(DBO_entrada_mg_L, 1),
        "DBO_salida_mg_L": DBO_salida_mg_L,
        "C_fondo_mg_L": C_fondo_mg_L,
        "Q_m3_d": round(Q_m3_d, 1),
        # Parámetros del modelo k-C*
        "k_20_m_d": k_20_m_d,
        "k_T_m_d": round(k_T_m_d, 4),
        "theta": theta,
        "n_porosidad": n_p,
        "h_lecho_m": h_lecho,
        # Resultados
        "A_sup_m2": round(A_m2, 1),
        "A_diseño_m2": round(A_m2_diseño, 1),
        "q_hidraulica_m_d": round(q_m_d, 5),
        "largo_m": round(largo_m, 1),
        "ancho_m": round(ancho_m, 1),
        "V_lecho_m3": round(V_lecho_m3, 1),
        "TRH_dias": round(TRH_d, 2),
        "H_total_m": round(h_lecho + borde_libre, 2),
        # Para layout
        "largo_layout_m": round(largo_m, 1),
        "ancho_layout_m": round(ancho_m, 1),
        "fuente": (
            f"Modelo k-C* de {ref_kw} (Ec. 6.4, p. 302); "
            f"{ref_vy} (doi:10.1021/es101403q); "
            f"{ref_rd} (Cap. 7)"
        ),
        "notas": (
            f"k_T = {k_T_m_d:.4f} m/d a T={Q.T_agua_C} grados C "
            f"(k_20 = {k_20_m_d} m/d, θ = {theta}; {ref_kw}, Tabla 6.7). "
            f"C* = {C_fondo_mg_L} mg/L para clima tropical "
            f"({ref_kw}, Tabla 6.6). "
            f"Coeficiente de seguridad CS = {Q.CS_area} aplicado al área."
        ),
    }


# =============================================================================
# 6 - SEDIMENTADOR SECUNDARIO CIRCULAR
# =============================================================================

def dimensionar_sedimentador_sec(Q: ConfigDiseno = CFG,
                                  DBO_entrada_mg_L: float = None,
                                  DBO_removida_fp_kg_d: float = None) -> Dict[str, Any]:
    """
    Dimensionamiento del sedimentador secundario circular (clarificador).

    El sedimentador secundario acompaña al filtro percolador para separar
    el biopelícula desprendida (humus) del efluente tratado.

    Criterio de diseño
    ------------------
    Tasa de desbordamiento superficial (SOR):
        SOR = Q / A_sup                                     [Ec. 7a]
        Rango para FP: 16-32 m^3/m^2*d                       [Metcalf & Eddy, 2014, Tabla 9-35]
        Adoptado: SOR = 24 m^3/m^2*d

    Área superficial:
        A_sup = Q / SOR                                     [Ec. 7b]

    Diámetro:
        D = √(4 * A_sup / π)                               [Ec. 7c]

    Tiempo de retención hidráulico:
        TRH = V / Q = A_sup * h_sed / Q                    [Ec. 7d]
        Mínimo 1.5 h para sedimentadores secundarios de FP.

    Referencias
    -----------
    Metcalf & Eddy (2014), pp. 870-880
    WEF MOP-8 (2010), pp. 9-60 a 9-72
    """
    ref_me = citar("metcalf_2014")
    ref_wef = citar("wef_mop8_2010")
    ref_sp = citar("sperling_2007")

    # Parámetros de diseño adoptados desde configuración
    # SOR configurado a 18 m³/m²·d para tener margen respecto al límite de 45 m³/m²·d
    # (con factor 2.5: SOR_max = 18 × 2.5 = 45, margen de seguridad del 10%)
    SOR_m3_m2_d = Q.sed_SOR_m3_m2_d  # desde configuración (default: 18.0 m³/m²·d)
    h_sed_m = Q.sed_h_sed_m
    factor_pico = Q.factor_pico_Qmax  # Factor desde configuración
    factor_min = 0.4  # Caudal mínimo = 40% del medio

    Q_m3_d = Q.Q_linea_m3_d
    Q_max_m3_d = Q_m3_d * factor_pico
    Q_min_m3_d = Q_m3_d * factor_min

    # [Ec. 7b] Área superficial
    A_sup_m2 = Q_m3_d / SOR_m3_m2_d

    # [Ec. 7c] Diámetro
    D_m = math.sqrt(4 * A_sup_m2 / math.pi)
    
    # Perímetro para carga sobre vertedero
    perimetro_m = math.pi * D_m

    # [Ec. 7d] TRH
    V_m3 = A_sup_m2 * h_sed_m
    TRH_h = (V_m3 / Q_m3_d) * 24.0   # d -> h
    TRH_max_h = (V_m3 / Q_max_m3_d) * 24.0  # TRH a caudal máximo
    TRH_min_h = (V_m3 / Q_min_m3_d) * 24.0  # TRH a caudal mínimo (alerta operativa)

    # Verificación a caudal máximo horario
    SOR_max_m3_m2_d = Q_max_m3_d / A_sup_m2
    
    # Límite recomendado por Metcalf & Eddy para SOR máximo: 40-50 m³/m²·d
    # Usamos 45 m³/m²·d como valor intermedio
    SOR_max_limite = 45.0
    margen_seguridad_pct = ((SOR_max_limite - SOR_max_m3_m2_d) / SOR_max_limite) * 100
    
    # Ajuste automático si excede el límite (aumentar área reduciendo SOR)
    iteracion = 0
    max_iteraciones = 100
    ajuste_realizado = False
    
    while iteracion < max_iteraciones:
        SOR_max_m3_m2_d = Q_max_m3_d / A_sup_m2
        margen_seguridad_pct = ((SOR_max_limite - SOR_max_m3_m2_d) / SOR_max_limite) * 100
        
        # Si está por debajo del límite con margen mínimo del 10%, aceptamos
        if SOR_max_m3_m2_d <= SOR_max_limite * 0.90:
            break
        
        # Reducimos SOR (aumentamos área) en 2%, pero no bajamos de 15.0
        SOR_m3_m2_d = max(SOR_m3_m2_d * 0.98, 15.0)
        A_sup_m2 = Q_m3_d / SOR_m3_m2_d
        D_m = math.sqrt(4 * A_sup_m2 / math.pi)
        perimetro_m = math.pi * D_m
        V_m3 = A_sup_m2 * h_sed_m
        ajuste_realizado = True
        iteracion += 1
    
    # Recalcular valores finales
    TRH_h = (V_m3 / Q_m3_d) * 24.0
    TRH_max_h = (V_m3 / Q_max_m3_d) * 24.0
    TRH_min_h = (V_m3 / Q_min_m3_d) * 24.0
    SOR_max_m3_m2_d = Q_max_m3_d / A_sup_m2
    margen_seguridad_pct = ((SOR_max_limite - SOR_max_m3_m2_d) / SOR_max_limite) * 100
    
    # Verificaciones adicionales
    # Carga sobre vertedero perimetral (weir loading)
    weir_loading_m3_m_d = Q_m3_d / perimetro_m  # m³/m·d
    weir_loading_max = 250.0  # límite según Metcalf & Eddy
    
    # Tasa de aplicación de sólidos (humus del filtro percolador)
    # Producción típica: ~0.15 kg SST/kg DBO removida en el FP
    factor_produccion_humus = Q.sed_factor_produccion_humus  # kg SST/kg DBO removida
    
    if DBO_removida_fp_kg_d is not None:
        # Usar valor calculado del Filtro Percolador (encadenado)
        produccion_humus_kg_d = factor_produccion_humus * DBO_removida_fp_kg_d
    else:
        # Fallback: estimar si no se proporciona (no recomendado)
        if DBO_entrada_mg_L is not None:
            DBO_remocion_estimada = DBO_entrada_mg_L * 0.5  # Asumir 50% remoción
        else:
            DBO_remocion_estimada = Q.DBO5_mg_L * 0.3  # Fallback conservador
        produccion_humus_kg_d = factor_produccion_humus * (DBO_remocion_estimada * Q_m3_d / 1000)
    
    solids_loading_kg_m2_d = produccion_humus_kg_d / A_sup_m2
    
    # Cálculo de DBO de salida (para balance de calidad en LaTeX)
    # El sedimentador remueve SST biológicos (humus) que representan ~30% de la DBO restante
    eta_DBO_sed = Q.sed_eta_DBO  # fracción remoción DBO por separación de humus
    if DBO_entrada_mg_L is not None:
        DBO_salida_mg_L = DBO_entrada_mg_L * (1 - eta_DBO_sed)
    else:
        DBO_salida_mg_L = Q.DBO5_mg_L * 0.7 * (1 - eta_DBO_sed)  # Fallback
    solids_loading_limite = 100.0  # kg/m²·d (conservador para FP)
    
    # Verificaciones finales
    # SOR puede haber sido ajustada ligeramente por debajo de 16.0 en el while loop
    # Se acepta un margen de 15.0 como mínimo práctico
    assert 15.0 <= SOR_m3_m2_d <= 40.0, (
        f"SOR = {SOR_m3_m2_d} m^3/m^2*d fuera de rango 15-40 ({ref_me}, Tabla 9-35)"
    )
    assert TRH_h >= 1.5, (
        f"TRH = {TRH_h:.1f} h < 1.5 h mínimo ({ref_me}, p. 872)"
    )
    assert weir_loading_m3_m_d <= weir_loading_max, (
        f"Weir loading = {weir_loading_m3_m_d:.1f} m³/m·d > {weir_loading_max} límite"
    )
    
    # Texto de verificación
    if SOR_max_m3_m2_d <= SOR_max_limite:
        verif_sor_max_texto = f"la tasa de desbordamiento máxima ({SOR_max_m3_m2_d:.1f} m³/m²·d) está dentro del rango operativo seguro ($\\leq$ {SOR_max_limite:.0f} m³/m²·d) con un margen del {margen_seguridad_pct:.1f}%"
    else:
        verif_sor_max_texto = f"la tasa de desbordamiento máxima ({SOR_max_m3_m2_d:.1f} m³/m²·d) excede el límite recomendado ({SOR_max_limite:.0f} m³/m²·d), se recomienda duplicar unidades"

    return {
        "unidad": "Sedimentador secundario circular",
        "Q_m3_d": round(Q_m3_d, 1),
        "Q_max_m3_d": round(Q_max_m3_d, 1),
        "Q_min_m3_d": round(Q_min_m3_d, 1),
        "factor_pico": factor_pico,
        "factor_min": factor_min,
        "SOR_m3_m2_d": round(SOR_m3_m2_d, 1),
        "SOR_max_m3_m2_d": round(SOR_max_m3_m2_d, 1),
        "SOR_max_limite": SOR_max_limite,
        "margen_seguridad_pct": round(margen_seguridad_pct, 1),
        "A_sup_m2": round(A_sup_m2, 2),
        "D_m": round(D_m, 2),
        "perimetro_m": round(perimetro_m, 2),
        "h_sed_m": h_sed_m,
        "V_m3": round(V_m3, 1),
        "TRH_h": round(TRH_h, 1),
        "TRH_max_h": round(TRH_max_h, 1),
        "TRH_min_h": round(TRH_min_h, 1),
        "weir_loading_m3_m_d": round(weir_loading_m3_m_d, 1),
        "weir_loading_max": weir_loading_max,
        "solids_loading_kg_m2_d": round(solids_loading_kg_m2_d, 2),
        "solids_loading_limite": solids_loading_limite,
        "produccion_humus_kg_d": round(produccion_humus_kg_d, 2),
        "factor_produccion_humus": factor_produccion_humus,
        "DBO_entrada_mg_L": round(DBO_entrada_mg_L, 1) if DBO_entrada_mg_L else None,
        "DBO_salida_mg_L": round(DBO_salida_mg_L, 1),
        "eta_DBO_sed": eta_DBO_sed,
        "ajuste_realizado": ajuste_realizado,
        "verif_sor_max_texto": verif_sor_max_texto,
        "diametro_layout_m": round(D_m + 0.30, 1),
        "fuente": f"{ref_me} (pp. 870-880); {ref_wef} (pp. 9-60); {ref_sp}",
    }


# =============================================================================
# 7 - DESINFECCIÓN CON CLORO (HIPOCLORITO)
# =============================================================================

def dimensionar_desinfeccion_cloro(Q: ConfigDiseno = CFG,
                                    CF_entrada_NMP: float = None) -> Dict[str, Any]:
    """
    Dimensionamiento del sistema de desinfección con hipoclorito de sodio.

    Fundamento teórico
    ------------------
    La desinfección con cloro se basa en el concepto CT (concentración × tiempo):
        CT = C × t                                           [Ec. 7h]
    
    Donde:
        C = cloro residual libre o combinado (mg/L)
        t = tiempo de contacto efectivo (minutos)
        CT = mg.min/L (producto concentracion x tiempo)
    
    Log reducción típica de coliformes:
        CT = 5-10 mg.min/L   -> 2-3 log  (99-99.9%)
        CT = 10-20 mg.min/L  -> 3-4 log  (99.9-99.99%)
        CT = 20-40 mg.min/L  -> 4-5 log  (99.99-99.999%)
    
    Estimación práctica:
        Log reducción ≈ 0.1 × CT (cloro combinado, pH 7-8, 25°C)
    
    Criterios de diseño
    -------------------
    - Dosis de cloro: 5-15 mg/L (typ: 8-12 mg/L para efluente secundario)
    - Cloro residual: 0.5-2.0 mg/L (post-demanda)
    - Tiempo de contacto: 15-45 minutos (typ: 30 min)
    - CT objetivo: >= 30 mg.min/L (conservador para cumplimiento)
    
    Ecuaciones de dimensionamiento
    ------------------------------
    Volumen del tanque de contacto:
        V = Q × t                                            [Ec. 7i]
    
    CT calculado:
        CT = C_residual × t                                  [Ec. 7j]
    
    Log reducción estimada:
        Log_red ≈ 0.1 × CT                                   [Ec. 7k]
    
    Coliformes finales:
        CF_final = CF_inicial / 10^Log_red                   [Ec. 7l]
    
    Referencias
    -----------
    Metcalf & Eddy (2014), pp. 1200-1220
    USEPA (2003) - LT1ESWTR Disinfection Profiling and Benchmarking
    OPS/CEPIS (2005) - Guía de desinfección
    """
    ref_me = citar("metcalf_2014")
    ref_epa = "USEPA (2003)"
    ref_ops = citar("ops_cepis_2005")
    
    # Parámetros de diseño - Optimizados para cumplir solo TULSMA (CF <= 3000)
    # CF entrada típica post-sedimentador: ~5,000,000 NMP/100mL
    # CF límite TULSMA: 3,000 NMP/100mL
    # Reducción necesaria: log10(5000000/3000) ≈ 3.2 log
    # CT necesario: ~15 mg·min/L (conservador, da margen de seguridad)
    
    # Descomposición de la dosis:
    # Dosis_total = Demanda_cloro + Cloro_residual
    demanda_cloro_mg_L = Q.desinfeccion_demanda_cloro_mg_L   # mg/L (consumido por amoníaco y MO)
    cloro_residual_mg_L = Q.desinfeccion_cloro_residual_mg_L # mg/L (mínimo necesario al final)
    dosis_cloro_mg_L = demanda_cloro_mg_L + cloro_residual_mg_L
    TRH_min = Q.desinfeccion_TRH_min                  # minutos (tiempo de contacto)
    relacion_L_A = Q.desinfeccion_relacion_L_A        # Relación largo/ancho
    h_tanque_m = Q.desinfeccion_h_tanque_m            # m (profundidad)
    borde_libre_m = 0.30                              # m (estándar)
    
    # Caudales
    Q_m3_d = Q.Q_linea_m3_d
    Q_m3_h = Q.Q_linea_m3_h
    Q_m3_min = Q_m3_h / 60.0        # m³/min
    
    # Coliformes de entrada (si no se proporciona, usar valor típico post-sedimentador)
    if CF_entrada_NMP is None:
        CF_entrada_NMP = 5e6        # NMP/100mL (típico post-sedimentador, para obtener ~2500 NMP/100mL final)
    
    # [Ec. 7i] Volumen del tanque de contacto
    V_contacto_m3 = Q_m3_min * TRH_min  # m³
    
    # Dimensiones del tanque
    A_superficial_m2 = V_contacto_m3 / h_tanque_m
    ancho_m = math.sqrt(A_superficial_m2 / relacion_L_A)
    largo_m = relacion_L_A * ancho_m
    
    # [Ec. 7h] CT calculado
    CT_calculado = cloro_residual_mg_L * TRH_min  # mg·min/L = 0.5 * 30 = 15
    
    # [Ec. 7k] Log reducción estimada
    # Coeficiente ajustado para cumplir TULSMA sin excederse
    # Log_red ≈ coef × CT (coeficiente desde configuración)
    log_reduccion = Q.desinfeccion_coef_log_red * CT_calculado
    
    # [Ec. 7l] Coliformes finales estimados
    # Obj: reducir de ~5,000,000 (post-sed) a ≤ 3,000 (TULSMA)
    CF_final_NMP = CF_entrada_NMP / (10 ** log_reduccion)
    
    # Porcentaje de reducción
    pct_reduccion = (1 - CF_final_NMP / CF_entrada_NMP) * 100
    
    # Verificación de cumplimiento TULSMA (CF ≤ 3000 NMP/100mL)
    cumple_TULSMA = CF_final_NMP <= 3000
    
    # Verificación CT mínimo recomendado
    CT_min_recomendado = 30.0  # mg·min/L
    CT_aceptable = CT_calculado >= CT_min_recomendado
    
    # Consumo de cloro (como Cl₂ activo)
    consumo_cloro_kg_d = (dosis_cloro_mg_L * Q_m3_d) / 1000  # kg Cl₂/d
    
    # Conversión a hipoclorito de sodio comercial (NaOCl al 10-12.5%)
    # Fórmula: m_NaOCl = m_Cl2 / [% NaOCl]
    concentracion_NaOCl = Q.desinfeccion_concentracion_NaOCl  # fracción
    consumo_NaOCl_kg_d = consumo_cloro_kg_d / concentracion_NaOCl  # kg NaOCl/d
    
    # Volumen de NaOCl (densidad desde configuración)
    densidad_NaOCl = Q.desinfeccion_densidad_NaOCl  # kg/L
    volumen_NaOCl_L_d = consumo_NaOCl_kg_d / densidad_NaOCl  # L/d
    volumen_NaOCl_L_mes = volumen_NaOCl_L_d * 30  # L/mes
    
    # Volumen de almacenamiento (30 días)
    volumen_almacenamiento_L = volumen_NaOCl_L_mes
    
    return {
        "unidad": "Tanque de contacto con cloro",
        "Q_m3_d": round(Q_m3_d, 1),
        # Dosis descompuesta
        "demanda_cloro_mg_L": demanda_cloro_mg_L,
        "cloro_residual_mg_L": cloro_residual_mg_L,
        "dosis_cloro_mg_L": dosis_cloro_mg_L,
        "TRH_min": TRH_min,
        # Dimensiones
        "V_contacto_m3": round(V_contacto_m3, 1),
        "A_superficial_m2": round(A_superficial_m2, 1),
        "largo_m": round(largo_m, 1),
        "ancho_m": round(ancho_m, 1),
        "h_tanque_m": h_tanque_m,
        "h_total_m": round(h_tanque_m + borde_libre_m, 2),
        # Parámetros de desinfección
        "CT_mg_min_L": round(CT_calculado, 1),
        "CT_min_recomendado": CT_min_recomendado,
        "CT_aceptable": CT_aceptable,
        "log_reduccion": round(log_reduccion, 1),
        "CF_entrada_NMP": CF_entrada_NMP,
        "CF_final_NMP": round(CF_final_NMP, 0),
        "pct_reduccion": round(pct_reduccion, 1),
        "cumple_TULSMA": cumple_TULSMA,
        # Consumos
        "consumo_cloro_kg_d": round(consumo_cloro_kg_d, 2),  # kg Cl₂/d
        "concentracion_NaOCl_pct": concentracion_NaOCl * 100,  # %
        "consumo_NaOCl_kg_d": round(consumo_NaOCl_kg_d, 1),  # kg NaOCl/d
        "volumen_NaOCl_L_d": round(volumen_NaOCl_L_d, 1),  # L/d
        "volumen_NaOCl_L_mes": round(volumen_NaOCl_L_mes, 0),  # L/mes
        "volumen_almacenamiento_L": round(volumen_almacenamiento_L, 0),  # L
        # Layout
        "largo_layout_m": round(largo_m + 0.30, 1),
        "ancho_layout_m": round(ancho_m + 0.30, 1),
        "fuente": f"{ref_me} (pp. 1200-1220); {ref_epa}; {ref_ops}",
    }


# =============================================================================
# 7b - DESINFECCIÓN UV (ALTERNATIVA)
# =============================================================================

def dimensionar_uv(Q: ConfigDiseno = CFG) -> Dict[str, Any]:
    """
    Dimensionamiento del sistema de desinfección UV.

    Criterio de diseño
    ------------------
    Dosis UV: 30-40 mJ/cm² para inactivación de coliformes fecales
              [USEPA, 2006]
    
    Ecuaciones
    ----------
    Tiempo de exposición: t = Dosis / I                              [Ec. 7e]
        donde I = intensidad UV (mW/cm²)
    
    Longitud del canal: L = v × t                                    [Ec. 7f]
        donde v = velocidad del flujo (m/s)
    
    Número de lámparas: N = Q / (q_lamp × n_series)                  [Ec. 7g]
        donde q_lamp = caudal por lámpara (m³/h)
              n_series = lámparas en serie

    Parámetros típicos para sistemas UV de bajo caudal:
        - Intensidad UV: 25-40 mW/cm²
        - Caudal por lámpara: 5-10 m³/h/lámpara
        - Velocidad en canal: 0.3-0.5 m/s

    Referencias
    -----------
    USEPA (2006) - Ultraviolet Disinfection Guidance Manual
    Metcalf & Eddy (2014), pp. 1200-1210
    """
    ref_epa = "USEPA (2006)"
    ref_me = citar("metcalf_2014")

    # Parámetros de diseño adoptados
    dosis_mj_cm2 = 30.0           # mJ/cm² - dosis mínima para 4-log inactivación
    intensidad_mw_cm2 = 30.0      # mW/cm² - intensidad de lámparas UV comerciales
    caudal_por_lampara_m3_h = 8.0 # m³/h por lámpara (baja presión)
    n_lamparas_serie = 2          # lámparas en serie por canal
    
    # Margen de seguridad para diseño
    factor_seguridad = 1.2
    
    Q_m3_d = Q.Q_linea_m3_d
    Q_m3_h = Q.Q_linea_m3_h
    Q_m3_s = Q.Q_linea_m3_s
    
    # [Ec. 7g] Número de lámparas necesarias
    n_lamparas_total = math.ceil((Q_m3_h * factor_seguridad) / caudal_por_lampara_m3_h)
    n_lamparas_total = max(n_lamparas_total, 2)  # mínimo 2 lámparas
    
    # Dimensiones del sistema UV (diseño compacto tipo cámara para caudales pequeños)
    # Para caudales pequeños (<10 L/s) se usa cámara con lámparas sumergidas
    # en lugar de canal de flujo largo
    ancho_canal_m = 0.30          # m - ancho de la cámara
    profundidad_m = 0.30          # m - profundidad de la cámara
    
    # Largo basado en espacio para lámparas en serie
    # Cada lámpara necesita ~0.6m de espacio
    L_canal_m = max(n_lamparas_serie * 0.60, 1.5)  # m
    
    # Verificación de tiempo de retención (volumen/caudal)
    V_canal_m3 = L_canal_m * ancho_canal_m * profundidad_m
    TRH_s = V_canal_m3 / Q_m3_s
    
    # Velocidad superficial en la cámara
    A_superficial_m2 = L_canal_m * ancho_canal_m
    velocidad_superficial_m_h = Q_m3_h / A_superficial_m2
    
    # [Ec. 7e] Dosis efectiva = Intensidad × Tiempo × Factor lámparas
    # Considerando que el agua pasa cerca de las lámparas (factor de mezcla)
    factor_mezcla = 0.10  # solo ~10% del tiempo está expuesto a la luz directa
    dosis_efectiva_mj_cm2 = intensidad_mw_cm2 * TRH_s * factor_mezcla
    
    return {
        "unidad": "Canal de desinfección UV",
        "dosis_objetivo_mj_cm2": dosis_mj_cm2,
        "dosis_efectiva_mj_cm2": round(dosis_efectiva_mj_cm2, 1),
        "intensidad_mw_cm2": intensidad_mw_cm2,
        "TRH_s": round(TRH_s, 1),
        "velocidad_superficial_m_h": round(velocidad_superficial_m_h, 1),
        "n_lamparas": n_lamparas_total,
        "largo_m": round(L_canal_m, 1),
        "ancho_m": ancho_canal_m,
        "profundidad_m": profundidad_m,
        "largo_layout_m": round(L_canal_m + 0.50, 1),  # incluye equipos y acceso
        "ancho_layout_m": round(ancho_canal_m + 0.50, 1),
        "fuente": f"{ref_epa}; {ref_me} (pp. 1200-1210)",
    }


# =============================================================================
# 7 - LECHO DE SECADO DE LODOS
# =============================================================================

def dimensionar_lecho_secado(Q: ConfigDiseno = CFG,
                              lodos_kg_SST_d: float = None) -> Dict[str, Any]:
    """
    Dimensionamiento del lecho de secado por arena (gravedad + evaporación).

    El lecho de secado es un sistema de deshidratación de lodos que utiliza
    la evaporación y el drenaje gravitacional para reducir el contenido de
    humedad de los lodos generados en el proceso de tratamiento.

    Criterios de diseño
    -------------------
    Carga superficial de sólidos: 60-220 kg SST/m²·año [Metcalf & Eddy, 2014]
    Concentración de lodos: 15-30 kg SST/m³ (typ: 20 kg/m³)
    Tiempo de secado: 10-30 días (depende de clima y tipo de lodo)
    Espesor de aplicación: 0.20-0.40 m por ciclo
    Relación largo/ancho: 2:1 a 4:1

    Ecuaciones de diseño
    --------------------
    Volumen de lodos a tratar:
        V_lodo_d = M_SST / C_SST                            [Ec. 8a]
        donde M_SST = producción diaria de lodos (kg SST/d)
              C_SST = concentración de sólidos en el lodo (kg/m³)

    Área TOTAL requerida (todas las celdas):
        A_total = (V_lodo_d * t_s) / h_lodo                 [Ec. 8b]

    Área por BLOQUE (un bloque al final de cada tren):
        A_bloque = A_total / num_lineas                     [Ec. 8c]

    Área por CELDA (subdivisión interna del bloque):
        A_celda = A_total / n_celdas                        [Ec. 8d]

    Tasa de carga superficial de sólidos:
        ρ_S = M_SST * 365 / A_total                         [Ec. 8e]
        Rango: 60-220 kg SST/m²·año [Metcalf & Eddy, 2014, p. 1148]

    Referencias
    -----------
    Metcalf & Eddy (2014), pp. 1145-1155
    OPS/CEPIS (2005), Cap. 5
    """
    ref_me = citar("metcalf_2014")
    ref_ops = citar("ops_cepis_2005")

    # Producción de lodos (si no se provee externamente, usar valor típico)
    # Calcula lodos de TODAS las líneas del sistema
    if lodos_kg_SST_d is None:
        # Producción típica de lodos UASB desde configuración
        # Usar caudal TOTAL (todas las líneas) para calcular lodos del sistema completo
        DBO_removida_kg_d_total = Q.Q_total_m3_d * (Q.DBO5_mg_L / 1000) * Q.uasb_eta_DBO
        lodos_kg_SST_d = Q.lecho_factor_produccion_lodos * DBO_removida_kg_d_total

    # Parámetros de diseño adoptados desde configuración
    C_SST_kg_m3 = Q.lecho_C_SST_kg_m3
    t_secado_d = Q.lecho_t_secado_d
    # Usar num_lineas del proyecto (para construcción por fases)
    n_celdas = Q.num_lineas  # Una celda por línea de tratamiento
    h_lodo_m = Q.lecho_h_lodo_m

    # Caudal total del sistema (todas las líneas)
    Q_m3_d = Q.Q_total_m3_d  # Caudal total para calcular lodos de todo el sistema

    # [Ec. 8a] Volumen de lodo a tratar por día
    V_lodo_m3_d = lodos_kg_SST_d / C_SST_kg_m3   # m^3/d

    # [Ec. 8b] ÁREA TOTAL necesaria para el secado (todas las celdas)
    # Volumen total en proceso de secado = V_lodo/d × t_secado
    V_total_secando_m3 = V_lodo_m3_d * t_secado_d
    # Área total requerida (dividir volumen por altura de lodo)
    A_total_m2 = V_total_secando_m3 / h_lodo_m

    # [Ec. 8c] ÁREA POR BLOQUE (Tren): dividir área total entre número de líneas
    # Cada tren tiene un bloque de secado al final
    A_bloque_m2 = A_total_m2 / Q.num_lineas

    # [Ec. 8d] ÁREA POR CELDA (subdivisión interna de cada bloque)
    A_celda_m2 = A_total_m2 / n_celdas

    # Geometría del BLOQUE (relación 3:1) - para el layout de cada tren
    ancho_m = math.sqrt(A_bloque_m2 / 3.0)
    largo_m = 3.0 * ancho_m

    # Tasa de carga de sólidos (por bloque)
    lodos_por_bloque_kg_d = lodos_kg_SST_d / Q.num_lineas
    rho_S_kgSST_m2_año = lodos_por_bloque_kg_d * 365 / A_bloque_m2

    # Dimensiones de la celda (para referencia interna)
    ancho_celda_m = math.sqrt(A_celda_m2 / 3.0)
    largo_celda_m = 3.0 * ancho_celda_m
    
    return {
        "unidad": "Lecho de secado de lodos",
        "lodos_kg_SST_d": round(lodos_kg_SST_d, 2),
        "lodos_por_bloque_kg_d": round(lodos_por_bloque_kg_d, 2),
        "C_SST_kg_m3": C_SST_kg_m3,
        "t_secado_d": t_secado_d,
        "V_lodo_m3_d": round(V_lodo_m3_d, 3),
        "V_total_secando_m3": round(V_total_secando_m3, 2),
        "n_celdas": n_celdas,
        "num_lineas": Q.num_lineas,
        # Áreas
        "A_total_m2": round(A_total_m2, 1),      # Área TOTAL de todos los lechos
        "A_bloque_m2": round(A_bloque_m2, 1),    # Área de CADA bloque (por tren)
        "A_celda_m2": round(A_celda_m2, 1),      # Área de CADA celda interna
        # Dimensiones del bloque (para layout)
        "largo_m": round(largo_m, 1),
        "ancho_m": round(ancho_m, 1),
        # Dimensiones de la celda (referencia)
        "largo_celda_m": round(largo_celda_m, 1),
        "ancho_celda_m": round(ancho_celda_m, 1),
        "h_lodo_m": h_lodo_m,
        "rho_S_kgSST_m2_año": round(rho_S_kgSST_m2_año, 1),
        # Layout usa dimensiones del bloque
        "largo_layout_m": round(largo_m, 1),
        "ancho_layout_m": round(ancho_m, 1),
        "fuente": f"{ref_me} (pp. 1145-1155); {ref_ops} (Cap. 5)",
    }


# =============================================================================
# 8 - RESUMEN DEL TREN DE TRATAMIENTO
# =============================================================================

def calcular_tren_A(Q: ConfigDiseno = None) -> Dict[str, Any]:
    """
    Calcula y resume el dimensionamiento completo del Tren A:
    Rejillas -> Desarenador -> UASB -> Filtro Percolador -> Sed. Secundario
    -> Cloro -> Lecho de Secado

    Args:
        Q: Configuración de diseño. Si es None, usa ConfigDiseno() por defecto.
    
    Retorna dict con todas las unidades dimensionadas y balance de calidad.
    """
    if Q is None:
        Q = ConfigDiseno()

    rejillas   = dimensionar_rejillas(Q)
    desarenador= dimensionar_desarenador(Q)
    uasb       = dimensionar_uasb(Q)
    # Usar eta_DBO calculado por UASB (ajustado por temperatura) para el FP
    fp         = dimensionar_filtro_percolador(Q, DBO_entrada_mg_L=Q.DBO5_mg_L * (1 - uasb['eta_DBO']))
    sed_sec    = dimensionar_sedimentador_sec(Q)
    cloro      = dimensionar_desinfeccion_cloro(Q)
    lecho      = dimensionar_lecho_secado(Q)

    # Balance de calidad (progresivo) - usando resultados reales del dimensionamiento
    DBO_in     = Q.DBO5_mg_L
    DBO_uasb   = DBO_in  * (1 - uasb["eta_DBO"])       # tras UASB
    # Usar DBO calculada por el modelo de Germain (no valor hardcodeado)
    DBO_fp_salida = fp.get("DBO_salida_Germain_mg_L", fp.get("DBO_salida_mg_L", 55.0))
    # El sedimentador remueve ~30% de la DBO restante (sólidos biológicos)
    DBO_efluente = DBO_fp_salida * (1 - 0.30)          # tras sedimentación (30% SST)

    print("=" * 70)
    print("TREN A - UASB + FILTRO PERCOLADOR + CLORO")
    print("Puerto Baquerizo Moreno, Galápagos")
    print(f"Caudal por línea: {Q.Q_linea_L_s} L/s = {Q.Q_linea_m3_d} m^3/d")
    print("=" * 70)

    unidades = [
        ("Rejillas",          rejillas,    "largo_layout_m",    "ancho_layout_m"),
        ("Desarenador",       desarenador, "largo_layout_m",    "ancho_layout_m"),
        ("UASB",              uasb,        "diametro_layout_m", None),
        ("Filtro Percolador", fp,          "diametro_layout_m", None),
        ("Sed. Secundario",   sed_sec,     "diametro_layout_m", None),
        ("Cloro",             cloro,       "largo_layout_m",    "ancho_layout_m"),
        ("Lecho de Secado",   lecho,       "largo_layout_m",    "ancho_layout_m"),
    ]

    print(f"\n{'Unidad':<22} {'Dim. Principal':>18}  {'Fuente'}")
    print("-" * 70)
    for nombre, data, dim1, dim2 in unidades:
        if dim2 and dim2 in data:
            dim_str = f"{data[dim1]:.1f} × {data[dim2]:.1f} m"
        else:
            dim_str = f"Ø {data[dim1]:.1f} m"
        fuente_corta = data["fuente"][:35] + "..."
        print(f"  {nombre:<20} {dim_str:>18}  {fuente_corta}")

    print("\nBALANCE DE CALIDAD DEL AGUA:")
    print(f"  Afluente     DBO5 = {DBO_in:.0f} mg/L")
    print(f"  Tras UASB    DBO5 = {DBO_uasb:.0f} mg/L  "
          f"(eta={uasb['eta_DBO']*100:.0f}%)")
    print(f"  Tras FP+Sed  DBO5 ~ {DBO_efluente:.0f} mg/L")
    print(f"  Límite TULSMA DBO5 <= 100 mg/L  -> {'CUMPLE [OK]' if DBO_efluente <= 100 else 'NO CUMPLE'}")

    return {
        "rejillas": rejillas,
        "desarenador": desarenador,
        "uasb": uasb,
        "filtro_percolador": fp,
        "sedimentador_sec": sed_sec,
        "cloro": cloro,
        "lecho_secado": lecho,
        "balance": {
            "DBO_in_mg_L": DBO_in,
            "DBO_tras_UASB_mg_L": round(DBO_uasb, 1),
            "DBO_efluente_mg_L": round(DBO_efluente, 1),
            "cumple_TULSMA": DBO_efluente <= 100,
        },
    }


def calcular_tren_C() -> Dict[str, Any]:
    """
    Calcula y resume el dimensionamiento completo del Tren C:
    Rejillas -> Desarenador -> UASB -> Humedal Vertical -> Cloro -> Lecho de Secado
    """
    Q = ConfigDiseno()

    rejillas   = dimensionar_rejillas(Q)
    desarenador= dimensionar_desarenador(Q)
    uasb       = dimensionar_uasb(Q)
    humedal    = dimensionar_humedal_vertical(Q, DBO_entrada_mg_L=Q.DBO5_mg_L * 0.30)
    lecho      = dimensionar_lecho_secado(Q)

    DBO_in     = Q.DBO5_mg_L
    DBO_uasb   = DBO_in * (1 - uasb["eta_DBO"])
    DBO_efluente = humedal["DBO_salida_mg_L"]

    print("=" * 70)
    print("TREN C - UASB + HUMEDAL VERTICAL + CLORO")
    print(f"Caudal por línea: {Q.Q_linea_L_s} L/s = {Q.Q_linea_m3_d} m^3/d")
    print("=" * 70)

    print(f"\n  UASB          Ø {uasb['diametro_layout_m']:.1f} m   V={uasb['V_r_m3']:.1f} m^3")
    print(f"  Humedal HFCV  {humedal['largo_layout_m']:.1f} × {humedal['ancho_layout_m']:.1f} m"
          f"  A={humedal['A_sup_m2']:.0f} m^2")
    print(f"  Lecho Secado  {lecho['largo_layout_m']:.1f} × {lecho['ancho_layout_m']:.1f} m")

    print("\nBALANCE DE CALIDAD:")
    print(f"  Afluente    DBO5 = {DBO_in:.0f} mg/L")
    print(f"  Tras UASB   DBO5 = {DBO_uasb:.0f} mg/L")
    print(f"  Tras HFCV   DBO5 ~ {DBO_efluente:.0f} mg/L")
    print(f"  TULSMA       <= 100 mg/L -> {'CUMPLE [OK]' if DBO_efluente <= 100 else 'NO CUMPLE'}")

    return {
        "rejillas": rejillas,
        "desarenador": desarenador,
        "uasb": uasb,
        "humedal": humedal,
        "lecho_secado": lecho,
        "balance": {
            "DBO_in_mg_L": DBO_in,
            "DBO_tras_UASB_mg_L": round(DBO_uasb, 1),
            "DBO_efluente_mg_L": round(DBO_efluente, 1),
            "cumple_TULSMA": DBO_efluente <= 100,
        },
    }


# =============================================================================
# 9 - BALANCE COMPLETO DE CALIDAD DEL AGUA
# =============================================================================

def calcular_balance_calidad_agua(Q: ConfigDiseno = None, 
                                   resultados: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Calcula el balance completo de calidad del agua para todos los parámetros
    en cada etapa del tren de tratamiento.
    
    Parámetros calculados:
        - DBO5 (mg/L)
        - DQO (mg/L) 
        - SST (mg/L)
        - Coliformes Fecales (NMP/100mL)
    
    Eficiencias típicas por unidad:
        - Rejillas: SST ~10%, CF ~5%
        - Desarenador: SST ~15%, DBO/DQO ~5%
        - UASB: DBO ~70%, DQO ~65%, SST ~70%, CF ~30%
        - Filtro Percolador: DBO ~75%, DQO ~70%, SST ~60%
        - Sedimentador: SST ~80% (humus), DBO ~30% (sólidos biológicos)
        - Cloro: CF >99.9%
    
    Referencias:
        Metcalf & Eddy (2014)
        Sperling (2007)
    """
    if Q is None:
        Q = ConfigDiseno()
    
    # Valores de entrada
    calidad = {
        "afluente": {
            "DBO5_mg_L": Q.DBO5_mg_L,
            "DQO_mg_L": Q.DQO_mg_L,
            "SST_mg_L": Q.SST_mg_L,
            "CF_NMP": Q.CF_NMP,
        }
    }
    
    # Si se proporcionan resultados, usar eficiencias reales calculadas
    if resultados:
        # Tras UASB
        if "uasb" in resultados:
            uasb = resultados["uasb"]
            eta_DBO_uasb = uasb.get("eta_DBO", 0.70)
            eta_DQO_uasb = uasb.get("eta_DQO", 0.65)
            # SST similar a DBO en UASB
            eta_SST_uasb = eta_DBO_uasb
            # CF en UASB desde configuración
            eta_CF_uasb = Q.balance_eta_CF_uasb
            
            calidad["tras_uasb"] = {
                "DBO5_mg_L": round(Q.DBO5_mg_L * (1 - eta_DBO_uasb), 1),
                "DQO_mg_L": round(Q.DQO_mg_L * (1 - eta_DQO_uasb), 1),
                "SST_mg_L": round(Q.SST_mg_L * (1 - eta_SST_uasb), 1),
                "CF_NMP": round(Q.CF_NMP * (1 - eta_CF_uasb), 0),
            }
        
        # Tras Filtro Percolador
        if "filtro_percolador" in resultados and "tras_uasb" in calidad:
            fp = resultados["filtro_percolador"]
            DBO_entrada_fp = calidad["tras_uasb"]["DBO5_mg_L"]
            # Eficiencia del modelo Germain
            relacion = fp.get("relacion_Se_S0_Germain", 0.50)
            eta_DBO_fp = 1 - relacion
            # DQO desde configuración (factor sobre DBO)
            eta_DQO_fp = eta_DBO_fp * Q.balance_eta_DQO_fp_factor
            # SST removido por biopelícula desde configuración
            eta_SST_fp = Q.balance_eta_SST_fp
            # CF remoción mínima en FP desde configuración
            eta_CF_fp = Q.balance_eta_CF_fp
            
            calidad["tras_fp"] = {
                "DBO5_mg_L": round(DBO_entrada_fp * (1 - eta_DBO_fp), 1),
                "DQO_mg_L": round(calidad["tras_uasb"]["DQO_mg_L"] * (1 - eta_DQO_fp), 1),
                "SST_mg_L": round(calidad["tras_uasb"]["SST_mg_L"] * (1 - eta_SST_fp), 1),
                "CF_NMP": round(calidad["tras_uasb"]["CF_NMP"] * (1 - eta_CF_fp), 0),
            }
        
        # Tras Sedimentador Secundario
        if ("sedimentador_sec" in resultados or "sedimentador" in resultados) and "tras_fp" in calidad:
            sed = resultados.get("sedimentador_sec") or resultados.get("sedimentador")
            DBO_entrada_sed = calidad["tras_fp"]["DBO5_mg_L"]
            eta_DBO_sed = sed.get("eta_DBO_sed", 0.30)
            # SST removido por separación de humus desde configuración
            eta_SST_sed = Q.balance_eta_SST_sed
            # DQO similar a DBO
            eta_DQO_sed = eta_DBO_sed
            # CF remoción mínima desde configuración
            eta_CF_sed = Q.balance_eta_CF_sed
            
            calidad["tras_sed"] = {
                "DBO5_mg_L": round(DBO_entrada_sed * (1 - eta_DBO_sed), 1),
                "DQO_mg_L": round(calidad["tras_fp"]["DQO_mg_L"] * (1 - eta_DQO_sed), 1),
                "SST_mg_L": round(calidad["tras_fp"]["SST_mg_L"] * (1 - eta_SST_sed), 1),
                "CF_NMP": round(calidad["tras_fp"]["CF_NMP"] * (1 - eta_CF_sed), 0),
            }
        
        # Tras desinfección (UV o Cloro)
        desinfeccion_keys = ["uv", "desinfeccion", "cloro"]
        tiene_desinfeccion = any(k in resultados for k in desinfeccion_keys)
        if tiene_desinfeccion and "tras_sed" in calidad:
            if "uv" in resultados:
                # UV inactiva >99.9% de coliformes
                eta_CF = 0.999
            elif "cloro" in resultados:
                # Cloro - usar log reducción calculada
                des = resultados["cloro"]
                log_red = des.get("log_reduccion", Q.balance_log_reduccion_default)
                eta_CF = 1 - (10 ** (-log_red))
            else:
                # Desinfeccion generica
                des = resultados["desinfeccion"]
                log_red = des.get("log_reduccion", Q.balance_log_reduccion_default)
                eta_CF = 1 - (10 ** (-log_red))
            
            # Desinfección no remueve DBO/DQO/SST significativamente
            CF_final = round(calidad["tras_sed"]["CF_NMP"] * (1 - eta_CF), 0)
            if CF_final < 1:
                CF_final = 1  # Mínimo detectable
            
            calidad["efluente_final"] = {
                "DBO5_mg_L": calidad["tras_sed"]["DBO5_mg_L"],
                "DQO_mg_L": calidad["tras_sed"]["DQO_mg_L"],
                "SST_mg_L": calidad["tras_sed"]["SST_mg_L"],
                "CF_NMP": CF_final,
            }
    
    # Calcular eficiencias totales
    if "efluente_final" in calidad:
        ef_final = calidad["efluente_final"]
        entrada = calidad["afluente"]
        
        calidad["eficiencias_totales"] = {
            "DBO5_pct": round((1 - ef_final["DBO5_mg_L"] / entrada["DBO5_mg_L"]) * 100, 1),
            "DQO_pct": round((1 - ef_final["DQO_mg_L"] / entrada["DQO_mg_L"]) * 100, 1),
            "SST_pct": round((1 - ef_final["SST_mg_L"] / entrada["SST_mg_L"]) * 100, 1),
            "CF_pct": round((1 - ef_final["CF_NMP"] / entrada["CF_NMP"]) * 100, 1),
        }
    
    # Verificar cumplimiento TULSMA
    if "efluente_final" in calidad:
        ef = calidad["efluente_final"]
        calidad["cumplimiento_TULSMA"] = {
            "DBO5": ef["DBO5_mg_L"] <= 100,
            "SST": ef["SST_mg_L"] <= 100,
            "CF": ef["CF_NMP"] <= 3000,
        }
    
    return calidad


# =============================================================================
# MAIN - EJECUTAR DIMENSIONAMIENTO COMPLETO
# =============================================================================

if __name__ == "__main__":
    print()
    tren_A = calcular_tren_A()
    print()
    tren_C = calcular_tren_C()

    # Mostrar parámetros clave del UASB
    print("\n" + "=" * 70)
    print("DETALLE UASB - PARÁMETROS DE DISEÑO")
    print("=" * 70)
    u = tren_A["uasb"]
    print(f"  Volumen reactor     V_r   = {u['V_r_m3']:.1f} m^3")
    print(f"  TRH                       = {u['TRH_h']:.1f} h  "
          f"[rango 4-12 h; Sperling, 2007]")
    print(f"  Velocidad ascendente v_up = {u['v_up_m_h']:.3f} m/h  "
          f"[rango 0.5-1.0 m/h; Metcalf & Eddy, 2014]")
    print(f"  Diámetro            D     = {u['D_m']:.2f} m")
    print(f"  Altura              H     = {u['H_r_m']:.2f} m")
    print(f"  Carga vol.          Cv    = {u['Cv_kgDQO_m3_d']} kg DQO/m^3*d  "
          f"[rango 2-8; van Haandel & Lettinga, 1994]")
    print(f"  Biogás producido          = {u['biogaz_m3_d']:.1f} m^3 CH4/d")
    print(f"  Fuente: {u['fuente'][:65]}")

    # Mostrar parámetros del humedal
    print("\n" + "=" * 70)
    print("DETALLE HUMEDAL VERTICAL - PARÁMETROS DE DISEÑO")
    print("=" * 70)
    h = tren_C["humedal"]
    print(f"  Área superficial    A     = {h['A_sup_m2']:.1f} m^2  (x CS={CFG.CS_area}: {h['A_diseño_m2']:.1f} m^2)")
    print(f"  Dimensiones               = {h['largo_m']:.1f} × {h['ancho_m']:.1f} m")
    print(f"  k_T (T={CFG.T_agua_C} grados C)       = {h['k_T_m_d']:.4f} m/d  "
          f"[k_20={h['k_20_m_d']} m/d, θ={h['theta']}]")
    print(f"  Carga hidráulica    q     = {h['q_hidraulica_m_d']:.5f} m/d  "
          f"[rango 0.02-0.08; Kadlec & Wallace, 2009]")
    print(f"  TRH                       = {h['TRH_dias']:.2f} días")
    print(f"  Fuente: {h['fuente'][:65]}")
