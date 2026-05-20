# Tutoriel — Surr - Renamer

Guide complet d'utilisation avec cas concrets pour le pipeline 3D / VFX / motion design.

---

## Sommaire

1. [Premier lancement](#1-premier-lancement)
2. [Workflow général](#2-workflow-général)
3. [Cas pratiques](#3-cas-pratiques)
   - [3.1 Renommer un render Arnold/Redshift en séquence propre](#31-renommer-un-render-arnoldredshift-en-séquence-propre)
   - [3.2 Corriger un préfixe sur tout un dossier](#32-corriger-un-préfixe-sur-tout-un-dossier)
   - [3.3 Normaliser le padding d'une vieille séquence](#33-normaliser-le-padding-dune-vieille-séquence)
   - [3.4 Shifter une séquence (+10 frames)](#34-shifter-une-séquence-10-frames)
   - [3.5 Ajouter un tag de version](#35-ajouter-un-tag-de-version)
   - [3.6 Filtrer pour ne renommer que les .exr](#36-filtrer-pour-ne-renommer-que-les-exr)
4. [Trucs et astuces](#4-trucs-et-astuces)
5. [Erreurs courantes](#5-erreurs-courantes)

---

## 1. Premier lancement

Double-clic sur **`Lancer_Mini_Renamer.bat`**. La toute première fois, le script installe `tkinterdnd2` (drag & drop) — ça prend 5 secondes. Les lancements suivants sont instantanés.

La fenêtre s'ouvre en thème sombre, dimensions ~780×720.

---

## 2. Workflow général

Quel que soit le cas d'usage, le workflow est toujours le même :

1. **Charger les fichiers** — glisse un dossier dans la zone du haut, ou utilise `Choisir un dossier...`. Tous les fichiers du dossier sont listés (sous-dossiers ignorés).
2. **Filtrer** (optionnel) — dans `Filtre ext`, taper `.exr` (ou `.exr,.png` pour plusieurs) pour ne garder que ces extensions.
3. **Choisir l'onglet** correspondant à l'opération (Rename & Number, Search & Replace, Prefix/Suffix, Renumber).
4. **Régler les paramètres** — l'**aperçu se met à jour en temps réel**. La colonne de gauche montre les noms actuels, celle de droite les nouveaux.
5. **Vérifier les collisions** — si surlignées en rouge, le bouton APPLIQUER est désactivé. Ajuste les paramètres.
6. **Cliquer APPLIQUER** — confirmation, puis renommage immédiat sur le disque.

> **Règle d'or** : l'aperçu ne ment jamais. Si tu vois `render_0001.exr` à droite, c'est exactement ce que tu auras sur le disque.

---

## 3. Cas pratiques

### 3.1 Renommer un render Arnold/Redshift en séquence propre

**Situation** : ton render sort avec des noms verbeux du genre :
```
MyScene_beauty_v003.0001.exr
MyScene_beauty_v003.0002.exr
MyScene_beauty_v003.0003.exr
...
```

Et tu veux la séquence finale en `shot010_0001.exr`.

**Onglet** : `Rename & Number`

| Paramètre | Valeur |
|---|---|
| Nom de base | `shot010_` |
| Numéro de départ | `1` |
| Pas (step) | `1` |
| Padding | `4` |
| Conserver l'extension | ☑ coché |

**Résultat** :
```
MyScene_beauty_v003.0001.exr → shot010_0001.exr
MyScene_beauty_v003.0002.exr → shot010_0002.exr
...
```

---

### 3.2 Corriger un préfixe sur tout un dossier

**Situation** : tu as livré une séquence avec le mauvais nom de shot.
```
sho010_0001.exr   ← typo, manque le 't'
sho010_0002.exr
```

**Onglet** : `Search & Replace`

| Paramètre | Valeur |
|---|---|
| Chercher | `sho010` |
| Remplacer par | `shot010` |
| Sensible à la casse | ☑ |

**Résultat** :
```
sho010_0001.exr → shot010_0001.exr
sho010_0002.exr → shot010_0002.exr
```

---

### 3.3 Normaliser le padding d'une vieille séquence

**Situation** : une vieille séquence sans padding cohérent.
```
test_1.png
test_2.png
...
test_10.png
test_42.png
```

Tu veux du padding à 4 chiffres.

**Onglet** : `Renumber / Re-padding`

| Paramètre | Valeur |
|---|---|
| Nouveau départ | `1` |
| Pas | `1` |
| Padding | `4` |

> ⚠️ **Important** : Renumber ne préserve PAS les numéros d'origine, il **re-numérote dans l'ordre alphabétique** des fichiers. Si tu veux préserver les numéros exacts (1, 2, 10, 42 → 0001, 0002, 0010, 0042), utilise plutôt l'onglet `Search & Replace` avec un regex... ou applique le renommage en plusieurs lots.

**Résultat avec Renumber** :
```
test_1.png  → test_0001.png
test_10.png → test_0002.png   ← réordonné car '10' < '2' alphabétiquement
test_2.png  → test_0003.png
test_42.png → test_0004.png
```

💡 **Astuce** : pour éviter ce piège, donne à tes séquences un padding minimum dès le rendu (jamais de `_1`, toujours `_001` ou plus).

---

### 3.4 Shifter une séquence (+10 frames)

**Situation** : tu veux décaler ta séquence de 10 frames pour la raccorder à un autre plan.
```
shot_0001.exr
shot_0002.exr
shot_0003.exr
```

Doit devenir :
```
shot_0011.exr
shot_0012.exr
shot_0013.exr
```

**Onglet** : `Renumber / Re-padding`

| Paramètre | Valeur |
|---|---|
| Nouveau départ | `11` |
| Pas | `1` |
| Padding | `4` |

C'est le cas qui casse beaucoup d'outils de renommage naïfs (parce que `0001 → 0002` écraserait l'ancien `0002`). Surr - Renamer renomme en deux passes via fichiers temporaires, donc **aucun risque de perte de données**.

---

### 3.5 Ajouter un tag de version

**Situation** : avant livraison, tu veux marquer ta séquence d'un suffixe `_v01`.
```
shot010_0001.exr
shot010_0002.exr
```

Doit devenir :
```
shot010_0001_v01.exr
shot010_0002_v01.exr
```

**Onglet** : `Prefix / Suffix`

| Paramètre | Valeur |
|---|---|
| Préfixe | *(vide)* |
| Suffixe (avant l'ext) | `_v01` |

Le suffixe est inséré **avant** l'extension (jamais `.exr_v01`).

---

### 3.6 Filtrer pour ne renommer que les .exr

**Situation** : ton dossier contient des `.exr`, des `.jpg` de preview, et un fichier `.xml` de métadata. Tu veux renommer **uniquement** les `.exr`.

1. Charger le dossier complet (drag & drop).
2. Dans `Filtre ext`, taper : `.exr`
3. La liste et l'aperçu n'affichent plus que les `.exr` — les autres fichiers sont ignorés par l'opération.

Pour plusieurs extensions : `.exr,.png,.tif`

---

## 4. Trucs et astuces

- **Toujours regarder l'aperçu en entier** — utilise la scrollbar pour vérifier les bords (premier et dernier fichier).
- **Tester d'abord sur une copie** si tu n'es pas sûr — fais un `Ctrl+C / Ctrl+V` du dossier avant la première utilisation.
- **Les noms inchangés** apparaissent en gris dans l'aperçu — c'est normal, ils ne seront pas touchés.
- **Drag & drop d'un dossier** charge tous les fichiers du dossier (pas récursif). Pour glisser des fichiers spécifiques, sélectionne-les dans l'explorateur Windows et glisse la sélection.
- **Combinaison d'opérations** : tu peux enchaîner Search & Replace puis Prefix/Suffix puis Renumber. Chaque clic sur APPLIQUER renomme et la liste se met à jour avec les nouveaux noms.
- **Annulation** : il n'y a pas de undo intégré (le renommage est immédiat sur le disque). Si tu te trompes, applique l'opération inverse — l'aperçu te confirmera que ça ramène les noms d'origine.

---

## 5. Erreurs courantes

| Symptôme | Cause | Solution |
|---|---|---|
| Bouton APPLIQUER grisé | Collisions détectées (cellules rouges dans l'aperçu) | Ajuste le start#, padding, ou search pattern jusqu'à éliminer les rouges |
| L'app ne se lance pas (cmd se ferme) | Python pas dans le PATH | Réinstalle Python en cochant "Add to PATH" |
| Pas de drag & drop | `tkinterdnd2` non installé | Utiliser le .bat (auto-install) ou `pip install tkinterdnd2` |
| Erreur "Permission denied" sur APPLIQUER | Un des fichiers est ouvert dans un autre programme | Fermer Nuke / DJV / Photoshop / l'explorateur et réessayer |
| Renumber a tout mélangé | L'ordre alphabétique des sources n'était pas celui attendu (voir 3.3) | Padder les sources d'abord (`_1` → `_001`) avant de Renumber |

---

## Ressources

- **Comet Renamer** (l'inspiration originale) : http://www.comet-cartoons.com/toons/3ddocs/cometScripts/
- **tkinterdnd2** (lib drag & drop) : https://github.com/pmgagne/tkinterdnd2
- **PyInstaller** (pour packager en .exe) : https://pyinstaller.org

---

Bon rename !  
— *Powered by Surrendr.art*
