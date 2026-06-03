import tkinter as tk
from tkinter import ttk

# Paleta de Colores Profesional y Refinada (Dark Theme Premium)
BG_PRINCIPAL = "#0f1923"
BG_CARD = "#1a2744"
BG_HEADER = "#141e30"
BG_INPUT = "#1a2744"
BG_CANVAS = "#0a1628"
ACENTO = "#f0c040"
ACENTO_HOVER = "#ffda47"
TEXTO = "#c8d6e5"
TEXTO_DIM = "#6b7f99"
VERDE = "#2ecc71"
ROJO = "#e74c3c"
NARANJA = "#ff9800"
BORDE_CARD = "#2a3f5f"
ENTRY_BG = "#1c2e45"
ENTRY_FG = "#e0e6ed"

# Tipografía (Nativa de Windows, Limpia y Profesional)
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_SUBTITLE = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 9)
FONT_CODE = ("Consolas", 9)
FONT_SMALL = ("Segoe UI", 8)

def configurar_estilos_ttk():
    style = ttk.Style()
    style.theme_use("default")

    # Notebook (Pestañas)
    style.configure("TNotebook",
                    background=BG_PRINCIPAL,
                    borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=BG_HEADER,
                    foreground=TEXTO,
                    font=("Segoe UI", 10, "bold"),
                    padding=[18, 8])
    style.map("TNotebook.Tab",
              background=[("selected", BG_PRINCIPAL)],
              foreground=[("selected", ACENTO)])

    # Treeview (Tablas)
    style.configure("Treeview",
                    background=BG_CANVAS,
                    foreground=TEXTO,
                    fieldbackground=BG_CANVAS,
                    font=("Consolas", 9),
                    rowheight=22)
    style.map("Treeview",
              background=[("selected", "#243b55")],
              foreground=[("selected", "#ffffff")])
    style.configure("Treeview.Heading",
                    background=BG_HEADER,
                    foreground=ACENTO,
                    font=("Segoe UI", 9, "bold"))

def crear_header(parent, title, subtitle=None):
    """Crea un header elegante y consistente para los paneles."""
    header = tk.Frame(parent, bg=BG_HEADER, height=52)
    header.pack(fill="x", side="top")
    header.pack_propagate(False)
    
    text_container = tk.Frame(header, bg=BG_HEADER)
    text_container.pack(side="left", padx=15, fill="both", expand=True)
    
    lbl_title = tk.Label(text_container, text=title, font=FONT_TITLE, fg=ACENTO, bg=BG_HEADER, anchor="w")
    lbl_title.pack(fill="x", pady=(6, 0))
    
    if subtitle:
        lbl_sub = tk.Label(text_container, text=subtitle, font=FONT_SMALL, fg=TEXTO_DIM, bg=BG_HEADER, anchor="w")
        lbl_sub.pack(fill="x")
    
    # Separador sutil inferior
    sep = tk.Frame(header, bg=BORDE_CARD, height=1)
    sep.pack(fill="x", side="bottom")
    
    return header

def crear_barra_rut(parent, placeholder, button_text, command):
    """Crea la barra de entrada RUT unificada."""
    bar = tk.Frame(parent, bg=BG_INPUT, height=52)
    bar.pack(fill="x", side="top", pady=(0, 2))
    bar.pack_propagate(False)
    
    inner = tk.Frame(bar, bg=BG_INPUT)
    inner.pack(side="left", padx=15, fill="y")
    
    lbl = tk.Label(inner, text="RUT:", font=FONT_SUBTITLE, fg=TEXTO, bg=BG_INPUT)
    lbl.pack(side="left", padx=(0, 10))
    
    entry = tk.Entry(inner, font=FONT_BODY, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG, bd=0, highlightthickness=1, highlightbackground=BORDE_CARD, width=20)
    entry.pack(side="left", padx=(0, 10), ipady=3)
    entry.insert(0, placeholder)
    
    btn = tk.Button(inner, text=button_text, command=command, font=FONT_SUBTITLE, bg=ACENTO, fg=BG_PRINCIPAL, activebackground=ACENTO_HOVER, activeforeground=BG_PRINCIPAL, bd=0, padx=15, cursor="hand2")
    btn.pack(side="left")
    
    def on_enter(e):
        btn.config(bg=ACENTO_HOVER)
    def on_leave(e):
        btn.config(bg=ACENTO)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    # Separador inferior
    sep = tk.Frame(bar, bg=BORDE_CARD, height=1)
    sep.pack(fill="x", side="bottom")
    
    return bar, entry

def crear_card(parent, title=None, subtitle=None):
    """Crea un contenedor en forma de 'Card' con borde y padding."""
    card = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDE_CARD, highlightthickness=1)
    
    if title:
        header_frame = tk.Frame(card, bg=BG_CARD)
        header_frame.pack(fill="x", padx=12, pady=(10, 5))
        lbl_title = tk.Label(header_frame, text=title, font=FONT_SUBTITLE, fg=ACENTO, bg=BG_CARD, anchor="w")
        lbl_title.pack(fill="x")
        if subtitle:
            lbl_sub = tk.Label(header_frame, text=subtitle, font=FONT_SMALL, fg=TEXTO_DIM, bg=BG_CARD, anchor="w")
            lbl_sub.pack(fill="x")
            
    body = tk.Frame(card, bg=BG_CARD)
    body.pack(fill="both", expand=True, padx=12, pady=(2, 10))
    
    return card, body

def crear_status_bar(parent, text):
    """Crea la barra de estado inferior."""
    status = tk.Frame(parent, bg=BG_HEADER, height=30)
    status.pack(fill="x", side="bottom")
    status.pack_propagate(False)
    
    # Separador sutil superior
    sep = tk.Frame(status, bg=BORDE_CARD, height=1)
    sep.pack(fill="x", side="top")
    
    lbl = tk.Label(status, text=text, font=FONT_SMALL, fg=TEXTO_DIM, bg=BG_HEADER, anchor="w")
    lbl.pack(side="left", padx=15, fill="both", expand=True)
    return status, lbl

