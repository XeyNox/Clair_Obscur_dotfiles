# hyprland.lua — passe d'intention

Date : 2026-07-21
Statut : validé

## Problème

Le socle palette est terminé : `palette.toml` alimente waybar, rofi, dunst,
kitty, hyprlock et hypridle. `hyprland.lua` est le dernier fichier resté en
arrière — c'est encore à ~90 % le config d'exemple livré par Hyprland, dont
seules les bordures ont été branchées sur la palette.

Concrètement : le logo anime par défaut est actif, la couleur d'ombre est
écrite en dur hors palette, le device d'exemple `epic-mouse-v1` est toujours
là, l'autostart lance un navigateur à chaque session, et les valeurs de
`decoration` sont celles d'un exemple — pas un parti pris.

Un rice qui justifie ses seuils de contraste sur trois paragraphes ne peut pas
laisser son compositeur aux valeurs par défaut.

## Périmètre

Une passe unique sur `hyprland.lua`, plus une extension minimale de la chaîne
palette. Nettoyage, parti pris visuel, binds et window rules sont traités
ensemble : ils touchent le même fichier, les séparer produirait des commits qui
se marchent dessus.

Fichiers touchés :

| Fichier | Nature |
|---|---|
| `palette.toml` | nouveau rôle `shadow` |
| `bin/generate_theme.py` | table `raw` dans la sortie Lua |
| `tests/test_generate_theme.py` | couverture du rôle et de la table |
| `hypr/.config/hypr/hyprland.lua` | réécriture intentionnelle |

Hors périmètre, assumé : les 17 lignes d'animations, qui reprennent les défauts
de Hyprland. Les retoucher est un chantier esthétique distinct, et elles ne
gênent personne.

## Direction visuelle — « le tableau éclairé »

Le clair-obscur devient un comportement du compositeur, pas seulement une
palette. La fenêtre active est le sujet éclairé ; le reste recule dans l'ombre.

### Le rôle `shadow`

Ajout dans `[variants.nuit.roles]` :

```toml
shadow = "#050403"   # sous bg_primary — une ombre doit creuser
```

La valeur est délibérément plus sombre que `bg_primary` (`#0d0b0a`), en gardant
la dérive chaude de la palette. L'ombre actuelle vaut `#1a1512`, soit
exactement `bg_secondary` : une ombre couleur du fond ne creuse rien.

`shadow` n'entre pas dans `ROLES_TEXTE`, qui est une liste blanche explicite.
Le contrôle de contraste l'ignore donc sans qu'on ait à inventer une exemption
— contrairement à `black` côté ANSI.

### La table `raw`

Une ombre a besoin d'un canal alpha, or `emit_lua` enveloppe chaque rôle dans
`rgb(...)`. Le générateur émet donc en plus une table de hex bruts, calquée sur
le traitement que reçoivent déjà les ANSI :

```lua
raw = { bg_primary = "0d0b0a", …, shadow = "050403" },
```

`hyprland.lua` compose l'alpha lui-même : `"rgba(" .. colors.raw.shadow .. "ee")`.

L'alpha reste dans le config et non dans la palette, parce que c'est un réglage
esthétique et non une couleur. Écrire `#050403ee` dans `palette.toml` casserait
`_luminance()`, qui parse six caractères hex, le jour où le rôle passerait sous
un contrôle.

### Valeurs

| Réglage | Avant | Après | Raison |
|---|---|---|---|
| `gaps_in` / `gaps_out` | 5 / 20 | 8 / 24 | le noir entre les fenêtres devient le mur de la galerie |
| `rounding` | 10 | 8 | moins bulle, plus toile encadrée |
| `shadow.range` | 4 | 20 | l'ombre existe vraiment |
| `shadow.color` | `0xee1a1a1a` en dur | `rgba(050403ee)` | depuis la palette |
| `blur.size` / `passes` | 3 / 1 | 6 / 2 | l'arrière-plan recule franchement |
| `blur.brightness` | absent | 0.8 | assombrit le flou — le clair-obscur se joue là |
| `dim_inactive` | absent | true | voir ci-dessous |
| `dim_strength` | absent | 0.12 | |
| `inactive_opacity` | 1.0 | 1.0 | inchangé, délibérément |
| `misc.disable_hyprland_logo` | false | true | retire la mascotte |

### Pourquoi `dim_inactive` et non `inactive_opacity`

L'opacité rend les fenêtres inactives translucides : le fond d'écran et les
fenêtres du dessous transparaissent au travers. C'est du bruit visuel, et c'est
un coût de lisibilité réel dès qu'on lit une documentation à côté de son code.

`dim_inactive` assombrit uniformément, sans rien laisser passer. Le clair-obscur
est un rapport ombre/lumière, pas de la transparence : c'est littéralement
l'effet recherché, sans le défaut.

## Autostart

Services uniquement, un appel par processus :

```lua
hl.on("hyprland.start", function()
  hl.exec_cmd("waybar")
  hl.exec_cmd("hyprpaper")
  hl.exec_cmd("hypridle")
  hl.exec_cmd("nm-applet")
  hl.exec_cmd("blueman-applet")
  hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
end)
```

`kitty` et `firefox` sont retirés : une session plus rapide, et un repo qui
reste reproductible pour qui le clone.

Les `&` shell disparaissent aussi. `hl.exec_cmd("waybar & hyprpaper & firefox")`
enchaîne trois processus dans un seul appel : si `waybar` meurt, rien ne le
signale. C'est de la fiabilité, pas du goût.

## Nettoyage

Supprimés :

- le device `epic-mouse-v1` — exemple stock
- les blocs `permission` commentés
- les règles `no-gaps-*` commentées — non retenues
- l'exemple `layer_rule` commenté
- `misc.force_default_wallpaper`
- la variable `closeWindowBind` et son `set_enabled` commenté
- les blocs `master` et `scrolling` — le layout est `dwindle` ; ces blocs
  règlent des layouts inutilisés

Les commentaires d'exemple anglais laissent place à des commentaires français
qui **justifient les choix**, comme le fait déjà `palette.toml`. Aucun
commentaire ne paraphrase le code.

## Binds

`SUPER + L` reste le verrouillage : la convention est trop installée pour y
renoncer. En conséquence, la navigation hjkl est abandonnée — `l` serait le
focus à droite. Les flèches assurent focus et déplacement.

Ce renoncement a une bonne conséquence : `SUPER + J` (togglesplit) et
`SUPER + P` (pseudo) n'ont plus besoin de déménager. Un seul raccourci change.

| Raccourci | Action | Statut |
|---|---|---|
| `SUPER + D` | rofi | **déplacé** — était `SUPER + ALT + space` |
| `SUPER + SHIFT + flèches` | déplacer la fenêtre dans le layout | **nouveau** |
| `SUPER + R` | submap de redimensionnement | **nouveau** |
| `SUPER + Return` | terminal | inchangé |
| `SUPER + W` | fermer la fenêtre | inchangé |
| `SUPER + V` | flottant | inchangé |
| `SUPER + F` | plein écran | inchangé |
| `SUPER + J` | togglesplit | inchangé |
| `SUPER + P` | pseudo | inchangé |
| `SUPER + L` | hyprlock | inchangé |
| `SUPER + flèches` | focus | inchangé |
| `SUPER + S` / `SUPER + SHIFT + X` | scratchpad / y envoyer | inchangé |
| `SUPER + 1..0` / `SUPER + SHIFT + 1..0` | workspace / y envoyer | inchangé |
| `SUPER + SHIFT + S` / `SUPER + SHIFT + P` | capture presse-papier / fichier | inchangé |
| `SUPER + SHIFT + F` / `SHIFT + B` / `SHIFT + M` | thunar / firefox / quitter | inchangé |
| touches multimédia | volume, luminosité, playerctl | inchangé |

Le déplacement passe sur `SUPER + SHIFT + flèches` : c'était le manque le plus
net du config, qui permettait de déplacer le focus mais jamais les fenêtres.

## Window rules

Conservées : `suppress-maximize-events` et `fix-xwayland-drags`. La seconde
corrige un vrai bug XWayland, pas un exemple.

Ajoutées :

- **Dialogues flottants et centrés** — sélecteurs de fichiers et boîtes de
  confirmation, par correspondance sur les titres usuels et les portails XDG.
- **Inhibition de la veille en plein écran** — hypridle ne verrouille pas
  pendant une vidéo ou un jeu.

## Risque : l'API Lua

Hyprland 0.55.4, et l'API de configuration Lua est récente. Aucune
documentation locale n'est inspectable sur cette machine. Deux clés du design
doivent être vérifiées contre l'API réelle **avant** écriture, chacune avec son
repli :

| Clé | Repli si absente |
|---|---|
| `hl.submap` (redimensionnement) | `SUPER + ALT + flèches` — quatre binds globaux au lieu d'un mode |
| `idle_inhibit` (veille) | poser la règle dans `hypridle.conf`, déjà présent dans le repo |

Aucun des deux replis ne bloque le reste de la passe.

## Vérification

- `python3 -m unittest discover -s tests` — la table `raw` et le rôle `shadow`
  sont couverts par de nouveaux tests.
- `python3 bin/generate_theme.py --check-contrast` — doit rester vert ; le
  nouveau rôle ne doit pas être contrôlé.
- `hyprctl reload`, puis contrôle qu'aucun bind n'a été perdu. Le tableau
  ci-dessus fait foi.
- Contrôle visuel : ombre visible sous la fenêtre active, fenêtres inactives
  assombries sans transparence, aucun logo Hyprland.

## Ordre d'implémentation

1. `palette.toml` et `generate_theme.py` — tout le reste en dépend
2. Vérification de l'API Lua (submap, idle_inhibit)
3. Look & feel
4. Autostart et nettoyage
5. Binds
6. Window rules
