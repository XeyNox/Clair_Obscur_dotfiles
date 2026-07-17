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
