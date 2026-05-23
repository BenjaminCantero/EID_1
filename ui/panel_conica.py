"""Panel de cónicas y análisis visual."""

import tkinter as tk
from tkinter import messagebox, scrolledtext

from core.exceptions import ConicaInvalidaError, RUTInvalidoError
from core.graficas import puntos_grafica
from core.services import analizar_conica
from ui.componentes import (AZUL_OSCURO, AZUL_MEDIO, AZUL_CLARO,
                            BLANCO, AMARILLO, GRIS_TEXTO, VERDE,
                            ROJO, NARANJA)


class PanelConica(tk.Frame):
    def __init__(self, parent, cambiar_tab_callback=None, logger=None):
        super().__init__(parent, bg=AZUL_OSCURO)
        self.cambiar_tab = cambiar_tab_callback
        self.logger = logger
        self.digitos = None
        self.dv = None
        self.A = self.B = self.C = self.D = self.E = 0
        self.tipo = ""
        self.elementos = {}
        self._construir_ui()

    def _construir_ui(self):
        # ── Título ──────────────────────────────────────────
        tk.Label(self, text="Análisis de Secciones Cónicas",
                 font=("Helvetica", 16, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(pady=(15, 5))
        tk.Label(self, text="Ingresa tu RUT para generar la cónica automáticamente.",
                 font=("Helvetica", 10), bg=AZUL_OSCURO, fg=GRIS_TEXTO).pack()
        tk.Label(self, text="MAT1186 · UCT · 2026",
                 font=("Helvetica", 9), bg=AZUL_OSCURO, fg=GRIS_TEXTO).pack(pady=(0, 10))

        # ── Entrada RUT ──────────────────────────────────────
        frame_rut = tk.Frame(self, bg=AZUL_MEDIO, padx=15, pady=10)
        frame_rut.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(frame_rut, text="Ingrese RUT chileno:",
                 font=("Helvetica", 11, "bold"),
                 bg=AZUL_MEDIO, fg=BLANCO).grid(row=0, column=0, sticky="w")

        self.entry_rut = tk.Entry(frame_rut, font=("Courier", 13),
                                   width=18, bg=BLANCO, fg=AZUL_OSCURO,
                                   insertbackground=AZUL_OSCURO,
                                   relief="flat", bd=3)
        self.entry_rut.grid(row=0, column=1, padx=10)
        self.entry_rut.insert(0, "12.345.678-9")
        self.entry_rut.bind("<Return>", lambda e: self._procesar())

        tk.Label(frame_rut, text="(formato: 12.345.678-9)",
                 font=("Helvetica", 8), bg=AZUL_MEDIO, fg=GRIS_TEXTO).grid(row=1, column=1, sticky="w")

        btn_frame = tk.Frame(frame_rut, bg=AZUL_MEDIO)
        btn_frame.grid(row=0, column=2, padx=5)

        tk.Button(btn_frame, text="▶  Analizar", command=self._procesar,
                  font=("Helvetica", 11, "bold"),
                  bg=AMARILLO, fg=AZUL_OSCURO,
                  relief="flat", padx=12, pady=5,
                  cursor="hand2").pack(side="left")
        tk.Button(btn_frame, text="🗑 Limpiar", command=self._limpiar,
                  font=("Helvetica", 10),
                  bg=AZUL_MEDIO, fg=BLANCO,
                  relief="flat", padx=10, pady=5,
                  cursor="hand2").pack(side="left", padx=(6, 0))

        # ── Área principal dividida ──────────────────────────
        main_frame = tk.Frame(self, bg=AZUL_OSCURO)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Columna izquierda: pasos y resultados
        left = tk.Frame(main_frame, bg=AZUL_OSCURO)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Columna derecha: gráfica + elementos
        right = tk.Frame(main_frame, bg=AZUL_OSCURO)
        right.pack(side="right", fill="both", expand=True)

        # ── Texto de pasos ───────────────────────────────────
        tk.Label(left, text="Desarrollo matemático:",
                 font=("Helvetica", 10, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(anchor="w")

        self.txt_pasos = scrolledtext.ScrolledText(
            left, height=18, width=55,
            font=("Courier", 9),
            bg="#0d1b2e", fg=GRIS_TEXTO,
            insertbackground=BLANCO,
            relief="flat", bd=2,
            state="disabled")
        self.txt_pasos.pack(fill="both", expand=True)

        # ── Canvas gráfica ───────────────────────────────────
        tk.Label(right, text="Gráfica:",
                 font=("Helvetica", 10, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(anchor="w")

        self.canvas = tk.Canvas(right, width=380, height=320,
                                 bg="#051020", relief="flat", bd=2,
                                 highlightthickness=1,
                                 highlightbackground=AZUL_CLARO)
        self.canvas.pack()

        # ── Tipo de cónica resaltado ─────────────────────────
        self.lbl_tipo = tk.Label(right, text="",
                                  font=("Helvetica", 13, "bold"),
                                  bg=AZUL_OSCURO, fg=VERDE)
        self.lbl_tipo.pack(pady=3)

        self.frame_resumen = tk.Frame(right, bg="#2e567f", padx=8, pady=8)
        self.frame_resumen.pack(fill="x", pady=(5, 8))
        tk.Label(self.frame_resumen, text="Resumen rápido:",
                 font=("Helvetica", 10, "bold"),
                 bg="#2e567f", fg=AMARILLO).pack(anchor="w")
        self.lbl_resumen_ecuacion = tk.Label(self.frame_resumen,
                                             text="Ecuación: —",
                                             font=("Courier", 9),
                                             bg="#2e567f", fg=GRIS_TEXTO,
                                             anchor="w", justify="left",
                                             wraplength=320)
        self.lbl_resumen_ecuacion.pack(fill="x", pady=(2, 0))
        self.lbl_resumen_tipo = tk.Label(self.frame_resumen,
                                         text="Tipo: —",
                                         font=("Helvetica", 9, "bold"),
                                         bg="#2e567f", fg=BLANCO,
                                         anchor="w")
        self.lbl_resumen_tipo.pack(fill="x", pady=(2, 0))

        # ── Elementos geométricos (campos para defensa oral) ──
        tk.Label(right, text="Elementos geométricos (completar en defensa):",
                 font=("Helvetica", 9, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(anchor="w", pady=(5, 2))

        self.frame_elementos = tk.Frame(right, bg=AZUL_MEDIO, padx=8, pady=8)
        self.frame_elementos.pack(fill="x")

        self.entries_elem = {}
        for nombre in ["Centro", "Vértice(s)", "Foco(s)", "Radio / a / b", "Directriz"]:
            fila = tk.Frame(self.frame_elementos, bg=AZUL_MEDIO)
            fila.pack(fill="x", pady=1)
            tk.Label(fila, text=f"{nombre}:", width=14, anchor="w",
                     font=("Helvetica", 8, "bold"),
                     bg=AZUL_MEDIO, fg=GRIS_TEXTO).pack(side="left")
            e = tk.Entry(fila, font=("Courier", 9), width=22,
                          bg=BLANCO, fg=AZUL_OSCURO, relief="flat", bd=2)
            e.pack(side="left", padx=3)
            self.entries_elem[nombre] = e

        # Botón verificar (para defensa)
        tk.Button(right, text="✔  Verificar respuestas",
                  command=self._verificar_elementos,
                  font=("Helvetica", 9, "bold"),
                  bg=VERDE, fg="white", relief="flat",
                  padx=8, pady=3, cursor="hand2").pack(pady=5)

        self._set_defensa_state(True)

        # ── Barra de estado ───────────────────────────────────
        self.lbl_estado = tk.Label(self, text="Ingrese un RUT y presione Analizar",
                                    font=("Helvetica", 9), bg=AZUL_OSCURO, fg=GRIS_TEXTO)
        self.lbl_estado.pack(pady=5)

    def _procesar(self):
        rut_str = self.entry_rut.get().strip()
        if self.logger:
            self.logger.info(f"PanelCónica: Inicia análisis de RUT '{rut_str}'")

        if not rut_str:
            self.lbl_estado.config(text="❗ Debes ingresar un RUT.", fg=ROJO)
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
            self.lbl_estado.config(text="❌ RUT inválido", fg=ROJO)
            self.lbl_tipo.config(text="")
            self.lbl_resumen_ecuacion.config(text="Ecuación: —")
            self.lbl_resumen_tipo.config(text="Tipo: —")
            self._set_defensa_state(False)
            if self.logger:
                self.logger.warning(f"PanelCónica: RUT inválido '{rut_str}'")
            return
        except ConicaInvalidaError as e:
            self._mostrar_texto(f"❌ Error en cónica:\n{e}\n")
            self.lbl_estado.config(text="❌ Cónica inválida", fg=ROJO)
            self.lbl_tipo.config(text="")
            self.lbl_resumen_ecuacion.config(text="Ecuación: —")
            self.lbl_resumen_tipo.config(text="Tipo: —")
            self._set_defensa_state(False)
            if self.logger:
                self.logger.error(f"PanelCónica: Error de cónica para RUT '{rut_str}' — {e}")
            return

        texto = "═══ VALIDACIÓN DEL RUT ═══\n"
        texto += "\n".join(resultado.pasos_validacion) + "\n\n"
        texto += "═══ CONSTRUCCIÓN DE LA ECUACIÓN ═══\n"
        texto += "\n".join(resultado.pasos_coeficientes) + "\n\n"
        texto += "Ajustes aplicados:\n"
        for aj in resultado.ajustes:
            texto += f"  • {aj}\n"
        texto += "\n"
        texto += f"Ecuación general:\n  {resultado.ecuacion_general}\n\n"
        texto += f"Tipo de cónica: {resultado.tipo_conica}\n\n"
        texto += "═══ FORMA CANÓNICA ═══\n"
        texto += "\n".join(resultado.pasos_canonica) + "\n\n"
        texto += f"Forma canónica: {resultado.ecuacion_canonica}\n"

        self._mostrar_texto(texto)
        self.lbl_tipo.config(text=f"Cónica: {resultado.tipo_conica}", fg=AMARILLO)
        self.lbl_resumen_ecuacion.config(text=f"Ecuación: {resultado.ecuacion_general}")
        self.lbl_resumen_tipo.config(text=f"Tipo: {resultado.tipo_conica}")
        self.lbl_estado.config(text=f"✓ RUT válido — {resultado.tipo_conica} detectada", fg=VERDE)
        if self.logger:
            self.logger.info(f"PanelCónica: RUT válido '{rut_str}' → tipo '{resultado.tipo_conica}'")

        self.elementos = resultado.elementos_geometricos
        for e in self.entries_elem.values():
            e.delete(0, "end")
        self._set_defensa_state(True)

        self._graficar(resultado.A, resultado.B,
                       resultado.C, resultado.D,
                       resultado.E, resultado.tipo_conica,
                       resultado.elementos_geometricos)

    def _graficar(self, A, B, C, D, E, tipo, elementos):
        self.canvas.delete("all")
        # Canvas más grande para mejor visibilidad
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w <= 1:  # Canvas no ha sido renderizado aún
            w, h = 380, 320
        
        cx, cy = w // 2, h // 2
        escala = 24  # Escala ligeramente mayor

        # Fondo más oscuro para contraste
        self.canvas.create_rectangle(0, 0, w, h, fill="#051020", outline="")

        # Ejes con mejor visibilidad
        self.canvas.create_line(10, cy, w - 10, cy, fill="#4a7aaa", width=1.5)
        self.canvas.create_line(cx, 10, cx, h - 10, fill="#4a7aaa", width=1.5)

        # Grid sutil para mejor orientación
        for i in range(-8, 9):
            if i == 0:
                continue
            px = cx + i * escala
            py = cy + i * escala
            # Grid de fondo muy sutil
            self.canvas.create_line(px, 10, px, h - 10, fill="#1a2f4a", width=0.5)
            self.canvas.create_line(10, py, w - 10, py, fill="#1a2f4a", width=0.5)

        # Marcas en ejes con mejor contraste
        for i in range(-8, 9):
            if i == 0:
                continue
            px = cx + i * escala
            py = cy + i * escala
            # Marcas más largas
            self.canvas.create_line(px, cy - 5, px, cy + 5, fill="#6a9aaa", width=1)
            self.canvas.create_line(cx - 5, py, cx + 5, py, fill="#6a9aaa", width=1)
            if i % 2 == 0:
                self.canvas.create_text(px, cy + 14, text=str(i),
                                         font=("Courier", 7, "bold"), fill="#8aaaaa")
                self.canvas.create_text(cx - 14, py, text=str(-i),
                                         font=("Courier", 7, "bold"), fill="#8aaaaa")

        self.canvas.create_text(w - 12, cy - 15, text="x",
                                 font=("Courier", 10, "bold"), fill="#6a9aaa")
        self.canvas.create_text(cx + 12, 12, text="y",
                                 font=("Courier", 10, "bold"), fill="#6a9aaa")

        # Obtener puntos
        puntos = puntos_grafica(A, B, C, D, E, tipo, n=500)  # Más puntos
        if not puntos:
            self.canvas.create_text(cx, cy, text="Sin gráfica disponible",
                                     font=("Helvetica", 11), fill="#6a8aaa")
            return

        def mundo_pantalla(x, y):
            px = cx + x * escala
            py = cy - y * escala
            return px, py

        # Colores mejorados según tipo de cónica
        colores_tipo = {
            "Circunferencia": "#00ff88",    # Verde brillante
            "Elipse": "#00ddff",             # Cian brillante
            "Hipérbola": "#ff6b9d",          # Rosa/magenta
            "Parábola": "#ffdd44"            # Amarillo brillante
        }
        color_conica = colores_tipo.get(tipo, AMARILLO)

        # Dibujar cónica con mayor grosor y suavidad
        if puntos and isinstance(puntos[0], tuple) and len(puntos[0]) == 2 and puntos[0][0] == "rama":
            # Hipérbola con dos ramas
            for _, rama_pts in puntos:
                pts_pantalla = [mundo_pantalla(x, y) for x, y in rama_pts]
                # Dibujar con múltiples líneas para efecto de grosor
                for i in range(len(pts_pantalla) - 1):
                    x1, y1 = pts_pantalla[i]
                    x2, y2 = pts_pantalla[i + 1]
                    # Validar que los puntos están dentro del canvas
                    if self._punto_valido(x1, y1, w, h) and self._punto_valido(x2, y2, w, h):
                        self.canvas.create_line(x1, y1, x2, y2,
                                                 fill=color_conica, width=3, capstyle="round", joinstyle="round")
        else:
            # Circunferencia, Elipse o Parábola
            pts_pantalla = [mundo_pantalla(x, y) for x, y in puntos]
            for i in range(len(pts_pantalla) - 1):
                x1, y1 = pts_pantalla[i]
                x2, y2 = pts_pantalla[i + 1]
                if self._punto_valido(x1, y1, w, h) and self._punto_valido(x2, y2, w, h):
                    self.canvas.create_line(x1, y1, x2, y2,
                                             fill=color_conica, width=3, capstyle="round", joinstyle="round")

        # Marcar elementos geométricos con mejor visibilidad
        self._dibujar_elementos(elementos, mundo_pantalla, w, h)

        # Leyenda mejorada
        self.canvas.create_text(w // 2, h - 8, text=tipo,
                                 font=("Helvetica", 10, "bold"), fill=color_conica)

    def _punto_valido(self, x, y, w, h):
        """Verifica si un punto está dentro del canvas con margen."""
        margen = 5
        return -margen <= x <= w + margen and -margen <= y <= h + margen

    def _dibujar_elementos(self, elementos, mundo_pantalla, w, h):
        """Dibuja los elementos geométricos con mejor visibilidad."""
        # Centro (punto de referencia)
        if "Centro" in elementos:
            hx, ky = elementos["Centro"]
            px, py = mundo_pantalla(hx, ky)
            # Círculo relleno más grande
            self.canvas.create_oval(px - 6, py - 6, px + 6, py + 6,
                                     fill=ROJO, outline=BLANCO, width=2)
            # Etiqueta con fondo
            self.canvas.create_text(px + 15, py - 12,
                                     text=f"Centro",
                                     font=("Courier", 8, "bold"), fill=ROJO,
                                     anchor="w")

        # Foco único (para parábola)
        if "Foco" in elementos:
            fx, fy = elementos["Foco"]
            px, py = mundo_pantalla(fx, fy)
            self.canvas.create_oval(px - 5, py - 5, px + 5, py + 5,
                                     fill=NARANJA, outline=BLANCO, width=2)
            self.canvas.create_text(px + 12, py - 8,
                                     text="F",
                                     font=("Courier", 8, "bold"), fill=NARANJA,
                                     anchor="w")

        # Focos múltiples (para elipse e hipérbola)
        if "Focos" in elementos:
            for i, foco in enumerate(elementos["Focos"]):
                fx, fy = foco
                px, py = mundo_pantalla(fx, fy)
                self.canvas.create_oval(px - 5, py - 5, px + 5, py + 5,
                                         fill=NARANJA, outline=BLANCO, width=2)
                label = f"F{i+1}"
                self.canvas.create_text(px + 12, py - 8,
                                         text=label,
                                         font=("Courier", 8, "bold"), fill=NARANJA,
                                         anchor="w")

        # Vértices
        if "Vértice" in elementos:
            vx, vy = elementos["Vértice"]
            px, py = mundo_pantalla(vx, vy)
            # Cuadrado más grande
            self.canvas.create_rectangle(px - 6, py - 6, px + 6, py + 6,
                                          fill=VERDE, outline=BLANCO, width=2)
            self.canvas.create_text(px + 14, py - 12,
                                     text="V",
                                     font=("Courier", 8, "bold"), fill=VERDE,
                                     anchor="w")

        if "Vértices" in elementos:
            for i, vertice in enumerate(elementos["Vértices"]):
                vx, vy = vertice
                px, py = mundo_pantalla(vx, vy)
                self.canvas.create_rectangle(px - 6, py - 6, px + 6, py + 6,
                                              fill=VERDE, outline=BLANCO, width=2)
                label = f"V{i+1}"
                self.canvas.create_text(px + 14, py - 12,
                                         text=label,
                                         font=("Courier", 8, "bold"), fill=VERDE,
                                         anchor="w")

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
                                      self.canvas.winfo_height(), fill="#051020")
        self.canvas.create_text(self.canvas.winfo_width() // 2, 
                                 self.canvas.winfo_height() // 2,
                                 text="Aquí aparecerá la cónica",
                                 font=("Helvetica", 11), fill="#7a92c6")
        self._set_defensa_state(True)

    def _set_defensa_state(self, enabled):
        state = "normal" if enabled else "disabled"
        bg = BLANCO if enabled else "#d0d7eb"
        for entry in self.entries_elem.values():
            entry.config(state=state, bg=bg)
        if not enabled:
            for entry in self.entries_elem.values():
                entry.delete(0, "end")

    def _limpiar(self):
        self.entry_rut.delete(0, "end")
        self.lbl_estado.config(text="Ingrese un RUT y presione Analizar", fg=GRIS_TEXTO)
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
            entry.config(bg="#fff9c4")  # amarillo neutro por defecto

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
                    entry.config(bg="#c8e6c9")  # verde
                    correctos += 1
                else:
                    entry.config(bg="#ffcdd2")  # rojo

        if total == 0:
            messagebox.showinfo("Aviso", "Complete al menos un campo para verificar.")
        else:
            messagebox.showinfo("Resultado",
                                f"Respuestas correctas: {correctos}/{total}\n\n"
                                f"Verde = correcto  |  Rojo = revisar\n"
                                f"Elementos esperados:\n{self.elementos}")
