"""Panel de cónicas y análisis visual."""

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


class PanelConica(tk.Frame):
    def __init__(self, parent, cambiar_tab_callback=None, actualizar_rut_callback=None, logger=None):
        super().__init__(parent, bg=BG_PRINCIPAL)
        self.cambiar_tab = cambiar_tab_callback
        self.actualizar_rut = actualizar_rut_callback
        self.logger = logger
        self.digitos = None
        self.dv = None
        self.A = self.B = self.C = self.D = self.E = 0
        self.tipo = ""
        self.elementos = {}
        self._ultima_grafica = None
        self._zoom_factor = 1.0
        self.lbl_zoom = None
        self._construir_ui()

    def _construir_ui(self):
        # ── Encabezado principal ────────────────────────────
        crear_header(self, "ANÁLISIS DE SECCIONES CÓNICAS", "Ingrese un RUT chileno válido para generar y analizar una cónica")

        # ── Sección de entrada (RUT) ────────────────────────
        _, self.entry_rut = crear_barra_rut(self, "12.345.678-9", "Analizar", self._procesar)
        self.entry_rut.bind("<Return>", lambda e: self._procesar())

        # ── Área principal dividida ──────────────────────────
        main_frame = tk.Frame(self, bg=BG_PRINCIPAL)
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        # ── Columna izquierda: Paso 2 análisis matemático ────
        left, body_left = crear_card(main_frame, "Paso 2: Análisis Matemático", "Validación, coeficientes y forma canónica")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.txt_pasos = scrolledtext.ScrolledText(
            body_left,
            font=FONT_CODE,
            bg=BG_CANVAS, fg=TEXTO,
            insertbackground=TEXTO,
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDE_CARD,
            state="disabled")
        self.txt_pasos.pack(fill="both", expand=True)

        # ── Columna derecha: Paso 3 + Resultado + Defensa ────
        right_outer = tk.Frame(main_frame, bg=BG_PRINCIPAL)
        right_outer.grid(row=0, column=1, sticky="nsew")
        right_outer.rowconfigure(0, weight=1)
        right_outer.columnconfigure(0, weight=1)

        # Canvas scrollable para que los elementos de defensa sean accesibles
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
                                            "Gráfica · resultado · elementos geométricos para la defensa oral")
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

        self.canvas = tk.Canvas(graph_canvas_frame,
                                 bg=BG_CANVAS, relief="flat", bd=0,
                                 highlightthickness=1,
                                 highlightbackground=BORDE_CARD,
                                 xscrollincrement=10,
                                 yscrollincrement=10)
        vbar = ttk.Scrollbar(graph_canvas_frame, orient="vertical", command=self.canvas.yview)
        hbar = ttk.Scrollbar(graph_canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<MouseWheel>", self._on_graph_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_graph_shift_mousewheel)
        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))

        # ── Info compacta: tipo y ecuación ────────────────────
        self.lbl_canvas_info = tk.Label(body_graph, text="Esperando análisis...",
                                         font=FONT_SMALL,
                                         bg=BG_CARD, fg=TEXTO_DIM)
        self.lbl_canvas_info.pack(anchor="w", pady=(2, 0))

        frame_resumen = tk.Frame(body_graph, bg=BG_CARD)
        frame_resumen.pack(fill="x", pady=(2, 0))

        self.lbl_tipo = tk.Label(frame_resumen, text="",
                                  font=FONT_SUBTITLE,
                                  bg=BG_CARD, fg=VERDE)
        self.lbl_tipo.pack(side="left", padx=(0, 10))

        self.lbl_resumen_tipo = tk.Label(frame_resumen, text="",
                                         font=FONT_BODY,
                                         bg=BG_CARD, fg=ACENTO)
        self.lbl_resumen_tipo.pack(side="left")

        self.lbl_resumen_ecuacion = tk.Label(body_graph,
                                             text="",
                                             font=FONT_CODE,
                                             bg=BG_CARD, fg=TEXTO,
                                             anchor="w", justify="left",
                                             wraplength=400)
        self.lbl_resumen_ecuacion.pack(fill="x", pady=(2, 0))

        # ── Separador ─────────────────────────────────────────
        tk.Frame(body_graph, bg=BORDE_CARD, height=1).pack(fill="x", pady=8)

        # ── Elementos geométricos integrados a la gráfica ─────
        tk.Label(body_graph,
                 text="Elementos Geométricos — Complete desde la gráfica para la defensa oral",
                 font=FONT_SUBTITLE, fg=ACENTO, bg=BG_CARD,
                 anchor="w").pack(fill="x", pady=(0, 6))

        campos_grid = tk.Frame(body_graph, bg=BG_CARD)
        campos_grid.pack(fill="x")
        campos_grid.columnconfigure(0, weight=1)
        campos_grid.columnconfigure(1, weight=1)

        self.entries_elem = {}
        for idx, nombre in enumerate(["Centro", "Vértice(s)", "Foco(s)", "Radio / a / b", "Directriz"]):
            row_i = idx // 2
            col_i = idx % 2
            celda = tk.Frame(campos_grid, bg=BG_CARD)
            celda.grid(row=row_i, column=col_i, sticky="ew",
                       padx=(0, 6) if col_i == 0 else 0, pady=3)
            tk.Label(celda, text=f"{nombre}:", width=13, anchor="w",
                     font=FONT_SMALL, bg=BG_CARD, fg=TEXTO).pack(side="left")
            e = tk.Entry(celda, font=FONT_CODE, width=16,
                          bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG,
                          relief="flat", bd=0, highlightthickness=1,
                          highlightbackground=BORDE_CARD)
            e.pack(side="left", padx=3, ipady=2)
            self.entries_elem[nombre] = e

        # Botón verificar
        btn_row = tk.Frame(body_graph, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(10, 0))

        self.btn_verificar = tk.Button(btn_row, text="Verificar Respuestas",
                  command=self._verificar_elementos,
                  font=FONT_SUBTITLE,
                  bg=VERDE, fg=BG_PRINCIPAL, activebackground="#3ee884",
                  activeforeground=BG_PRINCIPAL,
                  relief="flat", padx=15, pady=6, cursor="hand2")
        self.btn_verificar.pack(side="left")

        def on_enter_ver(e):
            self.btn_verificar.config(bg="#3ee884")
        def on_leave_ver(e):
            self.btn_verificar.config(bg=VERDE)
        self.btn_verificar.bind("<Enter>", on_enter_ver)
        self.btn_verificar.bind("<Leave>", on_leave_ver)

        self._set_defensa_state(False)

        # ── Barra de estado ───────────────────────────────────
        _, self.lbl_estado = crear_status_bar(self, "Ingrese un RUT válido y presione 'Analizar'")

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
            texto = "═══ VALIDACIÓN DEL RUT ═══\n"
            texto += "\n".join(getattr(e, 'detalles', [str(e)])) + "\n"
            self._mostrar_texto(texto)
            self.lbl_estado.config(text="RUT inválido", fg=ROJO)
            self.lbl_tipo.config(text="")
            self.lbl_resumen_ecuacion.config(text="Ecuación: —")
            self.lbl_resumen_tipo.config(text="Tipo: —")
            self._set_defensa_state(False)
            if self.logger:
                self.logger.warning(f"PanelCónica: RUT inválido '{rut_str}'")
            return
        except ConicaInvalidaError as e:
            self._mostrar_texto(f"Error en cónica:\n{e}\n")
            self.lbl_estado.config(text="Cónica inválida", fg=ROJO)
            self.lbl_tipo.config(text="")
            self.lbl_resumen_ecuacion.config(text="Ecuación: —")
            self.lbl_resumen_tipo.config(text="Tipo: —")
            self._set_defensa_state(False)
            if self.logger:
                self.logger.error(f"PanelCónica: Error de cónica para RUT '{rut_str}' — {e}")
            return

        texto = "╔════════════════════════════════════════════════════════╗\n"
        texto += "║           VALIDACIÓN DEL RUT CHILENO                  ║\n"
        texto += "╚════════════════════════════════════════════════════════╝\n\n"
        texto += "\n".join(resultado.pasos_validacion) + "\n\n"
        
        texto += "╔════════════════════════════════════════════════════════╗\n"
        texto += "║         CONSTRUCCIÓN DE LA ECUACIÓN GENERAL           ║\n"
        texto += "╚════════════════════════════════════════════════════════╝\n\n"
        texto += "\n".join(resultado.pasos_coeficientes) + "\n\n"
        
        texto += "Ajustes aplicados:\n"
        for aj in resultado.ajustes:
            texto += f"  ▸ {aj}\n"
        texto += "\n"
        texto += f"➤ Ecuación general:\n   {resultado.ecuacion_general}\n\n"
        
        texto += f"➤ Tipo de cónica detectado: {resultado.tipo_conica}\n\n"
        
        texto += "╔════════════════════════════════════════════════════════╗\n"
        texto += "║             TRANSFORMACIÓN A FORMA CANÓNICA           ║\n"
        texto += "╚════════════════════════════════════════════════════════╝\n\n"
        texto += "\n".join(resultado.pasos_canonica) + "\n\n"
        texto += f"➤ Forma canónica:\n   {resultado.ecuacion_canonica}\n"

        self._mostrar_texto(texto)
        
        # Actualizar información del canvas
        self.lbl_canvas_info.config(text=f"Cónica generada desde RUT {rut_str}", fg=VERDE)
        self.lbl_tipo.config(text=f"Tipo: {resultado.tipo_conica}", fg=ACENTO)
        self.lbl_resumen_ecuacion.config(text=f"Ecuación: {resultado.ecuacion_general}")
        self.lbl_resumen_tipo.config(text=f"Tipo: {resultado.tipo_conica}")
        self.lbl_estado.config(text=f"RUT válido — {resultado.tipo_conica} detectada — Complete los elementos geométricos", fg=VERDE)
        if self.logger:
            self.logger.info(f"PanelCónica: RUT válido '{rut_str}' → tipo '{resultado.tipo_conica}'")

        # Actualizar RUT validado en la aplicación principal
        if self.actualizar_rut:
            from core.rut import formatear_rut
            cuerpo_8 = "".join(str(d) for d in resultado.digitos).zfill(8)
            rut_formateado = formatear_rut(cuerpo_8, resultado.dv)
            self.actualizar_rut(rut_formateado)

        self.elementos = resultado.elementos_geometricos
        for e in self.entries_elem.values():
            e.delete(0, "end")
        self._set_defensa_state(True)

        self._graficar(resultado.A, resultado.B,
                       resultado.C, resultado.D,
                       resultado.E, resultado.tipo_conica,
                       resultado.elementos_geometricos)

    def _graficar(self, A, B, C, D, E, tipo, elementos):
        self._ultima_grafica = (A, B, C, D, E, tipo, elementos)
        self.canvas.delete("all")

        # Usar el tamaño real del canvas visible
        visible_w = self.canvas.winfo_width()
        visible_h = self.canvas.winfo_height()
        if visible_w <= 1 or visible_h <= 1:
            visible_w, visible_h = 450, 380

        # Aplicar zoom al tamaño del canvas
        draw_w = int(visible_w * self._zoom_factor)
        draw_h = int(visible_h * self._zoom_factor)
        if draw_w < visible_w:
            draw_w = visible_w
        if draw_h < visible_h:
            draw_h = visible_h

        # ── Determinar centro de la cónica y radio/semiejes para escala adaptativa ──
        h, k = 0.0, 0.0
        tamaño_ref = 5.0  # radio de referencia en unidades matemáticas

        if "Centro" in elementos:
            h, k = elementos["Centro"]

        if tipo == "Circunferencia" and "Radio" in elementos:
            r = elementos["Radio"]
            if r and r > 0:
                tamaño_ref = r * 2.2
        elif tipo == "Elipse":
            a_val = elementos.get("a (semi-eje mayor)", None)
            if a_val and a_val > 0:
                tamaño_ref = a_val * 2.5
        elif tipo == "Hipérbola":
            focos = elementos.get("Focos", None)
            if focos and len(focos) == 2:
                f1, f2 = focos
                dist = ((f1[0]-f2[0])**2 + (f1[1]-f2[1])**2)**0.5
                tamaño_ref = max(dist * 1.5, 6.0)
        elif tipo == "Parábola":
            tamaño_ref = 8.0

        # Escala adaptativa: ajustar para que la cónica ocupe ~70% del canvas
        margen = 0.85
        escala_x = (draw_w * margen) / (2 * tamaño_ref)
        escala_y = (draw_h * margen) / (2 * tamaño_ref)
        escala = min(escala_x, escala_y)
        escala = max(escala, 5.0)  # mínimo 5 px/unidad

        # Centro en pantalla que corresponde al centro matemático (h, k)
        cx = draw_w // 2
        cy = draw_h // 2

        # ── Fondo ──
        self.canvas.create_rectangle(0, 0, draw_w, draw_h, fill="#051020", outline="")

        # ── Calcular rango de unidades visibles ──
        rango_x = draw_w / (2 * escala)
        rango_y = draw_h / (2 * escala)
        paso_grid = max(1, int(tamaño_ref / 4))
        if tamaño_ref > 20:
            paso_grid = 5
        elif tamaño_ref > 10:
            paso_grid = 2

        inicio_xi = int(-(rango_x + abs(h))) - 2
        fin_xi = int(rango_x + abs(h)) + 2
        inicio_yi = int(-(rango_y + abs(k))) - 2
        fin_yi = int(rango_y + abs(k)) + 2

        def mundo_pantalla(x, y):
            px = cx + (x - h) * escala
            py = cy - (y - k) * escala
            return px, py

        # ── Fondo ──
        self.canvas.create_rectangle(0, 0, draw_w, draw_h, fill=BG_CANVAS, outline="")

        # ── Grid ──
        for i in range(inicio_xi, fin_xi + 1, paso_grid):
            px, _ = mundo_pantalla(h + i, k)
            if -10 <= px <= draw_w + 10:
                self.canvas.create_line(px, 0, px, draw_h, fill=BORDE_CARD, width=0.5)

        for j in range(inicio_yi, fin_yi + 1, paso_grid):
            _, py = mundo_pantalla(h, k + j)
            if -10 <= py <= draw_h + 10:
                self.canvas.create_line(0, py, draw_w, py, fill=BORDE_CARD, width=0.5)

        # ── Ejes matemáticos (x=0, y=0) ──
        ax_px, _ = mundo_pantalla(0, k)
        _, ay_py = mundo_pantalla(h, 0)
        # Eje X (y=0)
        self.canvas.create_line(0, ay_py, draw_w, ay_py, fill=TEXTO_DIM, width=1.5)
        # Eje Y (x=0)
        self.canvas.create_line(ax_px, 0, ax_px, draw_h, fill=TEXTO_DIM, width=1.5)

        # ── Marcas y etiquetas en ejes ──
        for i in range(inicio_xi, fin_xi + 1, paso_grid):
            if i == 0:
                continue
            val_x = h + i
            px, _ = mundo_pantalla(val_x, k)
            if -5 <= px <= draw_w + 5:
                self.canvas.create_line(px, ay_py - 5, px, ay_py + 5, fill=BORDE_CARD, width=1)
                self.canvas.create_text(px, ay_py + 14, text=f"{val_x:.3g}",
                                        font=FONT_SMALL, fill=TEXTO_DIM)

        for j in range(inicio_yi, fin_yi + 1, paso_grid):
            if j == 0:
                continue
            val_y = k + j
            _, py = mundo_pantalla(h, val_y)
            if -5 <= py <= draw_h + 5:
                self.canvas.create_line(ax_px - 5, py, ax_px + 5, py, fill=BORDE_CARD, width=1)
                self.canvas.create_text(ax_px - 16, py, text=f"{val_y:.3g}",
                                        font=FONT_SMALL, fill=TEXTO_DIM)

        self.canvas.create_text(draw_w - 12, ay_py - 12, text="x",
                                font=FONT_SMALL, fill=TEXTO_DIM)
        self.canvas.create_text(ax_px + 12, 10, text="y",
                                font=FONT_SMALL, fill=TEXTO_DIM)

        # ── Obtener puntos ──
        puntos = puntos_grafica(A, B, C, D, E, tipo, n=600)
        if not puntos:
            self.canvas.create_text(cx, cy, text="Sin gráfica disponible",
                                    font=FONT_BODY, fill=TEXTO_DIM)
            self.canvas.configure(scrollregion=(0, 0, draw_w, draw_h))
            return

        # Colores según tipo
        colores_tipo = {
            "Circunferencia": VERDE,
            "Elipse": "#00ddff",
            "Hipérbola": "#ff6b9d",
            "Parábola": ACENTO
        }
        color_conica = colores_tipo.get(tipo, ACENTO)

        margen_clip = 30  # px de margen para clipping

        def clip_ok(x1, y1, x2, y2):
            """Acepta segmento si al menos un extremo está dentro del canvas con margen."""
            in1 = (-margen_clip <= x1 <= draw_w + margen_clip and
                   -margen_clip <= y1 <= draw_h + margen_clip)
            in2 = (-margen_clip <= x2 <= draw_w + margen_clip and
                   -margen_clip <= y2 <= draw_h + margen_clip)
            return in1 or in2

        # ── Dibujar cónica ──
        if puntos and isinstance(puntos[0], tuple) and puntos[0][0] == "rama":
            for _, rama_pts in puntos:
                pts_pantalla = [mundo_pantalla(x, y) for x, y in rama_pts]
                for i in range(len(pts_pantalla) - 1):
                    x1, y1 = pts_pantalla[i]
                    x2, y2 = pts_pantalla[i + 1]
                    if clip_ok(x1, y1, x2, y2):
                        self.canvas.create_line(x1, y1, x2, y2,
                                                fill=color_conica, width=2.5,
                                                capstyle="round", joinstyle="round")
        else:
            pts_pantalla = [mundo_pantalla(x, y) for x, y in puntos]
            for i in range(len(pts_pantalla) - 1):
                x1, y1 = pts_pantalla[i]
                x2, y2 = pts_pantalla[i + 1]
                if clip_ok(x1, y1, x2, y2):
                    self.canvas.create_line(x1, y1, x2, y2,
                                            fill=color_conica, width=2.5,
                                            capstyle="round", joinstyle="round")

        # ── Marcar elementos geométricos ──
        self._dibujar_elementos(elementos, mundo_pantalla, draw_w, draw_h)

        # ── Etiqueta de tipo en esquina superior izquierda ───
        self.canvas.create_rectangle(4, 4, 136, 22,
                                      fill=BG_CANVAS, outline=BORDE_CARD, width=1)
        self.canvas.create_text(8, 13, text=f"  {tipo}",
                                 font=FONT_SMALL, fill=ACENTO, anchor="w")

        self.canvas.configure(scrollregion=(0, 0, draw_w, draw_h))

        # Si el canvas virtual es más grande que visible, centrar
        if draw_w > visible_w:
            self.canvas.xview_moveto((draw_w - visible_w) / 2 / draw_w)
        if draw_h > visible_h:
            self.canvas.yview_moveto((draw_h - visible_h) / 2 / draw_h)

    def _on_canvas_resize(self, event):
        if self._ultima_grafica:
            self._graficar(*self._ultima_grafica)

    def _on_graph_mousewheel(self, event):
        self._zoom_graph(event)
        return "break"

    def _on_graph_shift_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    def _zoom_graph(self, event):
        if not self._ultima_grafica:
            return

        factor = 1.15 if event.delta > 0 else 0.87
        self._zoom_factor = max(0.3, min(self._zoom_factor * factor, 5.0))
        if self.lbl_zoom:
            self.lbl_zoom.config(text=f"{int(self._zoom_factor * 100)}%")
        self._graficar(*self._ultima_grafica)

    def _zoom_in(self):
        self._zoom_factor = min(self._zoom_factor * 1.25, 5.0)
        if self.lbl_zoom:
            self.lbl_zoom.config(text=f"{int(self._zoom_factor * 100)}%")
        if self._ultima_grafica:
            self._graficar(*self._ultima_grafica)

    def _zoom_out(self):
        self._zoom_factor = max(self._zoom_factor / 1.25, 0.3)
        if self.lbl_zoom:
            self.lbl_zoom.config(text=f"{int(self._zoom_factor * 100)}%")
        if self._ultima_grafica:
            self._graficar(*self._ultima_grafica)

    def _zoom_reset(self):
        self._zoom_factor = 1.0
        if self.lbl_zoom:
            self.lbl_zoom.config(text="100%")
        if self._ultima_grafica:
            self._graficar(*self._ultima_grafica)

    def _punto_valido(self, x, y, w, h):
        """Verifica si un punto está dentro del canvas con margen."""
        margen = 5
        return -margen <= x <= w + margen and -margen <= y <= h + margen

    def _dibujar_elementos(self, elementos, mundo_pantalla, w, h):
        """Dibuja elementos geométricos con coordenadas visibles."""

        def _lbl(px, py, text, color, offset_x=12, offset_y=-12):
            """Texto con fondo semiopaco para legibilidad."""
            chars = len(text)
            bw = chars * 6 + 6
            bh = 14
            self.canvas.create_rectangle(
                px + offset_x - 2, py + offset_y - bh // 2,
                px + offset_x + bw, py + offset_y + bh // 2,
                fill=BG_CANVAS, outline="", stipple="")
            self.canvas.create_text(px + offset_x, py + offset_y,
                                     text=text, font=FONT_SMALL, fill=color, anchor="w")

        if "Centro" in elementos:
            hx, ky = elementos["Centro"]
            px, py = mundo_pantalla(hx, ky)
            self.canvas.create_oval(px - 7, py - 7, px + 7, py + 7,
                                     fill=ROJO, outline="#ffffff", width=2)
            _lbl(px, py, f"C ({hx:.3g}, {ky:.3g})", ROJO)

        if "Foco" in elementos:
            fx, fy = elementos["Foco"]
            px, py = mundo_pantalla(fx, fy)
            self.canvas.create_oval(px - 5, py - 5, px + 5, py + 5,
                                     fill=NARANJA, outline="#ffffff", width=2)
            _lbl(px, py, f"F ({fx:.3g}, {fy:.3g})", NARANJA)

        if "Focos" in elementos:
            offsets = [(12, -14), (12, 6)]
            for i, foco in enumerate(elementos["Focos"]):
                fx, fy = foco
                px, py = mundo_pantalla(fx, fy)
                self.canvas.create_oval(px - 6, py - 6, px + 6, py + 6,
                                         fill=NARANJA, outline="#ffffff", width=2)
                ox, oy = offsets[i % 2]
                _lbl(px, py, f"F{i+1} ({fx:.3g}, {fy:.3g})", NARANJA, ox, oy)

        if "Vértice" in elementos:
            vx, vy = elementos["Vértice"]
            px, py = mundo_pantalla(vx, vy)
            self.canvas.create_rectangle(px - 6, py - 6, px + 6, py + 6,
                                          fill=VERDE, outline="#ffffff", width=2)
            _lbl(px, py, f"V ({vx:.3g}, {vy:.3g})", VERDE)

        if "Vértices" in elementos:
            offsets = [(12, -14), (12, 6)]
            for i, vertice in enumerate(elementos["Vértices"]):
                vx, vy = vertice
                px, py = mundo_pantalla(vx, vy)
                self.canvas.create_rectangle(px - 6, py - 6, px + 6, py + 6,
                                              fill=VERDE, outline="#ffffff", width=2)
                ox, oy = offsets[i % 2]
                _lbl(px, py, f"V{i+1} ({vx:.3g}, {vy:.3g})", VERDE, ox, oy)

        if "Radio" in elementos:
            r = elementos["Radio"]
            if "Centro" in elementos:
                hx, ky = elementos["Centro"]
                px, py = mundo_pantalla(hx, ky)
                self.canvas.create_text(px + 4, py + 16,
                                         text=f"r = {r:.3g}",
                                         font=FONT_SMALL, fill=ROJO, anchor="w")

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
        # Canvas con fondo oscuro
        self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), 
                                      self.canvas.winfo_height(), fill=BG_CANVAS, outline="")
        self.canvas.create_text(self.canvas.winfo_width() // 2, 
                                 self.canvas.winfo_height() // 2,
                                 text="Aquí aparecerá la cónica",
                                 font=FONT_BODY, fill=TEXTO_DIM)
        self._set_defensa_state(True)

    def _set_defensa_state(self, enabled):
        state = "normal" if enabled else "disabled"
        bg = ENTRY_BG if enabled else BG_PRINCIPAL
        fg = ENTRY_FG if enabled else TEXTO_DIM
        for entry in self.entries_elem.values():
            entry.config(state=state, bg=bg, fg=fg)
        if not enabled:
            for entry in self.entries_elem.values():
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
        correctos = 0
        total = 0

        import re

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
                normalized_value = value.lower().replace(" ", "")
                normalized_expected = expected.lower().replace(" ", "")
                if normalized_expected in normalized_value:
                    return True
            expected_numbers = flatten_expected(expected)
            input_numbers = parse_numbers(value)
            if not expected_numbers or not input_numbers:
                return False
            for exp_num in expected_numbers:
                tol = max(0.01, abs(exp_num) * 0.02, 1e-6)
                if any(abs(exp_num - inp) <= tol for inp in input_numbers):
                    return True
            return False

        for nombre, entry in self.entries_elem.items():
            val = entry.get().strip()
            if not val:
                continue
            total += 1
            entry.config(bg="#fff9c4", fg=BG_PRINCIPAL)  # amarillo neutro por defecto

            esperado_key = None
            if "Centro" in nombre and "Centro" in self.elementos:
                esperado_key = "Centro"
            elif "Vértice" in nombre:
                if "Vértices" in self.elementos:
                    esperado_key = "Vértices"
                elif "Vértice" in self.elementos:
                    esperado_key = "Vértice"
            elif "Foco" in nombre:
                if "Focos" in self.elementos:
                    esperado_key = "Focos"
                elif "Foco" in self.elementos:
                    esperado_key = "Foco"
            elif "Radio" in nombre:
                if "Radio" in self.elementos:
                    esperado_key = "Radio"
                elif "a (semi-eje mayor)" in self.elementos and "b (semi-eje menor)" in self.elementos:
                    esperado_key = "a_b_semi_ejes"
            elif "Directriz" in nombre and "Directriz" in self.elementos:
                esperado_key = "Directriz"

            if esperado_key:
                if esperado_key == "a_b_semi_ejes":
                    esperado = (self.elementos["a (semi-eje mayor)"], self.elementos["b (semi-eje menor)"])
                else:
                    esperado = self.elementos[esperado_key]

                if matches_expected(val, esperado):
                    entry.config(bg="#c8e6c9", fg=BG_PRINCIPAL)  # verde
                    correctos += 1
                else:
                    entry.config(bg="#ffcdd2", fg=BG_PRINCIPAL)  # rojo

        if total == 0:
            messagebox.showinfo("Aviso", "Complete al menos un campo para verificar.")
        else:
            messagebox.showinfo("Resultado",
                                f"Respuestas correctas: {correctos}/{total}\n\n"
                                f"Verde = correcto  |  Rojo = revisar\n"
                                f"Elementos esperados:\n{self.elementos}")
