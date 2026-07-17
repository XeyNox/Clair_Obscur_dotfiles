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


CIBLES = (
    ("hypr/.config/hypr/colors.lua", emit_lua),
    ("waybar/.config/waybar/colors.css", emit_css),
    ("rofi/.config/rofi/colors.rasi", emit_rasi),
    ("hyprlock/.config/hypr/colors.conf", emit_hyprlang),
    ("kitty/.config/kitty/colors.conf", emit_kitty),
    ("dunst/.config/dunst/dunstrc", emit_dunstrc),
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

    echecs = check_contrast(palette)
    if echecs:
        for e in echecs:
            print(f"ÉCHEC {e}", file=sys.stderr)
        print("génération annulée : corriger palette.toml", file=sys.stderr)
        return 1

    for chemin in write_all(palette):
        print(f"écrit {chemin.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
