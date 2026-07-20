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
