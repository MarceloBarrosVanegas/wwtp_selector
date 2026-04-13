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
    desarenador_h_almacenamiento_arena_min_m: float = 0.25  # Rango tipico almacenamiento arena (m)
    desarenador_h_almacenamiento_arena_max_m: float = 0.30  # Rango tipico almacenamiento arena (m)
    desarenador_h_almacenamiento_arena_m: float = 0.30      # Altura adoptada almacenamiento arena (m)
    # Parámetros para Camp-Shields (verificación de velocidad crítica)
    desarenador_beta_min: float = 0.04      # Rango recomendado factor de forma
    desarenador_beta_max: float = 0.06      # Rango recomendado factor de forma
    desarenador_beta: float = 0.05          # Factor de forma partícula (rango 0.04-0.06)
    desarenador_f_darcy_min: float = 0.02   # Rango recomendado friccion Darcy-Weisbach
    desarenador_f_darcy_max: float = 0.03   # Rango recomendado friccion Darcy-Weisbach
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
    # PARÁMETROS DE CALIDAD Y ESTABILIDAD DEL PROCESO UASB
    # =========================================================================
    uasb_pH_optimo_min: float = 6.8         # pH mínimo óptimo para metanogénesis
    uasb_pH_optimo_max: float = 7.2         # pH máximo óptimo para metanogénesis
    uasb_alcalinidad_min_mg_L: float = 1000.0  # Alcalinidad mínima requerida (mg/L CaCO3)
    uasb_biogas_CH4_pct: float = 65.0       # Porcentaje metano en biogás (%)
    uasb_biogas_CO2_pct: float = 35.0       # Porcentaje CO2 en biogás (%)
    uasb_biogas_H2S_max_ppm: float = 100.0  # Límite H2S en biogás (ppm)
    uasb_lodo_estabilizado: bool = True     # El lodo UASB está estabilizado anaeróbicamente
    
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
    # FACTORES DE CONVERSIÓN SÓLIDOS - SUBPRODUCTOS (para agregación)
    # =========================================================================
    # NOTA: Estos factores permiten convertir entre bases de sólidos cuando
    # las unidades reportan en diferentes bases (SSV vs SST). Si no están
    # definidos, el agregador reportará kg_SST_d = None y lo marcará como pendiente.
    #
    # Conversión SSV → SST: SST = SSV / fraccion_SSV_en_SST
    # Ejemplo: Si SSV representa el 80% de SST (fraccion=0.80), entonces:
    #   SST = SSV / 0.80 = 1.25 × SSV
    fraccion_SSV_en_SST_lodo_uasb: float = None         # Fracción SSV/SST (ej: 0.80 = 80%)
    fraccion_SSV_en_SST_lodo_fp: float = None           # Fracción SSV/SST para biomasa FP (ej: 0.85)
    concentracion_lodo_uasb_kg_SST_m3: float = None     # Concentración lodo UASB para m3/d (ej: 40-60 kg SST/m3)
    concentracion_lodo_fp_kg_SST_m3: float = None       # Concentración humus FP para m3/d (ej: 30-50 kg SST/m3)
    
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
    fp_D_medio_min_m: float = 3.0           # Rango recomendado profundidad medio filtrante (m)
    fp_D_medio_max_m: float = 8.0           # Rango recomendado profundidad medio filtrante (m)
    fp_R_recirculacion: float = 1.0         # Tasa recirculación
    fp_H_total_m: float = 4.30              # Altura total (medio + 0.80m)
    
    # PASO 4 - Geometría del filtro (desglose de alturas)
    fp_H_distribucion_m: float = 0.20       # Espacio distribuidor-medio (0.15-0.23 m) [EPA, 2000]
    fp_H_distribucion_min_m: float = 0.15   # Rango recomendado espacio distribuidor-medio (m)
    fp_H_distribucion_max_m: float = 0.23   # Rango recomendado espacio distribuidor-medio (m)
    fp_H_underdrain_m: float = 0.50         # Altura underdrain (0.45-0.60 m) [Metcalf & Eddy, 2014]
    fp_H_underdrain_min_m: float = 0.45     # Rango recomendado altura underdrain (m)
    fp_H_underdrain_max_m: float = 0.60     # Rango recomendado altura underdrain (m)
    fp_H_bordo_libre_fp_m: float = 0.30     # Bordo libre filtro (0.30-0.50 m)
    fp_H_bordo_libre_min_m: float = 0.30    # Rango recomendado bordo libre (m)
    fp_H_bordo_libre_max_m: float = 0.50    # Rango recomendado bordo libre (m)
    
    # PASO 6 - Distribuidor rotatorio
    fp_num_brazos: int = 2                  # Número de brazos (2 para D < 6m, 4 para D > 15m)
    fp_velocidad_boquilla_m_s: float = 2.0  # Velocidad salida boquilla (1.5-3.0 m/s)
    fp_velocidad_boquilla_min_m_s: float = 1.5  # Rango recomendado velocidad salida boquilla (m/s)
    fp_velocidad_boquilla_max_m_s: float = 3.0  # Rango recomendado velocidad salida boquilla (m/s)
    fp_rotacion_rpm_min: float = 0.5        # Rango tipico velocidad rotacion distribuidor (rpm)
    fp_rotacion_rpm_max: float = 2.0        # Rango tipico velocidad rotacion distribuidor (rpm)
    fp_vel_periferica_min_m_min: float = 0.5 # Rango tipico velocidad periferica distribuidor (m/min)
    fp_vel_periferica_max_m_min: float = 4.0 # Rango tipico velocidad periferica distribuidor (m/min)
    fp_motor_aux_min_kW: float = 0.5        # Potencia minima motor auxiliar recomendado (kW)
    fp_motor_aux_max_kW: float = 1.0        # Potencia maxima motor auxiliar recomendado (kW)
    fp_num_boquillas_por_brazo: int = 8     # Número de boquillas por brazo (5-15)
    
    # PASO 7 - Underdrain
    fp_pendiente_underdrain_pct: float = 1.0    # Pendiente mínima piso underdrain (>= 1%)
    fp_ancho_canal_central_m: float = 0.30      # Ancho canal central underdrain (0.30-0.60 m)
    fp_altura_canal_central_m: float = 0.30     # Altura canal central underdrain (m)
    fp_n_manning_underdrain: float = 0.013      # Coef. rugosidad Manning underdrain (concreto)
    fp_factor_capacidad_underdrain: float = 0.50  # Factor capacidad underdrain (diseño = Q_ap / factor)
    fp_llenado_max_underdrain: float = 0.50       # Llenado máximo permitido en canal underdrain
    
    # PASO 5 - Recirculación y caudal mínimo
    fp_factor_caudal_min_nocturno: float = 0.40   # Factor caudal mínimo nocturno (fracción de Q_medio)
    
    # PASO 8 - Ventilación
    fp_area_ventilacion_pct: float = 1.0        # Área ventilación / Área superficial (>= 1%)
    fp_Q_aire_factor: float = 0.3               # Caudal aire / caudal agua óptimo (m³/m³)
    fp_Q_aire_min_factor: float = 0.1           # Caudal aire / caudal agua mínimo (m³/m³)
    fp_apertura_ventilacion_ancho_m: float = 0.20   # Ancho apertura ventilación (m)
    fp_apertura_ventilacion_alto_m: float = 0.30    # Alto apertura ventilación (m)
    
    # PASO 10 - Especificaciones medio plástico
    fp_sup_especifica_m2_m3: float = 100.0      # Superficie específica (90-150 m²/m³)
    fp_vacios_pct: float = 94.0                 # Índice de vacíos (>= 94%)
    fp_densidad_media_kg_m3: float = 60.0       # Densidad aparente (30-100 kg/m³)
    fp_carga_agua_sobre_medio_kg_m3: float = 40.0       # Carga agua sobre medio (kg/m³)
    fp_carga_biopelicula_sobre_medio_kg_m3: float = 15.0 # Carga biopelícula sobre medio (kg/m³)
    fp_Cv_kgDBO_m3_d: float = 0.5               # Carga orgánica volumétrica (kg DBO/m³·d)
    fp_Cv_maxima_kgDBO_m3_d: float = 3.0        # Carga orgánica máxima recomendada (kg DBO/m³·d)
    fp_Q_A_limite_m3_m2_h: float = 4.0          # Límite tasa hidráulica (m³/m²·h)
    fp_Cv_minima_kgDBO_m3_d: float = 0.30       # Carga orgánica mínima recomendada (kg DBO/m³·d)
    fp_qA_min_humectacion_m3_m2_h: float = 0.5  # Tasa mínima humectación biopelícula (m³/m²·h)
    
    # CRITERIOS DE AUTOAJUSTE Y OPERACIÓN
    fp_qA_real_min_m3_m2_h: float = 1.0         # Tasa hidráulica mínima operativa (m³/m²·h)
    fp_incremento_recirculacion: float = 0.5    # Incremento gradual de R en ajustes (adimensional)
    fp_R_min: float = 1.0                       # Recirculación mínima operativa (adimensional)
    fp_R_max: float = 2.0                       # Recirculación máxima permitida (adimensional)
    fp_R_recomendado_min: float = 0.5           # Rango bibliografico recomendado para recirculacion
    fp_R_recomendado_max: float = 2.0           # Rango bibliografico recomendado para recirculacion
    fp_Q_por_brazo_min_rotacion_m3_h: float = 10.0  # Caudal mínimo por brazo para rotación hidráulica (m³/h)
    
    # CRITERIOS DE RESISTENCIA MECÁNICA DEL MEDIO
    fp_resistencia_umbral_profundidad_m: float = 3.5   # Profundidad umbral cambio resistencia (m)
    fp_resistencia_min_baja_kg_m2: float = 600         # Resistencia mínima D <= 3.5m (kg/m²)
    fp_resistencia_min_alta_kg_m2: float = 1000        # Resistencia mínima D > 3.5m (kg/m²)
    
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
    desinfeccion_NaOCl_comercial_min_pct: float = 10.0  # Rango típico NaOCl comercial (%)
    desinfeccion_NaOCl_comercial_max_pct: float = 12.5  # Rango típico NaOCl comercial (%)
    desinfeccion_demanda_cloro_min_mg_L: float = 2.0    # Rango típico demanda de cloro (mg/L)
    desinfeccion_demanda_cloro_max_mg_L: float = 5.0    # Rango típico demanda de cloro (mg/L)
    desinfeccion_cloro_residual_min_mg_L: float = 0.5   # Rango recomendado residual (mg/L)
    desinfeccion_cloro_residual_max_mg_L: float = 2.0   # Rango recomendado residual (mg/L)
    desinfeccion_dosis_cloro_min_mg_L: float = 3.0      # Rango típico dosis total (mg/L)
    desinfeccion_dosis_cloro_max_mg_L: float = 10.0     # Rango típico dosis total (mg/L)
    desinfeccion_TRH_recomendado_min: float = 15.0      # Rango recomendado TRH (min)
    desinfeccion_TRH_recomendado_max: float = 45.0      # Rango recomendado TRH (min)
    desinfeccion_CT_min_recomendado_mg_min_L: float = 30.0  # CT mínimo conservador (mg min/L)
    desinfeccion_limite_TULSMA_CF_NMP: float = 3000.0   # Límite CF para vertimiento (NMP/100mL)
    desinfeccion_CF_objetivo_NMP: float = 3000.0        # CF objetivo de diseño para desinfección (NMP/100mL)
    desinfeccion_residual_monitoreo_min_mg_L: float = 0.5 # Rango recomendado monitoreo residual (mg/L)
    desinfeccion_residual_monitoreo_max_mg_L: float = 1.0 # Rango recomendado monitoreo residual (mg/L)
    desinfeccion_almacenamiento_dias: float = 30.0      # Autonomía almacenamiento NaOCl (días)
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - HUMEDAL VERTICAL (HAFV)
    # Metodología Unificada: Sistema Clásico (Ruta A) y HAFV tropical de alta carga (Ruta B)
    # =============================================================================
    # Parámetros comunes
    desinfeccion_borde_libre_m: float = 0.30        # Bordo libre camara de contacto (m)
    desinfeccion_n_canales_serpentin: int = 5       # Numero de pasos del culebrin
    desinfeccion_ancho_canal_min_m: float = 0.50    # Ancho minimo constructivo por canal (m)
    desinfeccion_espesor_bafle_m: float = 0.15      # Espesor de muros/bafles internos (m)
    desinfeccion_relacion_recorrido_ancho_min: float = 30.0 # Criterio L recorrido/ancho para aproximar flujo piston

    humedal_DBO_salida_mg_L: float = 20.0   # DBO5 objetivo (mg/L)
    humedal_C_fondo_mg_L: float = 3.5       # Concentración fondo C* (mg/L)
    humedal_k_20_m_d: float = 0.093         # Constante a 20°C (m/d) - Kadlec & Wallace (2009), Tabla 6.6: kA,20 = 0.093 m/d para DBO5
    humedal_theta: float = 1.06             # Coeficiente temperatura
    humedal_n_porosidad: float = 0.38       # Porosidad lecho grava
    humedal_h_lecho_m: float = 0.60         # Profundidad lecho filtrante (m)
    humedal_borde_libre_m: float = 0.20     # Borde libre (m)
    humedal_factor_seguridad_area: float = 1.25  # FS para variaciones estacionales
    humedal_eta_CF: float = 0.90            # Eficiencia remoción CF en HAFV (fracción) - Kadlec & Wallace: 1-2 log (90-99%)
    
    # Algoritmo de selección de sistema (Sección 3 del manual)
    humedal_temp_limite_clasico_C: float = 15.0      # T < 15°C → Sistema Clásico obligatorio
    humedal_temp_limite_transicion_C: float = 20.0   # 15-20°C → Zona transición; ≥20°C → Ruta B candidata
    
    # RUTA A - Sistema Clásico (Cooper et al., 1996; ÖNORM B 2505)
    # Aplicable cuando: T < 20°C o criterios no favorecen Ruta B
    humedal_clasico_COS_gDBO_m2_d: float = 40.0      # Carga orgánica superficial 1ª etapa (g DBO₅/m²·d)
    humedal_clasico_area_por_PE_m2: float = 2.0      # Área por PE en 1ª etapa (m²/PE)
    humedal_clasico_n_filtros_1etapa: int = 3        # Número filtros 1ª etapa
    humedal_clasico_n_filtros_2etapa: int = 2        # Número filtros 2ª etapa
    humedal_clasico_relacion_2da_1ra: float = 0.50   # Área 2ª etapa = 50% de 1ª etapa
    humedal_clasico_HLR_1etapa_m_d: float = 0.06     # Carga hidráulica 1ª etapa (m/d) - valor medio del rango 0.02-0.08
    humedal_clasico_HLR_2etapa_m_d: float = 0.035    # Carga hidráulica 2ª etapa (m/d) - valor medio del rango 0.02-0.05
    humedal_clasico_ciclo_alim_1etapa_dias: float = 3.5  # Ciclo alimentación 1ª etapa (d)
    humedal_clasico_ciclo_reposo_1etapa_dias: float = 7.0 # Ciclo reposo 1ª etapa (d)
    humedal_clasico_ciclo_alim_2etapa_dias: float = 7.0   # Ciclo alimentación 2ª etapa (d)
    humedal_clasico_ciclo_reposo_2etapa_dias: float = 7.0 # Ciclo reposo 2ª etapa (d)
    
    # RUTA B - HAFV tropical de alta carga (adaptación basada en Molle et al., 2015)
    # Aplicable cuando: T ≥ 20°C y criterios favorecen Ruta B
    humedal_frances_OLR_gDQO_m2_d: float = 300.0     # Carga orgánica superficial (g DQO/m²·d) - conservador
    humedal_frances_HLR_m_d: float = 0.75            # Carga hidráulica superficial (m/d) - límite superior del rango 0.50-0.75
    humedal_frances_n_filtros: int = 2               # Número de filtros en paralelo
    humedal_frances_area_por_PE_m2_T22: float = 1.0  # Área por PE, T > 22°C (m²/PE)
    humedal_frances_area_por_PE_m2_T20: float = 1.3  # Área por PE, T = 20-22°C (m²/PE)
    humedal_frances_ciclo_alim_dias: float = 3.5     # Días alimentando por filtro
    humedal_frances_ciclo_reposo_dias: float = 3.5   # Días en reposo por filtro
    humedal_frances_relacion_L_A: float = 1.3         # Relación largo/ancho filtros Ruta B
    humedal_clasico_relacion_L_A: float = 2.0         # Relación largo/ancho filtros clásicos
    humedal_separacion_filtros_m: float = 1.5         # Separación entre filtros para layout (m)
    humedal_frances_h_medio_m: float = 0.85           # Profundidad media Ruta B (m)
    humedal_clasico_h_medio_m: float = 0.70           # Profundidad media sistema clásico (m)
    humedal_frances_H_total_m: float = 1.50           # Altura constructiva total Ruta B (m)
    humedal_clasico_H_total_m: float = 1.20           # Altura constructiva total sistema clásico (m)
    humedal_capa_drenaje_m: float = 0.25              # Capa drenaje para esquema/documentación (m)
    humedal_capa_grava_media_m: float = 0.30          # Capa grava media para esquema/documentación (m)
    humedal_capa_grava_fina_m: float = 0.30           # Capa grava fina para esquema/documentación (m)
    
    # Verificación cinética k-C* (complementaria/recomendada en ambas rutas)
    humedal_kC_verificar_obligatorio: bool = True    # Mantiene la verificación activa por trazabilidad del diseño
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - SEDIMENTADOR SECUNDARIO
    # =============================================================================
    sed_SOR_m3_m2_d: float = 18.0           # Tasa desbordamiento superficial (conservador)
    sed_SOR_min_m3_m2_d: float = 16.0       # Rango recomendado SOR operación normal (m³/m²·d)
    sed_SOR_max_m3_m2_d: float = 32.0       # Rango recomendado SOR operación normal (m³/m²·d)
    sed_SOR_max_limite_m3_m2_d: float = 45.0 # Límite SOR a caudal máximo horario (m³/m²·d)
    sed_h_sed_m: float = 3.50               # Profundidad lateral (m)
    sed_h_sed_min_m: float = 3.0            # Rango recomendado profundidad lateral (m)
    sed_h_sed_max_m: float = 4.5            # Rango recomendado profundidad lateral (m)
    sed_h_lodos_tolva_m: float = 0.50       # Zona de almacenamiento de lodos en tolva (m)
    sed_bordo_libre_m: float = 0.30         # Bordo libre sedimentador secundario (m)
    # Parámetros para sedimentador secundario (reusable para cualquier etapa biológica aerobia)
    sed_factor_produccion_humus: float = 0.15  # Factor producción sólidos biológicos/humus (kg SST/kg DBO removida en etapa biológica aerobia)
    sed_eta_DBO: float = 0.15               # Eficiencia remoción DBO en sedimentador (fracción) - Valor conservador según Metcalf & Eddy (2014) para sedimentador secundario tras proceso biológico aerobio (10-15%)
    sed_factor_min_Q: float = 0.40          # Factor caudal mínimo (Qmin/Qmedio) para verificación TRH mínimo
    sed_TRH_min_h: float = 1.5              # TRH mínimo sedimentador secundario (h)
    sed_TRH_min_operacion_alerta_h: float = 8.0 # Umbral operativo para alertar TRH excesivo a caudal mínimo (h)
    sed_weir_loading_max_m3_m_d: float = 250.0 # Límite carga sobre vertedero (m³/m·d)
    sed_solids_loading_limite_kg_m2_d: float = 100.0 # Límite conservador carga sólidos (kg/m²·d)
    sed_solids_loading_tipico_min_kg_m2_d: float = 50.0 # Rango típico carga sólidos (kg/m²·d)
    sed_solids_loading_tipico_max_kg_m2_d: float = 150.0 # Rango típico carga sólidos (kg/m²·d)
    sed_purga_lodos_min_h: float = 48.0     # Frecuencia mínima recomendada purga lodos (h)
    
    # =============================================================================
    # PARÁMETROS DE BALANCE DE CALIDAD DEL AGUA
    # =============================================================================
    balance_eta_CF_uasb: float = 0.30       # Eficiencia remoción CF en UASB (fracción)
    balance_eta_DQO_fp_factor: float = 0.90 # Factor para calcular ηDQO desde ηDBO en FP
    balance_eta_SST_fp: float = 0.60        # Eficiencia remoción SST en FP (fracción)
    balance_eta_CF_fp: float = 0.20         # Eficiencia remoción CF en FP (fracción)
    balance_eta_SST_sed: float = 0.80       # Eficiencia remoción SST en Sed (fracción)
    balance_eta_CF_sed: float = 0.10        # Eficiencia remoción CF en Sed (fracción)
    balance_eta_SST_humedal: float = 0.60   # Eficiencia remoción SST en Humedal (fracción)
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
    lecho_h_arena_m: float = 0.25           # Espesor capa de arena (m)
    lecho_h_grava_m: float = 0.20           # Espesor capa de grava (m)
    lecho_factor_produccion_lodos: float = 0.10  # kg SST/kg DBO removida (producción UASB)
    lecho_rho_S_min_kgSST_m2_año: float = 60.0   # Rango recomendado carga superficial sólidos
    lecho_rho_S_max_kgSST_m2_año: float = 220.0  # Rango recomendado carga superficial sólidos
    lecho_C_SST_min_kg_m3: float = 15.0      # Rango recomendado concentración sólidos en lodo
    lecho_C_SST_max_kg_m3: float = 30.0      # Rango recomendado concentración sólidos en lodo
    lecho_t_secado_min_d: float = 10.0       # Rango recomendado tiempo secado
    lecho_t_secado_max_d: float = 30.0       # Rango recomendado tiempo secado
    lecho_h_lodo_min_m: float = 0.20         # Rango recomendado espesor aplicación
    lecho_h_lodo_max_m: float = 0.40         # Rango recomendado espesor aplicación
    lecho_relacion_L_A: float = 3.0          # Relación largo/ancho adoptada
    lecho_relacion_L_A_min: float = 2.0      # Rango recomendado relación largo/ancho
    lecho_relacion_L_A_max: float = 4.0      # Rango recomendado relación largo/ancho
    lecho_humedad_final_min_pct: float = 40.0 # Rango típico humedad final lodo seco
    lecho_humedad_final_max_pct: float = 60.0 # Rango típico humedad final lodo seco
    
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
    uasb_temp_moderada_min_C: float = 18.0     # Temperatura mínima para rango moderado (°C)
    uasb_temp_min_operativa_C: float = 15.0    # Temperatura mínima operativa (°C)
    uasb_temp_muy_baja_min_C: float = 10.0     # Temperatura mínima para operación muy baja (°C)
    uasb_trh_min_optimo_h: float = 4.0         # TRH mínimo óptimo (h)
    uasb_trh_min_baja_temp_h: float = 6.0      # TRH mínimo baja temp (h)
    uasb_v_up_min_m_h: float = 0.5             # Velocidad ascendente mínima (m/h)
    uasb_v_up_max_m_h: float = 1.5             # Velocidad ascendente máxima (m/h)
    uasb_margen_operativo_reducido_pct: float = 10.0  # Umbral para reportar margen operativo estrecho (%)
    uasb_inoculo_ssv_min_kg_m3: float = 10.0   # Inóculo mínimo recomendado (kg SSV/m³)
    uasb_inoculo_ssv_max_kg_m3: float = 15.0   # Inóculo máximo recomendado (kg SSV/m³)
    uasb_inoculo_vol_min_pct: float = 15.0     # Volumen mínimo aproximado de inoculación (%)
    uasb_inoculo_vol_max_pct: float = 30.0     # Volumen máximo aproximado de inoculación (%)
    uasb_lodo_granular_diam_min_mm: float = 0.5  # Diámetro mínimo lodo granular (mm)
    uasb_lodo_granular_diam_max_mm: float = 5.0  # Diámetro máximo lodo granular (mm)
    uasb_lodo_granular_vsed_min_m_h: float = 50.0  # Velocidad mínima sedimentación lodo granular (m/h)
    uasb_granulacion_natural_min_meses: float = 2.0  # Tiempo mínimo granulación natural (meses)
    uasb_granulacion_natural_max_meses: float = 6.0  # Tiempo máximo granulación natural (meses)
    
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
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - BIOFILTRO CARGA MECANIZADA HIDRÁULICA (TAF)
    # =============================================================================
    # Biofiltro percolador con carga mecanizada hidráulica (Trickling Filter)
    # Dos rutas de diseño: Ruta A (NRC, sin recirculación) y Ruta B (Germain, con recirculación)
    bf_cmh_DBO_salida_objetivo_mg_L: float = 50.0   # DBO5 objetivo post-biofiltro (mg/L)
    bf_cmh_k_20_m_h: float = 0.068              # Constante cinética a 20°C (m/h) - Germain
    bf_cmh_theta: float = 1.035                 # Coeficiente temperatura DBO5
    bf_cmh_n_germain: float = 0.50              # Exponente modelo Germain (plástico)
    bf_cmh_n_nrc: float = 0.67                  # Exponente para medio de roca (NRC)
    bf_cmh_D_medio_m: float = 3.00              # Profundidad medio filtrante (m)
    bf_cmh_D_medio_min_m: float = 2.0           # Rango recomendado profundidad (m)
    bf_cmh_D_medio_max_m: float = 8.0           # Rango recomendado profundidad (m)
    bf_cmh_R_recirculacion: float = 1.0         # Tasa recirculación Ruta B (0.5-4.0)
    bf_cmh_R_min: float = 0.5                   # Recirculación mínima
    bf_cmh_R_max: float = 4.0                   # Recirculación máxima
    bf_cmh_COS_limite_ruta_A: float = 0.40      # Límite COS para selección Ruta A (kg/m³·d)
    bf_cmh_COS_max_kgDBO_m3_d: float = 1.2      # COS máxima recomendada (Ruta A)
    bf_cmh_CHS_min_m3_m2_h: float = 0.5         # Carga hidráulica superficial mínima
    bf_cmh_CHS_max_m3_m2_h: float = 4.0         # Carga hidráulica superficial máxima
    bf_cmh_CHS_diseño_m3_m2_h: float = 1.5      # CHS de diseño objetivo
    bf_cmh_Cv_kgDBO_m3_d: float = 0.6           # Carga orgánica volumétrica (Ruta A)
    bf_cmh_Cv_ruta_B_kgDBO_m3_d: float = 1.0    # Carga orgánica volumétrica (Ruta B)
    bf_cmh_H_distribucion_m: float = 0.20       # Espacio distribuidor-medio
    bf_cmh_H_underdrain_m: float = 0.50         # Altura underdrain
    bf_cmh_H_bordo_libre_m: float = 0.30        # Bordo libre
    bf_cmh_tipo_medio_default: str = "plástico aleatorio"  # Tipo de medio
    bf_cmh_sup_especifica_m2_m3: float = 100.0  # Superficie específica medio (m²/m³)
    bf_cmh_vacios_pct: float = 94.0             # Índice de vacíos (%)
    bf_cmh_densidad_media_kg_m3: float = 60.0   # Densidad aparente (kg/m³)
    bf_cmh_eficiencia_DBO_max: float = 0.85     # Eficiencia máxima teórica
    bf_cmh_num_brazos: int = 2                  # Número brazos distribuidor
    bf_cmh_num_boquillas_por_brazo: int = 8     # Boquillas por brazo
    bf_cmh_velocidad_boquilla_m_s: float = 2.0  # Velocidad salida boquilla
    bf_cmh_factor_produccion_humus: float = 0.15 # kg SST/kg DBO removida
    bf_cmh_area_ventilacion_pct: float = 1.0    # Área ventilación / Área sup (%)
    bf_cmh_Q_aire_factor: float = 0.3           # Factor caudal aire/agua
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - BIOFILTRO BIOLÓGICO AIREADO (BAF)
    # =============================================================================
    # Biofiltro de lecho sumergido con aireación forzada (Biological Aerated Filter)
    # Post-tratamiento aerobio típico después de UASB
    baf_HLR_diseño_m3_m2_h: float = 3.5         # Tasa hidráulica superficial (m³/m²·h)
    baf_HLR_min_m3_m2_h: float = 2.0            # HLR mínimo recomendado
    baf_HLR_max_m3_m2_h: float = 6.0            # HLR máximo recomendado
    baf_HLR_max_pico_m3_m2_h: float = 10.0      # HLR máximo pico permisible
    baf_EBCT_min_h: float = 0.5                 # Tiempo contacto mínimo (h)
    baf_EBCT_max_h: float = 1.5                 # Tiempo contacto máximo (h)
    baf_OLR_min_kgDBO_m3_d: float = 1.0         # Carga orgánica mínima (kg DBO/m³·d)
    baf_OLR_max_kgDBO_m3_d: float = 6.0         # Carga orgánica máxima (kg DBO/m³·d)
    baf_profundidad_lecho_m: float = 3.0        # Profundidad del lecho de relleno (m)
    baf_profundidad_min_m: float = 2.5          # Profundidad mínima
    baf_profundidad_max_m: float = 4.0          # Profundidad máxima
    baf_relacion_aire_agua: float = 8.0         # Relación aire:agua (Nm³/m³)
    baf_relacion_aire_agua_min: float = 5.0     # Relación mínima
    baf_relacion_aire_agua_max: float = 10.0    # Relación máxima
    baf_SAR_min_m3_m2_h: float = 15.0           # Tasa específica aireación mínima
    baf_SAR_max_m3_m2_h: float = 50.0           # Tasa específica aireación máxima
    baf_sup_especifica_m2_m3: float = 250.0     # Superficie específica relleno (m²/m³)
    baf_porosidad_pct: float = 40.0             # Porosidad del lecho (%)
    baf_altura_plenum_m: float = 0.50           # Altura plenum distribución (m)
    baf_altura_headspace_m: float = 0.50        # Zona libre sobre relleno (m)
    baf_altura_acumulacion_m: float = 0.30      # Zona acumulación retrolavado (m)
    baf_bordo_libre_m: float = 0.30             # Bordo libre
    baf_perdida_carga_max_m: float = 1.5        # Pérdida de carga máxima (m H2O)
    baf_freq_retrolavado_h: float = 24.0        # Frecuencia retrolavado mínima (h)
    baf_freq_retrolavado_max_h: float = 48.0    # Frecuencia retrolavado máxima (h)
    baf_duracion_retrolavado_min: float = 20.0  # Duración retrolavado (min)
    baf_vel_bw_aire_m3_m2_h: float = 75.0       # Velocidad retrolavado aire
    baf_vel_bw_agua_m3_m2_h: float = 20.0       # Velocidad retrolavado agua
    baf_DBO_entrada_mg_L: float = 100.0         # DBO entrada (efluente UASB)
    baf_factor_O2_kgO2_kgDBO: float = 1.35      # Factor demanda oxígeno
    baf_OTE_pct: float = 25.0                   # Eficiencia transferencia oxígeno (%)
    baf_factor_seguridad_aire_min: float = 1.5  # Factor mínimo para "CUMPLE CON HOLGURA"
    baf_densidad_aire_kg_Nm3: float = 1.20      # Densidad aire (kg/Nm³)
    baf_fraccion_O2_aire: float = 0.2314        # Fracción O2 en aire
    baf_relacion_H_D_min: float = 0.8           # Relación H/D mínima recomendada
    baf_relacion_H_D_max: float = 1.5           # Relación H/D máxima recomendada
    baf_fraccion_bw_min_pct: float = 3.0        # Fracción retrolavado mínima (%)
    baf_fraccion_bw_max_pct: float = 7.0        # Fracción retrolavado máxima (%)
    baf_duracion_fase_agua_bw_min: float = 10.0 # Duración fase agua retrolavado (min)
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - REACTOR ANAEROBIO CON PANTALLAS (ABR / RAP)
    # =============================================================================
    # El ABR (Anaerobic Baffled Reactor) o RAP (Reactor Anaerobio con Pantallas)
    # es un reactor anaerobio de múltiples compartimentos sin separador trifásico.
    # Referencia: manual_ABR_RAP.txt
    
    # Parámetros de diseño principales
    abr_TRH_diseno_h: float = 48.0              # Tiempo de retención hidráulico (h) - rango: 24-72 h
    abr_TRH_min_h: float = 24.0                 # TRH mínimo absoluto (h)
    abr_TRH_max_h: float = 72.0                 # TRH máximo recomendado (h)
    abr_num_compartimentos: int = 4             # Número de compartimentos - rango: 2-8, recomendado: 4-6
    abr_num_compartimentos_min: int = 3         # Mínimo compartimentos para separación funcional
    abr_num_compartimentos_recomendado: int = 4 # Mínimo recomendado
    abr_num_compartimentos_max: int = 8         # Máximo práctico
    
    # Velocidad ascensional - parámetro crítico de diseño
    abr_v_up_diseno_m_h: float = 1.0            # Velocidad ascensional diseño (m/h) - rango: 0.2-1.5
    abr_v_up_max_admisible_m_h: float = 2.0     # Velocidad máxima admisible en picos (m/h)
    abr_v_up_min_operativa_m_h: float = 0.2     # Velocidad mínima operativa (m/h)
    
    # Geometría del reactor
    abr_profundidad_util_m: float = 2.0         # Profundidad útil líquido (m) - rango: 1.5-3.0
    abr_profundidad_min_m: float = 1.5          # Profundidad mínima (m)
    abr_profundidad_max_m: float = 3.0          # Profundidad máxima (m)
    abr_zona_lodos_m: float = 0.30              # Zona acumulación lodos (m) - rango: 0.2-0.5
    abr_bordo_libre_m: float = 0.30             # Bordo libre (m)
    
    # Criterios geométricos
    abr_relacion_Lcomp_W_min: float = 0.5       # Relación largo/ancho compartimento mínima
    abr_relacion_Lcomp_W_max: float = 2.0       # Relación largo/ancho compartimento máxima
    abr_COV_referencial_min: float = 0.5        # Carga orgánica volumétrica mínima (kg DBO/m³·d)
    abr_COV_referencial_max: float = 5.0        # Carga orgánica volumétrica máxima (kg DBO/m³·d)
    
    # Calidad del afluente (valores por defecto para diseño)
    abr_DBO_entrada_mg_L: float = 200.0         # DBO5 entrada (mg/L) - típico doméstico
    abr_DQO_entrada_mg_L: float = 400.0         # DQO entrada (mg/L) - relación DQO/DBO = 2.0
    abr_SST_entrada_mg_L: float = 200.0         # SST entrada (mg/L)
    
    # Temperatura de diseño
    abr_temp_min_diseno_C: float = 18.0         # Temperatura mínima diseño (°C)
    abr_temp_optima_min_C: float = 20.0         # Temperatura óptima mínima (°C)

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
                f"se recomienda monitorear periodicamente. Si la temperatura descendiera por debajo de {cfg.uasb_temp_moderada_min_C:.0f}°C, "
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
    elif cfg.uasb_temp_moderada_min_C <= T_celsius < cfg.uasb_temp_optimina_C:
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
            "factor_temp_texto": f"moderada ({cfg.uasb_temp_moderada_min_C:.0f}-{cfg.uasb_temp_optimina_C:.0f}°C)",
            "rangos_recomendados": {
                "cv": f"{cfg.uasb_Cv_moderado_min:.1f}--{cfg.uasb_Cv_moderado_max:.1f}".replace(".", ","),
                "vup": "0,4--1,2",
                "hrt": f"{cfg.uasb_HRT_moderado_min_h:.0f}--{cfg.uasb_HRT_moderado_max_h:.0f}",
                "eta": "50--65"
            }
        }
    elif cfg.uasb_temp_min_operativa_C <= T_celsius < cfg.uasb_temp_moderada_min_C:
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
            "factor_temp_texto": f"baja ({cfg.uasb_temp_min_operativa_C:.0f}-{cfg.uasb_temp_moderada_min_C:.0f}°C)",
            "rangos_recomendados": {
                "cv": f"{cfg.uasb_Cv_bajo_min:.1f}--{cfg.uasb_Cv_bajo_max:.1f}".replace(".", ","),
                "vup": "0,3--1,0",
                "hrt": f"{cfg.uasb_HRT_bajo_min_h:.0f}--{cfg.uasb_HRT_bajo_max_h:.0f}",
                "eta": "40--55"
            }
        }
    elif cfg.uasb_temp_muy_baja_min_C <= T_celsius < cfg.uasb_temp_min_operativa_C:
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
            "factor_temp_texto": f"muy baja ({cfg.uasb_temp_muy_baja_min_C:.0f}-{cfg.uasb_temp_min_operativa_C:.0f}°C) - se recomienda aislamiento térmico",
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
                f"NO RECOMENDABLE: Temperatura por debajo de {cfg.uasb_temp_muy_baja_min_C:.0f}°C. El proceso anaerobio es inviable sin calentar la biomasa. "
                "Se requiere calefacción del reactor para mantenerlo en rango operativo o cambio obligatorio a tecnología aerobia activada. "
                "Los ajustes automáticos aplicados (carga reducida a 30%, HRT aumentado 150%) NO son suficientes para garantizar tratamiento adecuado."
            ),
            "cv_kgDQO_m3_d": Cv_base * 0.30,
            "trh_h": HRT_base * 2.5,
            "v_up_m_h": cfg.uasb_v_up_m_h * 0.375,
            "eficiencia_dbo": cfg.uasb_eta_DBO * 0.60,
            "eficiencia_dqo": cfg.uasb_eta_DQO * 0.60,
            "factor_temp_texto": f"crítica (< {cfg.uasb_temp_muy_baja_min_C:.0f}°C) - requiere calefacción o cambio de tecnología",
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
    ancho_minimo_constructivo_m = 0.60
    ancho_criterio_tabla_m = 0.30
    hL_criterio_m = 0.15
    ancho_layout = round(max(b_canal * 2 + 0.30, ancho_minimo_constructivo_m), 2)
    
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
    perdida_aceptable = hL_max < hL_criterio_m
    
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

    if velocidad_segura:
        estado_velocidad = "OPTIMO"
        texto_velocidad_verificacion = (
            f"es menor que el limite recomendado de {v_max_limite_advertencia:.1f}~m/s "
            f"para operacion segura"
        )
    elif velocidad_no_destructiva:
        estado_velocidad = "ACEPTABLE"
        texto_velocidad_verificacion = (
            f"supera el limite recomendado de {v_max_limite_advertencia:.1f}~m/s pero "
            f"se mantiene por debajo del limite destructivo de "
            f"{v_max_limite_destructivo:.1f}~m/s (operacion aceptable con monitoreo)"
        )
    else:
        estado_velocidad = "NO ADMISIBLE"
        texto_velocidad_verificacion = (
            f"excede el limite destructivo de {v_max_limite_destructivo:.1f}~m/s y "
            f"requiere mayor ancho de canal"
        )

    if ajuste_ancho_rejillas:
        texto_velocidad_verificacion = (
            f"se aumento el ancho del canal en {incremento_ancho_cm:.0f}~cm "
            f"(de {ancho_original:.2f}~m a {ancho_layout:.2f}~m) "
            f"para mantener la velocidad maxima por debajo del limite destructivo "
            f"de {v_max_limite_destructivo:.1f}~m/s"
        )

    estado_velocidad_norma = "CUMPLE" if velocidad_no_destructiva else "NO CUMPLE"
    estado_perdida = "CUMPLE" if perdida_aceptable else "NO CUMPLE"
    texto_perdida_verificacion = (
        f"es menor que el umbral de {hL_criterio_m*100:.0f}~cm para limpieza manual aceptable"
        if perdida_aceptable
        else f"excede el umbral de {hL_criterio_m*100:.0f}~cm y requiere limpieza mecanica"
    )

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
        "velocidad_no_destructiva": velocidad_no_destructiva,
        "perdida_aceptable": perdida_aceptable,
        "ancho_minimo_constructivo_m": ancho_minimo_constructivo_m,
        "ancho_criterio_tabla_m": ancho_criterio_tabla_m,
        "hL_criterio_m": hL_criterio_m,
        "estado_velocidad_diseno": "Cumple" if Q.rejillas_v_canal_min_m_s <= v_canal_m_s <= Q.rejillas_v_canal_max_m_s else "No cumple",
        "estado_perdida_qmax": "Cumple" if perdida_aceptable else "No cumple",
        "estado_ancho_constructivo": "Cumple" if ancho_layout >= ancho_criterio_tabla_m else "No cumple",
        "estado_velocidad": estado_velocidad,
        "estado_velocidad_norma": estado_velocidad_norma,
        "estado_perdida": estado_perdida,
        "texto_velocidad_verificacion": texto_velocidad_verificacion,
        "texto_perdida_verificacion": texto_perdida_verificacion,
        "verif_vel_texto": verif_vel_texto,
        "verif_hl_texto": verif_hl_texto,
        "ajuste_ancho_rejillas": ajuste_ancho_rejillas,
        "ancho_original_m": round(ancho_original, 2),
        "incremento_ancho_cm": incremento_ancho_cm,
        "largo_layout_m": largo_canal,
        "fuente": f"{ref1} (pp. 470-488); {ref2} (pp. 185-202)",
        # Subproductos - estructura normalizada
        "subproductos": {
            "lodos": [],
            "retenciones": [],
            "transferencias": [],
            "biogas": [],
            "residuos_gruesos": [
                {
                    "origen": "Rejillas",
                    "tipo": "solidos gruesos retenidos",
                    "cantidad": None,
                    "unidad": None,
                    "kg_d": None,
                    "m3_d": None,
                    "destino": "disposicion_externa",
                    "apto_lecho_directo": False,
                    "nota": "Las rejillas retienen solidos gruesos; el dimensionamiento "
                            "actual no estima masa o volumen diario de residuos de cribado."
                }
            ],
            "arenas": []
        },
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
    h_almacenamiento_arena_min_m = Q.desarenador_h_almacenamiento_arena_min_m
    h_almacenamiento_arena_max_m = Q.desarenador_h_almacenamiento_arena_max_m
    h_almacenamiento_arena_m = Q.desarenador_h_almacenamiento_arena_m
    bordo_libre_m = Q.bordo_libre_desarenador_m
    H_total_m = H_util + h_almacenamiento_arena_m + bordo_libre_m

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
    scour_seguro = v_h_max <= v_h_max_limite_destructivo
    incremento_ancho_des_cm = round((b_canal - b_canal_original) * 100)
    
    # Texto automático de verificación (evita errores si cambian los datos)
    if scour_seguro:
        verif_scour_texto = f"es menor que el limite de resuspension con factor de seguridad ({v_h_max_limite_destructivo:.3f}~m/s), por lo que no se produce resuspension de la arena depositada"
    else:
        verif_scour_texto = f"EXCEDE el limite de resuspension con factor de seguridad ({v_h_max_limite_destructivo:.3f}~m/s), por lo que se produciria resuspension de arena -- AJUSTAR DIMENSIONES"

    estado_resuspension = "SEGURIDAD" if scour_seguro else "RIESGO"
    estado_resuspension_norma = "CUMPLE" if scour_seguro else "NO CUMPLE"
    factor_seguridad_scour_pct = round(Q.desarenador_factor_seguridad_scour * 100)
    
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
        "h_almacenamiento_arena_min_m": h_almacenamiento_arena_min_m,
        "h_almacenamiento_arena_max_m": h_almacenamiento_arena_max_m,
        "h_almacenamiento_arena_m": h_almacenamiento_arena_m,
        "bordo_libre_m": bordo_libre_m,
        "H_total_m": round(H_total_m, 2),
        "b_teorico_m": round(b_teorico, 3),
        "b_min_constructivo_m": b_min_m,
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
        "beta_min": Q.desarenador_beta_min,
        "beta_max": Q.desarenador_beta_max,
        "f_darcy": f_darcy,                   # Factor de fricción Darcy-Weisbach
        "f_darcy_min": Q.desarenador_f_darcy_min,
        "f_darcy_max": Q.desarenador_f_darcy_max,
        "v_c_scour_m_s": round(v_c_scour, 3), # Velocidad crítica resuspensión
        "factor_seguridad_scour": Q.desarenador_factor_seguridad_scour,
        "factor_seguridad_scour_pct": factor_seguridad_scour_pct,
        "v_h_max_limite_scour_m_s": round(v_h_max_limite_destructivo, 3),
        # Verificación caudal máximo horario
        "factor_pico": factor_pico,           # 2.5 (Qmax/Qmedio)
        "Q_max_L_s": Q_max_L_s,               # Caudal máximo horario (L/s)
        "v_h_max_m_s": round(v_h_max, 3),     # Velocidad a Qmax
        "t_r_max_s": round(t_r_max, 1),       # Tiempo retención a Qmax
        "scour_seguro": scour_seguro,         # v_h_max < v_c_scour?
        "estado_resuspension": estado_resuspension,
        "estado_resuspension_norma": estado_resuspension_norma,
        "verif_scour_texto": verif_scour_texto,  # Texto automático de verificación
        "ajuste_ancho_desarenador": ajuste_ancho_desarenador,
        "b_canal_original_m": round(b_canal_original, 3),
        "incremento_ancho_cm": incremento_ancho_des_cm,
        # Layout
        "largo_layout_m": round(L_diseno, 1),
        "ancho_layout_m": round(b_canal + bordo_libre_m, 2),
        # Nota explicativa
        "nota_diseño": f"Para Q={Q_L_s:.1f} L/s, la longitud se reduce de {L_teorica_metcatlf:.1f} m (teórica) a {L_diseno:.1f} m por criterio práctico latinoamericano",
        "fuente": (f"{ref1} (pp. 488-510, Tabla 9-6); {ref2} (pp. 202-218); {ref3}; {ref4}"),
        # Subproductos - estructura normalizada
        "subproductos": {
            "lodos": [],
            "retenciones": [],
            "transferencias": [],
            "biogas": [],
            "residuos_gruesos": [],
            "arenas": [
                {
                    "origen": "Desarenador",
                    "tipo": "arena sedimentada / material inerte",
                    "cantidad": None,
                    "unidad": None,
                    "kg_d": None,
                    "m3_d": None,
                    "destino": "disposicion_externa",
                    "apto_lecho_directo": False,
                    "nota": "El desarenador retiene arenas y material inerte; el "
                            "dimensionamiento actual no estima masa o volumen diario "
                            "de arenas removidas."
                }
            ]
        },
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

    # [Ec. 4b] Volumen del reactor - CRITERIO BIOLÓGICO (carga orgánica volumétrica)
    V_r_biol_m3 = Q_m3_d * DQO_kg_m3 / Cv_kgDQO_m3_d   # m^3 (volumen teórico biológico)
    V_r_m3 = V_r_biol_m3  # Inicialmente el volumen adoptado es el biológico

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

    if v_up_max_m_h <= v_up_max_limite_recomendado:
        estado_verificacion_texto = "garantiza la estabilidad del manto de lodos bajo todas las condiciones operativas esperadas."
    elif v_up_max_m_h <= v_up_max_limite_destructivo:
        estado_verificacion_texto = "requiere monitoreo durante eventos de pico de caudal."
    else:
        estado_verificacion_texto = "no es admisible y debe redimensionarse."
    
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

    if TRH_sed_cumple:
        TRH_sed_texto = (
            f"El tiempo de retencion de {TRH_sed_medio_h:.2f} h cumple con el minimo "
            f"de {Q.uasb_TRH_sed_medio_min_h:.1f} h recomendado por Chernicharo "
            "para permitir la adecuada separacion gas-liquido-solido."
        )
    else:
        TRH_sed_texto = (
            f"El tiempo de retencion de {TRH_sed_medio_h:.2f} h no cumple con el minimo "
            f"de {Q.uasb_TRH_sed_medio_min_h:.1f} h recomendado por Chernicharo y "
            "requiere ajuste de las dimensiones del sedimentador."
        )

    estado_SOR_max = "Cumple" if SOR_max_cumple else "No cumple"
    if SOR_medio_cumple:
        estado_SOR_medio = "Cumple (conservador)"
    elif SOR_medio_m_h < Q.uasb_SOR_medio_min_m_h:
        estado_SOR_medio = "Bajo (aceptable)"
    else:
        estado_SOR_medio = "No cumple"
    estado_TRH_sed = "Cumple" if TRH_sed_cumple else "No cumple"

    if SOR_max_cumple and SOR_medio_cumple and TRH_sed_cumple:
        verif_sed_final = "La verificacion demuestra que el compartimiento de sedimentacion disenado cumple satisfactoriamente con todos los criterios tecnicos establecidos en la literatura especializada para reactores UASB."
    elif SOR_max_cumple and not SOR_medio_cumple and TRH_sed_cumple:
        verif_sed_final = "La verificacion muestra que el SOR medio esta por debajo del rango optimo pero dentro de valores aceptables conservadores; el diseno cumple con SOR maximo y TRH."
    else:
        partes = []
        if not SOR_max_cumple:
            partes.append("SOR maximo excede el limite.")
        if not SOR_medio_cumple:
            partes.append("SOR medio fuera de rango.")
        if not TRH_sed_cumple:
            partes.append("TRH sedimentador insuficiente.")
        verif_sed_final = (
            "La verificacion indica que el compartimiento de sedimentacion requiere revision: "
            + " ".join(partes)
            + " Se recomienda ajustar las dimensiones del diseno."
        )
    
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
    simbolo_abertura_max = r"\leq" if v_abertura_max_cumple else ">"
    estado_aberturas = "Cumple" if v_abertura_max_cumple else "No cumple"
    if v_abertura_max_cumple:
        verif_aberturas_gls_texto = (
            f"La velocidad máxima calculada en las aberturas GLS es {v_abertura_max_calculada_m_h:.2f} m/h, "
            f"menor o igual al límite de {Q.uasb_v_abertura_max_m_h:.1f} m/h recomendado para caudal máximo. "
            "Esta condición indica que el área libre adoptada permite el paso del líquido clarificado hacia "
            "la cámara de sedimentación sin imponer velocidades que favorezcan el arrastre de sólidos del manto "
            "de lodos. En términos operativos, las aberturas funcionan como zona de transición hidráulica entre "
            "la digestión y la sedimentación; por ello se recomienda mantener limpias las ranuras del GLS y "
            "verificar su condición durante inspecciones de rutina."
        )
    else:
        verif_aberturas_gls_texto = (
            f"La velocidad máxima calculada en las aberturas GLS es {v_abertura_max_calculada_m_h:.2f} m/h, "
            f"mayor que el límite de {Q.uasb_v_abertura_max_m_h:.1f} m/h recomendado para caudal máximo. "
            "Esta condición puede inducir arrastre de sólidos hacia la cámara de sedimentación, por lo que "
            "se recomienda aumentar el área libre de aberturas o revisar la geometría del separador GLS."
        )
    margen_SOR_max_pct = ((Q.uasb_SOR_max_limite_m_h - SOR_max_m_h) / Q.uasb_SOR_max_limite_m_h) * 100
    margen_abertura_pct = ((Q.uasb_v_abertura_max_m_h - v_abertura_max_calculada_m_h) / Q.uasb_v_abertura_max_m_h) * 100
    margen_minimo_operativo_pct = min(margen_SOR_max_pct, margen_abertura_pct)
    margen_operativo_estado = (
        "reducido"
        if margen_minimo_operativo_pct <= Q.uasb_margen_operativo_reducido_pct
        else "holgado"
    )
    if SOR_max_cumple and v_abertura_max_cumple:
        nota_margenes_operativos = (
            f"Los parámetros críticos de control hidráulico del reactor se mantienen dentro de los límites "
            f"recomendados por Chernicharo \\cite{{chernicharo2007}}. El SOR máximo es "
            f"{SOR_max_m_h:.2f} m/h frente al límite de {Q.uasb_SOR_max_limite_m_h:.1f} m/h, con "
            f"un margen de {margen_SOR_max_pct:.1f}%; este criterio controla el riesgo de arrastre de "
            f"sólidos en la cámara de sedimentación durante caudales pico. La velocidad máxima en aberturas "
            f"GLS es {v_abertura_max_calculada_m_h:.2f} m/h frente al límite de "
            f"{Q.uasb_v_abertura_max_m_h:.1f} m/h, con un margen de {margen_abertura_pct:.1f}%; este "
            f"criterio controla el paso del líquido clarificado hacia el compartimiento de sedimentación sin "
            f"inducir arrastre de lodos. En conjunto, el margen operativo se clasifica como "
            f"{margen_operativo_estado}. Por ello, aunque la unidad cumple, se recomienda verificar SOR y "
            f"velocidad en aberturas durante la puesta en marcha y monitorear periódicamente SST/turbidez del "
            f"efluente como indicador de posible arrastre."
        )
    else:
        partes_margenes = []
        if not SOR_max_cumple:
            partes_margenes.append("SOR máximo excede el límite establecido")
        if not v_abertura_max_cumple:
            partes_margenes.append("velocidad en aberturas GLS excede el límite establecido")
        nota_margenes_operativos = (
            "La revisión de márgenes operativos indica que "
            + " y ".join(partes_margenes)
            + "; se recomienda revisar el dimensionamiento antes de aprobar la unidad."
        )
    
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

    estado_tubo = "Adecuado" if velocidad_tubo_m_s <= Q.uasb_v_tubo_max_m_s else "Revisar"
    estado_boca = "Cumple" if v_boca_cumple else "No cumple"
    if v_boca_cumple:
        texto_boca = "cumple con el rango recomendado por Lettinga y Hulshoff Pol para inyeccion adecuada en el lecho de lodo."
    else:
        texto_boca = "esta fuera del rango recomendado. Se recomienda revisar el diametro de las bocas de salida."

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
        "V_r_biol_m3": round(V_r_biol_m3, 1),  # Volumen por criterio biológico (carga orgánica)
        "V_r_m3": round(V_r_m3, 1),  # Volumen final adoptado (puede ajustarse por criterio hidráulico)
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
        "estado_SOR_max": estado_SOR_max,
        "estado_SOR_medio": estado_SOR_medio,
        "TRH_sed_medio_h": round(TRH_sed_medio_h, 2),
        "TRH_sed_max_h": round(TRH_sed_max_h, 2),
        "TRH_sed_cumple": TRH_sed_cumple,
        "estado_TRH_sed": estado_TRH_sed,
        "TRH_sed_texto": TRH_sed_texto,
        "verif_sed_final": verif_sed_final,
        # Aberturas GLS (Paso 9 manual)
        "A_aberturas_min_m2": round(A_aberturas_min_m2, 2),
        "v_abertura_adoptada_m_h": round(v_abertura_adoptada_m_h, 2),
        "v_abertura_max_calculada_m_h": round(v_abertura_max_calculada_m_h, 2),
        "v_abertura_max_cumple": v_abertura_max_cumple,
        "simbolo_abertura_max": simbolo_abertura_max,
        "estado_aberturas": estado_aberturas,
        "verif_aberturas_gls_texto": verif_aberturas_gls_texto,
        "nota_margenes_operativos": nota_margenes_operativos,
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
        "estado_tubo": estado_tubo,
        "diam_boca_salida_mm": round(diam_boca_salida_mm, 0),
        "velocidad_boca_m_s": round(velocidad_boca_m_s, 2),
        "v_boca_min_m_s": Q.uasb_v_boca_min_m_s,
        "v_boca_max_m_s": Q.uasb_v_boca_max_m_s,
        "v_boca_cumple": v_boca_cumple,
        "estado_boca": estado_boca,
        "texto_boca": texto_boca,
        # Producción de subproductos
        "factor_biogas_ch4": factor_biogas,   # Factor usado (m³ CH4 / kg DQO removida)
        "DQO_removida_kg_d": round(DQO_removida_kg_d, 2),
        "biogaz_m3_d": round(biogaz_m3_d, 1),
        "lodos_kg_SSV_d": round(lodos_kg_SSV_d, 2),
        # Parámetros de calidad y estabilidad del proceso
        "pH_optimo_min": Q.uasb_pH_optimo_min,
        "pH_optimo_max": Q.uasb_pH_optimo_max,
        "alcalinidad_min_mg_L": Q.uasb_alcalinidad_min_mg_L,
        "biogas_CH4_pct": Q.uasb_biogas_CH4_pct,
        "biogas_CO2_pct": Q.uasb_biogas_CO2_pct,
        "biogas_H2S_max_ppm": Q.uasb_biogas_H2S_max_ppm,
        "lodo_estabilizado": Q.uasb_lodo_estabilizado,
        # Subproductos - estructura normalizada
        "subproductos": {
            "lodos": [
                {
                    "origen": "UASB",
                    "tipo": "lodo anaerobio",
                    "kg_d": round(lodos_kg_SSV_d, 2),
                    "base_solidos": "SSV",
                    "kg_SSV_d": round(lodos_kg_SSV_d, 2),
                    "kg_SST_d": None,  # Pendiente: requiere factor de conversión aprobado
                    "m3_d": None,  # Pendiente: requiere concentración y conversión a SST
                    "concentracion_kg_m3": None,  # Pendiente: definir para lecho
                    "destino": "lecho_secado",
                    "nota": "Produccion estimada en base SSV (solidos suspendidos volatiles); "
                            "kg_SST_d = None hasta aprobar factor de conversion SSV->SST. "
                            "Ver config: fraccion_SSV_en_SST_lodo_uasb (ej: 0.80 = SSV es 80pct de SST)."
                }
            ],
            "transferencias": [],  # UASB no transfiere carga a otra unidad
            "biogas": [
                {
                    "origen": "UASB",
                    "tipo": "metano",
                    "m3_d": round(biogaz_m3_d, 1),
                    "factor_usado": factor_biogas,
                    "destino": "manejo_por_definir",  # Honesto: no hay diseño de aprovechamiento aún
                    "nota": "Biogás producido en reactor UASB. "
                            "Destino real depende de evaluación de viabilidad energética."
                }
            ],
            "residuos_gruesos": [],
            "arenas": []
        },
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
        "estado_verificacion_texto": estado_verificacion_texto,
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

    # ========================================================================
    # LOOP INTEGRAL DE AUTO-AJUSTE DEL FILTRO PERCOLADOR
    # Verifica y ajusta automáticamente todos los criterios de diseño
    # ========================================================================
    
    factor_pico = Q.factor_pico_Qmax
    Q_max_m3_d = Q_m3_d * factor_pico
    Q_max_m3_h = Q_max_m3_d / 24
    Q_A_limite_m3_m2_h = Q.fp_Q_A_limite_m3_m2_h
    Cv_minima = Q.fp_Cv_minima_kgDBO_m3_d
    
    iteracion = 0
    max_iteraciones = 100
    ajuste_realizado = True
    
    while iteracion < max_iteraciones and ajuste_realizado:
        iteracion += 1
        ajuste_realizado = False
        
        # Recalcular parámetros base
        A_sup_m2 = V_medio_m3 / D_m
        Q_ap_m3_h = Q_m3_h * (1 + R)
        Q_A_real = Q_ap_m3_h / A_sup_m2
        
        # VERIFICACIÓN 1: qA_real >= fp_qA_real_min_m3_m2_h (mojado mínimo del medio)
        if Q_A_real < Q.fp_qA_real_min_m3_m2_h:
            # Despeje de Q_A_real = Q_m3_h * (1 + R) / A_sup_m2
            # R >= A_sup_m2 / Q_m3_h - 1
            R_nuevo = math.ceil((A_sup_m2 / Q_m3_h) - 1.0)
            R = max(R_nuevo, R + Q.fp_incremento_recirculacion, Q.fp_R_min)
            ajuste_realizado = True
            continue
        
        # VERIFICACIÓN 2: Se_Germain <= objetivo (eficiencia requerida)
        relacion_Se_S0 = math.exp(-k_T_m_h * D_m / (Q_A_real ** n))
        Se_calculado_mg_L = DBO_entrada_mg_L * relacion_Se_S0
        
        if Se_calculado_mg_L > DBO_salida_mg_L:
            # Estrategia: reducir Cv para aumentar volumen y mejorar eficiencia
            # (mayor V = mayor área = menor Q_A = mejor eficiencia)
            if Cv_kgDBO_m3_d > Cv_minima * 1.05:
                Cv_kgDBO_m3_d = max(Cv_kgDBO_m3_d * 0.95, Cv_minima)
                V_medio_m3 = Q_m3_d * DBO_kg_m3 / Cv_kgDBO_m3_d
                ajuste_realizado = True
                continue
            # Si no se puede mejorar más, salir del loop (se reportará al final)
        
        # VERIFICACIÓN 3: qA_max <= limite (evitar arrastre)
        Q_A_max_m3_m2_h = Q_max_m3_h * (1 + R) / A_sup_m2
        if Q_A_max_m3_m2_h > Q_A_limite_m3_m2_h:
            # Estrategia: aumentar área reduciendo Cv
            if Cv_kgDBO_m3_d > Cv_minima * 1.05:
                Cv_kgDBO_m3_d = max(Cv_kgDBO_m3_d * 0.95, Cv_minima)
                V_medio_m3 = Q_m3_d * DBO_kg_m3 / Cv_kgDBO_m3_d
                ajuste_realizado = True
                continue
            else:
                # Forzar área mínima necesaria
                A_sup_m2 = (Q_max_m3_h * (1 + R)) / Q_A_limite_m3_m2_h
                V_medio_m3 = A_sup_m2 * D_m
                break
        
        # VERIFICACIÓN 4: qA_min >= umbral humectación biopelícula
        Q_min_m3_h = Q_m3_h * Q.fp_factor_caudal_min_nocturno
        qA_min_m3_m2_h = Q_min_m3_h * (1 + R) / A_sup_m2
        if qA_min_m3_m2_h < Q.fp_qA_min_humectacion_m3_m2_h:
            R = min(R + Q.fp_incremento_recirculacion, Q.fp_R_max)
            ajuste_realizado = True
            continue
        
        # Si llegamos aquí, todas las verificaciones pasaron
        break
    
    # Recálculo final con valores ajustados
    A_sup_m2 = V_medio_m3 / D_m
    Q_ap_m3_h = Q_m3_h * (1 + R)
    Q_A_real = Q_ap_m3_h / A_sup_m2
    D_filtro_m = math.sqrt(4 * A_sup_m2 / math.pi)
    
    # Eficiencia Germain final
    relacion_Se_S0 = math.exp(-k_T_m_h * D_m / (Q_A_real ** n))
    Se_calculado_mg_L = DBO_entrada_mg_L * relacion_Se_S0
    DBO_removida_kg_d = Q_m3_d * DBO_kg_m3 * (1 - relacion_Se_S0)
    
    # Verificaciones finales
    Q_A_max_m3_m2_h = Q_max_m3_h * (1 + R) / A_sup_m2
    Q_min_m3_h = Q_m3_h * Q.fp_factor_caudal_min_nocturno
    qA_min_m3_m2_h = Q_min_m3_h * (1 + R) / A_sup_m2
    
    # Reportar estado de cumplimiento (una sola vez al final)
    se_cumple_objetivo = Se_calculado_mg_L <= DBO_salida_mg_L
    if not se_cumple_objetivo:
        print(f"[ADVERTENCIA] Filtro Percolador: Se_Germain = {Se_calculado_mg_L:.1f} mg/L "
              f"excede el objetivo de {DBO_salida_mg_L:.1f} mg/L. "
              f"Diseño no cumple eficiencia requerida.")
    
    # =================================================================
    # PASO 4 - GEOMETRÍA COMPLETA DEL FILTRO (Desglose de alturas)
    # =================================================================
    H_distribucion = Q.fp_H_distribucion_m    # Espacio distribuidor-medio
    H_underdrain = Q.fp_H_underdrain_m        # Sistema drenaje inferior
    H_bordo_fp = Q.fp_H_bordo_libre_fp_m      # Bordo libre
    
    # Altura total verificada
    H_total_calculada = H_distribucion + D_m + H_underdrain + H_bordo_fp
    
    # =================================================================
    # PASO 5 - SISTEMA DE RECIRCULACIÓN (valores finales post-ajuste)
    # Verificación de qA a caudal mínimo (factor desde configuración)
    # =================================================================
    # Q_min_m3_h y qA_min_m3_m2_h ya calculados en loop de auto-ajuste
    
    qA_min_umbral = Q.fp_qA_min_humectacion_m3_m2_h
    if qA_min_m3_m2_h < qA_min_umbral:
        recirculacion_adicional = True
        qA_min_texto = f"$q_{{A,min}} = {qA_min_m3_m2_h:.2f}$ m³/m²·h $< {qA_min_umbral:.1f}$ (riesgo de sequedad). Se recomienda aumentar $R$ o implementar control de nivel."
    else:
        recirculacion_adicional = False
        qA_min_texto = f"$q_{{A,min}} = {qA_min_m3_m2_h:.2f}$ m³/m²·h $\\geq {qA_min_umbral:.1f}$ (biopelícula húmeda garantizada)."
    
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
    
    # Verificación rotación hidráulica (necesita caudal mínimo por brazo para rotar)
    rotacion_hidraulica = Q_por_brazo_m3_h >= Q.fp_Q_por_brazo_min_rotacion_m3_h
    
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
    # Caudal de diseño (regla del factor de capacidad: diseñar para 1/factor)
    Q_underdrain_diseno_m3_h = Q_ap_m3_h / Q.fp_factor_capacidad_underdrain
    
    # Canal central - verificación con Manning
    ancho_canal = Q.fp_ancho_canal_central_m
    altura_canal = Q.fp_altura_canal_central_m
    pendiente_canal = Q.fp_pendiente_underdrain_pct / 100
    n_manning = Q.fp_n_manning_underdrain
    
    A_canal = ancho_canal * altura_canal
    P_canal = ancho_canal + 2 * altura_canal
    R_hidraulico = A_canal / P_canal
    
    Q_canal_m3_s = (1/n_manning) * A_canal * (R_hidraulico**(2/3)) * (pendiente_canal**0.5)
    Q_canal_m3_h = Q_canal_m3_s * 3600
    
    # Verificación: canal debe fluir < llenado máximo de su capacidad
    llenado_canal = Q_ap_m3_h / Q_canal_m3_h
    canal_ok = llenado_canal <= Q.fp_llenado_max_underdrain
    
    # =================================================================
    # PASO 8 - VENTILACIÓN NATURAL
    # =================================================================
    # Área de ventilación requerida (>= 1% del área superficial)
    area_ventilacion_requerida_m2 = A_sup_m2 * (Q.fp_area_ventilacion_pct / 100)
    
    # Caudal de aire necesario
    Q_aire_min_m3_h = Q_m3_h * Q.fp_Q_aire_min_factor
    Q_aire_opt_m3_h = Q_m3_h * Q.fp_Q_aire_factor  # Óptimo 0.3 m³/m³
    
    # Número de aperturas (dimensiones desde configuración)
    area_apertura_m2 = Q.fp_apertura_ventilacion_ancho_m * Q.fp_apertura_ventilacion_alto_m
    num_aperturas_min = math.ceil(area_ventilacion_requerida_m2 / area_apertura_m2)
    
    # Perímetro para distribución
    perimetro_m = math.pi * D_filtro_m
    espaciado_aperturas_m = perimetro_m / num_aperturas_min
    
    # =================================================================
    # PASO 10 - ESPECIFICACIONES DEL MEDIO PLÁSTICO
    # =================================================================
    # Carga sobre el medio
    carga_peso_medio_kg_m2 = (Q.fp_densidad_media_kg_m3 + Q.fp_carga_agua_sobre_medio_kg_m3 + Q.fp_carga_biopelicula_sobre_medio_kg_m3) * D_m
    
    # Verificación resistencia a compresión
    if D_m <= Q.fp_resistencia_umbral_profundidad_m:
        resistencia_minima_requerida = Q.fp_resistencia_min_baja_kg_m2
    else:
        resistencia_minima_requerida = Q.fp_resistencia_min_alta_kg_m2
    
    resistencia_ok = carga_peso_medio_kg_m2 <= resistencia_minima_requerida

    # Textos y estados de verificacion para render LaTeX.
    # La capa documental solo debe concatenar estos campos, no decidir cumplimiento.
    estado_germain = "Cumple" if se_cumple_objetivo else "No cumple"
    if se_cumple_objetivo:
        texto_germain = (
            f"El valor calculado de $S_e = {Se_calculado_mg_L:.1f}$ mg/L cumple con el "
            f"objetivo de diseño interno de ${DBO_salida_mg_L:.0f}$ mg/L. El diseño cumple "
            "satisfactoriamente con el objetivo establecido para el filtro percolador."
        )
    else:
        texto_germain = (
            f"El valor calculado de $S_e = {Se_calculado_mg_L:.1f}$ mg/L excede el "
            f"objetivo de diseño interno de ${DBO_salida_mg_L:.0f}$ mg/L. Se debe verificar "
            "el desempeño del tren completo o ajustar el diseño del filtro antes de adoptar "
            "el valor como cumplimiento de la etapa."
        )

    estado_rotacion = "Cumple" if rotacion_hidraulica else "Requiere motor auxiliar"
    if rotacion_hidraulica:
        texto_rotacion = (
            f"Dado que el caudal por brazo ({Q_por_brazo_m3_h:.1f} m³/h) supera el umbral "
            f"mínimo de {Q.fp_Q_por_brazo_min_rotacion_m3_h:.1f} m³/h, la rotación hidráulica "
            "está garantizada sin necesidad de motor auxiliar. La fuerza de reacción generada "
            "por el agua al salir por las boquillas proporciona suficiente par de giro para "
            "mantener la rotación continua del distribuidor durante la operación normal."
        )
    else:
        texto_rotacion = (
            f"Dado que el caudal por brazo ({Q_por_brazo_m3_h:.1f} m³/h) es inferior al umbral "
            f"mínimo de {Q.fp_Q_por_brazo_min_rotacion_m3_h:.1f} m³/h, se recomienda instalar "
            f"un motor eléctrico auxiliar de {Q.fp_motor_aux_min_kW:.1f}--{Q.fp_motor_aux_max_kW:.1f} kW "
            "para garantizar la rotación del distribuidor durante periodos de bajo caudal, "
            "evitando así la distribución no uniforme del agua sobre el medio filtrante."
        )

    boquillas_ok = Q.fp_velocidad_boquilla_min_m_s <= v_boquilla_m_s <= Q.fp_velocidad_boquilla_max_m_s
    estado_boquillas = "Cumple" if boquillas_ok else "No cumple"
    if boquillas_ok:
        texto_boquillas = (
            "cumple con el rango establecido, garantizando el funcionamiento hidráulico "
            "adecuado del sistema de distribución"
        )
    else:
        texto_boquillas = (
            "se encuentra fuera del rango recomendado, por lo que se sugiere revisar el "
            "diámetro de las boquillas"
        )

    estado_underdrain = "Cumple" if canal_ok else "No cumple"
    if canal_ok:
        texto_underdrain = (
            f"El llenado calculado ({llenado_canal * 100:.1f}%) cumple satisfactoriamente con "
            f"el criterio establecido ({Q.fp_llenado_max_underdrain * 100:.0f}%), operando el "
            "canal con superficie libre. Esta condición asegura que durante la operación normal "
            "y condiciones de pico el sistema mantendrá espacio disponible para el flujo de aire, "
            "garantizando la ventilación natural del filtro percolador."
        )
    else:
        texto_underdrain = (
            f"El llenado calculado ({llenado_canal * 100:.1f}%) excede el límite recomendado "
            f"({Q.fp_llenado_max_underdrain * 100:.0f}%), indicando que el canal operará con "
            "sección llena o cercana a la capacidad máxima. Esta condición compromete la "
            "ventilación natural y puede causar acumulación de agua en el fondo del filtro. "
            "Se recomienda incrementar la pendiente del canal o aumentar sus dimensiones."
        )

    estado_resistencia = "Cumple" if resistencia_ok else "No cumple"
    if resistencia_ok:
        texto_resistencia = (
            f"La carga calculada de {carga_peso_medio_kg_m2:.1f} kg/m² es inferior a la "
            f"resistencia mínima requerida de {resistencia_minima_requerida:.0f} kg/m² para "
            f"la profundidad de {D_m:.2f} m adoptada. El medio plástico seleccionado cumple "
            "satisfactoriamente con el requisito de resistencia a compresión, garantizando la "
            "integridad estructural durante la vida útil del filtro."
        )
    else:
        texto_resistencia = (
            f"La carga calculada de {carga_peso_medio_kg_m2:.1f} kg/m² excede la resistencia "
            f"mínima requerida de {resistencia_minima_requerida:.0f} kg/m² para la profundidad "
            "adoptada. Se recomienda reducir la profundidad del medio o seleccionar un medio "
            "con mayor resistencia estructural."
        )
    
    # =================================================================
    # SÓLIDOS BIOLÓGICOS DESPRENDIDOS (para transferencia al sedimentador)
    # =================================================================
    # La biomasa desprendida del FP se transfiere al sedimentador secundario
    # donde se sedimenta como humus. No va directo al lecho (evita doble conteo).
    solidos_biologicos_kg_d = DBO_removida_kg_d * Q.sed_factor_produccion_humus
    
    # Verificaciones finales (después de todos los ajustes)
    assert Cv_minima <= Cv_kgDBO_m3_d <= Q.fp_Cv_maxima_kgDBO_m3_d, (
        f"Carga orgánica Cv = {Cv_kgDBO_m3_d:.3f} kg DBO/m^3*d fuera de rango {Cv_minima}-{Q.fp_Cv_maxima_kgDBO_m3_d} "
        f"({ref_wef}, Cap. 9)"
    )
    assert Q.fp_qA_real_min_m3_m2_h <= Q_A_real <= 18.0, (
        f"Tasa hidráulica Q_A = {Q_A_real:.2f} m^3/m^2*h fuera de rango "
        f"{Q.fp_qA_real_min_m3_m2_h}-18 ({ref_me}, p. 843)"
    )
    # Texto de verificación narrativo
    if Q_A_max_m3_m2_h < Q_A_limite_m3_m2_h:
        verif_qmax_texto = f"el valor obtenido ({Q_A_max_m3_m2_h:.2f} m³/m²·h) es menor que el límite máximo recomendado de {Q_A_limite_m3_m2_h:.1f} m³/m²·h establecido por Metcalf y Eddy para evitar el arrastre de biopelícula, por lo que el diseño es adecuado"
    elif Q_A_max_m3_m2_h == Q_A_limite_m3_m2_h:
        verif_qmax_texto = f"el valor obtenido ({Q_A_max_m3_m2_h:.2f} m³/m²·h) es igual al límite máximo recomendado de {Q_A_limite_m3_m2_h:.1f} m³/m²·h establecido por Metcalf y Eddy para evitar el arrastre de biopelícula, por lo que el diseño es adecuado"
    else:
        verif_qmax_texto = f"el valor obtenido ({Q_A_max_m3_m2_h:.2f} m³/m²·h) excede el límite máximo recomendado de {Q_A_limite_m3_m2_h:.1f} m³/m²·h establecido por Metcalf y Eddy para evitar el arrastre de biopelícula, por lo que el diseño requiere revisión"

    return {
        "unidad": "Filtro Percolador",
        # Datos de entrada
        "DBO_entrada_mg_L": round(DBO_entrada_mg_L, 1),
        "DBO_salida_objetivo_mg_L": DBO_salida_mg_L,
        "DBO_salida_Germain_mg_L": round(Se_calculado_mg_L, 1),
        "se_cumple_objetivo_Germain": se_cumple_objetivo,  # True si Se <= objetivo
        "estado_germain": estado_germain,
        "texto_germain": texto_germain,
        "Q_m3_d": round(Q_m3_d, 1),
        "Q_ap_m3_h": round(Q_ap_m3_h, 2),
        # Parámetros del modelo Germain (verificación)
        "k_20_m_h": k_20_m_h,
        "k_T_m_h": round(k_T_m_h, 4),
        "theta": theta,
        "n_germain": n,
        "D_medio_m": D_m,
        "D_medio_min_m": Q.fp_D_medio_min_m,
        "D_medio_max_m": Q.fp_D_medio_max_m,
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
        "H_distribucion_min_m": Q.fp_H_distribucion_min_m,
        "H_distribucion_max_m": Q.fp_H_distribucion_max_m,
        "H_medio_m": D_m,
        "H_underdrain_m": H_underdrain,
        "H_underdrain_min_m": Q.fp_H_underdrain_min_m,
        "H_underdrain_max_m": Q.fp_H_underdrain_max_m,
        "H_bordo_libre_m": H_bordo_fp,
        "H_bordo_libre_min_m": Q.fp_H_bordo_libre_min_m,
        "H_bordo_libre_max_m": Q.fp_H_bordo_libre_max_m,
        # PASO 5 - Recirculación
        "qA_min_m3_m2_h": round(qA_min_m3_m2_h, 2),
        "recirculacion_adicional_recomendada": recirculacion_adicional,
        "qA_min_texto": qA_min_texto,
        # PASO 6 - Distribuidor
        "num_brazos": num_brazos,
        "L_brazo_m": round(L_brazo_m, 2),
        "Q_por_brazo_m3_h": round(Q_por_brazo_m3_h, 1),
        "rotacion_hidraulica": rotacion_hidraulica,
        "estado_rotacion": estado_rotacion,
        "texto_rotacion": texto_rotacion,
        "num_boquillas_por_brazo": num_boquillas_por_brazo,
        "Q_por_boquilla_L_s": round(Q_por_boquilla_L_s, 2),
        "v_boquilla_m_s": v_boquilla_m_s,
        "estado_boquillas": estado_boquillas,
        "texto_boquillas": texto_boquillas,
        "diam_orificio_mm": round(diam_orificio_mm, 1),
        # PASO 7 - Underdrain
        "Q_underdrain_diseno_m3_h": round(Q_underdrain_diseno_m3_h, 1),
        "ancho_canal_central_m": ancho_canal,
        "altura_canal_central_m": altura_canal,
        "Q_canal_capacidad_m3_h": round(Q_canal_m3_h, 1),
        "llenado_canal_pct": round(llenado_canal * 100, 1),
        "canal_underdrain_ok": canal_ok,
        "estado_underdrain": estado_underdrain,
        "texto_underdrain": texto_underdrain,
        "pendiente_underdrain_pct": Q.fp_pendiente_underdrain_pct,
        # PASO 8 - Ventilación
        "area_ventilacion_requerida_m2": round(area_ventilacion_requerida_m2, 4),
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
        "resistencia_minima_requerida_kg_m2": resistencia_minima_requerida,
        "estado_resistencia": estado_resistencia,
        "texto_resistencia": texto_resistencia,
        "DBO_removida_kg_d": round(DBO_removida_kg_d, 2),
        "solidos_biologicos_kg_d": round(solidos_biologicos_kg_d, 2),
        # Subproductos - estructura normalizada
        "subproductos": {
            "lodos": [
                {
                    "origen": "Filtro Percolador",
                    "tipo": "solidos biologicos desprendidos / humus",
                    "kg_d": round(solidos_biologicos_kg_d, 2),
                    "base_solidos": "SST",
                    "kg_SST_d": round(solidos_biologicos_kg_d, 2),
                    "kg_SSV_d": None,
                    "m3_d": None,
                    "concentracion_kg_m3": None,
                    "estado_fisico": "suspendido_en_efluente",
                    "destino": "sedimentador_secundario",
                    "apto_lecho_directo": False,
                    "nota": "El filtro genera biomasa desprendida; en este tren se "
                            "transfiere al sedimentador secundario y no se suma "
                            "directamente al lecho."
                }
            ],
            "transferencias": [],
            "biogas": [],
            "residuos_gruesos": [],
            "arenas": []
        },
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
            f"{'<=' if se_cumple_objetivo else '>'} objetivo {DBO_salida_mg_L} mg/L"
            f"{' (cumple eficiencia requerida)' if se_cumple_objetivo else ' (NO CUMPLE eficiencia requerida)'}. "
            f"k_T = {k_T_m_h:.4f} m/h a T={Q.T_agua_C} grados C (θ={theta})."
        ),
    }


# =============================================================================
# 4b - BIOFILTRO DE CARGA MECANIZADA HIDRÁULICA (TAF - TRICKLING FILTER)
# =============================================================================

def dimensionar_biofiltro_carga_mecanizada_hidraulica(
    Q: ConfigDiseno = CFG,
    DBO_entrada_mg_L: float = None,
    SST_entrada_mg_L: float = None,
    ruta_diseno: str = None
) -> Dict[str, Any]:
    """
    Dimensionamiento del Biofiltro de Carga Mecanizada Hidráulica (TAF).
    
    Siguiendo el manual técnico, implementa dos rutas de diseño:
    - RUTA A: Carga Hidráulica Convencional (modelo NRC, sin recirculación)
    - RUTA B: Carga Mecanizada de Alta Carga (modelo Germain, con recirculación)
    
    El algoritmo de selección automática usa COS_preliminar > 0.40 kg/m³·d como
    umbral para seleccionar Ruta B, con fallback a Ruta A.
    
    Parámetros:
        Q: ConfigDiseno con parámetros globales
        DBO_entrada_mg_L: DBO5 del afluente al biofiltro (mg/L)
        SST_entrada_mg_L: SST del afluente al biofiltor (mg/L) 
        ruta_diseno: "A", "B", o None para selección automática
    
    Retorna:
        Dict con resultados del dimensionamiento y verificación
    """
    ref_me = citar("metcalf_2014")
    ref_wef = citar("wef_mop8_2010")
    ref_germain = "Germain (1966)"
    ref_nrc = "NRC (National Research Council)"
    
    # DBO5 entrante al biofiltro (si no se especifica, asumir salida típica UASB)
    if DBO_entrada_mg_L is None:
        DBO_entrada_mg_L = Q.DBO5_mg_L * 0.30  # ~75 mg/L tras UASB con 70% remoción
    
    if SST_entrada_mg_L is None:
        SST_entrada_mg_L = Q.SST_mg_L * 0.40  # ~100 mg/L tras UASB
    
    # Parámetros básicos
    Q_m3_d = Q.Q_linea_m3_d
    Q_m3_h = Q.Q_linea_m3_h
    T = Q.T_agua_C
    factor_pico = Q.factor_pico_Qmax
    Q_max_m3_d = Q_m3_d * factor_pico
    Q_max_m3_h = Q_max_m3_d / 24
    
    # Carga orgánica afluente (kg/d)
    W_kg_d = Q_m3_d * DBO_entrada_mg_L / 1000.0
    
    # =============================================================================
    # ALGORITMO DE SELECCIÓN DE RUTA
    # =============================================================================
    
    # Estimación preliminar de COS para selección de ruta
    # Asumiendo volumen típico inicial para estimar COS
    V_estimado_m3 = W_kg_d / Q.bf_cmh_Cv_kgDBO_m3_d
    COS_prelim = W_kg_d / V_estimado_m3
    
    if ruta_diseno is None:
        # Selección automática basada en COS y criterios del manual
        if COS_prelim > Q.bf_cmh_COS_limite_ruta_A:
            ruta = "B"
            criterio_seleccion = f"COS_prelim = {COS_prelim:.2f} kg/m³·d > {Q.bf_cmh_COS_limite_ruta_A:.2f} → Ruta B"
        else:
            ruta = "A"
            criterio_seleccion = f"COS_prelim = {COS_prelim:.2f} kg/m³·d ≤ {Q.bf_cmh_COS_limite_ruta_A:.2f} → Ruta A"
    else:
        ruta = ruta_diseno.upper()
        criterio_seleccion = f"Selección manual: Ruta {ruta}"
    
    # =============================================================================
    # PARÁMETROS DEL MODELO
    # =============================================================================
    
    # Corrección por temperatura
    k_20 = Q.bf_cmh_k_20_m_h
    theta = Q.bf_cmh_theta
    k_T_m_h = k_20 * (theta ** (T - 20))
    
    # Profundidad del medio
    D_m = Q.bf_cmh_D_medio_m
    
    if ruta == "A":
        # =============================================================================
        # RUTA A: CARGA HIDRÁULICA CONVENCIONAL - Modelo NRC
        # =============================================================================
        
        # Sin recirculación para Ruta A convencional
        R = 0.0
        F_recirculacion = 1.0  # Factor F = 1 cuando R = 0
        
        # Carga orgánica y volumen por criterio de carga
        Cv_diseno = Q.bf_cmh_Cv_kgDBO_m3_d
        V_medio_m3 = W_kg_d / Cv_diseno
        
        # Área y diámetro
        A_sup_m2 = V_medio_m3 / D_m
        D_bf_m = math.sqrt(4 * A_sup_m2 / math.pi)
        
        # Carga Hidráulica Superficial (CHS)
        CHS_m3_m2_h = Q_m3_h / A_sup_m2
        CHS_m3_m2_d = CHS_m3_m2_h * 24
        
        # Verificación NRC: E = 1 / (1 + 0.4432 * sqrt(W/(V*F)))
        E_calculada = 1.0 / (1.0 + 0.4432 * math.sqrt(W_kg_d / (V_medio_m3 * F_recirculacion)))
        Se_calculada_mg_L = DBO_entrada_mg_L * (1 - E_calculada)
        
        # COS final
        COS = W_kg_d / V_medio_m3
        
        # Tiempo de retención hidráulico
        HRT_h = V_medio_m3 / Q_m3_h
        
        modelo_usado = "NRC (sin recirculación)"
        ecuacion_eficiencia = r"E = \frac{1}{1 + 0.4432 \sqrt{\frac{W}{V \cdot F}}}"
        
    else:
        # =============================================================================
        # RUTA B: CARGA MECANIZADA DE ALTA CARGA - Modelo Germain
        # =============================================================================
        
        # Con recirculación
        R = Q.bf_cmh_R_recirculacion
        
        # Concentración diluida
        S0_prima = DBO_entrada_mg_L / (1 + R)
        
        # Carga orgánica volumétrica para alta carga
        Cv_diseno = Q.bf_cmh_Cv_ruta_B_kgDBO_m3_d
        V_medio_m3 = W_kg_d / Cv_diseno
        
        # Área y dimensiones
        A_sup_m2 = V_medio_m3 / D_m
        D_bf_m = math.sqrt(4 * A_sup_m2 / math.pi)
        
        # Carga hidráulica total (con recirculación)
        Q_T_m3_h = Q_m3_h * (1 + R)
        Q_T_m3_m2_h = Q_T_m3_h / A_sup_m2
        
        # Modelo de Germain: Se/S0' = exp(-k_T * D / Q_T^n)
        n = Q.bf_cmh_n_germain
        relacion_Se_S0 = math.exp(-k_T_m_h * D_m / (Q_T_m3_m2_h ** n))
        Se_calculada_mg_L = S0_prima * relacion_Se_S0
        
        # Eficiencia global (considerando recirculación)
        E_calculada = (DBO_entrada_mg_L - Se_calculada_mg_L) / DBO_entrada_mg_L
        
        # COS y CHS
        COS = W_kg_d / V_medio_m3
        CHS_m3_m2_h = Q_T_m3_m2_h  # CHS total con recirculación
        CHS_m3_m2_d = CHS_m3_m2_h * 24
        
        # Caudal de recirculación
        Q_R_m3_d = Q_m3_d * R
        Q_R_m3_h = Q_R_m3_d / 24
        
        # Tiempo de retención hidráulico
        HRT_h = V_medio_m3 / Q_T_m3_h
        
        modelo_usado = "Germain (con recirculación)"
        ecuacion_eficiencia = r"\frac{S_e}{S_0'} = \exp\left(-\frac{k_T \cdot D}{Q_T^n}\right)"
        F_recirculacion = (1 + R) / ((1 + 0.1 * R) ** 2)  # Factor NRC equivalente
    
    # =============================================================================
    # GEOMETRÍA COMPLETA
    # =============================================================================
    
    H_distribucion = Q.bf_cmh_H_distribucion_m
    H_underdrain = Q.bf_cmh_H_underdrain_m
    H_bordo = Q.bf_cmh_H_bordo_libre_m
    H_total_m = H_distribucion + D_m + H_underdrain + H_bordo
    
    # =============================================================================
    # VERIFICACIONES
    # =============================================================================
    
    # 1. Verificación COS (carga orgánica superficial)
    cumple_COS = COS <= Q.bf_cmh_COS_max_kgDBO_m3_d
    
    # 3. Verificación CHS
    cumple_CHS = (Q.bf_cmh_CHS_min_m3_m2_h <= CHS_m3_m2_h <= Q.bf_cmh_CHS_max_m3_m2_h)
    
    # 4. Verificación TULSMA
    cumple_TULSMA = Se_calculada_mg_L <= Q.tulsma_DBO5_limite_mg_L
    
    # =============================================================================
    # SISTEMA DE DISTRIBUCIÓN
    # =============================================================================
    
    num_brazos = Q.bf_cmh_num_brazos
    if ruta == "B":
        Q_aplicado_m3_h = Q_m3_h * (1 + R)
    else:
        Q_aplicado_m3_h = Q_m3_h
    
    Q_por_brazo_m3_h = Q_aplicado_m3_h / num_brazos
    L_brazo_m = D_bf_m / 2
    
    # Boquillas
    num_boquillas = Q.bf_cmh_num_boquillas_por_brazo
    Q_por_boquilla_L_s = (Q_por_brazo_m3_h / num_boquillas) * 1000 / 3600
    v_boquilla_m_s = Q.bf_cmh_velocidad_boquilla_m_s
    A_orificio_m2 = (Q_por_brazo_m3_h / 3600) / (num_boquillas * v_boquilla_m_s)
    diam_orificio_mm = math.sqrt(4 * A_orificio_m2 / math.pi) * 1000
    
    # =============================================================================
    # VENTILACIÓN
    # =============================================================================
    
    area_vent_m2 = A_sup_m2 * Q.bf_cmh_area_ventilacion_pct / 100
    Q_aire_m3_h = Q_m3_h * Q.bf_cmh_Q_aire_factor
    
    # =============================================================================
    # PRODUCCIÓN DE LODOS (sólidos biológicos)
    # =============================================================================
    
    DBO_removida_kg_d = Q_m3_d * (DBO_entrada_mg_L - Se_calculada_mg_L) / 1000
    solidos_humus_kg_d = DBO_removida_kg_d * Q.bf_cmh_factor_produccion_humus
    
    # SST efluente estimado (considerando producción de humus)
    SST_efluente_estimado = SST_entrada_mg_L * 0.7 + (solidos_humus_kg_d / Q_m3_d * 1000)
    
    # =============================================================================
    # TEXTOS DE VERIFICACIÓN PARA LATEX
    # =============================================================================
    
    if ruta == "A":
        texto_ruta = (
            f"Se selecciona la Ruta A (Carga Hidráulica Convencional) según el criterio: "
            f"{criterio_seleccion}. Esta ruta utiliza el modelo NRC sin recirculación, "
            f"apropiada para cargas orgánicas moderadas."
        )
    else:
        texto_ruta = (
            f"Se selecciona la Ruta B (Carga Mecanizada de Alta Carga) según el criterio: "
            f"{criterio_seleccion}. Esta ruta utiliza el modelo Germain con recirculación "
            f"R={R:.1f}, apropiada para alta carga orgánica y mejora la eficiencia de tratamiento."
        )
    
    return {
        "unidad": "Biofiltro Carga Mecanizada Hidráulica",
        "ruta_diseno": ruta,
        "modelo_usado": modelo_usado,
        "criterio_seleccion": criterio_seleccion,
        "texto_ruta": texto_ruta,
        
        # Datos de entrada
        "Q_m3_d": round(Q_m3_d, 1),
        "Q_m3_h": round(Q_m3_h, 2),
        "Q_max_m3_d": round(Q_max_m3_d, 1),
        "Q_max_m3_h": round(Q_max_m3_h, 2),
        "DBO_entrada_mg_L": round(DBO_entrada_mg_L, 1),
        "SST_entrada_mg_L": round(SST_entrada_mg_L, 1),
        "T_agua_C": T,
        
        # Parámetros del modelo
        "k_20_m_h": k_20,
        "k_T_m_h": round(k_T_m_h, 4),
        "theta": theta,
        "n_germain": Q.bf_cmh_n_germain if ruta == "B" else None,
        "D_medio_m": D_m,
        "R_recirculacion": R,
        "F_recirculacion": round(F_recirculacion, 3),
        
        # Resultados de dimensionamiento
        "W_kg_d": round(W_kg_d, 2),
        "E_calculada": round(E_calculada, 3),
        "V_medio_m3": round(V_medio_m3, 1),
        "A_sup_m2": round(A_sup_m2, 2),
        "D_bf_m": round(D_bf_m, 2),
        "COS_kg_m3_d": round(COS, 3),
        "Cv_diseno_kg_m3_d": Cv_diseno,
        "CHS_m3_m2_h": round(CHS_m3_m2_h, 3),
        "CHS_m3_m2_d": round(CHS_m3_m2_d, 2),
        "HRT_h": round(HRT_h, 2),
        
        # Geometría
        "H_distribucion_m": H_distribucion,
        "H_underdrain_m": H_underdrain,
        "H_bordo_libre_m": H_bordo,
        "H_total_m": round(H_total_m, 2),
        
        # Efluente calculado
        "Se_calculada_mg_L": round(Se_calculada_mg_L, 1),
        "texto_eficiencia": f"La DBO₅ efluente calculada es {Se_calculada_mg_L:.1f} mg/L.",
        "cumple_TULSMA": cumple_TULSMA,
        
        # Ruta B específico
        "S0_prima_mg_L": round(DBO_entrada_mg_L / (1 + R), 1) if ruta == "B" else None,
        "Q_T_m3_h": round(Q_m3_h * (1 + R), 2) if ruta == "B" else None,
        "Q_R_m3_d": round(Q_m3_d * R, 1) if ruta == "B" else None,
        "Q_R_m3_h": round(Q_m3_h * R, 2) if ruta == "B" else None,
        "relacion_Se_S0": round(Se_calculada_mg_L / DBO_entrada_mg_L, 4) if ruta == "B" else None,
        
        # Distribuidor
        "num_brazos": num_brazos,
        "Q_aplicado_m3_h": round(Q_aplicado_m3_h, 2),
        "Q_por_brazo_m3_h": round(Q_por_brazo_m3_h, 2),
        "L_brazo_m": round(L_brazo_m, 2),
        "num_boquillas_por_brazo": num_boquillas,
        "Q_por_boquilla_L_s": round(Q_por_boquilla_L_s, 3),
        "v_boquilla_m_s": v_boquilla_m_s,
        "diam_orificio_mm": round(diam_orificio_mm, 1),
        
        # Ventilación
        "area_ventilacion_m2": round(area_vent_m2, 3),
        "Q_aire_m3_h": round(Q_aire_m3_h, 1),
        
        # Lodos
        "DBO_removida_kg_d": round(DBO_removida_kg_d, 2),
        "solidos_humus_kg_d": round(solidos_humus_kg_d, 2),
        "SST_efluente_estimado_mg_L": round(SST_efluente_estimado, 1),
        
        # Verificaciones
        "verificaciones": {
            "COS": {"valor": round(COS, 3), "limite": Q.bf_cmh_COS_max_kgDBO_m3_d, "cumple": cumple_COS},
            "CHS": {"valor": round(CHS_m3_m2_h, 3), "min": Q.bf_cmh_CHS_min_m3_m2_h, "max": Q.bf_cmh_CHS_max_m3_m2_h, "cumple": cumple_CHS},
            "TULSMA": {"valor": round(Se_calculada_mg_L, 1), "limite": Q.tulsma_DBO5_limite_mg_L, "cumple": cumple_TULSMA},
        },
        
        # Subproductos
        "subproductos": {
            "lodos": [
                {
                    "origen": "Biofiltro TAF",
                    "tipo": "solidos biologicos desprendidos / humus",
                    "kg_d": round(solidos_humus_kg_d, 2),
                    "base_solidos": "SST",
                    "kg_SST_d": round(solidos_humus_kg_d, 2),
                    "destino": "sedimentador_secundario",
                    "nota": "Producción de humus del biofiltro TAF"
                }
            ],
            "transferencias": [],
            "biogas": [],
            "residuos_gruesos": [],
            "arenas": []
        },
        
        # Layout
        "diametro_layout_m": round(D_bf_m + 0.30, 1),
        "ecuacion_eficiencia": ecuacion_eficiencia,
        
        # Fuentes
        "fuente": f"{ref_me} (pp. 840-870); {ref_wef} (Cap. 9); {ref_germain if ruta == 'B' else ref_nrc}",
        "notas": f"Ruta {ruta}: {modelo_usado}. COS={COS:.2f} kg/m³·d, CHS={CHS_m3_m2_h:.2f} m³/m²·h",
    }


# =============================================================================
# 5 - HUMEDAL CONSTRUIDO DE FLUJO VERTICAL SUBSUPERFICIAL (HFCV)
# =============================================================================

def seleccionar_sistema_humedal(Q: ConfigDiseno = CFG,
                                 area_disponible_m2: float = None,
                                 afluente_crudo: bool = False,
                                 capacitacion_operador: bool = True,
                                 restriccion_bioseguridad: bool = False,
                                 objetivo_NH4_estricto: bool = False,
                                 contexto_proyecto: str = "general") -> Dict[str, Any]:
    """
    Algoritmo de selección entre Sistema Clásico (Ruta A) y HAFV tropical de alta carga (Ruta B).
    
    Basado en Sección 3 del manual: temperatura es criterio primario (Paso A1).
    
    Lógica de criterios A2 (transparente y trazable):
    ------------------------------------------------------------
    Según el manual, se evalúan 4 criterios A2.1-A2.4, pero solo algunos afectan
    la selección del sistema hidráulico:
    
    Puntuación (0 o 1 por criterio AFECTIVO):
    - A2.1 (Área): <1.5 m²/PE → 1 punto (limitada favorece Ruta B)
                     No especificada → ASUMIDA según contexto (marcado como supuesto)
                     ≥2.5 m²/PE → 0 puntos (suficiente para clásico)
                     [AFECTA SELECCIÓN]
                     
    - A2.2 (Afluente): Si crudo → 1 punto (celda francesa canónica / Ruta B favorecida en trópico)
                       Si post-UASB/primario → 0 puntos NEUTRAL 
                       (manual: "ambos sistemas son aplicables")
                       [SOLO AFECTA SI ES CRUDO]
    
    - A2.3 (Capacitación): Disponible → 1 punto; Limitada → 0 puntos
                           (Ruta B requiere operación por pulsos entrenada)
                           [AFECTA SELECCIÓN]
    
    - A2.4 (Bioseguridad): NEUTRAL → Siempre 0 puntos para selección hidráulica
                           (manual: "NO afecta la selección del sistema")
                           Solo se documenta como observación.
    
    Decisión: ≥2 puntos de 2 criterios afectivos → Ruta B (HAFV tropical de alta carga)
              <2 puntos → Ruta A (Clásico)
    
    NOTA METODOLÓGICA IMPORTANTE:
    ------------------------------------------------------------
    La regla "2/2 criterios afectivos" es una SIMPLIFICACIÓN IMPLEMENTADA,
    no una formulación literal del manual. Surge de:
    
    1. Tratar A2.2 como NEUTRAL (0 puntos) para post-UASB, siguiendo el 
       manual que indica "ambos sistemas son aplicables"
    2. Tratar A2.4 como NEUTRAL (0 puntos) siempre, siguiendo el manual 
       que indica "NO afecta la selección del sistema"
    
    Esto reduce los criterios que verdaderamente discriminan entre sistemas
    a solo A2.1 (Área) y A2.3 (Capacitación). El umbral ≥2/2 es la traducción
    implementada del criterio conceptual del manual: la adaptación tropical de alta carga
    es viable cuando el área es limitada Y hay capacitación disponible.
    
    NOTA IMPORTANTE SOBRE A2.1 SIN ESPECIFICAR:
    Si area_disponible_m2 es None, se requiere el parámetro contexto_proyecto:
    - "insular": Asume área limitada típica de islas (favorece Ruta B)
    - "urbano": Asume área intermedia
    - "rural": Asume área suficiente disponible (favorece clásico)
    - "general": Asume área limitada por defecto (conservador)
    El supuesto se registra explícitamente en 'supuestos_explicitos'.
    
    Args:
        Q: Configuración de diseño
        area_disponible_m2: Área disponible en el terreno (m²), None si no se conoce
        afluente_crudo: True si afluente crudo, False si post-primario
        capacitacion_operador: True si hay capacitación técnica disponible
        restriccion_bioseguridad: True si hay restricciones de inoculantes
        objetivo_NH4_estricto: True si requiere NH4 < 10 mg/L (activa sistema híbrido)
        contexto_proyecto: "insular", "urbano", "rural", o "general" (para A2.1 sin especificar)
    
    Returns:
        Dict con sistema seleccionado, justificación detallada, y trazabilidad completa
    """
    T = Q.T_agua_C
    
    # PASO A1: Criterio primario de temperatura
    if T < Q.humedal_temp_limite_clasico_C:
        # CONDICIÓN 1: T < 15°C → Sistema Clásico obligatorio
        return {
            "sistema": "CLASICO",
            "ruta": "A",
            "condicion": 1,
            "justificacion": f"T = {T}C < {Q.humedal_temp_limite_clasico_C}C: Sistema Clasico obligatorio (manual Seccion 3, Paso A1)",
            "hibrido": False,
            "trazabilidad": {
                "temperatura_C": T, 
                "criterio": "T < 15C obliga Clasico",
                "nota_metodologica": "Sistema Clasico obligatorio por temperatura < 15C. No se evaluan criterios A2."
            }
        }
    
    if objetivo_NH4_estricto and T >= Q.humedal_temp_limite_transicion_C:
        # CONDICIÓN 4: Sistema híbrido Ruta B + HFHS
        return {
            "sistema": "FRANCES_HIBRIDO",
            "ruta": "B+",
            "condicion": 4,
            "justificacion": f"T = {T}C >= 20C pero objetivo NH4 estricto (<10 mg/L) requiere HFHS adicional (manual Seccion 3, A2.5)",
            "hibrido": True,
            "trazabilidad": {
                "NH4_estricto": True, 
                "sistema_adicional": "HFHS",
                "nota_metodologica": "Sistema hibrido activado por objetivo estricto de NH4."
            }
        }
    
    if T < Q.humedal_temp_limite_transicion_C:
        # CONDICIÓN 3: Zona de transición (15-20°C) → Clásico con factor de seguridad
        return {
            "sistema": "CLASICO",
            "ruta": "A",
            "condicion": 3,
            "justificacion": f"T = {T}C en zona transicion (15-20C): Sistema Clasico con FS 20-30% (manual Seccion 3, Paso A1)",
            "hibrido": False,
            "factor_seguridad_adicional": 1.25,
            "trazabilidad": {
                "temperatura_C": T, 
                "zona": "transicion",
                "nota_metodologica": "Zona de transicion 15-20C: Sistema Clasico con factor de seguridad 20-30%."
            }
        }
    
    # T >= 20°C: Evaluar criterios A2 para HAFV tropical de alta carga (Paso A2)
    # Sistema de puntuación transparente: 4 criterios, cada uno 0 o 1 punto
    puntuacion = {"A2.1": 0, "A2.2": 0, "A2.3": 0, "A2.4": 0}
    detalle_criterios = {}
    supuestos = []  # Lista de supuestos explícitos
    
    # A2.1: Área disponible (m²/PE)
    if area_disponible_m2 is not None:
        # Cálculo explícito con dato proporcionado
        PE_estimado = Q.Q_total_m3_d / 0.15  # 150 L/hab·d según manual
        area_por_PE = area_disponible_m2 / PE_estimado if PE_estimado > 0 else 999
        if area_por_PE < 1.5:
            puntuacion["A2.1"] = 1
            detalle_criterios["A2.1_area"] = f"Limitada ({area_por_PE:.1f} m2/PE < 1.5) -> favorece Ruta B"
        elif area_por_PE >= 2.5:
            puntuacion["A2.1"] = 0
            detalle_criterios["A2.1_area"] = f"Suficiente ({area_por_PE:.1f} m2/PE >= 2.5) -> favorece clasico"
        else:
            puntuacion["A2.1"] = 0  # Intermedia no suma punto
            detalle_criterios["A2.1_area"] = f"Intermedia ({area_por_PE:.1f} m2/PE) -> neutral"
    else:
        # Área no especificada: aplicar supuesto según contexto del proyecto
        if contexto_proyecto == "insular":
            puntuacion["A2.1"] = 1
            detalle_criterios["A2.1_area"] = "No especificada -> SUPUESTO: contexto insular tipicamente limitado -> favorece Ruta B"
            supuestos.append("A2.1: Area asumida limitada por contexto insular (isla San Cristobal)")
        elif contexto_proyecto == "rural":
            puntuacion["A2.1"] = 0
            detalle_criterios["A2.1_area"] = "No especificada -> SUPUESTO: contexto rural tipicamente con area suficiente"
            supuestos.append("A2.1: Area asumida suficiente por contexto rural")
        else:  # "general" o "urbano"
            puntuacion["A2.1"] = 1
            detalle_criterios["A2.1_area"] = "No especificada -> SUPUESTO: general/urbano tipicamente limitado -> favorece Ruta B"
            supuestos.append(f"A2.1: Area asumida limitada por contexto '{contexto_proyecto}'")
    
    # A2.2: Tipo de afluente
    # Manual Seccion 3: 
    # - Crudo: French es el único viable en trópico (1 punto)
    # - Post-UASB/primario: AMBOS sistemas aplicables → NEUTRAL (0 puntos)
    if afluente_crudo:
        puntuacion["A2.2"] = 1
        detalle_criterios["A2.2_afluente"] = "Crudo pretratado -> celda francesa canónica/Ruta B favorecida en tropico"
    else:
        # Post-UASB: Manual dice "ambos sistemas son aplicables" → NEUTRAL
        puntuacion["A2.2"] = 0
        detalle_criterios["A2.2_afluente"] = "Post-primario (post-UASB) -> ambos aplicables segun manual (neutral)"
    
    # A2.3: Capacitación operador
    if capacitacion_operador:
        puntuacion["A2.3"] = 1
        detalle_criterios["A2.3_capacitacion"] = "Disponible -> favorece Ruta B (requiere operacion por pulsos)"
    else:
        puntuacion["A2.3"] = 0
        detalle_criterios["A2.3_capacitacion"] = "Limitada -> favorece clasico (sistema mas robusto operativamente)"
    
    # A2.4: Bioseguridad
    # Manual Seccion 3: "Esto NO afecta la seleccion del sistema hidraulico"
    # Por tanto es NEUTRAL para la decision (siempre 0 puntos), solo se documenta
    puntuacion["A2.4"] = 0
    if not restriccion_bioseguridad:
        detalle_criterios["A2.4_bioseguridad"] = "Sin restricciones de inoculantes (neutral - no afecta seleccion)"
    else:
        detalle_criterios["A2.4_bioseguridad"] = "Con restricciones de inoculantes (neutral - no afecta seleccion)"
        supuestos.append("A2.4: Proyecto en area con restricciones de bioseguridad (observacion, no afecta seleccion)")
    
    # PASO A3: Decisión final
    # Solo A2.1 y A2.3 afectan la selección (A2.2 y A2.4 son neutrales para post-UASB)
    puntos_total = sum(puntuacion.values())
    criterios_afectivos = ["A2.1", "A2.3"]  # Los únicos que puntúan para la decisión
    puntos_efectivos = puntuacion["A2.1"] + puntuacion["A2.3"]
    
    # Umbral: ≥2 de 2 criterios afectivos favorables → Ruta B
    # (A2.2=0 y A2.4=0 para post-UASB según manual)
    if puntos_efectivos >= 2:
        # CONDICIÓN 2: HAFV tropical de alta carga
        return {
            "sistema": "FRANCES",
            "ruta": "B",
            "condicion": 2,
            "justificacion": f"T = {T}C >= 20C y {puntos_efectivos}/2 criterios afectivos favorables (A2.1 y A2.3) -> Ruta B (HAFV tropical de alta carga, adaptacion basada en Molle)",
            "hibrido": False,
            "puntuacion_detalle": puntuacion,
            "puntos_total": puntos_total,
            "puntos_efectivos_decision": puntos_efectivos,
            "criterios_afectivos": criterios_afectivos,
            "criterios": detalle_criterios,
            "supuestos_explicitos": supuestos if supuestos else None,
            "trazabilidad": {
                "temperatura_C": T,
                "criterios_evaluados": 4,
                "criterios_afectivos_decision": 2,
                "puntos_efectivos": puntos_efectivos,
                "umbral_ruta_B": 2,
                "nota_metodologica": "Regla 2/2 es simplificacion implementada (A2.2 y A2.4 neutrales), no literal del manual",
                "contexto_proyecto": contexto_proyecto
            }
        }
    else:
        # CONDICIÓN 3: Volver a Clásico
        return {
            "sistema": "CLASICO",
            "ruta": "A",
            "condicion": 3,
            "justificacion": f"T = {T}C >= 20C pero solo {puntos_efectivos}/2 criterios afectivos favorables -> Ruta A (Clásico)",
            "hibrido": False,
            "puntuacion_detalle": puntuacion,
            "puntos_total": puntos_total,
            "puntos_efectivos_decision": puntos_efectivos,
            "criterios_afectivos": criterios_afectivos,
            "criterios": detalle_criterios,
            "supuestos_explicitos": supuestos if supuestos else None,
            "trazabilidad": {
                "temperatura_C": T,
                "criterios_evaluados": 4,
                "criterios_afectivos_decision": 2,
                "puntos_efectivos": puntos_efectivos,
                "umbral_ruta_B": 2,
                "nota_metodologica": "Regla 2/2 es simplificacion implementada (A2.2 y A2.4 neutrales), no literal del manual",
                "contexto_proyecto": contexto_proyecto
            }
        }


def verificar_kc_humedal(Q: ConfigDiseno, 
                         A_operando_m2: float,
                         DBO_entrada_mg_L: float,
                         DQO_entrada_mg_L: float = None,
                         Q_verificacion_m3_d: float = None) -> Dict[str, Any]:
    """
    Verificación complementaria de eficiencia por modelo k-C* (Sección 11 del manual).
    Recomendada en ambas rutas como chequeo secundario de desempeño.
    
    Args:
        Q: Configuración de diseño
        A_operando_m2: Área del filtro en operación (m²)
        DBO_entrada_mg_L: DBO5 afluente (mg/L)
        DQO_entrada_mg_L: DQO afluente opcional (mg/L)
        Q_verificacion_m3_d: Caudal usado para la verificación k-C* (m³/d).
            Si no se entrega, usa Q.Q_linea_m3_d por compatibilidad.
    
    Returns:
        Dict con resultados de verificación k-C*
    """
    ref_kw = citar("kadlec_wallace_2009")
    
    Q_m3_d = Q_verificacion_m3_d if Q_verificacion_m3_d is not None else Q.Q_linea_m3_d
    
    # [Ec. V3] Corrección cinética por temperatura
    k_T_m_d = correccion_temperatura(Q.humedal_k_20_m_d, Q.humedal_theta, Q.T_agua_C)
    
    # [Ec. V1, V2] Modelo k-C* para DBO5
    C_star_DBO = Q.humedal_C_fondo_mg_L  # 3.5 mg/L
    q_m_d = Q_m3_d / A_operando_m2  # Carga hidráulica superficial
    
    # Ce = C* + (Ci - C*) × exp(-kA,T / q)
    exponente = -k_T_m_d / q_m_d
    DBO_salida_calc_mg_L = C_star_DBO + (DBO_entrada_mg_L - C_star_DBO) * math.exp(exponente)
    
    # [Ec. V4] Eficiencia de remoción
    eficiencia_DBO_pct = ((DBO_entrada_mg_L - DBO_salida_calc_mg_L) / DBO_entrada_mg_L) * 100
    
    resultado = {
        "k_20_m_d": Q.humedal_k_20_m_d,
        "k_T_m_d": round(k_T_m_d, 4),
        "theta": Q.humedal_theta,
        "T_C": Q.T_agua_C,
        "Q_m3_d": round(Q_m3_d, 1),
        "A_operando_m2": round(A_operando_m2, 1),
        "q_m_d": round(q_m_d, 4),
        "C_star_mg_L": C_star_DBO,
        "DBO_entrada_mg_L": DBO_entrada_mg_L,
        "DBO_salida_calc_mg_L": round(DBO_salida_calc_mg_L, 1),
        "eficiencia_DBO_pct": round(eficiencia_DBO_pct, 1),
        "cumple_objetivo": DBO_salida_calc_mg_L <= Q.humedal_DBO_salida_mg_L,
        "fuente": f"{ref_kw}, Ec. V1-V4"
    }
    
    # Si se proporciona DQO, verificar también
    if DQO_entrada_mg_L is not None:
        C_star_DQO = 17.5  # Promedio 15-20 mg/L según manual
        k_20_DQO = 0.075  # m/d según manual
        k_T_DQO = correccion_temperatura(k_20_DQO, Q.humedal_theta, Q.T_agua_C)
        DQO_salida_calc = C_star_DQO + (DQO_entrada_mg_L - C_star_DQO) * math.exp(-k_T_DQO / q_m_d)
        eficiencia_DQO_pct = ((DQO_entrada_mg_L - DQO_salida_calc) / DQO_entrada_mg_L) * 100
        resultado["DQO_entrada_mg_L"] = DQO_entrada_mg_L
        resultado["DQO_salida_calc_mg_L"] = round(DQO_salida_calc, 1)
        resultado["eficiencia_DQO_pct"] = round(eficiencia_DQO_pct, 1)
    
    return resultado


def dimensionar_humedal_vertical(Q: ConfigDiseno = CFG,
                                  DBO_entrada_mg_L: float = None,
                                  DQO_entrada_mg_L: float = None,
                                  area_disponible_m2: float = None,
                                  forzar_ruta: str = None,
                                  contexto_proyecto: str = "general") -> Dict[str, Any]:
    """
    Dimensionamiento del Humedal Artificial de Flujo Vertical (HAFV).
    
    Metodología Unificada: Sistema Clásico (Ruta A) vs HAFV tropical de alta carga (Ruta B)
    según algoritmo de selección del manual (Sección 3).
    
    PARA SAN CRISTÓBAL (T = 25.6°C, post-UASB):
    → Selecciona automáticamente RUTA B (HAFV tropical de alta carga para pulimiento post-UASB)
    
    Dimensionamiento RUTA B (adaptación basada en Molle et al., 2015):
    ------------------------------------------------
    PASO F1 - Área por Carga Orgánica Superficial (OLR):
        A_operando,OLR = (Q × S₀,DQO) / OLR           [Ec. F1]
        OLR = 200-350 g DQO/m²·d (típico 300)
    
    PASO F2 - Área por Carga Hidráulica Superficial (HLR):
        A_operando,HLR = Q / HLR                      [Ec. F2]
        HLR = 0.50-0.75 m/d
    
    PASO F3 - Selección área operando:
        A_operando = máx(A_OLR, A_HLR)                [Ec. F3]
    
    PASO F4 - Área total sistema:
        A_total = A_operando × N_filtros              [Ec. F4]
        N_filtros = 2 (operación alterna 3.5d/3.5d)
    
    PASO F5/F6 - Verificación por Equivalente Habitante (PE):
        PE_carga = (Q × S₀,DBO) / 60                  [Ec. F5b] (post-UASB)
        A_PE = Área_por_PE × PE_carga                 [Ec. F6]
        Si A_PE > A_total → adoptar A_PE

    Jerarquía metodológica en esta adaptación post-UASB:
        OLR y HLR son los criterios primarios de dimensionamiento.
        PE funciona como contraste empírico de escala/carga y puede aumentar
        el área si resulta más exigente, pero no reemplaza OLR/HLR.
    
    VERIFICACIÓN COMPLEMENTARIA k-C* (Sección 11):
        Ce = C* + (Ci - C*) × exp(-kA,T / q)         [Ec. V2]
        kA,T = kA,20 × θ^(T-20)                      [Ec. V3]
    
    Dimensionamiento RUTA A (Cooper et al., 1996):
    ------------------------------------------------
    Implementado para reusabilidad en climas fríos.
    - 2 etapas con filtros en rotación
    - Criterio COS (20-60 g DBO₅/m²·d)
    
    Referencias
    -----------
    - Molle et al. (2015): adaptación tropical de humedales verticales de alta carga
    - Cooper et al. (1996), ÖNORM B 2505: Sistema Clásico
    - Kadlec & Wallace (2009): Verificación k-C*
    """
    ref_molle = citar("molle_2015")
    ref_cooper = citar("cooper_1996")
    
    # =========================================================================
    # 1. DATOS DE ENTRADA
    # =========================================================================
    if DBO_entrada_mg_L is None:
        DBO_entrada_mg_L = Q.DBO5_mg_L * (1.0 - 0.70)  # ~73 mg/L post-UASB
    
    if DQO_entrada_mg_L is None:
        # Relación DQO/DBO típica post-UASB: 2.0-2.8
        DQO_entrada_mg_L = DBO_entrada_mg_L * 2.4
    
    Q_m3_d = Q.Q_linea_m3_d
    Q_total_m3_d = Q.Q_total_m3_d
    Q_diseno_m3_d = Q_m3_d
    
    # =========================================================================
    # 2. SELECCIÓN DEL SISTEMA (Sección 3 del manual)
    # =========================================================================
    if forzar_ruta:
        seleccion = {
            "ruta": forzar_ruta,
            "sistema": "FRANCES" if forzar_ruta == "B" else "CLASICO",
            "justificacion": f"Ruta {forzar_ruta} forzada por parámetro",
            "trazabilidad": {
                "nota_metodologica": "Ruta forzada por parámetro; no se aplicó selección automática."
            },
        }
    else:
        seleccion = seleccionar_sistema_humedal(
            Q, 
            area_disponible_m2=area_disponible_m2,
            afluente_crudo=False,  # Post-UASB para San Cristóbal
            capacitacion_operador=True,
            restriccion_bioseguridad=False,
            objetivo_NH4_estricto=False,
            contexto_proyecto=contexto_proyecto  # "insular" para San Cristobal
        )
    
    ruta = seleccion["ruta"]
    sistema = seleccion["sistema"]
    
    # =========================================================================
    # 3. DIMENSIONAMIENTO POR RUTA
    # =========================================================================
    
    if ruta == "B" and sistema == "FRANCES":
        # =====================================================================
        # RUTA B: HAFV TROPICAL DE ALTA CARGA (adaptación basada en Molle et al., 2015)
        # =====================================================================
        
        # Parámetros de diseño
        OLR_adoptada = Q.humedal_frances_OLR_gDQO_m2_d  # g DQO/m²·d
        HLR_adoptada = Q.humedal_frances_HLR_m_d        # m/d
        n_filtros = Q.humedal_frances_n_filtros
        
        # PASO F1: Área por OLR [Ec. F1]
        # A_operando,OLR = (Q × S₀,DQO) / OLR
        masa_DQO_g_d = Q_diseno_m3_d * DQO_entrada_mg_L  # mg/L = g/m³
        A_operando_OLR = masa_DQO_g_d / OLR_adoptada    # m²
        
        # PASO F2: Área por HLR [Ec. F2]
        # A_operando,HLR = Q / HLR
        A_operando_HLR = Q_diseno_m3_d / HLR_adoptada    # m²
        
        # PASO F3: Seleccionar área operando [Ec. F3]
        A_operando_m2 = max(A_operando_OLR, A_operando_HLR)
        criterio_controla = "HLR" if A_operando_HLR > A_operando_OLR else "OLR"
        
        # Verificar que OLR resultante no exceda límite si controla HLR
        OLR_real = masa_DQO_g_d / A_operando_m2
        
        # PASO F4: Área total [Ec. F4]
        A_total_m2 = A_operando_m2 * n_filtros
        
        # PASO F5/F6: Verificación por PE [Ec. F5b, F6]
        # PE_carga = (Q × S₀,DBO) / 60  (post-UASB usa carga real, no caudal per cápita)
        masa_DBO_g_d = Q_diseno_m3_d * DBO_entrada_mg_L
        PE_carga = masa_DBO_g_d / 60  # 60 g DBO₅/PE·d
        
        # Seleccionar área por PE según temperatura
        if Q.T_agua_C > 22:
            area_por_PE = Q.humedal_frances_area_por_PE_m2_T22
        else:
            area_por_PE = Q.humedal_frances_area_por_PE_m2_T20
        
        A_PE = area_por_PE * PE_carga
        
        # Si A_PE > A_total, adoptar A_PE
        if A_PE > A_total_m2:
            A_total_adoptado_m2 = A_PE
            A_operando_adoptado_m2 = A_PE / n_filtros
            usado_PE = True
        else:
            A_total_adoptado_m2 = A_total_m2
            A_operando_adoptado_m2 = A_operando_m2
            usado_PE = False
        
        # Dimensiones del filtro
        # Relación L:B = 1:1 a 1.5:1 (adaptación compacta Ruta B)
        relacion_L_A = Q.humedal_frances_relacion_L_A
        ancho_filtro_m = math.sqrt(A_operando_adoptado_m2 / relacion_L_A)
        largo_filtro_m = relacion_L_A * ancho_filtro_m
        
        # Dimensiones totales (considerando 2 filtros en serie - uno tras otro)
        # Layout: celdas en serie en el sentido del flujo (largo), mismo ancho
        separacion_filtros_m = Q.humedal_separacion_filtros_m
        largo_total_m = largo_filtro_m * n_filtros + separacion_filtros_m * (n_filtros - 1)
        ancho_total_m = ancho_filtro_m
        
        # Parámetros operacionales
        ciclo_alim_d = Q.humedal_frances_ciclo_alim_dias
        ciclo_reposo_d = Q.humedal_frances_ciclo_reposo_dias
        
        # TRH real [Ec. G1]
        h_medio = Q.humedal_frances_h_medio_m
        n_p = Q.humedal_n_porosidad
        TRH_d = (A_operando_adoptado_m2 * h_medio * n_p) / Q_diseno_m3_d
        
        # Parámetros para resultado
        resultado_base = {
            "sistema": "HAFV tropical de alta carga",
            "nota_metodologica_ruta": (
                "Ruta B aplicada como adaptación tropical de alta carga para pulimiento post-UASB; "
                "no representa por sí sola el sistema francés canónico completo de dos etapas."
            ),
            "ruta": "B",
            "referencia_principal": ref_molle,
            "criterio_controla": criterio_controla,
            "A_op_OLR_m2": round(A_operando_OLR, 1),
            "A_op_HLR_m2": round(A_operando_HLR, 1),
            "A_operando_m2": round(A_operando_adoptado_m2, 1),
            "A_total_m2": round(A_total_adoptado_m2, 1),
            "n_filtros": n_filtros,
            "dimensiones_por_filtro_m": (round(largo_filtro_m, 1), round(ancho_filtro_m, 1)),
            "largo_total_m": round(largo_total_m, 1),
            "ancho_total_m": round(ancho_total_m, 1),
            "OLR_gDQO_m2_d": round(OLR_real, 1),
            "HLR_m_d": round(Q_diseno_m3_d / A_operando_adoptado_m2, 3),
            "PE_carga": round(PE_carga, 0),
            "A_PE_m2": round(A_PE, 1),
            "usado_criterio_PE": usado_PE,
            "ciclo_dias": f"{ciclo_alim_d}/{ciclo_reposo_d}",
            "ciclo_alim_dias": ciclo_alim_d,
            "ciclo_reposo_dias": ciclo_reposo_d,
            "relacion_L_A": relacion_L_A,
            "separacion_filtros_m": separacion_filtros_m,
            "h_medio_m": h_medio,
            "TRH_dias": round(TRH_d, 2),
        }
        
    else:
        # =====================================================================
        # RUTA A: SISTEMA CLÁSICO (Cooper et al., 1996)
        # =====================================================================
        # Implementación básica para reusabilidad en climas fríos
        
        COS_adoptada = Q.humedal_clasico_COS_gDBO_m2_d  # g DBO₅/m²·d
        
        # Área 1ª etapa por COS [Ec. A1]
        masa_DBO_g_d = Q_diseno_m3_d * DBO_entrada_mg_L
        A_1etapa_COS = masa_DBO_g_d / COS_adoptada
        
        # Área 1ª etapa por PE [Ec. A2]
        PE_carga = masa_DBO_g_d / 60
        A_1etapa_PE = PE_carga * Q.humedal_clasico_area_por_PE_m2
        
        # Adoptar mayor [Ec. A1 vs A2]
        A_1etapa = max(A_1etapa_COS, A_1etapa_PE)
        
        # Área 2ª etapa = 50% de 1ª [Ec. A3]
        A_2etapa = A_1etapa * Q.humedal_clasico_relacion_2da_1ra
        
        # Área total [Ec. A4]
        A_total = A_1etapa + A_2etapa
        
        # Distribución de filtros
        n_filtros_1e = Q.humedal_clasico_n_filtros_1etapa
        n_filtros_2e = Q.humedal_clasico_n_filtros_2etapa
        
        # Geometría
        relacion_L_A = Q.humedal_clasico_relacion_L_A
        ancho_1e = math.sqrt(A_1etapa / n_filtros_1e / relacion_L_A)
        largo_1e = relacion_L_A * ancho_1e
        
        # Dimensiones por filtro (de la primera etapa, que es la más grande)
        dimensiones_por_filtro_m = (round(largo_1e, 1), round(ancho_1e, 1))
        
        # Área por criterio de PE para verificación
        area_por_PE_clasico = Q.humedal_clasico_area_por_PE_m2
        A_PE = 1.5 * area_por_PE_clasico * PE_carga
        
        resultado_base = {
            "sistema": "Clásico",
            "ruta": "A",
            "referencia_principal": ref_cooper,
            "A_1etapa_m2": round(A_1etapa, 1),
            "A_2etapa_m2": round(A_2etapa, 1),
            "A_total_m2": round(A_total, 1),
            "n_filtros_1etapa": n_filtros_1e,
            "n_filtros_2etapa": n_filtros_2e,
            "dimensiones_por_filtro_m": dimensiones_por_filtro_m,
            "PE_carga": round(PE_carga, 0),
            "A_PE_m2": round(A_PE, 1),
            "relacion_L_A": relacion_L_A,
            "separacion_filtros_m": Q.humedal_separacion_filtros_m,
            "h_medio_m": Q.humedal_clasico_h_medio_m,
            "ciclo_alim_1etapa_dias": Q.humedal_clasico_ciclo_alim_1etapa_dias,
            "ciclo_reposo_1etapa_dias": Q.humedal_clasico_ciclo_reposo_1etapa_dias,
            "ciclo_alim_2etapa_dias": Q.humedal_clasico_ciclo_alim_2etapa_dias,
            "ciclo_reposo_2etapa_dias": Q.humedal_clasico_ciclo_reposo_2etapa_dias,
            "COS_gDBO_m2_d": COS_adoptada,
        }
        
        # Para compatibilidad con layout
        A_operando_adoptado_m2 = A_1etapa / n_filtros_1e
        largo_total_m = largo_1e
        ancho_total_m = ancho_1e * n_filtros_1e + Q.humedal_separacion_filtros_m * (n_filtros_1e - 1)
    
    # =========================================================================
    # 4. VERIFICACIÓN k-C* (complementaria/recomendada en ambas rutas)
    # =========================================================================
    verif_kc = verificar_kc_humedal(
        Q, 
        A_operando_adoptado_m2 if ruta == "B" else A_1etapa,
        DBO_entrada_mg_L,
        DQO_entrada_mg_L,
        Q_verificacion_m3_d=Q_diseno_m3_d
    )
    
    # =========================================================================
    # 5. RESULTADO UNIFICADO
    # =========================================================================
    
    # DBO de salida para integración: usar el calculado por verificación k-C*
    # Este es el efluente esperado según modelo cinético (Kadlec & Wallace)
    DBO_salida_mg_L = verif_kc["DBO_salida_calc_mg_L"]
    
    # Compatibilidad: también incluir objetivo de diseño si diferente
    DBO_objetivo_mg_L = Q.humedal_DBO_salida_mg_L
    estado_verificacion_kC = "cumple" if verif_kc["cumple_objetivo"] else "no cumple"
    texto_cumplimiento_kC = (
        f"La DBO5 calculada de {verif_kc['DBO_salida_calc_mg_L']:.1f} mg/L "
        f"{estado_verificacion_kC} con el objetivo de diseño de {DBO_objetivo_mg_L:.1f} mg/L."
    )
    texto_criterio_PE = (
        "se aplicó el criterio de PE como controlante"
        if resultado_base.get("usado_criterio_PE", False)
        else "no se aplicó el criterio de PE como controlante"
    )
    nota_metodologia_area = (
        "En esta adaptacion post-UASB, el dimensionamiento primario se realiza por OLR y HLR. "
        "El criterio de PE se usa como contraste empirico de escala/carga y puede aumentar el area "
        "si resulta mas exigente, pero no reemplaza los criterios de carga organica e hidraulica."
    )
    capas_medio_filtrante = [
        {"espesor_m": Q.humedal_capa_drenaje_m, "nombre": "Grava drenaje (20-60 mm)"},
        {"espesor_m": Q.humedal_capa_grava_media_m, "nombre": "Grava media (5-15 mm)"},
        {"espesor_m": Q.humedal_capa_grava_fina_m, "nombre": "Grava fina (2-6 mm)"},
    ]
    h_medio_resultado = Q.humedal_frances_h_medio_m if ruta == "B" else Q.humedal_clasico_h_medio_m
    H_total_resultado = Q.humedal_frances_H_total_m if ruta == "B" else Q.humedal_clasico_H_total_m
    metodologia_descriptiva = f"{resultado_base['sistema']} (Ruta {ruta})"
    altura_sobre_lecho_m = max(H_total_resultado - h_medio_resultado, 0.0)
    if ruta == "B":
        nota_estratigrafia_medio = (
            "Estratigrafía adoptada para HAFV tropical de alta carga post-UASB; "
            "no pretende reproducir literalmente una celda francesa canónica de dos etapas "
            "ni el caso específico Hoffmann/Chincha."
        )
        texto_interpretacion_criterio_resultados = (
            "El criterio controlante es hidráulico: el tiempo de contacto entre el agua residual "
            "y la biopelícula es el parámetro que acota el rendimiento, mientras que la carga "
            "orgánica real sobre la celda activa permanece por debajo del límite máximo adoptado."
            if criterio_controla == "HLR"
            else
            "El criterio controlante es orgánico: la capacidad de degradación de la biopelícula "
            "es el factor que determina el área, mientras que la carga hidráulica resultante se "
            "mantiene dentro del rango admisible para el sistema seleccionado."
        )
        campos_render = {
            "criterio_resultados": criterio_controla,
            "A_operando_resultados_m2": round(A_operando_adoptado_m2, 1),
            "n_filtros_resultados": n_filtros,
            "ciclo_resultados": f"{ciclo_alim_d}/{ciclo_reposo_d}",
            "ciclo_alim_resultados_dias": ciclo_alim_d,
            "ciclo_reposo_resultados_dias": ciclo_reposo_d,
            "carga_organica_resultados_etiqueta": "OLR real",
            "carga_organica_resultados_valor": round(OLR_real, 1),
            "carga_organica_resultados_unidad": "g DQO/m²·d",
            "HLR_resultados_m_d": round(Q_diseno_m3_d / A_operando_adoptado_m2, 3),
        }
    else:
        nota_estratigrafia_medio = (
            "Estratigrafía adoptada para la ruta clásica del HAFV; "
            "se documenta como configuración del medio filtrante de esta metodología."
        )
        texto_interpretacion_criterio_resultados = (
            "El dimensionamiento de la ruta clásica queda gobernado por los criterios "
            "combinados de carga orgánica superficial y contraste por habitante equivalente, "
            "propios de la configuración en dos etapas."
        )
        COS_real = masa_DBO_g_d / A_1etapa
        campos_render = {
            "criterio_resultados": "COS/PE",
            "A_operando_resultados_m2": round(A_1etapa, 1),
            "n_filtros_resultados": n_filtros_1e,
            "ciclo_resultados": f"{Q.humedal_clasico_ciclo_alim_1etapa_dias}/{Q.humedal_clasico_ciclo_reposo_1etapa_dias}",
            "ciclo_alim_resultados_dias": Q.humedal_clasico_ciclo_alim_1etapa_dias,
            "ciclo_reposo_resultados_dias": Q.humedal_clasico_ciclo_reposo_1etapa_dias,
            "carga_organica_resultados_etiqueta": "COS real",
            "carga_organica_resultados_valor": round(COS_real, 1),
            "carga_organica_resultados_unidad": "g DBO5/m²·d",
            "HLR_resultados_m_d": round(Q_diseno_m3_d / A_1etapa, 3),
        }
    estados_filtros_esquema = [
        {
            "indice": i + 1,
            "estado": "ALIMENTANDO" if i == 0 else "REPOSO",
            "duracion_dias": (
                campos_render["ciclo_alim_resultados_dias"]
                if i == 0
                else campos_render["ciclo_reposo_resultados_dias"]
            ),
        }
        for i in range(campos_render["n_filtros_resultados"])
    ]
    texto_operacion_alternada = (
        f"El esquema representa un ciclo operativo con 1 filtro en alimentacion durante "
        f"{campos_render['ciclo_alim_resultados_dias']:.1f} dias y "
        f"{max(campos_render['n_filtros_resultados'] - 1, 0)} filtro(s) en reposo durante "
        f"{campos_render['ciclo_reposo_resultados_dias']:.1f} dias. "
        "La rotacion distribuye el desgaste entre unidades y permite la recuperacion aerobia del medio filtrante."
    )
    texto_operacion_figura = (
        f"Operacion alternada: {campos_render['ciclo_alim_resultados_dias']:.1f} dias alimentando / "
        f"{campos_render['ciclo_reposo_resultados_dias']:.1f} dias reposo"
    )
    
    return {
        "unidad": "Humedal Artificial Flujo Vertical (HAFV)",
        "metodologia": metodologia_descriptiva,
        "justificacion_seleccion": seleccion["justificacion"],
        "seleccion_sistema": seleccion,
        "nota_metodologica_seleccion": seleccion["trazabilidad"]["nota_metodologica"],
        "texto_criterio_PE": texto_criterio_PE,
        "nota_metodologia_area": nota_metodologia_area,
        **resultado_base,
        **campos_render,
        # Verificación cinética (modelo k-C* completo)
        "verificacion_kC": verif_kc,
        "estado_verificacion_kC": estado_verificacion_kC,
        "texto_cumplimiento_kC": texto_cumplimiento_kC,
        # DBO de salida (CRÍTICO para integración con resto del proyecto)
        "DBO_salida_mg_L": DBO_salida_mg_L,           # Calculado por k-C* (efluente esperado)
        "DBO_objetivo_mg_L": DBO_objetivo_mg_L,       # Objetivo de diseño original
        # Datos de entrada
        "DBO_entrada_mg_L": round(DBO_entrada_mg_L, 1),
        "DQO_entrada_mg_L": round(DQO_entrada_mg_L, 1),
        "Q_m3_d": round(Q_diseno_m3_d, 1),
        "Q_linea_m3_d": round(Q_m3_d, 1),
        "Q_total_sistema_m3_d": round(Q_total_m3_d, 1),
        "num_lineas": Q.num_lineas,
        "T_agua_C": Q.T_agua_C,
        # Parámetros de diseño
        "k_20_m_d": Q.humedal_k_20_m_d,
        "theta": Q.humedal_theta,
        "n_porosidad": Q.humedal_n_porosidad,
        "h_lecho_m": h_medio_resultado,
        "capas_medio_filtrante": capas_medio_filtrante,
        "nota_estratigrafia_medio": nota_estratigrafia_medio,
        "texto_interpretacion_criterio_resultados": texto_interpretacion_criterio_resultados,
        "estados_filtros_esquema": estados_filtros_esquema,
        "texto_operacion_alternada": texto_operacion_alternada,
        "texto_operacion_figura": texto_operacion_figura,
        # Para layout (compatibilidad con ptar_layout_graficador.py)
        "largo_layout_m": round(largo_total_m, 1),
        "ancho_layout_m": round(ancho_total_m, 1),
        "A_sup_m2": round(A_total_adoptado_m2 if ruta == "B" else A_total, 1),
        "A_diseño_m2": round(A_total_adoptado_m2 if ruta == "B" else A_total, 1),
        "A_total_sistema_m2": round((A_total_adoptado_m2 if ruta == "B" else A_total) * Q.num_lineas, 1),
        "largo_m": round(largo_total_m, 1),
        "ancho_m": round(ancho_total_m, 1),
        "H_total_m": H_total_resultado,
        "altura_sobre_lecho_m": round(altura_sobre_lecho_m, 2),
        # Datos específicos para referencias
        "fuente": f"{ref_molle if ruta == 'B' else ref_cooper}; Kadlec & Wallace (2009) para verificación k-C*",
        # Subproductos - estructura normalizada
        "subproductos": {
            "lodos": [],  # No hay purga diaria de lodos al lecho en el dimensionamiento
            "retenciones": [
                {
                    "origen": "Humedal Vertical",
                    "tipo": "solidos retenidos/acumulados en el medio filtrante",
                    "kg_d": None,
                    "base_solidos": "SST",
                    "kg_SST_d": None,
                    "kg_SSV_d": None,
                    "m3_d": None,
                    "concentracion_kg_m3": None,
                    "estado_fisico": "acumulado_en_medio_filtrante",
                    "destino": "mantenimiento_periodico_humedal",
                    "apto_lecho_directo": False,
                    "nota": "El humedal retiene solidos en el medio filtrante durante la operacion; "
                            "no se considera una purga diaria hacia el lecho de secado en el "
                            "dimensionamiento actual. Requiere mantenimiento periodico del lecho."
                }
            ],
            "transferencias": [],
            "biogas": [],
            "residuos_gruesos": [],
            "arenas": []
        },
    }


# =============================================================================
# 6 - SEDIMENTADOR SECUNDARIO CIRCULAR
# =============================================================================

def dimensionar_sedimentador_sec(Q: ConfigDiseno = CFG,
                                  DBO_entrada_mg_L: float = None,
                                  solidos_biologicos_entrada_kg_d: float = None,
                                  DBO_removida_fp_kg_d: float = None) -> Dict[str, Any]:
    """
    Dimensionamiento del sedimentador secundario circular (clarificador).

    El sedimentador secundario separa los solidos biologicos desprendidos 
    de una etapa biologica aerobia (filtro percolador, MBBR, biofiltro, etc.)
    del efluente tratado. Es una unidad de post-tratamiento reusable para
    cualquier proceso de biopelicula que genere humus o lodos biologicos.

    Criterio de diseño
    ------------------
    Tasa de desbordamiento superficial (SOR):
        SOR = Q / A_sup                                     [Ec. 7a]
        Rango operativo: 16-32 m^3/m^2*d                     [Metcalf & Eddy, 2014, Tabla 9-35]
        SOR de diseño se toma desde configuración (default: 18 m³/m²·d)

    Área superficial:
        A_sup = Q / SOR                                     [Ec. 7b]

    Diámetro:
        D = √(4 * A_sup / π)                               [Ec. 7c]

    Tiempo de retención hidráulico:
        TRH = V / Q = A_sup * h_sed / Q                    [Ec. 7d]
        Mínimo 1.5 h para sedimentadores secundarios posteriores a procesos biológicos aerobios.

    Autoajuste iterativo:
        Si SOR_max (a caudal pico) excede el límite de 45 m³/m²·d,
        se reduce SOR en pasos del 2% (aumentando área) intentando
        alcanzar un margen de seguridad del 10%. El ajuste está 
        acotado inferiormente por 16.0 m³/m²·d (mínimo operativo), 
        por lo que el margen del 10% no siempre es alcanzable.

    Referencias
    -----------
    Metcalf & Eddy (2014), pp. 870-880
    WEF MOP-8 (2010), pp. 9-60 a 9-72
    """
    ref_me = citar("metcalf_2014")
    ref_wef = citar("wef_mop8_2010")
    ref_sp = citar("sperling_2007")

    # Parámetros de diseño adoptados desde configuración
    SOR_m3_m2_d = Q.sed_SOR_m3_m2_d  # desde configuración (default: 18.0 m³/m²·d)
    # Rango operativo: 16-32 m³/m²·d. El autoajuste no permite bajar de 16.0
    h_sed_m = Q.sed_h_sed_m
    factor_pico = Q.factor_pico_Qmax  # Factor desde configuración
    factor_min = Q.sed_factor_min_Q  # Caudal mínimo desde configuración

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
    SOR_max_limite = Q.sed_SOR_max_limite_m3_m2_d
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
        
        # Reducimos SOR (aumentamos área) en 2%, pero no bajamos de 16.0 (límite inferior del rango operativo)
        SOR_m3_m2_d = max(SOR_m3_m2_d * 0.98, Q.sed_SOR_min_m3_m2_d)
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
    weir_loading_max = Q.sed_weir_loading_max_m3_m_d  # límite según Metcalf & Eddy
    
    # Tasa de aplicación de solidos biologicos (humus de etapa biologica aerobia)
    # Produccion tipica: ~0.15 kg SST/kg DBO removida en proceso aerobio
    factor_produccion_humus = Q.sed_factor_produccion_humus  # kg SST/kg DBO removida
    
    # Produccion de solidos biologicos - entrada generica para reusabilidad
    # Se acepta tanto el nuevo parametro (solidos_biologicos_entrada_kg_d) como
    # el antiguo (DBO_removida_fp_kg_d) para mantener compatibilidad hacia atras
    if solidos_biologicos_entrada_kg_d is not None:
        produccion_humus_kg_d = solidos_biologicos_entrada_kg_d
    elif DBO_removida_fp_kg_d is not None:
        # Compatibilidad hacia atras con codigo existente
        produccion_humus_kg_d = factor_produccion_humus * DBO_removida_fp_kg_d
    else:
        raise ValueError("solidos_biologicos_entrada_kg_d (o DBO_removida_fp_kg_d para compatibilidad) es requerida para dimensionar el sedimentador")
    
    solids_loading_kg_m2_d = produccion_humus_kg_d / A_sup_m2
    
    # Cálculo de DBO de salida (para balance de calidad en LaTeX)
    # El sedimentador remueve SST biológicos (humus) que representan ~30% de la DBO restante
    eta_DBO_sed = Q.sed_eta_DBO  # fracción remoción DBO por separación de humus
    if DBO_entrada_mg_L is None:
        raise ValueError("DBO_entrada_mg_L es requerida para calcular la DBO de salida del sedimentador")
    DBO_salida_mg_L = DBO_entrada_mg_L * (1 - eta_DBO_sed)
    solids_loading_limite = Q.sed_solids_loading_limite_kg_m2_d  # kg/m²·d
    
    # Verificaciones finales
    # Verificación final: SOR debe estar dentro del rango operativo documentado 16-32 m³/m²·d
    assert Q.sed_SOR_min_m3_m2_d <= SOR_m3_m2_d <= Q.sed_SOR_max_m3_m2_d, (
        f"SOR = {SOR_m3_m2_d} m^3/m^2*d fuera de rango {Q.sed_SOR_min_m3_m2_d}-{Q.sed_SOR_max_m3_m2_d} ({ref_me}, Tabla 9-35)"
    )
    assert TRH_h >= Q.sed_TRH_min_h, (
        f"TRH = {TRH_h:.1f} h < {Q.sed_TRH_min_h:.1f} h mínimo ({ref_me}, p. 872)"
    )
    assert weir_loading_m3_m_d <= weir_loading_max, (
        f"Weir loading = {weir_loading_m3_m_d:.1f} m³/m·d > {weir_loading_max} límite"
    )
    
    # Texto de verificación
    if SOR_max_m3_m2_d <= SOR_max_limite:
        verif_sor_max_texto = f"la tasa de desbordamiento máxima ({SOR_max_m3_m2_d:.1f} m³/m²·d) está dentro del rango operativo seguro ($\\leq$ {SOR_max_limite:.0f} m³/m²·d) con un margen del {margen_seguridad_pct:.1f}%"
    else:
        verif_sor_max_texto = f"la tasa de desbordamiento máxima ({SOR_max_m3_m2_d:.1f} m³/m²·d) excede el límite recomendado ({SOR_max_limite:.0f} m³/m²·d), se recomienda duplicar unidades"

    estado_sor_max = "Cumple" if SOR_max_m3_m2_d <= SOR_max_limite else "No cumple"
    texto_sor_max_verificacion = (
        f"{verif_sor_max_texto}. El margen de seguridad respecto al límite de "
        f"{SOR_max_limite:.0f} m³/m²·d es del {margen_seguridad_pct:.1f} por ciento. "
        "Según Metcalf & Eddy (2014), mantener el SOR máximo por debajo del límite "
        "asegura que la sedimentación no se vea afectada por las condiciones de pico, "
        "preservando la calidad del efluente."
    )

    estado_weir_loading = "Cumple" if weir_loading_m3_m_d <= weir_loading_max else "No cumple"
    texto_weir_loading = (
        f"La carga calculada de {weir_loading_m3_m_d:.1f} m³/m·d se compara contra el "
        f"límite establecido por Metcalf & Eddy de {weir_loading_max:.0f} m³/m·d para "
        "sedimentadores secundarios. Este límite surge de la necesidad de mantener "
        "velocidades de aproximación al vertedero suficientemente bajas que no arrastren "
        "los sólidos ya sedimentados hacia el efluente. Con la carga calculada, el estado "
        f"de la verificación es {estado_weir_loading}."
    )

    estado_solids_loading = "Cumple" if solids_loading_kg_m2_d <= solids_loading_limite else "No cumple"
    texto_solids_loading = (
        f"La tasa de aplicación de sólidos calculada de {solids_loading_kg_m2_d:.2f} "
        f"kg SST/m²·d se compara contra el límite conservador de {solids_loading_limite:.0f} "
        "kg SST/m²·d adoptado para este diseño, basado en criterios de Metcalf & Eddy "
        "para sedimentadores secundarios después de procesos biológicos aerobios. "
        f"El rango operativo típico de referencia es {Q.sed_solids_loading_tipico_min_kg_m2_d:.0f}--"
        f"{Q.sed_solids_loading_tipico_max_kg_m2_d:.0f} kg SST/m²·d. "
        f"El estado de la verificación es {estado_solids_loading}."
    )

    estado_trh_min = "Aceptable" if TRH_min_h <= Q.sed_TRH_min_operacion_alerta_h else "Requiere monitoreo operativo"
    if TRH_min_h <= Q.sed_TRH_min_operacion_alerta_h:
        texto_trh_min = "Este valor es aceptable para operación normal."
    else:
        texto_trh_min = (
            f"Este valor excede {Q.sed_TRH_min_operacion_alerta_h:.1f} horas, por lo que se "
            "recomienda monitorear la operación para evitar condiciones sépticas."
        )

    nota_operacion_caudal_minimo = (
        f"El HRT de {TRH_min_h:.1f} h a caudal mínimo puede favorecer condiciones sépticas "
        "en el fondo del sedimentador si la operación no se controla. Se recomiendan las "
        "siguientes medidas operativas: (1) mantener una recirculación interna del efluente "
        "clarificado hacia la entrada del sedimentador para mantener la turbulencia y prevenir "
        "la putrefacción de lodos; (2) instalar un sistema de control de nivel que permita "
        "operar con tirante variable, reduciendo el volumen almacenado en horas de bajo caudal; "
        f"(3) programar purgas periódicas de lodos acumulados en la tolva, mínimo cada "
        f"{Q.sed_purga_lodos_min_h:.0f} horas. Estas medidas deberán detallarse en la "
        "ingeniería de detalle del proyecto."
    )

    altura_total_construccion_m = h_sed_m + Q.sed_h_lodos_tolva_m + Q.sed_bordo_libre_m

    return {
        "unidad": "Sedimentador secundario circular",
        "Q_m3_d": round(Q_m3_d, 1),
        "Q_max_m3_d": round(Q_max_m3_d, 1),
        "Q_min_m3_d": round(Q_min_m3_d, 1),
        "factor_pico": factor_pico,
        "factor_min": factor_min,
        "SOR_m3_m2_d": round(SOR_m3_m2_d, 1),
        "SOR_min_m3_m2_d": Q.sed_SOR_min_m3_m2_d,
        "SOR_max_rango_m3_m2_d": Q.sed_SOR_max_m3_m2_d,
        "SOR_max_m3_m2_d": round(SOR_max_m3_m2_d, 1),
        "SOR_max_limite": SOR_max_limite,
        "estado_sor_max": estado_sor_max,
        "texto_sor_max_verificacion": texto_sor_max_verificacion,
        "margen_seguridad_pct": round(margen_seguridad_pct, 1),
        "A_sup_m2": round(A_sup_m2, 2),
        "D_m": round(D_m, 2),
        "perimetro_m": round(perimetro_m, 2),
        "h_sed_m": h_sed_m,
        "h_sed_min_m": Q.sed_h_sed_min_m,
        "h_sed_max_m": Q.sed_h_sed_max_m,
        "h_lodos_tolva_m": Q.sed_h_lodos_tolva_m,
        "bordo_libre_m": Q.sed_bordo_libre_m,
        "altura_total_construccion_m": round(altura_total_construccion_m, 2),
        "V_m3": round(V_m3, 1),
        "TRH_h": round(TRH_h, 1),
        "TRH_min_criterio_h": Q.sed_TRH_min_h,
        "TRH_max_h": round(TRH_max_h, 1),
        "TRH_min_h": round(TRH_min_h, 1),
        "TRH_min_operacion_alerta_h": Q.sed_TRH_min_operacion_alerta_h,
        "estado_trh_min": estado_trh_min,
        "texto_trh_min": texto_trh_min,
        "nota_operacion_caudal_minimo": nota_operacion_caudal_minimo,
        "weir_loading_m3_m_d": round(weir_loading_m3_m_d, 1),
        "weir_loading_max": weir_loading_max,
        "estado_weir_loading": estado_weir_loading,
        "texto_weir_loading": texto_weir_loading,
        "solids_loading_kg_m2_d": round(solids_loading_kg_m2_d, 2),
        "solids_loading_limite": solids_loading_limite,
        "solids_loading_tipico_min": Q.sed_solids_loading_tipico_min_kg_m2_d,
        "solids_loading_tipico_max": Q.sed_solids_loading_tipico_max_kg_m2_d,
        "estado_solids_loading": estado_solids_loading,
        "texto_solids_loading": texto_solids_loading,
        "produccion_humus_kg_d": round(produccion_humus_kg_d, 2),
        "factor_produccion_humus": factor_produccion_humus,
        # Subproductos - estructura normalizada
        "subproductos": {
            "lodos": [
                {
                    "origen": "Sedimentador Secundario",
                    "tipo": "humus sedimentado / lodo biologico",
                    "kg_d": round(produccion_humus_kg_d, 2),
                    "base_solidos": "SST",
                    "kg_SST_d": round(produccion_humus_kg_d, 2),
                    "kg_SSV_d": None,
                    "m3_d": None,
                    "concentracion_kg_m3": None,
                    "estado_fisico": "sedimentado_en_tolva",
                    "destino": "lecho_secado",
                    "apto_lecho_directo": True,
                    "nota": "Solidos biologicos separados en el sedimentador secundario; "
                            "se envian al lecho de secado como lodo/humus sedimentado."
                }
            ],
            "transferencias": [],
            "biogas": [],
            "residuos_gruesos": [],
            "arenas": []
        },
        "DBO_entrada_mg_L": round(DBO_entrada_mg_L, 1) if DBO_entrada_mg_L else None,
        "DBO_salida_mg_L": round(DBO_salida_mg_L, 1),
        "eta_DBO_sed": eta_DBO_sed,
        "ajuste_realizado": ajuste_realizado,
        "verif_sor_max_texto": verif_sor_max_texto,
        "diametro_layout_m": round(D_m, 2),
        "fuente": f"{ref_me} (pp. 870-880); {ref_wef} (pp. 9-60); {ref_sp}",
    }


# =============================================================================
# 7 - DESINFECCIÓN CON CLORO (HIPOCLORITO)
# =============================================================================

def dimensionar_desinfeccion_cloro(Q: ConfigDiseno = CFG,
                                    CF_entrada_NMP: float = None,
                                    CF_objetivo_NMP: float = None) -> Dict[str, Any]:
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
    
    Log reducción requerida para cumplir objetivo:
        Log_red_req = log10(CF_entrada / CF_objetivo)        [Ec. 7g']
    
    CT requerido para lograr la reducción:
        CT_req = Log_red_req / k                             [Ec. 7h']
        donde k = coeficiente de log-reducción (log/CT)
    
    Filosofía de diseño adoptada (Opción A - residual fijo, TRH variable):
        - Se fija un cloro residual objetivo (por criterio operativo/normativo)
        - Se calcula el TRH necesario para alcanzar el CT requerido
        - Si el TRH calculado excede límites prácticos, se ajusta y se verifica cumplimiento
    
    Log reducción típica de coliformes:
        CT = 5-10 mg.min/L   -> 2-3 log  (99-99.9%)
        CT = 10-20 mg.min/L  -> 3-4 log  (99.9-99.99%)
        CT = 20-40 mg.min/L  -> 4-5 log  (99.99-99.999%)
    
    Estimación práctica:
        Log reducción ≈ k × CT (coeficiente k desde configuración)
    
    Criterios de diseño
    -------------------
    - CF objetivo: definido por requisito de vertimiento (ej. TULSMA: 3000 NMP/100mL)
    - Dosis de cloro: demanda + residual = dosis total
    - Cloro residual: 0.5-2.0 mg/L (fijado por monitoreo operativo)
    - Tiempo de contacto: resultado del cálculo basado en CT requerido
    - CT: calculado desde reducción logarítmica requerida
    
    Ecuaciones de dimensionamiento
    ------------------------------
    Log reducción requerida:
        Log_red_req = log10(CF_entrada / CF_objetivo)        [Ec. 7g']
    
    CT requerido:
        CT_req = Log_red_req / k                             [Ec. 7h']
    
    TRH requerido (con residual fijo):
        TRH_req = CT_req / C_residual                        [Ec. 7i']
    
    Volumen del tanque de contacto:
        V = Q × t                                            [Ec. 7j]
    
    CT calculado (verificación):
        CT = C_residual × t                                  [Ec. 7k]
    
    Log reducción estimada:
        Log_red ≈ k × CT                                     [Ec. 7l]
    
    Coliformes finales:
        CF_final = CF_inicial / 10^Log_red                   [Ec. 7m]
    
    Referencias
    -----------
    Metcalf & Eddy (2014), pp. 1200-1220
    USEPA (2003) - LT1ESWTR Disinfection Profiling and Benchmarking
    OPS/CEPIS (2005) - Guía de desinfección
    """
    ref_me = citar("metcalf_2014")
    ref_epa = "USEPA (2003)"
    ref_ops = citar("ops_cepis_2005")
    
    # =========================================================================
    # PARÁMETROS DE DISEÑO BASADO EN OBJETIVO DE CF
    # =========================================================================
    
    # Coliformes de entrada - requerido para cálculo encadenado
    if CF_entrada_NMP is None:
        raise ValueError("CF_entrada_NMP es requerida para dimensionar la desinfección (cálculo encadenado)")
    
    # CF objetivo de diseño - puede pasarse explícito o tomar de configuración
    if CF_objetivo_NMP is None:
        CF_objetivo_NMP = Q.desinfeccion_CF_objetivo_NMP
    
    # Coeficiente de log-reducción (k): log reducidos por unidad de CT
    k_log_red = Q.desinfeccion_coef_log_red  # log/(mg·min/L)
    
    # Filosofía de diseño: RESIDUAL FIJO + TRH VARIABLE (Opción A)
    # El residual se fija por criterio operativo/normativo
    # El TRH se calcula para alcanzar el CT requerido
    
    # Demanda de cloro (insumo del efluente)
    demanda_cloro_mg_L = Q.desinfeccion_demanda_cloro_mg_L   # mg/L (consumido por amoníaco y MO)
    
    # Residual mínimo operativo (criterio de monitoreo/fiscalización)
    residual_minimo_operativo = Q.desinfeccion_cloro_residual_mg_L  # mg/L
    
    # TRH base de configuración (para iniciar dimensionamiento)
    TRH_base_config = Q.desinfeccion_TRH_min  # min
    
    # Caudales
    Q_m3_d = Q.Q_linea_m3_d
    Q_m3_h = Q.Q_linea_m3_h
    Q_m3_min = Q_m3_h / 60.0        # m³/min
    
    # =========================================================================
    # CÁLCULO DEL CT REQUERIDO PARA CUMPLIR CF OBJETIVO
    # =========================================================================
    
    # [Ec. 7g'] Log reducción requerida para alcanzar CF objetivo
    # Log_red_req = log10(CF_entrada / CF_objetivo)
    # Si el efluente ya cumple el objetivo, la reducción requerida es cero.
    log_reduccion_requerida = max(0.0, math.log10(CF_entrada_NMP / CF_objetivo_NMP))
    
    # [Ec. 7h'] CT requerido para lograr la reducción necesaria
    # CT_req = Log_red_req / k
    CT_requerido = log_reduccion_requerida / k_log_red  # mg·min/L
    
    # =========================================================================
    # DIMENSIONAMIENTO DEL TANQUE DE CONTACTO (base: TRH configurado)
    # =========================================================================
    
    # Parámetros geométricos
    relacion_L_A = Q.desinfeccion_relacion_L_A        # Relación largo/ancho
    h_tanque_m = Q.desinfeccion_h_tanque_m            # m (profundidad)
    borde_libre_m = Q.desinfeccion_borde_libre_m
    n_canales_serpentin = max(2, int(Q.desinfeccion_n_canales_serpentin))
    ancho_canal_min_m = Q.desinfeccion_ancho_canal_min_m
    espesor_bafle_m = Q.desinfeccion_espesor_bafle_m
    relacion_recorrido_ancho_min = Q.desinfeccion_relacion_recorrido_ancho_min
    
    # [Ec. 7i] Volumen del tanque de contacto basado en TRH base de config
    V_contacto_m3 = Q_m3_min * TRH_base_config  # m³
    
    # Dimensiones del tanque
    V_contacto_min_m3 = V_contacto_m3
    A_superficial_min_m2 = V_contacto_min_m3 / h_tanque_m
    coef_b = relacion_recorrido_ancho_min * (n_canales_serpentin - 1) * espesor_bafle_m / n_canales_serpentin
    ancho_canal_teorico_m = (-coef_b + math.sqrt(coef_b ** 2 + 4 * relacion_recorrido_ancho_min * A_superficial_min_m2)) / (2 * relacion_recorrido_ancho_min)
    ancho_canal_m = max(ancho_canal_teorico_m, ancho_canal_min_m)
    largo_canal_m = relacion_recorrido_ancho_min * ancho_canal_m / n_canales_serpentin
    ancho_total_m = n_canales_serpentin * ancho_canal_m + (n_canales_serpentin - 1) * espesor_bafle_m
    largo_m = largo_canal_m
    ancho_m = ancho_total_m
    longitud_recorrido_m = n_canales_serpentin * largo_canal_m
    relacion_recorrido_ancho = longitud_recorrido_m / ancho_canal_m
    A_superficial_m2 = largo_m * ancho_m
    V_contacto_m3 = A_superficial_m2 * h_tanque_m
    TRH_real_min = V_contacto_m3 / Q_m3_min  # TRH real con dimensiones adoptadas
    
    # =========================================================================
    # CÁLCULO DEL RESIDUAL REQUERIDO Y ADOPTADO (coherente con TRH real)
    # =========================================================================
    
    # [Ec. 7j'] Residual requerido para alcanzar CT_requerido con TRH_real
    # C_req = CT_req / TRH_real
    residual_requerido = CT_requerido / TRH_real_min  # mg/L
    residual_requerido = max(0.0, residual_requerido)  # El residual no puede ser negativo
    
    # Residual adoptado: el máximo entre el requerido y el mínimo operativo normativo.
    # Garantiza que siempre haya un residual mensurable para desinfección y monitoreo.
    residual_adoptado = max(residual_requerido, residual_minimo_operativo)
    
    # Ajuste automático: si el CT real queda por debajo del mínimo recomendado,
    # se incrementa el residual adoptado para alcanzar CT_min sin sobredimensionar el tanque.
    CT_min_recomendado = Q.desinfeccion_CT_min_recomendado_mg_min_L
    CT_real_preliminar = residual_adoptado * TRH_real_min
    if CT_real_preliminar < CT_min_recomendado:
        residual_adoptado = max(residual_adoptado, CT_min_recomendado / TRH_real_min)
    
    # Indicador si el residual queda por debajo del mínimo operativo recomendado
    residual_por_debajo_minimo = (residual_requerido < residual_minimo_operativo)
    
    # [Ec. 7k'] CT real con el residual adoptado y TRH real
    CT_real = residual_adoptado * TRH_real_min  # mg·min/L
    
    # Dosis total de cloro
    dosis_cloro_mg_L = demanda_cloro_mg_L + residual_adoptado  # mg/L
    
    # =========================================================================
    # VERIFICACIÓN DE LA REDUCCIÓN LOGARÍTMICA ALCANZADA
    # =========================================================================
    
    # [Ec. 7l] Log reducción estimada con el CT real
    log_reduccion = k_log_red * CT_real
    
    # [Ec. 7m] Coliformes finales estimados
    CF_final_NMP = CF_entrada_NMP / (10 ** log_reduccion)
    
    # Porcentaje de reducción
    pct_reduccion = (1 - CF_final_NMP / CF_entrada_NMP) * 100
    
    # Verificación de cumplimiento TULSMA (CF ≤ límite configurado)
    limite_TULSMA_CF_NMP = Q.desinfeccion_limite_TULSMA_CF_NMP
    cumple_TULSMA = CF_final_NMP <= limite_TULSMA_CF_NMP
    
    # Verificación CT mínimo recomendado
    CT_min_recomendado = Q.desinfeccion_CT_min_recomendado_mg_min_L  # mg·min/L
    CT_aceptable = CT_real >= CT_min_recomendado
    
    # Textos de verificación para módulo LaTeX
    if cumple_TULSMA:
        verif_TULSMA_texto = f"Cumple con el límite de TULSMA (CF final = {CF_final_NMP:.0f} NMP/100mL $≤$ {limite_TULSMA_CF_NMP:.0f} NMP/100mL)."
        estado_TULSMA = "Cumple"
    else:
        verif_TULSMA_texto = f"No cumple con el límite de TULSMA (CF final = {CF_final_NMP:.0f} NMP/100mL > {limite_TULSMA_CF_NMP:.0f} NMP/100mL). Se recomienda aumentar el CT o revisar el sistema."
        estado_TULSMA = "No cumple"
    
    if CT_aceptable:
        verif_CT_texto = f"El valor CT real ({CT_real:.1f} mg$⋅$min/L) supera el mínimo recomendado de {CT_min_recomendado:.0f} mg$⋅$min/L."
        estado_CT = "Cumple"
    else:
        verif_CT_texto = f"El valor CT real ({CT_real:.1f} mg$⋅$min/L) está por debajo del mínimo recomendado de {CT_min_recomendado:.0f} mg$⋅$min/L."
        estado_CT = "No cumple"

    estado_camara_contacto = "Cumple" if relacion_recorrido_ancho >= relacion_recorrido_ancho_min else "No cumple"
    texto_camara_contacto = (
        f"La camara de contacto se configura como culebrin con {n_canales_serpentin} pasos "
        f"hidraulicos, ancho de canal de {ancho_canal_m:.2f} m y recorrido total de "
        f"{longitud_recorrido_m:.1f} m. La relacion recorrido/ancho es "
        f"{relacion_recorrido_ancho:.1f}:1, frente al criterio minimo adoptado de "
        f"{relacion_recorrido_ancho_min:.0f}:1 para aproximar flujo piston y reducir "
        f"cortocircuitos hidraulicos. El estado de la verificacion es {estado_camara_contacto}."
    )
    texto_volumen_contacto = (
        f"El volumen minimo por tiempo de contacto es {V_contacto_min_m3:.1f} m3; "
        f"la geometria serpentina adoptada entrega {V_contacto_m3:.1f} m3 y un tiempo "
        f"hidraulico teorico de {TRH_real_min:.1f} min."
    )
    
    # Consumo de cloro (como Cl₂ activo)
    consumo_cloro_kg_d = (dosis_cloro_mg_L * Q_m3_d) / 1000  # kg Cl₂/d
    
    # Conversión a hipoclorito de sodio comercial (NaOCl al 10-12.5%)
    # Fórmula: m_NaOCl = m_Cl2 / [% NaOCl]
    concentracion_NaOCl = Q.desinfeccion_concentracion_NaOCl  # fracción
    consumo_NaOCl_kg_d = consumo_cloro_kg_d / concentracion_NaOCl  # kg NaOCl/d
    
    # Volumen de NaOCl (densidad desde configuración)
    densidad_NaOCl = Q.desinfeccion_densidad_NaOCl  # kg/L
    volumen_NaOCl_L_d = consumo_NaOCl_kg_d / densidad_NaOCl  # L/d
    volumen_NaOCl_L_mes = volumen_NaOCl_L_d * Q.desinfeccion_almacenamiento_dias  # L/periodo
    
    # Volumen de almacenamiento
    volumen_almacenamiento_L = volumen_NaOCl_L_mes

    rango_demanda_cloro_mg_L_texto = f"{Q.desinfeccion_demanda_cloro_min_mg_L:.0f}--{Q.desinfeccion_demanda_cloro_max_mg_L:.0f} mg/L"
    rango_cloro_residual_mg_L_texto = f"{Q.desinfeccion_cloro_residual_min_mg_L:.1f}--{Q.desinfeccion_cloro_residual_max_mg_L:.1f} mg/L".replace(".", ",")
    rango_dosis_cloro_mg_L_texto = f"{Q.desinfeccion_dosis_cloro_min_mg_L:.0f}--{Q.desinfeccion_dosis_cloro_max_mg_L:.0f} mg/L"
    rango_TRH_min_texto = f"{Q.desinfeccion_TRH_recomendado_min:.0f}--{Q.desinfeccion_TRH_recomendado_max:.0f} min"
    rango_NaOCl_comercial_pct_texto = f"{Q.desinfeccion_NaOCl_comercial_min_pct:.0f}--{Q.desinfeccion_NaOCl_comercial_max_pct:.1f}\\%"
    rango_residual_monitoreo_mg_L_texto = f"{Q.desinfeccion_residual_monitoreo_min_mg_L:.1f}--{Q.desinfeccion_residual_monitoreo_max_mg_L:.1f} mg/L".replace(".", ",")
    texto_operacion_cloro = (
        f"Se recomienda monitorear el cloro residual en la salida del tanque "
        f"(debe mantenerse entre {rango_residual_monitoreo_mg_L_texto}) y ajustar "
        f"la dosis según la demanda del efluente. Realizar pruebas de coliformes "
        f"periódicas para verificar la eficacia del sistema."
    )
    
    # =============================================================================
    # COMPARACIÓN CON LÍMITES TULSMA POR USO DEL AGUA
    # =============================================================================
    # Tablas del TULSMA - Límites de Coliformes Fecales (NMP/100mL)
    limites_tulsma_cf = {
        "agua_dulce": {"tabla": "Tabla 12", "limite": limite_TULSMA_CF_NMP, "descripcion": "Agua dulce"},
        "agua_marina": {"tabla": "Tabla 13", "limite": limite_TULSMA_CF_NMP, "descripcion": "Agua marina"},
        "alcantarillado": {"tabla": "Tabla 11", "limite": None, "descripcion": "Alcantarillado"},
        "flora_fauna": {"tabla": "Tabla 3", "limite": 200, "descripcion": "Flora y fauna"},
        "agricola_riego": {"tabla": "Tabla 6", "limite": 1000, "descripcion": "Agrícola/riego"},
        "pecuario": {"tabla": "Tabla 7", "limite": 1000, "descripcion": "Pecuario"},
        "recreativo_primario": {"tabla": "Tabla 9", "limite": 200, "descripcion": "Recreativo primario"},
        "recreativo_secundario": {"tabla": "Tabla 10", "limite": 2000, "descripcion": "Recreativo secundario"},
        "consumo_humano": {"tabla": "Tabla 1", "limite": 600, "descripcion": "Consumo humano trat. conv."},
    }
    
    # Calcular cumplimiento para cada uso
    comparacion_tulsma = {}
    for uso, datos in limites_tulsma_cf.items():
        limite = datos["limite"]
        if limite is None:
            # Sin límite específico (ej. alcantarillado)
            cumple = True
            dictamen = "N/A"
        else:
            cumple = CF_final_NMP <= limite
            dictamen = "CUMPLE" if cumple else "NO CUMPLE"
        
        comparacion_tulsma[uso] = {
            "tabla": datos["tabla"],
            "descripcion": datos["descripcion"],
            "limite_CF": limite,
            "CF_calculado": round(CF_final_NMP, 0),
            "cumple": cumple,
            "dictamen": dictamen
        }
    
    return {
        "unidad": "Tanque de contacto con cloro",
        "Q_m3_d": round(Q_m3_d, 1),
        # Dosis descompuesta
        "demanda_cloro_mg_L": demanda_cloro_mg_L,
        "cloro_residual_mg_L": round(residual_adoptado, 2),  # Residual adoptado para diseño
        "residual_requerido": round(residual_requerido, 2),  # Residual teóricamente requerido
        "residual_minimo_operativo": residual_minimo_operativo,  # Mínimo operativo/config
        "residual_por_debajo_minimo": residual_por_debajo_minimo,  # True si residual < mínimo operativo (advertencia)
        "dosis_cloro_mg_L": dosis_cloro_mg_L,
        "TRH_base_config": TRH_base_config,  # TRH base de configuración (entrada al dimensionamiento)
        "TRH_real_min": round(TRH_real_min, 1),  # TRH real del tanque dimensionado
        "texto_volumen_contacto": texto_volumen_contacto,
        "rango_demanda_cloro_mg_L_texto": rango_demanda_cloro_mg_L_texto,
        "rango_cloro_residual_mg_L_texto": rango_cloro_residual_mg_L_texto,
        "rango_dosis_cloro_mg_L_texto": rango_dosis_cloro_mg_L_texto,
        "rango_TRH_min_texto": rango_TRH_min_texto,
        "rango_NaOCl_comercial_pct_texto": rango_NaOCl_comercial_pct_texto,
        "rango_residual_monitoreo_mg_L_texto": rango_residual_monitoreo_mg_L_texto,
        "texto_operacion_cloro": texto_operacion_cloro,
        "dias_almacenamiento": Q.desinfeccion_almacenamiento_dias,
        # Dimensiones
        "V_contacto_m3": round(V_contacto_m3, 1),
        "V_contacto_min_m3": round(V_contacto_min_m3, 1),
        "A_superficial_m2": round(A_superficial_m2, 1),
        "largo_m": round(largo_m, 1),
        "ancho_m": round(ancho_m, 1),
        "largo_canal_m": round(largo_canal_m, 2),
        "ancho_canal_m": round(ancho_canal_m, 2),
        "ancho_canal_teorico_m": round(ancho_canal_teorico_m, 2),
        "n_canales_serpentin": n_canales_serpentin,
        "espesor_bafle_m": espesor_bafle_m,
        "longitud_recorrido_m": round(longitud_recorrido_m, 1),
        "relacion_recorrido_ancho": round(relacion_recorrido_ancho, 1),
        "relacion_recorrido_ancho_min": relacion_recorrido_ancho_min,
        "estado_camara_contacto": estado_camara_contacto,
        "texto_camara_contacto": texto_camara_contacto,
        "h_tanque_m": h_tanque_m,
        "h_total_m": round(h_tanque_m + borde_libre_m, 2),
        # Parámetros de diseño basado en CF objetivo
        "CF_objetivo_NMP": CF_objetivo_NMP,
        "log_reduccion_requerida": round(log_reduccion_requerida, 2),
        "CT_requerido": round(CT_requerido, 1),
        # Parámetros de desinfección verificados
        "CT_mg_min_L": round(CT_real, 1),  # CT real con residual adoptado y TRH real
        "CT_requerido": round(CT_requerido, 1),  # CT requerido para lograr CF objetivo
        "CT_min_recomendado": CT_min_recomendado,
        "CT_aceptable": CT_aceptable,
        "log_reduccion": round(log_reduccion, 2),
        "CF_entrada_NMP": CF_entrada_NMP,
        "k_log_red": k_log_red,  # Coeficiente log-reducción usado
        "CF_final_NMP": round(CF_final_NMP, 0),
        "pct_reduccion": round(pct_reduccion, 1),
        "cumple_TULSMA": cumple_TULSMA,
        "limite_TULSMA_CF_NMP": limite_TULSMA_CF_NMP,
        "estado_TULSMA": estado_TULSMA,
        "estado_CT": estado_CT,
        "verif_TULSMA_texto": verif_TULSMA_texto,
        "verif_CT_texto": verif_CT_texto,
        # Consumos
        "consumo_cloro_kg_d": round(consumo_cloro_kg_d, 2),  # kg Cl₂/d
        "concentracion_NaOCl_pct": concentracion_NaOCl * 100,  # %
        "consumo_NaOCl_kg_d": round(consumo_NaOCl_kg_d, 1),  # kg NaOCl/d
        "volumen_NaOCl_L_d": round(volumen_NaOCl_L_d, 1),  # L/d
        "volumen_NaOCl_L_mes": round(volumen_NaOCl_L_mes, 0),  # L/mes
        "volumen_almacenamiento_L": round(volumen_almacenamiento_L, 0),  # L
        # Layout (dimensiones reales calculadas, sin márgenes adicionales)
        "largo_layout_m": round(largo_m, 1),
        "ancho_layout_m": round(ancho_m, 1),
        # Comparación TULSMA por uso del agua
        "comparacion_tulsma": comparacion_tulsma,
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

    # Producción de lodos - requerida para dimensionar (cálculo encadenado desde UASB + FP)
    if lodos_kg_SST_d is None:
        raise ValueError("lodos_kg_SST_d es requerido para dimensionar el lecho de secado (cálculo encadenado)")

    # Parámetros de diseño adoptados desde configuración
    C_SST_kg_m3 = Q.lecho_C_SST_kg_m3
    t_secado_d = Q.lecho_t_secado_d
    n_celdas_por_bloque = Q.lecho_n_celdas
    n_celdas_total = Q.num_lineas * n_celdas_por_bloque
    h_lodo_m = Q.lecho_h_lodo_m
    relacion_L_A = Q.lecho_relacion_L_A

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
    A_celda_m2 = A_total_m2 / n_celdas_total

    # Geometría del BLOQUE - para el layout de cada tren
    ancho_m = math.sqrt(A_bloque_m2 / relacion_L_A)
    largo_m = relacion_L_A * ancho_m

    # Tasa de carga de sólidos (por bloque)
    lodos_por_bloque_kg_d = lodos_kg_SST_d / Q.num_lineas
    rho_S_kgSST_m2_año = lodos_por_bloque_kg_d * 365 / A_bloque_m2

    # Dimensiones de la celda (para referencia interna)
    ancho_celda_m = math.sqrt(A_celda_m2 / relacion_L_A)
    largo_celda_m = relacion_L_A * ancho_celda_m

    rango_rho_S_texto = f"{Q.lecho_rho_S_min_kgSST_m2_año:.0f}--{Q.lecho_rho_S_max_kgSST_m2_año:.0f} kg SST/m²·año"
    rango_C_SST_texto = f"{Q.lecho_C_SST_min_kg_m3:.0f}--{Q.lecho_C_SST_max_kg_m3:.0f} kg/m³"
    rango_t_secado_texto = f"{Q.lecho_t_secado_min_d:.0f}--{Q.lecho_t_secado_max_d:.0f} días"
    rango_h_lodo_texto = f"{Q.lecho_h_lodo_min_m:.2f}--{Q.lecho_h_lodo_max_m:.2f} m"
    rango_relacion_L_A_texto = f"{Q.lecho_relacion_L_A_min:.0f}:1--{Q.lecho_relacion_L_A_max:.0f}:1"
    rango_humedad_final_texto = f"{Q.lecho_humedad_final_min_pct:.0f}--{Q.lecho_humedad_final_max_pct:.0f}\\%"

    if Q.lecho_rho_S_min_kgSST_m2_año <= rho_S_kgSST_m2_año <= Q.lecho_rho_S_max_kgSST_m2_año:
        estado_carga_solidos = "Cumple"
        texto_carga_solidos = (
            f"El valor obtenido ({rho_S_kgSST_m2_año:.1f} kg SST/m²·año) se encuentra "
            f"dentro del rango recomendado de {rango_rho_S_texto} para lechos de secado "
            "según Metcalf & Eddy."
        )
    elif rho_S_kgSST_m2_año < Q.lecho_rho_S_min_kgSST_m2_año:
        estado_carga_solidos = "Bajo (conservador)"
        texto_carga_solidos = (
            f"El valor obtenido ({rho_S_kgSST_m2_año:.1f} kg SST/m²·año) está por debajo "
            f"del rango recomendado de {rango_rho_S_texto}. La condición es conservadora "
            "desde el punto de vista de área, aunque puede implicar mayor ocupación de terreno."
        )
    else:
        estado_carga_solidos = "No cumple"
        texto_carga_solidos = (
            f"El valor obtenido ({rho_S_kgSST_m2_año:.1f} kg SST/m²·año) excede el rango "
            f"recomendado de {rango_rho_S_texto}; se recomienda aumentar el área de lechos "
            "o revisar el ciclo de secado adoptado."
        )

    texto_operacion_lecho = (
        "Se recomienda operar los lechos en sistema de rotación, aplicando lodo en una "
        "celda mientras las demás están en proceso de secado o reposo. Bajo operación "
        f"normal, el lodo secado puede alcanzar contenidos de humedad del "
        f"{rango_humedad_final_texto}, facilitando su manejo y disposición final."
    )
    desglose_lodos = [
        {
            "origen": "Producción total de lodos",
            "por_linea_kg_d": round(lodos_kg_SST_d / Q.num_lineas, 2),
            "total_kg_d": round(lodos_kg_SST_d, 2),
        }
    ]
    
    return {
        "unidad": "Lecho de secado de lodos",
        "lodos_kg_SST_d": round(lodos_kg_SST_d, 2),
        "lodos_total_kg_d": round(lodos_kg_SST_d, 2),
        "lodos_total_kg_d_por_linea": round(lodos_kg_SST_d / Q.num_lineas, 2),
        "desglose_lodos": desglose_lodos,
        "lodos_por_bloque_kg_d": round(lodos_por_bloque_kg_d, 2),
        "C_SST_kg_m3": C_SST_kg_m3,
        "t_secado_d": t_secado_d,
        "V_lodo_m3_d": round(V_lodo_m3_d, 3),
        "V_total_secando_m3": round(V_total_secando_m3, 2),
        "n_celdas": n_celdas_total,
        "n_celdas_por_bloque": n_celdas_por_bloque,
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
        "h_arena_m": Q.lecho_h_arena_m,
        "h_grava_m": Q.lecho_h_grava_m,
        "relacion_L_A": relacion_L_A,
        "rho_S_kgSST_m2_año": round(rho_S_kgSST_m2_año, 1),
        "rango_rho_S_texto": rango_rho_S_texto,
        "rango_C_SST_texto": rango_C_SST_texto,
        "rango_t_secado_texto": rango_t_secado_texto,
        "rango_h_lodo_texto": rango_h_lodo_texto,
        "rango_relacion_L_A_texto": rango_relacion_L_A_texto,
        "rango_humedad_final_texto": rango_humedad_final_texto,
        "estado_carga_solidos": estado_carga_solidos,
        "texto_carga_solidos": texto_carga_solidos,
        "texto_operacion_lecho": texto_operacion_lecho,
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
    # Dimensionar sedimentador secundario - unidad reusable para separar sólidos biológicos
    # Calcula carga de sólidos desde la etapa biológica aerobia (filtro percolador)
    if "DBO_salida_Germain_mg_L" not in fp:
        raise KeyError("Falta 'DBO_salida_Germain_mg_L' en resultados del Filtro Percolador")
    DBO_fp_salida = fp["DBO_salida_Germain_mg_L"]
    if "DBO_removida_kg_d" not in fp:
        raise KeyError("Falta 'DBO_removida_kg_d' en resultados del Filtro Percolador")
    # Calcular carga genérica de sólidos biológicos para interfaz reusable
    solidos_biologicos_kg_d = fp["DBO_removida_kg_d"] * Q.sed_factor_produccion_humus
    sed_sec = dimensionar_sedimentador_sec(
        Q, 
        DBO_entrada_mg_L=DBO_fp_salida, 
        solidos_biologicos_entrada_kg_d=solidos_biologicos_kg_d
        # DBO_removida_fp_kg_d se mantiene disponible para retrocompatibilidad legacy
    )
    
    # Calcular CF de entrada (post-sedimentador) basado en eficiencias configuradas (encadenado)
    cf_afluente = 1e7  # NMP/100mL (típico aguas residuales sin tratar)
    cf_tras_uasb = cf_afluente * (1 - Q.balance_eta_CF_uasb)
    cf_tras_fp = cf_tras_uasb * (1 - Q.balance_eta_CF_fp)
    cf_tras_sed = cf_tras_fp * (1 - Q.balance_eta_CF_sed)
    cloro      = dimensionar_desinfeccion_cloro(Q, CF_entrada_NMP=cf_tras_sed)
    
    # Calcular producción de lodos REAL para toda la planta
    # UASB: lodos anaerobios (factor de producción desde config)
    DBO_removida_uasb_kg_d_por_linea = Q.Q_linea_m3_d * (Q.DBO5_mg_L / 1000) * uasb['eta_DBO']
    lodos_uasb_kg_d_por_linea = Q.lecho_factor_produccion_lodos * DBO_removida_uasb_kg_d_por_linea
    # Filtro Percolador: humus (sólidos biológicos desprendidos del control de espesor)
    # El factor de producción de humus debe aplicarse consistentemente (igual que en sedimentador)
    if "DBO_removida_kg_d" not in fp:
        raise KeyError("Falta 'DBO_removida_kg_d' en resultados del Filtro Percolador")
    # Producción de humus = factor × DBO removida (factor típico: 0.15 kg SST/kg DBO)
    lodos_fp_kg_d_por_linea = fp["DBO_removida_kg_d"] * Q.sed_factor_produccion_humus
    # Producción total de lodos (todas las líneas)
    lodos_total_kg_d_total = (lodos_uasb_kg_d_por_linea + lodos_fp_kg_d_por_linea) * Q.num_lineas
    lecho      = dimensionar_lecho_secado(Q, lodos_kg_SST_d=lodos_total_kg_d_total)
    
    # Agregar desglose de lodos al resultado del lecho para consistencia en documentación
    lecho["lodos_uasb_kg_d_por_linea"] = round(lodos_uasb_kg_d_por_linea, 2)
    lecho["lodos_fp_kg_d_por_linea"] = round(lodos_fp_kg_d_por_linea, 2)
    lecho["lodos_uasb_kg_d"] = round(lodos_uasb_kg_d_por_linea * Q.num_lineas, 2)
    lecho["lodos_fp_kg_d"] = round(lodos_fp_kg_d_por_linea * Q.num_lineas, 2)
    lecho["lodos_total_kg_d"] = round(lodos_total_kg_d_total, 2)
    lecho["desglose_lodos"] = [
        {
            "origen": "Lodos UASB (anaerobios)",
            "por_linea_kg_d": lecho["lodos_uasb_kg_d_por_linea"],
            "total_kg_d": lecho["lodos_uasb_kg_d"],
        },
        {
            "origen": "Humus FP + Sedimentador",
            "por_linea_kg_d": lecho["lodos_fp_kg_d_por_linea"],
            "total_kg_d": lecho["lodos_fp_kg_d"],
        },
    ]

    # Balance de calidad (progresivo) - usando resultados reales del dimensionamiento
    DBO_in     = Q.DBO5_mg_L
    DBO_uasb   = DBO_in  * (1 - uasb["eta_DBO"])       # tras UASB
    # Usar DBO de salida del sedimentador calculada realmente
    if "DBO_salida_mg_L" not in sed_sec:
        raise KeyError("Falta 'DBO_salida_mg_L' en resultados del Sedimentador Secundario")
    DBO_efluente = sed_sec["DBO_salida_mg_L"]  # tras sedimentación

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
        "desinfeccion": cloro,
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
    
    # Calcular CF de entrada para desinfección (post-humedal)
    cf_afluente = 1e7  # NMP/100mL (típico aguas residuales sin tratar)
    cf_tras_uasb = cf_afluente * (1 - Q.balance_eta_CF_uasb)
    cf_tras_humedal = cf_tras_uasb * (1 - Q.humedal_eta_CF)  # Eficiencia específica del HAFV según manual
    cloro      = dimensionar_desinfeccion_cloro(Q, CF_entrada_NMP=cf_tras_humedal)
    
    # Calcular producción de lodos REAL para toda la planta
    # UASB: lodos anaerobios (factor de producción desde config)
    DBO_removida_uasb_kg_d_por_linea = Q.Q_linea_m3_d * (Q.DBO5_mg_L / 1000) * uasb['eta_DBO']
    lodos_uasb_kg_d_por_linea = Q.lecho_factor_produccion_lodos * DBO_removida_uasb_kg_d_por_linea
    # Humedal: produce lodos mínimos (retención en el lecho), se considera despreciable para simplificación
    lodos_humedal_kg_d_por_linea = 0.0  # Los sólidos se acumulan en el lecho del humedal
    # Producción total de lodos (ambas líneas)
    lodos_total_kg_d_total = (lodos_uasb_kg_d_por_linea + lodos_humedal_kg_d_por_linea) * Q.num_lineas
    lecho      = dimensionar_lecho_secado(Q, lodos_kg_SST_d=lodos_total_kg_d_total)
    lecho["lodos_uasb_kg_d_por_linea"] = round(lodos_uasb_kg_d_por_linea, 2)
    lecho["lodos_humedal_kg_d_por_linea"] = round(lodos_humedal_kg_d_por_linea, 2)
    lecho["lodos_uasb_kg_d"] = round(lodos_uasb_kg_d_por_linea * Q.num_lineas, 2)
    lecho["lodos_humedal_kg_d"] = round(lodos_humedal_kg_d_por_linea * Q.num_lineas, 2)
    lecho["lodos_total_kg_d"] = round(lodos_total_kg_d_total, 2)
    lecho["desglose_lodos"] = [
        {
            "origen": "Lodos UASB (anaerobios)",
            "por_linea_kg_d": lecho["lodos_uasb_kg_d_por_linea"],
            "total_kg_d": lecho["lodos_uasb_kg_d"],
        },
        {
            "origen": "Retención/acumulación en humedal",
            "por_linea_kg_d": lecho["lodos_humedal_kg_d_por_linea"],
            "total_kg_d": lecho["lodos_humedal_kg_d"],
        },
    ]

    DBO_in     = Q.DBO5_mg_L
    DBO_uasb   = DBO_in * (1 - uasb["eta_DBO"])
    DBO_efluente = humedal["DBO_salida_mg_L"]
    CF_final = cloro["CF_final_NMP"]
    
    # Verificación de cumplimiento TULSMA (DBO y CF)
    cumple_DBO = DBO_efluente <= 100
    cumple_CF = CF_final <= Q.desinfeccion_CF_objetivo_NMP
    cumple_TULSMA = cumple_DBO and cumple_CF

    print("=" * 70)
    print("TREN C - UASB + HUMEDAL VERTICAL + CLORO")
    print(f"Caudal por línea: {Q.Q_linea_L_s} L/s = {Q.Q_linea_m3_d} m^3/d")
    print("=" * 70)
    
    # Metodología actualizada: HAFV tropical de alta carga (Ruta B) según manual
    print(f"\n  SISTEMA HUMEDAL: {humedal['metodologia']}")
    print(f"  Selección: {humedal['justificacion_seleccion']}")
    print(f"  Criterio que controla: {humedal.get('criterio_controla', 'N/A')}")
    print(f"  OLR real: {humedal.get('OLR_gDQO_m2_d', 0):.0f} g DQO/m²·d")
    print(f"  HLR: {humedal.get('HLR_m_d', 0):.2f} m/d")
    print(f"  Verificación k-C*: DBO salida = {humedal['verificacion_kC']['DBO_salida_calc_mg_L']:.1f} mg/L")

    print(f"\n  UASB          Ø {uasb['diametro_layout_m']:.1f} m   V={uasb['V_r_m3']:.1f} m^3")
    print(f"  Humedal HFCV  {humedal['largo_layout_m']:.1f} x {humedal['ancho_layout_m']:.1f} m"
          f"  A={humedal['A_sup_m2']:.0f} m^2")
    print(f"  Desinfeccion  {cloro['largo_m']:.1f} m × {cloro['ancho_m']:.1f} m  TRH={cloro['TRH_real_min']:.0f} min, Residual={cloro['cloro_residual_mg_L']:.2f} mg/L")
    print(f"  Lecho Secado  {lecho['largo_layout_m']:.1f} × {lecho['ancho_layout_m']:.1f} m")

    print("\nBALANCE DE CALIDAD:")
    print(f"  Afluente    DBO5 = {DBO_in:.0f} mg/L")
    print(f"  Tras UASB   DBO5 = {DBO_uasb:.0f} mg/L")
    print(f"  Tras HFCV   DBO5 ~ {DBO_efluente:.0f} mg/L")
    print(f"  Efluente    CF   ~ {CF_final:.0f} NMP/100mL")
    print(f"\n  CUMPLIMIENTO TULSMA:")
    print(f"    DBO5 <= 100 mg/L      -> {'CUMPLE [OK]' if cumple_DBO else 'NO CUMPLE [X]'}")
    limite_cf = Q.desinfeccion_CF_objetivo_NMP
    print(f"    CF   <= {limite_cf:.0f} NMP/100mL -> {'CUMPLE [OK]' if cumple_CF else 'NO CUMPLE [X]'}")
    print(f"    TOTAL                  -> {'CUMPLE [OK]' if cumple_TULSMA else 'NO CUMPLE [X]'}")

    return {
        "rejillas": rejillas,
        "desarenador": desarenador,
        "uasb": uasb,
        "humedal": humedal,
        "desinfeccion": cloro,
        "lecho_secado": lecho,
        "balance": {
            "DBO_in_mg_L": DBO_in,
            "DBO_tras_UASB_mg_L": round(DBO_uasb, 1),
            "DBO_efluente_mg_L": round(DBO_efluente, 1),
            "CF_final_NMP": CF_final,
            "cumple_DBO": cumple_DBO,
            "cumple_CF": cumple_CF,
            "cumple_TULSMA": cumple_TULSMA,
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
            # Guardar eficiencias por parámetro
            calidad["eficiencias_uasb"] = {
                "DBO5_pct": round(eta_DBO_uasb * 100, 1),
                "DQO_pct": round(eta_DQO_uasb * 100, 1),
                "SST_pct": round(eta_SST_uasb * 100, 1),
                "CF_pct": round(eta_CF_uasb * 100, 1),
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
            # Guardar eficiencias por parámetro
            calidad["eficiencias_fp"] = {
                "DBO5_pct": round(eta_DBO_fp * 100, 1),
                "DQO_pct": round(eta_DQO_fp * 100, 1),
                "SST_pct": round(eta_SST_fp * 100, 1),
                "CF_pct": round(eta_CF_fp * 100, 1),
            }
        
        # Tras Humedal Vertical (Alternativa C)
        if "humedal" in resultados and "tras_uasb" in calidad:
            hum = resultados["humedal"]
            DBO_entrada_hum = calidad["tras_uasb"]["DBO5_mg_L"]
            # DBO salida del humedal según modelo k-C*
            DBO_salida_hum = hum.get("DBO_salida_mg_L", Q.humedal_DBO_salida_mg_L)
            eta_DBO_hum = 1 - (DBO_salida_hum / DBO_entrada_hum) if DBO_entrada_hum > 0 else 0
            # SST removido por humedal
            eta_SST_hum = Q.balance_eta_SST_humedal
            # DQO similar a DBO
            eta_DQO_hum = eta_DBO_hum
            # CF remoción según configuración del humedal
            eta_CF_hum = Q.humedal_eta_CF
            
            calidad["tras_humedal"] = {
                "DBO5_mg_L": round(DBO_salida_hum, 1),
                "DQO_mg_L": round(calidad["tras_uasb"]["DQO_mg_L"] * (1 - eta_DQO_hum), 1),
                "SST_mg_L": round(calidad["tras_uasb"]["SST_mg_L"] * (1 - eta_SST_hum), 1),
                "CF_NMP": round(calidad["tras_uasb"]["CF_NMP"] * (1 - eta_CF_hum), 0),
            }
            # Guardar eficiencias por parámetro
            calidad["eficiencias_humedal"] = {
                "DBO5_pct": round(eta_DBO_hum * 100, 1),
                "DQO_pct": round(eta_DQO_hum * 100, 1),
                "SST_pct": round(eta_SST_hum * 100, 1),
                "CF_pct": round(eta_CF_hum * 100, 1),
            }
        
        # Tras Sedimentador Secundario
        if "sedimentador_sec" in resultados and "tras_fp" in calidad:
            sed = resultados["sedimentador_sec"]
            DBO_entrada_sed = calidad["tras_fp"]["DBO5_mg_L"]
            if "eta_DBO_sed" not in sed:
                raise KeyError("Falta 'eta_DBO_sed' en resultados del Sedimentador Secundario")
            eta_DBO_sed = sed["eta_DBO_sed"]
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
            # Guardar eficiencias por parámetro
            calidad["eficiencias_sed"] = {
                "DBO5_pct": round(eta_DBO_sed * 100, 1),
                "DQO_pct": round(eta_DQO_sed * 100, 1),
                "SST_pct": round(eta_SST_sed * 100, 1),
                "CF_pct": round(eta_CF_sed * 100, 1),
            }
        
        # Tras desinfección (UV o Cloro)
        desinfeccion_keys = ["uv", "desinfeccion", "cloro"]
        tiene_desinfeccion = any(k in resultados for k in desinfeccion_keys)
        # Determinar etapa previa (sed o humedal)
        etapa_previa = None
        if "tras_sed" in calidad:
            etapa_previa = "tras_sed"
        elif "tras_humedal" in calidad:
            etapa_previa = "tras_humedal"
        
        if tiene_desinfeccion and etapa_previa:
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
            CF_final = round(calidad[etapa_previa]["CF_NMP"] * (1 - eta_CF), 0)
            if CF_final < 1:
                CF_final = 1  # Mínimo detectable
            
            calidad["efluente_final"] = {
                "DBO5_mg_L": calidad[etapa_previa]["DBO5_mg_L"],
                "DQO_mg_L": calidad[etapa_previa]["DQO_mg_L"],
                "SST_mg_L": calidad[etapa_previa]["SST_mg_L"],
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
        limite_CF = Q.desinfeccion_CF_objetivo_NMP if Q else 3000.0
        calidad["cumplimiento_TULSMA"] = {
            "DBO5": ef["DBO5_mg_L"] <= 100,
            "SST": ef["SST_mg_L"] <= 100,
            "CF": ef["CF_NMP"] <= limite_CF,
        }
    
    return calidad


# =============================================================================
# 4c - BIOFILTRO BIOLÓGICO AIREADO (BAF)
# =============================================================================

def dimensionar_baf(Q: ConfigDiseno = CFG,
                    DBO_entrada_mg_L: float = None) -> Dict[str, Any]:
    """
    Dimensionamiento del Biofiltro Biológico Aireado (BAF).
    
    El BAF es un reactor de lecho sumergido con aireación forzada que combina
    degradación biológica y filtración física en una sola unidad, eliminando
    la necesidad de sedimentador secundario posterior.
    
    Parámetros:
        Q: ConfigDiseno con parámetros globales
        DBO_entrada_mg_L: DBO5 del afluente al BAF (mg/L), típicamente efluente UASB
    
    Retorna:
        Dict con resultados del dimensionamiento y verificaciones
    """
    ref_me = citar("metcalf_2014")
    ref_henze = citar("henze_2008")
    
    # DBO5 entrante (si no se especifica, asumir valor típico post-UASB)
    if DBO_entrada_mg_L is None:
        DBO_entrada_mg_L = Q.baf_DBO_entrada_mg_L
    
    # Parámetros básicos
    Q_m3_d = Q.Q_linea_m3_d
    Q_m3_h = Q.Q_linea_m3_h
    factor_pico = Q.factor_pico_Qmax
    Q_max_m3_d = Q_m3_d * factor_pico
    Q_max_m3_h = Q_max_m3_d / 24.0
    
    # =============================================================================
    # DIMENSIONAMIENTO PRINCIPAL
    # =============================================================================
    
    # [PASO 1] Área superficial por criterio HLR
    HLR_diseño = Q.baf_HLR_diseño_m3_m2_h
    A_s_m2 = Q_m3_h / HLR_diseño
    
    # [PASO 2] Diámetro del reactor circular
    D_m = math.sqrt(4 * A_s_m2 / math.pi)
    D_adoptado_m = math.ceil(D_m * 10) / 10  # Redondear a 1 decimal hacia arriba
    
    # Área real con diámetro adoptado
    A_real_m2 = math.pi * (D_adoptado_m ** 2) / 4
    
    # HLR real a caudal medio
    HLR_real_m3_m2_h = Q_m3_h / A_real_m2
    
    # [PASO 3] Volumen de lecho de relleno
    H_lecho_m = Q.baf_profundidad_lecho_m
    V_lecho_m3 = A_real_m2 * H_lecho_m
    
    # [PASO 4] Tiempo de contacto en lecho vacío (EBCT)
    EBCT_h = V_lecho_m3 / Q_m3_h
    
    # [PASO 5] Carga orgánica volumétrica (OLR)
    carga_DBO_kg_d = Q_m3_d * DBO_entrada_mg_L / 1000.0
    OLR_kgDBO_m3_d = carga_DBO_kg_d / V_lecho_m3
    
    # [PASO 6] Demanda de aire para proceso biológico
    relacion_aire_agua = Q.baf_relacion_aire_agua
    Q_aire_Nm3_h = relacion_aire_agua * Q_m3_h
    
    # Tasa específica de aireación (SAR)
    SAR_m3_m2_h = Q_aire_Nm3_h / A_real_m2
    
    # Verificación de suficiencia de oxígeno
    DO_requerida_kg_d = Q.baf_factor_O2_kgO2_kgDBO * carga_DBO_kg_d
    OTE = Q.baf_OTE_pct / 100.0
    Q_aire_min_Nm3_h = (DO_requerida_kg_d / 
                       (OTE * Q.baf_densidad_aire_kg_Nm3 * Q.baf_fraccion_O2_aire * 24))
    factor_seguridad_aire = Q_aire_Nm3_h / Q_aire_min_Nm3_h if Q_aire_min_Nm3_h > 0 else 999
    
    # [PASO 7] Altura total de construcción
    H_plenum_m = Q.baf_altura_plenum_m
    H_headspace_m = Q.baf_altura_headspace_m
    H_acumulacion_m = Q.baf_altura_acumulacion_m
    H_bordo_m = Q.baf_bordo_libre_m
    
    H_total_m = H_plenum_m + H_lecho_m + H_headspace_m + H_acumulacion_m + H_bordo_m
    
    # [PASO 8] Diseño del retrolavado
    vel_bw_aire_m3_m2_h = Q.baf_vel_bw_aire_m3_m2_h
    vel_bw_agua_m3_m2_h = Q.baf_vel_bw_agua_m3_m2_h
    
    Q_bw_aire_m3_h = vel_bw_aire_m3_m2_h * A_real_m2
    Q_bw_agua_m3_h = vel_bw_agua_m3_m2_h * A_real_m2
    
    # Volumen de agua de retrolavado por ciclo (fase agua configurable)
    duracion_fase_agua_h = Q.baf_duracion_fase_agua_bw_min / 60.0
    V_bw_ciclo_m3 = Q_bw_agua_m3_h * duracion_fase_agua_h
    fraccion_bw_pct = (V_bw_ciclo_m3 / Q_m3_d) * 100
    
    # =============================================================================
    # VERIFICACIONES
    # =============================================================================
    
    # HLR a caudal máximo
    HLR_max_m3_m2_h = Q_max_m3_h / A_real_m2
    
    # EBCT a caudal máximo
    EBCT_pico_h = V_lecho_m3 / Q_max_m3_h
    
    # OLR a caudal máximo
    carga_DBO_pico_kg_d = Q_max_m3_d * DBO_entrada_mg_L / 1000.0
    OLR_pico_kgDBO_m3_d = carga_DBO_pico_kg_d / V_lecho_m3
    
    # Relación H/D
    relacion_H_D = H_lecho_m / D_adoptado_m
    
    # =============================================================================
    # VERIFICACIONES CON ESTADOS TEXTUALES PARA RENDER EN LATEX
    # =============================================================================
    
    # Verificación EBCT pico: siempre requiere nota si está debajo del mínimo
    cumple_EBCT_pico = EBCT_pico_h >= Q.baf_EBCT_min_h
    if cumple_EBCT_pico:
        estado_EBCT_pico = "CUMPLE"
        texto_EBCT_pico = "El EBCT a caudal pico se encuentra dentro del rango de diseño."
    else:
        estado_EBCT_pico = "VER NOTA"
        texto_EBCT_pico = ("El EBCT de pico es inferior al mínimo de diseño. "
                          "Los picos de caudal son eventos de corta duración y la inercia "
                          "biológica del biofilm amortigua los efectos. "
                          "Se recomienda ecualización de caudales aguas arriba.")
    
    # Verificación OLR pico: requiere nota si supera el máximo
    cumple_OLR_pico = OLR_pico_kgDBO_m3_d <= Q.baf_OLR_max_kgDBO_m3_d
    if cumple_OLR_pico:
        estado_OLR_pico = "CUMPLE"
        texto_OLR_pico = "La OLR a caudal pico se encuentra dentro del rango permisible."
    else:
        estado_OLR_pico = "VER NOTA"
        texto_OLR_pico = ("La OLR de pico supera ligeramente el límite durante caudal máximo. "
                         "El UASB aguas arriba actúa como amortiguador. "
                         "El impacto es transitorio y tolerable.")
    
    # Verificación de suficiencia de aire: con factor de seguridad
    cumple_aire = factor_seguridad_aire >= 1.0
    if factor_seguridad_aire >= Q.baf_factor_seguridad_aire_min:
        estado_aire = "CUMPLE CON HOLGURA"
        texto_aire = (f"El caudal de aire diseñado ({Q_aire_Nm3_h:.1f} Nm³/h) supera ampliamente "
                     f"el requerimiento mínimo ({Q_aire_min_Nm3_h:.1f} Nm³/h), "
                     f"con un factor de seguridad de {factor_seguridad_aire:.1f}.")
    elif cumple_aire:
        estado_aire = "CUMPLE"
        texto_aire = "El caudal de aire diseñado satisface la demanda biológica mínima."
    else:
        estado_aire = "NO CUMPLE"
        texto_aire = "El caudal de aire diseñado es insuficiente para la demanda biológica."
    
    # Verificaciones estructuradas para el render
    verificaciones = {
        "HLR_medio": {
            "valor": HLR_real_m3_m2_h,
            "min": Q.baf_HLR_min_m3_m2_h,
            "max": Q.baf_HLR_max_m3_m2_h,
            "cumple": Q.baf_HLR_min_m3_m2_h <= HLR_real_m3_m2_h <= Q.baf_HLR_max_m3_m2_h,
            "estado": "CUMPLE" if Q.baf_HLR_min_m3_m2_h <= HLR_real_m3_m2_h <= Q.baf_HLR_max_m3_m2_h else "NO CUMPLE"
        },
        "HLR_maximo": {
            "valor": HLR_max_m3_m2_h,
            "limite": Q.baf_HLR_max_pico_m3_m2_h,
            "cumple": HLR_max_m3_m2_h <= Q.baf_HLR_max_pico_m3_m2_h,
            "estado": "CUMPLE" if HLR_max_m3_m2_h <= Q.baf_HLR_max_pico_m3_m2_h else "NO CUMPLE"
        },
        "EBCT_medio": {
            "valor": EBCT_h,
            "min": Q.baf_EBCT_min_h,
            "max": Q.baf_EBCT_max_h,
            "cumple": Q.baf_EBCT_min_h <= EBCT_h <= Q.baf_EBCT_max_h,
            "estado": "CUMPLE" if Q.baf_EBCT_min_h <= EBCT_h <= Q.baf_EBCT_max_h else "NO CUMPLE"
        },
        "EBCT_pico": {
            "valor": EBCT_pico_h,
            "min": Q.baf_EBCT_min_h,
            "cumple": cumple_EBCT_pico,
            "estado": estado_EBCT_pico,
            "texto": texto_EBCT_pico
        },
        "OLR_medio": {
            "valor": OLR_kgDBO_m3_d,
            "min": Q.baf_OLR_min_kgDBO_m3_d,
            "max": Q.baf_OLR_max_kgDBO_m3_d,
            "cumple": Q.baf_OLR_min_kgDBO_m3_d <= OLR_kgDBO_m3_d <= Q.baf_OLR_max_kgDBO_m3_d,
            "estado": "CUMPLE" if Q.baf_OLR_min_kgDBO_m3_d <= OLR_kgDBO_m3_d <= Q.baf_OLR_max_kgDBO_m3_d else "NO CUMPLE"
        },
        "OLR_pico": {
            "valor": OLR_pico_kgDBO_m3_d,
            "max": Q.baf_OLR_max_kgDBO_m3_d,
            "cumple": cumple_OLR_pico,
            "estado": estado_OLR_pico,
            "texto": texto_OLR_pico
        },
        "SAR": {
            "valor": SAR_m3_m2_h,
            "min": Q.baf_SAR_min_m3_m2_h,
            "max": Q.baf_SAR_max_m3_m2_h,
            "cumple": Q.baf_SAR_min_m3_m2_h <= SAR_m3_m2_h <= Q.baf_SAR_max_m3_m2_h,
            "estado": "CUMPLE" if Q.baf_SAR_min_m3_m2_h <= SAR_m3_m2_h <= Q.baf_SAR_max_m3_m2_h else "NO CUMPLE"
        },
        "suficiencia_aire": {
            "valor": factor_seguridad_aire,
            "cumple": cumple_aire,
            "estado": estado_aire,
            "texto": texto_aire
        },
        "relacion_H_D": {
            "valor": relacion_H_D,
            "min": Q.baf_relacion_H_D_min,
            "max": Q.baf_relacion_H_D_max,
            "cumple": Q.baf_relacion_H_D_min <= relacion_H_D <= Q.baf_relacion_H_D_max,
            "estado": "CUMPLE" if Q.baf_relacion_H_D_min <= relacion_H_D <= Q.baf_relacion_H_D_max else "NO CUMPLE"
        },
        "fraccion_retrolavado": {
            "valor": fraccion_bw_pct,
            "min": Q.baf_fraccion_bw_min_pct,
            "max": Q.baf_fraccion_bw_max_pct,
            "cumple": Q.baf_fraccion_bw_min_pct <= fraccion_bw_pct <= Q.baf_fraccion_bw_max_pct,
            "estado": "CUMPLE" if Q.baf_fraccion_bw_min_pct <= fraccion_bw_pct <= Q.baf_fraccion_bw_max_pct else "NO CUMPLE"
        }
    }
    
    # Texto resumen de verificaciones para el cierre de la sección
    verificaciones_cumplen = sum(1 for v in verificaciones.values() if v["estado"] == "CUMPLE")
    verificaciones_cumplen_holgura = sum(1 for v in verificaciones.values() if v["estado"] == "CUMPLE CON HOLGURA")
    verificaciones_ver_nota = sum(1 for v in verificaciones.values() if v["estado"] == "VER NOTA")
    verificaciones_no_cumplen = sum(1 for v in verificaciones.values() if v["estado"] == "NO CUMPLE")
    
    if verificaciones_no_cumplen > 0:
        texto_resumen_verificaciones = (
            f"Se detectaron {verificaciones_no_cumplen} verificaciones que no cumplen los criterios establecidos. "
            f"{verificaciones_cumplen} parámetros cumplen directamente; "
            f"{verificaciones_cumplen_holgura} cumplen con holgura adicional; "
            f"{verificaciones_ver_nota} requieren nota operativa por condiciones de pico transitorio. "
            f"Se requiere revisión de diseño para los parámetros marcados como NO CUMPLE."
        )
    elif verificaciones_ver_nota > 0:
        texto_resumen_verificaciones = (
            f"Las verificaciones principales cumplen con los criterios establecidos. "
            f"{verificaciones_cumplen} parámetros cumplen directamente; "
            f"{verificaciones_cumplen_holgura} cumplen con holgura adicional; "
            f"{verificaciones_ver_nota} requieren nota operativa por condiciones de pico transitorio."
        )
    else:
        texto_resumen_verificaciones = (
            f"Todas las verificaciones cumplen con los criterios establecidos. "
            f"{verificaciones_cumplen} parámetros cumplen directamente y "
            f"{verificaciones_cumplen_holgura} cumplen con holgura adicional."
        )
    
    return {
        # Identificación
        "unidad": "BAF",
        "nombre": "Biofiltro Biológico Aireado",
        
        # Dimensiones principales
        "D_m": D_adoptado_m,
        "diametro_layout_m": round(D_adoptado_m, 2),
        "A_real_m2": round(A_real_m2, 2),
        "area_huella_layout_m2": round(A_real_m2, 2),
        "V_lecho_m3": round(V_lecho_m3, 2),
        "H_lecho_m": H_lecho_m,
        "H_plenum_m": H_plenum_m,
        "H_headspace_m": H_headspace_m,
        "H_acumulacion_m": H_acumulacion_m,
        "H_bordo_m": H_bordo_m,
        "H_total_m": H_total_m,
        "relacion_H_D": round(relacion_H_D, 2),
        
        # Parámetros hidráulicos
        "Q_m3_d": Q_m3_d,
        "Q_m3_h": Q_m3_h,
        "Q_max_m3_d": Q_max_m3_d,
        "Q_max_m3_h": Q_max_m3_h,
        "HLR_diseño_m3_m2_h": HLR_diseño,
        "HLR_real_m3_m2_h": round(HLR_real_m3_m2_h, 2),
        "HLR_max_m3_m2_h": round(HLR_max_m3_m2_h, 2),
        
        # Parámetros de proceso
        "DBO_entrada_mg_L": DBO_entrada_mg_L,
        "carga_DBO_kg_d": round(carga_DBO_kg_d, 1),
        "carga_DBO_pico_kg_d": round(carga_DBO_pico_kg_d, 1),
        "EBCT_h": round(EBCT_h, 2),
        "EBCT_pico_h": round(EBCT_pico_h, 2),
        "OLR_kgDBO_m3_d": round(OLR_kgDBO_m3_d, 2),
        "OLR_pico_kgDBO_m3_d": round(OLR_pico_kgDBO_m3_d, 2),
        
        # Aireación
        "relacion_aire_agua": relacion_aire_agua,
        "Q_aire_Nm3_h": round(Q_aire_Nm3_h, 1),
        "SAR_m3_m2_h": round(SAR_m3_m2_h, 1),
        "Q_aire_min_Nm3_h": round(Q_aire_min_Nm3_h, 1),
        "factor_seguridad_aire": round(factor_seguridad_aire, 1),
        
        # Retrolavado
        "vel_bw_aire_m3_m2_h": vel_bw_aire_m3_m2_h,
        "vel_bw_agua_m3_m2_h": vel_bw_agua_m3_m2_h,
        "Q_bw_aire_m3_h": round(Q_bw_aire_m3_h, 1),
        "Q_bw_agua_m3_h": round(Q_bw_agua_m3_h, 1),
        "V_bw_ciclo_m3": round(V_bw_ciclo_m3, 1),
        "fraccion_bw_pct": round(fraccion_bw_pct, 1),
        "freq_retrolavado_h": Q.baf_freq_retrolavado_h,
        "duracion_retrolavado_min": Q.baf_duracion_retrolavado_min,
        
        # Verificaciones
        "verificaciones": verificaciones,
        "todas_cumplen": all(v["cumple"] for v in verificaciones.values()),
        "texto_resumen_verificaciones": texto_resumen_verificaciones,
        
        # Rellenos
        "sup_especifica_m2_m3": Q.baf_sup_especifica_m2_m3,
        "porosidad_pct": Q.baf_porosidad_pct,
        
        # Referencias
        "fuente": f"{ref_me}; {ref_henze}"
    }


# =============================================================================
# 4d - REACTOR ANAEROBIO CON PANTALLAS (ABR / RAP)
# =============================================================================

def dimensionar_abr_rap(Q: ConfigDiseno = CFG,
                        DBO_entrada_mg_L: float = None,
                        DQO_entrada_mg_L: float = None,
                        SST_entrada_mg_L: float = None) -> Dict[str, Any]:
    """
    Dimensionamiento del Reactor Anaerobio con Pantallas (ABR / RAP).
    
    El ABR (Anaerobic Baffled Reactor) o RAP es un reactor anaerobio de
    múltiples compartimentos que opera mediante flujo ascendente-descendente
    a través de una serie de cámaras separadas por pantallas o bafles.
    
    A diferencia del UASB, el ABR no requiere separador trifásico: la
    retención de biomasa se logra por medios puramente hidráulicos y
    gravitacionales, aprovechando la baja velocidad ascensional en cada
    compartimento.
    
    NOTA IMPORTANTE SOBRE EL ALCANCE:
    Esta función implementa el dimensionamiento básico del ABR según el
    manual_ABR_RAP.txt. Calcula volumen, geometría y verificaciones
    hidráulicas fundamentales. No implementa: modelo cinético de remoción
    de DBO, cálculo de producción de biogás, balance detallado de lodos,
    ni diseño de pantallas individuales.
    
    Parámetros:
        Q: ConfigDiseno con parámetros globales
        DBO_entrada_mg_L: DBO5 del afluente al ABR (mg/L)
        DQO_entrada_mg_L: DQO del afluente al ABR (mg/L)
        SST_entrada_mg_L: SST del afluente al ABR (mg/L)
    
    Retorna:
        Dict con resultados del dimensionamiento y verificaciones
    """
    ref_barber = "Barber & Stuckey (1999)"
    ref_foxon = "Foxon et al. (2004)"
    ref_ops = "OPS/OMS (2005)"
    
    # Usar valores de configuración si no se especifican
    if DBO_entrada_mg_L is None:
        DBO_entrada_mg_L = Q.abr_DBO_entrada_mg_L
    if DQO_entrada_mg_L is None:
        DQO_entrada_mg_L = Q.abr_DQO_entrada_mg_L
    if SST_entrada_mg_L is None:
        SST_entrada_mg_L = Q.abr_SST_entrada_mg_L
    
    # Parámetros de caudal
    Q_m3_d = Q.Q_linea_m3_d
    Q_m3_h = Q.Q_linea_m3_h
    factor_pico = Q.factor_pico_Qmax
    Q_max_m3_d = Q_m3_d * factor_pico
    Q_max_m3_h = Q_max_m3_d / 24.0
    
    # =============================================================================
    # DIMENSIONAMIENTO PRINCIPAL
    # =============================================================================
    
    # [PASO 1] Volumen total según TRH de diseño
    # V_total = Q_medio × TRH
    TRH_diseno_h = Q.abr_TRH_diseno_h
    TRH_diseno_d = TRH_diseno_h / 24.0
    V_total_m3 = Q_m3_d * TRH_diseno_d
    
    # [PASO 2] Número de compartimentos
    n_comp = Q.abr_num_compartimentos
    
    # Volumen por compartimento (distribución uniforme)
    V_comp_m3 = V_total_m3 / n_comp
    
    # [PASO 3] Área de sección transversal por velocidad ascensional
    # A_transversal = Q_medio / v_up_diseno
    v_up_diseno_m_h = Q.abr_v_up_diseno_m_h
    A_transversal_m2 = Q_m3_h / v_up_diseno_m_h
    
    # [PASO 4] Dimensiones geométricas
    # Profundidad útil del líquido
    H_util_m = Q.abr_profundidad_util_m
    
    # Ancho del reactor: W = A_transversal / H
    W_m = A_transversal_m2 / H_util_m
    
    # Largo de cada compartimento: L_comp = V_comp / (W × H)
    L_comp_m = V_comp_m3 / (W_m * H_util_m)
    
    # Largo total del reactor
    L_total_m = n_comp * L_comp_m
    
    # Profundidad total (incluye zona de lodos y bordo libre)
    H_zona_lodos_m = Q.abr_zona_lodos_m
    H_bordo_m = Q.abr_bordo_libre_m
    H_total_m = H_util_m + H_zona_lodos_m + H_bordo_m
    
    # [PASO 5] Verificaciones hidráulicas
    
    # Velocidad ascensional calculada a caudal medio
    v_up_calc_m_h = Q_m3_h / (W_m * H_util_m)
    
    # Velocidad ascensional a caudal máximo
    v_up_max_calc_m_h = Q_max_m3_h / (W_m * H_util_m)
    
    # TRH calculado a partir de la geometría
    V_geometria_m3 = L_total_m * W_m * H_util_m
    TRH_calc_h = (V_geometria_m3 / Q_m3_d) * 24.0
    
    # Carga hidráulica superficial (informativa)
    A_planta_m2 = L_total_m * W_m
    CHS_m_d = Q_m3_d / A_planta_m2
    
    # Carga orgánica volumétrica (informativa)
    COV_kgDBO_m3_d = (Q_m3_d * DBO_entrada_mg_L / 1000.0) / V_total_m3
    
    # Relación L_comp / W (informativa)
    relacion_Lcomp_W = L_comp_m / W_m
    
    # =============================================================================
    # VERIFICACIONES DE DISEÑO
    # =============================================================================
    
    verificaciones = {}
    
    # [V-1] Velocidad ascensional a caudal medio
    cumple_v_up_medio = v_up_calc_m_h <= Q.abr_v_up_diseno_m_h
    estado_v_up_medio = "CUMPLE" if cumple_v_up_medio else "NO CUMPLE"
    verificaciones["v_up_medio"] = {
        "parametro": "Velocidad ascensional (caudal medio)",
        "valor": round(v_up_calc_m_h, 2),
        "unidad": "m/h",
        "criterio": f"≤ {Q.abr_v_up_diseno_m_h} m/h",
        "cumple": cumple_v_up_medio,
        "estado": estado_v_up_medio,
        "tipo": "obligatoria"
    }
    
    # [V-2] Velocidad ascensional a caudal máximo
    cumple_v_up_max = v_up_max_calc_m_h <= Q.abr_v_up_max_admisible_m_h
    estado_v_up_max = "CUMPLE" if cumple_v_up_max else "NO CUMPLE"
    verificaciones["v_up_max"] = {
        "parametro": "Velocidad ascensional (caudal máximo)",
        "valor": round(v_up_max_calc_m_h, 2),
        "unidad": "m/h",
        "criterio": f"≤ {Q.abr_v_up_max_admisible_m_h} m/h",
        "cumple": cumple_v_up_max,
        "estado": estado_v_up_max,
        "tipo": "obligatoria"
    }
    
    # [V-3] TRH verificado
    cumple_TRH = TRH_calc_h >= TRH_diseno_h
    estado_TRH = "CUMPLE" if cumple_TRH else "NO CUMPLE"
    verificaciones["TRH"] = {
        "parametro": "Tiempo de retención hidráulico",
        "valor": round(TRH_calc_h, 1),
        "unidad": "h",
        "criterio": f"≥ {TRH_diseno_h} h",
        "cumple": cumple_TRH,
        "estado": estado_TRH,
        "tipo": "obligatoria"
    }
    
    # [V-4] Largo mínimo de compartimento
    cumple_Lcomp = L_comp_m >= H_util_m
    estado_Lcomp = "CUMPLE" if cumple_Lcomp else "NO CUMPLE"
    verificaciones["L_comp"] = {
        "parametro": "Largo de compartimento vs profundidad",
        "valor": round(L_comp_m, 2),
        "unidad": "m",
        "criterio": f"≥ {H_util_m} m (profundidad)",
        "cumple": cumple_Lcomp,
        "estado": estado_Lcomp,
        "tipo": "obligatoria"
    }
    
    # [V-5] Relación L_comp / W (complementaria/informativa)
    cumple_relacion = (Q.abr_relacion_Lcomp_W_min <= relacion_Lcomp_W <= Q.abr_relacion_Lcomp_W_max)
    if relacion_Lcomp_W < Q.abr_relacion_Lcomp_W_min:
        estado_relacion = "BAJO RANGO"
    elif relacion_Lcomp_W > Q.abr_relacion_Lcomp_W_max:
        estado_relacion = "SOBRE RANGO"
    else:
        estado_relacion = "DENTRO RANGO"
    verificaciones["relacion_LW"] = {
        "parametro": "Relación L_comp / W",
        "valor": round(relacion_Lcomp_W, 2),
        "unidad": "-",
        "criterio": f"{Q.abr_relacion_Lcomp_W_min} - {Q.abr_relacion_Lcomp_W_max}",
        "cumple": cumple_relacion,
        "estado": estado_relacion,
        "tipo": "complementaria"
    }
    
    # [V-6] Número de compartimentos mínimo (complementaria)
    cumple_n_comp = n_comp >= Q.abr_num_compartimentos_min
    estado_n_comp = "CUMPLE" if cumple_n_comp else "NO CUMPLE"
    verificaciones["n_comp"] = {
        "parametro": "Número de compartimentos",
        "valor": n_comp,
        "unidad": "-",
        "criterio": f"≥ {Q.abr_num_compartimentos_min}",
        "cumple": cumple_n_comp,
        "estado": estado_n_comp,
        "tipo": "complementaria"
    }
    
    # Texto de resumen de verificaciones
    obligatorias = [v for v in verificaciones.values() if v["tipo"] == "obligatoria"]
    cumplen_todas = all(v["cumple"] for v in obligatorias)
    n_obligatorias = len(obligatorias)
    n_cumplen = sum(1 for v in obligatorias if v["cumple"])
    
    if cumplen_todas:
        texto_resumen_verificaciones = (
            f"Todas las verificaciones obligatorias CUMPLEN ({n_cumplen}/{n_obligatorias}). "
            f"El diseño del ABR es técnicamente aceptable."
        )
    else:
        texto_resumen_verificaciones = (
            f"ALERTA: {n_obligatorias - n_cumplen} verificación(es) obligatoria(s) no cumple(n). "
            f"Revise los parámetros de diseño."
        )
    
    # =============================================================================
    # RESULTADOS CONSOLIDADOS
    # =============================================================================
    
    return {
        # Parámetros de entrada
        "Q_m3_d": Q_m3_d,
        "Q_m3_h": round(Q_m3_h, 2),
        "Q_max_m3_d": round(Q_max_m3_d, 1),
        "Q_max_m3_h": round(Q_max_m3_h, 2),
        "factor_pico": factor_pico,
        
        # Parámetros de diseño adoptados
        "TRH_diseno_h": TRH_diseno_h,
        "n_compartimentos": n_comp,
        "v_up_diseno_m_h": v_up_diseno_m_h,
        "H_util_m": H_util_m,
        "H_zona_lodos_m": H_zona_lodos_m,
        "H_bordo_m": H_bordo_m,
        
        # Dimensiones geométricas
        "V_total_m3": round(V_total_m3, 1),
        "V_comp_m3": round(V_comp_m3, 2),
        "A_transversal_m2": round(A_transversal_m2, 2),
        "A_planta_m2": round(A_planta_m2, 2),
        "area_huella_layout_m2": round(A_planta_m2, 2),
        "W_m": round(W_m, 2),
        "L_comp_m": round(L_comp_m, 2),
        "L_total_m": round(L_total_m, 2),
        "largo_layout_m": round(L_total_m, 2),
        "ancho_layout_m": round(W_m, 2),
        "H_total_m": round(H_total_m, 2),
        # Claves adicionales para compatibilidad con esquema matplotlib
        "H_total_construccion_m": round(H_total_m, 2),
        "H_zona_liquida_m": round(H_util_m, 2),
        "H_zona_biogas_m": round(H_bordo_m * 0.6, 2),  # Estimación zona biogás
        "H_bordo_libre_m": round(H_bordo_m, 2),
        "num_compartimentos": n_comp,
        "Vup_m_h": round(v_up_calc_m_h, 2),
        "TRH_h": round(TRH_calc_h, 1),
        
        # Parámetros hidráulicos calculados
        "v_up_calc_m_h": round(v_up_calc_m_h, 2),
        "v_up_max_calc_m_h": round(v_up_max_calc_m_h, 2),
        "TRH_calc_h": round(TRH_calc_h, 1),
        "CHS_m_d": round(CHS_m_d, 2),
        
        # Parámetros de calidad (informativos)
        "DBO_entrada_mg_L": DBO_entrada_mg_L,
        "DQO_entrada_mg_L": DQO_entrada_mg_L,
        "SST_entrada_mg_L": SST_entrada_mg_L,
        "COV_kgDBO_m3_d": round(COV_kgDBO_m3_d, 2),
        
        # Verificaciones
        "verificaciones": verificaciones,
        "todas_verificaciones_cumplen": cumplen_todas,
        "texto_resumen_verificaciones": texto_resumen_verificaciones,
        
        # Metadatos
        "fuente": f"{ref_barber}; {ref_foxon}; {ref_ops}",
        "alcance": "Dimensionamiento básico de volumen y geometría. "
                   "No incluye: modelo cinético de remoción, cálculo de biogás, "
                   "balance de lodos, diseño de pantallas individuales."
    }


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
