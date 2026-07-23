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
Task 6: complete (commits 74019ed..cfb0aef, review clean)
  3 bugs réparés en live : palette branchée (bordure ffc9a961/ff8a7442 gradient 45deg confirmée), polkit (authentification->authentication + exec->exec_cmd), double bind SHIFT+S -> déplacement passe sur SHIFT+X.
  Note : le fix polkit ne se vérifie qu'au prochain démarrage de session (le hook hyprland.start ne rejoue pas sur reload).
Task 7: complete (commits 2c72e2a..b371d44, review clean — @import à l'octet 0 vérifié par hexdump, 7 rôles croisés avec colors.css)
  waybar sur palette dorée, cyan #33ccff éliminé, police fantôme JetBrainMono->JetBrainsMono corrigée.
Task 8: complete (commits f2f2fb2..013fc07, review clean — 7 rôles en tirets croisés avec colors.rasi, re-stow fait)
  Thème rofi maison clair-obscur.rasi + config.rasi en @import. Arc-Dark abandonné. dump-theme exit=0.
  Validation visuelle (rofi -show drun) différée à l'humain — pas de fenêtre interactive en agent.
Task 9: complete (commits 724a247..9fe6e83, review clean — noms de propriétés croisés contre le binaire hyprlock 0.9.5)
  hyprlock sur palette, horloge Cinzel + date Cormorant, chemin wallpaper réparé (?  -> /wallpaper_clair_obscur.jpg).
  Validation VISUELLE différée à l'humain (hyprlock verrouille pour de vrai, pas de mode syntaxe-seule). Vérif statique complète et clean.
Task 10: complete (commits 3ab4153..4e9453d, review clean — config rechargée via kitty +runpy, garance plus sombre que vert-de-gris confirmé)
  Paquet kitty créé (terminal n'avait aucune config), re-stow fait, ANSI pigments d'époque.
  Adaptation validée : kitty --debug-config absent en 0.47.4, remplacé par kitty +runpy load_config.
  Validation VISUELLE des 16 teintes différée à l'humain.
  Minor POUR REVIEW FINAL : adjust_line_height 110% (kitty.conf:5) déprécié en kitty 0.47.4. Fonctionne (mappé vers modify_font cell_height 110% en interne) mais syntaxe historique. Fix trivial : remplacer par `modify_font cell_height 110%`. Hérité du plan verbatim.
Task 11: complete (commits 51fbbae..e8fded3, review clean — preuve de bout en bout 6/6 re-confirmée indépendamment)
  README + recette d'acceptation. 24/24 tests, contrastes OK, stow sans conflit, polices résolues.
  Fix contrôleur : docstring _rgb() #c9a961 -> #rrggbb (critère 3 passe maintenant). C'était le Minor #2 de Task 2.
  ATTENDU (pas un échec) : critère 6 polkit — le fix ne prend effet qu'au prochain démarrage de session (hook autostart ne rejoue pas sur reload). pgrep -f donne un faux positif (argv du wrapper).
  Note env : dunst --print entre en conflit D-Bus avec le daemon vivant ; la config est saine (symlink vers le repo), ce n'est pas un échec du socle.

## Minor restants pour triage au review final
- kitty.conf:5 adjust_line_height 110% déprécié en kitty 0.47.4 (fonctionne, mappé en interne). Fix trivial : modify_font cell_height 110%.
- TestIdempotence tautologique (2 appels fonction pure en mémoire) + n'inclut pas emit_dunstrc. Idempotence réelle vérifiée sur disque.
- main() ne capture pas KeyError d'un --variant invalide (traceback brut).

---

# hyprland.lua — passe d'intention — ledger

Plan : docs/superpowers/plans/2026-07-21-hyprland-config.md
Spec : docs/superpowers/specs/2026-07-21-hyprland-config-design.md
Branche : hyprland-intention
Base : b5ab2d5 (plan)

## Pré-vol
- Scan de conflits plan/rubrique : propre. Seul point noté, non bloquant : le
  nouveau test_shadow_n_est_pas_controle assied la même assertion que
  test_black_est_exempte (check_contrast == []). Ce n'est pas tautologique —
  il échoue si shadow entre dans ROLES_TEXTE — et le motif préexiste dans la
  suite. À adjuger si un reviewer le lève.
- Les Minor du socle (kitty adjust_line_height, TestIdempotence, KeyError de
  main()) restent non triés du plan précédent. Hors périmètre ici.
- Tâches 3 à 6 rechargent la session Hyprland VIVANTE de l'humain. Consentement
  donné explicitement avant lancement.

## Tâches
Task 1: complete (commit e7736d3, review clean — reviewer a ré-exécuté tests, contraste et régénération de façon indépendante)
  Note : l'implémentation préexistait dans l'arbre de travail, non vérifiée. L'implémenteur a été dispatché pour la vérifier contre le brief, pas pour l'écrire. Conforme au caractère près, aucun écart.
  7 fichiers commités ; dunstrc et kitty se réécrivent à l'identique (confirmé, pas d'anomalie).
  Minor pour review final : les tests raw découpent la sortie via .split("},")[0] — fragile si une valeur de rôle contenait un jour "},". Code hérité du plan verbatim.
Task 2: complete (aucun commit — livrable = relevé .superpowers/sdd/api-lua.md)
  DEUX ERREURS DU PLAN CORRIGÉES. hl.submap n'existe pas -> hl.define_submap(name, fn).
  hl.dsp.submap_reset n'existe pas -> hl.dsp.submap("reset"). Appeler hl.submap lève une
  erreur fatale qui interrompt tout le chunk Lua suivant — le plan aurait cassé le config.
  CONFIRMÉS tels quels : window.move({direction=}), window.resize({x=,y=}), idle_inhibit.
  Le mode submap reste utilisable ; le repli « 4 binds globaux » n'est plus nécessaire.
  Preuves à l'exécution, pas à la lecture : socket d'événements (submap>>resize / submap>>),
  en-tête C++ LuaBindingsInternal.hpp:74 pour idle_inhibit, champ inhibitingIdle observé.
  TROUVAILLE : /usr/share/hypr/stubs/hl.meta.lua — stub LSP faisant autorité sur toute
  l'API hl. Ma recherche initiale (/usr/share/hyprland, /usr/share/doc) l'avait manqué.
  Plan corrigé en conséquence (Task 5 Step 3 + prérequis) avant extraction du brief.
  INCIDENT : hyprland.lua était modifié non commité en arrivant ; le subagent l'a écrasé
  par git checkout. Changements perdus, non récupérables. Signalé à l'humain.
  Restauration prouvée : configerrors vide, git status propre, 477 binds = témoin initial.
Task 3: complete (commit 3cdbcfb, review clean — reviewer a décodé l'ombre et grep-é tout le fichier indépendamment)
  Chaîne palette prouvée de bout en bout : hyprctl getoption decoration:shadow:color -> 3993306115
  = 0xee050403 = alpha ee + colors.raw.shadow. Une seule occurrence de couleur dans le fichier,
  et c'est la composition depuis la palette. Zéro hex en dur.
  Les 3 clés incertaines (dim_inactive, dim_strength, blur.brightness) sont documentées dans
  le stub hl.meta.lua et acceptées sans erreur — aucun retrait nécessaire.
  Animations non touchées (vérifié par diff), nettoyage T4 non anticipé.
  VALIDATION VISUELLE DIFFÉRÉE À L'HUMAIN : ombre perçue, absence de transparence sur
  l'inactif, gaps élargis, absence du logo. Valeurs vérifiées, perception non.
Task 4: complete (commit 460f948, review clean — reviewer a rejoué le grep restreint aux lignes 1-189 : sortie vide)
  Autostart réduit à 6 services, un exec_cmd par processus, & shell supprimés.
  107 suppressions / 17 insertions. fix-xwayland-drags et suppress-maximize-events conservés.
  DÉFAUT DE PLAN TROUVÉ ET CORRIGÉ : le Step 4 lançait le grep de francisation sur TOUT le
  fichier en annonçant « aucune sortie », alors que KEYBINDINGS (T5) et WINDOWS (T6) ne sont
  pas du ressort de T4. Critère structurellement inatteignable. L'implémenteur a refusé de
  déborder et l'a signalé au lieu de maquiller le grep — bon réflexe, confirmé par le reviewer.
  Plan corrigé : T4 vérifie son propre périmètre (awk jusqu'à KEYBINDINGS), T5 et T6 gagnent
  chacune un Step 3 bis pour leur section, T7 gagne un Step 4 bis sur le fichier entier.
  T6 hérite aussi du retrait de la variable inutilisée suppressMaximizeRule.
  NON VÉRIFIABLE : le retrait de kitty/firefox ne se constate qu'au prochain démarrage de
  session (hyprland.start ne rejoue pas sur reload). Ni l'implémenteur ni le reviewer ne l'ont
  sur-affirmé.
Task 5: complete (commits 62b6007 + c1b9599, re-review clean après correctif — Important clos)
  Rofi SUPER+ALT+space -> SUPER+D, déplacement SUPER+SHIFT+flèches, submap resize sur SUPER+R.
  Syntaxe corrigée de la T2 appliquée : hl.define_submap / hl.dsp.submap("resize") / ("reset").
  Aucun hl.submap ni submap_reset dans le code (vérifié par grep du reviewer).
  Binds 477 -> 567 (+90 = 10 blocs de 9). Reviewer a recompté le delta lui-même au lieu de
  se fier au total : pas de compensation masquée. 9 touches vérifiées nommément, ALT+space parti.
  DÉFAUT DE PLAN TROUVÉ PAR LE REVIEWER : mon grep de francisation par mots-clés était trop
  étroit — 6 commentaires anglais y échappaient, et le grep de T7 ne les aurait pas vus non plus.
  Correctif dispatché ; le correcteur en a trouvé un 7e en relisant. Le reviewer en a recompté
  10 au total. Plan durci : en T7 le critère est la RELECTURE, le grep n'est qu'un filet.
  Minor pour review final : le rapport du correctif annonce « 6+1=7 » alors que son propre
  tableau et le diff en montrent 10. Traçabilité, sans effet sur le résultat.
  À VALIDER PAR L'HUMAIN (Step 6, test clavier) : SUPER+D ouvre rofi, SUPER+SHIFT+flèche déplace
  vraiment, SUPER+R -> flèches -> Échap, SUPER+L verrouille. Ni l'implémenteur ni les reviewers
  n'ont déclenché de raccourci : session verrouillable sans échappatoire, fenêtres sensibles ouvertes.
Task 6: complete (commit 0ff5864, review clean — reviewer a relu les 318 lignes, pas seulement grep-é)
  3 règles ajoutées : float-dialogues, float-portails-xdg, inhibe-veille-plein-ecran.
  idle_inhibit ACCEPTÉ sans repli — hypridle.conf non touché, conforme au verdict T2.
  suppress-maximize-events et fix-xwayland-drags conservés intacts ; seule l'affectation
  local suppressMaximizeRule retirée. Binds toujours 567, KEYBINDINGS non touchée.
  Arbitrage move-hyprland-run validé par le reviewer : commentaire paraphrastique retiré,
  règle fonctionnelle conservée (la supprimer aurait outrepassé le mandat).
  Francisation de la prose COMPLÈTE sur tout le fichier (vérifiée par relecture intégrale).
  QUESTION OUVERTE POUR T7 : les bannières de section en capitales (MONITORS, MY PROGRAMS,
  AUTOSTART, LOOK AND FEEL, INPUT, KEYBINDINGS, WINDOWS AND WORKSPACES...) restent en anglais,
  uniformément, depuis l'origine. Le reviewer refuse de trancher : repère structurel ou prose
  à traduire ? Décision posée à l'humain avant clôture.
  À VALIDER PAR L'HUMAIN (Step 5) : dialogue flottant à l'ouverture d'un sélecteur de fichiers,
  veille non déclenchée pendant une vidéo plein écran.
Task 7: complete (aucun commit — rien ne le justifiait, tête inchangée à 8245090)
  Vérifié par le contrôleur indépendamment : 29/29 tests, contraste vert, 567 binds,
  configerrors vide, luac OK, régénération déterministe (aucun fragment ne bouge).
  Relecture intégrale des 318 lignes : prose entièrement française. Bannières en anglais =
  décision auteur, hors périmètre. Faux positif du grep-filet : « and » dans « drag-and-drop »
  (ligne 274), phrase française, terme technique. Section propre.
  README jugé à jour : ne documente ni rôles couleur ni raccourcis, rien n'y devient faux.
  graphify update . : 144 nœuds, 148 arêtes, 14 communautés. graphify-out/ non suivi (pré-existant,
  jamais tracké, hors périmètre de la passe — laissé tel quel).

## Validations manuelles en attente (session vivante — à faire par l'humain)
- Rendu visuel : ombre portée, dim des inactives, flou, bordures dorées, absence du logo.
- Test clavier : SUPER+D (rofi), SUPER+SHIFT+flèche (déplace), SUPER+R -> flèches -> Échap, SUPER+L (verrou).
- Dialogue flottant à l'ouverture d'un sélecteur de fichiers.
- Veille non déclenchée pendant une vidéo plein écran.
- Prochain démarrage de session : kitty/firefox ne se lancent plus, fix polkit effectif.

## Revue de branche complète (opus) : PRÊT À FUSIONNER
  Tout re-vérifié indépendamment : 29 tests, contraste vert, 567 binds, configerrors vide,
  régénération déterministe (3 passages, aucun fragment ne bouge), luac OK.
  Chaîne d'ombre exacte de bout en bout : palette #050403 -> raw 050403 -> rgba(050403ee) = 0xee050403.
  hyprland.lua cohérent : submap déclaré/entré/quitté sans orphelin, aucun doublon de touche
  (collisions F/P/S différenciées par modificateur, i%10 mappe 10->0 sans chevaucher).
  Aucun hl.submap ni submap_reset. Triage des 3 Minor : tous « peuvent rester ».
    - .split("},")[0] : fragilité THÉORIQUEMENT IMPOSSIBLE (hex brut ne contient jamais "},").
    - « 6+1=7 » : traçabilité de rapport, zéro impact code.
    - hérités socle (TestIdempotence, KeyError main(), kitty adjust_line_height) : hors périmètre.
  DÉFAUT RÉEL PRÉEXISTANT (hors branche, commit 1901632 du 2026-07-11) : hyprland.lua SUPER+SHIFT+M,
  repli « || hyprctl dispatch 'hl.dsp.exit()' » — syntaxe API Lua dans une chaîne shell passée à
  hyprctl dispatch, qui attend un nom de dispatcher. Si hyprshutdown absent, le repli ne quitte pas.
  Correctif d'une ligne : hyprctl dispatch exit. Soumis à l'humain.
Fix hors-tâche (validé par l'humain) : SUPER+SHIFT+M repli hl.dsp.exit() -> hyprctl dispatch exit.
  Commité séparément. luac OK, reload OK, configerrors vide, binds toujours 567.

## Clôture — fusionnée sur main
  PR ouverte impossible côté agent (gh absent) : branche poussée, corps de PR préparé,
  merge fait à la main par l'humain via GitHub en REBASE MERGE (messages conservés, SHA réécrits).
  origin/main = 9d0bd92 (fix SUPER+SHIFT+M) après rebase des 11 commits.
  DÉSALIGNEMENT LOCAL RÉSOLU : le spec (6746f8a) et le plan (b5ab2d5) avaient été commités sur
  main AVANT création de la branche ; main local pointait donc EN AMONT de la passe. Le checkout
  main a fait régresser l'arbre (et la session live via symlink stow) au config d'exemple, et le
  rebase distant a empêché le fast-forward. Corrigé par git reset --hard origin/main. Rien perdu :
  spec+plan présents sur origin/main sous SHA rebasés, ledger sauvegardé en scratchpad avant reset.
  Branche hyprland-intention supprimée (contenu sur main). Session rechargée : luac OK,
  configerrors vide, 567 binds. Tests 29/29, contraste vert.
  graphify-out/ ajouté au .gitignore (commit a53f3c6). main poussé : local == origin == a53f3c6.

## Reste à faire (humain)
  Validations manuelles de la session vivante — checklist dans la description de PR :
  rendu visuel, tests clavier, dialogue flottant, veille plein écran, prochain démarrage de session.
