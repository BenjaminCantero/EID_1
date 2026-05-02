# core/rut.py
# Módulo de validación y extracción de dígitos del RUT chileno


def limpiar_rut(rut_str):
    """Elimina puntos y guión del RUT ingresado."""
    return rut_str.strip().replace(".", "").replace("-", "").upper()


def validar_rut(rut_str):
    """
    Valida un RUT chileno usando el algoritmo oficial del módulo 11.

    Retorna:
        (es_valido: bool, pasos: list[str], digitos: list[int], dv_calculado: str)
    """
    limpio = limpiar_rut(rut_str)

    if len(limpio) < 2:
        return False, ["RUT demasiado corto."], [], ""

    cuerpo = limpio[:-1]
    dv_ingresado = limpio[-1]

    if not cuerpo.isdigit():
        return False, ["El cuerpo del RUT debe contener solo dígitos."], [], ""

    if len(cuerpo) < 7 or len(cuerpo) > 8:
        return False, ["El cuerpo del RUT debe tener entre 7 y 8 dígitos."], [], ""

    # Aseguramos 8 dígitos rellenando con cero a la izquierda si es necesario
    cuerpo_8 = cuerpo.zfill(8)

    serie = [2, 3, 4, 5, 6, 7]
    suma = 0
    pasos = []
    pasos.append(f"Cuerpo del RUT: {cuerpo_8}")
    pasos.append(f"DV ingresado: {dv_ingresado}")
    pasos.append("")
    pasos.append("Multiplicación por serie [2,3,4,5,6,7] de derecha a izquierda:")

    for i, digito in enumerate(reversed(cuerpo_8)):
        factor = serie[i % 6]
        producto = int(digito) * factor
        suma += producto
        pasos.append(f"  {digito} × {factor} = {producto}  (suma acumulada: {suma})")

    pasos.append(f"\nSuma total = {suma}")
    pasos.append(f"Resto = {suma} mod 11 = {suma % 11}")

    resto = suma % 11
    resultado = 11 - resto

    if resultado == 11:
        dv_calculado = "0"
    elif resultado == 10:
        dv_calculado = "K"
    else:
        dv_calculado = str(resultado)

    pasos.append(f"11 - {resto} = {resultado}  →  DV esperado: {dv_calculado}")
    es_valido = dv_calculado == dv_ingresado
    pasos.append(f"\nDV calculado '{dv_calculado}' {'==' if es_valido else '!='} DV ingresado '{dv_ingresado}'")
    pasos.append(f"RUT {'VÁLIDO ✓' if es_valido else 'INVÁLIDO ✗'}")

    digitos = [int(c) for c in cuerpo_8]
    return es_valido, pasos, digitos, dv_calculado


def formatear_rut(cuerpo_8, dv):
    """Formatea el RUT con puntos y guión para mostrarlo."""
    c = cuerpo_8.lstrip("0") or "0"
    if len(c) > 6:
        c = c[:-6] + "." + c[-6:-3] + "." + c[-3:]
    elif len(c) > 3:
        c = c[:-3] + "." + c[-3:]
    return c + "-" + dv