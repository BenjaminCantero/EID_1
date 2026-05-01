# EID_1
Evaluación Integrada de Desempeño N°1 Análisis y Modelamiento de Secciones Cónicas y Funciones por Tramos a partir del RUT
---
## Requisitos

- Python 3.8 o superior
- **Sin dependencias externas** — usa únicamente la librería estándar de Python (`tkinter`)
- Tkinter ya viene incluido en Python. Si no lo tienes: `sudo apt install python3-tk` (Linux)

---

## Cómo ejecutar

```bash
python main.py
```

---

## Estructura del proyecto

```
proyecto_EID/
│
├── main.py                   # Punto de entrada de la aplicación
├── README.md                 # Este archivo
├── etica.md                  # Código de ética del grupo
│
├── core/
│   ├── rut.py                # Validación RUT (módulo 11) y extracción de dígitos
│   ├── conica.py             # Coeficientes, clasificación, forma canónica, graficación
│   └── limites.py            # Funciones por tramos, límites laterales, discontinuidades
│
└── ui/
    ├── interfaz_conica.py    # Interfaz gráfica — módulo de cónicas
    └── interfaz_limites.py   # Interfaz gráfica — módulo de límites
```

---

## Módulos del sistema

### `core/rut.py`
- Validación del RUT chileno mediante el **algoritmo oficial del módulo 11**
- Muestra el procedimiento paso a paso
- Extracción de los 8 dígitos del cuerpo del RUT

### `core/conica.py`
- Construcción de coeficientes A, B, C, D, E a partir de los dígitos del RUT
- Aplicación de ajustes (hipérbola, circunferencia, parábola)
- Clasificación automática de la cónica
- Transformación a **forma canónica paso a paso**
- **Procedimiento inverso** (canónica → general)
- Generación de puntos para graficación (usando series de Taylor, sin `math`)

### `core/limites.py`
- Selección automática del tipo de función según `d8 % 3`
- Construcción de la función por tramos
- Cálculo de límites laterales
- Tabla de valores numéricos cercanos al punto `a`
- Clasificación de discontinuidad (removible, salto, infinita)

---

## RUTs de prueba verificados

| RUT | Cónica | Discontinuidad |
|-----|--------|----------------|
| 12.345.678-5 | Elipse | Infinita |
| 11.234.567-1 | Parábola | Salto |
| 13.456.789-9 | Hipérbola | Removible |
| 11.345.678-7 | Circunferencia | Infinita |
| 17.654.321-3 | Hipérbola | Salto |
| 14.725.836-4 | Elipse | Removible |

Estos RUTs cubren las 4 cónicas y los 3 tipos de discontinuidad.

---

## Restricciones cumplidas

✅ Sin uso de `numpy`, `math`, `sympy`, `scipy`, `pandas`  
✅ Todos los cálculos implementados manualmente  
✅ Raíz cuadrada por método de Newton-Raphson  
✅ Seno y coseno por series de Taylor  
✅ Logaritmos/exponenciales por series de Taylor  
✅ Interfaz con Tkinter (librería estándar)  
✅ Campos vacíos para defensa oral  
✅ Código modular separado en archivos  

---

## Guía de desarrollo colaborativo (GitHub)

Cada integrante debe:
1. Clonar el repositorio
2. Crear su rama: `git checkout -b nombre/feature`
3. Hacer commits descriptivos: `git commit -m "feat: implementar forma canónica elipse"`
4. Hacer merge a main mediante Pull Request
5. Mínimo **3 commits por integrante**

---

## Autoría
- Universidad Católica de Temuco — Ingeniería Civil en Informática
