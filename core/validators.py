"""
Validadores reutilizables para el proyecto EID.
Centraliza la lógica de validación para reducir duplicación de código.
"""

from core.exceptions import RUTInvalidoError, ConicaInvalidaError, LimiteInvalidoError


def validar_rut_str(rut_str):
    """
    Valida que un RUT sea un string no vacío y con formato básico.
    
    Args:
        rut_str (str): RUT a validar
        
    Returns:
        str: RUT limpio (sin espacios)
        
    Raises:
        RUTInvalidoError: Si el RUT no cumple los requisitos básicos
    """
    if not isinstance(rut_str, str):
        raise RUTInvalidoError(
            mensaje="El RUT debe ser un string",
            rut_ingresado=str(rut_str)
        )
    
    rut_limpio = rut_str.strip()
    
    if not rut_limpio:
        raise RUTInvalidoError(
            mensaje="El RUT no puede estar vacío",
            rut_ingresado=rut_str
        )
    
    if len(rut_limpio) < 9:
        raise RUTInvalidoError(
            mensaje="El RUT tiene formato inválido (muy corto)",
            rut_ingresado=rut_str,
            detalles=["Se espera formato: 12.345.678-9 o similar"]
        )
    
    return rut_limpio


def validar_digitos(digitos, dv):
    """
    Valida que los dígitos extraídos sean válidos.
    
    Args:
        digitos (list): Lista de 8 dígitos del RUT
        dv (str): Dígito verificador (puede ser número, K, o 0)
        
    Returns:
        tuple: (digitos validados, dv validado)
        
    Raises:
        RUTInvalidoError: Si los dígitos no son válidos
    """
    if not isinstance(digitos, list) or len(digitos) != 8:
        raise RUTInvalidoError(
            mensaje="Los dígitos del RUT deben ser una lista de 8 elementos",
            detalles=[f"Se recibieron: {len(digitos) if isinstance(digitos, list) else 'no list'}"]
        )
    
    if not all(isinstance(d, int) and 0 <= d <= 9 for d in digitos):
        raise RUTInvalidoError(
            mensaje="Los dígitos del RUT deben ser números entre 0-9",
            detalles=[f"Dígitos recibidos: {digitos}"]
        )
    
    if not isinstance(dv, str) or dv not in "0123456789K":
        raise RUTInvalidoError(
            mensaje="El dígito verificador debe ser 0-9 o K",
            detalles=[f"DV recibido: '{dv}'"]
        )
    
    return digitos, dv


def validar_coeficientes_conica(A, B, C, D, E):
    """
    Valida que los coeficientes de la cónica sean válidos.
    
    Args:
        A, B, C, D, E (float): Coeficientes de la ecuación general
        
    Raises:
        ConicaInvalidaError: Si los coeficientes no son válidos
    """
    # Verificar que sean números
    for coef, nombre in [(A, 'A'), (B, 'B'), (C, 'C'), (D, 'D'), (E, 'E')]:
        if not isinstance(coef, (int, float)):
            raise ConicaInvalidaError(
                mensaje=f"El coeficiente {nombre} debe ser un número",
                razon=f"{nombre}={coef}"
            )
    
    # Ambos ceros es degenerada
    if abs(A) < 1e-10 and abs(B) < 1e-10:
        raise ConicaInvalidaError(
            mensaje="Cónica degenerada",
            A=A,
            B=B,
            razon="A y B son ambos cero"
        )


def validar_punto_discontinuidad(a, digitos):
    """
    Valida que el punto de discontinuidad sea válido.
    
    Args:
        a (int): Punto de discontinuidad
        digitos (list): Lista de dígitos del RUT (para contexto)
        
    Returns:
        int: Punto validado
        
    Raises:
        LimiteInvalidoError: Si el punto no es válido
    """
    if not isinstance(a, int) or a < 0 or a > 9:
        raise LimiteInvalidoError(
            mensaje="El punto de discontinuidad debe estar entre 0-9",
            punto_a=a,
            razon=f"Valor recibido: {a}"
        )
    
    return a


def validar_caso_tipo(caso_tipo, caso_validos=None):
    """
    Valida que el tipo de discontinuidad sea válido.
    
    Args:
        caso_tipo (str): Tipo de discontinuidad
        caso_validos (list): Tipos válidos (por defecto: removible, salto, infinita)
        
    Returns:
        str: Tipo validado
        
    Raises:
        LimiteInvalidoError: Si el tipo no es válido
    """
    if caso_validos is None:
        caso_validos = ["removible", "salto", "infinita"]
    
    if not isinstance(caso_tipo, str):
        raise LimiteInvalidoError(
            mensaje="El tipo de discontinuidad debe ser string",
            razon=f"Tipo recibido: {type(caso_tipo)}"
        )
    
    if caso_tipo.lower() not in caso_validos:
        raise LimiteInvalidoError(
            mensaje=f"Tipo de discontinuidad inválido: '{caso_tipo}'",
            razon=f"Válidos: {', '.join(caso_validos)}"
        )
    
    return caso_tipo.lower()


def validar_tramos(tramos):
    """
    Valida que la estructura de tramos sea correcta.
    
    Args:
        tramos (dict): Diccionario con información de tramos
        
    Returns:
        dict: Tramos validados
        
    Raises:
        LimiteInvalidoError: Si la estructura es inválida
    """
    if not isinstance(tramos, dict):
        raise LimiteInvalidoError(
            mensaje="Los tramos deben ser un diccionario",
            razon=f"Tipo recibido: {type(tramos)}"
        )
    
    campos_requeridos = ["tipo", "a"]
    for campo in campos_requeridos:
        if campo not in tramos:
            raise LimiteInvalidoError(
                mensaje=f"Campo requerido '{campo}' falta en tramos",
                razon=f"Campos disponibles: {list(tramos.keys())}"
            )
    
    return tramos


def validar_tabla_valores(tabla):
    """
    Valida que la tabla de valores tenga la estructura correcta.
    
    Args:
        tabla (list): Lista de valores
        
    Returns:
        list: Tabla validada
        
    Raises:
        LimiteInvalidoError: Si la tabla es inválida
    """
    if not isinstance(tabla, list):
        raise LimiteInvalidoError(
            mensaje="La tabla de valores debe ser una lista",
            razon=f"Tipo recibido: {type(tabla)}"
        )
    
    if len(tabla) == 0:
        raise LimiteInvalidoError(
            mensaje="La tabla de valores no puede estar vacía",
            razon="Lista sin elementos"
        )
    
    # Validar estructura de cada elemento
    campos_esperados = {"x", "f_x", "lado"}
    for i, item in enumerate(tabla):
        if not isinstance(item, dict):
            raise LimiteInvalidoError(
                mensaje=f"Elemento {i} de tabla no es diccionario",
                razon=f"Tipo recibido: {type(item)}"
            )
        
        campos_presentes = set(item.keys())
        if not campos_esperados.issubset(campos_presentes):
            raise LimiteInvalidoError(
                mensaje=f"Elemento {i} de tabla tiene campos faltantes",
                razon=f"Esperados: {campos_esperados}, Presentes: {campos_presentes}"
            )
    
    return tabla
