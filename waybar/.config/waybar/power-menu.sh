#!/usr/bin/env bash
# Menu d'alimentation via rofi (thème Clair Obscur, déjà en place).
# Appelé au clic sur le module custom/power de la waybar.
#
# Libellés en texte, sans icône : le thème rofi peut rendre en Cormorant
# Garamond, qui n'a pas les glyphes Nerd Font — un texte évite tout tofu.
#
# Ordre du moins au plus destructeur.

set -euo pipefail

options="Verrouiller
Veille
Déconnexion
Redémarrer
Éteindre"

choice=$(printf '%s' "$options" | rofi -dmenu -i -p "Alimentation")

case "$choice" in
    Verrouiller)  hyprlock ;;
    Veille)       systemctl suspend ;;
    Déconnexion)  hyprctl dispatch exit ;;
    Redémarrer)   systemctl reboot ;;
    Éteindre)     systemctl poweroff ;;
esac
