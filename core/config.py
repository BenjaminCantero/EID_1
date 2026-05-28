"""
Configuración centralizada de UI para el proyecto EID.
Colores, fuentes, tamaños, espaciados y otras propiedades visuales.
"""

# ══════════════════════════════════════════════════════════════════════════
# PALETA DE COLORES
# ══════════════════════════════════════════════════════════════════════════

# Colores principales (tema azul/amarillo)
COLOR_FONDO_PRINCIPAL = "#1a2a4a"        # Azul oscuro
COLOR_FONDO_SECUNDARIO = "#2d4a7a"       # Azul medio
COLOR_FONDO_TERCIARIO = "#4a7abf"        # Azul claro
COLOR_FONDO_CANVAS = "#0d1b2e"           # Azul muy oscuro (para canvas)

# Colores de texto
COLOR_TEXTO_PRINCIPAL = "#f0f4ff"        # Blanco
COLOR_TEXTO_SECUNDARIO = "#e8eaf6"       # Gris claro
COLOR_TEXTO_RESALTADO = "#f5c842"        # Amarillo

# Colores de estados
COLOR_EXITO = "#4caf50"                  # Verde
COLOR_ERROR = "#e53935"                  # Rojo
COLOR_ADVERTENCIA = "#ff9800"            # Naranja

# Alias para compatibilidad con código existente
AZUL_OSCURO = COLOR_FONDO_PRINCIPAL
AZUL_MEDIO = COLOR_FONDO_SECUNDARIO
AZUL_CLARO = COLOR_FONDO_TERCIARIO
BLANCO = COLOR_TEXTO_PRINCIPAL
GRIS_TEXTO = COLOR_TEXTO_SECUNDARIO
AMARILLO = COLOR_TEXTO_RESALTADO
VERDE = COLOR_EXITO
ROJO = COLOR_ERROR
NARANJA = COLOR_ADVERTENCIA


# ══════════════════════════════════════════════════════════════════════════
# TIPOGRAFÍA
# ══════════════════════════════════════════════════════════════════════════

# Fuentes
FUENTE_TITULO = ("Helvetica", 16, "bold")
FUENTE_SUBTITULO = ("Helvetica", 14, "bold")
FUENTE_LABEL_GRANDE = ("Helvetica", 13, "bold")
FUENTE_LABEL_NORMAL = ("Helvetica", 11, "bold")
FUENTE_LABEL_PEQUEÑO = ("Helvetica", 10, "bold")
FUENTE_LABEL_MUY_PEQUEÑO = ("Helvetica", 9, "bold")
FUENTE_LABEL_MINUSCULA = ("Helvetica", 8, "bold")
FUENTE_LABEL_EXTRA_PEQUEÑO = ("Helvetica", 7, "bold")

FUENTE_TEXTO_NORMAL = ("Helvetica", 11)
FUENTE_TEXTO_PEQUEÑO = ("Helvetica", 10)
FUENTE_TEXTO_MUY_PEQUEÑO = ("Helvetica", 9)

FUENTE_MONOESPACIADA_GRANDE = ("Courier", 13)
FUENTE_MONOESPACIADA_NORMAL = ("Courier", 10)
FUENTE_MONOESPACIADA_PEQUEÑO = ("Courier", 9)
FUENTE_MONOESPACIADA_MINUSCULA = ("Courier", 8)


# ══════════════════════════════════════════════════════════════════════════
# DIMENSIONES DE VENTANA
# ══════════════════════════════════════════════════════════════════════════

# Ventana principal
VENTANA_ANCHO = 1050
VENTANA_ALTO = 700
VENTANA_ANCHO_MIN = 900
VENTANA_ALTO_MIN = 620

# Altura de barra superior
ALTURA_BARRA_SUPERIOR = 45

# Canvas
ANCHO_CANVAS_CONICA = 340
ALTO_CANVAS_CONICA = 280

ANCHO_CANVAS_LIMITES = 320
ALTO_CANVAS_LIMITES = 220


# ══════════════════════════════════════════════════════════════════════════
# ESPACIADOS Y PADDINGS
# ══════════════════════════════════════════════════════════════════════════

# Padding estándar
PADDING_GRANDE = 20
PADDING_NORMAL = 15
PADDING_MEDIO = 10
PADDING_PEQUEÑO = 5
PADDING_MUY_PEQUEÑO = 2

# Pady (espaciado vertical)
PADY_GRANDE = (40, 5)
PADY_NORMAL = (15, 5)
PADY_MEDIO = (10, 5)
PADY_PEQUEÑO = (5, 0)

# Padx (espaciado horizontal)
PADX_ENTRADA = 10
PADX_BOTON = 12

# Border
BORDE_NORMAL = 2
BORDE_FINO = 1


# ══════════════════════════════════════════════════════════════════════════
# COMPONENTES DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════

# Campos de entrada RUT
ENTRY_RUT_ANCHO = 18
ENTRY_RUT_ANCHO_PEQUEÑO = 16
FONT_ENTRY_RUT = ("Courier", 13)
FONT_ENTRY_NORMAL = ("Courier", 12)
FONT_ENTRY_PEQUEÑO = ("Courier", 9)

# Placeholder
PLACEHOLDER_RUT = "12.345.678-9"


# ══════════════════════════════════════════════════════════════════════════
# TEXTAREA / SCROLLED TEXT
# ══════════════════════════════════════════════════════════════════════════

# Pasos matemáticos
TEXTAREA_PASOS_ALTO = 18
TEXTAREA_PASOS_ANCHO = 55
TEXTAREA_PASOS_FONT = ("Courier", 9)

# Análisis de límites
TEXTAREA_ANALISIS_ALTO = 14
TEXTAREA_ANALISIS_ANCHO = 50
TEXTAREA_ANALISIS_FONT = ("Courier", 9)


# ══════════════════════════════════════════════════════════════════════════
# TABLA (TREEVIEW)
# ══════════════════════════════════════════════════════════════════════════

TABLA_ALTO = 6
TABLA_COLUMNA_X_ANCHO = 100
TABLA_COLUMNA_FX_ANCHO = 120
TABLA_COLUMNA_LADO_ANCHO = 70
TABLA_FONT = ("Courier", 9)
TABLA_HEADING_FONT = ("Helvetica", 9, "bold")


# ══════════════════════════════════════════════════════════════════════════
# BOTONES
# ══════════════════════════════════════════════════════════════════════════

# Dimensiones
BOTON_PADX = 12
BOTON_PADY = 5
BOTON_PADX_PEQUEÑO = 10
BOTON_PADY_PEQUEÑO = 3
BOTON_PADX_MINUSCULO = 8
BOTON_PADY_MINUSCULO = 3

# Estados
RELIEF_FLAT = "flat"


# ══════════════════════════════════════════════════════════════════════════
# MARCOS Y DIVISORES
# ══════════════════════════════════════════════════════════════════════════

# Marco de entrada RUT
MARCO_RUT_PADX = 15
MARCO_RUT_PADY = 10

# Marco de elementos geométricos
MARCO_ELEMENTOS_PADX = 8
MARCO_ELEMENTOS_PADY = 8

# Marco de resumen
MARCO_RESUMEN_PADX = 8
MARCO_RESUMEN_PADY = 8

# Marco de defensa
MARCO_DEFENSA_PADX = 8
MARCO_DEFENSA_PADY = 8

# Divisor visual
DIVISOR_ALTURA = 2
DIVISOR_ANCHO = 400


# ══════════════════════════════════════════════════════════════════════════
# ETIQUETAS Y TEXTO
# ══════════════════════════════════════════════════════════════════════════

# Ancho para labels
LABEL_ANCHO = 14
LABEL_ANCHO_GRANDE = 22

# Wraplength para labels largos
WRAP_LENGTH_NORMAL = 300
WRAP_LENGTH_GRANDE = 320


# ══════════════════════════════════════════════════════════════════════════
# ESTILOS TTKSTYLE (Para Notebook y Treeview)
# ══════════════════════════════════════════════════════════════════════════

# Tema
TEMA_TTK = "default"

# Padding para tabs
TAB_PADDING = [15, 6]


# ══════════════════════════════════════════════════════════════════════════
# INFORMACIÓN Y VERSIÓN
# ══════════════════════════════════════════════════════════════════════════

TITULO_VENTANA = "EID MAT1186 — Cónicas y Límites · UCT 2026"
TITULO_BARRA = "EID N°1 — MAT1186 · Introducción al Cálculo · UCT 2026"
SUBTITULO_BARRA = "Versión 2026 · Benjamin C. Eduardo D. Ricardo G."

TITULO_EID = "Evaluación Integrada de Desempeño N°1"
SUBTITULO_EID = "Análisis y Modelamiento de Secciones Cónicas\ny Funciones por Tramos a partir del RUT"

CURSO = "MAT1186 — Introducción al Cálculo"
INSTITUCION = "Universidad Católica de Temuco"
CARRERA = "Ingeniería Civil en Informática"
AÑO = "2026"
