"""
Excepciones personalizadas para el proyecto EID.
Proporciona manejo consistente de errores en toda la aplicación.
"""


class EIDError(Exception):
    """Excepción base para todas las excepciones del proyecto EID."""
    pass


class RUTInvalidoError(EIDError):
    """Se lanza cuando el RUT ingresado no es válido."""
    
    def __init__(self, mensaje="RUT inválido", rut_ingresado=None, detalles=None):
        """
        Args:
            mensaje (str): Descripción del error
            rut_ingresado (str): RUT que fue rechazado
            detalles (list): Lista de detalles/pasos del error
        """
        self.mensaje = mensaje
        self.rut_ingresado = rut_ingresado
        self.detalles = detalles or []
        
        msg_completo = f"{mensaje}"
        if rut_ingresado:
            msg_completo += f" (RUT: '{rut_ingresado}')"
        if self.detalles:
            msg_completo += f"\nDetalles: {'; '.join(self.detalles)}"
        
        super().__init__(msg_completo)


class ConicaInvalidaError(EIDError):
    """Se lanza cuando los coeficientes de la cónica son inválidos."""
    
    def __init__(self, mensaje="Cónica inválida o degenerada", A=None, B=None, razon=None):
        """
        Args:
            mensaje (str): Descripción del error
            A (float): Coeficiente A (para contexto)
            B (float): Coeficiente B (para contexto)
            razon (str): Razón específica del error
        """
        self.mensaje = mensaje
        self.A = A
        self.B = B
        self.razon = razon
        
        msg_completo = f"{mensaje}"
        if A is not None and B is not None:
            msg_completo += f" (A={A:.4f}, B={B:.4f})"
        if razon:
            msg_completo += f" — {razon}"
        
        super().__init__(msg_completo)


class LimiteInvalidoError(EIDError):
    """Se lanza cuando no se puede calcular el límite o la función es inválida."""
    
    def __init__(self, mensaje="Límite no calculable", punto_a=None, caso_tipo=None, razon=None):
        """
        Args:
            mensaje (str): Descripción del error
            punto_a (float): Punto de análisis (para contexto)
            caso_tipo (str): Tipo de discontinuidad (para contexto)
            razon (str): Razón específica del error
        """
        self.mensaje = mensaje
        self.punto_a = punto_a
        self.caso_tipo = caso_tipo
        self.razon = razon
        
        msg_completo = f"{mensaje}"
        if punto_a is not None:
            msg_completo += f" en x={punto_a}"
        if caso_tipo:
            msg_completo += f" (tipo: {caso_tipo})"
        if razon:
            msg_completo += f" — {razon}"
        
        super().__init__(msg_completo)


class DatosEstructuradosError(EIDError):
    """Se lanza cuando hay problemas en la conversión de datos estructurados."""
    
    def __init__(self, mensaje="Error en datos estructurados", tipo_dato=None):
        """
        Args:
            mensaje (str): Descripción del error
            tipo_dato (str): Tipo de dato que causó el problema
        """
        self.mensaje = mensaje
        self.tipo_dato = tipo_dato
        
        msg_completo = f"{mensaje}"
        if tipo_dato:
            msg_completo += f" ({tipo_dato})"
        
        super().__init__(msg_completo)
