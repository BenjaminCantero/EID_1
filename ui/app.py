from ui.componentes import FONT_SMALL
import tkinter as tk
from tkinter import ttk

from core.log_service import setup_logger
from ui.componentes import (
    BG_PRINCIPAL, BG_CARD, BG_HEADER, ACENTO, TEXTO, TEXTO_DIM,
    BORDE_CARD, ENTRY_FG, FONT_TITLE, FONT_SUBTITLE, FONT_BODY,
    configurar_estilos_ttk, crear_header, crear_card
)
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
        self.configure(bg=BG_PRINCIPAL)
        self.resizable(True, True)
        configurar_estilos_ttk()
        # Estado compartido de RUT validado
        self.rut_validado = None
        self.lbl_rut_actual = None  # Se inicializa en _construir_ui
        self._construir_ui()

    def _construir_ui(self):
        # Barra superior decorativa
        barra = tk.Frame(self, bg=BG_HEADER, height=45)
        barra.pack(fill="x")
        barra.pack_propagate(False)

        tk.Label(barra,
                 text="EID N°1 — MAT1186 · Introducción al Cálculo · UCT 2026",
                 font=FONT_SUBTITLE,
                 bg=BG_HEADER, fg=ACENTO).pack(side="left", padx=15, pady=8)

        # RUT actual compartido
        self.lbl_rut_actual = tk.Label(barra,
                 text="RUT: —",
                 font=FONT_SMALL if 'FONT_SMALL' in globals() else ("Segoe UI", 8),
                 bg=BG_HEADER, fg=TEXTO_DIM,
                 relief="flat", padx=10, pady=4)
        self.lbl_rut_actual.pack(side="right", padx=5)

        tk.Label(barra,
                 text="Versión 2026 · Benjamin C. Eduardo D. Ricardo G.",
                 font=FONT_SMALL if 'FONT_SMALL' in globals() else ("Segoe UI", 8),
                 bg=BG_HEADER, fg=TEXTO_DIM).pack(side="right", padx=12)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        self.panel_conica = PanelConica(self.notebook,
                                         cambiar_tab_callback=self._ir_limites,
                                         actualizar_rut_callback=self._actualizar_rut_validado,
                                         logger=self.logger)
        self.notebook.add(self.panel_conica, text="Secciones Cónicas")

        self.panel_limites = PanelLimites(self.notebook,
                                          obtener_rut_callback=self._obtener_rut_validado,
                                          actualizar_rut_callback=self._actualizar_rut_validado,
                                          logger=self.logger)
        self.notebook.add(self.panel_limites, text="Funciones y Límites")

        # Listener para cambios de pestaña - generar automáticamente en Límites
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._agregar_tab_acerca()

    def _actualizar_rut_validado(self, rut_completo):
        """Almacena el RUT validado y lo muestra en la barra superior."""
        self.rut_validado = rut_completo
        if self.lbl_rut_actual:
            self.lbl_rut_actual.config(text=f"RUT: {rut_completo}", fg=ACENTO)
        if self.logger:
            self.logger.info(f"RUT validado actualizado: {rut_completo}")
        
        # Actualizar automáticamente el panel de límites si está visible
        current_tab_index = self.notebook.index(self.notebook.select())
        if current_tab_index == 1:
            # Si estamos en la pestaña de Límites, actualizar directamente
            entrada_actual = self.panel_limites.entry_rut.get().strip()
            if not entrada_actual or entrada_actual != rut_completo:
                self.panel_limites.entry_rut.delete(0, "end")
                self.panel_limites.entry_rut.insert(0, rut_completo)
                if self.logger:
                    self.logger.info(f"RUT pre-llenado en Panel Límites desde actualización: {rut_completo}")
                self.after(150, self.panel_limites._procesar)

    def _obtener_rut_validado(self):
        """Retorna el RUT validado actualmente."""
        return self.rut_validado

    def _generar_limites_automatico(self):
        """Callback para generar automáticamente en Panel Límites cuando hay RUT validado."""
        if self.rut_validado:
            if self.logger:
                self.logger.info(f"Generando automáticamente funciones y límites para RUT: {self.rut_validado}")
            self.panel_limites._procesar()

    def _on_tab_changed(self, event):
        """Se ejecuta cuando se cambia de pestaña."""
        # Obtener índice de la pestaña actual
        current_tab_index = self.notebook.index(self.notebook.select())
        
        # Si es la pestaña de Límites (índice 1) y hay un RUT validado
        if current_tab_index == 1 and self.rut_validado:
            if self.logger:
                self.logger.info(f"Cambio a Panel Límites detectado. RUT validado: {self.rut_validado}")
            
            # Pre-llenar el RUT
            entrada_actual = self.panel_limites.entry_rut.get().strip()
            if not entrada_actual or entrada_actual != self.rut_validado:
                self.panel_limites.entry_rut.delete(0, "end")
                self.panel_limites.entry_rut.insert(0, self.rut_validado)
                if self.logger:
                    self.logger.info(f"RUT pre-llenado en Panel Límites: {self.rut_validado}")
                
                # Generar automáticamente con un pequeño delay
                self.after(150, self.panel_limites._procesar)

    def _ir_limites(self):
        self.notebook.select(1)

    def _agregar_tab_acerca(self):
        frame = tk.Frame(self.notebook, bg=BG_PRINCIPAL)
        self.notebook.add(frame, text="Acerca del Proyecto")

        crear_header(frame, "EID N°1 — CÓNICAS Y LÍMITES", "MAT1186 · Introducción al Cálculo · UCT 2026")

        central_frame = tk.Frame(frame, bg=BG_PRINCIPAL)
        central_frame.pack(fill="both", expand=True, padx=30, pady=25)
        central_frame.columnconfigure(0, weight=1)
        central_frame.columnconfigure(1, weight=1)
        central_frame.rowconfigure(0, weight=1)

        # Card Left: Project Info
        card_left, body_left = crear_card(central_frame, "Propósito de la Aplicación", "Detalles del sistema académico interactivo")
        card_left.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        desc_text = (
            "Esta aplicación interactiva ha sido diseñada para automatizar la generación "
            "y el análisis de secciones cónicas y límites matemáticos de manera personalizada.\n\n"
            "A partir de un RUT chileno válido, el sistema calcula de manera determinista:\n"
            "  ▸ Coeficientes de la ecuación cuadrática general.\n"
            "  ▸ Conversión paso a paso a la ecuación canónica.\n"
            "  ▸ Puntos críticos y tipo de sección cónica (Elipse, Parábola, Hipérbola, Círculo).\n"
            "  ▸ Funciones definidas por tramos y tipo de discontinuidad.\n"
            "  ▸ Cálculo preciso de límites laterales y f(a) para defensa oral.\n\n"
            "El objetivo es facilitar el estudio práctico y visual del cálculo mediante representaciones cartesianas exactas y herramientas de autoevaluación."
        )
        lbl_desc = tk.Label(body_left, text=desc_text, font=FONT_BODY, fg=TEXTO, bg=BG_CARD, justify="left", anchor="nw", wraplength=480)
        lbl_desc.pack(fill="both", expand=True)

        # Card Right: Authors & Specs
        card_right, body_right = crear_card(central_frame, "Ficha del Proyecto", "Información institucional y equipo de desarrollo")
        card_right.grid(row=0, column=1, sticky="nsew")

        info_header = tk.Label(body_right, text="UNIVERSIDAD CATÓLICA DE TEMUCO", font=FONT_SUBTITLE, fg=ACENTO, bg=BG_CARD, anchor="w")
        info_header.pack(fill="x", pady=(0, 8))

        specs_text = (
            "Curso: MAT1186 — Introducción al Cálculo\n"
            "Carrera: Ingeniería Civil en Informática\n"
            "Periodo Académico: Primer Semestre 2026\n"
            "Tecnologías: Python 3.8+ · Tkinter GUI · Service Architecture\n"
        )
        lbl_specs = tk.Label(body_right, text=specs_text, font=FONT_BODY, fg=TEXTO, bg=BG_CARD, justify="left", anchor="w", pady=10)
        lbl_specs.pack(fill="x")

        sep = tk.Frame(body_right, bg=BORDE_CARD, height=1)
        sep.pack(fill="x", pady=15)

        autores_header = tk.Label(body_right, text="EQUIPO DE DESARROLLO (AUTORES)", font=FONT_SUBTITLE, fg=ACENTO, bg=BG_CARD, anchor="w")
        autores_header.pack(fill="x", pady=(0, 8))

        autores_text = (
            "Benjamin Cantero\n"
            "Eduardo D.\n"
            "Ricardo G."
        )
        lbl_autores = tk.Label(body_right, text=autores_text, font=FONT_BODY, fg=TEXTO, bg=BG_CARD, justify="left", anchor="w")
        lbl_autores.pack(fill="x")


def main():
    app = AppEID()
    app.mainloop()

