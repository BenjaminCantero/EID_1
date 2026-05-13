"""
Script de prueba para demostrar el Service Layer con manejo de excepciones.
Prueba: Validación de RUT, análisis de cónicas y límites.
"""

from core.services import analizar_conica, analizar_limites
from core.exceptions import RUTInvalidoError, ConicaInvalidaError, LimiteInvalidoError


def test_rut_valido():
    """Prueba con un RUT válido"""
    print("\n" + "="*70)
    print("TEST 1: RUT VÁLIDO (12.345.678-9)")
    print("="*70)
    
    try:
        resultado = analizar_conica("12.345.678-9")
        print(f"✓ Cónica analizada exitosamente")
        print(f"  RUT formateado: {resultado.rut_formateado}")
        print(f"  Tipo: {resultado.tipo_conica}")
        print(f"  Ecuación: {resultado.ecuacion_general}")
    except (RUTInvalidoError, ConicaInvalidaError) as e:
        print(f"✗ Error: {e}")


def test_rut_invalido_formato():
    """Prueba con un RUT con formato inválido"""
    print("\n" + "="*70)
    print("TEST 2: RUT CON FORMATO INVÁLIDO (muy corto)")
    print("="*70)
    
    try:
        resultado = analizar_conica("123")
        print(f"✓ Análisis completado")
    except RUTInvalidoError as e:
        print(f"✓ Error capturado correctamente:")
        print(f"  {e}")


def test_rut_invalido_digito():
    """Prueba con un RUT con dígito verificador incorrecto"""
    print("\n" + "="*70)
    print("TEST 3: RUT CON DÍGITO VERIFICADOR INCORRECTO")
    print("="*70)
    
    try:
        resultado = analizar_conica("12.345.678-1")  # DV incorrecto
        print(f"✓ Análisis completado")
    except RUTInvalidoError as e:
        print(f"✓ Error capturado correctamente:")
        print(f"  {e}")


def test_rut_vacio():
    """Prueba con un RUT vacío"""
    print("\n" + "="*70)
    print("TEST 4: RUT VACÍO")
    print("="*70)
    
    try:
        resultado = analizar_conica("")
        print(f"✓ Análisis completado")
    except RUTInvalidoError as e:
        print(f"✓ Error capturado correctamente:")
        print(f"  {e}")


def test_limites_valido():
    """Prueba análisis de límites con RUT válido"""
    print("\n" + "="*70)
    print("TEST 5: ANÁLISIS DE LÍMITES CON RUT VÁLIDO")
    print("="*70)
    
    try:
        resultado = analizar_limites("12.345.678-9")
        print(f"✓ Límites analizados exitosamente")
        print(f"  RUT: {resultado.rut_formateado}")
        print(f"  Punto a: {resultado.a}")
        print(f"  Tipo discontinuidad: {resultado.tipo_discontinuidad}")
        print(f"  Es continua: {resultado.es_continua}")
        print(f"  Tabla de valores: {len(resultado.tabla_valores)} puntos")
    except (RUTInvalidoError, LimiteInvalidoError) as e:
        print(f"✗ Error: {e}")


def test_limites_invalido():
    """Prueba análisis de límites con RUT inválido"""
    print("\n" + "="*70)
    print("TEST 6: ANÁLISIS DE LÍMITES CON RUT INVÁLIDO")
    print("="*70)
    
    try:
        resultado = analizar_limites("999.999.999-9")
        print(f"✓ Análisis completado")
    except LimiteInvalidoError as e:
        print(f"✓ Error capturado:")
        print(f"  {e}")
    except RUTInvalidoError as e:
        print(f"✓ Error capturado correctamente (RUT inválido):")
        print(f"  {e}")


def main():
    print("\n" + "█"*70)
    print("PRUEBAS DEL SERVICE LAYER CON EXCEPCIONES Y VALIDADORES")
    print("█"*70)
    
    test_rut_valido()
    test_rut_invalido_formato()
    test_rut_invalido_digito()
    test_rut_vacio()
    test_limites_valido()
    test_limites_invalido()
    
    print("\n" + "█"*70)
    print("PRUEBAS COMPLETADAS")
    print("█"*70 + "\n")


if __name__ == "__main__":
    main()
