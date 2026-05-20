# Surr - Renamer

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

Mini-tool Windows de renommage de **séquences d'images** et de fichiers en lot, inspiré de **Comet Renamer** (Michael B. Comet) pour Maya.

Interface compacte, thème sombre rose-gris, preview live obligatoire, drag & drop.

---

## ✨ Fonctionnalités

- **Rename & Number** — renomme une séquence avec nom de base + numérotation (`render_0001.exr`, `render_0002.exr`, ...)
- **Search & Replace** — chercher/remplacer dans les noms (avec ou sans casse)
- **Prefix / Suffix** — ajout d'un préfixe et/ou suffixe (l'extension est toujours préservée)
- **Renumber / Re-padding** — re-séquence une série existante : change start, step ou padding (`shot_1.exr` → `shot_0001.exr`, ou shift `+10` d'une séquence entière)

Toutes les opérations sont précédées d'une **preview avant/après** et la détection de collisions bloque l'application en cas de conflit.

---

## 🚀 Installation

### Prérequis

- **Python 3.8+** installé et accessible dans le PATH ([python.org](https://www.python.org/downloads/windows/))
- Tkinter (inclus par défaut dans l'installateur Windows)

### Lancement

1. Cloner le repo :
   ```bash
   git clone https://github.com/surrendrart-hub/Surr-MiniTool-Renamer.git
   ```
2. **Double-cliquer** sur `Lancer_Mini_Renamer.bat`.

Le .bat installe automatiquement `tkinterdnd2` (drag & drop) la première fois, puis lance l'app.

### Lancement manuel

```bash
pip install tkinterdnd2
python mini_renamer.py
```

---

## 🖼️ Aperçu

```
┌──────────────────────────────────────────────────────────┐
│  Surr - Renamer powered by Surrendr.art                  │
├──────────────────────────────────────────────────────────┤
│  [📁 Dossier]  [📄 Fichiers]  [🗑️ Vider]   Filtre: .exr  │
│  ┌──────────────────────────────────────────────────┐    │
│  │ shot_001.exr                                     │    │
│  │ shot_002.exr                                     │    │
│  │ shot_003.exr   (drag & drop zone)                │    │
│  └──────────────────────────────────────────────────┘    │
├──────────────────────────────────────────────────────────┤
│ [Rename & Number] [Search & Replace] [Prefix] [Renumber] │
│   Nom de base :   render_                                │
│   Numéro :        1                                      │
│   Step :          1                                      │
│   Padding :       4                                      │
├──────────────────────────────────────────────────────────┤
│  APERÇU (avant → après)                                  │
│  shot_001.exr  →  render_0001.exr                        │
│  shot_002.exr  →  render_0002.exr                        │
│  shot_003.exr  →  render_0003.exr                        │
├──────────────────────────────────────────────────────────┤
│  3 fichiers — 3 changements        [Rafraîchir][APPLIQUER]│
└──────────────────────────────────────────────────────────┘
```

---

## 🔒 Sécurités

- **Preview obligatoire** avant toute action
- **Détection de collisions** : surlignées en rouge, bouton Appliquer désactivé
- **Renommage en deux passes** via fichiers temporaires : permet de shifter une séquence (001→002, 002→003, ...) sans qu'un fichier en écrase un autre
- Confirmation avant exécution

---

## 📚 Tutoriel

Cas d'usage concrets (renommer un render Arnold, normaliser un padding, etc.) → voir [**TUTORIEL.md**](TUTORIEL.md)

---

## 🛠️ Packaging en .exe (optionnel)

Pour distribuer sans dépendance Python :

```bash
pip install pyinstaller tkinterdnd2
pyinstaller --onefile --windowed --name SurrRenamer mini_renamer.py
```

L'exécutable apparaît dans `dist\SurrRenamer.exe`.

---

## 📁 Structure du projet

```
Surr-MiniTool-Renamer/
├── mini_renamer.py            # script principal (Tkinter)
├── Lancer_Mini_Renamer.bat    # launcher Windows
├── README.md
├── TUTORIEL.md                # guide d'utilisation détaillé
└── .gitignore
```

---

## 📝 Crédits

- Concept inspiré de [**Comet Renamer**](http://www.comet-cartoons.com/) par Michael B. Comet (Maya)
- Powered by [**Surrendr.art**](https://surrendr.art)

## 📄 Licence

MIT — voir [`LICENSE`](LICENSE)
