import tkinter as tk
from tkinter import ttk

from core.log_service import setup_logger
from ui.componentes import AZUL_OSCURO, AZUL_MEDIO, AMARILLO, BLANCO, GRIS_TEXTO, configurar_estilos_ttk
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

        tk.Label(frame,
                 text="Evaluación Integrada de Desempeño N°1",
                 font=("Helvetica", 18, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(pady=(40, 5))

        tk.Label(frame,
                 text="Análisis y Modelamiento de Secciones Cónicas\ny Funciones por Tramos a partir del RUT",
                 font=("Helvetica", 13),
                 bg=AZUL_OSCURO, fg=BLANCO,
                 justify="center").pack(pady=5)

        separador = tk.Frame(frame, bg=AMARILLO, height=2, width=400)
        separador.pack(pady=15)

        info = [
            ("Curso", "MAT1186 — Introducción al Cálculo"),
            ("Institución", "Universidad Católica de Temuco"),
            ("Carrera", "Ingeniería Civil en Informática"),
            ("Año", "2026"),
        ]
        for etiqueta, valor in info:
            row = tk.Frame(frame, bg=AZUL_OSCURO)
            row.pack()
            tk.Label(row, text=f"{etiqueta}:",
                     font=("Helvetica", 11, "bold"),
                     bg=AZUL_OSCURO, fg=AMARILLO, width=14, anchor="e").pack(side="left")
            tk.Label(row, text=f"  {valor}",
                     font=("Helvetica", 11),
                     bg=AZUL_OSCURO, fg=BLANCO).pack(side="left")

        separador2 = tk.Frame(frame, bg=AZUL_MEDIO, height=2, width=400)
        separador2.pack(pady=20)

        tk.Label(frame,
                 text="Instrucciones de uso:",
                 font=("Helvetica", 11, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack()

        instrucciones = (
            "1.  Ingrese un RUT chileno válido en cualquiera de las dos pestañas.\n"
            "2.  En 'Secciones Cónicas': el sistema valida el RUT, construye la ecuación\n"
            "     general, clasifica la cónica, muestra la forma canónica y la grafica.\n"
            "3.  En 'Funciones y Límites': el sistema genera una función por tramos,\n"
            "     calcula los límites laterales, clasifica la discontinuidad y muestra la tabla.\n"
            "4.  Los campos en blanco están disponibles para completar durante la defensa oral.\n"
            "5.  Todos los cálculos son implementados manualmente (sin numpy/math/sympy)."
        )
        tk.Label(frame, text=instrucciones,
                 font=("Courier", 10),
                 bg=AZUL_OSCURO, fg=GRIS_TEXTO,
                 justify="left").pack(padx=40, pady=5)


def main():
    app = AppEID()
    app.mainloop()
