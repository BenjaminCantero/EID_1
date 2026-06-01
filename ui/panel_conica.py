"""Panel de cónicas y análisis visual."""

import re
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from core.exceptions import ConicaInvalidaError, RUTInvalidoError
from core.graficas import puntos_grafica
from core.services import analizar_conica
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


class PanelConica(tk.Frame):
    def __init__(self, parent, cambiar_tab_callback=None, logger=None):
        super().__init__(parent, bg=BG_PRINCIPAL)
        self.cambiar_tab = cambiar_tab_callback
        self.logger      = logger
        self.digitos = self.dv = None
        self.A = self.B = self.C = self.D = self.E = 0
        self.tipo      = ""
        self.elementos = {}
        self._ultima_grafica = None
        self._zoom_factor    = 1.0
        self._construir_ui()

    # ─────────────────────────── UI ────────────────────────────────

    def _construir_ui(self):
        crear_header(self, "ANÁLISIS DE SECCIONES CÓNICAS",
                     "Ingrese un RUT chileno válido para generar y analizar una cónica")

        _, self.entry_rut = crear_barra_rut(self, "12.345.678-9", "Analizar", self._procesar)
        self.entry_rut.bind("<Return>", lambda e: self._procesar())

        main_frame = tk.Frame(self, bg=BG_PRINCIPAL)
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        self._construir_columna_izquierda(main_frame)
        self._construir_columna_derecha(main_frame)

        _, self.lbl_estado = crear_status_bar(self, "Ingrese un RUT válido y presione 'Analizar'")

    def _construir_columna_izquierda(self, parent):
        left, body_left = crear_card(parent, "Paso 2: Análisis Matemático",
                                     "Validación, coeficientes y forma canónica")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.txt_pasos = scrolledtext.ScrolledText(
            body_left, font=FONT_CODE, bg=BG_CANVAS, fg=TEXTO,
            insertbackground=TEXTO, relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDE_CARD, state="disabled")
        self.txt_pasos.pack(fill="both", expand=True)

    def _construir_columna_derecha(self, parent):
        right_outer = tk.Frame(parent, bg=BG_PRINCIPAL)
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

        # Tipo de cónica resaltado
        self.lbl_tipo = tk.Label(right, text="", font=FONT_TITLE, bg=BG_PRINCIPAL, fg=VERDE)
        self.lbl_tipo.pack(pady=5)

        self._construir_resumen(right)
        self._construir_defensa(right)

    def _construir_grafica(self, parent):
        card_graph, body_graph = crear_card(parent, "Paso 3: Visualización Gráfica",
                                            "Representación de la cónica en el plano cartesiano")
        card_graph.pack(fill="x", pady=(0, 10))

        gcf = tk.Frame(body_graph, bg=BG_CANVAS, height=310)
        gcf.pack(fill="x", padx=0, pady=(0, 4))
        gcf.pack_propagate(False)
        gcf.columnconfigure(0, weight=1)
        gcf.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(gcf, bg=BG_CANVAS, relief="flat", bd=0,
                                 highlightthickness=1, highlightbackground=BORDE_CARD,
                                 xscrollincrement=10, yscrollincrement=10)
        vbar = ttk.Scrollbar(gcf, orient="vertical",   command=self.canvas.yview)
        hbar = ttk.Scrollbar(gcf, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")

        self.canvas.bind("<Configure>",        self._on_canvas_resize)
        self.canvas.bind("<MouseWheel>",        self._on_graph_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>",  self._on_graph_shift_mousewheel)
        self.canvas.bind("<ButtonPress-1>",     lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>",         lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))

        self.lbl_canvas_info = tk.Label(body_graph, text="Esperando análisis...",
                                         font=FONT_SMALL, bg=BG_CARD, fg=TEXTO_DIM)
        self.lbl_canvas_info.pack(anchor="w")

    def _construir_resumen(self, parent):
        card_resumen, body_resumen = crear_card(parent, "Resultado")
        card_resumen.pack(fill="x", pady=(0, 10))

        self.lbl_resumen_ecuacion = tk.Label(body_resumen, text="Ecuación: —",
                                             font=FONT_CODE, bg=BG_CARD, fg=TEXTO,
                                             anchor="w", justify="left", wraplength=320)
        self.lbl_resumen_ecuacion.pack(fill="x", pady=(2, 0))

        self.lbl_resumen_tipo = tk.Label(body_resumen, text="Tipo: —",
                                          font=FONT_SUBTITLE, bg=BG_CARD, fg=ACENTO, anchor="w")
        self.lbl_resumen_tipo.pack(fill="x", pady=(2, 0))

    def _construir_defensa(self, parent):
        card_defensa, body_defensa = crear_card(parent, "Elementos Geométricos",
                                                "Complete los campos para verificar sus respuestas en la defensa oral")
        card_defensa.pack(fill="x", pady=(0, 10))

        self.entries_elem = {}
        for nombre in ["Centro", "Vértice(s)", "Foco(s)", "Radio / a / b", "Directriz"]:
            fila = tk.Frame(body_defensa, bg=BG_CARD)
            fila.pack(fill="x", pady=3)
            tk.Label(fila, text=f"{nombre}:", width=15, anchor="w",
                     font=FONT_SUBTITLE, bg=BG_CARD, fg=TEXTO).pack(side="left")
            e = tk.Entry(fila, font=FONT_CODE, width=22, bg=ENTRY_BG, fg=ENTRY_FG,
                          insertbackground=ENTRY_FG, relief="flat", bd=0,
                          highlightthickness=1, highlightbackground=BORDE_CARD)
            e.pack(side="left", padx=3, ipady=2)
            self.entries_elem[nombre] = e

        btn_row = tk.Frame(body_defensa, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(10, 0))

        self.btn_verificar = tk.Button(btn_row, text="Verificar Respuestas",
                                        command=self._verificar_elementos,
                                        font=FONT_SUBTITLE, bg=VERDE, fg=BG_PRINCIPAL,
                                        activebackground="#3ee884", activeforeground=BG_PRINCIPAL,
                                        relief="flat", padx=15, pady=6, cursor="hand2")
        self.btn_verificar.pack(side="left")
        _hover(self.btn_verificar, "#3ee884", VERDE)

        self._set_defensa_state(False)

    # ─────────────────────────── LÓGICA ────────────────────────────

    def _procesar(self):
        rut_str = self.entry_rut.get().strip()
        if self.logger:
            self.logger.info(f"PanelCónica: Inicia análisis de RUT '{rut_str}'")

        if not rut_str:
            self.lbl_estado.config(text="Debes ingresar un RUT.", fg=ROJO)
            self._limpiar_resultado()
            if self.logger:
                self.logger.warning("PanelCónica: RUT vacío ingresado")
            return

        try:
            resultado = analizar_conica(rut_str)
        except RUTInvalidoError as e:
            texto = "═══ VALIDACIÓN DEL RUT ═══\n" + "\n".join(getattr(e, "detalles", [str(e)])) + "\n"
            self._mostrar_texto(texto)
            self._reset_labels("RUT inválido")
            if self.logger:
                self.logger.warning(f"PanelCónica: RUT inválido '{rut_str}'")
            return
        except ConicaInvalidaError as e:
            self._mostrar_texto(f"Error en cónica:\n{e}\n")
            self._reset_labels("Cónica inválida")
            if self.logger:
                self.logger.error(f"PanelCónica: Error de cónica para RUT '{rut_str}' — {e}")
            return

        texto = (
            "╔════════════════════════════════════════════════════════╗\n"
            "║           VALIDACIÓN DEL RUT CHILENO                  ║\n"
            "╚════════════════════════════════════════════════════════╝\n\n"
            + "\n".join(resultado.pasos_validacion) + "\n\n"
            "╔════════════════════════════════════════════════════════╗\n"
            "║         CONSTRUCCIÓN DE LA ECUACIÓN GENERAL           ║\n"
            "╚════════════════════════════════════════════════════════╝\n\n"
            + "\n".join(resultado.pasos_coeficientes) + "\n\n"
            "Ajustes aplicados:\n"
            + "".join(f"  ▸ {aj}\n" for aj in resultado.ajustes)
            + f"\n➤ Ecuación general:\n   {resultado.ecuacion_general}\n\n"
            f"➤ Tipo de cónica detectado: {resultado.tipo_conica}\n\n"
            "╔════════════════════════════════════════════════════════╗\n"
            "║             TRANSFORMACIÓN A FORMA CANÓNICA           ║\n"
            "╚════════════════════════════════════════════════════════╝\n\n"
            + "\n".join(resultado.pasos_canonica) + "\n\n"
            f"➤ Forma canónica:\n   {resultado.ecuacion_canonica}\n"
        )
        self._mostrar_texto(texto)

        self.lbl_canvas_info.config(text=f"Cónica generada desde RUT {rut_str}", fg=VERDE)
        self.lbl_tipo.config(text=f"Tipo: {resultado.tipo_conica}", fg=ACENTO)
        self.lbl_resumen_ecuacion.config(text=f"Ecuación: {resultado.ecuacion_general}")
        self.lbl_resumen_tipo.config(text=f"Tipo: {resultado.tipo_conica}")
        self.lbl_estado.config(
            text=f"RUT válido — {resultado.tipo_conica} detectada — Complete los elementos geométricos",
            fg=VERDE)
        if self.logger:
            self.logger.info(f"PanelCónica: RUT válido '{rut_str}' → tipo '{resultado.tipo_conica}'")

        self.elementos = resultado.elementos_geometricos
        for e in self.entries_elem.values():
            e.delete(0, "end")
        self._set_defensa_state(True)

        self._graficar(resultado.A, resultado.B, resultado.C,
                       resultado.D, resultado.E,
                       resultado.tipo_conica, resultado.elementos_geometricos)

    def _reset_labels(self, estado_text):
        """Restablece etiquetas de estado tras un error."""
        self.lbl_estado.config(text=estado_text, fg=ROJO)
        self.lbl_tipo.config(text="")
        self.lbl_resumen_ecuacion.config(text="Ecuación: —")
        self.lbl_resumen_tipo.config(text="Tipo: —")
        self._set_defensa_state(False)

    # ─────────────────────────── GRÁFICA ───────────────────────────

    def _graficar(self, A, B, C, D, E, tipo, elementos):
        self._ultima_grafica = (A, B, C, D, E, tipo, elementos)
        self.canvas.delete("all")

        visible_w = max(450, self.canvas.winfo_width())
        visible_h = max(380, self.canvas.winfo_height())
        draw_w = max(visible_w, int(visible_w * self._zoom_factor))
        draw_h = max(visible_h, int(visible_h * self._zoom_factor))

        # Centro y escala adaptativa
        h, k       = elementos.get("Centro", (0.0, 0.0))
        tamaño_ref = 5.0

        if tipo == "Circunferencia" and elementos.get("Radio", 0) > 0:
            tamaño_ref = elementos["Radio"] * 2.2
        elif tipo == "Elipse" and elementos.get("a (semi-eje mayor)", 0) > 0:
            tamaño_ref = elementos["a (semi-eje mayor)"] * 2.5
        elif tipo == "Hipérbola":
            focos = elementos.get("Focos")
            if focos and len(focos) == 2:
                dist = ((focos[0][0]-focos[1][0])**2 + (focos[0][1]-focos[1][1])**2)**0.5
                tamaño_ref = max(dist * 1.5, 6.0)
        elif tipo == "Parábola":
            tamaño_ref = 8.0

        margen  = 0.85
        escala  = max(5.0, min((draw_w * margen) / (2 * tamaño_ref),
                               (draw_h * margen) / (2 * tamaño_ref)))
        cx, cy  = draw_w // 2, draw_h // 2

        rango_x   = draw_w / (2 * escala)
        rango_y   = draw_h / (2 * escala)
        paso_grid = 5 if tamaño_ref > 20 else (2 if tamaño_ref > 10 else max(1, int(tamaño_ref / 4)))

        ini_x = int(-(rango_x + abs(h))) - 2
        fin_x = int( (rango_x + abs(h))) + 2
        ini_y = int(-(rango_y + abs(k))) - 2
        fin_y = int( (rango_y + abs(k))) + 2

        def mp(x, y):
            return cx + (x - h) * escala, cy - (y - k) * escala

        # Fondo
        self.canvas.create_rectangle(0, 0, draw_w, draw_h, fill=BG_CANVAS, outline="")

        ax_px, _ = mp(0, k)
        _,  ay_py = mp(h, 0)

        # Cuadrícula + ticks + etiquetas (bucle unificado)
        for i in range(ini_x, fin_x + 1, paso_grid):
            px, _ = mp(h + i, k)
            if -10 <= px <= draw_w + 10:
                self.canvas.create_line(px, 0, px, draw_h, fill=BORDE_CARD, width=0.5)
                if i != 0:
                    self.canvas.create_line(px, ay_py - 5, px, ay_py + 5, fill=BORDE_CARD, width=1)
                    self.canvas.create_text(px, ay_py + 14, text=f"{h + i:.3g}",
                                            font=FONT_SMALL, fill=TEXTO_DIM)
        for j in range(ini_y, fin_y + 1, paso_grid):
            _, py = mp(h, k + j)
            if -10 <= py <= draw_h + 10:
                self.canvas.create_line(0, py, draw_w, py, fill=BORDE_CARD, width=0.5)
                if j != 0:
                    self.canvas.create_line(ax_px - 5, py, ax_px + 5, py, fill=BORDE_CARD, width=1)
                    self.canvas.create_text(ax_px - 16, py, text=f"{k + j:.3g}",
                                            font=FONT_SMALL, fill=TEXTO_DIM)

        # Ejes matemáticos
        self.canvas.create_line(0, ay_py, draw_w, ay_py, fill=TEXTO_DIM, width=1.5)
        self.canvas.create_line(ax_px, 0, ax_px, draw_h, fill=TEXTO_DIM, width=1.5)
        self.canvas.create_text(draw_w - 12, ay_py - 12, text="x", font=FONT_SMALL, fill=TEXTO_DIM)
        self.canvas.create_text(ax_px + 12, 10,          text="y", font=FONT_SMALL, fill=TEXTO_DIM)

        # Puntos de la cónica
        puntos = puntos_grafica(A, B, C, D, E, tipo, n=600)
        if not puntos:
            self.canvas.create_text(cx, cy, text="Sin gráfica disponible",
                                    font=FONT_BODY, fill=TEXTO_DIM)
            self.canvas.configure(scrollregion=(0, 0, draw_w, draw_h))
            return

        color_conica = {"Circunferencia": VERDE, "Elipse": "#00ddff",
                        "Hipérbola": "#ff6b9d", "Parábola": ACENTO}.get(tipo, ACENTO)
        mc = 30  # margen clip

        def dibujar_segmentos(pts):
            screen = [mp(x, y) for x, y in pts]
            for i in range(len(screen) - 1):
                x1, y1 = screen[i]
                x2, y2 = screen[i + 1]
                if ((-mc <= x1 <= draw_w + mc and -mc <= y1 <= draw_h + mc) or
                        (-mc <= x2 <= draw_w + mc and -mc <= y2 <= draw_h + mc)):
                    self.canvas.create_line(x1, y1, x2, y2, fill=color_conica, width=2.5,
                                            capstyle="round", joinstyle="round")

        if puntos and isinstance(puntos[0], tuple) and puntos[0][0] == "rama":
            for _, rama_pts in puntos:
                dibujar_segmentos(rama_pts)
        else:
            dibujar_segmentos(puntos)

        self._dibujar_elementos(elementos, mp, draw_w, draw_h)
        self.canvas.configure(scrollregion=(0, 0, draw_w, draw_h))

        if draw_w > visible_w:
            self.canvas.xview_moveto((draw_w - visible_w) / 2 / draw_w)
        if draw_h > visible_h:
            self.canvas.yview_moveto((draw_h - visible_h) / 2 / draw_h)

    def _dibujar_elementos(self, elementos, mp, w, h):
        """Dibuja los elementos geométricos con mejor visibilidad."""
        if "Centro" in elementos:
            px, py = mp(*elementos["Centro"])
            self.canvas.create_oval(px - 6, py - 6, px + 6, py + 6,
                                     fill=ROJO, outline=ENTRY_FG, width=2)
            self.canvas.create_text(px + 15, py - 12, text="Centro",
                                     font=FONT_SMALL, fill=ROJO, anchor="w")

        # Foco único (parábola)
        if "Foco" in elementos:
            px, py = mp(*elementos["Foco"])
            self.canvas.create_oval(px - 5, py - 5, px + 5, py + 5,
                                     fill=NARANJA, outline=ENTRY_FG, width=2)
            self.canvas.create_text(px + 12, py - 8, text="F",
                                     font=FONT_SMALL, fill=NARANJA, anchor="w")

        # Focos múltiples (elipse / hipérbola)
        for i, foco in enumerate(elementos.get("Focos", [])):
            px, py = mp(*foco)
            self.canvas.create_oval(px - 5, py - 5, px + 5, py + 5,
                                     fill=NARANJA, outline=ENTRY_FG, width=2)
            self.canvas.create_text(px + 12, py - 8, text=f"F{i+1}",
                                     font=FONT_SMALL, fill=NARANJA, anchor="w")

        # Vértice único (parábola)
        if "Vértice" in elementos:
            px, py = mp(*elementos["Vértice"])
            self.canvas.create_rectangle(px - 6, py - 6, px + 6, py + 6,
                                          fill=VERDE, outline=ENTRY_FG, width=2)
            self.canvas.create_text(px + 14, py - 12, text="V",
                                     font=FONT_SMALL, fill=VERDE, anchor="w")

        # Vértices múltiples (elipse / hipérbola)
        for i, vertice in enumerate(elementos.get("Vértices", [])):
            px, py = mp(*vertice)
            self.canvas.create_rectangle(px - 6, py - 6, px + 6, py + 6,
                                          fill=VERDE, outline=ENTRY_FG, width=2)
            self.canvas.create_text(px + 14, py - 12, text=f"V{i+1}",
                                     font=FONT_SMALL, fill=VERDE, anchor="w")

    # ─────────────────────────── CALLBACKS ─────────────────────────

    def _on_canvas_resize(self, event):
        if self._ultima_grafica:
            self._graficar(*self._ultima_grafica)

    def _on_graph_mousewheel(self, event):
        if self._ultima_grafica:
            self._zoom_factor = max(0.3, min(self._zoom_factor * (1.15 if event.delta > 0 else 0.87), 5.0))
            self._graficar(*self._ultima_grafica)
        return "break"

    def _on_graph_shift_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def _mostrar_texto(self, texto):
        self.txt_pasos.config(state="normal")
        self.txt_pasos.delete("1.0", "end")
        self.txt_pasos.insert("end", texto)
        self.txt_pasos.config(state="disabled")
        self.txt_pasos.see("1.0")

    def _limpiar_resultado(self):
        self.lbl_tipo.config(text="")
        self.lbl_resumen_ecuacion.config(text="Ecuación: —")
        self.lbl_resumen_tipo.config(text="Tipo: —")
        self._mostrar_texto("")
        self.canvas.delete("all")
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.canvas.create_rectangle(0, 0, cw, ch, fill=BG_CANVAS, outline="")
        self.canvas.create_text(cw // 2, ch // 2, text="Aquí aparecerá la cónica",
                                 font=FONT_BODY, fill=TEXTO_DIM)
        self._set_defensa_state(True)

    def _set_defensa_state(self, enabled):
        state = "normal" if enabled else "disabled"
        bg    = ENTRY_BG if enabled else BG_PRINCIPAL
        fg    = ENTRY_FG if enabled else TEXTO_DIM
        for entry in self.entries_elem.values():
            entry.config(state=state, bg=bg, fg=fg)
            if not enabled:
                entry.delete(0, "end")

    def _limpiar(self):
        self.entry_rut.delete(0, "end")
        self.lbl_estado.config(text="Ingrese un RUT y presione Analizar", fg=TEXTO_DIM)
        self._limpiar_resultado()
        if self.logger:
            self.logger.info("PanelCónica: Limpiar interfaz")

    def _verificar_elementos(self):
        if not self.elementos:
            messagebox.showinfo("Sin datos", "Primero analice un RUT.")
            return
        correctos = total = 0

        def parse_numbers(text):
            tokens = re.findall(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?", text)
            return [float(t) for t in tokens] if tokens else []

        def flatten_expected(value):
            if isinstance(value, (tuple, list)):
                result = []
                for item in value:
                    result.extend(flatten_expected(item))
                return result
            if isinstance(value, (int, float)):
                return [float(value)]
            try:
                return [float(str(value))]
            except (ValueError, TypeError):
                return []

        def matches_expected(value, expected):
            if isinstance(expected, str):
                if expected.lower().replace(" ", "") in value.lower().replace(" ", ""):
                    return True
            exp_nums = flatten_expected(expected)
            inp_nums = parse_numbers(value)
            if not exp_nums or not inp_nums:
                return False
            return any(abs(en - inp) <= max(0.01, abs(en) * 0.02, 1e-6)
                       for en in exp_nums for inp in inp_nums)

        for nombre, entry in self.entries_elem.items():
            val = entry.get().strip()
            if not val:
                continue
            total += 1
            entry.config(bg="#fff9c4", fg=BG_PRINCIPAL)

            # Mapeo nombre → clave en self.elementos
            if "Centro" in nombre and "Centro" in self.elementos:
                esperado_key = "Centro"
            elif "Vértice" in nombre:
                esperado_key = "Vértices" if "Vértices" in self.elementos else (
                               "Vértice"  if "Vértice"  in self.elementos else None)
            elif "Foco" in nombre:
                esperado_key = "Focos" if "Focos" in self.elementos else (
                               "Foco"  if "Foco"  in self.elementos else None)
            elif "Radio" in nombre:
                esperado_key = "Radio" if "Radio" in self.elementos else (
                               "a_b_semi_ejes" if "a (semi-eje mayor)" in self.elementos else None)
            elif "Directriz" in nombre and "Directriz" in self.elementos:
                esperado_key = "Directriz"
            else:
                esperado_key = None

            if esperado_key:
                esperado = (
                    (self.elementos["a (semi-eje mayor)"], self.elementos["b (semi-eje menor)"])
                    if esperado_key == "a_b_semi_ejes"
                    else self.elementos[esperado_key]
                )
                if matches_expected(val, esperado):
                    entry.config(bg="#c8e6c9", fg=BG_PRINCIPAL)
                    correctos += 1
                else:
                    entry.config(bg="#ffcdd2", fg=BG_PRINCIPAL)

        if total == 0:
            messagebox.showinfo("Aviso", "Complete al menos un campo para verificar.")
        else:
            messagebox.showinfo("Resultado",
                                f"Respuestas correctas: {correctos}/{total}\n\n"
                                f"Verde = correcto  |  Rojo = revisar\n"
                                f"Elementos esperados:\n{self.elementos}")
