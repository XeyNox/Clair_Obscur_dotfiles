#!/usr/bin/env bash
# Sélecteur de fond d'écran : liste ~/Pictures/wallpapers, montre un aperçu
# dans rofi (thème Clair Obscur), applique via l'IPC hyprpaper.
# Lié à SUPER + SHIFT + W.

set -euo pipefail

dir="$HOME/Pictures/wallpapers"
[ -d "$dir" ] || exit 0

shopt -s nullglob nocaseglob
files=("$dir"/*.jpg "$dir"/*.jpeg "$dir"/*.png "$dir"/*.webp)
shopt -u nocaseglob
[ ${#files[@]} -gt 0 ] || exit 0

# Chaque entrée porte son image en icône (\0icon\x1f) → vignette dans rofi.
# Vignettes agrandies juste pour ce menu, sans toucher au thème partagé.
choice=$(
    for f in "${files[@]}"; do
        printf '%s\0icon\x1f%s\n' "$(basename "$f")" "$f"
    done | rofi -dmenu -i -p "Fond d'écran" \
                -theme-str 'element-icon { size: 64px; } listview { lines: 5; }'
)
[ -n "$choice" ] || exit 0

wall="$dir/$choice"
[ -f "$wall" ] || exit 0

hyprctl hyprpaper preload "$wall" >/dev/null
hyprctl hyprpaper wallpaper ",$wall" >/dev/null
hyprctl hyprpaper unload unused >/dev/null
