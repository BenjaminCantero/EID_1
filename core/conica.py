# core/conica.py
# Construcción de la ecuación general, clasificación y forma canónica
# Todos los cálculos implementados manualmente (sin numpy/math/sympy)


def _raiz_cuadrada_manual(n):
    """Calcula raíz cuadrada por método de Newton-Raphson sin usar math."""
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


def _abs(x):
    return x if x >= 0 else -x


def calcular_coeficientes(digitos, dv_str):
    """
    Construye los coeficientes A, B, C, D, E de la ecuación general
    Ax² + By² + Cx + Dy + E = 0 a partir de los dígitos del RUT.

    Retorna:
        (A, B, C, D, E, pasos: list[str], ajustes: list[str])
    """
    d = digitos  # d[0]=d1 ... d[7]=d8

    # Variable auxiliar v
    if dv_str == "K":
        v = 10
    elif dv_str == "0":
        v = 11
    else:
        v = int(dv_str)

    pasos = []
    pasos.append(f"Dígitos del RUT: d1={d[0]}, d2={d[1]}, d3={d[2]}, d4={d[3]}, "
                 f"d5={d[4]}, d6={d[5]}, d7={d[6]}, d8={d[7]}")
    pasos.append(f"Dígito verificador DV={dv_str}  →  v={v}")
    pasos.append("")

    A = (d[0] + d[1]) / v
    B = (d[2] + d[3]) / v
    C = -(d[4] + d[5])
    D = -(d[6] + d[7])
    E = d[0] + d[2] + d[4] + d[6]

    pasos.append("Coeficientes base:")
    pasos.append(f"  A = (d1 + d2) / v = ({d[0]} + {d[1]}) / {v} = {A:.4f}")
    pasos.append(f"  B = (d3 + d4) / v = ({d[2]} + {d[3]}) / {v} = {B:.4f}")
    pasos.append(f"  C = -(d5 + d6) = -({d[4]} + {d[5]}) = {C}")
    pasos.append(f"  D = -(d7 + d8) = -({d[6]} + {d[7]}) = {D}")
    pasos.append(f"  E = d1+d3+d5+d7 = {d[0]}+{d[2]}+{d[4]}+{d[6]} = {E}")

    ajustes = []

    # Ajuste 1: d8 impar → B = -B (hipérbola)
    if d[7] % 2 != 0:
        B = -B
        ajustes.append(f"d8={d[7]} es IMPAR → se aplica B = -B = {B:.4f} (favorece hipérbola)")

    # Ajuste 2: d1 == d2 → B = A (circunferencia)
    if d[0] == d[1]:
        B = A
        ajustes.append(f"d1={d[0]} == d2={d[1]} → se impone B = A = {A:.4f} (favorece circunferencia)")

    # Ajuste 3: (d5+d6) múltiplo de 3 → parábola
    if (d[4] + d[5]) % 3 == 0:
        if d[6] % 2 == 0:
            B = 0
            ajustes.append(f"d5+d6={d[4]+d[5]} es múltiplo de 3 y d7={d[6]} es PAR → B=0 (parábola eje vertical)")
        else:
            A = 0
            ajustes.append(f"d5+d6={d[4]+d[5]} es múltiplo de 3 y d7={d[6]} es IMPAR → A=0 (parábola eje horizontal)")

    if not ajustes:
        ajustes.append("No se aplicaron ajustes especiales.")

    return A, B, C, D, E, pasos, ajustes


def clasificar_conica(A, B):
    """Clasifica la cónica según los coeficientes A y B."""
    if A == 0 and B == 0:
        return "Degenerada"
    if A == 0 or B == 0:
        return "Parábola"
    if _abs(A - B) < 1e-9:  # A == B con tolerancia flotante
        return "Circunferencia"
    if (A > 0 and B > 0) or (A < 0 and B < 0):
        return "Elipse"
    return "Hipérbola"


def ecuacion_str(A, B, C, D, E):
    """Retorna la ecuación general como string legible."""
    def term(coef, var, primero=False):
        if _abs(coef) < 1e-9:
            return ""
        signo = "+" if coef > 0 and not primero else ("-" if coef < 0 and not primero else "")
        valor = _abs(coef)
        if _abs(valor - 1.0) < 1e-9 and "²" in var:
            num = signo + var if signo else ("-" + var if coef < 0 else var)
        elif _abs(valor - 1.0) < 1e-9:
            num = signo + var if signo else ("-" + var if coef < 0 else var)
        else:
            num = f"{signo}{valor:.4g}{var}" if signo else (f"{valor:.4g}{var}" if coef > 0 else f"-{valor:.4g}{var}")
        return num.strip()

    partes = []
    if _abs(A) > 1e-9:
        partes.append(f"({A:.4g})x²")
    if _abs(B) > 1e-9:
        signo = " + " if B > 0 else " - "
        partes.append(f"{signo}({_abs(B):.4g})y²")
    if _abs(C) > 1e-9:
        signo = " + " if C > 0 else " - "
        partes.append(f"{signo}({_abs(C):.4g})x")
    if _abs(D) > 1e-9:
        signo = " + " if D > 0 else " - "
        partes.append(f"{signo}({_abs(D):.4g})y")
    if _abs(E) > 1e-9:
        signo = " + " if E > 0 else " - "
        partes.append(f"{signo}{_abs(E):.4g}")
    partes.append(" = 0")
    return "".join(partes)


def forma_canonica(A, B, C, D, E, tipo):
    """
    Transforma la ecuación general a forma canónica paso a paso.
    Retorna (canonica_str, pasos, elementos_geometricos)
    """
    pasos = []
    elementos = {}

    if tipo == "Circunferencia":
        pasos, elementos, canonica = _canonica_circunferencia(A, B, C, D, E)
    elif tipo == "Elipse":
        pasos, elementos, canonica = _canonica_elipse(A, B, C, D, E)
    elif tipo == "Hipérbola":
        pasos, elementos, canonica = _canonica_hiperbola(A, B, C, D, E)
    elif tipo == "Parábola":
        pasos, elementos, canonica = _canonica_parabola(A, B, C, D, E)
    else:
        pasos = ["Tipo degenerado, no tiene forma canónica estándar."]
        canonica = "No aplica"

    return canonica, pasos, elementos


def _completar_cuadrado(coef, lin):
    """
    Completa el cuadrado: coef*(x² + (lin/coef)*x)
    Retorna (h, termino_adicional) donde h es el vértice.
    h = -lin/(2*coef), adicional = -(lin²)/(4*coef)
    """
    h = -lin / (2 * coef)
    adicional = -(lin * lin) / (4 * coef)
    return h, adicional


def _canonica_circunferencia(A, B, C, D, E):
    pasos = []
    elementos = {}
    pasos.append("=== Circunferencia: A = B ===")
    pasos.append(f"Ecuación general: {ecuacion_str(A, B, C, D, E)}")
    pasos.append("")
    pasos.append("Paso 1: Dividir toda la ecuación por A para igualar coeficientes a 1:")
    a2 = A
    c2 = C / a2
    d2 = D / a2
    e2 = E / a2
    pasos.append(f"  x² + y² + ({c2:.4g})x + ({d2:.4g})y + {e2:.4g} = 0")
    pasos.append("")
    pasos.append("Paso 2: Completar el cuadrado en x:")
    h, add_x = _completar_cuadrado(1, c2)
    pasos.append(f"  x² + ({c2:.4g})x = (x + {c2/2:.4g})² - ({c2/2:.4g})²")
    pasos.append(f"  h = {h:.4g},  término adicional = {add_x:.4g}")
    pasos.append("")
    pasos.append("Paso 3: Completar el cuadrado en y:")
    k, add_y = _completar_cuadrado(1, d2)
    pasos.append(f"  y² + ({d2:.4g})y = (y + {d2/2:.4g})² - ({d2/2:.4g})²")
    pasos.append(f"  k = {k:.4g},  término adicional = {add_y:.4g}")
    pasos.append("")
    r2 = -e2 - add_x - add_y
    pasos.append(f"Paso 4: Reescribir:")
    pasos.append(f"  (x - ({h:.4g}))² + (y - ({k:.4g}))² = {r2:.4g}")
    r = _raiz_cuadrada_manual(r2) if r2 >= 0 else None

    if r is None or r2 <= 0:
        pasos.append("  ⚠ r² ≤ 0: la cónica es imaginaria o puntual.")
        canonica = f"(x - {h:.4g})² + (y - {k:.4g})² = {r2:.4g}  [sin solución real]"
    else:
        pasos.append(f"  Radio r = √{r2:.4g} ≈ {r:.4f}")
        canonica = f"(x - {h:.4g})² + (y - {k:.4g})² = {r2:.4g}"
        elementos["Centro"] = (round(h, 4), round(k, 4))
        elementos["Radio"] = round(r, 4)

    pasos.append("")
    pasos.append("=== Procedimiento inverso (canónica → general) ===")
    pasos.append(f"  Expandir (x - {h:.4g})² = x² - {2*h:.4g}x + {h**2:.4g}")
    pasos.append(f"  Expandir (y - {k:.4g})² = y² - {2*k:.4g}y + {k**2:.4g}")
    pasos.append(f"  Sumar y pasar {r2:.4g} al otro lado:")
    pasos.append(f"  x² + y² - {2*h:.4g}x - {2*k:.4g}y + {h**2 + k**2 - r2:.4g} = 0")

    return pasos, elementos, canonica


def _canonica_elipse(A, B, C, D, E):
    pasos = []
    elementos = {}
    pasos.append("=== Elipse: A ≠ B, mismo signo ===")
    pasos.append(f"Ecuación general: {ecuacion_str(A, B, C, D, E)}")
    pasos.append("")
    pasos.append("Paso 1: Agrupar términos en x e y:")
    pasos.append(f"  {A:.4g}(x² + {C/A:.4g}x) + {B:.4g}(y² + {D/B:.4g}y) + {E:.4g} = 0")
    pasos.append("")
    pasos.append("Paso 2: Completar el cuadrado en x:")
    h, add_x = _completar_cuadrado(A, C)
    pasos.append(f"  {A:.4g}(x - {h:.4g})²,  término adicional = {add_x:.4g}")
    pasos.append("")
    pasos.append("Paso 3: Completar el cuadrado en y:")
    k, add_y = _completar_cuadrado(B, D)
    pasos.append(f"  {B:.4g}(y - {k:.4g})²,  término adicional = {add_y:.4g}")
    pasos.append("")
    constante = -E - add_x - add_y
    pasos.append(f"Paso 4: Pasar constante al lado derecho:")
    pasos.append(f"  {A:.4g}(x - {h:.4g})² + {B:.4g}(y - {k:.4g})² = {constante:.4g}")

    if _abs(constante) < 1e-9:
        pasos.append("  ⚠ Constante = 0: elipse puntual.")
        canonica = f"{A:.4g}(x-{h:.4g})² + {B:.4g}(y-{k:.4g})² = 0"
        return pasos, elementos, canonica

    pasos.append("")
    pasos.append("Paso 5: Dividir para obtener forma estándar (x-h)²/a² + (y-k)²/b² = 1:")
    a2 = constante / A
    b2 = constante / B
    pasos.append(f"  a² = {constante:.4g} / {A:.4g} = {a2:.4g}")
    pasos.append(f"  b² = {constante:.4g} / {B:.4g} = {b2:.4g}")
    canonica = f"(x - {h:.4g})²/{a2:.4g} + (y - {k:.4g})²/{b2:.4g} = 1"
    pasos.append(f"  Forma canónica: {canonica}")

    if a2 > 0 and b2 > 0:
        a = _raiz_cuadrada_manual(a2)
        b = _raiz_cuadrada_manual(b2)
        elementos["Centro"] = (round(h, 4), round(k, 4))
        elementos["a (semi-eje mayor)"] = round(max(a, b), 4)
        elementos["b (semi-eje menor)"] = round(min(a, b), 4)
        c_foco = _raiz_cuadrada_manual(_abs(a2 - b2))
        if a2 >= b2:
            elementos["Focos"] = (round(h - c_foco, 4), round(k, 4)), (round(h + c_foco, 4), round(k, 4))
            elementos["Vértices"] = (round(h - a, 4), round(k, 4)), (round(h + a, 4), round(k, 4))
        else:
            elementos["Focos"] = (round(h, 4), round(k - c_foco, 4)), (round(h, 4), round(k + c_foco, 4))
            elementos["Vértices"] = (round(h, 4), round(k - b, 4)), (round(h, 4), round(k + b, 4))

    pasos.append("")
    pasos.append("=== Procedimiento inverso (canónica → general) ===")
    pasos.append(f"  Expandir (x-{h:.4g})²/{a2:.4g}: multiplica por {A:.4g}")
    pasos.append(f"  Expandir (y-{k:.4g})²/{b2:.4g}: multiplica por {B:.4g}")
    pasos.append(f"  Pasar 1 al otro lado y expandir para obtener la forma general.")

    return pasos, elementos, canonica


def _canonica_hiperbola(A, B, C, D, E):
    pasos = []
    elementos = {}
    pasos.append("=== Hipérbola: A y B con signos opuestos ===")
    pasos.append(f"Ecuación general: {ecuacion_str(A, B, C, D, E)}")
    pasos.append("")
    pasos.append("Paso 1: Agrupar y completar cuadrados:")
    h, add_x = _completar_cuadrado(A, C)
    k, add_y = _completar_cuadrado(B, D)
    pasos.append(f"  Completar en x: h = {h:.4g}, adicional = {add_x:.4g}")
    pasos.append(f"  Completar en y: k = {k:.4g}, adicional = {add_y:.4g}")
    constante = -E - add_x - add_y
    pasos.append(f"  {A:.4g}(x-{h:.4g})² + {B:.4g}(y-{k:.4g})² = {constante:.4g}")

    if _abs(constante) < 1e-9:
        canonica = f"{A:.4g}(x-{h:.4g})² + {B:.4g}(y-{k:.4g})² = 0  [hipérbola degenerada]"
        return pasos, elementos, canonica

    pasos.append("")
    pasos.append("Paso 2: Dividir por la constante para forma estándar:")
    a2 = constante / A
    b2 = constante / B
    pasos.append(f"  a² = {constante:.4g}/{A:.4g} = {a2:.4g}")
    pasos.append(f"  b² = {constante:.4g}/{B:.4g} = {b2:.4g}")

    if a2 > 0:
        canonica = f"(x-{h:.4g})²/{a2:.4g} - (y-{k:.4g})²/{_abs(b2):.4g} = 1"
        pasos.append(f"  Hipérbola horizontal: {canonica}")
        a = _raiz_cuadrada_manual(a2)
        b = _raiz_cuadrada_manual(_abs(b2))
        c_foco = _raiz_cuadrada_manual(a2 + _abs(b2))
        elementos["Centro"] = (round(h, 4), round(k, 4))
        elementos["Vértices"] = (round(h - a, 4), round(k, 4)), (round(h + a, 4), round(k, 4))
        elementos["Focos"] = (round(h - c_foco, 4), round(k, 4)), (round(h + c_foco, 4), round(k, 4))
        elementos["Eje transverso"] = f"2a = {2*a:.4g}"
        elementos["Eje conjugado"] = f"2b = {2*b:.4g}"
    else:
        canonica = f"(y-{k:.4g})²/{_abs(b2):.4g} - (x-{h:.4g})²/{_abs(a2):.4g} = 1"
        pasos.append(f"  Hipérbola vertical: {canonica}")
        a = _raiz_cuadrada_manual(_abs(a2))
        b = _raiz_cuadrada_manual(_abs(b2))
        c_foco = _raiz_cuadrada_manual(_abs(a2) + _abs(b2))
        elementos["Centro"] = (round(h, 4), round(k, 4))
        elementos["Vértices"] = (round(h, 4), round(k - b, 4)), (round(h, 4), round(k + b, 4))
        elementos["Focos"] = (round(h, 4), round(k - c_foco, 4)), (round(h, 4), round(k + c_foco, 4))

    pasos.append("")
    pasos.append("=== Procedimiento inverso (canónica → general) ===")
    pasos.append(f"  Expandir cuadrados, multiplicar cruzado y pasar todo al lado izquierdo.")

    return pasos, elementos, canonica


def _canonica_parabola(A, B, C, D, E):
    pasos = []
    elementos = {}

    if _abs(B) < 1e-9:
        # Parábola de eje vertical: Ax² + Cx + Dy + E = 0
        pasos.append("=== Parábola de eje vertical (B = 0) ===")
        pasos.append(f"Ecuación general: {ecuacion_str(A, B, C, D, E)}")
        pasos.append("")
        pasos.append("Paso 1: Completar el cuadrado en x:")
        h, add_x = _completar_cuadrado(A, C)
        pasos.append(f"  {A:.4g}(x - {h:.4g})²,  adicional = {add_x:.4g}")
        pasos.append("")
        pasos.append("Paso 2: Despejar y:")
        # A(x-h)² + add_x + Dy + E = 0  →  Dy = -A(x-h)² - add_x - E
        const = -add_x - E
        pasos.append(f"  {D:.4g}y = -{A:.4g}(x - {h:.4g})² + {const:.4g}")
        if _abs(D) < 1e-9:
            pasos.append("  ⚠ D = 0: ecuación sin término y, posible parábola degenerada.")
            canonica = "Degenerada"
            return pasos, elementos, canonica
        p_coef = -A / D
        q = const / D
        pasos.append(f"  y = {p_coef:.4g}(x - {h:.4g})² + {q:.4g}")
        canonica = f"y = {p_coef:.4g}(x - {h:.4g})² + {q:.4g}"
        elementos["Vértice"] = (round(h, 4), round(q, 4))
        if _abs(p_coef) > 1e-9:
            p_focal = 1 / (4 * p_coef)
            elementos["Foco"] = (round(h, 4), round(q + p_focal, 4))
            elementos["Directriz"] = f"y = {q - p_focal:.4g}"
        pasos.append(f"  Forma canónica: {canonica}")
    else:
        # Parábola de eje horizontal: By² + Cx + Dy + E = 0
        pasos.append("=== Parábola de eje horizontal (A = 0) ===")
        pasos.append(f"Ecuación general: {ecuacion_str(A, B, C, D, E)}")
        pasos.append("")
        pasos.append("Paso 1: Completar el cuadrado en y:")
        k, add_y = _completar_cuadrado(B, D)
        pasos.append(f"  {B:.4g}(y - {k:.4g})²,  adicional = {add_y:.4g}")
        pasos.append("")
        pasos.append("Paso 2: Despejar x:")
        const = -add_y - E
        pasos.append(f"  {C:.4g}x = -{B:.4g}(y - {k:.4g})² + {const:.4g}")
        if _abs(C) < 1e-9:
            pasos.append("  ⚠ C = 0: ecuación sin término x, posible parábola degenerada.")
            canonica = "Degenerada"
            return pasos, elementos, canonica
        p_coef = -B / C
        q = const / C
        pasos.append(f"  x = {p_coef:.4g}(y - {k:.4g})² + {q:.4g}")
        canonica = f"x = {p_coef:.4g}(y - {k:.4g})² + {q:.4g}"
        elementos["Vértice"] = (round(q, 4), round(k, 4))
        if _abs(p_coef) > 1e-9:
            p_focal = 1 / (4 * p_coef)
            elementos["Foco"] = (round(q + p_focal, 4), round(k, 4))
            elementos["Directriz"] = f"x = {q - p_focal:.4g}"
        pasos.append(f"  Forma canónica: {canonica}")

    pasos.append("")
    pasos.append("=== Procedimiento inverso (canónica → general) ===")
    pasos.append("  Expandir el cuadrado, distribuir coeficientes y reordenar todos")
    pasos.append("  los términos al lado izquierdo igualando a 0.")

    return pasos, elementos, canonica


def puntos_grafica(A, B, C, D, E, tipo, n=300):
    """
    Genera lista de puntos (x, y) para graficar la cónica.
    Retorna lista de segmentos [(x1,y1,x2,y2), ...] para dibujar con canvas.
    Sin numpy: se usa evaluación manual de raíces cuadradas.
    """
    puntos = []

    if tipo in ("Circunferencia", "Elipse"):
        # Parametrizar: x = h + a*cos(t), y = k + b*sin(t)
        h, add_x = _completar_cuadrado(A, C)
        k, add_y = _completar_cuadrado(B, D)
        constante = -E - add_x - add_y
        if constante <= 0:
            return []
        a2 = constante / A
        b2 = constante / B
        if a2 <= 0 or b2 <= 0:
            return []
        a = _raiz_cuadrada_manual(a2)
        b = _raiz_cuadrada_manual(b2)
        paso = 6.283185307179586 / n  # 2*pi / n
        pi2 = 6.283185307179586
        for i in range(n + 1):
            t = i * paso
            # sin y cos por serie de Taylor (sin math)
            cos_t = _cos_taylor(t)
            sin_t = _sin_taylor(t)
            puntos.append((h + a * cos_t, k + b * sin_t))

    elif tipo == "Hipérbola":
        h, add_x = _completar_cuadrado(A, C)
        k, add_y = _completar_cuadrado(B, D)
        constante = -E - add_x - add_y
        if _abs(constante) < 1e-9:
            return []
        a2 = constante / A
        b2 = constante / B
        # Rama derecha e izquierda
        if a2 > 0 and b2 < 0:
            a = _raiz_cuadrada_manual(a2)
            b = _raiz_cuadrada_manual(_abs(b2))
            for rama in [1, -1]:
                rama_pts = []
                for i in range(n):
                    t = -2.5 + 5.0 * i / n
                    cosh_t = _cosh_taylor(t)
                    sinh_t = _sinh_taylor(t)
                    rama_pts.append((h + rama * a * cosh_t, k + b * sinh_t))
                puntos.append(("rama", rama_pts))
                return puntos
        else:
            a2, b2 = b2, a2
            if a2 > 0:
                a = _raiz_cuadrada_manual(a2)
                b = _raiz_cuadrada_manual(_abs(b2)) if b2 < 0 else _raiz_cuadrada_manual(b2)
                for rama in [1, -1]:
                    rama_pts = []
                    for i in range(n):
                        t = -2.5 + 5.0 * i / n
                        cosh_t = _cosh_taylor(t)
                        sinh_t = _sinh_taylor(t)
                        rama_pts.append((h + b * sinh_t, k + rama * a * cosh_t))
                    puntos.append(("rama", rama_pts))
                return puntos

    elif tipo == "Parábola":
        if _abs(B) < 1e-9:
            h, add_x = _completar_cuadrado(A, C)
            const = -add_x - E
            if _abs(D) < 1e-9:
                return []
            p_coef = -A / D
            q = const / D
            x_vals = [h - 10 + 20 * i / n for i in range(n + 1)]
            for x in x_vals:
                y = p_coef * (x - h) ** 2 + q
                puntos.append((x, y))
        else:
            k, add_y = _completar_cuadrado(B, D)
            const = -add_y - E
            if _abs(C) < 1e-9:
                return []
            p_coef = -B / C
            q = const / C
            y_vals = [k - 10 + 20 * i / n for i in range(n + 1)]
            for y in y_vals:
                x = p_coef * (y - k) ** 2 + q
                puntos.append((x, y))

    return puntos


def _cos_taylor(x):
    """Coseno por serie de Taylor hasta término x^16."""
    # Reducir al rango [-pi, pi]
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


def _sin_taylor(x):
    """Seno por serie de Taylor hasta término x^17."""
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


def _cosh_taylor(x):
    """Coseno hiperbólico por serie de Taylor."""
    if x > 10:
        e = _exp_taylor(x)
        return (e + 1 / e) / 2
    result = 1.0
    term = 1.0
    for n in range(1, 10):
        term *= x * x / ((2 * n - 1) * (2 * n))
        result += term
    return result


def _sinh_taylor(x):
    """Seno hiperbólico por serie de Taylor."""
    if _abs(x) > 10:
        e = _exp_taylor(x)
        return (e - 1 / e) / 2
    result = x
    term = x
    for n in range(1, 10):
        term *= x * x / ((2 * n) * (2 * n + 1))
        result += term
    return result


def _exp_taylor(x):
    """Exponencial por serie de Taylor."""
    if x > 20:
        return 485165195.4
    if x < -20:
        return 0.0
    result = 1.0
    term = 1.0
    for n in range(1, 30):
        term *= x / n
        result += term
        if _abs(term) < 1e-15:
            break
    return result