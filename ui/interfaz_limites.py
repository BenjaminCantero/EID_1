
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.rut import validar_rut
from core.limites import (seleccionar_caso, construir_funcion,
                           calcular_limites, tabla_valores, puntos_grafica_limite)

AZUL_OSCURO = "#1a2a4a"
AZUL_MEDIO  = "#2d4a7a"
AZUL_CLARO  = "#4a7abf"
BLANCO      = "#f0f4ff"
AMARILLO    = "#f5c842"
GRIS_TEXTO  = "#e8eaf6"
VERDE       = "#4caf50"
ROJO        = "#e53935"
NARANJA     = "#ff9800"


class PanelLimites(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=AZUL_OSCURO)
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

        self.canvas_lim = tk.Canvas(right, width=320, height=220,
                                     bg="#0d1b2e", relief="flat", bd=2,
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
        es_valido, _, digitos, dv = validar_rut(rut_str)

        if not es_valido:
            messagebox.showerror("Error", "RUT inválido. Verifique e intente de nuevo.")
            return

        self.a = digitos[2]  # a = d3
        caso, razon = seleccionar_caso(digitos[7])
        desc, tramos = construir_funcion(caso, self.a, digitos)
        self.tramos = tramos
        analisis = calcular_limites(tramos)
        self.analisis = analisis

        # Texto análisis
        texto = f"═══ FUNCIÓN GENERADA ═══\n{desc}\n\n"
        texto += f"Punto de análisis: a = d3 = {self.a}\n"
        texto += f"Selección del caso:\n  {razon}\n\n"
        texto += "═══ CÁLCULO DE LÍMITES ═══\n"
        texto += "\n".join(analisis["pasos"]) + "\n"

        self._mostrar_texto(texto)
        self.lbl_funcion.config(text=f"f(x) definida con a={self.a}  |  Caso: {caso}")
        self.lbl_estado.config(text=f"✓ Función generada — Discontinuidad: {analisis['tipo_disc']}", fg=VERDE)

        # Tabla
        for row in self.tabla_tree.get_children():
            self.tabla_tree.delete(row)
        filas = tabla_valores(tramos)
        for x_str, y_str, lado in filas:
            tag = "izq" if lado == "izq" else "der"
            self.tabla_tree.insert("", "end", values=(x_str, y_str, "← izq" if lado == "izq" else "der →"),
                                    tags=(tag,))
        self.tabla_tree.tag_configure("izq", background="#1a3a6a", foreground="#90caf9")
        self.tabla_tree.tag_configure("der", background="#1a4a2a", foreground="#a5d6a7")

        # Gráfica
        self._graficar(tramos, analisis)
        self._limpiar_defensa()

    def _graficar(self, tramos, analisis):
        self.canvas_lim.delete("all")
        w, h = 320, 220
        cx, cy = w // 2, h // 2
        escala = 18

        # Ejes
        self.canvas_lim.create_line(5, cy, w - 5, cy, fill="#3a5a8a", width=1)
        self.canvas_lim.create_line(cx, 5, cx, h - 5, fill="#3a5a8a", width=1)

        for i in range(-8, 9):
            if i == 0:
                continue
            px = cx + i * escala
            py = cy + i * escala
            self.canvas_lim.create_line(px, cy - 3, px, cy + 3, fill="#3a5a8a")
            self.canvas_lim.create_line(cx - 3, py, cx + 3, py, fill="#3a5a8a")

        self.canvas_lim.create_text(w - 12, cy - 8, text="x",
                                     font=("Courier", 7, "bold"), fill="#5a7aaa")
        self.canvas_lim.create_text(cx + 7, 10, text="y",
                                     font=("Courier", 7, "bold"), fill="#5a7aaa")

        # Asíntota vertical si es infinita
        caso = tramos["tipo"]
        a = tramos["a"]
        if caso == "infinita":
            ax = cx + a * escala
            self.canvas_lim.create_line(ax, 5, ax, h - 5,
                                         fill=ROJO, width=1, dash=(4, 4))
            self.canvas_lim.create_text(ax + 5, 15,
                                         text=f"x={a}", font=("Courier", 7), fill=ROJO)

        # Obtener segmentos
        segmentos, pantalla_fn = puntos_grafica_limite(tramos, w, h, rango_x=8)
        for seg in segmentos:
            x1, y1, x2, y2 = seg
            self.canvas_lim.create_line(x1, y1, x2, y2, fill=AMARILLO, width=2)

        # Marcar punto a
        ax_px, ay_px = pantalla_fn(a, 0)
        self.canvas_lim.create_oval(ax_px - 4, ay_px - 4,
                                     ax_px + 4, ay_px + 4,
                                     outline=NARANJA, fill="#0d1b2e", width=2)
        self.canvas_lim.create_text(ax_px, cy + 15,
                                     text=f"a={a}", font=("Courier", 7), fill=NARANJA)

        # Puntos de discontinuidad de salto
        if caso == "salto":
            lim_izq = analisis.get("lim_real_izq", 0)
            lim_der = analisis.get("lim_real_der", 0)
            if isinstance(lim_izq, (int, float)):
                px_i, py_i = pantalla_fn(a, lim_izq)
                self.canvas_lim.create_oval(px_i - 4, py_i - 4, px_i + 4, py_i + 4,
                                             outline=AMARILLO, fill="#0d1b2e", width=2)
            if isinstance(lim_der, (int, float)):
                px_d, py_d = pantalla_fn(a, lim_der)
                self.canvas_lim.create_oval(px_d - 4, py_d - 4, px_d + 4, py_d + 4,
                                             fill=AMARILLO, outline="white", width=1)

        # Etiqueta tipo
        self.canvas_lim.create_text(cx, h - 10,
                                     text=f"Discontinuidad: {analisis['tipo_disc']}",
                                     font=("Helvetica", 8, "bold"), fill=AMARILLO)

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
            return [str(round(float(v), 2)).replace(".0", ""), str(v)]

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
        else:
            messagebox.showinfo("Resultado",
                                f"Respuestas correctas: {correctos}/{total}\n\n"
                                f"Verde = correcto  |  Rojo = revisar")
