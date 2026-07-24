#!/usr/bin/env bash
# Libellés dynamiques de l'écran de verrouillage hyprlock.
# Appelé par les labels `cmd[...]` de hyprlock.conf.
#
# Usage : lock-labels.sh {greeting|battery}
#
# BAT1 est le nom de la batterie sur cette machine (voir /sys/class/power_supply) ;
# à adapter sur un autre matériel.

case "${1:-}" in
    greeting)
        h=$(date +%H)
        if   [ "$h" -lt 5 ];  then m="Bonne nuit"
        elif [ "$h" -lt 12 ]; then m="Bonjour"
        elif [ "$h" -lt 18 ]; then m="Bon après-midi"
        else                       m="Bonsoir"
        fi
        printf '%s, %s' "$m" "$(whoami)"
        ;;
    battery)
        c=$(cat /sys/class/power_supply/BAT1/capacity 2>/dev/null)
        s=$(cat /sys/class/power_supply/BAT1/status 2>/dev/null)
        case "$s" in
            Charging) l="En charge" ;;
            Full)     l="Chargée" ;;
            *)        l="Batterie" ;;
        esac
        printf '%s · %s %%' "$l" "$c"
        ;;
esac
