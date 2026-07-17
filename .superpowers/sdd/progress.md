# Socle palette — ledger

Plan : docs/superpowers/plans/2026-07-17-socle-palette.md
Branche : socle-palette
Base : fcc58f5 (spec)

## Pré-vol
- Shadow config violet découvert hors repo (5 vrais fichiers). Décision auteur : l'or, violet = essai abandonné. Purge en Task 5, sauvegarde /tmp/dotfiles-backup.
- Bug d'ordre corrigé : polices (T4) et purge stow (T5) remontées AVANT tout câblage. Sans T5, T6 fait planter Hyprland (colors.accent_gold = nil).
- Conflit plan/rubrique corrigé : le critère « aucun hex en dur » excluait à tort tests/, qui doivent coder en dur leurs attendus.
- Plan réordonné en 11 tâches.

## Tâches
Task 1: complete (commits daa00d2..6622dfa, review clean — reviewer a recalculé les 21 contrastes, tous exacts)
  Minor reporté au review final : main() ne capture pas le KeyError d'un --variant invalide (traceback brut au lieu d'un message propre). Non exigé Task 1.
Task 2: complete (commits 6622dfa..bd4fe42, review clean — Lua validé par exécution réelle)
  Contrôleur : .pyc échappés en Task 1 retirés du suivi + .gitignore Python (commit bd4fe42). Le reviewer T1 avait raté ça.
  Minor reporté au review final : TestIdempotence est tautologique (2 appels d'une fonction pure en mémoire). Code imposé par le plan ; l'idempotence réelle est vérifiée sur disque au Step 7. Ne détecterait pas un effet de bord non déterministe dans write_all.
  Minor reporté au review final : hex #c9a961 en dur dans le docstring de _rgb() (illustratif, imposé par le plan).
Task 3: complete (commits 8073823..e0de273, review clean — garde anti-placeholder vérifiée non contournable)
  Note env : l'implémenteur a dû stop/mask dunst.service pour vérifier --print (conflit D-Bus). Restauré et confirmé par le contrôleur (dunst tourne, service actif, notify-send OK).
  Minor reporté au review final : TestIdempotence n'inclut pas emit_dunstrc. L'idempotence du dunstrc n'est vérifiée que manuellement (md5sum), pas par la suite.
Task 4: complete (commits e1e9759..7087d69, review clean)
  DÉVIATION VALIDÉE : le script verbatim du plan avait un bug SIGPIPE (fc-list | grep -q sous pipefail -> exit 141 -> "déjà présente" toujours faux -> retéléchargement à chaque run, violant l'idempotence). L'implémenteur a corrigé (capture dans variable + here-string). Contrôleur a reproduit le bug (141) et validé le fix. Reviewer a confirmé qu'aucun autre pipe n'est vulnérable.
  Polices installées et résolues : Cormorant Garamond, Cinzel, JetBrainsMono Nerd Font.
Task 5: complete (commits 16fd80f..91e1a92, review clean — reviewer a audité l'état système, pas le diff : symlinks orphelins, conflits stow, --adopt, tout OK)
  DESTRUCTIF EXÉCUTÉ : 5 vrais fichiers supprimés de ~/.config, sauvegardés dans /tmp/dotfiles-backup/ (dunst-dunstrc, hypr-colors.lua, hypr-hyprpaper.conf, rofi-colors.rasi, waybar-colors.css). colors/ retiré du repo.
  Erreur du brief détectée et corrigée par l'implémenteur : ~/.config/hyprlock.conf -> ~/.config/hypr/hyprlock.conf.
  Minor : dunst tourne encore avec l'ancien dunstrc violet en mémoire (reload en Task 11).
  Minor : /tmp/dotfiles-backup/ non nettoyé (volontaire, filet de sécurité).
