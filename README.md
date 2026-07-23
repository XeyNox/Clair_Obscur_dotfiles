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

## Raccourcis

Modificateur principal : `SUPER`. Table tenue à la main — la source fait foi est
la section `KEYBINDINGS` de `hypr/.config/hypr/hyprland.lua`.

**Applications & session**

| Raccourci | Action |
|---|---|
| `SUPER + Return` | terminal (kitty) |
| `SUPER + D` | menu d'applications (rofi) |
| `SUPER + SHIFT + B` | navigateur (firefox) |
| `SUPER + SHIFT + F` | gestionnaire de fichiers (thunar) |
| `SUPER + L` | verrouiller l'écran (hyprlock) |
| `SUPER + SHIFT + M` | quitter Hyprland |
| `SUPER + SHIFT + S` | capture d'une région → presse-papier |
| `SUPER + SHIFT + P` | capture d'une région → `~/Pictures` |

**Fenêtres**

| Raccourci | Action |
|---|---|
| `SUPER + W` | fermer la fenêtre |
| `SUPER + F` | plein écran |
| `SUPER + V` | bascule flottant / tuilé |
| `SUPER + J` | bascule le sens de découpe (layout dwindle) |
| `SUPER + P` | pseudo-tuilage |
| `SUPER + flèches` | déplacer le focus |
| `SUPER + SHIFT + flèches` | déplacer la fenêtre dans le layout |
| `SUPER + R` | mode redimensionnement : flèches pour ajuster, `Échap` pour sortir |
| `SUPER + clic gauche` | déplacer à la souris |
| `SUPER + clic droit` | redimensionner à la souris |

**Espaces de travail**

| Raccourci | Action |
|---|---|
| `SUPER + 1…0` | aller à l'espace |
| `SUPER + SHIFT + 1…0` | y envoyer la fenêtre |
| `SUPER + molette` | espace précédent / suivant |
| `SUPER + S` | bascule le scratchpad « magic » |
| `SUPER + SHIFT + X` | envoyer la fenêtre au scratchpad |

Les touches multimédia (volume, luminosité, lecture) sont câblées sur `wpctl`,
`brightnessctl` et `playerctl` — utiles sur un portable, sans effet sans ces outils.

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
