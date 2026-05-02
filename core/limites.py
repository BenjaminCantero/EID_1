# core/limites.py
# Módulo de análisis de funciones por tramos generadas a partir del RUT
# Todos los cálculos implementados manualmente (sin numpy/math/sympy)


def seleccionar_caso(d8):
    """
    Determina el tipo de discontinuidad según d8 % 3.
    0 → removible, 1 → salto, 2 → infinita
    """
    residuo = d8 % 3
    if residuo == 0:
        return "removible", f"d8={d8} → {d8} mod 3 = 0 → Discontinuidad REMOVIBLE"
    elif residuo == 1:
        return "salto", f"d8={d8} → {d8} mod 3 = 1 → Discontinuidad de SALTO"
    else:
        return "infinita", f"d8={d8} → {d8} mod 3 = 2 → Discontinuidad INFINITA"


def construir_funcion(caso, a, digitos):
    """
    Construye la descripción textual de la función por tramos según el caso.
    Retorna (descripcion_str, tramos_dict)
    """
    d = digitos
    if caso == "removible":
        desc = (
            f"f(x) = (x - {a})(x + {d[0]}) / (x - {a}),  si x < {a}\n"
            f"       No definida en x = {a}"
        )
        tramos = {
            "formula_izq": f"(x - {a})(x + {d[0]}) / (x - {a})",
            "formula_der": f"No definida en x = {a}",
            "tipo": "removible",
            "a": a,
            "d1": d[0],
        }
    elif caso == "salto":
        desc = (
            f"f(x) = x + {d[1]},   si x < {a}\n"
            f"       x + {d[3]},   si x ≥ {a}"
        )
        tramos = {
            "formula_izq": f"x + {d[1]}",
            "formula_der": f"x + {d[3]}",
            "tipo": "salto",
            "a": a,
            "d2": d[1],
            "d4": d[3],
        }
    else:  # infinita
        desc = (
            f"f(x) = ({d[4] + 1}) / (x - {a})"
        )
        tramos = {
            "formula_izq": f"{d[4] + 1} / (x - {a})",
            "formula_der": f"{d[4] + 1} / (x - {a})",
            "tipo": "infinita",
            "a": a,
            "numerador": d[4] + 1,
        }
    return desc, tramos


def evaluar_funcion(x, tramos):
    """
    Evalúa f(x) según los tramos definidos.
    Retorna el valor numérico o None si no está definida.
    """
    caso = tramos["tipo"]
    a = tramos["a"]

    if caso == "removible":
        if x == a:
            return None  # No definida
        # Simplificado: (x-a)(x+d1)/(x-a) = x + d1
        return x + tramos["d1"]

    elif caso == "salto":
        if x < a:
            return x + tramos["d2"]
        else:
            return x + tramos["d4"]

    elif caso == "infinita":
        if x == a:
            return None
        return tramos["numerador"] / (x - a)

    return None


def calcular_limites(tramos):
    """
    Calcula límites laterales, existencia del límite, continuidad
    y clasifica la discontinuidad. Retorna dict con todo el análisis.
    """
    caso = tramos["tipo"]
    a = tramos["a"]
    resultado = {}
    pasos = []

    epsilon = 1e-7  # Valor muy pequeño para aproximarse a 'a'

    # Límite por la izquierda (x → a⁻)
    x_izq = a - epsilon
    lim_izq = evaluar_funcion(x_izq, tramos)

    # Límite por la derecha (x → a⁺)
    x_der = a + epsilon
    lim_der = evaluar_funcion(x_der, tramos)

    # Valor de la función en x = a
    f_en_a = evaluar_funcion(a, tramos)

    resultado["a"] = a
    resultado["lim_izq"] = lim_izq
    resultado["lim_der"] = lim_der
    resultado["f_en_a"] = f_en_a

    pasos.append(f"Punto de análisis: a = {a}")
    pasos.append("")

    if caso == "removible":
        lim_real_izq = a + tramos["d1"]
        lim_real_der = a + tramos["d1"]
        pasos.append(f"Simplificación algebraica de f1(x):")
        pasos.append(f"  f(x) = (x - {a})(x + {tramos['d1']}) / (x - {a})")
        pasos.append(f"  Cancelando (x - {a}) con x ≠ {a}:")
        pasos.append(f"  f(x) = x + {tramos['d1']}   (para x ≠ {a})")
        pasos.append("")
        pasos.append(f"Límite por la izquierda:")
        pasos.append(f"  lím (x→{a}⁻) f(x) = {a} + {tramos['d1']} = {lim_real_izq}")
        pasos.append(f"Límite por la derecha:")
        pasos.append(f"  lím (x→{a}⁺) f(x) = {a} + {tramos['d1']} = {lim_real_der}")
        pasos.append(f"  → Los límites laterales son iguales: el límite EXISTE = {lim_real_izq}")
        pasos.append("")
        pasos.append(f"Valor f({a}): No está definida (denominador se anula)")
        pasos.append("")
        pasos.append("Análisis de continuidad:")
        pasos.append(f"  • El límite existe: ✓ ({lim_real_izq})")
        pasos.append(f"  • f({a}) está definida: ✗ (no existe)")
        pasos.append(f"  • Conclusión: f NO es continua en x = {a}")
        pasos.append("")
        pasos.append("Tipo de discontinuidad: REMOVIBLE")
        pasos.append(f"  Justificación: El límite existe ({lim_real_izq}) pero la función")
        pasos.append(f"  no está definida en x = {a}. Si se define f({a}) = {lim_real_izq},")
        pasos.append(f"  la discontinuidad desaparece.")

        resultado["lim_existe"] = True
        resultado["lim_valor"] = lim_real_izq
        resultado["continua"] = False
        resultado["tipo_disc"] = "Removible"

    elif caso == "salto":
        lim_real_izq = a + tramos["d2"]
        lim_real_der = a + tramos["d4"]
        pasos.append(f"Límite por la izquierda (x → {a}⁻):")
        pasos.append(f"  f(x) = x + {tramos['d2']}  →  lím = {a} + {tramos['d2']} = {lim_real_izq}")
        pasos.append(f"Límite por la derecha (x → {a}⁺):")
        pasos.append(f"  f(x) = x + {tramos['d4']}  →  lím = {a} + {tramos['d4']} = {lim_real_der}")
        pasos.append("")

        if abs(lim_real_izq - lim_real_der) < 1e-9:
            pasos.append(f"  → Ambos límites son iguales ({lim_real_izq}): el límite EXISTE")
            resultado["lim_existe"] = True
            resultado["lim_valor"] = lim_real_izq
            f_a = evaluar_funcion(a, tramos)
            if abs(f_a - lim_real_izq) < 1e-9:
                resultado["continua"] = True
                resultado["tipo_disc"] = "Ninguna (continua)"
                pasos.append(f"  f({a}) = {f_a} = límite → la función ES CONTINUA en x = {a}")
            else:
                resultado["continua"] = False
                resultado["tipo_disc"] = "Removible"
                pasos.append(f"  Pero f({a}) = {f_a} ≠ límite → DISCONTINUIDAD REMOVIBLE")
        else:
            pasos.append(f"  → {lim_real_izq} ≠ {lim_real_der}: el límite NO EXISTE")
            pasos.append("")
            pasos.append("Análisis de continuidad:")
            pasos.append(f"  • El límite no existe: ✗")
            pasos.append(f"  • f({a}) = {evaluar_funcion(a, tramos)} (definida por tramo derecho)")
            pasos.append(f"  • Conclusión: f NO es continua en x = {a}")
            pasos.append("")
            pasos.append("Tipo de discontinuidad: SALTO")
            pasos.append(f"  Justificación: Los límites laterales existen pero son distintos.")
            pasos.append(f"  Salto = |{lim_real_der} - {lim_real_izq}| = {abs(lim_real_der - lim_real_izq)}")
            resultado["lim_existe"] = False
            resultado["lim_valor"] = None
            resultado["continua"] = False
            resultado["tipo_disc"] = "Salto"

        resultado["lim_real_izq"] = lim_real_izq
        resultado["lim_real_der"] = lim_real_der

    elif caso == "infinita":
        num = tramos["numerador"]
        pasos.append(f"Función: f(x) = {num} / (x - {a})")
        pasos.append("")
        pasos.append(f"Límite por la izquierda (x → {a}⁻):")
        pasos.append(f"  (x - {a}) → 0⁻  (negativo)")
        if num > 0:
            pasos.append(f"  {num} / 0⁻ → -∞")
            lim_izq_str = "-∞"
        else:
            pasos.append(f"  {num} / 0⁻ → +∞")
            lim_izq_str = "+∞"
        pasos.append(f"Límite por la derecha (x → {a}⁺):")
        pasos.append(f"  (x - {a}) → 0⁺  (positivo)")
        if num > 0:
            pasos.append(f"  {num} / 0⁺ → +∞")
            lim_der_str = "+∞"
        else:
            pasos.append(f"  {num} / 0⁺ → -∞")
            lim_der_str = "-∞"
        pasos.append("")
        pasos.append(f"  → El límite NO EXISTE (la función crece/decrece sin acotamiento)")
        pasos.append(f"  → Existe asíntota vertical en x = {a}")
        pasos.append("")
        pasos.append("Análisis de continuidad:")
        pasos.append(f"  • El límite no existe: ✗")
        pasos.append(f"  • f({a}) no está definida: ✗")
        pasos.append(f"  • Conclusión: f NO es continua en x = {a}")
        pasos.append("")
        pasos.append("Tipo de discontinuidad: INFINITA")
        pasos.append(f"  Justificación: La función crece sin límite al acercarse a x = {a}")
        pasos.append(f"  desde ambos lados. Hay asíntota vertical en x = {a}.")

        resultado["lim_existe"] = False
        resultado["lim_valor"] = None
        resultado["continua"] = False
        resultado["tipo_disc"] = "Infinita"
        resultado["lim_real_izq"] = lim_izq_str
        resultado["lim_real_der"] = lim_der_str

    resultado["pasos"] = pasos
    return resultado


def tabla_valores(tramos, n=4):
    """
    Genera tabla de valores cercanos al punto a.
    Retorna lista de (x, f(x)) para izquierda y derecha.
    """
    a = tramos["a"]
    offsets_izq = [-1, -0.1, -0.01, -0.001][:n]
    offsets_der = [0.001, 0.01, 0.1, 1][:n]

    filas = []
    for off in offsets_izq:
        x = a + off
        y = evaluar_funcion(x, tramos)
        if y is None:
            y_str = "No def."
        elif abs(y) > 1e10:
            y_str = "→ -∞" if y < 0 else "→ +∞"
        else:
            y_str = f"{y:.6f}"
        filas.append((f"{x:.4f}", y_str, "izq"))

    for off in offsets_der:
        x = a + off
        y = evaluar_funcion(x, tramos)
        if y is None:
            y_str = "No def."
        elif abs(y) > 1e10:
            y_str = "→ -∞" if y < 0 else "→ +∞"
        else:
            y_str = f"{y:.6f}"
        filas.append((f"{x:.4f}", y_str, "der"))

    return filas


def puntos_grafica_limite(tramos, ancho=400, alto=300, rango_x=10):
    """
    Genera puntos para graficar la función en el canvas de Tkinter.
    Retorna lista de segmentos (x1, y1, x2, y2) en coordenadas de pantalla.
    """
    a = tramos["a"]
    caso = tramos["tipo"]
    n = 200
    cx = ancho / 2
    cy = alto / 2
    escala_x = ancho / (2 * rango_x)
    escala_y = alto / (2 * rango_x)

    def mundo_a_pantalla(x, y):
        px = cx + x * escala_x
        py = cy - y * escala_y
        return px, py

    segmentos = []
    xs = [a - rango_x + 2 * rango_x * i / n for i in range(n + 1)]

    pts_izq = []
    pts_der = []

    for x in xs:
        if abs(x - a) < 0.05:
            continue
        y = evaluar_funcion(x, tramos)
        if y is None:
            continue
        if abs(y) > rango_x * 3:
            continue
        px, py = mundo_a_pantalla(x, y)
        if x < a:
            pts_izq.append((px, py))
        else:
            pts_der.append((px, py))

    def lista_a_segmentos(pts):
        segs = []
        for i in range(len(pts) - 1):
            segs.append((*pts[i], *pts[i + 1]))
        return segs

    segmentos.extend(lista_a_segmentos(pts_izq))
    segmentos.extend(lista_a_segmentos(pts_der))
    return segmentos, mundo_a_pantalla