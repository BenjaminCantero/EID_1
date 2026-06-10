"""Panel de límites y funciones por tramos."""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from core.exceptions import LimiteInvalidoError, RUTInvalidoError
from core.graficas import puntos_grafica_limite
from core.services import analizar_limites
from ui.componentes import (
    BG_PRINCIPAL, BG_CARD, BG_HEADER, BG_INPUT, BG_CANVAS,
    ACENTO, ACENTO_HOVER, TEXTO, TEXTO_DIM, VERDE, ROJO, NARANJA,
    BORDE_CARD, ENTRY_BG, ENTRY_FG, FONT_TITLE, FONT_SUBTITLE,
    FONT_BODY, FONT_CODE, FONT_SMALL,
    crear_header, crear_barra_rut, crear_card, crear_status_bar
)


class PanelLimites(tk.Frame):
    def __init__(self, parent, obtener_rut_callback=None, actualizar_rut_callback=None, logger=None):
        super().__init__(parent, bg=BG_PRINCIPAL)
        self.logger = logger
        self.obtener_rut = obtener_rut_callback
        self.actualizar_rut = actualizar_rut_callback
        self.tramos = None
        self.analisis = None
        self.a = 0
        self._ultimo_tramos = None
        self._ultimo_analisis = None
        self._zoom_factor = 1.0
        self.lbl_zoom = None
        self._construir_ui()

    def _construir_ui(self):
        # ── Encabezado principal ────────────────────────────
        crear_header(self, "ANÁLISIS DE FUNCIONES Y LÍMITES", "Ingrese un RUT para analizar funciones por tramos y comportamiento de límites")

        # ── Sección de entrada (RUT) ────────────────────────
        _, self.entry_rut = crear_barra_rut(self, "12.345.678-9", "Generar función", self._procesar)
        self.entry_rut.bind("<Return>", lambda e: self._procesar())

        # ── Cuerpo principal ──────────────────────────────────
        body = tk.Frame(self, bg=BG_PRINCIPAL)
        body.pack(fill="both", expand=True, padx=20, pady=5)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # ── Columna izquierda: análisis + tabla ───────────────
        left, body_left = crear_card(body, "Paso 2: Análisis Matemático", "Validación, tipo de función y cálculo de límites laterales")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        
        body_left.columnconfigure(0, weight=1)
        body_left.rowconfigure(0, weight=3)
        body_left.rowconfigure(2, weight=1)

        self.txt_analisis = scrolledtext.ScrolledText(
            body_left,
            font=FONT_CODE,
            bg=BG_CANVAS, fg=TEXTO,
            insertbackground=TEXTO,
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDE_CARD,
            state="disabled")
        self.txt_analisis.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # Tabla de valores
        lbl_tbl = tk.Label(body_left, text="Tabla de Valores (cercanos al punto crítico)", font=FONT_SUBTITLE, fg=ACENTO, bg=BG_CARD, anchor="w")
        lbl_tbl.grid(row=1, column=0, sticky="ew", pady=(0, 4))

        frame_tabla = tk.Frame(body_left, bg=BG_CARD)
        frame_tabla.grid(row=2, column=0, sticky="nsew")
        frame_tabla.rowconfigure(0, weight=1)
        frame_tabla.columnconfigure(0, weight=1)

        self.tabla_tree = ttk.Treeview(frame_tabla,
                                        columns=("x", "f(x)", "lado"),
                                        show="headings", height=6)
        self.tabla_tree.heading("x", text="x")
        self.tabla_tree.heading("f(x)", text="f(x)")
        self.tabla_tree.heading("lado", text="Lado")
        self.tabla_tree.column("x", width=100, anchor="center")
        self.tabla_tree.column("f(x)", width=120, anchor="center")
        self.tabla_tree.column("lado", width=70, anchor="center")
        self.tabla_tree.grid(row=0, column=0, sticky="nsew")

        # ── Columna derecha: Paso 3 + Defensa ────────────────
        right_outer = tk.Frame(body, bg=BG_PRINCIPAL)
        right_outer.grid(row=0, column=1, sticky="nsew")
        right_outer.rowconfigure(0, weight=1)
        right_outer.columnconfigure(0, weight=1)

        right_scroll_canvas = tk.Canvas(right_outer, bg=BG_PRINCIPAL, highlightthickness=0)
        right_scrollbar = ttk.Scrollbar(right_outer, orient="vertical",
                                        command=right_scroll_canvas.yview)
        right = tk.Frame(right_scroll_canvas, bg=BG_PRINCIPAL)
        right.columnconfigure(0, weight=1)

        right.bind(
            "<Configure>",
            lambda e: right_scroll_canvas.configure(
                scrollregion=right_scroll_canvas.bbox("all"))
        )
        rc_window = right_scroll_canvas.create_window((0, 0), window=right, anchor="nw")
        right_scroll_canvas.configure(yscrollcommand=right_scrollbar.set)

        def _on_right_canvas_resize(event):
            right_scroll_canvas.itemconfig(rc_window, width=event.width)
        right_scroll_canvas.bind("<Configure>", _on_right_canvas_resize)

        right_scroll_canvas.grid(row=0, column=0, sticky="nsew")
        right_scrollbar.grid(row=0, column=1, sticky="ns")

        def _on_right_mousewheel(event):
            right_scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        right_scroll_canvas.bind("<MouseWheel>", _on_right_mousewheel)
        right.bind("<MouseWheel>", _on_right_mousewheel)

        # ── Paso 3: Visualización Gráfica + Defensa Oral ─────
        card_graph, body_graph = crear_card(right, "Paso 3: Visualización Gráfica",
                                            "Función generada · comportamiento en punto crítico · defensa oral")
        card_graph.pack(fill="both", expand=True, pady=(0, 10))

        # ── Controles de zoom ─────────────────────────────────
        ctrl_bar = tk.Frame(body_graph, bg=BG_CARD)
        ctrl_bar.pack(fill="x", pady=(0, 3))
        tk.Label(ctrl_bar, text="Zoom:", font=FONT_SMALL,
                 bg=BG_CARD, fg=TEXTO_DIM).pack(side="left", padx=(0, 4))
        for _txt, _cmd in [(" + ", self._zoom_in), (" − ", self._zoom_out), ("1:1", self._zoom_reset)]:
            _b = tk.Button(ctrl_bar, text=_txt, command=_cmd,
                           font=FONT_BODY, bg=BG_CANVAS, fg=ACENTO,
                           activebackground=BORDE_CARD, activeforeground=ACENTO,
                           relief="flat", padx=8, pady=1, cursor="hand2",
                           highlightthickness=1, highlightbackground=BORDE_CARD)
            _b.pack(side="left", padx=1)
        self.lbl_zoom = tk.Label(ctrl_bar, text="100%",
                                  font=FONT_SMALL, bg=BG_CARD, fg=ACENTO)
        self.lbl_zoom.pack(side="left", padx=6)
        tk.Label(ctrl_bar, text="Rueda: zoom  ·  Clic+arrastrar: mover",
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXTO_DIM).pack(side="right", padx=4)

        # ── Canvas gráfica con altura fija ───────────────────
        graph_canvas_frame = tk.Frame(body_graph, bg=BG_CANVAS, height=320)
        graph_canvas_frame.pack(fill="x", padx=0, pady=(0, 4))
        graph_canvas_frame.pack_propagate(False)
        graph_canvas_frame.columnconfigure(0, weight=1)
        graph_canvas_frame.rowconfigure(0, weight=1)

        self.canvas_lim = tk.Canvas(graph_canvas_frame,
                                     bg=BG_CANVAS, relief="flat", bd=0,
                                     highlightthickness=1,
                                     highlightbackground=BORDE_CARD,
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

        # ── Info compacta: tipo función y discontinuidad ──────
        self.lbl_canvas_lim_info = tk.Label(body_graph, text="Esperando análisis...",
                                             font=FONT_SMALL,
                                             bg=BG_CARD, fg=TEXTO_DIM)
        self.lbl_canvas_lim_info.pack(anchor="w", pady=(2, 0))

        self.lbl_funcion = tk.Label(body_graph, text="",
                                     font=FONT_CODE,
                                     bg=BG_CARD, fg=TEXTO,
                                     wraplength=400, justify="left")
        self.lbl_funcion.pack(fill="x", pady=(2, 0))

        # ── Separador ─────────────────────────────────────────
        tk.Frame(body_graph, bg=BORDE_CARD, height=1).pack(fill="x", pady=8)

        # ── Campos de defensa integrados a la gráfica ─────────
        tk.Label(body_graph,
                 text="Defensa Oral — Complete desde la gráfica",
                 font=FONT_SUBTITLE, fg=ACENTO, bg=BG_CARD,
                 anchor="w").pack(fill="x", pady=(0, 6))

        campos = [
            ("lim_izq",      "Lím. izquierda:",     "lim x→a⁻ f(x) = "),
            ("lim_der",      "Lím. derecha:",        "lim x→a⁺ f(x) = "),
            ("lim_existe",   "¿Existe límite?:",     "sí / no"),
            ("fa",           "f(a) =",               "valor o 'no def.'"),
            ("continua",     "¿Es continua?:",       "sí / no"),
            ("tipo_disc",    "Tipo discontinuidad:", "removible/salto/infinita"),
            ("justificacion","Justificación:",        "descripción breve"),
        ]

        campos_grid = tk.Frame(body_graph, bg=BG_CARD)
        campos_grid.pack(fill="x")
        campos_grid.columnconfigure(0, weight=1)
        campos_grid.columnconfigure(1, weight=1)

        self.entries_defensa = {}
        for idx, (key, etiqueta, placeholder) in enumerate(campos):
            row_i = idx // 2
            col_i = idx % 2
            celda = tk.Frame(campos_grid, bg=BG_CARD)
            celda.grid(row=row_i, column=col_i, sticky="ew",
                       padx=(0, 6) if col_i == 0 else 0, pady=3)
            tk.Label(celda, text=etiqueta, width=16, anchor="w",
                     font=FONT_SMALL, bg=BG_CARD, fg=TEXTO).pack(side="left")
            e = tk.Entry(celda, font=FONT_CODE, width=15,
                          bg=ENTRY_BG, fg=TEXTO_DIM, insertbackground=ENTRY_FG,
                          relief="flat", bd=0, highlightthickness=1,
                          highlightbackground=BORDE_CARD)
            e.pack(side="left", padx=2, ipady=2)
            e.insert(0, placeholder)
            e._placeholder_text = placeholder
            e.bind("<FocusIn>", lambda event, entry=e: self._clear_placeholder(entry))
            e.bind("<FocusOut>", lambda event, entry=e: self._restore_placeholder(entry))
            self.entries_defensa[key] = e

        # Botones defensa
        btn_row = tk.Frame(body_graph, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(10, 0))

        btn_verificar = tk.Button(btn_row, text="Verificar",
                  command=self._verificar_defensa,
                  font=FONT_SUBTITLE,
                  bg=VERDE, fg=BG_PRINCIPAL, activebackground="#3ee884",
                  activeforeground=BG_PRINCIPAL,
                  relief="flat", padx=15, pady=6, cursor="hand2")
        btn_verificar.pack(side="left", padx=(0, 10))

        def on_enter_ver(e):
            btn_verificar.config(bg="#3ee884")
        def on_leave_ver(e):
            btn_verificar.config(bg=VERDE)
        btn_verificar.bind("<Enter>", on_enter_ver)
        btn_verificar.bind("<Leave>", on_leave_ver)

        btn_limpiar = tk.Button(btn_row, text="Limpiar Campos",
                  command=self._limpiar_defensa,
                  font=FONT_SUBTITLE,
                  bg=BG_PRINCIPAL, fg=TEXTO, activebackground=BORDE_CARD,
                  activeforeground=TEXTO,
                  relief="flat", padx=15, pady=6, cursor="hand2",
                  highlightthickness=1, highlightbackground=BORDE_CARD)
        btn_limpiar.pack(side="left")

        def on_enter_lim(e):
            btn_limpiar.config(bg=BORDE_CARD)
        def on_leave_lim(e):
            btn_limpiar.config(bg=BG_PRINCIPAL)
        btn_limpiar.bind("<Enter>", on_enter_lim)
        btn_limpiar.bind("<Leave>", on_leave_lim)

        # Estado
        _, self.lbl_estado = crear_status_bar(self, "Ingrese un RUT válido y presione 'Generar función'")

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
        self.lbl_canvas_lim_info.config(text=f"✓ {resultado.tipo_discontinuidad} (Caso: {resultado.caso_tipo})", fg=ACENTO)
        self.lbl_funcion.config(text=f"f(x) con a={resultado.a}  │  Tipo: {resultado.caso_tipo}  │  Discontinuidad: {resultado.tipo_discontinuidad}")
        self.lbl_estado.config(text=f"✓ Función generada — {resultado.tipo_discontinuidad} — Complete los campos de defensa", fg=VERDE)
        if self.logger:
            self.logger.info(f"PanelLímites: Función generada para RUT '{rut_str}' — caso '{resultado.caso_tipo}', tipo '{resultado.tipo_discontinuidad}'")

        # Actualizar RUT validado en la aplicación principal
        if self.actualizar_rut:
            from core.rut import formatear_rut
            cuerpo_8 = "".join(str(d) for d in resultado.digitos).zfill(8)
            rut_formateado = formatear_rut(cuerpo_8, resultado.dv)
            self.actualizar_rut(rut_formateado)

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

        # Usar el tamaño real del canvas visible
        visible_w = self.canvas_lim.winfo_width()
        visible_h = self.canvas_lim.winfo_height()
        if visible_w <= 1 or visible_h <= 1:
            visible_w, visible_h = 450, 290

        # Aplicar zoom
        draw_w = int(visible_w * self._zoom_factor)
        draw_h = int(visible_h * self._zoom_factor)
        if draw_w < visible_w:
            draw_w = visible_w
        if draw_h < visible_h:
            draw_h = visible_h

        caso = tramos["tipo"]
        a = tramos["a"]
        rango_x = 8.0

        # Obtener segmentos y pantalla_fn desde graficas.py
        # pantalla_fn usa: cx + (x-a)*escala_x, cy - y*escala_y
        # donde escala_x = draw_w/(2*rango_x), escala_y = draw_h/(2*rango_x)
        segmentos, pantalla_fn = puntos_grafica_limite(tramos, draw_w, draw_h, rango_x=rango_x)

        # Usar las mismas escalas que puntos_grafica_limite
        cx = draw_w / 2
        cy = draw_h / 2
        escala_x = draw_w / (2 * rango_x)
        escala_y = draw_h / (2 * rango_x)

        def mp(x, y):
            """Mismo sistema de coordenadas que puntos_grafica_limite."""
            return cx + (x - a) * escala_x, cy - y * escala_y

        # ── Fondo ──
        self.canvas_lim.create_rectangle(0, 0, draw_w, draw_h, fill=BG_CANVAS, outline="")

        # ── Grid ──
        for i in range(-int(rango_x) - 1, int(rango_x) + 2):
            px, _ = mp(a + i, 0)
            if -5 <= px <= draw_w + 5:
                self.canvas_lim.create_line(px, 0, px, draw_h, fill=BORDE_CARD, width=0.5)
        for j in range(-int(rango_x) - 1, int(rango_x) + 2):
            _, py = mp(a, j)
            if -5 <= py <= draw_h + 5:
                self.canvas_lim.create_line(0, py, draw_w, py, fill=BORDE_CARD, width=0.5)

        # ── Ejes matemáticos ──
        _, eje_y_px = mp(a, 0)
        eje_y_px = cy
        eje_x_px, _ = mp(0, 0)
        self.canvas_lim.create_line(0, cy, draw_w, cy, fill=TEXTO_DIM, width=1.5)
        self.canvas_lim.create_line(eje_x_px, 0, eje_x_px, draw_h, fill=TEXTO_DIM, width=1.5)

        # ── Marcas y etiquetas eje X ──
        for i in range(-int(rango_x) - 1, int(rango_x) + 2):
            val = a + i
            px, _ = mp(val, 0)
            if -5 <= px <= draw_w + 5:
                self.canvas_lim.create_line(px, cy - 4, px, cy + 4, fill=BORDE_CARD, width=1)
                self.canvas_lim.create_text(px, cy + 13, text=f"{val:.3g}",
                                            font=FONT_SMALL, fill=TEXTO_DIM)

        # ── Marcas y etiquetas eje Y ──
        for j in range(-int(rango_x) - 1, int(rango_x) + 2):
            if j == 0:
                continue
            _, py = mp(a, j)
            if -5 <= py <= draw_h + 5:
                self.canvas_lim.create_line(eje_x_px - 4, py, eje_x_px + 4, py, fill=BORDE_CARD, width=1)
                self.canvas_lim.create_text(eje_x_px - 18, py, text=f"{j:.3g}",
                                            font=FONT_SMALL, fill=TEXTO_DIM)

        self.canvas_lim.create_text(draw_w - 10, cy - 12, text="x",
                                     font=FONT_SMALL, fill=TEXTO_DIM)
        self.canvas_lim.create_text(eje_x_px + 12, 10, text="y",
                                     font=FONT_SMALL, fill=TEXTO_DIM)

        # ── Asíntota vertical si es infinita ──
        if caso == "infinita":
            ax_sint, _ = mp(a, 0)
            self.canvas_lim.create_line(ax_sint, 3, ax_sint, draw_h - 3,
                                         fill=ROJO, width=2, dash=(6, 4))
            self.canvas_lim.create_text(ax_sint + 10, 18,
                                         text=f"x={a}", font=FONT_SMALL, fill=ROJO)

        # ── Dibujar curva de la función ──
        for seg in segmentos:
            x1, y1, x2, y2 = seg
            in1 = (-30 <= x1 <= draw_w + 30 and -30 <= y1 <= draw_h + 30)
            in2 = (-30 <= x2 <= draw_w + 30 and -30 <= y2 <= draw_h + 30)
            if in1 or in2:
                self.canvas_lim.create_line(x1, y1, x2, y2,
                                            fill=VERDE, width=2.5,
                                            capstyle="round", joinstyle="round")

        # ── Etiqueta a en el eje X ──
        ax_label, _ = mp(a, 0)
        self.canvas_lim.create_text(ax_label, cy + 24,
                                     text=f"a={a}", font=FONT_SMALL, fill=NARANJA)

        # ── Discontinuidad removible ──
        if caso == "removible":
            lim_val = getattr(analisis, "lim_valor", None)
            f_en_a  = getattr(analisis, "f_en_a", None)
            if isinstance(lim_val, (int, float)):
                px_h, py_h = pantalla_fn(a, lim_val)
                self.canvas_lim.create_oval(px_h - 7, py_h - 7, px_h + 7, py_h + 7,
                                             outline=ACENTO, fill="", width=3)
                self.canvas_lim.create_text(px_h + 22, py_h - 10,
                                             text=f"lim={lim_val}",
                                             font=FONT_SMALL, fill=ACENTO)
            if f_en_a is not None and isinstance(f_en_a, (int, float)):
                px_fa, py_fa = pantalla_fn(a, f_en_a)
                self.canvas_lim.create_oval(px_fa - 5, py_fa - 5, px_fa + 5, py_fa + 5,
                                             fill=VERDE, outline=ENTRY_FG, width=2)

        # ── Discontinuidad de salto ──
        if caso == "salto":
            lim_izq = getattr(analisis, "lim_real_izq", None)
            lim_der = getattr(analisis, "lim_real_der", None)
            if isinstance(lim_izq, (int, float)):
                px_i, py_i = pantalla_fn(a, lim_izq)
                self.canvas_lim.create_oval(px_i - 6, py_i - 6, px_i + 6, py_i + 6,
                                             outline=ROJO, fill="", width=3)
                self.canvas_lim.create_text(px_i - 20, py_i - 12,
                                             text=f"L⁻={lim_izq}",
                                             font=FONT_SMALL, fill=ROJO)
            if isinstance(lim_der, (int, float)):
                px_d, py_d = pantalla_fn(a, lim_der)
                self.canvas_lim.create_oval(px_d - 6, py_d - 6, px_d + 6, py_d + 6,
                                             fill=VERDE, outline=ENTRY_FG, width=2)
                self.canvas_lim.create_text(px_d + 14, py_d - 12,
                                             text=f"L⁺={lim_der}",
                                             font=FONT_SMALL, fill=VERDE)

        # ── Panel de información de límites (esquina superior izquierda) ──
        lim_izq_val = getattr(analisis, 'lim_izquierda', None)
        lim_der_val = getattr(analisis, 'lim_derecha', None)
        f_a_val     = getattr(analisis, 'f_en_a', None)
        tipo_disc   = getattr(analisis, 'tipo_discontinuidad', '')

        def _fmt(v):
            if v is None:
                return "No def."
            if isinstance(v, str):
                return v
            try:
                fv = float(v)
                return "-∞" if fv < -1e8 else ("+∞" if fv > 1e8 else f"{fv:.4g}")
            except (TypeError, ValueError):
                return str(v)

        ann_lines = [
            (f"lím x→{a}⁻  =  {_fmt(lim_izq_val)}", ROJO),
            (f"lím x→{a}⁺  =  {_fmt(lim_der_val)}", VERDE),
            (f"f({a})       =  {_fmt(f_a_val)}",      ACENTO),
            (f"Tipo: {tipo_disc}",                     TEXTO_DIM),
        ]
        box_h = len(ann_lines) * 17 + 8
        self.canvas_lim.create_rectangle(4, 4, 230, 4 + box_h,
                                          fill=BG_CANVAS, outline=BORDE_CARD, width=1)
        for i, (line, color) in enumerate(ann_lines):
            self.canvas_lim.create_text(10, 13 + i * 17,
                                         text=line, font=FONT_SMALL, fill=color, anchor="w")

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

        factor = 1.15 if event.delta > 0 else 0.87
        self._zoom_factor = max(0.3, min(self._zoom_factor * factor, 5.0))
        if self.lbl_zoom:
            self.lbl_zoom.config(text=f"{int(self._zoom_factor * 100)}%")
        self._graficar(self._ultimo_tramos, self._ultimo_analisis)

    def _zoom_in(self):
        self._zoom_factor = min(self._zoom_factor * 1.25, 5.0)
        if self.lbl_zoom:
            self.lbl_zoom.config(text=f"{int(self._zoom_factor * 100)}%")
        if self._ultimo_tramos and self._ultimo_analisis:
            self._graficar(self._ultimo_tramos, self._ultimo_analisis)

    def _zoom_out(self):
        self._zoom_factor = max(self._zoom_factor / 1.25, 0.3)
        if self.lbl_zoom:
            self.lbl_zoom.config(text=f"{int(self._zoom_factor * 100)}%")
        if self._ultimo_tramos and self._ultimo_analisis:
            self._graficar(self._ultimo_tramos, self._ultimo_analisis)

    def _zoom_reset(self):
        self._zoom_factor = 1.0
        if self.lbl_zoom:
            self.lbl_zoom.config(text="100%")
        if self._ultimo_tramos and self._ultimo_analisis:
            self._graficar(self._ultimo_tramos, self._ultimo_analisis)

    def _mostrar_texto(self, texto):
        self.txt_analisis.config(state="normal")
        self.txt_analisis.delete("1.0", "end")
        self.txt_analisis.insert("end", texto)
        self.txt_analisis.config(state="disabled")
        self.txt_analisis.see("1.0")

    def _clear_placeholder(self, entry):
        if getattr(entry, "_placeholder_text", None) == entry.get():
            entry.delete(0, "end")
            entry.config(fg=ENTRY_FG)

    def _restore_placeholder(self, entry):
        if not entry.get().strip():
            placeholder = getattr(entry, "_placeholder_text", "")
            entry.delete(0, "end")
            entry.insert(0, placeholder)
            entry.config(fg=TEXTO_DIM)

    def _limpiar_defensa(self):
        for e in self.entries_defensa.values():
            e.delete(0, "end")
            e.config(bg=ENTRY_BG)
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
                entry.config(bg="#c8e6c9", fg=BG_PRINCIPAL)
                correctos += 1
            else:
                entry.config(bg="#ffcdd2", fg=BG_PRINCIPAL)

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
