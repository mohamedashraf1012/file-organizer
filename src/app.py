import os
import sys
import threading

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
except ImportError:
    print("customtkinter not installed. Run: pip install customtkinter")
    sys.exit(1)

from src.organizer import organize_files, get_folder_stats

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#0f0f0f",
    "surface": "#1a1a2e",
    "card": "#16213e",
    "accent": "#0f3460",
    "blue": "#4361ee",
    "green": "#06d6a0",
    "yellow": "#ffd166",
    "red": "#ef476f",
    "text": "#e2e8f0",
    "muted": "#94a3b8",
}


class FileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("File Organizer")
        self.geometry("860x640")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])

        self.selected_folder = ctk.StringVar(value="")
        self.dry_run_var = ctk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="🗂  File Organizer",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left", padx=24, pady=18)

        ctk.CTkLabel(
            header,
            text="CI/CD Project — ITI",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["muted"],
        ).pack(side="right", padx=24)

        # ── Main body ────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        # Left column
        left = ctk.CTkFrame(body, fg_color="transparent", width=380)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        self._build_folder_card(left)
        self._build_stats_card(left)

        # Right column
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True)

        self._build_log_card(right)
        self._build_action_bar(right)

    def _build_folder_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=12)
        card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            card,
            text="SELECT FOLDER",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["muted"],
        ).pack(anchor="w", padx=16, pady=(14, 4))

        path_frame = ctk.CTkFrame(card, fg_color=COLORS["accent"], corner_radius=8)
        path_frame.pack(fill="x", padx=16, pady=(0, 8))

        self.path_label = ctk.CTkLabel(
            path_frame,
            textvariable=self.selected_folder,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["muted"],
            wraplength=280,
            anchor="w",
        )
        self.path_label.pack(side="left", padx=12, pady=10, fill="x", expand=True)

        ctk.CTkButton(
            card,
            text="Browse",
            width=100,
            height=36,
            fg_color=COLORS["blue"],
            hover_color="#3451d1",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._browse_folder,
        ).pack(anchor="w", padx=16, pady=(0, 14))

        # Dry run toggle
        dry_frame = ctk.CTkFrame(card, fg_color="transparent")
        dry_frame.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkSwitch(
            dry_frame,
            text="Dry Run (simulate only)",
            variable=self.dry_run_var,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
            progress_color=COLORS["yellow"],
        ).pack(side="left")

    def _build_stats_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=12)
        card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            card,
            text="FOLDER PREVIEW",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["muted"],
        ).pack(anchor="w", padx=16, pady=(14, 8))

        self.stats_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=16, pady=(0, 14))

        self.stats_placeholder = ctk.CTkLabel(
            self.stats_frame,
            text="Select a folder to preview its contents",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["muted"],
        )
        self.stats_placeholder.pack()

    def _build_log_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=12)
        card.pack(fill="both", expand=True, pady=(0, 12))

        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.pack(fill="x", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            header_row,
            text="ACTIVITY LOG",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["muted"],
        ).pack(side="left")

        ctk.CTkButton(
            header_row,
            text="Clear",
            width=56,
            height=24,
            fg_color=COLORS["accent"],
            hover_color="#1a2a5e",
            font=ctk.CTkFont(size=11),
            command=self._clear_log,
        ).pack(side="right")

        self.log_box = ctk.CTkTextbox(
            card,
            fg_color=COLORS["accent"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=8,
            state="disabled",
        )
        self.log_box.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def _build_action_bar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=12, height=64)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        self.organize_btn = ctk.CTkButton(
            bar,
            text="⚡  Organize Files",
            height=40,
            fg_color=COLORS["green"],
            hover_color="#05b589",
            text_color="#0f0f0f",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._run_organize,
        )
        self.organize_btn.pack(side="left", padx=16, pady=12)

        self.status_label = ctk.CTkLabel(
            bar,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["muted"],
        )
        self.status_label.pack(side="left", padx=8)

        self.progress = ctk.CTkProgressBar(bar, mode="indeterminate", width=120)
        self.progress.pack(side="right", padx=16)
        self.progress.set(0)

    # ── Actions ───────────────────────────────────────────────────

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select folder to organize")
        if folder:
            self.selected_folder.set(folder)
            self._refresh_stats(folder)
            self._log(f"📁 Selected: {folder}", "info")

    def _refresh_stats(self, folder):
        # Clear previous stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        try:
            stats = get_folder_stats(folder)
            if not stats:
                ctk.CTkLabel(
                    self.stats_frame,
                    text="No files found in this folder",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["muted"],
                ).pack()
                return

            total = sum(stats.values())
            ctk.CTkLabel(
                self.stats_frame,
                text=f"Total files: {total}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text"],
            ).pack(anchor="w", pady=(0, 6))

            cat_colors = {
                "Images": COLORS["blue"],
                "Videos": "#9b5de5",
                "Audio": "#f15bb5",
                "Documents": COLORS["yellow"],
                "Code": COLORS["green"],
                "Archives": "#ff6b6b",
                "Others": COLORS["muted"],
            }

            for cat, count in sorted(stats.items(), key=lambda x: -x[1]):
                row = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
                row.pack(fill="x", pady=2)

                color = cat_colors.get(cat, COLORS["muted"])
                ctk.CTkLabel(
                    row,
                    text="●",
                    font=ctk.CTkFont(size=14),
                    text_color=color,
                    width=20,
                ).pack(side="left")
                ctk.CTkLabel(
                    row,
                    text=f"{cat}",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text"],
                    width=100,
                    anchor="w",
                ).pack(side="left")
                ctk.CTkLabel(
                    row,
                    text=str(count),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=color,
                ).pack(side="left")

        except Exception as e:
            ctk.CTkLabel(
                self.stats_frame,
                text=f"Error: {e}",
                text_color=COLORS["red"],
            ).pack()

    def _run_organize(self):
        folder = self.selected_folder.get()
        if not folder:
            messagebox.showwarning("No Folder", "Please select a folder first.")
            return

        self.organize_btn.configure(state="disabled")
        self.progress.start()
        self.status_label.configure(text="Organizing...", text_color=COLORS["yellow"])

        dry = self.dry_run_var.get()
        threading.Thread(target=self._organize_thread, args=(folder, dry), daemon=True).start()

    def _organize_thread(self, folder, dry_run):
        try:
            mode = "[DRY RUN] " if dry_run else ""
            self._log(f"🚀 {mode}Starting organization of: {folder}", "info")
            summary = organize_files(folder, dry_run=dry_run)

            self._log(f"✅ Done! Moved: {summary['moved']} | Errors: {summary['errors']}", "success")
            for detail in summary["details"]:
                status = detail["status"]
                icon = "✓" if "moved" in status or "simulated" in status else "✗"
                self._log(f"  {icon} {detail['file']} → {detail['category']}/", "info")

            self.after(0, lambda: self._on_done(summary))
        except Exception as e:
            self._log(f"❌ Error: {e}", "error")
            self.after(0, self._on_error)

    def _on_done(self, summary):
        self.organize_btn.configure(state="normal")
        self.progress.stop()
        self.progress.set(1)
        self.status_label.configure(
            text=f"Done! {summary['moved']} files organized",
            text_color=COLORS["green"],
        )
        if self.selected_folder.get():
            self._refresh_stats(self.selected_folder.get())

    def _on_error(self):
        self.organize_btn.configure(state="normal")
        self.progress.stop()
        self.status_label.configure(text="Failed!", text_color=COLORS["red"])

    def _log(self, message: str, level: str = "info"):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")


def main():
    app = FileOrganizerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
