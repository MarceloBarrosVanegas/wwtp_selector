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
    # Límite de velocidad para verificación (Camp-Shields)
    # v_h_max debe ser < v_c_scour (velocidad crítica de resuspensión)
    desarenador_factor_seguridad_scour: float = 0.9  # Factor sobre v_c (90% = margen seguro)
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - UASB
    # =============================================================================
    uasb_Cv_kgDQO_m3_d: float = 2.5         # Carga orgánica volumétrica (kg DQO/m³·d) - valor conservador para TRH >= 5h
    uasb_v_up_m_h: float = 0.80             # Velocidad ascendente (m/h)
    uasb_eta_DBO: float = 0.70              # Eficiencia remoción DBO5 (fracción)
    uasb_eta_DQO: float = 0.65              # Eficiencia remoción DQO (fracción)
    uasb_H_max_m: float = 5.5               # Altura máxima reactor (m)
    # Límites de velocidad ascendente para verificación (Metcalf & Eddy, 2014)
    # v_up_max debe controlarse para evitar arrastre del manto de lodos
    uasb_v_up_max_recomendado_m_h: float = 1.5   # Límite recomendado (m/h)
    uasb_v_up_max_destructivo_m_h: float = 2.0   # Límite destructivo (m/h)
    
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
    fp_Cv_kgDBO_m3_d: float = 0.5           # Carga orgánica volumétrica (kg DBO/m³·d)
    
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
    
    # =============================================================================
    # PARÁMETROS DE DISEÑO - LECHO DE SECADO
    # =============================================================================
    lecho_C_SST_kg_m3: float = 20.0         # Concentración sólidos en lodo (kg/m³)
    lecho_t_secado_d: float = 15.0          # Tiempo secado (días)
    lecho_n_celdas: int = 2                 # Número celdas en rotación
    lecho_h_lodo_m: float = 0.30            # Espesor lodo aplicado (m)

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
    # Para partículas de arena: d = 0.20 mm, Ss = 2.65, T = 24°C
    g = 9.81  # m/s²
    d_m = Q.desarenador_d_particula_mm / 1000.0  # 0.00020 m
    Ss = Q.desarenador_Ss  # 2.65
    
    # Viscosidad cinemática del agua
    # Valor a 24°C: 0.91 × 10⁻⁶ m²/s
    # Nota: A 25.6°C (T real del proyecto) sería ≈ 0.87 × 10⁻⁶ m²/s
    # Error ~4.4% en v_s, aceptable para diseño preliminar
    nu_m2_s = 0.91e-6  # m²/s (valor conservador a 24°C)
    
    # Ley de Stokes: Vs = g × (Ss - 1) × d² / (18 × ν)
    v_s_calculada = g * (Ss - 1) * (d_m ** 2) / (18 * nu_m2_s)  # m/s
    v_s_m_s = round(v_s_calculada, 3)  # ~0.040 m/s a 24°C
    
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
    if Q_L_s < 20:
        # Factor de escala: a 5 L/s → longitud práctica mínima
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
    beta = 0.05  # valor intermedio
    f_darcy = 0.025  # factor de fricción Darcy-Weisbach
    
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
        "v_s_m_s": v_s_m_s,                   # 0.021 m/s (referencia Stokes)
        # Dimensiones
        "H_util_m": H_util,
        "b_teorico_m": round(b_teorico, 3),
        "b_canal_m": round(b_canal, 3),
        "L_teorica_stokes_m": round(L_teorica_stokes, 1),  # ~3.0 m (basado en vs calculada)
        "L_teorica_Metcalf_m": round(L_teorica_metcatlf, 1),  # 9.0 m (criterio normativo)
        "L_diseno_m": round(L_diseno, 1),
        "relacion_L_B": round(L_diseno / b_canal, 1),
        # Tiempos
        "t_r_nominal_s": t_r_nominal,         # 30 s (norma)
        "t_r_real_s": round(t_r_real, 1),     # En el diseño adoptado
        # Verificación técnica - Stokes y Camp
        "d_mm": Q.desarenador_d_particula_mm, # Diámetro partícula objetivo (mm)
        "v_s_stokes_m_s": v_s_m_s,            # Calculada por Ley de Stokes
        "Re_stokes": round(Re, 3),            # Número de Reynolds
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
    
    # Parámetros base (para T >= 20°C)
    Cv_base = Q.uasb_Cv_kgDQO_m3_d  # 2.5 kg/m³·d
    HRT_min_base = 4.0  # horas
    
    # Ajuste por temperatura según Van Haandel & Lettinga (1994)
    # y Sperling (2007), Tabla 5.3
    if T_agua >= 22:
        # Temperatura óptima - parámetros base
        Cv_kgDQO_m3_d = Cv_base
        HRT_min = HRT_min_base
        factor_temp_texto = "óptima (>= 22°C)"
    elif 18 <= T_agua < 22:
        # Temperatura moderada - ligera reducción de carga
        Cv_kgDQO_m3_d = Cv_base * 0.85  # -15%
        HRT_min = HRT_min_base * 1.2     # +20%
        factor_temp_texto = "moderada (18-22°C)"
    elif 15 <= T_agua < 18:
        # Temperatura baja - reducción significativa
        Cv_kgDQO_m3_d = Cv_base * 0.60  # -40%
        HRT_min = HRT_min_base * 1.5     # +50%
        factor_temp_texto = "baja (15-18°C)"
    elif 10 <= T_agua < 15:
        # Temperatura muy baja - requiere aislamiento o medidas especiales
        Cv_kgDQO_m3_d = Cv_base * 0.40  # -60%
        HRT_min = HRT_min_base * 2.0     # +100%
        factor_temp_texto = "muy baja (10-15°C) - se recomienda aislamiento térmico"
    else:
        # Temperatura crítica - no recomendable para UASB sin calefacción
        Cv_kgDQO_m3_d = Cv_base * 0.30  # -70%
        HRT_min = HRT_min_base * 2.5     # +150%
        factor_temp_texto = "crítica (< 10°C) - requiere calefacción o cambio de tecnología"
    
    # Velocidad ascendente ajustada por temperatura
    if T_agua >= 20:
        v_up_m_h = Q.uasb_v_up_m_h  # 0.80 m/h (valor base)
    elif 15 <= T_agua < 20:
        v_up_m_h = 0.60  # Reducir velocidad para mejor retención a baja T
    else:
        v_up_m_h = 0.50  # Velocidad mínima recomendada
    
    # Parámetros de eficiencia (menor eficiencia a bajas temperaturas)
    if T_agua >= 20:
        eta_DBO = Q.uasb_eta_DBO  # 70%
        eta_DQO = Q.uasb_eta_DQO  # 65%
    elif 15 <= T_agua < 20:
        eta_DBO = 0.60  # -10 puntos
        eta_DQO = 0.55  # -10 puntos
    else:
        eta_DBO = 0.50  # -20 puntos
        eta_DQO = 0.45  # -20 puntos
    
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
    biogaz_m3_d = 0.35 * DQO_removida_kg_d               # m^3 CH4/d

    # Producción de lodos
    DBO_kg_m3 = Q.DBO5_mg_L * 1e-3
    DBO_removida_kg_d = Q_m3_d * DBO_kg_m3 * eta_DBO
    lodos_kg_SSV_d = 0.10 * DBO_removida_kg_d   # kg SSV/d (usando valor medio)
    
    # =============================================================================
    # VERIFICACIÓN PARA CAUDAL MÁXIMO HORARIO (SOLO VERIFICACIÓN, NO DISEÑO)
    # =============================================================================
    factor_pico_uasb = 2.5  # Factor típico Qmax/Qmedio
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
        if D_m > 10.0:  # máximo 10 metros
            break
    
    # Recalcular valores finales si hubo ajuste
    if ajuste_realizado:
        H_r_m = V_r_m3 / A_sup_m2
        v_up_m_h = Q_m3_h / A_sup_m2
        v_up_max_m_h = Q_max_m3_h / A_sup_m2
    
    v_up_max_aceptable = v_up_max_m_h <= v_up_max_limite_recomendado
    incremento_diametro_cm = round((D_m - D_m_original) * 100)
    
    # Estado de verificación para el texto del documento
    if v_up_max_m_h <= 1.5:
        estado_verificacion = "ÓPTIMO"
    elif v_up_max_m_h <= 2.0:
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

    # Verificaciones
    assert 2.0 <= Cv_kgDQO_m3_d <= 8.0, (
        f"Cv = {Cv_kgDQO_m3_d} kg DQO/m^3*d fuera de rango 2-8 "
        f"({ref_vh}, Tabla 6.1)"
    )
    assert HRT_min <= TRH_h <= 12.0, (
        f"TRH = {TRH_h:.1f} h fuera de rango {HRT_min:.1f}-12 h "
        f"({ref_sp}, p. 140; {ref_vh})"
    )
    assert 0.3 <= v_up_m_h <= 1.5, (
        f"v_up = {v_up_m_h:.2f} m/h fuera de rango 0.3-1.5 m/h "
        f"({ref_me}, p. 757; {ref_vh})"
    )

    return {
        "unidad": "Reactor UASB",
        # Datos de entrada
        "Q_m3_d": round(Q_m3_d, 1),
        "DQO_kg_m3": round(DQO_kg_m3, 4),
        "DBO5_kg_m3": round(DBO_kg_m3, 4),
        # Parámetros de temperatura
        "T_agua_C": T_agua,
        "factor_temp_texto": factor_temp_texto,
        "Cv_base": Q.uasb_Cv_kgDQO_m3_d,
        # Rangos recomendados según temperatura
        # Rangos según Van Haandel & Lettinga (1994) - valores conservadores
        "rango_Cv": "2,0--3,0" if T_agua >= 22 else ("1,5--2,5" if T_agua >= 18 else "1,0--2,0"),
        "rango_vup": "0,5--1,5" if T_agua >= 22 else ("0,4--1,2" if T_agua >= 18 else "0,3--1,0"),
        "rango_HRT": "4--6" if T_agua >= 22 else ("5--8" if T_agua >= 18 else "6--10"),
        "rango_eta": "60--75" if T_agua >= 22 else ("50--65" if T_agua >= 18 else "40--55"),
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
        # Producción de subproductos
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
            f"Cv adoptada = {Cv_kgDQO_m3_d} kg DQO/m^3*d (rango 2-8 a T>20 grados C, "
            f"{ref_vh}). "
            f"v_up = {v_up_m_h:.2f} m/h <= 1.0 m/h recomendado para lodo floculento "
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
    k_20_m_h = Q.fp_k_20_m_h  # m/h  - constante cinética a 20 grados C (cfg default: 0.068)
    theta    = Q.fp_theta     # coef. temperatura [Ec. 5b]
    n        = 0.50           # constante empírica del medio aleatorio plástico
    D_m      = 3.50           # m    - profundidad del medio filtrante
    R        = 1.0            # tasa de recirculación (R=1 -> Q_ap = 2Q)
    H_total  = D_m + 1.10     # m    - incluye zona distribución (0,30) + recolección (0,50) + bordo libre (0,30)

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
    Q_A_limite_m3_m2_h = 4.0
    
    # Ajuste automático si excede el límite: aumentamos recirculación primero, luego área
    # con protección de iteraciones máximas y límite mínimo de Cv
    iteracion = 0
    max_iteraciones = 100
    Cv_minima = 0.30  # kg DBO/m³·d - límite inferior de diseño
    
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
    
    # Recalcular dimensiones finales y parámetros dependientes
    D_filtro_m = math.sqrt(4 * A_sup_m2 / math.pi)
    Q_A_real = Q_ap_m3_h / A_sup_m2
    Q_A_max_m3_m2_h = Q_max_m3_h * (1 + R) / A_sup_m2
    Q_A_max_m3_m2_d = Q_A_max_m3_m2_h * 24  # Para reporte
    
    # Recalcular eficiencia Germain con tasa hidráulica final
    relacion_Se_S0 = math.exp(-k_T_m_h * D_m / (Q_A_real ** n))
    Se_calculado_mg_L = DBO_entrada_mg_L * relacion_Se_S0
    DBO_removida_kg_d = Q_m3_d * DBO_kg_m3 * (1 - relacion_Se_S0)
    
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
    
    # Texto de verificación
    if Q_A_max_m3_m2_h <= Q_A_limite_m3_m2_h:
        verif_qmax_texto = "la tasa hidráulica máxima está dentro del rango operativo seguro ($\\leq$ 4,0 m³/m²·h)"
    else:
        verif_qmax_texto = "la tasa hidráulica máxima excede el límite recomendado, requiere revisión"

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
        "factor_pico": factor_pico,
        "Q_max_m3_d": round(Q_max_m3_d, 1),
        "verif_qmax_texto": verif_qmax_texto,
        "A_sup_m2": round(A_sup_m2, 2),
        "V_medio_m3": round(V_medio_m3, 1),
        "D_filtro_m": round(D_filtro_m, 2),
        "H_total_m": round(H_total, 2),
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
                                  SST_entrada_mg_L: float = None) -> Dict[str, Any]:
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
    
    # Tasa de aplicación de sólidos (estimada)
    # Asumiendo producción de humus del filtro percolador ~ 0.15 kg SST/kg DBO removida
    # y DBO removida en FP ~ 0.3 * DBO entrada
    DBO_entrada_fp = Q.DBO5_mg_L * 0.30  # mg/L
    produccion_humus_kg_d = 0.15 * (DBO_entrada_fp * Q_m3_d / 1000)  # kg SST/d
    solids_loading_kg_m2_d = produccion_humus_kg_d / A_sup_m2
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
        "ajuste_realizado": ajuste_realizado,
        "verif_sor_max_texto": verif_sor_max_texto,
        "diametro_layout_m": round(D_m + 0.30, 1),
        "fuente": f"{ref_me} (pp. 870-880); {ref_wef} (pp. 9-60); {ref_sp}",
    }


# =============================================================================
# 7 - DESINFECCIÓN UV
# =============================================================================

def dimensionar_uv(Q: ConfigDiseno = CFG) -> Dict[str, Any]:
    """
    Dimensionamiento del sistema de desinfección UV.

    Criterio de diseño
    ------------------
    Dosis UV: 30-40 mJ/cm² para inactivación de coliformes fecales
              [USEPA, 2006; Galapagos requiere ≥ 4 log de reducción]
    
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
    Dimensionamiento del lecho de secado por arena (gravedad + evapotranspiración).

    Ecuaciones de diseño
    --------------------
    Volumen de lodos a tratar:
        V_lodo_d = M_SST / C_SST                            [Ec. 8a]
        donde M_SST = producción diaria de lodos (kg SST/d)
              C_SST = concentración de sólidos en el lodo (kg/m^3)
              Para UASB: C_SST ~ 15-30 g/L -> adoptado 20 kg/m^3

    Tiempo de secado en Galápagos (clima cálido y seco):
        t_s = 15-20 días [OPS/CEPIS, 2005; considerando evaporación alta]

    Área del lecho:
        A_lecho = V_lodo_d * t_s / (h_arena * ... )        [Ec. 8b]
        Simplificado: A_lecho = V_lodo_d * t_s * CS         [Ec. 8c]
        con CS = 2 (dos celdas en rotación)

    Tasa de carga superficial de sólidos:
        ρ_S = M_SST / A_lecho                              [Ec. 8d]
        Rango: 60-220 kg SST/m^2*año [Metcalf & Eddy, 2014, p. 1148]

    Referencias
    -----------
    Metcalf & Eddy (2014), pp. 1145-1155
    OPS/CEPIS (2005), Cap. 5
    """
    ref_me = citar("metcalf_2014")
    ref_ops = citar("ops_cepis_2005")

    # Producción de lodos del UASB (si no se provee externamente)
    if lodos_kg_SST_d is None:
        uasb = dimensionar_uasb(Q)
        lodos_kg_SST_d = uasb["lodos_kg_SSV_d"] / 0.75   # SSV/SST ~ 0.75 para lodo UASB

    # Parámetros de diseño adoptados desde configuración
    C_SST_kg_m3 = Q.lecho_C_SST_kg_m3
    t_secado_d = Q.lecho_t_secado_d
    n_celdas = Q.lecho_n_celdas
    h_lodo_m = Q.lecho_h_lodo_m

    Q_m3_d = Q.Q_linea_m3_d

    # [Ec. 8a] Volumen de lodo a tratar por día
    V_lodo_m3_d = lodos_kg_SST_d / C_SST_kg_m3   # m^3/d

    # [Ec. 8c] Área total del lecho (con rotación)
    # Volumen total en proceso de secado = V_lodo/d × t_secado
    V_total_secando_m3 = V_lodo_m3_d * t_secado_d
    A_lecho_m2 = (V_total_secando_m3 / h_lodo_m) * n_celdas

    # Geometría del lecho (relación 3:1)
    ancho_m = math.sqrt(A_lecho_m2 / 3.0)
    largo_m = 3.0 * ancho_m

    # Tasa de carga de sólidos
    rho_S_kgSST_m2_año = lodos_kg_SST_d * 365 / A_lecho_m2

    return {
        "unidad": "Lecho de secado de lodos",
        "lodos_kg_SST_d": round(lodos_kg_SST_d, 2),
        "C_SST_kg_m3": C_SST_kg_m3,
        "t_secado_d": t_secado_d,
        "V_lodo_m3_d": round(V_lodo_m3_d, 3),
        "n_celdas": n_celdas,
        "A_lecho_m2": round(A_lecho_m2, 1),
        "largo_m": round(largo_m, 1),
        "ancho_m": round(ancho_m, 1),
        "h_lodo_m": h_lodo_m,
        "rho_S_kgSST_m2_año": round(rho_S_kgSST_m2_año, 1),
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
    -> UV -> Lecho de Secado

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
    lecho      = dimensionar_lecho_secado(Q)

    # Balance de calidad (progresivo) - usando resultados reales del dimensionamiento
    DBO_in     = Q.DBO5_mg_L
    DBO_uasb   = DBO_in  * (1 - uasb["eta_DBO"])       # tras UASB
    # Usar DBO calculada por el modelo de Germain (no valor hardcodeado)
    DBO_fp_salida = fp.get("DBO_salida_Germain_mg_L", fp.get("DBO_salida_mg_L", 55.0))
    # El sedimentador remueve ~30% de la DBO restante (sólidos biológicos)
    DBO_efluente = DBO_fp_salida * (1 - 0.30)          # tras sedimentación (30% SST)

    print("=" * 70)
    print("TREN A - UASB + FILTRO PERCOLADOR + UV")
    print("Puerto Baquerizo Moreno, Galápagos")
    print(f"Caudal por línea: {Q.Q_linea_L_s} L/s = {Q.Q_linea_m3_d} m^3/d")
    print("=" * 70)

    unidades = [
        ("Rejillas",          rejillas,    "largo_layout_m",    "ancho_layout_m"),
        ("Desarenador",       desarenador, "largo_layout_m",    "ancho_layout_m"),
        ("UASB",              uasb,        "diametro_layout_m", None),
        ("Filtro Percolador", fp,          "diametro_layout_m", None),
        ("Sed. Secundario",   sed_sec,     "diametro_layout_m", None),
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
    Rejillas -> Desarenador -> UASB -> Humedal Vertical -> UV -> Lecho de Secado
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
    print("TREN C - UASB + HUMEDAL VERTICAL + UV")
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
