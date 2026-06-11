# core/conica.py
# Construcción de la ecuación general, clasificación y forma canónica
# Todos los cálculos implementados manualmente (sin numpy/math/sympy)

from core.modelos import raiz_cuadrada_manual, completar_cuadrado
from core.validators import validar_no_cero
from core.exceptions import ConicaInvalidaError


def calcular_coeficientes(digitos, dv_str):
    """
    Construye los coeficientes A, B, C, D, E de la ecuación general
    Ax² + By² + Cx + Dy + E = 0 a partir de los dígitos del RUT.

    Retorna:
        (A, B, C, D, E, pasos: list[str], ajustes: list[str])
        
    Raises:
        ConicaInvalidaError: Si hay indeterminación (división por cero)
    """
    d = digitos  # d[0]=d1 ... d[7]=d8

    # Variable auxiliar v
    if dv_str == "K":
        v = 10
    elif dv_str == "0":
        v = 11
    else:
        v = int(dv_str)
    
    # Validar que v no sea cero (protección)
    if v == 0:
        raise ConicaInvalidaError(
            mensaje="Indeterminación matemática: Divisor v = 0",
            razon="El dígito verificador genera una indeterminación en cálculo de coeficientes"
        )

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
    if abs(A - B) < 1e-9:  # A == B con tolerancia flotante
        return "Circunferencia"
    if (A > 0 and B > 0) or (A < 0 and B < 0):
        return "Elipse"
    return "Hipérbola"


def ecuacion_str(A, B, C, D, E):
    """Retorna la ecuación general como string legible."""
    def term(coef, var, primero=False):
        if abs(coef) < 1e-9:
            return ""
        signo = "+" if coef > 0 and not primero else ("-" if coef < 0 and not primero else "")
        valor = abs(coef)
        if abs(valor - 1.0) < 1e-9 and "²" in var:
            num = signo + var if signo else ("-" + var if coef < 0 else var)
        elif abs(valor - 1.0) < 1e-9:
            num = signo + var if signo else ("-" + var if coef < 0 else var)
        else:
            num = f"{signo}{valor:.4g}{var}" if signo else (f"{valor:.4g}{var}" if coef > 0 else f"-{valor:.4g}{var}")
        return num.strip()

    partes = []
    if abs(A) > 1e-9:
        partes.append(f"({A:.4g})x²")
    if abs(B) > 1e-9:
        signo = " + " if B > 0 else " - "
        partes.append(f"{signo}({abs(B):.4g})y²")
    if abs(C) > 1e-9:
        signo = " + " if C > 0 else " - "
        partes.append(f"{signo}({abs(C):.4g})x")
    if abs(D) > 1e-9:
        signo = " + " if D > 0 else " - "
        partes.append(f"{signo}({abs(D):.4g})y")
    if abs(E) > 1e-9:
        signo = " + " if E > 0 else " - "
        partes.append(f"{signo}{abs(E):.4g}")
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


def _canonica_circunferencia(A, B, C, D, E):
    pasos = []
    elementos = {}
    pasos.append("=== Circunferencia: A = B ===")
    pasos.append(f"Ecuación general: {ecuacion_str(A, B, C, D, E)}")
    pasos.append("")
    pasos.append("Nota: no hay término xy, por lo tanto no se requiere rotación de ejes.")
    pasos.append("Paso 1: Dividir toda la ecuación por A para normalizar los coeficientes:")
    a2 = A
    c2 = C / a2
    d2 = D / a2
    e2 = E / a2
    pasos.append(f"  x² + y² + ({c2:.4g})x + ({d2:.4g})y + {e2:.4g} = 0")
    pasos.append("")
    pasos.append("Paso 2: Agrupar términos y pasar la constante al otro lado:")
    pasos.append(f"  x² + ({c2:.4g})x + y² + ({d2:.4g})y = {-e2:.4g}")
    pasos.append("")
    pasos.append("Paso 3: Completar el cuadrado en x:")
    h, add_x = completar_cuadrado(1, c2)
    pasos.append(f"  x² + ({c2:.4g})x = (x + {c2/2:.4g})² - ({c2/2:.4g})²")
    pasos.append(f"  Término agregado al Lado Izquierdo (LHS): ({c2/2:.4g})² = {(c2/2)**2:.4g}")
    pasos.append(f"  Término equivalente en el Lado Derecho (RHS): +{(c2/2)**2:.4g}")
    pasos.append(f"  h = {h:.4g}")
    pasos.append("")
    pasos.append("Paso 4: Completar el cuadrado en y:")
    k, add_y = completar_cuadrado(1, d2)
    pasos.append(f"  y² + ({d2:.4g})y = (y + {d2/2:.4g})² - ({d2/2:.4g})²")
    pasos.append(f"  Término agregado al Lado Izquierdo (LHS): ({d2/2:.4g})² = {(d2/2)**2:.4g}")
    pasos.append(f"  Término equivalente en el Lado Derecho (RHS): +{(d2/2)**2:.4g}")
    pasos.append(f"  k = {k:.4g}")
    pasos.append("")
    r2 = -e2 - add_x - add_y
    pasos.append("Paso 5: Reescribir con los cuadrados completos y el término constante al otro lado:")
    pasos.append(f"  (x - ({h:.4g}))² + (y - ({k:.4g}))² = {r2:.4g}")
    pasos.append(f"  Centro de traslación: (h, k) = ({h:.4g}, {k:.4g})")

    if r2 < 0:
        pasos.append("  ⚠ r² < 0: la cónica no tiene solución real en el plano real.")
        canonica = f"(x - {h:.4g})² + (y - {k:.4g})² = {r2:.4g}  [sin solución real]"
    else:
        r = raiz_cuadrada_manual(r2)
        pasos.append(f"  Radio r = √{r2:.4g} ≈ {r:.4f}")
        canonica = f"(x - {h:.4g})² + (y - {k:.4g})² = {r2:.4g}"
        elementos["Centro"] = (round(h, 4), round(k, 4))
        elementos["Radio"] = round(r, 4)

    pasos.append("")
    pasos.append("=== Procedimiento inverso (canónica → general) ===")
    pasos.append(f"  Partiendo de: (x - {h:.4g})² + (y - {k:.4g})² = {r2:.4g}")
    pasos.append(f"  Expandir (x - {h:.4g})² = x² - {2*h:.4g}x + {h**2:.4g}")
    pasos.append(f"  Expandir (y - {k:.4g})² = y² - {2*k:.4g}y + {k**2:.4g}")
    pasos.append(f"  Sumar y pasar {r2:.4g} al otro lado:")
    pasos.append(f"  x² + y² - {2*h:.4g}x - {2*k:.4g}y + {h**2 + k**2 - r2:.4g} = 0")
    if abs(A - 1.0) > 1e-9:
        pasos.append(f"  Multiplicar toda la ecuación por A = {A:.4g} para recuperar la forma general original:")
        pasos.append(f"  {A:.4g}x² + {A:.4g}y² - {2*A*h:.4g}x - {2*A*k:.4g}y + {A*(h**2 + k**2 - r2):.4g} = 0")

    return pasos, elementos, canonica


def _canonica_elipse(A, B, C, D, E):
    pasos = []
    elementos = {}
    pasos.append("=== Elipse: A ≠ B, mismo signo ===")
    pasos.append(f"Ecuación general: {ecuacion_str(A, B, C, D, E)}")
    pasos.append("")
    pasos.append("Nota: no hay término xy, por lo tanto no se requiere rotación de ejes.")
    pasos.append("Paso 1: Agrupar términos en x e y y pasar la constante al otro lado:")
    pasos.append(f"  {A:.4g}(x² + {C/A:.4g}x) + {B:.4g}(y² + {D/B:.4g}y) = {-E:.4g}")
    pasos.append("")
    pasos.append("Paso 2: Completar el cuadrado en x:")
    h, add_x = completar_cuadrado(A, C)
    pasos.append(f"  {A:.4g}(x² + {C/A:.4g}x + ({C/(2*A):.4g})²) = {A:.4g}(x - {h:.4g})²")
    pasos.append(f"  Término agregado a la izquierda: {A:.4g} · ({C/(2*A):.4g})² = {A * (C/(2*A))**2:.4g}")
    pasos.append(f"  Ajuste en el lado derecho: +{A * (C/(2*A))**2:.4g}")
    pasos.append(f"  h = {h:.4g}")
    pasos.append("")
    pasos.append("Paso 3: Completar el cuadrado en y:")
    k, add_y = completar_cuadrado(B, D)
    pasos.append(f"  {B:.4g}(y² + {D/B:.4g}y + ({D/(2*B):.4g})²) = {B:.4g}(y - {k:.4g})²")
    pasos.append(f"  Término agregado a la izquierda: {B:.4g} · ({D/(2*B):.4g})² = {B * (D/(2*B))**2:.4g}")
    pasos.append(f"  Ajuste en el lado derecho: +{B * (D/(2*B))**2:.4g}")
    pasos.append(f"  k = {k:.4g}")
    pasos.append("")
    constante = -E - add_x - add_y
    pasos.append("Paso 4: Reescribir en términos de cuadrados completos:")
    pasos.append(f"  {A:.4g}(x - {h:.4g})² + {B:.4g}(y - {k:.4g})² = {constante:.4g}")

    if abs(constante) < 1e-9:
        pasos.append("  ⚠ Constante = 0: elipse puntual.")
        canonica = f"{A:.4g}(x-{h:.4g})² + {B:.4g}(y-{k:.4g})² = 0"
        return pasos, elementos, canonica

    pasos.append("")
    pasos.append("Paso 5: Dividir para obtener la forma estándar con el Lado Derecho (RHS) = 1:")
    a2 = constante / A
    b2 = constante / B
    pasos.append(f"  a² = {constante:.4g} / {A:.4g} = {a2:.4g}")
    pasos.append(f"  b² = {constante:.4g} / {B:.4g} = {b2:.4g}")
    canonica = f"(x - {h:.4g})²/{a2:.4g} + (y - {k:.4g})²/{b2:.4g} = 1"
    pasos.append(f"  Forma canónica: {canonica}")

    if a2 > 0 and b2 > 0:
        a = raiz_cuadrada_manual(a2)
        b = raiz_cuadrada_manual(b2)
        elementos["Centro"] = (round(h, 4), round(k, 4))
        elementos["a (semi-eje mayor)"] = round(max(a, b), 4)
        elementos["b (semi-eje menor)"] = round(min(a, b), 4)
        c_foco = raiz_cuadrada_manual(abs(a2 - b2))
        if a2 >= b2:
            elementos["Focos"] = (round(h - c_foco, 4), round(k, 4)), (round(h + c_foco, 4), round(k, 4))
            elementos["Vértices"] = (round(h - a, 4), round(k, 4)), (round(h + a, 4), round(k, 4))
        else:
            elementos["Focos"] = (round(h, 4), round(k - c_foco, 4)), (round(h, 4), round(k + c_foco, 4))
            elementos["Vértices"] = (round(h, 4), round(k - b, 4)), (round(h, 4), round(k + b, 4))

    pasos.append("")
    pasos.append("=== Procedimiento inverso (canónica → general) ===")
    pasos.append(f"  Partiendo de: {canonica}")
    pasos.append(f"  Multiplicar por {constante:.4g} para recuperar la forma con coeficientes {A:.4g} y {B:.4g}:")
    pasos.append(f"  {A:.4g}(x - {h:.4g})² + {B:.4g}(y - {k:.4g})² = {constante:.4g}")
    pasos.append(f"  Expandir: {A:.4g}(x² - {2*h:.4g}x + {h**2:.4g}) + {B:.4g}(y² - {2*k:.4g}y + {k**2:.4g}) = {constante:.4g}")
    pasos.append("  Recolectar términos y pasar todo al lado izquierdo:")
    pasos.append(f"  {A:.4g}x² + {B:.4g}y² - {2*A*h:.4g}x - {2*B*k:.4g}y + {A*h**2 + B*k**2 - constante:.4g} = 0")

    return pasos, elementos, canonica


def _canonica_hiperbola(A, B, C, D, E):
    pasos = []
    elementos = {}
    pasos.append("=== Hipérbola: A y B con signos opuestos ===")
    pasos.append(f"Ecuación general: {ecuacion_str(A, B, C, D, E)}")
    pasos.append("")
    pasos.append("Nota: no hay término xy, por lo tanto no se requiere rotación de ejes.")
    pasos.append("Paso 1: Agrupar términos en x e y y pasar la constante al otro lado:")
    pasos.append(f"  {A:.4g}(x² + {C/A:.4g}x) + {B:.4g}(y² + {D/B:.4g}y) = {-E:.4g}")
    pasos.append("")
    pasos.append("Paso 2: Completar el cuadrado en x:")
    h, add_x = completar_cuadrado(A, C)
    pasos.append(f"  {A:.4g}(x² + {C/A:.4g}x + ({C/(2*A):.4g})²) = {A:.4g}(x - {h:.4g})²")
    pasos.append(f"  Término agregado a la izquierda: {A:.4g} · ({C/(2*A):.4g})² = {A * (C/(2*A))**2:.4g}")
    pasos.append(f"  Ajuste en el lado derecho: +{A * (C/(2*A))**2:.4g}")
    pasos.append(f"  h = {h:.4g}")
    pasos.append("")
    pasos.append("Paso 3: Completar el cuadrado en y:")
    k, add_y = completar_cuadrado(B, D)
    pasos.append(f"  {B:.4g}(y² + {D/B:.4g}y + ({D/(2*B):.4g})²) = {B:.4g}(y - {k:.4g})²")
    pasos.append(f"  Término agregado a la izquierda: {B:.4g} · ({D/(2*B):.4g})² = {B * (D/(2*B))**2:.4g}")
    pasos.append(f"  Ajuste en el lado derecho: +{B * (D/(2*B))**2:.4g}")
    pasos.append(f"  k = {k:.4g}")
    pasos.append("")
    constante = -E - add_x - add_y
    pasos.append(f"Paso 4: Reescribir con cuadrados completos:")
    pasos.append(f"  {A:.4g}(x - {h:.4g})² + {B:.4g}(y - {k:.4g})² = {constante:.4g}")

    if abs(constante) < 1e-9:
        canonica = f"{A:.4g}(x-{h:.4g})² + {B:.4g}(y-{k:.4g})² = 0  [hipérbola degenerada]"
        return pasos, elementos, canonica

    pasos.append("")
    pasos.append("Paso 5: Dividir por la constante para obtener la forma estándar:")
    a2 = constante / A
    b2 = constante / B
    pasos.append(f"  a² = {constante:.4g}/{A:.4g} = {a2:.4g}")
    pasos.append(f"  b² = {constante:.4g}/{B:.4g} = {b2:.4g}")

    if a2 > 0:
        canonica = f"(x-{h:.4g})²/{a2:.4g} - (y-{k:.4g})²/{abs(b2):.4g} = 1"
        pasos.append(f"  Hipérbola horizontal: {canonica}")
        a = raiz_cuadrada_manual(a2)
        b = raiz_cuadrada_manual(abs(b2))
        c_foco = raiz_cuadrada_manual(a2 + abs(b2))
        elementos["Centro"] = (round(h, 4), round(k, 4))
        elementos["Vértices"] = (round(h - a, 4), round(k, 4)), (round(h + a, 4), round(k, 4))
        elementos["Focos"] = (round(h - c_foco, 4), round(k, 4)), (round(h + c_foco, 4), round(k, 4))
        elementos["Eje transverso"] = f"2a = {2*a:.4g}"
        elementos["Eje conjugado"] = f"2b = {2*b:.4g}"
    else:
        canonica = f"(y-{k:.4g})²/{abs(b2):.4g} - (x-{h:.4g})²/{abs(a2):.4g} = 1"
        pasos.append(f"  Hipérbola vertical: {canonica}")
        a = raiz_cuadrada_manual(abs(a2))
        b = raiz_cuadrada_manual(abs(b2))
        c_foco = raiz_cuadrada_manual(abs(a2) + abs(b2))
        elementos["Centro"] = (round(h, 4), round(k, 4))
        elementos["Vértices"] = (round(h, 4), round(k - b, 4)), (round(h, 4), round(k + b, 4))
        elementos["Focos"] = (round(h, 4), round(k - c_foco, 4)), (round(h, 4), round(k + c_foco, 4))

    pasos.append("")
    pasos.append("=== Procedimiento inverso (canónica → general) ===")
    pasos.append(f"  Partiendo de: {canonica}")
    pasos.append(f"  Multiplicar toda la ecuación por la constante original = {constante:.4g}:")
    pasos.append(f"  {A:.4g}(x - {h:.4g})² + {B:.4g}(y - {k:.4g})² = {constante:.4g}")
    pasos.append(f"  Expandir: {A:.4g}(x² - {2*h:.4g}x + {h**2:.4g}) + {B:.4g}(y² - {2*k:.4g}y + {k**2:.4g}) = {constante:.4g}")
    pasos.append("  Recolectar términos y pasar todo al lado izquierdo:")
    pasos.append(f"  {A:.4g}x² + {B:.4g}y² - {2*A*h:.4g}x - {2*B*k:.4g}y + {A*h**2 + B*k**2 - constante:.4g} = 0")

    return pasos, elementos, canonica


def _canonica_parabola(A, B, C, D, E):
    pasos = []
    elementos = {}

    if abs(B) < 1e-9:
        # Parábola de eje vertical: Ax² + Cx + Dy + E = 0
        pasos.append("=== Parábola de eje vertical (B = 0) ===")
        pasos.append(f"Ecuación general: {ecuacion_str(A, B, C, D, E)}")
        pasos.append("")
        pasos.append("Nota: no hay término xy, por lo tanto no se requiere rotación de ejes.")
        pasos.append("Paso 1: Completar el cuadrado en x:")
        h, add_x = completar_cuadrado(A, C)
        pasos.append(f"  {A:.4g}(x² + {C/A:.4g}x + ({C/(2*A):.4g})²) = {A:.4g}(x - {h:.4g})²")
        pasos.append(f"  Término agregado: {A:.4g} · ({C/(2*A):.4g})² = {A * (C/(2*A))**2:.4g}")
        pasos.append("")
        pasos.append("Paso 2: Reescribir y despejar y:")
        const = -add_x - E
        pasos.append(f"  {A:.4g}(x - {h:.4g})² + {add_x:.4g} + {D:.4g}y + {E:.4g} = 0")
        pasos.append(f"  {D:.4g}y = -{A:.4g}(x - {h:.4g})² - {add_x:.4g} - {E:.4g}")
        if abs(D) < 1e-9:
            pasos.append("  ⚠ D = 0: ecuación sin término y, posible parábola degenerada.")
            canonica = "Degenerada"
            return pasos, elementos, canonica
        p_coef = -A / D
        q = const / D
        pasos.append(f"  y = {p_coef:.4g}(x - {h:.4g})² + {q:.4g}")
        canonica = f"y = {p_coef:.4g}(x - {h:.4g})² + {q:.4g}"
        elementos["Vértice"] = (round(h, 4), round(q, 4))
        if abs(p_coef) > 1e-9:
            p_focal = 1 / (4 * p_coef)
            elementos["Foco"] = (round(h, 4), round(q + p_focal, 4))
            elementos["Directriz"] = f"y = {q - p_focal:.4g}"
        pasos.append(f"  Forma canónica: {canonica}")
    else:
        # Parábola de eje horizontal: By² + Cx + Dy + E = 0
        pasos.append("=== Parábola de eje horizontal (A = 0) ===")
        pasos.append(f"Ecuación general: {ecuacion_str(A, B, C, D, E)}")
        pasos.append("")
        pasos.append("Nota: no hay término xy, por lo tanto no se requiere rotación de ejes.")
        pasos.append("Paso 1: Completar el cuadrado en y:")
        k, add_y = completar_cuadrado(B, D)
        pasos.append(f"  {B:.4g}(y² + {D/B:.4g}y + ({D/(2*B):.4g})²) = {B:.4g}(y - {k:.4g})²")
        pasos.append(f"  Término agregado: {B:.4g} · ({D/(2*B):.4g})² = {B * (D/(2*B))**2:.4g}")
        pasos.append("")
        pasos.append("Paso 2: Reescribir y despejar x:")
        const = -add_y - E
        pasos.append(f"  {C:.4g}x = -{B:.4g}(y - {k:.4g})² - {add_y:.4g} - {E:.4g}")
        if abs(C) < 1e-9:
            pasos.append("  ⚠ C = 0: ecuación sin término x, posible parábola degenerada.")
            canonica = "Degenerada"
            return pasos, elementos, canonica
        p_coef = -B / C
        q = const / C
        pasos.append(f"  x = {p_coef:.4g}(y - {k:.4g})² + {q:.4g}")
        canonica = f"x = {p_coef:.4g}(y - {k:.4g})² + {q:.4g}"
        elementos["Vértice"] = (round(q, 4), round(k, 4))
        if abs(p_coef) > 1e-9:
            p_focal = 1 / (4 * p_coef)
            elementos["Foco"] = (round(q + p_focal, 4), round(k, 4))
            elementos["Directriz"] = f"x = {q - p_focal:.4g}"
        pasos.append(f"  Forma canónica: {canonica}")

    pasos.append("")
    pasos.append("=== Procedimiento inverso (canónica → general) ===")
    if abs(B) < 1e-9:
        pasos.append(f"  Partiendo de: {canonica}")
        pasos.append(f"  Expandir (x - {h:.4g})² = x² - {2*h:.4g}x + {h**2:.4g}")
        pasos.append(f"  Multiplicar por {p_coef:.4g} y sumar {q:.4g} para recuperar la forma general en y.")
        pasos.append(f"  Resultado: {A:.4g}x² + {C:.4g}x + {D:.4g}y + {E:.4g} = 0")
    else:
        pasos.append(f"  Partiendo de: {canonica}")
        pasos.append(f"  Expandir (y - {k:.4g})² = y² - {2*k:.4g}y + {k**2:.4g}")
        pasos.append(f"  Multiplicar por {p_coef:.4g} y sumar {q:.4g} para recuperar la forma general en x.")
        pasos.append(f"  Resultado: {A:.4g}x + {B:.4g}y² + {D:.4g}y + {E:.4g} = 0")

    return pasos, elementos, canonica
