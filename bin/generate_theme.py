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
