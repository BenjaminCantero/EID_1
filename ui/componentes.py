import tkinter as tk
from tkinter import ttk

AZUL_OSCURO = "#1a2a4a"
AZUL_MEDIO = "#2d4a7a"
AZUL_CLARO = "#4a7abf"
BLANCO = "#f0f4ff"
AMARILLO = "#f5c842"
GRIS_TEXTO = "#e8eaf6"
VERDE = "#4caf50"
ROJO = "#e53935"
NARANJA = "#ff9800"


def configurar_estilos_ttk():
    style = ttk.Style()
    style.theme_use("default")

    style.configure("TNotebook",
                    background=AZUL_OSCURO,
                    borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=AZUL_MEDIO,
                    foreground=GRIS_TEXTO,
                    font=("Helvetica", 10, "bold"),
                    padding=[15, 6])
    style.map("TNotebook.Tab",
              background=[("selected", AZUL_OSCURO)],
              foreground=[("selected", AMARILLO)])
    style.configure("Treeview",
                    background="#0d1b2e",
                    foreground=GRIS_TEXTO,
                    fieldbackground="#0d1b2e",
                    font=("Courier", 9))
    style.configure("Treeview.Heading",
                    background=AZUL_MEDIO,
                    foreground=AMARILLO,
                    font=("Helvetica", 9, "bold"))
