# Socle palette Clair Obscur — Design

**Date** : 2026-07-17
**Tranche** : 1 / 4 (socle)
**Statut** : validé

## Contexte

Le repo contient une palette Clair Obscur (`colors/colors.conf`) qui n'est lue par
aucun fichier. Les bordures Hyprland sont restées au cyan/vert du template par
défaut, waybar est en cyan `#33ccff`, rofi utilise le thème stock `Arc-Dark`, et
le paquet `dunst/` est vide. Le rice n'a jamais été branché.

Cinq bugs vérifiés s'ajoutent à ça, tous silencieux (voir « Réparations »).

Cette tranche ne produit aucun effet spectaculaire. Elle établit la source de
vérité sur laquelle les tranches suivantes s'appuient.

### Environnement constaté

| Élément | Valeur |
|---|---|
| Hyprland | 0.55.4, config Lua |
| Matériel | Ryzen AI 7 350 / Radeon 860M / 23 Gio, laptop (`eDP-1`) |
| Installé | kitty, alacritty, rofi 2.0 (Wayland natif), waybar, hyprpaper, dunst, hyprlock, hypridle, grim, slurp, playerctl |
| Absent | eww, ags, swww, mpvpaper, mako, cava, pywal |
| Python | 3.14.6 — `tomllib` en stdlib |
| Stow | 2.4.1 |

## Décisions de cadrage

| Question | Décision |
|---|---|
| Périmètre | Socle palette d'abord, avant tout élément vitrine |
| Direction visuelle | Belle Époque sombre et sobre — or patiné, noirs chauds, retenue |
| Animation | Shader **statique** (grain + vignettage) + animations **événementielles**. Pas de shader animé : il casse le damage tracking et vide la batterie en continu. |
| Source des couleurs | Générateur `palette.toml` → fragments |
| Typographie | Cormorant Garamond + Cinzel installées depuis Google Fonts |
| Jour/nuit | Structure prévue dès maintenant, mécanique construite en tranche 3 |

### Technologies écartées, et pourquoi

- **Picom** — compositeur X11, aucun rôle sous Wayland.
- **Sway / River** — régression : ni blur, ni ombres, ni courbes d'animation
  comparables à Hyprland.
- **Shaders GLSL dans kitty** — kitty ne supporte pas les shaders utilisateur.
  Le seul levier plein écran est `decoration:screen_shader` d'Hyprland
  (vérifié présent sur 0.55.4, actuellement vide).
- **Animations rofi** — rofi n'a pas de moteur d'animation. L'effet de révélation
  vient des animations de *layers* d'Hyprland (`layersIn` / `layersOut`).
- **pywal** — dérive les couleurs d'un wallpaper, ce qui contredit une palette
  choisie. Incompatible avec l'objectif.

## Architecture

```
palette.toml                    ← seule source de vérité éditée à la main
      │
      ▼
bin/generate_theme.py           ← Python stdlib (tomllib), zéro dépendance
      │
      ├──► hypr/.config/hypr/colors.lua           (table Lua)
      ├──► waybar/.config/waybar/colors.css       (@define-color)
      ├──► rofi/.config/rofi/colors.rasi          (bloc * {})
      ├──► hyprlock/.config/hypr/colors.conf      ($vars hyprlang)
      ├──► kitty/.config/kitty/colors.conf        (include)
      └──► dunst/.config/dunst/dunstrc            (fichier ENTIER, via templates/dunstrc.in)
```

### Principes

1. **Seul `palette.toml` s'édite à la main** pour les couleurs.
2. **Les fragments générés sont versionnés**, avec un en-tête
   `# GÉNÉRÉ PAR bin/generate_theme.py — NE PAS ÉDITER — source: palette.toml`.
   Le repo reste clonable et utilisable sans lancer le script.
3. **Les configs restent écrites à la main** (`hyprland.lua`, `style.css`, thème
   rofi, `hyprlock.conf`, `kitty.conf`) et importent leur fragment. Seules les
   couleurs sont générées.
4. **Dunst est la seule exception** : son `dunstrc` est généré en entier depuis
   `templates/dunstrc.in`, parce que dunst ne supporte ni `include` ni variables.
   C'est une exception assumée, pas le modèle.

### Emplacement des fichiers

- `palette.toml` à la **racine** du repo — c'est LE fichier à éditer, il doit se voir.
- `bin/generate_theme.py` — outil de repo, **pas** un paquet stow. Underscore et
  non tiret : Python n'importe pas les modules dont le nom contient un tiret, et
  les tests doivent pouvoir l'importer.
- `tests/test_generate_theme.py` — tests en `unittest` (stdlib). `pytest` n'est
  pas installé, et l'engagement « zéro dépendance » vaut aussi pour les tests.
- `templates/dunstrc.in` — template, pas un paquet stow.
- Le dossier `colors/` est **supprimé** : vestigial (jamais stowable — pas de
  sous-dossier `.config/`), son contenu est absorbé par `palette.toml`.
- Nouveau paquet stow `kitty/` (kitty n'a aucune config aujourd'hui).

### Structure de `palette.toml`

```toml
[meta]
default_variant = "nuit"

[variants.nuit.roles]
# ...

[variants.nuit.ansi]
# ...
```

Le générateur accepte `--variant <nom>` (défaut : `meta.default_variant`).
Une seule variante — `nuit` — est livrée en tranche 1. La structure imbriquée
existe dès maintenant pour que la tranche 3 (jour/nuit) n'ait pas à réécrire le
générateur ni ses appels.

## La palette

### Rôles (variante `nuit`)

Contrastes calculés selon WCAG 2.1, sur `bg_primary` `#0d0b0a`.

| Rôle | Hex | Contraste | Note |
|---|---|---|---|
| `bg_primary` | `#0d0b0a` | — | fond principal |
| `bg_secondary` | `#1a1512` | — | barre, surfaces plates |
| `bg_elevated` | `#241d18` | — | **nouveau** — popup rofi, doit se détacher de la barre |
| `accent_gold` | `#c9a961` | 8,73:1 | accent principal |
| `accent_gold_dim` | `#8a7442` | — | **nouveau** — état inactif / survol, dégradé de bordure |
| `accent_red` | `#7a1f1f` | 1,91:1 | **fond uniquement** — voir ci-dessous |
| `text_primary` | `#e8dcc8` | 14,50:1 | |
| `text_muted` | `#857b6e` | 4,73:1 | **modifié** — voir ci-dessous |
| `border_active` | `#c9a961` | — | |
| `border_inactive` | `#3d3730` | — | |

Deux valeurs changent par rapport à `colors/colors.conf`, sur la base de mesures :

- **`text_muted` : `#6b6459` → `#857b6e`.** L'original donne 3,36:1, sous le
  seuil AA de 4,5:1 pour du texte normal. La nouvelle valeur atteint 4,73:1 tout
  en restant discrète.
- **`accent_red` reste `#7a1f1f` mais devient un rôle de fond exclusivement.**
  À 1,91:1 il est illisible en texte et invisible en liseré fin. Utilisé comme
  fond avec `text_primary` dessus, il donne 7,59:1.

### Urgences dunst

| Niveau | Fond | Texte | Contraste |
|---|---|---|---|
| low | `bg_secondary` | `text_muted` | ≥ 4,5:1 |
| normal | `bg_secondary` | `text_primary` | ≥ 4,5:1 |
| critical | `accent_red` | `text_primary` | 7,59:1 |

L'urgence critique est un **bandeau plein**, pas un liseré — conséquence directe
du contraste d'`accent_red`.

### ANSI — les pigments d'époque

Problème : kitty a besoin de 16 couleurs ANSI discriminables. La palette Clair
Obscur n'a ni vert, ni bleu, ni cyan. Tout décliner en or rendrait `git diff`
illisible — rouge et vert doivent se distinguer, ce n'est pas négociable.

Solution : construire les ANSI comme des **pigments de la Belle Époque** —
désaturés, chauds, patinés. Ils restent dans l'univers visuel tout en étant
discriminables.

| ANSI | Pigment | Hex | Contraste |
|---|---|---|---|
| black | — | `#1a1512` | (= `bg_secondary`) |
| red | Garance | `#b84a4a` | 3,85:1 |
| green | Vert-de-gris | `#7d9470` | 5,93:1 |
| yellow | Or | `#c9a961` | 8,73:1 |
| blue | Bleu de Prusse délavé | `#5a7186` | 3,87:1 |
| magenta | Mauve fané | `#7a5f73` | 3,47:1 |
| cyan | Céladon | `#5f7373` | 3,91:1 |
| white | Crème | `#e8dcc8` | 14,50:1 |

Les 8 variantes `bright` sont définies explicitement dans `palette.toml`,
obtenues en éclaircissant la teinte normale, et soumises au même contrôle.

**Seuil ANSI : ≥ 3:1** — c'est la convention des thèmes de terminal, plus
permissive que les 4,5:1 des rôles d'interface. Compromis assumé entre contraste
et cohérence de palette, documenté ici pour qu'il ne soit pas relu comme un oubli.

**Exception : `black` est exempté du seuil.** Dans tout thème sombre, l'ANSI
`black` *est* la couleur de fond (ici 1,08:1 sur `bg_primary`) — le seuil n'a
pas de sens pour lui. C'est le seul exempté, et le contrôle échoue si un autre
l'invoque.

**`bright_black` = `#6b6459` (3,36:1).** C'est la couleur des commentaires en
coloration syntaxique, donc elle doit rester lisible : à `#3d3730` (= `border_inactive`)
elle donnerait 1,67:1, illisible. `#6b6459` est l'ancien `text_muted`, écarté des
rôles d'interface pour cause de 3,36:1 — insuffisant pour un label, conforme pour
de l'ANSI.

**Écart rouge/vert délibéré** : garance à 3,85:1 contre vert-de-gris à 5,93:1.
La différence de luminosité (et pas seulement de teinte) garde les diffs lisibles
en cas de deutéranopie.

### Contrôle automatisé

`bin/generate_theme.py --check-contrast` recalcule tous les ratios ci-dessus et
sort en code d'erreur non nul si un rôle d'interface passe sous 4,5:1 ou une
couleur ANSI sous 3:1. Les contrastes sont donc **vérifiables, pas affirmés** —
et la tranche 3 (variante jour) hérite du garde-fou gratuitement.

## Câblage par outil

| Outil | Mécanisme | Travail |
|---|---|---|
| Hyprland | `dofile` → table Lua | **La plomberie existe déjà** : `hyprland.lua:42` fait `local colors = dofile(...)`, la variable n'est jamais lue. Il suffit de la brancher sur `general.col`. |
| Waybar | `@import "colors.css"` + `@define-color` | Réécriture de `style.css` |
| rofi | `@import "colors.rasi"` | Abandon d'`Arc-Dark` pour un thème maison `clair-obscur.rasi` |
| hyprlock | `source = …/colors.conf` + `$vars` | Réécriture partielle |
| kitty | `include colors.conf` | **Terrain vierge** — aucune config aujourd'hui |
| dunst | aucun — généré en entier | `templates/dunstrc.in` |

### Bordure Hyprland — le motif clarté/obscurité

L'API Lua accepte un dégradé :

```lua
col = {
    active_border   = { colors = { colors.accent_gold, colors.accent_gold_dim }, angle = 45 },
    inactive_border = colors.border_inactive,
}
```

La fenêtre focus est « éclairée » par un dégradé or → or éteint à 45°, les autres
s'effacent dans le brun sourd. C'est le concept du jeu appliqué littéralement, en
une ligne de config.

## Réparations incluses

Six bugs, tous vérifiés, tous silencieux :

1. **Police fantôme.** `waybar/.config/waybar/style.css:2` et
   `rofi/.config/rofi/config.rasi:2` demandent `"JetBrainMono Nerd Font"` — sans
   le « s » de JetBrains. `fc-match` résout ça vers `NotoSansMono-Regular.ttf`.
   La police demandée n'a jamais été affichée. → `"JetBrainsMono Nerd Font"`.
2. **Agent polkit mort.** `hyprland.lua:57` lance
   `polkit-gnome-authentification-agent-1` (orthographe française). Le binaire
   réel est `polkit-gnome-authentication-agent-1`. Aucun agent polkit ne tourne :
   toute demande d'élévation de privilèges est sans fenêtre. **Bug fonctionnel,
   pas cosmétique.**
3. **Chemin hyprlock cassé.** `path = ~/Pictures?wallpaper.jpg` — le `?` est une
   typo et le fichier s'appelle `wallpaper_clair_obscur.jpg`.
   → `~/Pictures/wallpaper_clair_obscur.jpg`.
4. **Double bind `SUPER+SHIFT+S`.** Lié deux fois : capture d'écran vers le
   presse-papier (`hyprland.lua:279`) et déplacement vers le workspace spécial
   (`hyprland.lua:299`). L'un des deux ne répond pas.
   → le déplacement vers le workspace spécial passe sur `SUPER+SHIFT+X`, vérifié
   libre (aucune occurrence dans le fichier). `SUPER+SHIFT+M` (sortie de session,
   l. 271), `SHIFT+F` (l. 272), `SHIFT+B` (l. 276), `SHIFT+P` (l. 280) et
   `SHIFT+[0-9]` (l. 294) sont déjà pris.
5. **Palette morte.** `hyprland.lua:42` — `local colors = dofile(...)` jamais
   utilisé ; bordures restées au cyan/vert du template.
6. **Dérive stow.** `~/.config/hypr/colors.lua` et `~/.config/hypr/hyprpaper.conf`
   sont de vrais fichiers, pas des symlinks. Ce qui est versionné n'est pas ce qui
   tourne. `hyprpaper.conf` live et repo sont **identiques** (vérifié par `diff`)
   → suppression sans perte. `colors.lua` live contient une palette violette
   (`2C178A`) contredisant la palette dorée versionnée → remplacé par le fragment
   généré.

## Polices

Script `bin/install-fonts.sh` : télécharge Cormorant Garamond et Cinzel depuis
Google Fonts vers `~/.local/share/fonts/`, puis `fc-cache -f`. Pas d'AUR, pas de
compilation. Idempotent — ne retélécharge pas si déjà présentes.

Répartition :

- **Cinzel** — titres en capitales (horloge du lockscreen, en-têtes).
- **Cormorant Garamond** — labels d'affichage (horloge waybar, prompt rofi).
- **JetBrainsMono Nerd Font** — terminal, et tout ce qui est monospace ou
  iconographique (déjà installée).

Le contraste serif / mono *est* le motif clarté/obscurité appliqué à la typo.

Les polices ne sont pas versionnées (binaires, licence OFL redistribuable mais
encombrante) — d'où le script d'installation.

## Critères d'acceptation

1. `bin/generate_theme.py` régénère les 6 fichiers ; un second passage ne produit
   **aucun diff git** (idempotence).
2. `bin/generate_theme.py --check-contrast` sort en 0 sur la variante `nuit`.
3. Modifier `accent_gold` dans `palette.toml`, régénérer, recharger : la couleur
   change dans les 6 outils. **Aucun hex de la palette n'apparaît en dur** hors
   `palette.toml` et fragments générés — vérifiable par `grep -ri 'c9a961' --exclude-dir=.git`.
4. `stow -n` sur chaque paquet ne signale aucun conflit ; `~/.config/hypr/colors.lua`
   et `~/.config/hypr/hyprpaper.conf` sont des symlinks vers le repo.
5. `fc-match "JetBrainsMono Nerd Font"` et `fc-match Cinzel` résolvent vers les
   bonnes familles.
6. `pgrep -f polkit-gnome-authentication-agent` retourne un PID après relance de
   session.
7. Aucun bind Hyprland n'est déclaré deux fois.
8. Les 6 outils démarrent sans erreur (`hyprctl reload`, `waybar` en console,
   `dunst --print`, `rofi -show drun`, `hyprlock --immediate` puis déverrouillage,
   `kitty`).

## Hors périmètre

- **Tranche 2** — shader statique (grain + vignettage) via
  `decoration:screen_shader` ; affinage des animations d'événements (révélation
  rofi via `layersIn`, glissement de bordure, émergence des notifications).
- **Tranche 3** — bascule jour/nuit : variante `jour`, timer, rechargement à chaud
  (dunst veut un `SIGUSR2`, waybar un restart). La place est prévue en tranche 1.
- **Tranche 4+** — widgets eww (météo, stats système), wallpaper dynamique
  (swww / mpvpaper), retours sonores.

Ces tranches ont chacune leur propre cycle spec → plan → implémentation.
