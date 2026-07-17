# Socle palette Clair Obscur — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Faire de `palette.toml` la seule source de vérité des couleurs, réellement branchée sur Hyprland, waybar, rofi, dunst, hyprlock et kitty, et réparer les sept bugs silencieux du repo.

**Architecture:** Un `palette.toml` à la racine est lu par `bin/generate_theme.py` (Python stdlib), qui émet un fragment de couleurs par outil dans la syntaxe de cet outil. Les configs restent écrites à la main et importent leur fragment. Dunst est la seule exception : son `dunstrc` est généré en entier depuis un template, parce que dunst ne supporte ni `include` ni variables.

**Tech Stack:** Python 3.14 (`tomllib`, `unittest` — stdlib uniquement), GNU Stow 2.4.1, Hyprland 0.55.4 (config Lua), waybar (GTK3), rofi 2.0 (Wayland natif), dunst 1.13, hyprlock, kitty.

**Spec:** `docs/superpowers/specs/2026-07-17-socle-palette-clair-obscur-design.md`

## Global Constraints

- **Zéro dépendance externe.** Python stdlib uniquement (`tomllib`, `unittest`). `pytest` n'est pas installé et ne doit pas être ajouté.
- **Aucun hex de la palette en dur** hors `palette.toml`, fragments générés, **et tests**. Les tests codent en dur leurs valeurs attendues : un test qui lit son attendu depuis le code testé n'assure rien. Le critère d'acceptation exclut donc `tests/`.
- **Tout fichier généré porte l'en-tête** `GÉNÉRÉ PAR bin/generate_theme.py — NE PAS ÉDITER — source: palette.toml`, avec le préfixe de commentaire de sa syntaxe (`--` en Lua, `/* */` en CSS/rasi, `#` ailleurs).
- **Les fichiers générés sont versionnés.** Le repo doit rester clonable et utilisable sans lancer le script.
- **Idempotence.** Deux passages consécutifs du générateur ne produisent aucun diff git.
- **Seuils de contraste** : rôles d'interface ≥ 4,5:1 ; ANSI ≥ 3:1, `black` exempté (seul exempté).
- **Wayland uniquement.** Aucun outil X11.
- **Le générateur ne lit ni n'écrit jamais dans `~`.** Il écrit dans le repo ; c'est stow qui relie au home.
- **`~/.config/{hypr,waybar,rofi,dunst,kitty}` sont de vrais dossiers**, pas des symlinks (deux paquets partagent `~/.config/hypr`, donc stow ne peut pas les replier). Conséquence : **un fichier ajouté au repo n'apparaît pas tout seul dans `~/.config`**. Toute tâche qui ajoute un fichier à un paquet doit faire `stow -R <paquet>` avant de vérifier en live.

## Contexte découvert en pré-vol

Un **shadow config violet** existe hors du repo — un thème violet/magenta/saumon (`#070307` / `#FFB3A3` / `#2C178A` / `#852E69`) construit à la main le 15 juillet, cohérent sur quatre outils, **plus récent que la palette dorée du repo** (11 juillet).

Décision de l'auteur du repo, prise en pré-vol : **l'or est la direction retenue, le violet était un essai abandonné.** Les cinq fichiers concernés sont sauvegardés puis supprimés en Task 5.

Un seul d'entre eux est réellement actif : `~/.config/dunst/dunstrc`, lu directement par dunst. Les `colors.css` et `colors.rasi` violets sont morts — rien ne les importe.

## Ordre d'exécution

Les polices et la purge stow passent **avant** tout câblage : sans elles, les vérifications live des Tasks 6–10 échouent ou passent sur des replis silencieux.

| # | Tâche | Pourquoi ici |
|---|---|---|
| 1 | palette.toml + moteur de contraste | fondation |
| 2 | Émetteurs des cinq fragments | fondation |
| 3 | dunstrc depuis template | fondation |
| 4 | Polices | les Tasks 6–10 vérifient du Cormorant/Cinzel à l'œil |
| 5 | Purge du shadow config + stow | **sans ça, Task 6 fait planter Hyprland** |
| 6 | Hyprland + polkit + double bind | |
| 7 | waybar | |
| 8 | rofi | |
| 9 | hyprlock | |
| 10 | kitty | |
| 11 | README + recette d'acceptation | |

---

### Task 1: palette.toml + moteur de contraste

**Files:**
- Create: `palette.toml`
- Create: `bin/generate_theme.py`
- Create: `tests/test_generate_theme.py`

**Interfaces:**
- Consumes: rien (première tâche)
- Produces:
  - `load_palette(path: Path, variant: str | None = None) -> dict` — retourne `{"roles": {str: str}, "ansi": {str: str}}`, hex en `#rrggbb` minuscules. `variant=None` → `meta.default_variant`. Lève `KeyError` si la variante n'existe pas.
  - `contrast_ratio(fg_hex: str, bg_hex: str) -> float` — WCAG 2.1, accepte `#rrggbb`.
  - `check_contrast(palette: dict) -> list[str]` — retourne la liste des messages d'échec ; liste vide = tout passe.

- [ ] **Step 1: Écrire `palette.toml`**

Toutes les valeurs ci-dessous sont mesurées, pas estimées. Ne pas les modifier sans relancer `--check-contrast`.

```toml
# =====================================================================
# Palette Clair Obscur — SEULE SOURCE DE VÉRITÉ des couleurs.
#
# Éditer ce fichier, puis :   python3 bin/generate_theme.py
# Vérifier les contrastes :   python3 bin/generate_theme.py --check-contrast
#
# Ne JAMAIS éditer un fichier portant l'en-tête « GÉNÉRÉ PAR ».
# =====================================================================

[meta]
default_variant = "nuit"

# --- Variante nuit -----------------------------------------------------
# Contrastes indiqués sur bg_primary (#0d0b0a).

[variants.nuit.roles]
bg_primary      = "#0d0b0a"  # fond principal
bg_secondary    = "#1a1512"  # barre, surfaces plates
bg_elevated     = "#241d18"  # popup rofi — doit se détacher de la barre
accent_gold     = "#c9a961"  # 8,73:1  — accent principal
accent_gold_dim = "#8a7442"  #         — inactif / survol, dégradé de bordure
accent_red      = "#7a1f1f"  # 1,91:1  — FOND UNIQUEMENT (illisible en texte)
text_primary    = "#e8dcc8"  # 14,50:1
text_muted      = "#857b6e"  # 4,73:1
border_active   = "#c9a961"
border_inactive = "#3d3730"

# --- ANSI : pigments d'époque ------------------------------------------
# La palette n'a ni vert ni bleu ; tout décliner en or rendrait `git diff`
# illisible. Ces teintes sont désaturées et chaudes pour rester dans
# l'univers visuel, tout en restant discriminables.
#
# Écart rouge/vert délibéré (3,85 vs 5,93) : la différence de luminosité,
# et pas seulement de teinte, garde les diffs lisibles en deutéranopie.
#
# `black` est exempté du seuil de 3:1 — dans un thème sombre, l'ANSI black
# EST la couleur de fond. C'est le seul exempté.

[variants.nuit.ansi]
black          = "#1a1512"  #  1,08:1  exempté — couleur de fond par convention
red            = "#b84a4a"  #  3,85:1  garance
green          = "#7d9470"  #  5,93:1  vert-de-gris
yellow         = "#c9a961"  #  8,73:1  or
blue           = "#5a7186"  #  3,87:1  bleu de Prusse délavé
magenta        = "#7a5f73"  #  3,47:1  mauve fané
cyan           = "#5f7373"  #  3,91:1  céladon
white          = "#e8dcc8"  # 14,50:1  crème
bright_black   = "#6b6459"  #  3,36:1  commentaires — doit rester lisible
bright_red     = "#d16a6a"  #  5,59:1
bright_green   = "#9ab08d"  #  8,39:1
bright_yellow  = "#e0c485"  # 11,60:1
bright_blue    = "#7b93a8"  #  6,15:1
bright_magenta = "#9d7e96"  #  5,48:1
bright_cyan    = "#7f9696"  #  6,27:1
bright_white   = "#f5ecdd"  # 16,76:1
```

- [ ] **Step 2: Écrire les tests qui échouent**

```python
# tests/test_generate_theme.py
import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# bin/ n'est pas un paquet Python : on charge le module par chemin.
_spec = importlib.util.spec_from_file_location(
    "generate_theme", REPO / "bin" / "generate_theme.py"
)
generate_theme = importlib.util.module_from_spec(_spec)
sys.modules["generate_theme"] = generate_theme
_spec.loader.exec_module(generate_theme)


class TestContrastRatio(unittest.TestCase):
    def test_blanc_sur_noir_est_21(self):
        self.assertAlmostEqual(
            generate_theme.contrast_ratio("#ffffff", "#000000"), 21.0, places=2
        )

    def test_identique_est_1(self):
        self.assertAlmostEqual(
            generate_theme.contrast_ratio("#c9a961", "#c9a961"), 1.0, places=2
        )

    def test_symetrique(self):
        a = generate_theme.contrast_ratio("#e8dcc8", "#0d0b0a")
        b = generate_theme.contrast_ratio("#0d0b0a", "#e8dcc8")
        self.assertAlmostEqual(a, b, places=6)

    def test_valeur_connue_de_la_palette(self):
        # text_muted retenu = 4,73:1 sur bg_primary (mesuré au design).
        self.assertAlmostEqual(
            generate_theme.contrast_ratio("#857b6e", "#0d0b0a"), 4.73, places=2
        )


class TestLoadPalette(unittest.TestCase):
    def test_charge_la_variante_par_defaut(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertEqual(p["roles"]["accent_gold"], "#c9a961")
        self.assertEqual(p["ansi"]["red"], "#b84a4a")

    def test_variante_explicite(self):
        p = generate_theme.load_palette(REPO / "palette.toml", variant="nuit")
        self.assertEqual(p["roles"]["bg_primary"], "#0d0b0a")

    def test_variante_inconnue_leve_keyerror(self):
        with self.assertRaises(KeyError):
            generate_theme.load_palette(REPO / "palette.toml", variant="inexistante")

    def test_les_16_ansi_sont_presentes(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertEqual(len(p["ansi"]), 16)


class TestCheckContrast(unittest.TestCase):
    def test_la_palette_livree_passe(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertEqual(generate_theme.check_contrast(p), [])

    def test_detecte_un_role_trop_faible(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        p["roles"]["text_muted"] = "#6b6459"  # 3,36:1 — sous le seuil AA
        echecs = generate_theme.check_contrast(p)
        self.assertTrue(any("text_muted" in e for e in echecs))

    def test_black_est_exempte(self):
        # black est à 1,08:1 dans la palette livrée et ne doit PAS échouer.
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertEqual(generate_theme.check_contrast(p), [])

    def test_detecte_un_ansi_trop_faible(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        p["ansi"]["bright_black"] = "#3d3730"  # 1,67:1 — commentaires illisibles
        echecs = generate_theme.check_contrast(p)
        self.assertTrue(any("bright_black" in e for e in echecs))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Lancer les tests pour vérifier qu'ils échouent**

```bash
python3 -m unittest discover -s tests -v
```

Attendu : `FileNotFoundError` ou `AttributeError` — `bin/generate_theme.py` n'existe pas encore.

- [ ] **Step 4: Écrire l'implémentation minimale**

```python
#!/usr/bin/env python3
"""Génère les fragments de couleurs de chaque outil depuis palette.toml.

Seul palette.toml s'édite à la main. Ce script est la seule chose qui écrit
les fichiers portant l'en-tête « GÉNÉRÉ PAR ».
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Rôles d'interface portant du texte, vérifiés sur bg_primary.
# accent_red en est absent volontairement : à 1,91:1 il est illisible en texte
# et n'est utilisé QUE comme fond (voir PAIRES_FOND ci-dessous).
ROLES_TEXTE = ("text_primary", "text_muted", "accent_gold")

# (texte, fond) — couples où un rôle sert de fond à un autre.
PAIRES_FOND = (("text_primary", "accent_red"),)

# black est la couleur de fond par convention dans un thème sombre : le seuil
# n'a pas de sens pour lui. C'est le SEUL exempté.
ANSI_EXEMPTES = ("black",)

SEUIL_INTERFACE = 4.5
SEUIL_ANSI = 3.0


def _canal_lineaire(valeur_octet: int) -> float:
    c = valeur_octet / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(hex_couleur: str) -> float:
    h = hex_couleur.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return (
        0.2126 * _canal_lineaire(r)
        + 0.7152 * _canal_lineaire(g)
        + 0.0722 * _canal_lineaire(b)
    )


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """Ratio de contraste WCAG 2.1 entre deux couleurs #rrggbb."""
    a, b = _luminance(fg_hex), _luminance(bg_hex)
    clair, sombre = max(a, b), min(a, b)
    return (clair + 0.05) / (sombre + 0.05)


def load_palette(path: Path, variant: str | None = None) -> dict:
    """Charge une variante de palette.toml.

    Lève KeyError si la variante demandée n'existe pas.
    """
    with open(path, "rb") as f:
        data = tomllib.load(f)
    nom = variant or data["meta"]["default_variant"]
    if nom not in data["variants"]:
        raise KeyError(f"variante inconnue : {nom!r}")
    v = data["variants"][nom]
    return {
        "roles": {k: val.lower() for k, val in v["roles"].items()},
        "ansi": {k: val.lower() for k, val in v["ansi"].items()},
    }


def check_contrast(palette: dict) -> list[str]:
    """Retourne la liste des échecs de contraste. Liste vide = tout passe."""
    echecs: list[str] = []
    roles, ansi = palette["roles"], palette["ansi"]
    fond = roles["bg_primary"]

    for nom in ROLES_TEXTE:
        r = contrast_ratio(roles[nom], fond)
        if r < SEUIL_INTERFACE:
            echecs.append(
                f"rôle {nom} ({roles[nom]}) sur bg_primary : "
                f"{r:.2f}:1 < {SEUIL_INTERFACE}:1"
            )

    for texte, arriere in PAIRES_FOND:
        r = contrast_ratio(roles[texte], roles[arriere])
        if r < SEUIL_INTERFACE:
            echecs.append(
                f"rôle {texte} sur {arriere} : {r:.2f}:1 < {SEUIL_INTERFACE}:1"
            )

    for nom, val in ansi.items():
        if nom in ANSI_EXEMPTES:
            continue
        r = contrast_ratio(val, fond)
        if r < SEUIL_ANSI:
            echecs.append(
                f"ansi {nom} ({val}) sur bg_primary : {r:.2f}:1 < {SEUIL_ANSI}:1"
            )

    return echecs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", default=None, help="variante à générer")
    ap.add_argument(
        "--check-contrast",
        action="store_true",
        help="vérifie les contrastes et sort en erreur si un seuil est franchi",
    )
    args = ap.parse_args(argv)

    palette = load_palette(REPO / "palette.toml", args.variant)

    if args.check_contrast:
        echecs = check_contrast(palette)
        for e in echecs:
            print(f"ÉCHEC {e}", file=sys.stderr)
        if echecs:
            return 1
        print("contrastes : tout passe")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Lancer les tests pour vérifier qu'ils passent**

```bash
python3 -m unittest discover -s tests -v
```

Attendu : `OK` — 10 tests.

- [ ] **Step 6: Vérifier le CLI à la main**

```bash
python3 bin/generate_theme.py --check-contrast; echo "exit=$?"
```

Attendu : `contrastes : tout passe` puis `exit=0`.

- [ ] **Step 7: Commit**

```bash
git add palette.toml bin/generate_theme.py tests/test_generate_theme.py
git commit -m "feat: palette.toml + moteur de contraste vérifiable"
```

---

### Task 2: Émetteurs des cinq fragments

**Files:**
- Modify: `bin/generate_theme.py`
- Modify: `tests/test_generate_theme.py`
- Create (générés) : `hypr/.config/hypr/colors.lua`, `waybar/.config/waybar/colors.css`, `rofi/.config/rofi/colors.rasi`, `hyprlock/.config/hypr/colors.conf`, `kitty/.config/kitty/colors.conf`

**Interfaces:**
- Consumes: `load_palette`, `check_contrast` (Task 1)
- Produces:
  - `emit_lua(palette: dict) -> str`
  - `emit_css(palette: dict) -> str`
  - `emit_rasi(palette: dict) -> str`
  - `emit_hyprlang(palette: dict) -> str`
  - `emit_kitty(palette: dict) -> str`
  - `header(prefixe: str, suffixe: str = "") -> str`
  - `_AVERTISSEMENT: str` — le texte d'avertissement nu, sans préfixe de commentaire
  - `CIBLES: tuple[tuple[str, callable], ...]` — (chemin relatif, émetteur)
  - `write_all(palette: dict) -> list[Path]` — écrit les fragments, retourne les chemins écrits.

Format des couleurs par outil, à respecter exactement :
- Lua → `"rgb(c9a961)"` (Hyprland veut `rgb(...)`, pas `#...`)
- CSS → `@define-color accent_gold #c9a961;`
- rasi → `accent-gold: #c9a961;` dans un bloc `* { }` (on normalise les underscores en tirets)
- hyprlang → `$accent_gold = rgb(c9a961)`
- kitty → `color3 #c9a961` + `foreground`/`background`

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter à `tests/test_generate_theme.py` :

```python
class TestEmetteurs(unittest.TestCase):
    def setUp(self):
        self.p = generate_theme.load_palette(REPO / "palette.toml")

    def test_lua_est_une_table_avec_rgb(self):
        out = generate_theme.emit_lua(self.p)
        self.assertIn("return {", out)
        self.assertIn('accent_gold = "rgb(c9a961)"', out)
        self.assertTrue(out.startswith("--"))  # en-tête en commentaire Lua

    def test_css_utilise_define_color(self):
        out = generate_theme.emit_css(self.p)
        self.assertIn("@define-color accent_gold #c9a961;", out)
        self.assertTrue(out.startswith("/*"))

    def test_rasi_normalise_en_tirets(self):
        out = generate_theme.emit_rasi(self.p)
        self.assertIn("accent-gold: #c9a961;", out)
        self.assertIn("* {", out)

    def test_hyprlang_utilise_des_variables(self):
        out = generate_theme.emit_hyprlang(self.p)
        self.assertIn("$accent_gold = rgb(c9a961)", out)
        self.assertTrue(out.startswith("#"))

    def test_kitty_mappe_les_16_ansi(self):
        out = generate_theme.emit_kitty(self.p)
        self.assertIn("color3 #c9a961", out)   # yellow = or
        self.assertIn("color15 #f5ecdd", out)  # bright_white
        self.assertIn("background #0d0b0a", out)
        self.assertIn("foreground #e8dcc8", out)

    def test_tous_les_fragments_portent_l_entete(self):
        for emetteur in (
            generate_theme.emit_lua,
            generate_theme.emit_css,
            generate_theme.emit_rasi,
            generate_theme.emit_hyprlang,
            generate_theme.emit_kitty,
        ):
            self.assertIn("NE PAS ÉDITER", emetteur(self.p))
            self.assertIn("palette.toml", emetteur(self.p))


class TestIdempotence(unittest.TestCase):
    def test_deux_passages_donnent_le_meme_contenu(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        emetteurs = (
            generate_theme.emit_lua, generate_theme.emit_css,
            generate_theme.emit_rasi, generate_theme.emit_hyprlang,
            generate_theme.emit_kitty,
        )
        premier = {e.__name__: e(p) for e in emetteurs}
        second = {e.__name__: e(p) for e in emetteurs}
        self.assertEqual(premier, second)
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

```bash
python3 -m unittest discover -s tests -v
```

Attendu : `AttributeError: module 'generate_theme' has no attribute 'emit_lua'`.

- [ ] **Step 3: Implémenter les émetteurs**

Ajouter à `bin/generate_theme.py`, avant `main()` :

```python
# Ordre ANSI de kitty : color0..color15
ORDRE_ANSI = (
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "bright_black", "bright_red", "bright_green", "bright_yellow",
    "bright_blue", "bright_magenta", "bright_cyan", "bright_white",
)

_AVERTISSEMENT = (
    "GÉNÉRÉ PAR bin/generate_theme.py — NE PAS ÉDITER — source: palette.toml"
)


def header(prefixe: str, suffixe: str = "") -> str:
    """En-tête d'avertissement dans la syntaxe de commentaire de la cible."""
    return f"{prefixe} {_AVERTISSEMENT}{suffixe}\n"


def _rgb(hex_couleur: str) -> str:
    """#c9a961 -> rgb(c9a961) — format attendu par Hyprland et hyprlang."""
    return f"rgb({hex_couleur.lstrip('#')})"


def emit_lua(palette: dict) -> str:
    lignes = [header("--"), "return {"]
    for nom, val in palette["roles"].items():
        lignes.append(f'    {nom} = "{_rgb(val)}",')
    lignes.append("    ansi = {")
    for nom, val in palette["ansi"].items():
        lignes.append(f'        {nom} = "{val}",')
    lignes.append("    },")
    lignes.append("}")
    return "\n".join(lignes) + "\n"


def emit_css(palette: dict) -> str:
    lignes = [header("/*", " */")]
    for nom, val in palette["roles"].items():
        lignes.append(f"@define-color {nom} {val};")
    return "\n".join(lignes) + "\n"


def emit_rasi(palette: dict) -> str:
    lignes = [header("/*", " */"), "* {"]
    for nom, val in palette["roles"].items():
        lignes.append(f"    {nom.replace('_', '-')}: {val};")
    lignes.append("}")
    return "\n".join(lignes) + "\n"


def emit_hyprlang(palette: dict) -> str:
    lignes = [header("#")]
    for nom, val in palette["roles"].items():
        lignes.append(f"${nom} = {_rgb(val)}")
    return "\n".join(lignes) + "\n"


def emit_kitty(palette: dict) -> str:
    roles, ansi = palette["roles"], palette["ansi"]
    lignes = [
        header("#"),
        f"background {roles['bg_primary']}",
        f"foreground {roles['text_primary']}",
        f"cursor {roles['accent_gold']}",
        f"selection_background {roles['bg_elevated']}",
        f"selection_foreground {roles['text_primary']}",
        "",
    ]
    for i, nom in enumerate(ORDRE_ANSI):
        lignes.append(f"color{i} {ansi[nom]}")
    return "\n".join(lignes) + "\n"


CIBLES = (
    ("hypr/.config/hypr/colors.lua", emit_lua),
    ("waybar/.config/waybar/colors.css", emit_css),
    ("rofi/.config/rofi/colors.rasi", emit_rasi),
    ("hyprlock/.config/hypr/colors.conf", emit_hyprlang),
    ("kitty/.config/kitty/colors.conf", emit_kitty),
)


def write_all(palette: dict) -> list[Path]:
    """Écrit tous les fragments. Retourne les chemins écrits."""
    ecrits = []
    for rel, emetteur in CIBLES:
        chemin = REPO / rel
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(emetteur(palette), encoding="utf-8")
        ecrits.append(chemin)
    return ecrits
```

Puis brancher dans `main()`, en remplaçant le `return 0` final :

```python
    echecs = check_contrast(palette)
    if echecs:
        for e in echecs:
            print(f"ÉCHEC {e}", file=sys.stderr)
        print("génération annulée : corriger palette.toml", file=sys.stderr)
        return 1

    for chemin in write_all(palette):
        print(f"écrit {chemin.relative_to(REPO)}")
    return 0
```

Le contrôle de contraste tourne donc **avant chaque génération** : une palette qui échoue ne peut pas atteindre les fichiers.

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

```bash
python3 -m unittest discover -s tests -v
```

Attendu : `OK` — 18 tests.

- [ ] **Step 5: Générer les fragments**

```bash
python3 bin/generate_theme.py
```

Attendu : cinq lignes `écrit …`.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: émetteurs des cinq fragments de couleurs"
```

- [ ] **Step 7: Vérifier l'idempotence sur disque**

```bash
python3 bin/generate_theme.py
git diff --exit-code; echo "idempotent si exit=0 : $?"
```

Attendu : `exit=0`, aucun diff. Un diff ici signifie que le générateur n'est pas déterministe — corriger avant de continuer.

---

### Task 3: dunstrc généré depuis un template

**Files:**
- Create: `templates/dunstrc.in`
- Modify: `bin/generate_theme.py`
- Modify: `tests/test_generate_theme.py`
- Create (généré) : `dunst/.config/dunst/dunstrc`

**Interfaces:**
- Consumes: `load_palette` (Task 1) ; `_AVERTISSEMENT` et `CIBLES` (Task 2). N'utilise **pas** `header()` : le template porte son propre `{{HEADER}}`, avec le `#` déjà en place.
- Produces: `emit_dunstrc(palette: dict) -> str` — lit `templates/dunstrc.in`, substitue `{{HEADER}}` puis chaque `{{role}}`.

Dunst ne supporte ni `include` ni variables : son `dunstrc` est généré **en entier**. C'est la seule exception du repo.

Rappel du design (contrainte de contraste) : l'urgence critique est un **bandeau plein** (`accent_red` en fond, `text_primary` dessus = 7,59:1), pas un liseré — `accent_red` sur `bg_primary` donne 1,91:1 et serait invisible.

- [ ] **Step 1: Écrire le test qui échoue**

Ajouter à `tests/test_generate_theme.py` :

```python
class TestDunstrc(unittest.TestCase):
    def setUp(self):
        self.p = generate_theme.load_palette(REPO / "palette.toml")
        self.out = generate_theme.emit_dunstrc(self.p)

    def test_porte_l_entete(self):
        self.assertIn("NE PAS ÉDITER", self.out)

    def test_aucun_placeholder_ne_subsiste(self):
        self.assertNotIn("{{", self.out)
        self.assertNotIn("}}", self.out)

    def test_les_couleurs_sont_entre_guillemets(self):
        # dunst interprète un # non quoté comme un commentaire.
        self.assertIn('background = "#1a1512"', self.out)

    def test_critical_est_un_bandeau_rouge_a_texte_creme(self):
        bloc = self.out.split("[urgency_critical]")[1]
        self.assertIn('background = "#7a1f1f"', bloc)
        self.assertIn('foreground = "#e8dcc8"', bloc)

    def test_les_trois_urgences_sont_presentes(self):
        for section in ("[urgency_low]", "[urgency_normal]", "[urgency_critical]"):
            self.assertIn(section, self.out)
```

- [ ] **Step 2: Lancer le test pour vérifier qu'il échoue**

```bash
python3 -m unittest discover -s tests -v
```

Attendu : `AttributeError: module 'generate_theme' has no attribute 'emit_dunstrc'`.

- [ ] **Step 3: Écrire `templates/dunstrc.in`**

```ini
# {{HEADER}}

[global]
    monitor = 0
    follow = mouse
    width = 340
    height = (0, 300)
    origin = top-right
    offset = (16, 16)
    scale = 0
    notification_limit = 5

    progress_bar = true
    progress_bar_height = 8
    progress_bar_frame_width = 1
    progress_bar_min_width = 150
    progress_bar_max_width = 300

    indicate_hidden = yes
    transparency = 8
    separator_height = 2
    padding = 14
    horizontal_padding = 16
    text_icon_padding = 12
    frame_width = 2
    frame_color = "{{border_inactive}}"
    separator_color = frame
    corner_radius = 8
    gap_size = 6

    sort = yes
    font = Cormorant Garamond 12
    line_height = 0
    markup = full
    format = "<b>%s</b>\n%b"
    alignment = left
    vertical_alignment = center
    show_age_threshold = 60
    ellipsize = middle
    ignore_newline = no
    stack_duplicates = true
    hide_duplicate_count = false
    show_indicators = yes

    enable_recursive_icon_lookup = true
    icon_theme = Adwaita
    icon_position = left
    min_icon_size = 32
    max_icon_size = 48

    sticky_history = yes
    history_length = 20

    dmenu = /usr/bin/rofi -dmenu -p dunst
    browser = /usr/bin/firefox
    always_run_script = true
    title = Dunst
    class = Dunst

    mouse_left_click = do_action, close_current
    mouse_middle_click = close_all
    mouse_right_click = close_current

[urgency_low]
    background = "{{bg_secondary}}"
    foreground = "{{text_muted}}"
    frame_color = "{{border_inactive}}"
    timeout = 8
    default_icon = dialog-information

[urgency_normal]
    background = "{{bg_secondary}}"
    foreground = "{{text_primary}}"
    frame_color = "{{accent_gold_dim}}"
    timeout = 10
    override_pause_level = 30
    default_icon = dialog-information

# accent_red sur bg_primary ne donne que 1,91:1 : un liseré rouge serait
# invisible. L'urgence critique est donc un bandeau plein — text_primary sur
# accent_red donne 7,59:1.
[urgency_critical]
    background = "{{accent_red}}"
    foreground = "{{text_primary}}"
    frame_color = "{{accent_gold}}"
    timeout = 0
    override_pause_level = 60
    default_icon = dialog-warning
```

- [ ] **Step 4: Implémenter `emit_dunstrc`**

Ajouter à `bin/generate_theme.py`, après `emit_kitty` et **avant** `CIBLES` :

```python
def emit_dunstrc(palette: dict) -> str:
    """Génère le dunstrc ENTIER : dunst ne sait ni importer ni utiliser de variables."""
    gabarit = (REPO / "templates" / "dunstrc.in").read_text(encoding="utf-8")
    sortie = gabarit.replace("{{HEADER}}", _AVERTISSEMENT)
    for nom, val in palette["roles"].items():
        sortie = sortie.replace(f"{{{{{nom}}}}}", val)
    if "{{" in sortie or "}}" in sortie:
        raise ValueError(
            "placeholder non substitué dans templates/dunstrc.in — "
            "un rôle du template n'existe pas dans palette.toml"
        )
    return sortie
```

Puis ajouter la cible à `CIBLES` :

```python
CIBLES = (
    ("hypr/.config/hypr/colors.lua", emit_lua),
    ("waybar/.config/waybar/colors.css", emit_css),
    ("rofi/.config/rofi/colors.rasi", emit_rasi),
    ("hyprlock/.config/hypr/colors.conf", emit_hyprlang),
    ("kitty/.config/kitty/colors.conf", emit_kitty),
    ("dunst/.config/dunst/dunstrc", emit_dunstrc),
)
```

- [ ] **Step 5: Lancer les tests pour vérifier qu'ils passent**

```bash
python3 -m unittest discover -s tests -v
```

Attendu : `OK` — 23 tests.

- [ ] **Step 6: Vérifier que dunst accepte le fichier**

```bash
python3 bin/generate_theme.py
dunst --config dunst/.config/dunst/dunstrc --print 2>&1 | head -20; echo "exit=$?"
```

Attendu : dunst imprime sa config sans erreur de parsing. Toute ligne `CRITICAL` ou `WARNING: Unknown setting` est un échec à corriger.

Note : ce contrôle utilise `--config` avec un chemin explicite, donc il ne dépend pas de stow (réparé en Task 5).

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: dunstrc généré depuis template (dunst n'a ni include ni variables)"
```

---

### Task 4: Script d'installation des polices

**Files:**
- Create: `bin/install-fonts.sh`

**Interfaces:**
- Consumes: rien
- Produces: `Cormorant Garamond` et `Cinzel` résolvables par `fc-match`. Les Tasks 6–10 les référencent et vérifient leur rendu à l'œil.

Cette tâche passe **avant** les câblages : sans les polices, les vérifications visuelles des Tasks 6–10 passeraient sur un repli fontconfig silencieux, exactement le bug `JetBrainMono` qu'on répare par ailleurs.

Les polices ne sont pas versionnées (binaires ; licence OFL redistribuable mais encombrante) — d'où ce script. Pas d'AUR, pas de compilation.

- [ ] **Step 1: Écrire le script**

```bash
#!/usr/bin/env bash
# Installe les polices d'affichage Clair Obscur depuis Google Fonts.
# Idempotent : ne retélécharge pas ce qui est déjà résolvable.
set -euo pipefail

DEST="${HOME}/.local/share/fonts"
TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

BASE="https://github.com/google/fonts/raw/main/ofl"

# famille -> chemin distant relatif à BASE
declare -A CHEMINS=(
    ["Cormorant Garamond"]="cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"
    ["Cinzel"]="cinzel/Cinzel%5Bwght%5D.ttf"
)

# famille -> nom de fichier local
declare -A FICHIERS=(
    ["Cormorant Garamond"]="CormorantGaramond.ttf"
    ["Cinzel"]="Cinzel.ttf"
)

mkdir -p "${DEST}"
installe=0

for famille in "${!CHEMINS[@]}"; do
    if fc-list : family | grep -qiF "${famille}"; then
        echo "déjà présente : ${famille}"
        continue
    fi
    url="${BASE}/${CHEMINS[$famille]}"
    cible="${TMP}/${FICHIERS[$famille]}"
    echo "téléchargement : ${famille}"
    if ! curl -fsSL "${url}" -o "${cible}"; then
        echo "ÉCHEC du téléchargement de ${famille} depuis ${url}" >&2
        exit 1
    fi
    # Un dépôt qui répond du HTML au lieu d'une police est une panne silencieuse.
    if ! file "${cible}" | grep -qiE 'truetype|opentype|font'; then
        echo "ÉCHEC : ${cible} n'est pas une police (dépôt déplacé ?)" >&2
        exit 1
    fi
    mv "${cible}" "${DEST}/"
    installe=1
done

if [[ "${installe}" -eq 1 ]]; then
    echo "reconstruction du cache fontconfig…"
    fc-cache -f >/dev/null
fi

echec=0
for famille in "${!CHEMINS[@]}"; do
    resolu="$(fc-match "${famille}")"
    attendu="$(echo "${famille}" | tr -d ' ')"
    if echo "${resolu}" | grep -qiF "${attendu}"; then
        echo "OK  ${famille} → ${resolu}"
    else
        echo "ÉCHEC ${famille} ne se résout pas : ${resolu}" >&2
        echec=1
    fi
done
exit "${echec}"
```

- [ ] **Step 2: Rendre exécutable et lancer**

```bash
chmod +x bin/install-fonts.sh
./bin/install-fonts.sh; echo "exit=$?"
```

Attendu : les deux polices se téléchargent, `fc-cache` tourne, deux lignes `OK`, `exit=0`.

Si le téléchargement échoue (URL Google Fonts déplacée), **s'arrêter et le signaler** — ne pas contourner en installant une police approchante.

- [ ] **Step 3: Vérifier l'idempotence**

```bash
./bin/install-fonts.sh; echo "exit=$?"
```

Attendu : `déjà présente : …` deux fois, aucun téléchargement, `exit=0`.

- [ ] **Step 4: Vérifier la résolution des trois polices**

```bash
fc-match "Cormorant Garamond"
fc-match "Cinzel"
fc-match "JetBrainsMono Nerd Font"
```

Attendu : chaque commande résout vers la bonne famille, et **pas** vers un repli type `DejaVuSans.ttf` ou `NotoSansMono-Regular.ttf`.

- [ ] **Step 5: Commit**

```bash
git add bin/install-fonts.sh
git commit -m "feat: script d'installation des polices Cormorant Garamond et Cinzel"
```

---

### Task 5: Purger le shadow config + réparer la dérive stow

**Files:**
- Delete: `colors/colors.conf` et le dossier `colors/` (vestigial)
- Delete (hors repo) : cinq vrais fichiers de `~/.config/` — voir ci-dessous

**Interfaces:**
- Consumes: les six fragments générés (Tasks 2–3) — ils doivent exister avant le stow.
- Produces: `~/.config/**` entièrement en symlinks vers le repo. **Les Tasks 6–10 en dépendent** : sans ça, leurs vérifications live lisent les anciens fichiers.

**Cette tâche est bloquante pour tout le câblage.** `hyprland.lua` fait `dofile("~/.config/hypr/colors.lua")` : tant que ce chemin pointe sur le vieux fichier violet (qui n'a que `active_border` / `inactive_border`), `colors.accent_gold` vaut `nil` et Hyprland refuse la config.

Cinq vrais fichiers à supprimer :

| Fichier | Contenu | Perte ? |
|---|---|---|
| `~/.config/hypr/hyprpaper.conf` | identique au repo | aucune (vérifié par `diff`) |
| `~/.config/hypr/colors.lua` | thème violet abandonné | sauvegardé |
| `~/.config/waybar/colors.css` | thème violet abandonné | sauvegardé |
| `~/.config/rofi/colors.rasi` | thème violet abandonné | sauvegardé |
| `~/.config/dunst/dunstrc` | thème violet abandonné — **seul réellement actif** | sauvegardé |

Le dossier `colors/` n'a jamais été stowable (pas de sous-dossier `.config/`) — c'était un vestige. Son contenu vit dans `palette.toml`.

- [ ] **Step 1: Sauvegarder les cinq fichiers avant toute suppression**

```bash
mkdir -p /tmp/dotfiles-backup
for f in ~/.config/hypr/colors.lua ~/.config/hypr/hyprpaper.conf \
         ~/.config/waybar/colors.css ~/.config/rofi/colors.rasi \
         ~/.config/dunst/dunstrc; do
    [ -f "$f" ] && [ ! -L "$f" ] && cp -v "$f" "/tmp/dotfiles-backup/$(echo "${f#$HOME/.config/}" | tr '/' '-')"
done
ls -l /tmp/dotfiles-backup/
```

Attendu : cinq fichiers sauvegardés. **Si un fichier manque, s'arrêter et le signaler** — l'état du système a divergé de l'analyse.

- [ ] **Step 2: Confirmer que hyprpaper.conf n'a rien d'unique à perdre**

```bash
diff ~/.config/hypr/hyprpaper.conf hypr/.config/hypr/hyprpaper.conf && echo "IDENTIQUES — suppression sans perte"
```

Attendu : `IDENTIQUES`. **Si le diff n'est pas vide, s'arrêter** et reporter la différence — le fichier live a divergé depuis l'analyse.

- [ ] **Step 3: Supprimer les cinq vrais fichiers et le dossier vestigial**

```bash
rm -v ~/.config/hypr/colors.lua ~/.config/hypr/hyprpaper.conf \
      ~/.config/waybar/colors.css ~/.config/rofi/colors.rasi \
      ~/.config/dunst/dunstrc
git rm -r --quiet colors/
```

- [ ] **Step 4: Vérifier stow à blanc avant d'agir**

```bash
cd "$(git rev-parse --show-toplevel)"
for p in hypr waybar rofi dunst hyprlock kitty; do
    echo "--- $p"
    stow -n -v -R -t "$HOME" "$p" 2>&1
done
```

Attendu : aucun `CONFLICT`. Un conflit signale un vrai fichier restant — le traiter avant de continuer, ne pas forcer avec `--adopt`.

- [ ] **Step 5: Stow pour de bon**

```bash
stow -R -t "$HOME" hypr waybar rofi dunst hyprlock kitty
```

- [ ] **Step 6: Vérifier que tout est symlink et pointe vers le repo**

```bash
for f in ~/.config/hypr/colors.lua ~/.config/hypr/hyprpaper.conf \
         ~/.config/hypr/hyprland.lua ~/.config/waybar/colors.css \
         ~/.config/rofi/colors.rasi ~/.config/dunst/dunstrc \
         ~/.config/hyprlock.conf ~/.config/kitty/colors.conf; do
    if [ -L "$f" ] && [ -e "$f" ]; then echo "OK      $f"
    elif [ -L "$f" ]; then echo "ÉCHEC   symlink cassé : $f -> $(readlink "$f")"
    else echo "ÉCHEC   pas un symlink : $f"; fi
done
```

Attendu : huit `OK`. Note : `~/.config/hyprlock.conf` n'existe pas — hyprlock est stowé vers `~/.config/hypr/hyprlock.conf`. Corriger la liste si le chemin diffère, mais **ne pas ignorer un ÉCHEC**.

- [ ] **Step 7: Vérifier que le colors.lua livré est bien le doré**

```bash
grep -c 'accent_gold' ~/.config/hypr/colors.lua
grep -c '2C178A' ~/.config/hypr/colors.lua || echo "OK plus de violet"
```

Attendu : `1` ou plus pour `accent_gold`, et `OK plus de violet`.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "fix: purger le shadow config violet, supprimer colors/ vestigial, réparer la dérive stow"
```

---

### Task 6: Brancher Hyprland + réparer polkit et le double bind

**Files:**
- Modify: `hypr/.config/hypr/hyprland.lua` (lignes 42, 57, 299, et le bloc `general.col`)

**Interfaces:**
- Consumes: `hypr/.config/hypr/colors.lua` (Task 2), stowé vers `~/.config/hypr/colors.lua` (Task 5) — table Lua, clés = noms de rôles, valeurs = `"rgb(xxxxxx)"`, plus une sous-table `ansi`.
- Produces: rien pour les tâches suivantes.

Trois bugs réparés ici, tous vérifiés :
- **Palette morte** (l. 42) — `local colors = dofile(...)` chargé, jamais lu.
- **Agent polkit mort** (l. 57) — `authentification` (orthographe française) au lieu de `authentication`. Bug **fonctionnel** : aucune fenêtre d'élévation de privilèges.
- **Double bind `SUPER+SHIFT+S`** (l. 279 et 299).

- [ ] **Step 1: Vérifier l'état de départ**

```bash
sed -n '42p;57p;279p;299p' hypr/.config/hypr/hyprland.lua
grep -n 'active_border' hypr/.config/hypr/hyprland.lua
```

Attendu : la ligne 42 charge `colors`, la 57 contient `authentification`, les 279 et 299 sont toutes deux `SHIFT + S`, et `active_border` vaut encore le cyan/vert du template (`33ccffee` / `00ff99ee`).

Les numéros de ligne sont indicatifs — si le fichier a bougé, se repérer sur le contenu.

- [ ] **Step 2: Ne pas toucher au chemin du `dofile` (ligne 42)**

Le `dofile` pointe vers `~/.config/hypr/colors.lua`, qui est désormais un symlink vers le fragment généré (Task 5). Le chemin est correct — **ne pas le modifier**.

- [ ] **Step 3: Brancher les couleurs sur les bordures**

Remplacer le bloc `col` dans `hl.config({ general = { ... } })` :

```lua
        col = {
            active_border   = { colors = { colors.accent_gold, colors.accent_gold_dim }, angle = 45 },
            inactive_border = colors.border_inactive,
        },
```

La fenêtre focus est « éclairée » par un dégradé or → or éteint à 45° ; les autres s'effacent dans le brun sourd. C'est le motif clarté/obscurité en une ligne.

- [ ] **Step 4: Réparer l'agent polkit (ligne 57)**

```lua
  hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
```

Deux changements : `authentification` → `authentication`, et `hl.exec` → `hl.exec_cmd` pour rester cohérent avec les autres lignes de l'autostart.

- [ ] **Step 5: Réparer le double bind (ligne 299)**

```lua
hl.bind(mainMod .. " + SHIFT + X", hl.dsp.window.move({ workspace = "special:magic" }))
```

`SHIFT+X` est libre (vérifié : aucune occurrence). `SHIFT+M` (sortie), `SHIFT+F`, `SHIFT+B`, `SHIFT+P` et `SHIFT+[0-9]` sont pris. La ligne 279 (capture d'écran) reste inchangée.

- [ ] **Step 6: Vérifier qu'aucun bind n'est déclaré deux fois**

```bash
grep -oE 'mainMod \.\. " \+ [^"]*"' hypr/.config/hypr/hyprland.lua | sort | uniq -d
```

Attendu : **aucune sortie**. Toute ligne affichée est un bind en double.

- [ ] **Step 7: Vérifier que la config se recharge sans erreur**

```bash
hyprctl reload && hyprctl getoption general:col.active_border
```

Attendu : `hyprctl reload` répond `ok`, et `active_border` ne contient plus `33ccff`.

Si Hyprland se plaint d'un `nil`, c'est que Task 5 n'a pas abouti — vérifier `~/.config/hypr/colors.lua`.

- [ ] **Step 8: Commit**

```bash
git add hypr/.config/hypr/hyprland.lua
git commit -m "fix: brancher la palette + réparer l'agent polkit et le double bind SHIFT+S"
```

---

### Task 7: Brancher waybar

**Files:**
- Modify: `waybar/.config/waybar/style.css` (réécriture complète)

**Interfaces:**
- Consumes: `waybar/.config/waybar/colors.css` (Task 2), stowé (Task 5) — `@define-color <role> #hex;`

waybar utilise gtkmm-3.0 (vérifié via `ldd`), donc du CSS GTK3 : `@import` et `@define-color` sont supportés.

Deux corrections : le cyan `#33ccff` disparaît, et la police fantôme `"JetBrainMono Nerd Font"` (sans `s`, résolue en Noto Sans Mono par fontconfig) devient `"JetBrainsMono Nerd Font"`.

- [ ] **Step 1: Écrire `style.css`**

```css
@import "colors.css";

* {
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px;
    border: none;
    border-radius: 0;
    min-height: 0;
}

window#waybar {
    background-color: @bg_secondary;
    color: @text_primary;
}

#workspaces button {
    padding: 0 10px;
    color: @text_muted;
    background-color: transparent;
    border-bottom: 2px solid transparent;
}

/* Clarté/obscurité : l'espace actif est éclairé, les autres s'effacent. */
#workspaces button.active {
    color: @accent_gold;
    border-bottom: 2px solid @accent_gold;
}

#workspaces button:hover {
    color: @accent_gold_dim;
    background-color: @bg_elevated;
}

#clock {
    font-family: "Cormorant Garamond";
    font-size: 16px;
    color: @accent_gold;
    padding: 0 14px;
}

#pulseaudio, #network, #battery, #tray {
    color: @text_primary;
    padding: 0 10px;
}

#battery.warning {
    color: @accent_gold;
}

/* accent_red est illisible en texte (1,91:1) : en état critique il sert de
   fond, avec text_primary dessus (7,59:1). */
#battery.critical {
    background-color: @accent_red;
    color: @text_primary;
}
```

- [ ] **Step 2: Vérifier que waybar démarre sans erreur CSS**

```bash
pkill waybar; sleep 1
timeout 5 waybar -l debug 2>&1 | grep -iE 'error|css' | head -10; echo "---fin---"
```

Attendu : aucune ligne d'erreur CSS entre le lancement et `---fin---`. Une erreur `Failed to import` signalerait que `colors.css` n'est pas à côté de `style.css` dans `~/.config/waybar/` — c'est-à-dire que Task 5 n'a pas abouti.

- [ ] **Step 3: Relancer waybar en fond**

```bash
waybar >/dev/null 2>&1 &
sleep 2; pgrep waybar >/dev/null && echo "OK waybar tourne"
```

- [ ] **Step 4: Vérifier que la police fantôme a disparu**

```bash
grep -c 'JetBrainMono Nerd' waybar/.config/waybar/style.css || echo "OK plus de police fantôme"
grep -c 'JetBrainsMono Nerd' waybar/.config/waybar/style.css
```

Attendu : `OK plus de police fantôme` (aucune occurrence sans `s`), puis `1`.

- [ ] **Step 5: Commit**

```bash
git add waybar/.config/waybar/style.css
git commit -m "feat: waybar sur la palette + fix de la police fantôme JetBrainMono"
```

---

### Task 8: Brancher rofi

**Files:**
- Modify: `rofi/.config/rofi/config.rasi`
- Create: `rofi/.config/rofi/clair-obscur.rasi`

**Interfaces:**
- Consumes: `rofi/.config/rofi/colors.rasi` (Task 2), stowé (Task 5) — bloc `* { }`, noms de rôles **en tirets** (`accent-gold`, pas `accent_gold`).

Abandon du thème stock `Arc-Dark`. rofi 2.0 est Wayland natif (vérifié) — aucun XWayland.

`clair-obscur.rasi` est un **nouveau fichier** dans un paquet déjà stowé : `~/.config/rofi` est un vrai dossier, donc il faut `stow -R rofi` pour qu'il apparaisse.

- [ ] **Step 1: Écrire `clair-obscur.rasi`**

```rasi
@import "colors.rasi"

window {
    width: 640px;
    background-color: @bg-primary;
    border: 2px;
    border-color: @accent-gold-dim;
    border-radius: 8px;
    padding: 0;
}

inputbar {
    background-color: @bg-secondary;
    text-color: @text-primary;
    padding: 14px 16px;
    children: [ prompt, entry ];
}

prompt {
    font: "Cormorant Garamond 15";
    text-color: @accent-gold;
    margin: 0 10px 0 0;
}

entry {
    text-color: @text-primary;
    placeholder: "";
    placeholder-color: @text-muted;
}

listview {
    lines: 8;
    background-color: @bg-primary;
    padding: 8px;
    scrollbar: false;
}

element {
    padding: 8px 12px;
    border-radius: 4px;
    text-color: @text-muted;
    background-color: transparent;
}

/* Clarté/obscurité : l'entrée sélectionnée est éclairée. */
element selected {
    background-color: @bg-elevated;
    text-color: @accent-gold;
}

element-text {
    background-color: transparent;
    text-color: inherit;
}

element-icon {
    size: 22px;
    margin: 0 10px 0 0;
    background-color: transparent;
}
```

- [ ] **Step 2: Écrire `config.rasi`**

```rasi
configuration {
    font: "JetBrainsMono Nerd Font 12";
    show-icons: true;
    display-drun: "";
    drun-display-format: "{name}";
}

@import "clair-obscur.rasi"
```

`@import` relatif, et non `@theme "~/.config/rofi/…"` : l'expansion du `~` par rofi n'est pas garantie, alors qu'un `@import` se résout relativement au fichier qui l'importe. C'est aussi ce qui rend le thème correct quel que soit l'endroit où stow le relie.

- [ ] **Step 3: Re-stow pour que le nouveau fichier apparaisse**

```bash
stow -R -t "$HOME" rofi
ls -l ~/.config/rofi/clair-obscur.rasi
```

Attendu : un symlink vers le repo.

- [ ] **Step 4: Vérifier que rofi parse le thème**

```bash
rofi -dump-theme >/dev/null 2>&1; echo "exit=$?"
rofi -dump-theme 2>&1 | grep -iE 'c9a961|accent' | head -3
```

Attendu : `exit=0`, et le dump montre les couleurs de la palette. Une erreur de parsing s'affiche en clair avec le numéro de ligne.

- [ ] **Step 5: Vérifier à l'œil**

```bash
rofi -show drun
```

Attendu : fond noir chaud, bordure or éteint, entrée sélectionnée en or sur `bg_elevated`, prompt en Cormorant. Fermer avec Échap.

- [ ] **Step 6: Vérifier que la police fantôme a disparu**

```bash
grep -c 'JetBrainMono Nerd' rofi/.config/rofi/config.rasi || echo "OK plus de police fantôme"
```

Attendu : `OK plus de police fantôme`.

- [ ] **Step 7: Commit**

```bash
git add rofi/.config/rofi/
git commit -m "feat: thème rofi Clair Obscur, abandon d'Arc-Dark"
```

---

### Task 9: Brancher hyprlock + réparer le chemin du wallpaper

**Files:**
- Modify: `hyprlock/.config/hypr/hyprlock.conf`

**Interfaces:**
- Consumes: `hyprlock/.config/hypr/colors.conf` (Task 2), stowé (Task 5) — `$<role> = rgb(xxxxxx)`

Bug réparé : `path = ~/Pictures?wallpaper.jpg` — le `?` est une typo, et le fichier s'appelle `wallpaper_clair_obscur.jpg` (vérifié présent).

- [ ] **Step 1: Écrire `hyprlock.conf`**

```conf
source = ~/.config/hypr/colors.conf

background {
    monitor =
    path = ~/Pictures/wallpaper_clair_obscur.jpg
    blur_passes = 3
    blur_size = 8
    brightness = 0.4
    vibrancy = 0.1
}

input-field {
    monitor =
    size = 280, 56
    outline_thickness = 2
    dots_size = 0.25
    dots_spacing = 0.3
    dots_center = true
    outer_color = $accent_gold_dim
    inner_color = $bg_secondary
    font_color = $text_primary
    check_color = $accent_gold
    fail_color = $accent_red
    fade_on_empty = false
    placeholder_text = <i>Mot de passe…</i>
    position = 0, -100
    halign = center
    valign = center
}

label {
    monitor =
    text = cmd[update:1000] echo "$(date +"%H:%M")"
    color = $text_primary
    font_size = 72
    font_family = Cinzel
    position = 0, 150
    halign = center
    valign = center
}

label {
    monitor =
    text = cmd[update:3600000] echo "$(date +"%A %d %B")"
    color = $text_muted
    font_size = 16
    font_family = Cormorant Garamond
    position = 0, 80
    halign = center
    valign = center
}
```

- [ ] **Step 2: Vérifier que le wallpaper existe**

```bash
ls -l ~/Pictures/wallpaper_clair_obscur.jpg
```

Attendu : le fichier existe. S'il est absent, hyprlock affiche un fond noir **sans erreur** — d'où ce contrôle explicite.

- [ ] **Step 3: Re-stow et vérifier que le fragment est lisible**

```bash
stow -R -t "$HOME" hyprlock
ls -l ~/.config/hypr/hyprlock.conf ~/.config/hypr/colors.conf
grep -c 'accent_gold' ~/.config/hypr/colors.conf
```

Attendu : deux symlinks, et au moins une occurrence de `accent_gold`.

- [ ] **Step 4: Vérifier hyprlock**

⚠️ **Ne pas lancer cette étape sans savoir déverrouiller la session.** Si l'implémenteur est un agent sans accès au mot de passe, **sauter cette étape** et la signaler comme à vérifier par un humain.

```bash
hyprlock --immediate
```

Attendu : l'écran se verrouille, le wallpaper est flouté, l'horloge est en Cinzel, le champ a un contour or éteint. Déverrouiller avec le mot de passe.

- [ ] **Step 5: Commit**

```bash
git add hyprlock/.config/hypr/hyprlock.conf
git commit -m "feat: hyprlock sur la palette + fix du chemin wallpaper cassé"
```

---

### Task 10: Créer le paquet stow kitty

**Files:**
- Create: `kitty/.config/kitty/kitty.conf`

**Interfaces:**
- Consumes: `kitty/.config/kitty/colors.conf` (Task 2), stowé (Task 5) — `background`, `foreground`, `cursor`, `color0`…`color15`

kitty n'avait **aucune config** (`~/.config/kitty/` était un dossier vide). `kitty.conf` est un nouveau fichier : `stow -R kitty` est nécessaire.

- [ ] **Step 1: Écrire `kitty.conf`**

```conf
include colors.conf

font_family      JetBrainsMono Nerd Font
font_size        11.0
adjust_line_height 110%

window_padding_width 12
placement_strategy   center
hide_window_decorations yes
confirm_os_window_close 0

cursor_shape           beam
cursor_blink_interval  0

scrollback_lines 10000

enable_audio_bell no
visual_bell_duration 0

background_opacity 0.92
```

`background_opacity 0.92` laisse le blur d'Hyprland (déjà activé) travailler derrière le terminal.

- [ ] **Step 2: Re-stow**

```bash
stow -R -t "$HOME" kitty
ls -l ~/.config/kitty/
```

Attendu : `kitty.conf` et `colors.conf`, tous deux symlinks vers le repo.

- [ ] **Step 3: Vérifier que kitty charge la config sans erreur**

```bash
kitty --config ~/.config/kitty/kitty.conf --debug-config 2>&1 | grep -iE 'bad value|unknown option|error' | head; echo "---fin---"
kitty --config ~/.config/kitty/kitty.conf --debug-config 2>&1 | grep -E '^color3 |^background ' | head -3
```

Attendu : rien avant `---fin---`, puis `color3 #c9a961` et `background #0d0b0a`.

- [ ] **Step 4: Vérifier à l'œil que les ANSI sont discriminables**

```bash
kitty --config ~/.config/kitty/kitty.conf sh -c '
for i in 0 1 2 3 4 5 6 7; do printf "\033[3${i}m██ normal $i \033[0m"; done; echo
for i in 0 1 2 3 4 5 6 7; do printf "\033[9${i}m██ bright $i \033[0m"; done; echo
read -p "Rouge et vert distinguables ? Entrée pour fermer."'
```

Attendu : les 16 teintes sont visibles et distinctes. Le rouge (garance) doit être visiblement plus sombre que le vert (vert-de-gris) — cet écart de luminosité est délibéré, il garde les diffs lisibles en deutéranopie.

- [ ] **Step 5: Commit**

```bash
git add kitty/
git commit -m "feat: paquet kitty avec les ANSI pigments d'époque"
```

---

### Task 11: README + recette d'acceptation

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: tout ce qui précède.
- Produces: l'état final vérifiable.

- [ ] **Step 1: Écrire le README**

````markdown
# Clair Obscur — dotfiles

Rice Hyprland inspiré de Clair Obscur : Expedition 33.
Belle Époque sombre — or patiné sur noirs chauds.

## Couleurs

**`palette.toml` est la seule source de vérité.** Ne jamais éditer un fichier
portant l'en-tête `GÉNÉRÉ PAR`.

```bash
python3 bin/generate_theme.py                   # régénère les fragments
python3 bin/generate_theme.py --check-contrast   # vérifie les seuils
```

Le contrôle de contraste tourne avant chaque génération : une palette qui
franchit un seuil ne peut pas atteindre les fichiers.

Seuils : rôles d'interface ≥ 4,5:1 (WCAG AA), ANSI ≥ 3:1 (convention terminal).
`black` est le seul exempté — dans un thème sombre, l'ANSI black *est* le fond.

Dunst est généré en entier depuis `templates/dunstrc.in` : il ne supporte ni
`include` ni variables. C'est la seule exception.

## Installation

```bash
./bin/install-fonts.sh
stow -R -t "$HOME" hypr waybar rofi dunst hyprlock kitty
```

`bin/` et `templates/` ne sont pas des paquets stow.

`~/.config/{hypr,waybar,rofi,dunst,kitty}` sont de vrais dossiers (deux paquets
partagent `~/.config/hypr`), donc **tout nouveau fichier exige un `stow -R`** —
il n'apparaît pas tout seul.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Stdlib uniquement — pas de pytest, pas de dépendance.

## Structure

| Chemin | Rôle |
|---|---|
| `palette.toml` | source de vérité des couleurs |
| `bin/generate_theme.py` | générateur + contrôle de contraste |
| `bin/install-fonts.sh` | Cormorant Garamond + Cinzel |
| `templates/dunstrc.in` | dunst ne sait ni importer ni utiliser de variables |
| `docs/superpowers/specs/` | designs |
| `docs/superpowers/plans/` | plans d'implémentation |
````

- [ ] **Step 2: Recette d'acceptation — les huit critères de la spec**

```bash
cd "$(git rev-parse --show-toplevel)"

echo "=== 1. idempotence"
python3 bin/generate_theme.py >/dev/null && git diff --exit-code && echo "OK"

echo "=== 2. contrastes"
python3 bin/generate_theme.py --check-contrast

echo "=== 3. aucun hex égaré"
attendu=$(printf '%s\n' ./palette.toml ./hypr/.config/hypr/colors.lua \
    ./waybar/.config/waybar/colors.css ./rofi/.config/rofi/colors.rasi \
    ./hyprlock/.config/hypr/colors.conf ./kitty/.config/kitty/colors.conf \
    ./dunst/.config/dunst/dunstrc | sort)
trouve=$(grep -rIl 'c9a961' --exclude-dir=.git --exclude-dir=docs \
    --exclude-dir=tests --exclude-dir=.superpowers . | sort)
diff <(echo "$attendu") <(echo "$trouve") && echo "OK aucun hex égaré"

echo "=== 4. stow sans conflit"
for p in hypr waybar rofi dunst hyprlock kitty; do
    stow -n -R -t "$HOME" "$p" 2>&1 | grep -i conflict && echo "CONFLIT $p" || true
done; echo "OK"

echo "=== 5. polices"
fc-match "JetBrainsMono Nerd Font"; fc-match Cinzel; fc-match "Cormorant Garamond"

echo "=== 6. agent polkit (exige une RECONNEXION, pas un reload)"
pgrep -f polkit-gnome-authentication-agent >/dev/null \
    && echo "OK agent actif" || echo "À VÉRIFIER après relance de session"

echo "=== 7. aucun bind en double"
grep -oE 'mainMod \.\. " \+ [^"]*"' hypr/.config/hypr/hyprland.lua \
    | sort | uniq -d | grep . && echo "ÉCHEC bind double" || echo "OK"

echo "=== 8. les outils démarrent"
hyprctl reload >/dev/null && echo "OK hyprland"
dunst --config dunst/.config/dunst/dunstrc --print >/dev/null 2>&1 && echo "OK dunst"
rofi -dump-theme >/dev/null 2>&1 && echo "OK rofi"
```

Le critère 6 exige une **relance de session** : l'autostart ne rejoue pas sur `hyprctl reload`. Le noter comme à vérifier après reconnexion, ce n'est pas un échec.

- [ ] **Step 3: Preuve de bout en bout de la source unique**

C'est la vérification qui compte : un changement dans `palette.toml` atteint-il **les six** fichiers ?

```bash
sed -i 's/^accent_gold     = "#c9a961"/accent_gold     = "#ff0000"/' palette.toml
python3 bin/generate_theme.py >/dev/null
grep -l 'ff0000' hypr/.config/hypr/colors.lua waybar/.config/waybar/colors.css \
    rofi/.config/rofi/colors.rasi hyprlock/.config/hypr/colors.conf \
    kitty/.config/kitty/colors.conf dunst/.config/dunst/dunstrc | wc -l
```

Attendu : `6`. Si un seul fichier manque, la source unique est un mensonge — chercher pourquoi avant de continuer.

Puis annuler :

```bash
git checkout palette.toml && python3 bin/generate_theme.py >/dev/null \
    && git diff --exit-code && echo "OK revenu à l'état initial"
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "docs: README — palette.toml comme source de vérité"
```

---

## Récapitulatif des sept bugs réparés

| # | Bug | Où | Tâche |
|---|---|---|---|
| 1 | Police fantôme `JetBrainMono` (sans `s`) → Noto Sans Mono | `style.css:2`, `config.rasi:2` | 7, 8 |
| 2 | Agent polkit mort (`authentification`) — **bug fonctionnel** | `hyprland.lua:57` | 6 |
| 3 | Chemin hyprlock cassé (`~/Pictures?wallpaper.jpg`) | `hyprlock.conf` | 9 |
| 4 | Double bind `SUPER+SHIFT+S` | `hyprland.lua:279,299` | 6 |
| 5 | Palette morte (`dofile` chargé, jamais lu) | `hyprland.lua:42` | 6 |
| 6 | Dérive stow (`colors.lua`, `hyprpaper.conf` non symlinkés) | `~/.config/hypr/` | 5 |
| 7 | Shadow config violet hors repo (4 fichiers, dont un actif) | `~/.config/**` | 5 |
