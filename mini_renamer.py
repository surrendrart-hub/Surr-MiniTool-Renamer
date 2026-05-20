"""
Surr - Renamer  (powered by Surrendr.art)
Inspiré de Comet Renamer (Michael B. Comet) pour Maya.
Outil de renommage de séquences d'images / fichiers.

Fonctions :
  - Rename & Number  : nom de base + numérotation (padding configurable)
  - Search & Replace : chercher/remplacer dans les noms
  - Prefix / Suffix  : ajout de préfixe et/ou suffixe
  - Renumber         : ré-numéroter une séquence existante (start, step, padding)

Preview live obligatoire avant application.
Drag & drop d'un dossier ou de fichiers (nécessite tkinterdnd2).
Thème gris foncé + contours rose-gris.
"""

import os
import re
import sys
import shutil
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# --- Drag & drop (optionnel, fallback gracieux si absent) ---
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


# ============================================================
#  LOGIQUE DE RENOMMAGE
# ============================================================

SEQ_REGEX = re.compile(r"^(.*?)(\d+)$")


def split_name(filename):
    stem, ext = os.path.splitext(filename)
    return stem, ext


def op_rename_and_number(files, base, start, step, padding, keep_ext=True):
    out = []
    n = start
    for path in files:
        _, ext = split_name(os.path.basename(path))
        new_name = f"{base}{str(n).zfill(padding)}"
        if keep_ext:
            new_name += ext
        out.append(new_name)
        n += step
    return out


def op_search_replace(files, search, replace, case_sensitive=True):
    out = []
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(re.escape(search), flags) if search else None
    for path in files:
        stem, ext = split_name(os.path.basename(path))
        if pattern:
            new_stem = pattern.sub(replace, stem)
        else:
            new_stem = stem
        out.append(new_stem + ext)
    return out


def op_prefix_suffix(files, prefix, suffix):
    out = []
    for path in files:
        stem, ext = split_name(os.path.basename(path))
        new_stem = f"{prefix}{stem}{suffix}"
        out.append(new_stem + ext)
    return out


def op_renumber(files, start, step, padding):
    out = []
    n = start
    for path in files:
        stem, ext = split_name(os.path.basename(path))
        m = SEQ_REGEX.match(stem)
        if m:
            base = m.group(1)
        else:
            base = stem + "_"
        new_stem = f"{base}{str(n).zfill(padding)}"
        out.append(new_stem + ext)
        n += step
    return out


def apply_rename(files, new_names):
    if len(files) != len(new_names):
        raise ValueError("Mismatch entre fichiers et nouveaux noms")

    targets = []
    seen = set()
    dups = []
    for path, new in zip(files, new_names):
        target = os.path.join(os.path.dirname(path), new)
        targets.append(target)
        key = target.lower() if os.name == "nt" else target
        if key in seen:
            dups.append(new)
        seen.add(key)
    if dups:
        raise ValueError(f"Collision détectée dans les nouveaux noms : {dups[:5]}")

    tmp_paths = []
    errors = []
    for path in files:
        tmp = path + ".__tmp_rename__" + os.urandom(4).hex()
        try:
            os.rename(path, tmp)
            tmp_paths.append(tmp)
        except OSError as e:
            errors.append(f"{os.path.basename(path)} : {e}")
            tmp_paths.append(None)

    count = 0
    for tmp, target in zip(tmp_paths, targets):
        if tmp is None:
            continue
        try:
            os.rename(tmp, target)
            count += 1
        except OSError as e:
            errors.append(f"-> {os.path.basename(target)} : {e}")
            try:
                os.rename(tmp, tmp.split(".__tmp_rename__")[0])
            except OSError:
                pass

    return count, errors


# ============================================================
#  INTERFACE
# ============================================================

class MiniRenamerApp:
    def __init__(self, root):
        self.root = root
        root.title("Surr - Renamer powered by Surrendr.art")
        root.geometry("820x820")
        root.minsize(760, 760)

        self.files = []

        self._setup_style()
        self._build_ui()
        self._refresh_preview()

    # -------- Theme : gris foncé + contours rose-gris --------
    def _setup_style(self):
        self.C_BG       = "#2b2b2b"
        self.C_BG_ALT   = "#353535"
        self.C_BG_HOVER = "#42393a"
        self.C_FG       = "#e0e0e0"
        self.C_FG_MUTED = "#888888"
        self.C_BORDER   = "#b89a9a"
        self.C_ACCENT   = "#d4a5a5"
        self.C_COLLISION_BG = "#5a2a2a"
        self.C_COLLISION_FG = "#ffd0d0"

        self.root.configure(bg=self.C_BG)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".",
                        background=self.C_BG, foreground=self.C_FG,
                        fieldbackground=self.C_BG_ALT,
                        bordercolor=self.C_BORDER,
                        lightcolor=self.C_BORDER, darkcolor=self.C_BORDER,
                        focuscolor=self.C_ACCENT,
                        troughcolor=self.C_BG_ALT)

        style.configure("TFrame", background=self.C_BG)
        style.configure("TLabelframe",
                        background=self.C_BG,
                        bordercolor=self.C_BORDER,
                        lightcolor=self.C_BORDER, darkcolor=self.C_BORDER)
        style.configure("TLabelframe.Label",
                        background=self.C_BG, foreground=self.C_BORDER)
        style.configure("TLabel", background=self.C_BG, foreground=self.C_FG)

        style.configure("TButton",
                        background=self.C_BG_ALT, foreground=self.C_FG,
                        bordercolor=self.C_BORDER,
                        lightcolor=self.C_BORDER, darkcolor=self.C_BORDER,
                        focusthickness=1, focuscolor=self.C_ACCENT,
                        borderwidth=1, padding=(10, 5))
        style.map("TButton",
                  background=[("active", self.C_BG_HOVER),
                              ("disabled", "#2f2f2f")],
                  foreground=[("disabled", self.C_FG_MUTED)],
                  bordercolor=[("active", self.C_ACCENT),
                               ("focus", self.C_ACCENT)],
                  lightcolor=[("active", self.C_ACCENT)],
                  darkcolor=[("active", self.C_ACCENT)])

        style.configure("TEntry",
                        fieldbackground=self.C_BG_ALT, foreground=self.C_FG,
                        insertcolor=self.C_FG,
                        bordercolor=self.C_BORDER,
                        lightcolor=self.C_BORDER, darkcolor=self.C_BORDER,
                        borderwidth=1)
        style.map("TEntry",
                  bordercolor=[("focus", self.C_ACCENT)],
                  lightcolor=[("focus", self.C_ACCENT)],
                  darkcolor=[("focus", self.C_ACCENT)])

        style.configure("TCheckbutton",
                        background=self.C_BG, foreground=self.C_FG,
                        indicatorbackground=self.C_BG_ALT,
                        indicatorforeground=self.C_ACCENT,
                        bordercolor=self.C_BORDER)
        style.map("TCheckbutton",
                  background=[("active", self.C_BG)],
                  indicatorcolor=[("selected", self.C_ACCENT),
                                  ("!selected", self.C_BG_ALT)])

        style.configure("TNotebook",
                        background=self.C_BG, bordercolor=self.C_BORDER,
                        lightcolor=self.C_BG, darkcolor=self.C_BG)
        style.configure("TNotebook.Tab",
                        background=self.C_BG_ALT, foreground=self.C_FG,
                        bordercolor=self.C_BORDER,
                        lightcolor=self.C_BORDER, darkcolor=self.C_BORDER,
                        padding=(12, 6))
        style.map("TNotebook.Tab",
                  background=[("selected", self.C_BG_HOVER),
                              ("active", "#3d3536")],
                  foreground=[("selected", self.C_ACCENT)],
                  bordercolor=[("selected", self.C_ACCENT)])

        style.configure("Treeview",
                        background=self.C_BG_ALT, foreground=self.C_FG,
                        fieldbackground=self.C_BG_ALT,
                        bordercolor=self.C_BORDER, rowheight=22)
        style.configure("Treeview.Heading",
                        background=self.C_BG, foreground=self.C_BORDER,
                        bordercolor=self.C_BORDER, relief="flat")
        style.map("Treeview",
                  background=[("selected", self.C_BG_HOVER)],
                  foreground=[("selected", self.C_ACCENT)])
        style.map("Treeview.Heading",
                  background=[("active", self.C_BG_ALT)])

        style.configure("Vertical.TScrollbar",
                        background=self.C_BG_ALT,
                        bordercolor=self.C_BORDER,
                        lightcolor=self.C_BORDER, darkcolor=self.C_BORDER,
                        arrowcolor=self.C_BORDER, troughcolor=self.C_BG)
        style.map("Vertical.TScrollbar",
                  background=[("active", self.C_BG_HOVER)],
                  arrowcolor=[("active", self.C_ACCENT)])

    # -------- UI --------
    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        top = ttk.LabelFrame(self.root, text="Fichiers")
        top.pack(fill="x", **pad)

        btn_row = ttk.Frame(top)
        btn_row.pack(fill="x", padx=6, pady=4)
        ttk.Button(btn_row, text="Choisir un dossier...", command=self._browse_folder).pack(side="left")
        ttk.Button(btn_row, text="Choisir des fichiers...", command=self._browse_files).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Vider la liste", command=self._clear).pack(side="left", padx=4)

        ttk.Label(btn_row, text="Filtre ext (ex: .exr,.png) :").pack(side="left", padx=(20, 4))
        self.var_filter = tk.StringVar(value="")
        e_filter = ttk.Entry(btn_row, textvariable=self.var_filter, width=14)
        e_filter.pack(side="left")
        e_filter.bind("<KeyRelease>", lambda e: self._refresh_preview())

        list_frame = ttk.Frame(top)
        list_frame.pack(fill="x", padx=6, pady=4)
        self.lst_files = tk.Listbox(
            list_frame, height=6, selectmode="extended",
            bg=self.C_BG_ALT, fg=self.C_FG,
            selectbackground=self.C_BG_HOVER, selectforeground=self.C_ACCENT,
            highlightthickness=1,
            highlightbackground=self.C_BORDER, highlightcolor=self.C_ACCENT,
            borderwidth=0, relief="flat",
            activestyle="none",
        )
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.lst_files.yview)
        self.lst_files.config(yscrollcommand=sb.set)
        self.lst_files.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        if DND_AVAILABLE:
            self.lst_files.drop_target_register(DND_FILES)
            self.lst_files.dnd_bind("<<Drop>>", self._on_drop)
            hint = "Glisser-déposer un dossier ou des fichiers ici"
        else:
            hint = "(tkinterdnd2 non installé — utiliser les boutons ci-dessus)"
        ttk.Label(top, text=hint, foreground=self.C_FG_MUTED).pack(anchor="w", padx=10, pady=(0, 4))

        nb = ttk.Notebook(self.root)
        nb.pack(fill="x", **pad)
        self.nb = nb
        nb.bind("<<NotebookTabChanged>>", lambda e: self._refresh_preview())

        t1 = ttk.Frame(nb)
        nb.add(t1, text="Rename & Number")
        self.var_base = tk.StringVar(value="render_")
        self.var_start = tk.StringVar(value="1")
        self.var_step = tk.StringVar(value="1")
        self.var_pad = tk.StringVar(value="4")
        self.var_keep_ext = tk.BooleanVar(value=True)

        self._row(t1, 0, "Nom de base :", self.var_base, width=24)
        self._row(t1, 1, "Numéro de départ :", self.var_start, width=8)
        self._row(t1, 2, "Pas (step) :", self.var_step, width=8)
        self._row(t1, 3, "Padding (nb chiffres) :", self.var_pad, width=8)
        ttk.Checkbutton(t1, text="Conserver l'extension",
                        variable=self.var_keep_ext,
                        command=self._refresh_preview).grid(row=4, column=1, sticky="w", padx=6, pady=4)

        t2 = ttk.Frame(nb)
        nb.add(t2, text="Search & Replace")
        self.var_search = tk.StringVar()
        self.var_replace = tk.StringVar()
        self.var_case = tk.BooleanVar(value=True)
        self._row(t2, 0, "Chercher :", self.var_search, width=24)
        self._row(t2, 1, "Remplacer par :", self.var_replace, width=24)
        ttk.Checkbutton(t2, text="Sensible à la casse",
                        variable=self.var_case,
                        command=self._refresh_preview).grid(row=2, column=1, sticky="w", padx=6, pady=4)

        t3 = ttk.Frame(nb)
        nb.add(t3, text="Prefix / Suffix")
        self.var_prefix = tk.StringVar()
        self.var_suffix = tk.StringVar()
        self._row(t3, 0, "Préfixe :", self.var_prefix, width=24)
        self._row(t3, 1, "Suffixe (avant l'ext) :", self.var_suffix, width=24)

        t4 = ttk.Frame(nb)
        nb.add(t4, text="Renumber / Re-padding")
        self.var_rn_start = tk.StringVar(value="1")
        self.var_rn_step = tk.StringVar(value="1")
        self.var_rn_pad = tk.StringVar(value="4")
        self._row(t4, 0, "Nouveau départ :", self.var_rn_start, width=8)
        self._row(t4, 1, "Pas :", self.var_rn_step, width=8)
        self._row(t4, 2, "Padding :", self.var_rn_pad, width=8)

        prev = ttk.LabelFrame(self.root, text="Aperçu (avant → après)")
        prev.pack(fill="both", expand=True, **pad)

        prev_inner = ttk.Frame(prev)
        prev_inner.pack(fill="both", expand=True, padx=6, pady=4)
        cols = ("old", "arrow", "new")
        self.tree = ttk.Treeview(prev_inner, columns=cols, show="headings", height=10)
        self.tree.heading("old", text="Nom actuel")
        self.tree.heading("arrow", text="")
        self.tree.heading("new", text="Nouveau nom")
        self.tree.column("old", width=300, anchor="w")
        self.tree.column("arrow", width=30, anchor="center")
        self.tree.column("new", width=300, anchor="w")
        sb2 = ttk.Scrollbar(prev_inner, orient="vertical", command=self.tree.yview)
        self.tree.config(yscrollcommand=sb2.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")

        self.tree.tag_configure("collision",
                                background=self.C_COLLISION_BG,
                                foreground=self.C_COLLISION_FG)
        self.tree.tag_configure("unchanged", foreground=self.C_FG_MUTED)

        self.lbl_status = ttk.Label(self.root, text="", anchor="w")
        self.lbl_status.pack(fill="x", padx=10)

        actions = ttk.Frame(self.root)
        actions.pack(fill="x", padx=10, pady=8)
        ttk.Button(actions, text="Rafraîchir l'aperçu", command=self._refresh_preview).pack(side="left")
        self.btn_apply = ttk.Button(actions, text="APPLIQUER", command=self._apply)
        self.btn_apply.pack(side="right")

        for var in [self.var_base, self.var_start, self.var_step, self.var_pad,
                    self.var_search, self.var_replace,
                    self.var_prefix, self.var_suffix,
                    self.var_rn_start, self.var_rn_step, self.var_rn_pad]:
            var.trace_add("write", lambda *a: self._refresh_preview())

    def _row(self, parent, row, label, var, width=14):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="e", padx=6, pady=4)
        ttk.Entry(parent, textvariable=var, width=width).grid(row=row, column=1, sticky="w", padx=6, pady=4)

    def _browse_folder(self):
        d = filedialog.askdirectory(title="Choisir un dossier")
        if d:
            self._load_folder(d)

    def _browse_files(self):
        fs = filedialog.askopenfilenames(title="Choisir des fichiers")
        if fs:
            self.files = sorted(fs)
            self._refresh_list()

    def _on_drop(self, event):
        raw = event.data
        paths = self._parse_dnd_paths(raw)
        files = []
        for p in paths:
            if os.path.isdir(p):
                for name in sorted(os.listdir(p)):
                    full = os.path.join(p, name)
                    if os.path.isfile(full):
                        files.append(full)
            elif os.path.isfile(p):
                files.append(p)
        if files:
            self.files = files
            self._refresh_list()

    @staticmethod
    def _parse_dnd_paths(data):
        paths = []
        i = 0
        while i < len(data):
            if data[i] == "{":
                end = data.find("}", i)
                if end == -1:
                    break
                paths.append(data[i + 1:end])
                i = end + 1
            elif data[i] == " ":
                i += 1
            else:
                end = data.find(" ", i)
                if end == -1:
                    paths.append(data[i:])
                    break
                paths.append(data[i:end])
                i = end + 1
        return paths

    def _load_folder(self, folder):
        files = []
        for name in sorted(os.listdir(folder)):
            full = os.path.join(folder, name)
            if os.path.isfile(full):
                files.append(full)
        self.files = files
        self._refresh_list()

    def _clear(self):
        self.files = []
        self._refresh_list()

    def _refresh_list(self):
        self.lst_files.delete(0, "end")
        for f in self._filtered_files():
            self.lst_files.insert("end", os.path.basename(f))
        self._refresh_preview()

    def _filtered_files(self):
        filt = self.var_filter.get().strip()
        if not filt:
            return list(self.files)
        exts = [e.strip().lower() for e in filt.split(",") if e.strip()]
        exts = [e if e.startswith(".") else "." + e for e in exts]
        return [f for f in self.files if os.path.splitext(f)[1].lower() in exts]

    def _compute_new_names(self, files):
        tab = self.nb.index(self.nb.select())
        try:
            if tab == 0:
                return op_rename_and_number(
                    files,
                    self.var_base.get(),
                    int(self.var_start.get() or 1),
                    int(self.var_step.get() or 1),
                    int(self.var_pad.get() or 1),
                    self.var_keep_ext.get(),
                )
            elif tab == 1:
                return op_search_replace(
                    files,
                    self.var_search.get(),
                    self.var_replace.get(),
                    self.var_case.get(),
                )
            elif tab == 2:
                return op_prefix_suffix(files, self.var_prefix.get(), self.var_suffix.get())
            elif tab == 3:
                return op_renumber(
                    files,
                    int(self.var_rn_start.get() or 1),
                    int(self.var_rn_step.get() or 1),
                    int(self.var_rn_pad.get() or 1),
                )
        except ValueError:
            return None
        return None

    def _refresh_preview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        files = self._filtered_files()
        if not files:
            self.lbl_status.config(text="Aucun fichier sélectionné.")
            return

        new_names = self._compute_new_names(files)
        if new_names is None:
            self.lbl_status.config(text="Paramètres invalides (vérifier les nombres).")
            return

        seen = {}
        for n in new_names:
            key = n.lower() if os.name == "nt" else n
            seen[key] = seen.get(key, 0) + 1

        existing_targets = set()
        if files:
            folder = os.path.dirname(files[0])
            try:
                existing_targets = {n.lower() if os.name == "nt" else n
                                    for n in os.listdir(folder)}
            except OSError:
                pass
        source_set = {os.path.basename(f).lower() if os.name == "nt" else os.path.basename(f)
                      for f in files}

        n_changed = 0
        n_collisions = 0
        for path, new in zip(files, new_names):
            old = os.path.basename(path)
            tags = []
            key = new.lower() if os.name == "nt" else new
            if old == new:
                tags.append("unchanged")
            else:
                n_changed += 1
            if seen[key] > 1:
                tags.append("collision")
                n_collisions += 1
            elif key in existing_targets and key not in source_set:
                tags.append("collision")
                n_collisions += 1
            self.tree.insert("", "end", values=(old, "→", new), tags=tags)

        msg = f"{len(files)} fichier(s) — {n_changed} changement(s)"
        if n_collisions:
            msg += f"  ⚠ {n_collisions} collision(s) — application bloquée"
            self.btn_apply.state(["disabled"])
        else:
            self.btn_apply.state(["!disabled"])
        self.lbl_status.config(text=msg)

    def _apply(self):
        files = self._filtered_files()
        if not files:
            return
        new_names = self._compute_new_names(files)
        if not new_names:
            messagebox.showerror("Erreur", "Paramètres invalides.")
            return

        pairs = [(f, n) for f, n in zip(files, new_names)
                 if os.path.basename(f) != n]
        if not pairs:
            messagebox.showinfo("Rien à faire", "Aucun nom ne change.")
            return

        if not messagebox.askyesno(
                "Confirmer",
                f"Renommer {len(pairs)} fichier(s) ?\nCette action est immédiate sur le disque."):
            return

        src = [p[0] for p in pairs]
        dst = [p[1] for p in pairs]
        try:
            count, errors = apply_rename(src, dst)
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        if files:
            folder = os.path.dirname(files[0])
            renamed_map = dict(zip(src, [os.path.join(folder, n) for n in dst]))
            self.files = [renamed_map.get(f, f) for f in self.files]
        self._refresh_list()

        if errors:
            messagebox.showwarning(
                "Terminé avec erreurs",
                f"{count} renommé(s).\nErreurs :\n" + "\n".join(errors[:10]))
        else:
            messagebox.showinfo("OK", f"{count} fichier(s) renommé(s).")


# ============================================================
#  MAIN
# ============================================================

def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = MiniRenamerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
