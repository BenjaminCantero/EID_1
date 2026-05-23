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
EID_1/
│
├── main.py                   # Punto de entrada de la aplicación
├── README.md                 # Este archivo
├── etica.md                  # Código de ética del grupo
│
├── core/
│   ├── __init__.py           # Paquete core
│   ├── rut.py                # Validación RUT (módulo 11)
│   ├── conica.py             # Lógica de cónicas y formas canónicas
│   ├── limites.py            # Funciones por tramos y límites
│   ├── modelos.py            # Modelos matemáticos auxiliares
│   └── graficas.py           # Generación de puntos y tablas para graficación
│
└── ui/
    ├── __init__.py           # Paquete ui
    ├── app.py                # Aplicación principal y navegación
    ├── panel_conica.py       # Panel de análisis de cónicas
    ├── panel_limites.py      # Panel de funciones y límites
    └── componentes.py        # Constantes y helpers UI reutilizables
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

### `core/limites.py`
- Selección automática del tipo de función según `d8 % 3`
- Construcción de la función por tramos
- Cálculo de límites laterales y análisis de continuidad
- Clasificación de discontinuidad (removible, salto, infinita)

### `core/modelos.py`
- Raíz cuadrada por Newton-Raphson
- Cálculo de cuadrados completos
- Seno, coseno, exponencial e hiperbólicos por series de Taylor

### `core/graficas.py`
- Genera puntos para la visualización de cónicas
- Genera tablas de valores para límites laterales
- Construye segmentos de canvas para la gráfica de funciones por tramos

### `ui/app.py`
- Controla la aplicación Tkinter y el notebook principal
- Centraliza la creación de pestañas y la navegación interna

### `ui/panel_conica.py`
- Presenta la UI de cónicas
- Solicita el RUT y muestra resultados matemáticos,
  forma canónica y gráficos

### `ui/panel_limites.py`
- Presenta la UI de límites y discontinuidades
- Genera la función por tramos, calcula límites y muestra tablas

### `ui/componentes.py`
- Define colores y estilos reutilizables
- Centraliza la configuración visual de Tkinter

---

## Cambios en la arquitectura (Service Layer)

- Se añadió `core/services.py` como capa de servicio que orquesta la lógica de negocio
    para el análisis de cónicas y funciones por tramos. Este módulo expone las funciones
    `analizar_conica(rut_str)` y `analizar_limites(rut_str)` como puntos únicos de entrada.
- Los resultados ahora se retornan como DTOs basados en `@dataclass`:
    - `ConicaAnalysis` (resultado completo del análisis de cónicas)
    - `LimitesAnalysis` (resultado completo del análisis de límites)
- Las UIs `ui/panel_conica.py` y `ui/panel_limites.py` fueron refactorizadas para consumir
    estos servicios en lugar de invocar directamente los módulos de dominio (`core.conica`,
    `core.limites`, `core.rut`). Esto mejora la separación de responsabilidades y facilita
    las pruebas unitarias y la reutilización de la lógica.
- Los módulos de dominio (`core/conica.py`, `core/limites.py`, `core/rut.py`) se mantienen
    como implementaciones puras de la lógica matemática; `core/services.py` orquesta su uso.
- `test_services.py` sirve como verificación rápida del Service Layer y documenta los
    errores manejados (`RUTInvalidoError`, `ConicaInvalidaError`, `LimiteInvalidoError`).

Beneficios:

- Mejor separación entre presentación y lógica de negocio.
- Objetos de datos (`dataclasses`) que facilitan serialización y testing.
- UI más simple y menos acoplada al dominio.


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
