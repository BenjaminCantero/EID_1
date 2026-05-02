# ui/interfaz_conica.py
# Módulo de interfaz gráfica para el análisis de cónicas
# Usa únicamente Tkinter (incluida en Python estándar)

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.rut import validar_rut, formatear_rut
from core.conica import (calcular_coeficientes, clasificar_conica,
                          ecuacion_str, forma_canonica, puntos_grafica)


AZUL_OSCURO = "#1a2a4a"
AZUL_MEDIO = "#2d4a7a"
AZUL_CLARO = "#4a7abf"
BLANCO = "#f0f4ff"
AMARILLO = "#f5c842"
GRIS_TEXTO = "#e8eaf6"
VERDE = "#4caf50"
ROJO = "#e53935"
NARANJA = "#ff9800"


class PanelConica(tk.Frame):
    def __init__(self, parent, cambiar_tab_callback=None):
        super().__init__(parent, bg=AZUL_OSCURO)
        self.cambiar_tab = cambiar_tab_callback
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

        self.canvas = tk.Canvas(right, width=340, height=280,
                                 bg="#0d1b2e", relief="flat", bd=2,
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

        self._set_defensa_state(False)

        # ── Barra de estado ───────────────────────────────────
        self.lbl_estado = tk.Label(self, text="Ingrese un RUT y presione Analizar",
                                    font=("Helvetica", 9), bg=AZUL_OSCURO, fg=GRIS_TEXTO)
        self.lbl_estado.pack(pady=5)

    def _procesar(self):
        rut_str = self.entry_rut.get().strip()
        if not rut_str:
            self.lbl_estado.config(text="❗ Debes ingresar un RUT.", fg=ROJO)
            self._limpiar_resultado()
            return

        es_valido, pasos_val, digitos, dv_calc = validar_rut(rut_str)

        texto = "═══ VALIDACIÓN DEL RUT ═══\n"
        texto += "\n".join(pasos_val) + "\n\n"

        if not es_valido:
            self._mostrar_texto(texto)
            self.lbl_estado.config(text="❌ RUT inválido", fg=ROJO)
            self.lbl_tipo.config(text="")
            self.lbl_resumen_ecuacion.config(text="Ecuación: —")
            self.lbl_resumen_tipo.config(text="Tipo: —")
            self._set_defensa_state(False)
            return

        self.digitos = digitos
        self.dv = dv_calc

        # Calcular coeficientes
        A, B, C, D, E, pasos_coef, ajustes = calcular_coeficientes(digitos, dv_calc)
        self.A, self.B, self.C, self.D, self.E = A, B, C, D, E

        texto += "═══ CONSTRUCCIÓN DE LA ECUACIÓN ═══\n"
        texto += "\n".join(pasos_coef) + "\n\n"
        texto += "Ajustes aplicados:\n"
        for aj in ajustes:
            texto += f"  • {aj}\n"
        texto += "\n"

        # Clasificación
        tipo = clasificar_conica(A, B)
        self.tipo = tipo
        eq = ecuacion_str(A, B, C, D, E)
        texto += f"Ecuación general:\n  {eq}\n\n"
        texto += f"Tipo de cónica: {tipo}\n\n"

        # Forma canónica
        canonica, pasos_can, elementos = forma_canonica(A, B, C, D, E, tipo)
        self.elementos = elementos
        texto += "═══ FORMA CANÓNICA ═══\n"
        texto += "\n".join(pasos_can) + "\n\n"
        texto += f"Forma canónica: {canonica}\n"

        self._mostrar_texto(texto)
        self.lbl_tipo.config(text=f"Cónica: {tipo}", fg=AMARILLO)
        self.lbl_resumen_ecuacion.config(text=f"Ecuación: {eq}")
        self.lbl_resumen_tipo.config(text=f"Tipo: {tipo}")
        self.lbl_estado.config(text=f"✓ RUT válido — {tipo} detectada", fg=VERDE)

        # Limpiar campos de defensa
        for e in self.entries_elem.values():
            e.delete(0, "end")
        self._set_defensa_state(True)

        # Graficar
        self._graficar(A, B, C, D, E, tipo, elementos)

    def _graficar(self, A, B, C, D, E, tipo, elementos):
        self.canvas.delete("all")
        w, h = 340, 280
        cx, cy = w // 2, h // 2
        escala = 22

        # Ejes
        self.canvas.create_line(10, cy, w - 10, cy, fill="#3a5a8a", width=1)
        self.canvas.create_line(cx, 10, cx, h - 10, fill="#3a5a8a", width=1)

        # Marcas en ejes
        for i in range(-7, 8):
            if i == 0:
                continue
            px = cx + i * escala
            py = cy + i * escala
            self.canvas.create_line(px, cy - 3, px, cy + 3, fill="#3a5a8a")
            self.canvas.create_line(cx - 3, py, cx + 3, py, fill="#3a5a8a")
            if i % 2 == 0:
                self.canvas.create_text(px, cy + 10, text=str(i),
                                         font=("Courier", 6), fill="#5a7aaa")
                self.canvas.create_text(cx - 12, py, text=str(-i),
                                         font=("Courier", 6), fill="#5a7aaa")

        self.canvas.create_text(w - 15, cy - 10, text="x",
                                 font=("Courier", 8, "bold"), fill="#5a7aaa")
        self.canvas.create_text(cx + 8, 15, text="y",
                                 font=("Courier", 8, "bold"), fill="#5a7aaa")

        # Obtener puntos
        puntos = puntos_grafica(A, B, C, D, E, tipo, n=400)
        if not puntos:
            self.canvas.create_text(cx, cy, text="Sin gráfica disponible",
                                     font=("Helvetica", 10), fill="#888")
            return

        def mundo_pantalla(x, y):
            px = cx + x * escala
            py = cy - y * escala
            return px, py

        color_conica = AMARILLO

        # Detectar si hay ramas de hipérbola
        if puntos and isinstance(puntos[0], tuple) and len(puntos[0]) == 2 and puntos[0][0] == "rama":
            for _, rama_pts in puntos:
                pts_pantalla = [mundo_pantalla(x, y) for x, y in rama_pts]
                for i in range(len(pts_pantalla) - 1):
                    x1, y1 = pts_pantalla[i]
                    x2, y2 = pts_pantalla[i + 1]
                    if (0 <= x1 <= w and 0 <= y1 <= h and
                            0 <= x2 <= w and 0 <= y2 <= h):
                        self.canvas.create_line(x1, y1, x2, y2,
                                                 fill=color_conica, width=2)
        else:
            pts_pantalla = [mundo_pantalla(x, y) for x, y in puntos]
            for i in range(len(pts_pantalla) - 1):
                x1, y1 = pts_pantalla[i]
                x2, y2 = pts_pantalla[i + 1]
                if (0 <= x1 <= w and 0 <= y1 <= h and
                        0 <= x2 <= w and 0 <= y2 <= h):
                    self.canvas.create_line(x1, y1, x2, y2,
                                             fill=color_conica, width=2)

        # Marcar elementos geométricos
        if "Centro" in elementos:
            hx, ky = elementos["Centro"]
            px, py = mundo_pantalla(hx, ky)
            self.canvas.create_oval(px - 4, py - 4, px + 4, py + 4,
                                     fill=ROJO, outline="white")
            self.canvas.create_text(px + 10, py - 10,
                                     text=f"C({hx},{ky})",
                                     font=("Courier", 7), fill=ROJO)

        if "Foco" in elementos:
            fx, fy = elementos["Foco"]
            px, py = mundo_pantalla(fx, fy)
            self.canvas.create_oval(px - 3, py - 3, px + 3, py + 3,
                                     fill=NARANJA, outline="white")

        if "Focos" in elementos:
            for foco in elementos["Focos"]:
                fx, fy = foco
                px, py = mundo_pantalla(fx, fy)
                self.canvas.create_oval(px - 3, py - 3, px + 3, py + 3,
                                         fill=NARANJA, outline="white")

        if "Vértice" in elementos:
            vx, vy = elementos["Vértice"]
            px, py = mundo_pantalla(vx, vy)
            self.canvas.create_rectangle(px - 4, py - 4, px + 4, py + 4,
                                          fill=VERDE, outline="white")

        # Leyenda
        self.canvas.create_text(cx, h - 12, text=tipo,
                                 font=("Helvetica", 8, "bold"), fill=AMARILLO)

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
        self.canvas.create_text(170, 140, text="Aquí aparecerá la cónica",
                                 font=("Helvetica", 10), fill="#7a92c6")
        self._set_defensa_state(False)

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

    def _verificar_elementos(self):
        if not self.elementos:
            messagebox.showinfo("Sin datos", "Primero analice un RUT.")
            return
        correctos = 0
        total = 0
        for nombre, entry in self.entries_elem.items():
            val = entry.get().strip()
            if not val:
                continue
            total += 1
            entry.config(bg="#fff9c4")  # amarillo neutro por defecto
            # Verificación simple: ver si los números del elemento esperado aparecen
            esperado_key = None
            if "Centro" in nombre and "Centro" in self.elementos:
                esperado_key = "Centro"
            elif "Vértice" in nombre and "Vértice" in self.elementos:
                esperado_key = "Vértice"
            elif "Foco" in nombre and ("Foco" in self.elementos or "Focos" in self.elementos):
                esperado_key = "Foco" if "Foco" in self.elementos else "Focos"
            elif "Radio" in nombre and "Radio" in self.elementos:
                esperado_key = "Radio"
            elif "Directriz" in nombre and "Directriz" in self.elementos:
                esperado_key = "Directriz"

            if esperado_key:
                esperado = str(self.elementos[esperado_key])
                num_esp = [s for s in esperado.replace("(", "").replace(")", "")
                          .replace(",", " ").split() if any(c.isdigit() for c in s)]
                num_ing = [s for s in val.replace("(", "").replace(")", "")
                          .replace(",", " ").split() if any(c.isdigit() for c in s)]
                if num_esp and any(n in val for n in num_esp):
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
