import tkinter as tk
from tkinter import ttk

from core.log_service import setup_logger
from ui.componentes import AZUL_OSCURO, AZUL_MEDIO, AZUL_CLARO, AMARILLO, BLANCO, GRIS_TEXTO, ROJO, configurar_estilos_ttk
from ui.panel_conica import PanelConica
from ui.panel_limites import PanelLimites


class AppEID(tk.Tk):
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
        self.logger.info("Inicializando aplicación EID")
        self.title("EID MAT1186 — Cónicas y Límites · UCT 2026")
        self.geometry("1050x700")
        self.minsize(900, 620)
        self.configure(bg=AZUL_OSCURO)
        self.resizable(True, True)
        configurar_estilos_ttk()
        self._construir_ui()

    def _construir_ui(self):
        barra = tk.Frame(self, bg=AZUL_MEDIO, height=45)
        barra.pack(fill="x")
        barra.pack_propagate(False)

        tk.Label(barra,
                 text="🎓  EID N°1 — MAT1186 · Introducción al Cálculo · UCT 2026",
                 font=("Helvetica", 12, "bold"),
                 bg=AZUL_MEDIO, fg=AMARILLO).pack(side="left", padx=15, pady=8)

        tk.Label(barra,
                 text="Versión 2026 · Benjamin C. Eduardo D. Ricardo G.",
                 font=("Helvetica", 8),
                 bg=AZUL_MEDIO, fg=GRIS_TEXTO).pack(side="right", padx=12)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        self.panel_conica = PanelConica(self.notebook,
                                         cambiar_tab_callback=self._ir_limites,
                                         logger=self.logger)
        self.notebook.add(self.panel_conica, text="  📐  Secciones Cónicas  ")

        self.panel_limites = PanelLimites(self.notebook, logger=self.logger)
        self.notebook.add(self.panel_limites, text="  📊  Funciones y Límites  ")

        self._agregar_tab_acerca()

    def _ir_limites(self):
        self.notebook.select(1)

    def _agregar_tab_acerca(self):
        frame = tk.Frame(self.notebook, bg=AZUL_OSCURO)
        self.notebook.add(frame, text="  ℹ  Acerca del Proyecto  ")

        # Crear scrollbar para contenido largo
        canvas_frame = tk.Canvas(frame, bg=AZUL_OSCURO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas_frame.yview)
        scrollable_frame = tk.Frame(canvas_frame, bg=AZUL_OSCURO)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))
        )
        
        canvas_frame.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_frame.configure(yscrollcommand=scrollbar.set)
        canvas_frame.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ── Título principal ────────────────────────────────────
        tk.Label(scrollable_frame,
                 text="🎓 Evaluación Integrada de Desempeño N°1",
                 font=("Helvetica", 16, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(pady=(20, 8))

        tk.Label(scrollable_frame,
                 text="Análisis y Modelamiento de Secciones Cónicas\ny Funciones por Tramos a partir del RUT",
                 font=("Helvetica", 11),
                 bg=AZUL_OSCURO, fg=BLANCO,
                 justify="center").pack(pady=8)

        separador = tk.Frame(scrollable_frame, bg=AMARILLO, height=2, width=500)
        separador.pack(pady=10)

        # ── Información del proyecto ────────────────────────────
        info_frame = tk.Frame(scrollable_frame, bg=AZUL_OSCURO)
        info_frame.pack(fill="x", padx=40, pady=10)
        
        info = [
            ("📚 Curso", "MAT1186 — Introducción al Cálculo"),
            ("🏫 Institución", "Universidad Católica de Temuco"),
            ("💻 Carrera", "Ingeniería Civil en Informática"),
            ("📅 Año", "2026"),
            ("🔧 Tecnología", "Python 3.8+ • Tkinter (sin librerías matemáticas)"),
        ]
        for etiqueta, valor in info:
            row = tk.Frame(info_frame, bg=AZUL_OSCURO)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=etiqueta,
                     font=("Helvetica", 9, "bold"),
                     bg=AZUL_OSCURO, fg=AMARILLO, width=18, anchor="w").pack(side="left")
            tk.Label(row, text=valor,
                     font=("Helvetica", 9),
                     bg=AZUL_OSCURO, fg=BLANCO).pack(side="left")

        separador2 = tk.Frame(scrollable_frame, bg=AZUL_MEDIO, height=1, width=500)
        separador2.pack(pady=12)

        # ── Guía de uso rápida ──────────────────────────────────
        tk.Label(scrollable_frame,
                 text="📖 Guía de Uso Rápida",
                 font=("Helvetica", 11, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(anchor="w", padx=40)

        instruc_frame = tk.Frame(scrollable_frame, bg=AZUL_CLARO, padx=15, pady=12)
        instruc_frame.pack(fill="x", padx=40, pady=(3, 12))
        
        instrucciones = (
            "🔹 Pestaña 'Secciones Cónicas':\n"
            "   1. Ingrese un RUT chileno válido (ej: 12.345.678-9)\n"
            "   2. Presione 'Analizar' para generar la cónica\n"
            "   3. Revise: validación, ecuación, tipo, forma canónica\n"
            "   4. Complete los elementos geométricos (Centro, Vértices, Focos, etc.)\n\n"
            "🔹 Pestaña 'Funciones y Límites':\n"
            "   1. Ingrese el mismo RUT para generar la función por tramos\n"
            "   2. El sistema selecciona automáticamente el tipo de discontinuidad\n"
            "   3. Analice la tabla de valores y la gráfica\n"
            "   4. Complete los campos de defensa (límites, continuidad, tipo)\n\n"
        )
        tk.Label(instruc_frame, text=instrucciones,
                 font=("Courier", 8),
                 bg=AZUL_CLARO, fg=BLANCO,
                 justify="left").pack(anchor="w")

        # ── Consejos para la defensa ────────────────────────────
        tk.Label(scrollable_frame,
                 text="💡 Consejos para la Defensa Oral",
                 font=("Helvetica", 11, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(anchor="w", padx=40, pady=(10, 5))

        consejos_frame = tk.Frame(scrollable_frame, bg="#2e567f", padx=15, pady=12)
        consejos_frame.pack(fill="x", padx=40, pady=(0, 12))
        
        consejos = (
            "✓ Comprenda el algoritmo: Explique paso a paso cómo el programa\n"
            "  valida el RUT, construye los coeficientes y clasifica la cónica.\n\n"
            "✓ Justifique matemáticamente: Cada decisión del código debe\n"
            "  tener una explicación matemática clara.\n\n"
            "✓ Interprete los elementos geométricos: Sepa dónde está el\n"
            "  centro, vértices, focos, etc., en la gráfica mostrada.\n\n"
            "✓ Entienda los límites: Explique qué significa cada límite lateral,\n"
            "  por qué existe o no existe, y el tipo de discontinuidad.\n\n"
            "✓ No memorice solo código: El examen evaluará COMPRENSIÓN,\n"
            "  no memorización. Pueda adaptar y explicar la lógica."
        )
        tk.Label(consejos_frame, text=consejos,
                 font=("Courier", 8),
                 bg="#2e567f", fg=BLANCO,
                 justify="left").pack(anchor="w")

        separador3 = tk.Frame(scrollable_frame, bg=AZUL_MEDIO, height=1, width=500)
        separador3.pack(pady=12)

        # ── Nota importante ────────────────────────────────────
        tk.Label(scrollable_frame,
                 text="⚠️  Nota Importante",
                 font=("Helvetica", 10, "bold"),
                 bg=AZUL_OSCURO, fg=ROJO).pack(anchor="w", padx=40)

        nota_frame = tk.Frame(scrollable_frame, bg=AZUL_OSCURO, padx=15, pady=8)
        nota_frame.pack(fill="x", padx=40, pady=(3, 20))
        
        nota = (
            "• Todos los cálculos son IMPLEMENTADOS MANUALMENTE\n"
            "• NO se usa numpy, math.sqrt(), sympy, ni librerías de álgebra\n"
            "• Las funciones matemáticas (raíz, seno, coseno, etc.) están\n"
            "  codificadas usando algoritmos: Newton-Raphson, Taylor series, etc.\n"
            "• Esto debe ser evidente en su explicación durante la defensa"
        )
        tk.Label(nota_frame, text=nota,
                 font=("Courier", 8),
                 bg=AZUL_OSCURO, fg=AMARILLO,
                 justify="left").pack(anchor="w")


def main():
    app = AppEID()
    app.mainloop()
