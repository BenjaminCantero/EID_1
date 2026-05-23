"""
Servicios de negocio para lógica de Cónicas y Límites.
Separa la lógica de negocio de la capa de presentación (UI).
Retorna objetos de datos estructurados para facilitar reutilización y pruebas.

Patrón: Funciones de servicio que retornan dataclasses (mejor que diccionarios anidados).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from core.rut import validar_rut
from core.conica import (
    calcular_coeficientes, clasificar_conica, ecuacion_str, forma_canonica
)
from core.limites import (
    seleccionar_caso, construir_funcion, calcular_limites, evaluar_funcion
)
from core.exceptions import RUTInvalidoError, ConicaInvalidaError, LimiteInvalidoError
from core.validators import (
    validar_rut_str, validar_digitos, validar_coeficientes_conica,
    validar_punto_discontinuidad, validar_caso_tipo, validar_tramos,
    validar_tabla_valores
)


@dataclass
class ConicaAnalysis:
    """Estructura de datos para encapsular los resultados del análisis de cónicas."""
    es_valido: bool = False
    pasos_validacion: List[str] = field(default_factory=list)
    digitos: List[int] = field(default_factory=list)
    dv: str = ""
    rut_formateado: str = ""
    A: float = 0.0
    B: float = 0.0
    C: float = 0.0
    D: float = 0.0
    E: float = 0.0
    pasos_coeficientes: List[str] = field(default_factory=list)
    ajustes: List[str] = field(default_factory=list)
    tipo_conica: str = ""
    ecuacion_general: str = ""
    ecuacion_canonica: str = ""
    pasos_canonica: List[str] = field(default_factory=list)
    elementos_geometricos: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        """Convierte el análisis a diccionario para fácil serialización."""
        return {
            "validacion": {
                "es_valido": self.es_valido,
                "pasos": self.pasos_validacion,
                "digitos": self.digitos,
                "dv": self.dv,
                "rut_formateado": self.rut_formateado,
            },
            "coeficientes": {
                "A": self.A,
                "B": self.B,
                "C": self.C,
                "D": self.D,
                "E": self.E,
                "pasos": self.pasos_coeficientes,
                "ajustes": self.ajustes,
            },
            "clasificacion": {
                "tipo": self.tipo_conica,
            },
            "ecuacion": {
                "general": self.ecuacion_general,
            },
            "forma_canonica": {
                "canonica": self.ecuacion_canonica,
                "pasos": self.pasos_canonica,
                "elementos": self.elementos_geometricos,
            },
        }


@dataclass
class LimitesAnalysis:
    """Estructura de datos para encapsular los resultados del análisis de límites."""
    es_valido: bool = False
    pasos_validacion: List[str] = field(default_factory=list)
    digitos: List[int] = field(default_factory=list)
    dv: str = ""
    rut_formateado: str = ""
    a: int = 0
    caso_tipo: str = ""
    razon_caso: str = ""
    descripcion_funcion: str = ""
    tramos_info: Dict[str, Any] = field(default_factory=dict)
    lim_izquierda: Any = None
    lim_derecha: Any = None
    lim_existe: bool = False
    lim_valor: Any = None
    f_en_a: Any = None
    es_continua: bool = False
    tipo_discontinuidad: str = ""
    pasos_limites: List[str] = field(default_factory=list)
    tabla_valores: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self):
        """Convierte el análisis a diccionario para fácil serialización."""
        return {
            "validacion": {
                "es_valido": self.es_valido,
                "pasos": self.pasos_validacion,
                "digitos": self.digitos,
                "dv": self.dv,
                "rut_formateado": self.rut_formateado,
            },
            "funcion": {
                "punto_a": self.a,
                "caso_tipo": self.caso_tipo,
                "razon_caso": self.razon_caso,
                "descripcion": self.descripcion_funcion,
                "tramos": self.tramos_info,
            },
            "limites": {
                "lim_izquierda": self.lim_izquierda,
                "lim_derecha": self.lim_derecha,
                "lim_existe": self.lim_existe,
                "lim_valor": self.lim_valor,
                "f_en_a": self.f_en_a,
                "es_continua": self.es_continua,
                "tipo_discontinuidad": self.tipo_discontinuidad,
                "pasos": self.pasos_limites,
            },
            "tabla_valores": self.tabla_valores,
        }


# ══════════════════════════════════════════════════════════════════════════
# SERVICIOS PÚBLICOS (funciones de negocio)
# ══════════════════════════════════════════════════════════════════════════


def analizar_conica(rut_str):
    """
    Servicio: Analiza un RUT chileno y genera todos los datos de la cónica.
    
    Orquesta la validación, cálculo de coeficientes, clasificación, 
    ecuación general y forma canónica en un solo punto de entrada.
    
    Args:
        rut_str (str): RUT en formato "12.345.678-9" o similar
        
    Returns:
        ConicaAnalysis: Objeto con todo el análisis estructurado
        
    Raises:
        RUTInvalidoError: Si el RUT no es válido
        ConicaInvalidaError: Si los coeficientes son inválidos
    """
    resultado = ConicaAnalysis()
    
    # ─────────────────────────────────────────────────────
    # 0. Validar formato básico del RUT
    # ─────────────────────────────────────────────────────
    try:
        rut_str = validar_rut_str(rut_str)
    except RUTInvalidoError:
        raise
    
    # ─────────────────────────────────────────────────────
    # 1. Validar RUT
    # ─────────────────────────────────────────────────────
    es_valido, pasos_val, digitos, dv_calc = validar_rut(rut_str)
    
    resultado.es_valido = es_valido
    resultado.pasos_validacion = pasos_val
    resultado.digitos = digitos
    resultado.dv = dv_calc
    
    # Si el RUT es inválido, retornar aquí
    if not es_valido:
        raise RUTInvalidoError(
            mensaje="El RUT ingresado no pasó validación con módulo 11",
            rut_ingresado=rut_str,
            detalles=pasos_val[-3:] if len(pasos_val) > 3 else pasos_val
        )
    
    # Validar estructura de dígitos
    try:
        digitos, dv_calc = validar_digitos(digitos, dv_calc)
    except RUTInvalidoError:
        raise
    
    # Formatear RUT (simplificado para display)
    cuerpo_8 = "".join(str(d) for d in digitos)
    resultado.rut_formateado = f"{cuerpo_8[:-6]}.{cuerpo_8[-6:-3]}.{cuerpo_8[-3:]}-{dv_calc}"
    
    # ─────────────────────────────────────────────────────
    # 2. Calcular coeficientes
    # ─────────────────────────────────────────────────────
    A, B, C, D, E, pasos_coef, ajustes = calcular_coeficientes(digitos, dv_calc)
    
    resultado.A = A
    resultado.B = B
    resultado.C = C
    resultado.D = D
    resultado.E = E
    resultado.pasos_coeficientes = pasos_coef
    resultado.ajustes = ajustes
    
    # Validar coeficientes
    try:
        validar_coeficientes_conica(A, B, C, D, E)
    except ConicaInvalidaError:
        raise
    
    # ─────────────────────────────────────────────────────
    # 3. Clasificar cónica
    # ─────────────────────────────────────────────────────
    tipo_conica = clasificar_conica(A, B)
    resultado.tipo_conica = tipo_conica
    
    # ─────────────────────────────────────────────────────
    # 4. Generar ecuación general
    # ─────────────────────────────────────────────────────
    resultado.ecuacion_general = ecuacion_str(A, B, C, D, E)
    
    # ─────────────────────────────────────────────────────
    # 5. Forma canónica y elementos geométricos
    # ─────────────────────────────────────────────────────
    canonica, pasos_can, elementos = forma_canonica(A, B, C, D, E, tipo_conica)
    
    resultado.ecuacion_canonica = canonica
    resultado.pasos_canonica = pasos_can
    resultado.elementos_geometricos = elementos
    
    return resultado


def analizar_limites(rut_str):
    """
    Servicio: Analiza un RUT chileno y genera la función por tramos con límites.
    
    Orquesta la validación, generación de función, cálculo de límites,
    análisis de continuidad y tabla de valores en un solo punto de entrada.
    
    Args:
        rut_str (str): RUT en formato "12.345.678-9" o similar
        
    Returns:
        LimitesAnalysis: Objeto con todo el análisis estructurado
        
    Raises:
        RUTInvalidoError: Si el RUT no es válido
        LimiteInvalidoError: Si hay problemas en el cálculo de límites
    """
    resultado = LimitesAnalysis()
    
    # ─────────────────────────────────────────────────────
    # 0. Validar formato básico del RUT
    # ─────────────────────────────────────────────────────
    try:
        rut_str = validar_rut_str(rut_str)
    except RUTInvalidoError:
        raise
    
    # ─────────────────────────────────────────────────────
    # 1. Validar RUT
    # ─────────────────────────────────────────────────────
    es_valido, pasos_val, digitos, dv_calc = validar_rut(rut_str)
    
    resultado.es_valido = es_valido
    resultado.pasos_validacion = pasos_val
    resultado.digitos = digitos
    resultado.dv = dv_calc
    
    # Si el RUT es inválido, retornar aquí
    if not es_valido:
        raise RUTInvalidoError(
            mensaje="El RUT ingresado no pasó validación con módulo 11",
            rut_ingresado=rut_str,
            detalles=pasos_val[-3:] if len(pasos_val) > 3 else pasos_val
        )
    
    # Validar estructura de dígitos
    try:
        digitos, dv_calc = validar_digitos(digitos, dv_calc)
    except RUTInvalidoError:
        raise
    
    # Formatear RUT (simplificado para display)
    cuerpo_8 = "".join(str(d) for d in digitos)
    resultado.rut_formateado = f"{cuerpo_8[:-6]}.{cuerpo_8[-6:-3]}.{cuerpo_8[-3:]}-{dv_calc}"
    
    # ─────────────────────────────────────────────────────
    # 2. Generar la función por tramos
    # ─────────────────────────────────────────────────────
    a = digitos[2]  # a = d3
    
    # Validar punto de discontinuidad
    try:
        a = validar_punto_discontinuidad(a, digitos)
    except LimiteInvalidoError:
        raise
    
    caso, razon = seleccionar_caso(digitos[7])  # d8
    
    # Validar tipo de caso
    try:
        caso = validar_caso_tipo(caso)
    except LimiteInvalidoError:
        raise
    
    resultado.a = a
    resultado.caso_tipo = caso
    resultado.razon_caso = razon
    
    desc, tramos = construir_funcion(caso, a, digitos)
    resultado.descripcion_funcion = desc
    
    # Validar estructura de tramos
    try:
        tramos = validar_tramos(tramos)
    except LimiteInvalidoError:
        raise
    
    resultado.tramos_info = tramos
    
    # ─────────────────────────────────────────────────────
    # 3. Calcular límites y análisis de continuidad
    # ─────────────────────────────────────────────────────
    try:
        analisis_limites = calcular_limites(tramos)
    except Exception as e:
        raise LimiteInvalidoError(
            mensaje="Error calculando límites",
            punto_a=a,
            caso_tipo=caso,
            razon=str(e)
        )
    
    resultado.lim_izquierda = analisis_limites.get("lim_izq")
    resultado.lim_derecha = analisis_limites.get("lim_der")
    resultado.lim_existe = analisis_limites.get("lim_existe", False)
    resultado.lim_valor = analisis_limites.get("lim_valor")
    resultado.f_en_a = analisis_limites.get("f_en_a")
    resultado.es_continua = analisis_limites.get("continua", False)
    resultado.tipo_discontinuidad = analisis_limites.get("tipo_disc", "")
    resultado.pasos_limites = analisis_limites.get("pasos", [])
    
    # ─────────────────────────────────────────────────────
    # 4. Generar tabla de valores
    # ─────────────────────────────────────────────────────
    try:
        tabla = _generar_tabla_valores(tramos, a)
        tabla = validar_tabla_valores(tabla)
        resultado.tabla_valores = tabla
    except LimiteInvalidoError:
        raise
    
    return resultado


def _generar_tabla_valores(tramos, a, puntos=11):
    """
    Función auxiliar interna: genera tabla de valores cercanos al punto de discontinuidad.
    
    Args:
        tramos (dict): Información de los tramos
        a (float): Punto de análisis
        puntos (int): Cantidad de puntos a evaluar (por defecto 11)
        
    Returns:
        list: Lista de diccionarios con (x, f_x, lado)
    """
    tabla = []
    
    # Valores a la izquierda
    for i in range(puntos // 2, 0, -1):
        x = a - i * 0.2
        f_x = evaluar_funcion(x, tramos)
        tabla.append({
            "x": round(x, 4),
            "f_x": round(f_x, 4) if f_x is not None else None,
            "lado": "izq",
        })
    
    # Valor en a
    f_en_a = evaluar_funcion(a, tramos)
    tabla.append({
        "x": a,
        "f_x": round(f_en_a, 4) if f_en_a is not None else None,
        "lado": "a",
    })
    
    # Valores a la derecha
    for i in range(1, puntos // 2 + 1):
        x = a + i * 0.2
        f_x = evaluar_funcion(x, tramos)
        tabla.append({
            "x": round(x, 4),
            "f_x": round(f_x, 4) if f_x is not None else None,
            "lado": "der",
        })
    
    return tabla
