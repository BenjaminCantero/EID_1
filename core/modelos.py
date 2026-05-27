"""Modelos matemáticos auxiliares sin dependencias externas."""


def raiz_cuadrada_manual(n):
    """Calcula la raíz cuadrada usando Newton-Raphson."""
    if n < 0:
        return None
    if n == 0:
        return 0.0
    x = n / 2.0
    for _ in range(100):
        x_nuevo = (x + n / x) / 2.0
        if abs(x_nuevo - x) < 1e-10:
            return x_nuevo
        x = x_nuevo
    return x


def completar_cuadrado(coef, lin):
    """Completa el cuadrado para coef*(x^2 + (lin/coef)x).
    
    Nota: La validación de coef ≠ 0 se realiza en las funciones que la llaman.
    """
    h = -lin / (2 * coef)
    adicional = -(lin * lin) / (4 * coef)
    return h, adicional


def cos_taylor(x):
    """Calcula coseno por serie de Taylor."""
    pi2 = 6.283185307179586
    x = x % pi2
    if x > 3.141592653589793:
        x -= pi2
    result = 1.0
    term = 1.0
    for n in range(1, 9):
        term *= -x * x / ((2 * n - 1) * (2 * n))
        result += term
    return result


def sin_taylor(x):
    """Calcula seno por serie de Taylor."""
    pi2 = 6.283185307179586
    x = x % pi2
    if x > 3.141592653589793:
        x -= pi2
    result = x
    term = x
    for n in range(1, 9):
        term *= -x * x / ((2 * n) * (2 * n + 1))
        result += term
    return result


def exp_taylor(x):
    """Calcula exponencial por serie de Taylor."""
    if x > 20:
        return 485165195.4
    if x < -20:
        return 0.0
    result = 1.0
    term = 1.0
    for n in range(1, 30):
        term *= x / n
        result += term
        if abs(term) < 1e-15:
            break
    return result


def cosh_taylor(x):
    """Calcula cosh por serie de Taylor."""
    if x > 10:
        e = exp_taylor(x)
        return (e + 1 / e) / 2
    result = 1.0
    term = 1.0
    for n in range(1, 10):
        term *= x * x / ((2 * n - 1) * (2 * n))
        result += term
    return result


def sinh_taylor(x):
    """Calcula sinh por serie de Taylor."""
    if abs(x) > 10:
        e = exp_taylor(x)
        return (e - 1 / e) / 2
    result = x
    term = x
    for n in range(1, 10):
        term *= x * x / ((2 * n) * (2 * n + 1))
        result += term
    return result
