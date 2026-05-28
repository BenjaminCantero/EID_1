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
        self.geometry("1200x800")
        self.minsize(800, 600)
        self.configure(bg=AZUL_OSCURO)
        self.resizable(True, True)
        configurar_estilos_ttk()
        self._construir_ui()

    def _construir_ui(self):
        barra = tk.Frame(self, bg=AZUL_MEDIO, height=45)
        barra.pack(fill="x")
        barra.pack_propagate(False)

        tk.Label(barra,
                 text="EID N°1 — MAT1186 · Introducción al Cálculo · UCT 2026",
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
        self.notebook.add(self.panel_conica, text="Secciones Cónicas")

        self.panel_limites = PanelLimites(self.notebook, logger=self.logger)
        self.notebook.add(self.panel_limites, text="Funciones y Límites")

        self._agregar_tab_acerca()

    def _ir_limites(self):
        self.notebook.select(1)

    def _agregar_tab_acerca(self):
        frame = tk.Frame(self.notebook, bg=AZUL_OSCURO)
        self.notebook.add(frame, text="Acerca del Proyecto")

        # Frame central para contenido
        central_frame = tk.Frame(frame, bg=AZUL_OSCURO)
        central_frame.pack(fill="both", expand=True, padx=50, pady=40)

        # ── Título principal ────────────────────────────────────
        tk.Label(central_frame,
                 text="EID N°1 — Cónicas y Límites",
                 font=("Helvetica", 20, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(pady=(0, 15))

        tk.Label(central_frame,
                 text="Análisis de Secciones Cónicas y Funciones por Tramos",
                 font=("Helvetica", 12),
                 bg=AZUL_OSCURO, fg=BLANCO).pack(pady=(0, 20))

        separador = tk.Frame(central_frame, bg=AMARILLO, height=2)
        separador.pack(fill="x", pady=(0, 20))

        # ── Información esencial ────────────────────────────────
        info_frame = tk.Frame(central_frame, bg=AZUL_MEDIO, padx=20, pady=15)
        info_frame.pack(fill="x", pady=(0, 20))

        info_texto = (
            "MAT1186 — Introducción al Cálculo\n"
            "Universidad Católica de Temuco\n"
            "Ing. Civil en Informática — 2026\n"
            "Python 3.8+ • Tkinter • Implementación manual"
        )
        tk.Label(info_frame, text=info_texto,
                 font=("Helvetica", 11),
                 bg=AZUL_MEDIO, fg=BLANCO,
                 justify="center").pack()

        separador2 = tk.Frame(central_frame, bg=AMARILLO, height=2)
        separador2.pack(fill="x", pady=(0, 20))

        # ── Propósito ──────────────────────────────────────────
        tk.Label(central_frame,
                 text="Propósito de la Aplicación",
                 font=("Helvetica", 12, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(pady=(0, 10))

        proposito = (
            "Esta herramienta permite analizar matemáticamente secciones cónicas\n"
            "y funciones por tramos generadas a partir de un RUT chileno válido.\n\n"
            "Ingrese un RUT en cualquiera de las pestañas principales para comenzar."
        )
        tk.Label(central_frame, text=proposito,
                 font=("Helvetica", 10),
                 bg=AZUL_OSCURO, fg=GRIS_TEXTO,
                 justify="center").pack(pady=(0, 20))

        separador3 = tk.Frame(central_frame, bg=AMARILLO, height=2)
        separador3.pack(fill="x", pady=(0, 20))

        # ── Autores ────────────────────────────────────────────
        tk.Label(central_frame,
                 text="Autores",
                 font=("Helvetica", 11, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(pady=(0, 8))

        tk.Label(central_frame,
                 text="Benjamin C. • Eduardo D. • Ricardo G.",
                 font=("Helvetica", 10),
                 bg=AZUL_OSCURO, fg=BLANCO).pack()


def main():
    app = AppEID()
    app.mainloop()
