"""
Constantes matemáticas y valores globales para el proyecto EID.
Centraliza todos los valores "magic numbers" para fácil ajuste.
"""

# ══════════════════════════════════════════════════════════════════════════
# TOLERANCIAS MATEMÁTICAS
# ══════════════════════════════════════════════════════════════════════════

# Tolerancia para comparaciones con cero (comparar floats)
TOLERANCIA_CERO = 1e-9

# Tolerancia más estricta para cálculos de raíz cuadrada
TOLERANCIA_RAIZ = 1e-10

# Tolerancia para convergencia de métodos iterativos (Newton-Raphson, etc.)
TOLERANCIA_CONVERGENCIA = 1e-10

# Máximo número de iteraciones en métodos numéricos
MAX_ITERACIONES_METODOS_NUMERICOS = 100
MAX_ITERACIONES_SERIES_TAYLOR = 30


# ══════════════════════════════════════════════════════════════════════════
# PRECISIÓN DECIMAL Y REDONDEO
# ══════════════════════════════════════════════════════════════════════════

# Decimales para mostrar en UI
DECIMALES_DISPLAY = 4
DECIMALES_TABLA = 4
DECIMALES_COORDENADAS = 2

# Formato para valores científicos
FORMATO_CIENTIFICO = ".4g"


# ══════════════════════════════════════════════════════════════════════════
# PARÁMETROS DE RUT CHILENO
# ══════════════════════════════════════════════════════════════════════════

# Longitud esperada del cuerpo del RUT
LONGITUD_RUT_MIN = 7
LONGITUD_RUT_MAX = 8
LONGITUD_RUT_FORMATEADO_MIN = 9

# Serie para validación con módulo 11
SERIE_MODULO_11 = [2, 3, 4, 5, 6, 7]
DIVISOR_MODULO_11 = 11

# Dígitos verificadores especiales
DV_CERO = "0"
DV_K = "K"


# ══════════════════════════════════════════════════════════════════════════
# PARÁMETROS DE CÓNICAS
# ══════════════════════════════════════════════════════════════════════════

# Tipos de cónicas
TIPO_CIRCUNFERENCIA = "Circunferencia"
TIPO_ELIPSE = "Elipse"
TIPO_HIPERBOLA = "Hipérbola"
TIPO_PARABOLA = "Parábola"
TIPO_DEGENERADA = "Degenerada"

# Lista de todos los tipos válidos
TIPOS_CONICAS_VALIDOS = [
    TIPO_CIRCUNFERENCIA,
    TIPO_ELIPSE,
    TIPO_HIPERBOLA,
    TIPO_PARABOLA,
    TIPO_DEGENERADA,
]

# Denominación de elementos geométricos
ELEMENTO_CENTRO = "Centro"
ELEMENTO_RADIO = "Radio"
ELEMENTO_VERTICE = "Vértice(s)"
ELEMENTO_FOCOS = "Foco(s)"
ELEMENTO_SEMI_EJE_MAYOR = "a (semi-eje mayor)"
ELEMENTO_SEMI_EJE_MENOR = "b (semi-eje menor)"
ELEMENTO_DIRECTRIZ = "Directriz"


# ══════════════════════════════════════════════════════════════════════════
# PARÁMETROS DE LÍMITES Y FUNCIONES
# ══════════════════════════════════════════════════════════════════════════

# Tipos de discontinuidad
TIPO_DISCONTINUIDAD_REMOVIBLE = "removible"
TIPO_DISCONTINUIDAD_SALTO = "salto"
TIPO_DISCONTINUIDAD_INFINITA = "infinita"

# Lista de tipos válidos
TIPOS_DISCONTINUIDAD_VALIDOS = [
    TIPO_DISCONTINUIDAD_REMOVIBLE,
    TIPO_DISCONTINUIDAD_SALTO,
    TIPO_DISCONTINUIDAD_INFINITA,
]

# Residuos (d8 % 3) que determinan el tipo
RESIDUO_REMOVIBLE = 0
RESIDUO_SALTO = 1
RESIDUO_INFINITA = 2

# Precisión para aproximar al límite
EPSILON_LIMITE = 1e-7

# Cantidad de puntos en tabla de valores
PUNTOS_TABLA_VALORES = 11
PASO_TABLA_VALORES = 0.2


# ══════════════════════════════════════════════════════════════════════════
# PARÁMETROS DE GRÁFICAS Y VISUALIZACIÓN
# ══════════════════════════════════════════════════════════════════════════

# Rango de ejes para gráficas de cónicas
RANGO_GRAFICA_CONICA_MIN = -10.0
RANGO_GRAFICA_CONICA_MAX = 10.0

# Rango de ejes para gráficas de límites
RANGO_GRAFICA_LIMITES_X_MIN = -5.0
RANGO_GRAFICA_LIMITES_X_MAX = 5.0
RANGO_GRAFICA_LIMITES_Y_MIN = -10.0
RANGO_GRAFICA_LIMITES_Y_MAX = 10.0

# Densidad de puntos en gráficas
DENSIDAD_PUNTOS_GRAFICA = 0.1


# ══════════════════════════════════════════════════════════════════════════
# PARÁMETROS DE SERIE DE TAYLOR
# ══════════════════════════════════════════════════════════════════════════

# Límites para funciones exponenciales
LIMITE_EXP_MAXIMO = 20
LIMITE_EXP_MINIMO = -20
VALOR_EXP_MAXIMO_APROX = 485165195.4

# Aproximaciones de constantes matemáticas
PI_2 = 6.283185307179586  # 2*pi
PI = 3.141592653589793    # pi

# Precisión de series de Taylor
PRECISION_SERIE_TAYLOR = 1e-15


# ══════════════════════════════════════════════════════════════════════════
# MENSAJES Y ETIQUETAS
# ══════════════════════════════════════════════════════════════════════════

ETIQUETA_PASOS_VALIDACION = "═══ VALIDACIÓN DEL RUT ═══"
ETIQUETA_PASOS_COEFICIENTES = "═══ CONSTRUCCIÓN DE LA ECUACIÓN ═══"
ETIQUETA_PASOS_CANONICO = "═══ FORMA CANÓNICA ═══"
ETIQUETA_PASOS_LIMITES = "═══ ANÁLISIS DE LÍMITES ═══"
ETIQUETA_PASOS_FUNCION = "═══ FUNCIÓN GENERADA ═══"

ETIQUETA_MATEMATICA = "Desarrollo matemático:"
ETIQUETA_GRAFICA = "Gráfica:"
ETIQUETA_TABLA_VALORES = "Tabla de valores cercanos al punto a:"
ETIQUETA_RESUMEN_RAPIDO = "Resumen rápido:"
ETIQUETA_ELEMENTOS_GEOMETRICOS = "Elementos geométricos (completar en defensa):"
ETIQUETA_DEFENSA_ORAL = "Completar durante la defensa oral:"
