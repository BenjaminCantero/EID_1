import tkinter as tk
from tkinter import filedialog, messagebox

from core.log_service import export_logs, get_log_entries
from ui.componentes import (
    BG_PRINCIPAL, BG_CARD, BG_HEADER, BG_CANVAS,
    ACENTO, ACENTO_HOVER, TEXTO, TEXTO_DIM, VERDE, BORDE_CARD,
    FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_CODE, FONT_SMALL,
    crear_header, crear_card, crear_status_bar
)


class PanelLogs(tk.Frame):
    def __init__(self, parent, logger):
        super().__init__(parent, bg=BG_PRINCIPAL)
        self.logger = logger
        self._construir_ui()

    def _construir_ui(self):
        # Header
        crear_header(self, "REGISTRO DE EVENTOS Y TRAZABILIDAD", "Logs de auditoría y depuración en tiempo real")

        # Main frame
        main_frame = tk.Frame(self, bg=BG_PRINCIPAL)
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Card for log text area
        card, body = crear_card(main_frame, "Historial de Eventos", "Visualice la trazabilidad detallada de los cálculos y procesos")
        card.pack(fill="both", expand=True, pady=(0, 10))

        self.txt_logs = tk.Text(body, font=FONT_CODE,
                                bg=BG_CANVAS, fg=TEXTO,
                                insertbackground=TEXTO,
                                relief="flat", bd=0,
                                highlightthickness=1, highlightbackground=BORDE_CARD)
        self.txt_logs.pack(fill="both", expand=True)
        self.txt_logs.config(state="disabled")

        # Botones de control
        botones = tk.Frame(body, bg=BG_CARD)
        botones.pack(fill="x", pady=(10, 0))

        btn_refrescar = tk.Button(botones, text="🔄 Refrescar Logs",
                   command=self.refrescar, font=FONT_SUBTITLE,
                   bg=ACENTO, fg=BG_PRINCIPAL, activebackground=ACENTO_HOVER, activeforeground=BG_PRINCIPAL,
                   relief="flat", padx=15, pady=6, cursor="hand2")
        btn_refrescar.pack(side="left", padx=(0, 10))
        
        def on_enter_ref(e):
            btn_refrescar.config(bg=ACENTO_HOVER)
        def on_leave_ref(e):
            btn_refrescar.config(bg=ACENTO)
        btn_refrescar.bind("<Enter>", on_enter_ref)
        btn_refrescar.bind("<Leave>", on_leave_ref)

        btn_exportar = tk.Button(botones, text="📄 Exportar Logs",
                   command=self.exportar_logs, font=FONT_SUBTITLE,
                   bg=VERDE, fg=BG_PRINCIPAL, activebackground="#3ee884", activeforeground=BG_PRINCIPAL,
                   relief="flat", padx=15, pady=6, cursor="hand2")
        btn_exportar.pack(side="left", padx=(0, 10))
        
        def on_enter_exp(e):
            btn_exportar.config(bg="#3ee884")
        def on_leave_exp(e):
            btn_exportar.config(bg=VERDE)
        btn_exportar.bind("<Enter>", on_enter_exp)
        btn_exportar.bind("<Leave>", on_leave_exp)

        btn_limpiar = tk.Button(botones, text="🧹 Limpiar Panel",
                   command=self.limpiar_panel, font=FONT_SUBTITLE,
                   bg=BG_PRINCIPAL, fg=TEXTO, activebackground=BORDE_CARD, activeforeground=TEXTO,
                   relief="flat", padx=15, pady=6, cursor="hand2", highlightthickness=1, highlightbackground=BORDE_CARD)
        btn_limpiar.pack(side="left")
        
        def on_enter_lim(e):
            btn_limpiar.config(bg=BORDE_CARD)
        def on_leave_lim(e):
            btn_limpiar.config(bg=BG_PRINCIPAL)
        btn_limpiar.bind("<Enter>", on_enter_lim)
        btn_limpiar.bind("<Leave>", on_leave_lim)

        # Barra de estado
        _, self.lbl_estado = crear_status_bar(self, "Listo. Presione 'Refrescar Logs' para cargar el historial actual.")

    def refrescar(self):
        registros = get_log_entries()
        self.txt_logs.config(state="normal")
        self.txt_logs.delete("1.0", "end")
        if registros:
            self.txt_logs.insert("end", "\n".join(registros))
        else:
            self.txt_logs.insert("end", "No hay eventos registrados aún.")
        self.txt_logs.config(state="disabled")
        self.txt_logs.see("end")
        self.lbl_estado.config(text=f"✓ Registro actualizado con {len(registros)} líneas de eventos.")
        self.logger.info("Panel de logs refrescado")

    def exportar_logs(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="logs_eid.txt",
            title="Exportar logs a archivo"
        )
        if not path:
            return

        export_logs(path)
        messagebox.showinfo("Exportación completa", f"Logs exportados exitosamente a:\n{path}")
        self.lbl_estado.config(text=f"✓ Logs exportados a: {path}")
        self.logger.info(f"Logs exportados a: {path}")

    def limpiar_panel(self):
        self.txt_logs.config(state="normal")
        self.txt_logs.delete("1.0", "end")
        self.txt_logs.config(state="disabled")
        self.lbl_estado.config(text="Panel de visualización temporalmente vacío.")
        self.logger.info("Panel de logs limpiado")
