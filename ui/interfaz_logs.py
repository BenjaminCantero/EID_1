import tkinter as tk
from tkinter import ttk, filedialog, messagebox

AZUL_OSCURO = "#1a2a4a"
AZUL_MEDIO = "#2d4a7a"
BLANCO = "#f0f4ff"
AMARILLO = "#f5c842"
GRIS_TEXTO = "#e8eaf6"
VERDE = "#4caf50"


class PanelLogs(tk.Frame):
    def __init__(self, parent, logger):
        super().__init__(parent, bg=AZUL_OSCURO)
        self.logger = logger
        self._construir_ui()

    def _construir_ui(self):
        tk.Label(self, text="Registro de eventos y trazabilidad",
                 font=("Helvetica", 15, "bold"),
                 bg=AZUL_OSCURO, fg=AMARILLO).pack(pady=(15, 4))
        tk.Label(self, text="Aquí se muestran los logs generados por la aplicación.",
                 font=("Helvetica", 10), bg=AZUL_OSCURO, fg=GRIS_TEXTO).pack()

        self.txt_logs = tk.Text(self, height=22, width=110,
                                bg="#0d1b2e", fg=GRIS_TEXTO,
                                insertbackground=BLANCO,
                                relief="flat", bd=2)
        self.txt_logs.pack(fill="both", expand=True, padx=18, pady=(12, 6))
        self.txt_logs.config(state="disabled")

        botones = tk.Frame(self, bg=AZUL_OSCURO)
        botones.pack(pady=(0, 12))

        tk.Button(botones, text="🔄 Refrescar logs",
                  command=self.refrescar, font=("Helvetica", 10, "bold"),
                  bg=AMARILLO, fg=AZUL_OSCURO, relief="flat",
                  padx=10, pady=5, cursor="hand2").pack(side="left", padx=6)
        tk.Button(botones, text="📄 Exportar logs",
                  command=self.exportar_logs, font=("Helvetica", 10, "bold"),
                  bg=VERDE, fg="white", relief="flat",
                  padx=10, pady=5, cursor="hand2").pack(side="left", padx=6)

        tk.Button(botones, text="🧹 Limpiar panel",
                  command=self.limpiar_panel, font=("Helvetica", 10, "bold"),
                  bg=AZUL_MEDIO, fg=BLANCO, relief="flat",
                  padx=10, pady=5, cursor="hand2").pack(side="left", padx=6)

        self.lbl_info = tk.Label(self, text="Pulse Refrescar para ver los eventos más recientes.",
                                 font=("Helvetica", 9), bg=AZUL_OSCURO, fg=GRIS_TEXTO)
        self.lbl_info.pack()

    def refrescar(self):
        from core.log_service import get_log_entries
        registros = get_log_entries()
        self.txt_logs.config(state="normal")
        self.txt_logs.delete("1.0", "end")
        if registros:
            self.txt_logs.insert("end", "\n".join(registros))
        else:
            self.txt_logs.insert("end", "No hay eventos registrados aún.")
        self.txt_logs.config(state="disabled")
        self.txt_logs.see("end")
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

        from core.log_service import export_logs
        export_logs(path)
        messagebox.showinfo("Exportación completa", f"Logs exportados a:\n{path}")
        self.logger.info(f"Logs exportados a: {path}")

    def limpiar_panel(self):
        self.txt_logs.config(state="normal")
        self.txt_logs.delete("1.0", "end")
        self.txt_logs.config(state="disabled")
        self.logger.info("Panel de logs limpiado")
