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


def _hover(btn, color_on, color_off):
    """Vincula efecto hover a un botón de forma compacta."""
    btn.bind("<Enter>", lambda e: btn.config(bg=color_on))
    btn.bind("<Leave>", lambda e: btn.config(bg=color_off))


class PanelLimites(tk.Frame):
    def __init__(self, parent, logger=None):
        super().__init__(parent, bg=BG_PRINCIPAL)
        self.logger = logger
        self.tramos = self.analisis = None
        self.a = 0
        self._ultimo_tramos = self._ultimo_analisis = None
        self._zoom_factor = 1.0
        self._construir_ui()

    # ─────────────────────────── UI ────────────────────────────────

    def _construir_ui(self):
        crear_header(self, "ANÁLISIS DE FUNCIONES Y LÍMITES",
                     "Ingrese un RUT para analizar funciones por tramos y comportamiento de límites")

        _, self.entry_rut = crear_barra_rut(self, "12.345.678-9", "Generar función", self._procesar)
        self.entry_rut.bind("<Return>", lambda e: self._procesar())

        body = tk.Frame(self, bg=BG_PRINCIPAL)
        body.pack(fill="both", expand=True, padx=20, pady=5)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._construir_columna_izquierda(body)
        self._construir_columna_derecha(body)

        _, self.lbl_estado = crear_status_bar(self, "Ingrese un RUT válido y presione 'Generar función'")

    def _construir_columna_izquierda(self, body):
        left, body_left = crear_card(body, "Paso 2: Análisis Matemático",
                                     "Validación, tipo de función y cálculo de límites laterales")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        body_left.columnconfigure(0, weight=1)
        body_left.rowconfigure(0, weight=3)
        body_left.rowconfigure(2, weight=1)

        self.txt_analisis = scrolledtext.ScrolledText(
            body_left, font=FONT_CODE, bg=BG_CANVAS, fg=TEXTO,
            insertbackground=TEXTO, relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDE_CARD, state="disabled")
        self.txt_analisis.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        tk.Label(body_left, text="Tabla de Valores (cercanos al punto crítico)",
                 font=FONT_SUBTITLE, fg=ACENTO, bg=BG_CARD, anchor="w"
                 ).grid(row=1, column=0, sticky="ew", pady=(0, 4))

        frame_tabla = tk.Frame(body_left, bg=BG_CARD)
        frame_tabla.grid(row=2, column=0, sticky="nsew")
        frame_tabla.rowconfigure(0, weight=1)
        frame_tabla.columnconfigure(0, weight=1)

        self.tabla_tree = ttk.Treeview(frame_tabla, columns=("x", "f(x)", "lado"),
                                        show="headings", height=6)
        for col, txt, w in [("x", "x", 100), ("f(x)", "f(x)", 120), ("lado", "Lado", 70)]:
            self.tabla_tree.heading(col, text=txt)
            self.tabla_tree.column(col, width=w, anchor="center")
        self.tabla_tree.grid(row=0, column=0, sticky="nsew")

    def _construir_columna_derecha(self, body):
        right_outer = tk.Frame(body, bg=BG_PRINCIPAL)
        right_outer.grid(row=0, column=1, sticky="nsew")
        right_outer.rowconfigure(0, weight=1)
        right_outer.columnconfigure(0, weight=1)

        rsc = tk.Canvas(right_outer, bg=BG_PRINCIPAL, highlightthickness=0)
        rsb = ttk.Scrollbar(right_outer, orient="vertical", command=rsc.yview)
        right = tk.Frame(rsc, bg=BG_PRINCIPAL)
        right.columnconfigure(0, weight=1)

        rc_win = rsc.create_window((0, 0), window=right, anchor="nw")
        right.bind("<Configure>", lambda e: rsc.configure(scrollregion=rsc.bbox("all")))
        rsc.configure(yscrollcommand=rsb.set)
        rsc.bind("<Configure>", lambda e: rsc.itemconfig(rc_win, width=e.width))

        rsc.grid(row=0, column=0, sticky="nsew")
        rsb.grid(row=0, column=1, sticky="ns")

        mw = lambda e: rsc.yview_scroll(int(-1 * (e.delta / 120)), "units")
        rsc.bind("<MouseWheel>", mw)
        right.bind("<MouseWheel>", mw)

        self._construir_grafica(right)
        self._construir_funcion_generada(right)
        self._construir_defensa(right)

    def _construir_grafica(self, parent):
        card_graph, body_graph = crear_card(parent, "Paso 3: Visualización Gráfica",
                                            "Comportamiento de la función y su discontinuidad")
        card_graph.pack(fill="x", pady=(0, 10))

        gcf = tk.Frame(body_graph, bg=BG_CANVAS, height=310)
        gcf.pack(fill="x", padx=0, pady=(0, 4))
        gcf.pack_propagate(False)
        gcf.columnconfigure(0, weight=1)
        gcf.rowconfigure(0, weight=1)

        self.canvas_lim = tk.Canvas(gcf, bg=BG_CANVAS, relief="flat", bd=0,
                                     highlightthickness=1, highlightbackground=BORDE_CARD,
                                     xscrollincrement=10, yscrollincrement=10)
        vbar = ttk.Scrollbar(gcf, orient="vertical", command=self.canvas_lim.yview)
        hbar = ttk.Scrollbar(gcf, orient="horizontal", command=self.canvas_lim.xview)
        self.canvas_lim.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas_lim.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")

        self.canvas_lim.bind("<Configure>", self._on_canvas_resize)
        self.canvas_lim.bind("<MouseWheel>", self._on_graph_mousewheel)
        self.canvas_lim.bind("<Shift-MouseWheel>", self._on_graph_shift_mousewheel)
        self.canvas_lim.bind("<ButtonPress-1>", lambda e: self.canvas_lim.scan_mark(e.x, e.y))
        self.canvas_lim.bind("<B1-Motion>", lambda e: self.canvas_lim.scan_dragto(e.x, e.y, gain=1))

        self.lbl_canvas_lim_info = tk.Label(body_graph, text="Esperando análisis...",
                                             font=FONT_SMALL, bg=BG_CARD, fg=TEXTO_DIM)
        self.lbl_canvas_lim_info.pack(anchor="w")

    def _construir_funcion_generada(self, parent):
        card_resumen, body_resumen = crear_card(parent, "Función Generada")
        card_resumen.pack(fill="x", pady=(0, 10))
        self.lbl_funcion = tk.Label(body_resumen, text="Ninguna función generada aún.",
                                     font=FONT_CODE, bg=BG_CARD, fg=TEXTO,
                                     wraplength=320, justify="left")
        self.lbl_funcion.pack(fill="x", pady=(2, 0))

    def _construir_defensa(self, parent):
        card_defensa, body_defensa = crear_card(parent, "Defensa Oral",
                                                "Complete los campos para demostrar su comprensión de límites")
        card_defensa.pack(fill="x", pady=(0, 10))

        campos = [
            ("lim_izq",      "Límite por izquierda:", "lim x→a⁻ f(x) = "),
            ("lim_der",      "Límite por derecha:",   "lim x→a⁺ f(x) = "),
            ("lim_existe",   "¿Existe el límite?:",   "sí / no"),
            ("fa",           "f(a) =",                "valor o 'no def.'"),
            ("continua",     "¿Es continua?:",        "sí / no"),
            ("tipo_disc",    "Tipo de discontinuidad:", "removible / salto / infinita"),
            ("justificacion","Justificación matemática:", "descripción breve"),
        ]
        self.entries_defensa = {}
        for key, etiqueta, placeholder in campos:
            fila = tk.Frame(body_defensa, bg=BG_CARD)
            fila.pack(fill="x", pady=3)
            tk.Label(fila, text=etiqueta, width=22, anchor="w",
                     font=FONT_SUBTITLE, bg=BG_CARD, fg=TEXTO).pack(side="left")
            e = tk.Entry(fila, font=FONT_CODE, width=22, bg=ENTRY_BG, fg=TEXTO_DIM,
                          insertbackground=ENTRY_FG, relief="flat", bd=0,
                          highlightthickness=1, highlightbackground=BORDE_CARD)
            e.pack(side="left", padx=2, ipady=2)
            e.insert(0, placeholder)
            e._placeholder_text = placeholder
            e.bind("<FocusIn>",  lambda ev, en=e: self._clear_placeholder(en))
            e.bind("<FocusOut>", lambda ev, en=e: self._restore_placeholder(en))
            self.entries_defensa[key] = e

        btn_row = tk.Frame(body_defensa, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(10, 0))

        btn_ver = tk.Button(btn_row, text="Verificar", command=self._verificar_defensa,
                            font=FONT_SUBTITLE, bg=VERDE, fg=BG_PRINCIPAL,
                            activebackground="#3ee884", activeforeground=BG_PRINCIPAL,
                            relief="flat", padx=15, pady=6, cursor="hand2")
        btn_ver.pack(side="left", padx=(0, 10))
        _hover(btn_ver, "#3ee884", VERDE)

        btn_lim = tk.Button(btn_row, text="Limpiar Campos", command=self._limpiar_defensa,
                            font=FONT_SUBTITLE, bg=BG_PRINCIPAL, fg=TEXTO,
                            activebackground=BORDE_CARD, activeforeground=TEXTO,
                            relief="flat", padx=15, pady=6, cursor="hand2",
                            highlightthickness=1, highlightbackground=BORDE_CARD)
        btn_lim.pack(side="left")
        _hover(btn_lim, BORDE_CARD, BG_PRINCIPAL)

    # ─────────────────────────── LÓGICA ────────────────────────────

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

        self.tramos  = resultado.tramos_info
        self.analisis = resultado

        texto = (
            "╔════════════════════════════════════════════════════════╗\n"
            "║               FUNCIÓN GENERADA POR TRAMOS            ║\n"
            "╚════════════════════════════════════════════════════════╝\n\n"
            f"{resultado.descripcion_funcion}\n\n"
            f"➤ Punto de análisis: a = {resultado.a}\n\n"
            f"Criterio de selección del caso:\n  {resultado.razon_caso}\n\n"
            "╔════════════════════════════════════════════════════════╗\n"
            "║              CÁLCULO DE LÍMITES LATERALES             ║\n"
            "╚════════════════════════════════════════════════════════╝\n\n"
            + "\n".join(resultado.pasos_limites) + "\n"
        )
        self._mostrar_texto(texto)

        self.lbl_canvas_lim_info.config(
            text=f"✓ {resultado.tipo_discontinuidad} (Caso: {resultado.caso_tipo})", fg=ACENTO)
        self.lbl_funcion.config(
            text=f"f(x) con a={resultado.a}  │  Tipo: {resultado.caso_tipo}  │  "
                 f"Discontinuidad: {resultado.tipo_discontinuidad}")
        self.lbl_estado.config(
            text=f"✓ Función generada — {resultado.tipo_discontinuidad} — Complete los campos de defensa",
            fg=VERDE)
        if self.logger:
            self.logger.info(
                f"PanelLímites: Función generada para RUT '{rut_str}' — "
                f"caso '{resultado.caso_tipo}', tipo '{resultado.tipo_discontinuidad}'")

        for row in self.tabla_tree.get_children():
            self.tabla_tree.delete(row)
        for fila in resultado.tabla_valores:
            x_str = f"{fila['x']:.4f}" if fila['x'] is not None else "—"
            y_str = "No def." if fila['f_x'] is None else f"{fila['f_x']:.4f}"
            lado  = fila['lado']
            self.tabla_tree.insert("", "end",
                                   values=(x_str, y_str, "← izq" if lado == "izq" else "der →"),
                                   tags=(lado,))
        self.tabla_tree.tag_configure("izq", background="#1a3a6a", foreground="#90caf9")
        self.tabla_tree.tag_configure("der", background="#1a4a2a", foreground="#a5d6a7")

        self._graficar(self.tramos, resultado)
        self._limpiar_defensa()

    # ─────────────────────────── GRÁFICA ───────────────────────────

    def _graficar(self, tramos, analisis):
        self._ultimo_tramos, self._ultimo_analisis = tramos, analisis
        self.canvas_lim.delete("all")

        visible_w = max(450, self.canvas_lim.winfo_width())
        visible_h = max(290, self.canvas_lim.winfo_height())
        draw_w = max(visible_w, int(visible_w * self._zoom_factor))
        draw_h = max(visible_h, int(visible_h * self._zoom_factor))

        caso    = tramos["tipo"]
        a       = tramos["a"]
        rango_x = 8.0
        segmentos, pantalla_fn = puntos_grafica_limite(tramos, draw_w, draw_h, rango_x=rango_x)

        cx, cy   = draw_w / 2, draw_h / 2
        escala_x = draw_w / (2 * rango_x)
        escala_y = draw_h / (2 * rango_x)
        mp = lambda x, y: (cx + (x - a) * escala_x, cy - y * escala_y)

        # Fondo
        self.canvas_lim.create_rectangle(0, 0, draw_w, draw_h, fill=BG_CANVAS, outline="")

        eje_x_px, _ = mp(0, 0)

        # Cuadrícula + ticks + etiquetas (bucle unificado)
        rng = range(-int(rango_x) - 1, int(rango_x) + 2)
        for i in rng:
            # ── Eje vertical (grid + tick + label X) ──
            px, _ = mp(a + i, 0)
            if -5 <= px <= draw_w + 5:
                self.canvas_lim.create_line(px, 0, px, draw_h, fill=BORDE_CARD, width=0.5)
                self.canvas_lim.create_line(px, cy - 4, px, cy + 4, fill=BORDE_CARD, width=1)
                self.canvas_lim.create_text(px, cy + 13, text=f"{a + i:.3g}",
                                            font=FONT_SMALL, fill=TEXTO_DIM)
            # ── Eje horizontal (grid + tick + label Y) ──
            _, py = mp(a, i)
            if -5 <= py <= draw_h + 5:
                self.canvas_lim.create_line(0, py, draw_w, py, fill=BORDE_CARD, width=0.5)
                if i != 0:
                    self.canvas_lim.create_line(eje_x_px - 4, py, eje_x_px + 4, py,
                                                fill=BORDE_CARD, width=1)
                    self.canvas_lim.create_text(eje_x_px - 18, py, text=f"{i:.3g}",
                                                font=FONT_SMALL, fill=TEXTO_DIM)

        # Ejes matemáticos
        self.canvas_lim.create_line(0, cy, draw_w, cy, fill=TEXTO_DIM, width=1.5)
        self.canvas_lim.create_line(eje_x_px, 0, eje_x_px, draw_h, fill=TEXTO_DIM, width=1.5)
        self.canvas_lim.create_text(draw_w - 10, cy - 12, text="x", font=FONT_SMALL, fill=TEXTO_DIM)
        self.canvas_lim.create_text(eje_x_px + 12, 10,    text="y", font=FONT_SMALL, fill=TEXTO_DIM)

        # Asíntota vertical
        if caso == "infinita":
            ax_sint, _ = mp(a, 0)
            self.canvas_lim.create_line(ax_sint, 3, ax_sint, draw_h - 3,
                                         fill=ROJO, width=2, dash=(6, 4))
            self.canvas_lim.create_text(ax_sint + 10, 18, text=f"x={a}",
                                         font=FONT_SMALL, fill=ROJO)

        # Curva
        for x1, y1, x2, y2 in segmentos:
            in1 = -30 <= x1 <= draw_w + 30 and -30 <= y1 <= draw_h + 30
            in2 = -30 <= x2 <= draw_w + 30 and -30 <= y2 <= draw_h + 30
            if in1 or in2:
                self.canvas_lim.create_line(x1, y1, x2, y2, fill=VERDE, width=2.5,
                                            capstyle="round", joinstyle="round")

        # Etiqueta a
        self.canvas_lim.create_text(mp(a, 0)[0], cy + 24, text=f"a={a}",
                                     font=FONT_SMALL, fill=NARANJA)

        # Discontinuidad removible
        if caso == "removible":
            lim_val = getattr(analisis, "lim_valor", None)
            f_en_a  = getattr(analisis, "f_en_a", None)
            if isinstance(lim_val, (int, float)):
                px_h, py_h = pantalla_fn(a, lim_val)
                self.canvas_lim.create_oval(px_h - 7, py_h - 7, px_h + 7, py_h + 7,
                                             outline=ACENTO, fill="", width=3)
                self.canvas_lim.create_text(px_h + 22, py_h - 10, text=f"lim={lim_val}",
                                             font=FONT_SMALL, fill=ACENTO)
            if isinstance(f_en_a, (int, float)):
                px_fa, py_fa = pantalla_fn(a, f_en_a)
                self.canvas_lim.create_oval(px_fa - 5, py_fa - 5, px_fa + 5, py_fa + 5,
                                             fill=VERDE, outline=ENTRY_FG, width=2)

        # Discontinuidad de salto
        if caso == "salto":
            lim_izq = getattr(analisis, "lim_real_izq", getattr(analisis, "lim_valor", None))
            lim_der = getattr(analisis, "lim_real_der", getattr(analisis, "lim_valor", None))
            if isinstance(lim_izq, (int, float)):
                px_i, py_i = pantalla_fn(a, lim_izq)
                self.canvas_lim.create_oval(px_i - 6, py_i - 6, px_i + 6, py_i + 6,
                                             outline=ROJO, fill="", width=3)
                self.canvas_lim.create_text(px_i - 20, py_i - 12, text=f"L⁻={lim_izq}",
                                             font=FONT_SMALL, fill=ROJO)
            if isinstance(lim_der, (int, float)):
                px_d, py_d = pantalla_fn(a, lim_der)
                self.canvas_lim.create_oval(px_d - 6, py_d - 6, px_d + 6, py_d + 6,
                                             fill=VERDE, outline=ENTRY_FG, width=2)
                self.canvas_lim.create_text(px_d + 14, py_d - 12, text=f"L⁺={lim_der}",
                                             font=FONT_SMALL, fill=VERDE)

        # Leyenda inferior
        self.canvas_lim.create_text(draw_w // 2, draw_h - 8,
                                     text=f"Discontinuidad: {getattr(analisis, 'tipo_discontinuidad', '')}",
                                     font=FONT_SUBTITLE, fill=VERDE)
        self.canvas_lim.configure(scrollregion=(0, 0, draw_w, draw_h))

        if draw_w > visible_w:
            self.canvas_lim.xview_moveto((draw_w - visible_w) / 2 / draw_w)
        if draw_h > visible_h:
            self.canvas_lim.yview_moveto((draw_h - visible_h) / 2 / draw_h)

    # ─────────────────────────── CALLBACKS ─────────────────────────

    def _on_canvas_resize(self, event):
        if self._ultimo_tramos and self._ultimo_analisis:
            self._graficar(self._ultimo_tramos, self._ultimo_analisis)

    def _on_graph_mousewheel(self, event):
        if self._ultimo_tramos and self._ultimo_analisis:
            self._zoom_factor = max(0.3, min(self._zoom_factor * (1.15 if event.delta > 0 else 0.87), 5.0))
            self._graficar(self._ultimo_tramos, self._ultimo_analisis)
        return "break"

    def _on_graph_shift_mousewheel(self, event):
        self.canvas_lim.xview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

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
            entry.delete(0, "end")
            entry.insert(0, getattr(entry, "_placeholder_text", ""))
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
        correctos = total = 0

        def chk(entry, esperados):
            nonlocal correctos, total
            val = entry.get().strip()
            if not val or getattr(entry, "_placeholder_text", None) == val:
                return
            total += 1
            if any(e in val.lower().replace(" ", "") for e in esperados):
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

        liz  = getattr(a, "lim_real_izq", getattr(a, "lim_valor", None))
        lde  = getattr(a, "lim_real_der", getattr(a, "lim_valor", None))
        tipo = getattr(a, "tipo_discontinuidad", "").lower()

        validaciones = {
            "lim_izq":   num_str(liz)  + ["∞", "-∞", "+∞", "infinito"],
            "lim_der":   num_str(lde)  + ["∞", "-∞", "+∞", "infinito"],
            "lim_existe":["sí", "si", "s", "yes", "existe"] if getattr(a, "lim_existe", False)
                         else ["no", "n", "noexiste"],
            "fa":        num_str(getattr(a, "f_en_a", None)) + ["nodefinida", "indefinida", "noexiste"],
            "continua":  ["sí", "si", "s", "yes", "continua"] if getattr(a, "es_continua", False)
                         else ["no", "n", "nocontinua", "discontinua"],
            "tipo_disc": [tipo, tipo.split()[0] if tipo else ""],
        }

        for key, esperados in validaciones.items():
            if key in self.entries_defensa:
                chk(self.entries_defensa[key], esperados)

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
