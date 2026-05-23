
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
        self._construir_ui()

    def _construir_ui(self):
        # ── Título ───────────────────────────────────────────
        tk.Label(self, text="Análisis de Funciones por Tramos y Límites",
                 font=("Helvetica", 14, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(pady=(12, 3))
        tk.Label(self, text="MAT1186 · Fase 6",
                 font=("Helvetica", 9), bg=AZUL_OSCURO, fg=GRIS_TEXTO).pack()

        # ── Entrada RUT ──────────────────────────────────────
        frame_rut = tk.Frame(self, bg=AZUL_MEDIO, padx=15, pady=8)
        frame_rut.pack(fill="x", padx=20, pady=(10, 5))

        tk.Label(frame_rut, text="RUT:",
                 font=("Helvetica", 11, "bold"),
                 bg=AZUL_MEDIO, fg=BLANCO).grid(row=0, column=0, sticky="w")

        self.entry_rut = tk.Entry(frame_rut, font=("Courier", 12),
                                   width=16, bg=BLANCO, fg=AZUL_OSCURO,
                                   relief="flat", bd=3)
        self.entry_rut.grid(row=0, column=1, padx=8)
        self.entry_rut.insert(0, "12.345.678-9")
        self.entry_rut.bind("<Return>", lambda e: self._procesar())

        tk.Button(frame_rut, text="▶  Generar función",
                  command=self._procesar,
                  font=("Helvetica", 10, "bold"),
                  bg=AMARILLO, fg=AZUL_OSCURO,
                  relief="flat", padx=10, pady=4,
                  cursor="hand2").grid(row=0, column=2, padx=5)

        # ── Cuerpo principal ──────────────────────────────────
        body = tk.Frame(self, bg=AZUL_OSCURO)
        body.pack(fill="both", expand=True, padx=20, pady=5)

        left = tk.Frame(body, bg=AZUL_OSCURO)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right = tk.Frame(body, bg=AZUL_OSCURO)
        right.pack(side="right", fill="both", expand=True)

        # ── Texto de análisis matemático ─────────────────────
        tk.Label(left, text="Análisis matemático:",
                 font=("Helvetica", 10, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(anchor="w")

        self.txt_analisis = scrolledtext.ScrolledText(
            left, height=14, width=50,
            font=("Courier", 9),
            bg="#0d1b2e", fg=GRIS_TEXTO,
            insertbackground=BLANCO,
            relief="flat", bd=2,
            state="disabled")
        self.txt_analisis.pack(fill="both", expand=True)

        # ── Tabla de valores ─────────────────────────────────
        tk.Label(left, text="Tabla de valores cercanos al punto a:",
                 font=("Helvetica", 9, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(anchor="w", pady=(8, 2))

        frame_tabla = tk.Frame(left, bg=AZUL_MEDIO)
        frame_tabla.pack(fill="x")

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
        tk.Label(right, text="Gráfica de la función:",
                 font=("Helvetica", 10, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(anchor="w")

        self.canvas_lim = tk.Canvas(right, width=380, height=280,
                                     bg="#051020", relief="flat", bd=2,
                                     highlightthickness=1,
                                     highlightbackground=AZUL_CLARO)
        self.canvas_lim.pack()

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

        frame_defensa = tk.Frame(right, bg=AZUL_MEDIO, padx=8, pady=8)
        frame_defensa.pack(fill="x")

        campos = [
            "Límite por izquierda",
            "Límite por derecha",
            "¿Existe el límite? (sí/no)",
            "f(a) = ",
            "¿Es continua? (sí/no)",
            "Tipo de discontinuidad",
            "Justificación",
        ]
        self.entries_defensa = {}
        for campo in campos:
            fila = tk.Frame(frame_defensa, bg=AZUL_MEDIO)
            fila.pack(fill="x", pady=1)
            tk.Label(fila, text=campo + ":", width=22, anchor="w",
                     font=("Helvetica", 7, "bold"),
                     bg=AZUL_MEDIO, fg=GRIS_TEXTO).pack(side="left")
            e = tk.Entry(fila, font=("Courier", 8), width=18,
                          bg=BLANCO, fg=AZUL_OSCURO, relief="flat", bd=2)
            e.pack(side="left", padx=2)
            self.entries_defensa[campo] = e

        # Botones defensa
        btn_row = tk.Frame(right, bg=AZUL_OSCURO)
        btn_row.pack(pady=4)

        tk.Button(btn_row, text="✔ Verificar",
                  command=self._verificar_defensa,
                  font=("Helvetica", 9, "bold"),
                  bg=VERDE, fg="white", relief="flat",
                  padx=8, pady=3, cursor="hand2").pack(side="left", padx=4)

        tk.Button(btn_row, text="🗑 Limpiar",
                  command=self._limpiar_defensa,
                  font=("Helvetica", 9),
                  bg=AZUL_MEDIO, fg=GRIS_TEXTO, relief="flat",
                  padx=8, pady=3, cursor="hand2").pack(side="left", padx=4)

        # Estado
        self.lbl_estado = tk.Label(self, text="Ingrese un RUT y presione Generar función",
                                    font=("Helvetica", 9),
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

        texto = f"═══ FUNCIÓN GENERADA ═══\n{resultado.descripcion_funcion}\n\n"
        texto += f"Punto de análisis: a = {resultado.a}\n"
        texto += f"Selección del caso:\n  {resultado.razon_caso}\n\n"
        texto += "═══ CÁLCULO DE LÍMITES ═══\n"
        texto += "\n".join(resultado.pasos_limites) + "\n"

        self._mostrar_texto(texto)
        self.lbl_funcion.config(text=f"f(x) definida con a={resultado.a}  |  Caso: {resultado.caso_tipo}")
        self.lbl_estado.config(text=f"✓ Función generada — Discontinuidad: {resultado.tipo_discontinuidad}", fg=VERDE)
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
        self.canvas_lim.delete("all")
        w, h = self.canvas_lim.winfo_width(), self.canvas_lim.winfo_height()
        if w <= 1:  # Canvas no ha sido renderizado aún
            w, h = 380, 280
        
        cx, cy = w // 2, h // 2
        escala = 20  # Escala ligeramente mayor

        # Fondo más oscuro para contraste
        self.canvas_lim.create_rectangle(0, 0, w, h, fill="#051020", outline="")

        # Grid sutil para mejor orientación
        for i in range(-10, 11):
            if i == 0:
                continue
            px = cx + i * escala
            py = cy + i * escala
            # Grid de fondo muy sutil
            self.canvas_lim.create_line(px, 10, px, h - 10, fill="#1a2f4a", width=0.5)
            self.canvas_lim.create_line(10, py, w - 10, py, fill="#1a2f4a", width=0.5)

        # Ejes con mejor visibilidad
        self.canvas_lim.create_line(10, cy, w - 10, cy, fill="#4a7aaa", width=1.5)
        self.canvas_lim.create_line(cx, 10, cx, h - 10, fill="#4a7aaa", width=1.5)

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

        self.canvas_lim.create_text(w - 12, cy - 15, text="x",
                                     font=("Courier", 10, "bold"), fill="#6a9aaa")
        self.canvas_lim.create_text(cx + 12, 12, text="y",
                                     font=("Courier", 10, "bold"), fill="#6a9aaa")

        # Asíntota vertical si es infinita (más visible)
        caso = tramos["tipo"]
        a = tramos["a"]
        if caso == "infinita":
            ax = cx + a * escala
            # Asíntota punteada roja más gruesa
            self.canvas_lim.create_line(ax, 5, ax, h - 5,
                                         fill="#ff6b6b", width=2, dash=(6, 4))
            self.canvas_lim.create_text(ax + 8, 18,
                                         text=f"x={a}", font=("Courier", 8, "bold"), fill="#ff6b6b")

        # Obtener segmentos
        segmentos, pantalla_fn = puntos_grafica_limite(tramos, w, h, rango_x=8)
        
        # Dibujar función con grosor mejorado y colores vibrantes
        for seg in segmentos:
            x1, y1, x2, y2 = seg
            # Validar que los puntos están dentro del canvas
            if (10 <= x1 <= w - 10 and 10 <= y1 <= h - 10 and
                10 <= x2 <= w - 10 and 10 <= y2 <= h - 10):
                self.canvas_lim.create_line(x1, y1, x2, y2, 
                                            fill="#00ffaa", width=3, 
                                            capstyle="round", joinstyle="round")

        # Marcar visualmente la posición x = a en el eje (etiqueta)
        self.canvas_lim.create_text(cx + a * escala, h - 20,
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
        self.canvas_lim.create_text(w // 2, h - 12,
                                     text=f"Discontinuidad: {getattr(analisis, 'tipo_discontinuidad', '')}",
                                     font=("Helvetica", 10, "bold"), fill="#00ffaa")

    def _mostrar_texto(self, texto):
        self.txt_analisis.config(state="normal")
        self.txt_analisis.delete("1.0", "end")
        self.txt_analisis.insert("end", texto)
        self.txt_analisis.config(state="disabled")
        self.txt_analisis.see("1.0")

    def _limpiar_defensa(self):
        for e in self.entries_defensa.values():
            e.delete(0, "end")
            e.config(bg=BLANCO)

    def _verificar_defensa(self):
        if not self.analisis:
            messagebox.showinfo("Aviso", "Primero genere una función.")
            return

        a = self.analisis
        correctos = 0
        total = 0

        def chk(entry, esperado_str):
            nonlocal correctos, total
            val = entry.get().strip().lower().replace(" ", "")
            if not val:
                return
            total += 1
            if any(e in val for e in esperado_str):
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

        lim_izq_entry = self.entries_defensa["Límite por izquierda"]
        lim_der_entry = self.entries_defensa["Límite por derecha"]
        existe_entry = self.entries_defensa["¿Existe el límite? (sí/no)"]
        fa_entry = self.entries_defensa["f(a) = "]
        cont_entry = self.entries_defensa["¿Es continua? (sí/no)"]
        tipo_entry = self.entries_defensa["Tipo de discontinuidad"]

        # Límite izquierda
        liz = a.get("lim_real_izq", a.get("lim_valor"))
        chk(lim_izq_entry, num_str(liz) + ["∞", "-∞", "+∞", "infinito"])

        # Límite derecha
        lde = a.get("lim_real_der", a.get("lim_valor"))
        chk(lim_der_entry, num_str(lde) + ["∞", "-∞", "+∞", "infinito"])

        # Existe
        existe_ok = ["sí", "si", "s", "yes", "existe"] if a["lim_existe"] else ["no", "n", "noexiste"]
        chk(existe_entry, existe_ok)

        # f(a)
        fa = a.get("f_en_a")
        chk(fa_entry, num_str(fa) + ["nodefinida", "indefinida", "noexiste"])

        # Continua
        cont_ok = ["sí", "si", "s", "yes", "continua"] if a["continua"] else ["no", "n", "nocontinua", "discontinua"]
        chk(cont_entry, cont_ok)

        # Tipo
        tipo = a["tipo_disc"].lower()
        chk(tipo_entry, [tipo, tipo.split()[0]])

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
