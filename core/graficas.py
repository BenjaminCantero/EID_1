"""Funciones de graficación para cónicas y funciones por tramos."""

from core.modelos import (completar_cuadrado, cos_taylor, cosh_taylor,
                          exp_taylor, raiz_cuadrada_manual, sin_taylor, sinh_taylor)
from core.validators import validar_no_cero


def puntos_grafica(A, B, C, D, E, tipo, n=500):
    """Genera puntos para dibujar la cónica en un canvas.
    
    Raises:
        ConicaInvalidaError: Si hay indeterminación (división por cero)
    """
    puntos = []

    if tipo in ("Circunferencia", "Elipse"):
        h, add_x = completar_cuadrado(A, C)
        k, add_y = completar_cuadrado(B, D)
        constante = -E - add_x - add_y
        if constante <= 0:
            return []
        validar_no_cero(A, "coeficiente A")
        validar_no_cero(B, "coeficiente B")
        a2 = constante / A
        b2 = constante / B
        if a2 <= 0 or b2 <= 0:
            return []
        a = raiz_cuadrada_manual(a2)
        b = raiz_cuadrada_manual(b2)
        paso = 6.283185307179586 / n
        for i in range(n + 1):
            t = i * paso
            puntos.append((h + a * cos_taylor(t), k + b * sin_taylor(t)))

    elif tipo == "Hipérbola":
        h, add_x = completar_cuadrado(A, C)
        k, add_y = completar_cuadrado(B, D)
        constante = -E - add_x - add_y
        if abs(constante) < 1e-9:
            return []
        validar_no_cero(A, "coeficiente A")
        validar_no_cero(B, "coeficiente B")
        a2 = constante / A
        b2 = constante / B
        if a2 > 0 and b2 < 0:
            a = raiz_cuadrada_manual(a2)
            b = raiz_cuadrada_manual(abs(b2))
            for rama in [1, -1]:
                rama_pts = []
                for i in range(n):
                    t = -3.5 + 7.0 * i / n
                    rama_pts.append((h + rama * a * cosh_taylor(t), k + b * sinh_taylor(t)))
                puntos.append(("rama", rama_pts))
        else:
            a2, b2 = b2, a2
            if a2 > 0:
                a = raiz_cuadrada_manual(a2)
                b = raiz_cuadrada_manual(abs(b2))
                for rama in [1, -1]:
                    rama_pts = []
                    for i in range(n):
                        t = -3.5 + 7.0 * i / n
                        rama_pts.append((h + b * sinh_taylor(t), k + rama * a * cosh_taylor(t)))
                    puntos.append(("rama", rama_pts))

    elif tipo == "Parábola":
        if abs(B) < 1e-9:
            h, add_x = completar_cuadrado(A, C)
            const = -add_x - E
            validar_no_cero(D, "coeficiente D")
            if abs(D) < 1e-9:
                return []
            p_coef = -A / D
            q = const / D
            x_vals = [h - 15 + 30 * i / n for i in range(n + 1)]
            for x in x_vals:
                puntos.append((x, p_coef * (x - h) ** 2 + q))
        else:
            k, add_y = completar_cuadrado(B, D)
            const = -add_y - E
            validar_no_cero(C, "coeficiente C")
            if abs(C) < 1e-9:
                return []
            p_coef = -B / C
            q = const / C
            y_vals = [k - 15 + 30 * i / n for i in range(n + 1)]
            for y in y_vals:
                puntos.append((p_coef * (y - k) ** 2 + q, y))

    return puntos


def puntos_grafica_limite(tramos, ancho=400, alto=300, rango_x=10, centro_y=0.0):
    """Genera segmentos para graficar la función por tramos.

    centro_y desplaza el centro vertical de la vista: el valor y=centro_y
    queda en el medio del canvas. Esto permite que el salto/límite sea
    visible aunque tome valores grandes (p. ej. a + d en una discontinuidad
    de salto).
    """
    from core.limites import evaluar_funcion

    a = tramos["a"]
    n = 400
    cx = ancho / 2
    cy = alto / 2
    # Escala centrada en 'a': x=a → cx, igual que en _graficar del panel
    escala_x = ancho / (2 * rango_x)
    escala_y = alto / (2 * rango_x)

    def mundo_a_pantalla(x, y):
        px = cx + (x - a) * escala_x   # centrado en x=a
        py = cy - (y - centro_y) * escala_y  # centrado en y=centro_y
        return px, py

    segmentos = []
    xs = [a - rango_x + 2 * rango_x * i / n for i in range(n + 1)]
    pts_izq = []
    pts_der = []

    for x in xs:
        if abs(x - a) < 0.05:
            continue
        y = evaluar_funcion(x, tramos)
        if y is None or abs(y - centro_y) > rango_x * 3:
            continue
        px, py = mundo_a_pantalla(x, y)
        if x < a:
            pts_izq.append((px, py))
        else:
            pts_der.append((px, py))

    segmentos.extend(_lista_a_segmentos(pts_izq))
    segmentos.extend(_lista_a_segmentos(pts_der))
    return segmentos, mundo_a_pantalla


def _valor_str(y):
    if y is None:
        return "No def."
    if abs(y) > 1e10:
        return "→ -∞" if y < 0 else "→ +∞"
    return f"{y:.6f}"


def _lista_a_segmentos(pts):
    return [(*pts[i], *pts[i + 1]) for i in range(len(pts) - 1)]
