
"""Panel de límites y funciones por tramos."""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from core.exceptions import LimiteInvalidoError, RUTInvalidoError
from core.graficas import puntos_grafica_limite
from core.services import analizar_limites
from ui.componentes import (AZUL_OSCURO, AZUL_MEDIO, AZUL_CLARO,
                            BLANCO, AMARILLO, GRIS_TEXTO, VERDE,
                            ROJO, NARANJA)


class PanelLimites(tk.Frame):
    def __init__(self, parent, logger=None):
        super().__init__(parent, bg=AZUL_OSCURO)
        self.logger = logger
        self.tramos = None
        self.analisis = None
        self.a = 0
        self._ultimo_tramos = None
        self._ultimo_analisis = None
        self._zoom_factor = 1.0
        self._construir_ui()

    def _construir_ui(self):
        # ── Encabezado principal ────────────────────────────
        header = tk.Frame(self, bg=AZUL_MEDIO, height=60)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        tk.Label(header, text="ANÁLISIS DE FUNCIONES Y LÍMITES",
                 font=("Helvetica", 14, "bold"),
                 bg=AZUL_MEDIO, fg=AMARILLO).pack(anchor="w", padx=20, pady=(10, 5))
        tk.Label(header, text="Ingrese un RUT para analizar funciones por tramos y comportamiento de límites",
                 font=("Helvetica", 9),
                 bg=AZUL_MEDIO, fg=GRIS_TEXTO).pack(anchor="w", padx=20, pady=(0, 10))

        # ── Sección de entrada (RUT) ────────────────────────
        frame_rut = tk.Frame(self, bg=AZUL_CLARO, padx=20, pady=12)
        frame_rut.pack(fill="x", padx=0, pady=0)
        
        # Configurar pesos de columnas para responsividad
        frame_rut.columnconfigure(1, weight=1)

        tk.Label(frame_rut, text="Paso 1: Ingrese RUT chileno",
                 font=("Helvetica", 10, "bold"),
                 bg=AZUL_CLARO, fg=AMARILLO).grid(row=0, column=0, sticky="w", columnspan=3, pady=(0, 8))

        tk.Label(frame_rut, text="RUT:",
                 font=("Helvetica", 10, "bold"),
                 bg=AZUL_CLARO, fg=BLANCO).grid(row=1, column=0, sticky="w", padx=(0, 10))

        self.entry_rut = tk.Entry(frame_rut, font=("Courier", 12),
                                   bg=BLANCO, fg=AZUL_OSCURO,
                                   relief="flat", bd=3)
        self.entry_rut.grid(row=1, column=1, padx=10, sticky="ew")
        self.entry_rut.insert(0, "12.345.678-9")
        self.entry_rut.bind("<Return>", lambda e: self._procesar())

        btn_frame = tk.Frame(frame_rut, bg=AZUL_CLARO)
        btn_frame.grid(row=1, column=2, padx=5, sticky="w")

        tk.Button(btn_frame, text="Generar función",
                  command=self._procesar,
                  font=("Helvetica", 10, "bold"),
                  bg=AMARILLO, fg=AZUL_OSCURO,
                  relief="flat", padx=15, pady=6,
                  cursor="hand2", activebackground="#ffed4e").pack(side="left")
        
        tk.Label(frame_rut, text="Ejemplos: 8.769.123-K  •  12.456.789-5  •  15.234.567-8",
                 font=("Helvetica", 7), bg=AZUL_CLARO, fg=GRIS_TEXTO).grid(row=2, column=1, sticky="w", pady=(4, 0))

        # ── Cuerpo principal ──────────────────────────────────
        body = tk.Frame(self, bg=AZUL_OSCURO)
        body.pack(fill="both", expand=True, padx=20, pady=5)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=AZUL_OSCURO)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Marco derecho con scroll
        right_frame = tk.Frame(body, bg=AZUL_OSCURO)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # Canvas scrollable para el lado derecho
        right_canvas = tk.Canvas(right_frame, bg=AZUL_OSCURO, highlightthickness=0)
        right_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=right_canvas.yview)
        right = tk.Frame(right_canvas, bg=AZUL_OSCURO)

        right.bind(
            "<Configure>",
            lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"))
        )

        right_canvas_window = right_canvas.create_window((0, 0), window=right, anchor="nw")
        right_canvas.configure(yscrollcommand=right_scrollbar.set)

        # Hacer que el frame interno se expanda con el canvas
        def _on_canvas_configure(event):
            right_canvas.itemconfig(right_canvas_window, width=event.width)
        right_canvas.bind("<Configure>", _on_canvas_configure)

        right_canvas.grid(row=0, column=0, sticky="nsew")
        right_scrollbar.grid(row=0, column=1, sticky="ns")

        # Permitir scroll con la rueda del ratón
        def _on_mousewheel(event):
            right_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        right_canvas.bind("<MouseWheel>", _on_mousewheel)

        # ── Texto de análisis matemático ─────────────────────
        analysis_label_frame = tk.Frame(left, bg=AZUL_MEDIO, padx=10, pady=8)
        analysis_label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(analysis_label_frame, text="Paso 2: Análisis Matemático",
                 font=("Helvetica", 10, "bold"),
                 bg=AZUL_MEDIO, fg=AMARILLO).pack(anchor="w")
        tk.Label(analysis_label_frame, text="Validación, tipo de función y cálculo de límites laterales",
                 font=("Helvetica", 8),
                 bg=AZUL_MEDIO, fg=GRIS_TEXTO).pack(anchor="w", pady=(2, 0))

        self.txt_analisis = scrolledtext.ScrolledText(
            left,
            font=("Courier", 9),
            bg="#0d1b2e", fg=GRIS_TEXTO,
            insertbackground=BLANCO,
            relief="flat", bd=2,
            state="disabled")
        self.txt_analisis.pack(fill="both", expand=True)

        # ── Tabla de valores ─────────────────────────────────
        table_label_frame = tk.Frame(left, bg=AZUL_MEDIO, padx=10, pady=8)
        table_label_frame.pack(fill="x", pady=(8, 4))
        
        tk.Label(table_label_frame, text="Tabla de Valores",
                 font=("Helvetica", 9, "bold"),
                 bg=AZUL_MEDIO, fg=AMARILLO).pack(anchor="w")
        tk.Label(table_label_frame, text="Valores cercanos al punto crítico",
                 font=("Helvetica", 7),
                 bg=AZUL_MEDIO, fg=GRIS_TEXTO).pack(anchor="w", pady=(1, 0))

        frame_tabla = tk.Frame(left, bg=AZUL_MEDIO)
        frame_tabla.pack(fill="x", pady=(0, 8))

        self.tabla_tree = ttk.Treeview(frame_tabla,
                                        columns=("x", "f(x)", "lado"),
                                        show="headings", height=6)
        self.tabla_tree.heading("x", text="x")
        self.tabla_tree.heading("f(x)", text="f(x)")
        self.tabla_tree.heading("lado", text="Lado")
        self.tabla_tree.column("x", width=100, anchor="center")
        self.tabla_tree.column("f(x)", width=120, anchor="center")
        self.tabla_tree.column("lado", width=70, anchor="center")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#0d1b2e",
                        foreground=GRIS_TEXTO,
                        fieldbackground="#0d1b2e",
                        font=("Courier", 9))
        style.configure("Treeview.Heading",
                        background=AZUL_MEDIO,
                        foreground=AMARILLO,
                        font=("Helvetica", 9, "bold"))

        self.tabla_tree.pack(fill="x", padx=4, pady=4)

        # ── Gráfica canvas ───────────────────────────────────
        graph_label_frame = tk.Frame(right, bg=AZUL_MEDIO, padx=10, pady=8)
        graph_label_frame.pack(fill="x", pady=(0, 8))
        
        tk.Label(graph_label_frame, text="Paso 3: Visualización Gráfica",
                 font=("Helvetica", 10, "bold"),
                 bg=AZUL_MEDIO, fg=AMARILLO).pack(anchor="w")
        tk.Label(graph_label_frame, text="Comportamiento de la función y su discontinuidad",
                 font=("Helvetica", 8),
                 bg=AZUL_MEDIO, fg=GRIS_TEXTO).pack(anchor="w", pady=(2, 0))

        graph_canvas_frame = tk.Frame(right, bg=AZUL_OSCURO)
        graph_canvas_frame.pack(fill="both", expand=True)
        graph_canvas_frame.columnconfigure(0, weight=1)
        graph_canvas_frame.rowconfigure(0, weight=1)

        self.canvas_lim = tk.Canvas(graph_canvas_frame,
                                     bg="#051020", relief="flat", bd=2,
                                     highlightthickness=1,
                                     highlightbackground=AZUL_CLARO,
                                     xscrollincrement=10,
                                     yscrollincrement=10)
        vbar = ttk.Scrollbar(graph_canvas_frame, orient="vertical", command=self.canvas_lim.yview)
        hbar = ttk.Scrollbar(graph_canvas_frame, orient="horizontal", command=self.canvas_lim.xview)
        self.canvas_lim.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        self.canvas_lim.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")

        self.canvas_lim.bind("<Configure>", self._on_canvas_resize)
        self.canvas_lim.bind("<MouseWheel>", self._on_graph_mousewheel)
        self.canvas_lim.bind("<Shift-MouseWheel>", self._on_graph_shift_mousewheel)
        self.canvas_lim.bind("<ButtonPress-1>", lambda e: self.canvas_lim.scan_mark(e.x, e.y))
        self.canvas_lim.bind("<B1-Motion>", lambda e: self.canvas_lim.scan_dragto(e.x, e.y, gain=1))

        # Canvas info label - se actualiza con el tipo de discontinuidad
        self.lbl_canvas_lim_info = tk.Label(right, text="Esperando análisis...",
                                             font=("Courier", 8),
                                             bg=AZUL_OSCURO, fg=GRIS_TEXTO)
        self.lbl_canvas_lim_info.pack()

        # ── Función generada ──────────────────────────────────
        self.lbl_funcion = tk.Label(right, text="",
                                     font=("Courier", 9, "bold"),
                                     bg=AZUL_OSCURO, fg=GRIS_TEXTO,
                                     wraplength=300, justify="left")
        self.lbl_funcion.pack(pady=(3, 0))

        # ── Campos para defensa oral ──────────────────────────
        tk.Label(right, text="Completar durante la defensa oral:",
                 font=("Helvetica", 9, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(anchor="w", pady=(8, 2))
        
        tk.Label(right, text="Demuestre su comprensión del concepto de límite",
                 font=("Helvetica", 7),
                 bg=AZUL_OSCURO, fg=GRIS_TEXTO).pack(anchor="w", pady=(0, 3))

        frame_defensa = tk.Frame(right, bg=AZUL_MEDIO, padx=8, pady=8)
        frame_defensa.pack(fill="x")

        campos = [
            ("lim_izq", "Límite por izquierda:", "lim x→a⁻ f(x) = "),
            ("lim_der", "Límite por derecha:", "lim x→a⁺ f(x) = "),
            ("lim_existe", "¿Existe el límite?:", "sí / no"),
            ("fa", "f(a) =", "valor o 'no def.'"),
            ("continua", "¿Es continua?:", "sí / no"),
            ("tipo_disc", "Tipo de discontinuidad:", "removible / salto / infinita"),
            ("justificacion", "Justificación matemática:", "descripción breve"),
        ]
        self.entries_defensa = {}
        for key, etiqueta_full, placeholder in campos:
            fila = tk.Frame(frame_defensa, bg=AZUL_MEDIO)
            fila.pack(fill="x", pady=1)
            tk.Label(fila, text=etiqueta_full, width=22, anchor="w",
                     font=("Helvetica", 7, "bold"),
                     bg=AZUL_MEDIO, fg=GRIS_TEXTO).pack(side="left")
            e = tk.Entry(fila, font=("Courier", 8), width=18,
                          bg=BLANCO, fg="#444444", relief="flat", bd=2)
            e.pack(side="left", padx=2)
            e.insert(0, placeholder)
            e._placeholder_text = placeholder
            e.bind("<FocusIn>", lambda event, entry=e: self._clear_placeholder(entry))
            e.bind("<FocusOut>", lambda event, entry=e: self._restore_placeholder(entry))
            self.entries_defensa[key] = e

        # Botones defensa
        btn_row = tk.Frame(right, bg=AZUL_OSCURO)
        btn_row.pack(pady=6)

        tk.Button(btn_row, text="Verificar",
                  command=self._verificar_defensa,
                  font=("Helvetica", 9, "bold"),
                  bg=VERDE, fg="white", relief="flat",
                  padx=8, pady=3, cursor="hand2",
                  activebackground="#2e8b57").pack(side="left", padx=4)

        tk.Button(btn_row, text="Limpiar campos",
                  command=self._limpiar_defensa,
                  font=("Helvetica", 9),
                  bg=AZUL_MEDIO, fg=GRIS_TEXTO, relief="flat",
                  padx=8, pady=3, cursor="hand2",
                  activebackground="#4a7aaa").pack(side="left", padx=4)

        # Estado
        self.lbl_estado = tk.Label(self, text="Ingrese un RUT válido y presione 'Generar función'",
                                    font=("Helvetica", 9, "bold"),
                                    bg=AZUL_OSCURO, fg=GRIS_TEXTO)
        self.lbl_estado.pack(pady=4)

    def _procesar(self):
        rut_str = self.entry_rut.get().strip()
        if self.logger:
            self.logger.info(f"PanelLímites: Inicia generación de función para RUT '{rut_str}'")

        if not rut_str:
            messagebox.showerror("Error", "Debes ingresar un RUT válido.")
            if self.logger:
                self.logger.warning("PanelLímites: RUT vacío ingresado")
            return

        try:
            resultado = analizar_limites(rut_str)
        except RUTInvalidoError:
            messagebox.showerror("Error", "RUT inválido. Verifique e intente de nuevo.")
            if self.logger:
                self.logger.warning(f"PanelLímites: RUT inválido '{rut_str}'")
            return
        except LimiteInvalidoError as e:
            messagebox.showerror("Error", f"No se pudo generar la función: {e}")
            if self.logger:
                self.logger.error(f"PanelLímites: Error de límites para RUT '{rut_str}' — {e}")
            return

        self.tramos = resultado.tramos_info
        self.analisis = resultado

        texto = "╔════════════════════════════════════════════════════════╗\n"
        texto += "║               FUNCIÓN GENERADA POR TRAMOS            ║\n"
        texto += "╚════════════════════════════════════════════════════════╝\n\n"
        texto += f"{resultado.descripcion_funcion}\n\n"
        texto += f"➤ Punto de análisis: a = {resultado.a}\n\n"
        texto += "Criterio de selección del caso:\n"
        texto += f"  {resultado.razon_caso}\n\n"
        
        texto += "╔════════════════════════════════════════════════════════╗\n"
        texto += "║              CÁLCULO DE LÍMITES LATERALES             ║\n"
        texto += "╚════════════════════════════════════════════════════════╝\n\n"
        texto += "\n".join(resultado.pasos_limites) + "\n"

        self._mostrar_texto(texto)
        
        # Actualizar información del canvas
        self.lbl_canvas_lim_info.config(text=f"✓ {resultado.tipo_discontinuidad} (Caso: {resultado.caso_tipo})", fg=AMARILLO)
        self.lbl_funcion.config(text=f"f(x) con a={resultado.a}  │  Tipo: {resultado.caso_tipo}  │  Discontinuidad: {resultado.tipo_discontinuidad}")
        self.lbl_estado.config(text=f"✓ Función generada — {resultado.tipo_discontinuidad} — Complete los campos de defensa", fg=VERDE)
        if self.logger:
            self.logger.info(f"PanelLímites: Función generada para RUT '{rut_str}' — caso '{resultado.caso_tipo}', tipo '{resultado.tipo_discontinuidad}'")

        for row in self.tabla_tree.get_children():
            self.tabla_tree.delete(row)
        for fila in resultado.tabla_valores:
            x_str = f"{fila['x']:.4f}" if fila['x'] is not None else "—"
            y_str = "No def." if fila['f_x'] is None else f"{fila['f_x']:.4f}"
            lado = fila['lado']
            tag = "izq" if lado == "izq" else "der"
            self.tabla_tree.insert("", "end",
                                    values=(x_str, y_str, "← izq" if lado == "izq" else "der →"),
                                    tags=(tag,))
        self.tabla_tree.tag_configure("izq", background="#1a3a6a", foreground="#90caf9")
        self.tabla_tree.tag_configure("der", background="#1a4a2a", foreground="#a5d6a7")

        self._graficar(self.tramos, resultado)
        self._limpiar_defensa()

    def _graficar(self, tramos, analisis):
        self._ultimo_tramos = tramos
        self._ultimo_analisis = analisis
        self.canvas_lim.delete("all")
        visible_w, visible_h = self.canvas_lim.winfo_width(), self.canvas_lim.winfo_height()
        if visible_w <= 1 or visible_h <= 1:
            visible_w, visible_h = 400, 350

        base_w = max(visible_w, 1600)
        base_h = max(visible_h, 900)
        draw_w = int(base_w * self._zoom_factor)
        draw_h = int(base_h * self._zoom_factor)
        cx, cy = draw_w // 2, draw_h // 2

        # Escala dinámica basada en el tamaño del canvas virtual
        ancho_disponible = draw_w * 0.8
        escala = ancho_disponible / 20  # 20 unidades totales (-10 a +10)

        # Fondo más oscuro para contraste
        self.canvas_lim.create_rectangle(0, 0, draw_w, draw_h, fill="#051020", outline="")

        # Grid sutil para mejor orientación
        for i in range(-10, 11):
            if i == 0:
                continue
            px = cx + i * escala
            py = cy + i * escala
            # Grid de fondo muy sutil
            self.canvas_lim.create_line(px, 10, px, draw_h - 10, fill="#1a2f4a", width=0.5)
            self.canvas_lim.create_line(10, py, draw_w - 10, py, fill="#1a2f4a", width=0.5)

        # Ejes con mejor visibilidad
        self.canvas_lim.create_line(10, cy, draw_w - 10, cy, fill="#4a7aaa", width=1.5)
        self.canvas_lim.create_line(cx, 10, cx, draw_h - 10, fill="#4a7aaa", width=1.5)

        # Marcas en ejes con mejor contraste
        for i in range(-10, 11):
            if i == 0:
                continue
            px = cx + i * escala
            py = cy + i * escala
            # Marcas más largas
            self.canvas_lim.create_line(px, cy - 5, px, cy + 5, fill="#6a9aaa", width=1)
            self.canvas_lim.create_line(cx - 5, py, cx + 5, py, fill="#6a9aaa", width=1)
            if i % 2 == 0:
                self.canvas_lim.create_text(px, cy + 14, text=str(i),
                                            font=("Courier", 7, "bold"), fill="#8aaaaa")
                self.canvas_lim.create_text(cx - 14, py, text=str(-i),
                                            font=("Courier", 7, "bold"), fill="#8aaaaa")

        self.canvas_lim.create_text(draw_w - 12, cy - 15, text="x",
                                     font=("Courier", 10, "bold"), fill="#6a9aaa")
        self.canvas_lim.create_text(cx + 12, 12, text="y",
                                     font=("Courier", 10, "bold"), fill="#6a9aaa")

        # Asíntota vertical si es infinita (más visible)
        caso = tramos["tipo"]
        a = tramos["a"]
        if caso == "infinita":
            ax = cx + a * escala
            # Asíntota punteada roja más gruesa
            self.canvas_lim.create_line(ax, 5, ax, draw_h - 5,
                                         fill="#ff6b6b", width=2, dash=(6, 4))
            self.canvas_lim.create_text(ax + 8, 18,
                                         text=f"x={a}", font=("Courier", 8, "bold"), fill="#ff6b6b")

        # Obtener segmentos
        segmentos, pantalla_fn = puntos_grafica_limite(tramos, draw_w, draw_h, rango_x=8)
        
        # Dibujar función con grosor mejorado y colores vibrantes
        for seg in segmentos:
            x1, y1, x2, y2 = seg
            # Validar que los puntos están dentro del canvas
            if (10 <= x1 <= draw_w - 10 and 10 <= y1 <= draw_h - 10 and
                10 <= x2 <= draw_w - 10 and 10 <= y2 <= draw_h - 10):
                self.canvas_lim.create_line(x1, y1, x2, y2, 
                                            fill="#00ffaa", width=3, 
                                            capstyle="round", joinstyle="round")

        # Marcar visualmente la posición x = a en el eje (etiqueta)
        self.canvas_lim.create_text(cx + a * escala, draw_h - 20,
                                     text=f"a={a}", font=("Courier", 9, "bold"), fill=NARANJA)

        # Discontinuidad removible: dibujar hueco en (a, límite)
        if caso == "removible":
            lim_val = getattr(analisis, "lim_valor", None)
            f_en_a = getattr(analisis, "f_en_a", None)
            if isinstance(lim_val, (int, float)):
                px_h, py_h = pantalla_fn(a, lim_val)
                # Hueco: círculo grande vacío (punto no incluido)
                self.canvas_lim.create_oval(px_h - 7, py_h - 7, px_h + 7, py_h + 7,
                                             outline="#ffd27f", fill="", width=3)
                # Etiqueta del límite
                self.canvas_lim.create_text(px_h + 18, py_h - 10,
                                             text=f"lim={lim_val}",
                                             font=("Courier", 7, "bold"), fill="#ffd27f")
            # Si f(a) estuviera definida (no es el caso típico), mostrar punto relleno
            if f_en_a is not None and isinstance(f_en_a, (int, float)):
                px_fa, py_fa = pantalla_fn(a, f_en_a)
                self.canvas_lim.create_oval(px_fa - 5, py_fa - 5, px_fa + 5, py_fa + 5,
                                             fill="#66ff99", outline="white", width=2)

        # Puntos de discontinuidad de salto (mucho más visibles)
        if caso == "salto":
            lim_izq = getattr(analisis, "lim_real_izq", None)
            lim_der = getattr(analisis, "lim_real_der", None)
            
            # Punto por la izquierda (hueco)
            if isinstance(lim_izq, (int, float)):
                px_i, py_i = pantalla_fn(a, lim_izq)
                # Círculo hueco más grande (punto no incluido)
                self.canvas_lim.create_oval(px_i - 6, py_i - 6, px_i + 6, py_i + 6,
                                             outline="#ff9999", fill="", width=3)
                self.canvas_lim.create_text(px_i - 15, py_i - 10,
                                             text=f"L⁻={lim_izq}", 
                                             font=("Courier", 7, "bold"), fill="#ff9999")
            
            # Punto por la derecha (relleno)
            if isinstance(lim_der, (int, float)):
                px_d, py_d = pantalla_fn(a, lim_der)
                # Círculo relleno más grande (punto incluido)
                self.canvas_lim.create_oval(px_d - 6, py_d - 6, px_d + 6, py_d + 6,
                                             fill="#66ff99", outline="white", width=2)
                self.canvas_lim.create_text(px_d + 12, py_d - 10,
                                             text=f"L⁺={lim_der}", 
                                             font=("Courier", 7, "bold"), fill="#66ff99")

        # Leyenda mejorada
        self.canvas_lim.create_text(draw_w // 2, draw_h - 12,
                                     text=f"Discontinuidad: {getattr(analisis, 'tipo_discontinuidad', '')}",
                                     font=("Helvetica", 10, "bold"), fill="#00ffaa")
        self.canvas_lim.configure(scrollregion=(0, 0, draw_w, draw_h))

        if draw_w > visible_w:
            self.canvas_lim.xview_moveto((draw_w - visible_w) / 2 / draw_w)
        if draw_h > visible_h:
            self.canvas_lim.yview_moveto((draw_h - visible_h) / 2 / draw_h)

    def _on_canvas_resize(self, event):
        if self._ultimo_tramos and self._ultimo_analisis:
            self._graficar(self._ultimo_tramos, self._ultimo_analisis)

    def _on_graph_mousewheel(self, event):
        self._zoom_graph(event)
        return "break"

    def _on_graph_shift_mousewheel(self, event):
        self.canvas_lim.xview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    def _zoom_graph(self, event):
        if not self._ultimo_tramos or not self._ultimo_analisis:
            return

        visible_w, visible_h = self.canvas_lim.winfo_width(), self.canvas_lim.winfo_height()
        if visible_w <= 1 or visible_h <= 1:
            visible_w, visible_h = 400, 350

        old_base_w = max(visible_w, 1600)
        old_base_h = max(visible_h, 900)
        old_draw_w = int(old_base_w * self._zoom_factor)
        old_draw_h = int(old_base_h * self._zoom_factor)
        old_cx, old_cy = old_draw_w // 2, old_draw_h // 2
        old_escala = old_draw_w * 0.8 / 20

        canvas_x = self.canvas_lim.canvasx(event.x)
        canvas_y = self.canvas_lim.canvasy(event.y)
        world_x = (canvas_x - old_cx) / old_escala
        world_y = (old_cy - canvas_y) / old_escala

        factor = 1.1 if event.delta > 0 else 0.9
        self._zoom_factor = max(0.3, min(self._zoom_factor * factor, 3.0))

        new_draw_w = int(old_base_w * self._zoom_factor)
        new_draw_h = int(old_base_h * self._zoom_factor)
        new_cx, new_cy = new_draw_w // 2, new_draw_h // 2
        new_escala = new_draw_w * 0.8 / 20

        self._graficar(self._ultimo_tramos, self._ultimo_analisis)

        new_canvas_x = new_cx + world_x * new_escala
        new_canvas_y = new_cy - world_y * new_escala

        if new_draw_w > visible_w:
            self.canvas_lim.xview_moveto(max(0.0, min((new_canvas_x - event.x) / new_draw_w, 1.0)))
        if new_draw_h > visible_h:
            self.canvas_lim.yview_moveto(max(0.0, min((new_canvas_y - event.y) / new_draw_h, 1.0)))

    def _mostrar_texto(self, texto):
        self.txt_analisis.config(state="normal")
        self.txt_analisis.delete("1.0", "end")
        self.txt_analisis.insert("end", texto)
        self.txt_analisis.config(state="disabled")
        self.txt_analisis.see("1.0")

    def _clear_placeholder(self, entry):
        if getattr(entry, "_placeholder_text", None) == entry.get():
            entry.delete(0, "end")
            entry.config(fg=AZUL_OSCURO)

    def _restore_placeholder(self, entry):
        if not entry.get().strip():
            placeholder = getattr(entry, "_placeholder_text", "")
            entry.delete(0, "end")
            entry.insert(0, placeholder)
            entry.config(fg="#444444")

    def _limpiar_defensa(self):
        for e in self.entries_defensa.values():
            e.delete(0, "end")
            e.config(bg=BLANCO)
            self._restore_placeholder(e)

    def _verificar_defensa(self):
        if not self.analisis:
            messagebox.showinfo("Aviso", "Primero genere una función.")
            return

        a = self.analisis
        correctos = 0
        total = 0

        def chk(entry, esperado_str):
            nonlocal correctos, total
            val = entry.get().strip()
            if not val or getattr(entry, "_placeholder_text", None) == val:
                return
            normalized = val.lower().replace(" ", "")
            total += 1
            if any(e in normalized for e in esperado_str):
                entry.config(bg="#c8e6c9")
                correctos += 1
            else:
                entry.config(bg="#ffcdd2")

        def num_str(v):
            if v is None:
                return ["nodefinida", "noexiste", "∞"]
            if isinstance(v, str):
                return [v.lower(), v.replace(" ", ""), "∞", "-∞", "+∞", "infinito"]
            try:
                return [str(round(float(v), 2)).replace(".0", ""), str(v)]
            except (ValueError, TypeError):
                return [str(v).lower(), str(v), "∞", "-∞", "+∞", "infinito"]

        lim_izq_entry = self.entries_defensa["lim_izq"]
        lim_der_entry = self.entries_defensa["lim_der"]
        existe_entry = self.entries_defensa["lim_existe"]
        fa_entry = self.entries_defensa["fa"]
        cont_entry = self.entries_defensa["continua"]
        tipo_entry = self.entries_defensa["tipo_disc"]

        # Límite izquierda
        liz = getattr(a, "lim_real_izq", None)
        if liz is None:
            liz = getattr(a, "lim_valor", None)
        chk(lim_izq_entry, num_str(liz) + ["∞", "-∞", "+∞", "infinito"])

        # Límite derecha
        lde = getattr(a, "lim_real_der", None)
        if lde is None:
            lde = getattr(a, "lim_valor", None)
        chk(lim_der_entry, num_str(lde) + ["∞", "-∞", "+∞", "infinito"])

        # Existe
        existe_ok = ["sí", "si", "s", "yes", "existe"] if getattr(a, "lim_existe", False) else ["no", "n", "noexiste"]
        chk(existe_entry, existe_ok)

        # f(a)
        fa = getattr(a, "f_en_a", None)
        chk(fa_entry, num_str(fa) + ["nodefinida", "indefinida", "noexiste"])

        # Continua
        cont_ok = ["sí", "si", "s", "yes", "continua"] if getattr(a, "es_continua", False) else ["no", "n", "nocontinua", "discontinua"]
        chk(cont_entry, cont_ok)

        # Tipo
        tipo = getattr(a, "tipo_discontinuidad", "").lower()
        chk(tipo_entry, [tipo, tipo.split()[0] if tipo else ""]) 

        if total == 0:
            messagebox.showinfo("Aviso", "Complete al menos un campo.")
            if self.logger:
                self.logger.info("PanelLímites: Verificación cancelada, no se completó ningún campo.")
        else:
            messagebox.showinfo("Resultado",
                                f"Respuestas correctas: {correctos}/{total}\n\n"
                                f"Verde = correcto  |  Rojo = revisar")
            if self.logger:
                self.logger.info(f"PanelLímites: Verificación completada {correctos}/{total}")
