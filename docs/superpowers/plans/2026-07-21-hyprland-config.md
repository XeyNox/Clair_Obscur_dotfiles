# hyprland.lua — passe d'intention : plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal :** faire passer `hyprland.lua` du config d'exemple de Hyprland à un fichier intentionnel — palette branchée jusqu'à l'ombre, parti pris visuel « le tableau éclairé », autostart réduit aux services, binds complétés.

**Architecture :** `palette.toml` reste la seule source de vérité. On lui ajoute un rôle `shadow`, et on apprend au générateur à émettre une table de hex bruts pour que le config puisse composer un canal alpha. `hyprland.lua` est ensuite réécrit section par section, chaque section validée par `hyprctl` avant de passer à la suivante.

**Tech Stack :** Hyprland 0.55.4 (API de configuration Lua), Python 3.11+ (stdlib seule, `tomllib`), `unittest`, GNU Stow.

## Global Constraints

- **`palette.toml` est la seule source de vérité des couleurs.** Ne jamais éditer un fichier portant l'en-tête `GÉNÉRÉ PAR`.
- **Stdlib Python uniquement** — pas de pytest, pas de dépendance nouvelle.
- **Commentaires en français**, et ils justifient les choix. Aucun commentaire ne paraphrase le code.
- **Aucun commentaire d'exemple anglais** ne subsiste dans `hyprland.lua` en fin de passe.
- Le contrôle de contraste (`--check-contrast`) doit rester vert à chaque commit.
- Hyprland **0.55.4** : toute clé de l'API Lua non confirmée par la Tâche 2 doit utiliser son repli documenté.
- Le fichier de travail est `hypr/.config/hypr/hyprland.lua` (le paquet stow), **jamais** `~/.config/hypr/hyprland.lua` directement.

## Effet de bord à connaître

Ajouter un rôle à `palette.toml` modifie **quatre** fragments générés, pas un : `emit_css`, `emit_rasi` et `emit_hyprlang` itèrent tous sur `palette["roles"]`. Après la Tâche 1, `git status` montrera donc aussi :

- `waybar/.config/waybar/colors.css` → `@define-color shadow #050403;`
- `rofi/.config/rofi/colors.rasi` → `shadow: #050403;`
- `hyprlock/.config/hypr/colors.conf` → `$shadow = rgb(050403)`

C'est attendu et sans effet : ce sont des variables déclarées et non utilisées. `emit_dunstrc` n'est pas affecté (il substitue des placeholders présents dans le gabarit). **Ne pas chercher à les supprimer.**

---

### Task 1: Le rôle `shadow` et la table `raw`

**Files:**
- Modify: `palette.toml` (bloc `[variants.nuit.roles]`)
- Modify: `bin/generate_theme.py:122-136` (`_rgb` voisin, `emit_lua`)
- Test: `tests/test_generate_theme.py`
- Regenerated: `hypr/.config/hypr/colors.lua`, + les trois fragments listés ci-dessus

**Interfaces:**
- Consomme : rien (première tâche)
- Produit : `colors.raw.<role>` dans `hypr/.config/hypr/colors.lua` — une table Lua de hex **sans `#`** (ex. `shadow = "050403"`), pour toutes les clés de `roles`. La Tâche 3 en dépend pour composer `rgba(...)`.

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter dans `tests/test_generate_theme.py`, dans la classe `TestLoadPalette` :

```python
    def test_le_role_shadow_existe(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertEqual(p["roles"]["shadow"], "#050403")
```

Ajouter dans la classe `TestCheckContrast` :

```python
    def test_shadow_n_est_pas_controle(self):
        # shadow est à 1,04:1 sur bg_primary — c'est le but, une ombre doit
        # creuser sous le fond. Il n'est pas dans ROLES_TEXTE, donc la liste
        # blanche l'ignore : aucune exemption à inventer, contrairement à black.
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertIn("shadow", p["roles"])
        self.assertEqual(generate_theme.check_contrast(p), [])
```

Ajouter dans la classe `TestEmetteurs` :

```python
    def test_lua_expose_les_hex_bruts(self):
        # Hyprland veut rgba(rrggbbaa) pour l'ombre ; _rgb() produit rgb(rrggbb).
        # La table raw permet au config de composer l'alpha lui-même.
        out = generate_theme.emit_lua(self.p)
        self.assertIn("raw = {", out)
        self.assertIn('shadow = "050403"', out)

    def test_lua_raw_couvre_tous_les_roles(self):
        out = generate_theme.emit_lua(self.p)
        bloc = out.split("raw = {")[1].split("},")[0]
        for nom in self.p["roles"]:
            self.assertIn(f'{nom} = "', bloc)

    def test_lua_raw_ne_contient_pas_de_diese(self):
        out = generate_theme.emit_lua(self.p)
        bloc = out.split("raw = {")[1].split("},")[0]
        self.assertNotIn("#", bloc)
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `python3 -m unittest discover -s tests -v`
Expected: FAIL — `KeyError: 'shadow'` sur les tests de palette, et `IndexError: list index out of range` sur ceux qui découpent `raw = {` (le marqueur n'existe pas encore).

- [ ] **Step 3: Ajouter le rôle à la palette**

Dans `palette.toml`, à la fin du bloc `[variants.nuit.roles]`, après `border_inactive` :

```toml
shadow          = "#050403"  # 1,04:1 — SOUS bg_primary : une ombre doit creuser
```

- [ ] **Step 4: Ajouter le helper et la table `raw` au générateur**

Dans `bin/generate_theme.py`, juste après `_rgb()` (ligne 122-124) :

```python
def _hex_brut(hex_couleur: str) -> str:
    """#rrggbb -> rrggbb — pour composer un alpha côté config."""
    return hex_couleur.lstrip("#")
```

Puis remplacer `emit_lua()` en entier :

```python
def emit_lua(palette: dict) -> str:
    lignes = [header("--"), "return {"]
    for nom, val in palette["roles"].items():
        lignes.append(f'    {nom} = "{_rgb(val)}",')
    # Hex bruts : Hyprland attend rgba(rrggbbaa) pour l'ombre, et l'alpha est
    # un réglage esthétique qui appartient au config, pas à la palette.
    lignes.append("    raw = {")
    for nom, val in palette["roles"].items():
        lignes.append(f'        {nom} = "{_hex_brut(val)}",')
    lignes.append("    },")
    lignes.append("    ansi = {")
    for nom, val in palette["ansi"].items():
        lignes.append(f'        {nom} = "{val}",')
    lignes.append("    },")
    lignes.append("}")
    return "\n".join(lignes) + "\n"
```

- [ ] **Step 5: Lancer les tests pour vérifier qu'ils passent**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS — tous les tests, y compris les anciens.

- [ ] **Step 6: Régénérer les fragments et vérifier le contraste**

Run: `python3 bin/generate_theme.py --check-contrast && python3 bin/generate_theme.py`
Expected: aucun échec de contraste, puis la liste des fichiers écrits.

Run: `git status --short`
Expected: exactement 7 fichiers modifiés — les 3 édités à la main (`palette.toml`, `bin/generate_theme.py`, `tests/test_generate_theme.py`) et les 4 régénérés (`hypr/.config/hypr/colors.lua`, `waybar/.config/waybar/colors.css`, `rofi/.config/rofi/colors.rasi`, `hyprlock/.config/hypr/colors.conf`).

Si `dunst/.config/dunst/dunstrc` apparaît, s'arrêter et investiguer : `emit_dunstrc` substitue des placeholders du gabarit, il ne devrait pas réagir à un nouveau rôle.

- [ ] **Step 7: Commit**

```bash
git add palette.toml bin/generate_theme.py tests/test_generate_theme.py \
        hypr/.config/hypr/colors.lua waybar/.config/waybar/colors.css \
        rofi/.config/rofi/colors.rasi hyprlock/.config/hypr/colors.conf
git commit -m "feat: rôle shadow et table de hex bruts pour composer l'alpha"
```

---

### Task 2: Reconnaissance de l'API Lua

L'API de configuration Lua de Hyprland est récente et non documentée localement. Quatre constructions du design ne sont pas confirmées. Cette tâche les teste **empiriquement** avant qu'on écrive quoi que ce soit qui en dépende, et consigne le résultat.

**Files:**
- Create: `/tmp/claude-1000/-home-Blanche-Clair-Obscur-dotfiles/fc344754-00c6-4953-9281-402b4a5e9c98/scratchpad/api-lua.md` (notes, non versionné)
- Modify (temporairement, puis revert) : `hypr/.config/hypr/hyprland.lua`

**Interfaces:**
- Consomme : rien
- Produit : un relevé écrit indiquant, pour chacune des 4 constructions, la syntaxe confirmée **ou** le repli à utiliser. Les Tâches 5 et 6 le lisent avant d'écrire.

- [ ] **Step 1: Établir la référence — le config actuel est sain**

Run: `hyprctl configerrors`
Expected: sortie vide. Si elle ne l'est pas, corriger avant de continuer — sinon on ne saura pas distinguer nos erreurs des préexistantes.

Run: `hyprctl binds | grep -c .`
Noter le nombre de lignes : il sert de témoin pour la suite.

- [ ] **Step 2: Sonder les quatre constructions**

Ajouter **temporairement** à la fin de `hypr/.config/hypr/hyprland.lua` :

```lua
-- SONDE TEMPORAIRE — à retirer à l'étape 4
hl.bind("SUPER + ALT + F1", hl.dsp.window.move({ direction = "left" }))
hl.bind("SUPER + ALT + F2", hl.dsp.window.resize({ x = 40, y = 0 }))
-- Le mode se teste en DEUX morceaux : le déclarer, et y entrer. La Tâche 5 a
-- besoin des deux ; ne pas conclure CONFIRMÉ si seule la déclaration passe.
hl.submap("sonde", function()
    hl.bind("escape", hl.dsp.submap_reset())
end)
hl.bind("SUPER + ALT + F3", hl.dsp.submap("sonde"))
hl.window_rule({
    name  = "sonde-idle",
    match = { fullscreen = true },
    idle_inhibit = "fullscreen",
})
```

Puis : `stow -R -t "$HOME" hypr && hyprctl reload`

- [ ] **Step 3: Relever ce qui passe et ce qui casse**

Run: `hyprctl configerrors`

Lire les erreurs : elles nomment la construction fautive. Puis :

Run: `hyprctl binds | grep -A2 'ALT'`
Expected si `window.move` fonctionne : le bind `SUPER ALT F1` apparaît.

Consigner dans le fichier de notes, une ligne par construction :

```
window.move({direction=})   : CONFIRMÉ | ÉCHEC → repli
window.resize({x=,y=})      : CONFIRMÉ | ÉCHEC → repli
hl.submap (déclaration)     : CONFIRMÉ | ÉCHEC → repli SUPER+ALT+flèches
hl.dsp.submap (entrée)      : CONFIRMÉ | ÉCHEC → repli SUPER+ALT+flèches
hl.dsp.submap_reset         : CONFIRMÉ | ÉCHEC → repli SUPER+ALT+flèches
idle_inhibit (rule)         : CONFIRMÉ | ÉCHEC → repli hypridle.conf
```

Le mode n'est utilisable que si **les trois** lignes `submap` sont CONFIRMÉ. Une seule en échec impose le repli complet : un mode dans lequel on ne peut pas entrer, ou dont on ne peut pas sortir, est pire que quatre binds globaux.

Replis, si une construction échoue :

| Construction | Repli |
|---|---|
| `hl.submap` | quatre binds globaux `SUPER + ALT + flèches` pour redimensionner, pas de mode |
| `idle_inhibit` | poser la règle dans `hyprlock/.config/hypr/hypridle.conf` |
| `window.move({direction=})` | chercher le nom exact dans `hyprctl dispatch -h`, ou utiliser `hl.dsp.exec_cmd("hyprctl dispatch movewindow l")` |
| `window.resize({x=,y=})` | idem via `hyprctl dispatch resizeactive` |

- [ ] **Step 4: Retirer la sonde**

Run: `git checkout hypr/.config/hypr/hyprland.lua && stow -R -t "$HOME" hypr && hyprctl reload`
Run: `hyprctl configerrors`
Expected: sortie vide, et `git status --short` ne montre aucune modification de `hyprland.lua`.

- [ ] **Step 5: Pas de commit**

Cette tâche ne produit aucun changement versionné — uniquement le relevé dans le scratchpad. C'est normal.

---

### Task 3: Look & feel — « le tableau éclairé »

**Files:**
- Modify: `hypr/.config/hypr/hyprland.lua:97-144` (le premier `hl.config`), et `:217-222` (bloc `misc`)

**Interfaces:**
- Consomme : `colors.raw.shadow` (Tâche 1)
- Produit : rien que les tâches suivantes consomment

- [ ] **Step 1: Remplacer le bloc `hl.config` de LOOK AND FEEL**

Remplacer intégralement les lignes 97 à 144 (de `hl.config({` jusqu'à `})` inclus, celui qui contient `general`, `decoration`, `animations`) par :

```lua
hl.config({
    general = {
        -- Gaps généreux : le noir entre les fenêtres est le mur de la galerie.
        gaps_in  = 8,
        gaps_out = 24,

        border_size = 2,

        col = {
            active_border   = { colors = { colors.accent_gold, colors.accent_gold_dim }, angle = 45 },
            inactive_border = colors.border_inactive,
        },

        resize_on_border = false,
        allow_tearing    = false,

        layout = "dwindle",
    },

    decoration = {
        rounding       = 8,
        rounding_power = 2,

        -- L'inactif est assombri, pas rendu translucide. Le clair-obscur est un
        -- rapport ombre/lumière ; l'opacité laisserait transparaître le fond
        -- d'écran et les fenêtres du dessous, ce qui nuit à la lecture.
        active_opacity   = 1.0,
        inactive_opacity = 1.0,
        dim_inactive     = true,
        dim_strength     = 0.12,

        -- La couleur d'ombre est SOUS bg_primary : une ombre de la couleur du
        -- fond ne creuse rien. L'alpha se compose ici, pas dans la palette.
        shadow = {
            enabled      = true,
            range        = 20,
            render_power = 3,
            color        = "rgba(" .. colors.raw.shadow .. "ee)",
        },

        blur = {
            enabled    = true,
            size       = 6,
            passes     = 2,
            brightness = 0.8,      -- assombrit l'arrière-plan flouté
            vibrancy   = 0.1696,
        },
    },

    animations = {
        enabled = true,
    },
})
```

- [ ] **Step 2: Corriger le bloc `misc`**

Remplacer le bloc `misc` (lignes 217-222) par :

```lua
hl.config({
    misc = {
        disable_hyprland_logo = true,   -- pas de mascotte dans une galerie
    },
})
```

`force_default_wallpaper` disparaît : `disable_hyprland_logo` suffit, et `hyprpaper` gère le fond.

- [ ] **Step 3: Vérifier la syntaxe Lua avant de recharger**

Run: `luac -p hypr/.config/hypr/hyprland.lua`
Expected: aucune sortie (succès). Une erreur ici signale une parenthèse ou une accolade mal fermée — corriger avant de recharger.

- [ ] **Step 4: Déployer et recharger**

Run: `stow -R -t "$HOME" hypr && hyprctl reload && hyprctl configerrors`
Expected: sortie vide de `configerrors`.

Si `dim_inactive`, `dim_strength` ou `blur.brightness` sont signalés comme inconnus : les retirer un à un et relancer, puis consigner lesquels ne sont pas supportés par 0.55.4.

- [ ] **Step 5: Contrôle visuel**

Vérifier de visu, avec deux fenêtres ouvertes :
- une ombre est visible sous la fenêtre active (elle ne l'était quasiment pas avant) ;
- la fenêtre inactive est **assombrie**, et rien ne transparaît au travers ;
- les gaps sont plus larges qu'avant ;
- aucun logo Hyprland n'apparaît sur un workspace vide.

- [ ] **Step 6: Commit**

```bash
git add hypr/.config/hypr/hyprland.lua
git commit -m "feat: parti pris visuel « le tableau éclairé » — ombre depuis la palette"
```

---

### Task 4: Autostart et nettoyage du stock

**Files:**
- Modify: `hypr/.config/hypr/hyprland.lua` — bloc AUTOSTART, device d'exemple, blocs commentés, blocs `master`/`scrolling`

**Interfaces:**
- Consomme : rien
- Produit : rien

- [ ] **Step 1: Remplacer l'autostart**

Remplacer le bloc `hl.on("hyprland.start", ...)` par :

```lua
-- Services uniquement. Aucune application : une session doit démarrer vite, et
-- ce dépôt doit rester reproductible pour qui le clone.
hl.on("hyprland.start", function()
    hl.exec_cmd("waybar")
    hl.exec_cmd("hyprpaper")
    hl.exec_cmd("hypridle")
    hl.exec_cmd("nm-applet")
    hl.exec_cmd("blueman-applet")
    hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
end)
```

Un appel par processus : `"waybar & hyprpaper & firefox"` enchaînait trois lancements dans un seul, ce qui masquait tout échec.

- [ ] **Step 2: Retirer les blocs morts**

Supprimer intégralement :

- le bloc `hl.device({ name = "epic-mouse-v1", ... })` — exemple stock
- le bloc `hl.config({ master = { new_status = "master" } })` — layout inutilisé
- le bloc `hl.config({ scrolling = { fullscreen_on_one_column = true } })` — layout inutilisé
- tout le bloc de commentaires `PERMISSIONS` (les `hl.permission` et `hl.config` commentés)
- les `hl.workspace_rule` et `hl.window_rule` commentés « no-gaps » (non retenus au design)
- le `hl.layer_rule` commenté « no-anim-overlay »
- la ligne `-- closeWindowBind:set_enabled(false)` et la ligne `-- suppressMaximizeRule:set_enabled(false)`

Transformer la ligne du bind de fermeture, qui n'a plus besoin de sa variable :

```lua
hl.bind(mainMod .. " + W", hl.dsp.window.close())
```

- [ ] **Step 3: Franciser les commentaires restants**

Remplacer les commentaires d'exemple anglais et les en-têtes de section. Les commentaires doivent justifier, pas paraphraser. Exemples de la transformation attendue :

```lua
-- AVANT : -- Set programs that you use
-- APRÈS : (supprimé — les noms de variables suffisent)

-- AVANT : -- See https://wiki.hypr.land/Configuring/Layouts/Dwindle-Layout/ for more
-- APRÈS : -- dwindle : preserve_split garde l'orientation d'une découpe existante
```

L'en-tête « AUTOGENERATED HYPRLAND CONFIG » en haut du fichier est un mensonge — ce fichier est écrit à la main. Le remplacer par :

```lua
-- Configuration Hyprland — rice Clair Obscur.
-- Les couleurs viennent de colors.lua, généré depuis palette.toml.
-- Ne pas y écrire de couleur en dur.
```

- [ ] **Step 4: Vérifier qu'aucun anglais résiduel ne subsiste**

Run: `grep -nE '^\s*--.*\b(the|your|you|this|for more|Example|See)\b' hypr/.config/hypr/hyprland.lua`
Expected: aucune sortie. Chaque ligne retournée est un commentaire d'exemple oublié.

- [ ] **Step 5: Vérifier la syntaxe, déployer, recharger**

Run: `luac -p hypr/.config/hypr/hyprland.lua && stow -R -t "$HOME" hypr && hyprctl reload && hyprctl configerrors`
Expected: aucune sortie.

- [ ] **Step 6: Commit**

```bash
git add hypr/.config/hypr/hyprland.lua
git commit -m "refactor: autostart réduit aux services, retrait du config d'exemple"
```

---

### Task 5: Binds

**Prérequis :** lire `.superpowers/sdd/api-lua.md`, le relevé de la Tâche 2. `window.move({direction=})` et `window.resize({x=,y=})` y sont CONFIRMÉS tels quels ; la déclaration de submap et la sortie de mode ont dû être corrigées (voir Step 3).

Référence faisant autorité pour tout doute sur l'API : `/usr/share/hypr/stubs/hl.meta.lua`, le stub LSP installé par le paquet Hyprland — il contient les signatures complètes de `hl.*` et `hl.dsp.*`.

**Files:**
- Modify: `hypr/.config/hypr/hyprland.lua` — section KEYBINDINGS

**Interfaces:**
- Consomme : le relevé d'API de la Tâche 2
- Produit : rien

- [ ] **Step 1: Déplacer le bind rofi**

Remplacer :

```lua
hl.bind(mainMod .. " + ALT + space", hl.dsp.exec_cmd(menu))
```

par :

```lua
-- Le menu est le raccourci le plus frappé de la session : deux touches, pas trois.
hl.bind(mainMod .. " + D", hl.dsp.exec_cmd(menu))
```

`SUPER + J` (togglesplit), `SUPER + P` (pseudo) et `SUPER + L` (hyprlock) **ne bougent pas** : hjkl ayant été abandonné au design, aucune collision ne les force à déménager.

- [ ] **Step 2: Ajouter le déplacement de fenêtre**

Juste après le bloc « Move focus with mainMod + arrow keys », ajouter :

```lua
-- Déplacer la fenêtre dans le layout. C'était le manque le plus net du config
-- d'origine : on pouvait déplacer le focus, jamais les fenêtres.
hl.bind(mainMod .. " + SHIFT + left",  hl.dsp.window.move({ direction = "left" }))
hl.bind(mainMod .. " + SHIFT + right", hl.dsp.window.move({ direction = "right" }))
hl.bind(mainMod .. " + SHIFT + up",    hl.dsp.window.move({ direction = "up" }))
hl.bind(mainMod .. " + SHIFT + down",  hl.dsp.window.move({ direction = "down" }))
```

Si la Tâche 2 a marqué `window.move({direction=})` en ÉCHEC, utiliser le repli relevé.

- [ ] **Step 3: Ajouter le redimensionnement**

**Syntaxe corrigée par la Tâche 2 — le plan initial se trompait sur deux noms.**
`hl.submap` et `hl.dsp.submap_reset` **n'existent pas** dans l'API Lua de 0.55.4 ;
appeler `hl.submap` lève une erreur fatale qui interrompt tout le chunk Lua suivant.
Le mode reste utilisable, avec les noms confirmés empiriquement :

```lua
-- Redimensionnement en mode : évite de consommer quatre raccourcis globaux.
-- hl.define_submap déclare, hl.dsp.submap entre, hl.dsp.submap("reset") sort.
hl.bind(mainMod .. " + R", hl.dsp.submap("resize"))
hl.define_submap("resize", function()
    hl.bind("left",  hl.dsp.window.resize({ x = -40, y = 0 }))
    hl.bind("right", hl.dsp.window.resize({ x = 40,  y = 0 }))
    hl.bind("up",    hl.dsp.window.resize({ x = 0,   y = -40 }))
    hl.bind("down",  hl.dsp.window.resize({ x = 0,   y = 40 }))
    hl.bind("escape", hl.dsp.submap("reset"))
end)
```

Ces trois formes ont été prouvées à l'exécution, pas seulement à la lecture : le
socket d'événements de Hyprland émet `submap>>resize` à l'entrée et `submap>>` à
la sortie. Le relevé complet est dans `.superpowers/sdd/api-lua.md`.

Le repli « quatre binds globaux `SUPER + ALT + flèches`, sans mode » n'est donc
**plus nécessaire** — ne l'appliquer que si la syntaxe corrigée ci-dessus échoue.

- [ ] **Step 4: Vérifier la syntaxe, déployer, recharger**

Run: `luac -p hypr/.config/hypr/hyprland.lua && stow -R -t "$HOME" hypr && hyprctl reload && hyprctl configerrors`
Expected: aucune sortie.

- [ ] **Step 5: Prouver qu'aucun bind n'a été perdu**

D'abord, regarder le format réel de la sortie — ne pas présumer :

Run: `hyprctl binds | head -20`

Puis compter :

Run: `hyprctl binds | grep -ci 'key'`
Comparer au témoin relevé à la Tâche 2, étape 1. Le compte doit avoir **augmenté** de 4 (repli) ou 5 (submap : 4 flèches + l'entrée), jamais diminué.

Ensuite, vérifier nommément chaque touche attendue. Adapter le motif au format constaté ci-dessus :

```bash
for k in D L J P W F S Return; do
  printf '%-8s ' "$k"
  hyprctl binds | grep -qiE "key:\s*$k\b" && echo PRÉSENT || echo "ABSENT ← problème"
done
```

Expected: les 8 touches en PRÉSENT. `D` = rofi, `L` = hyprlock, `J` = togglesplit, `P` = pseudo, `W` = fermer, `F` = plein écran, `S` = scratchpad, `Return` = terminal.

Enfin, vérifier que l'ancien bind rofi a bien disparu :

Run: `hyprctl binds | grep -iE 'key:\s*space'`
Expected: aucune sortie. S'il en reste une, l'ancien `SUPER + ALT + space` n'a pas été retiré.

- [ ] **Step 6: Test manuel**

Ouvrir deux fenêtres. Presser `SUPER + D` (rofi doit s'ouvrir), `SUPER + SHIFT + flèche` (la fenêtre doit changer de place, pas seulement le focus), `SUPER + L` (l'écran doit se verrouiller — le déverrouiller ensuite).

- [ ] **Step 7: Commit**

```bash
git add hypr/.config/hypr/hyprland.lua
git commit -m "feat: déplacement et redimensionnement des fenêtres, rofi sur SUPER+D"
```

---

### Task 6: Window rules

**Prérequis :** lire le relevé de la Tâche 2 pour `idle_inhibit`.

**Files:**
- Modify: `hypr/.config/hypr/hyprland.lua` — section WINDOWS AND WORKSPACES
- Modify (si repli) : `hyprlock/.config/hypr/hypridle.conf`

**Interfaces:**
- Consomme : le relevé d'API de la Tâche 2
- Produit : rien

- [ ] **Step 1: Conserver les deux règles existantes**

`suppress-maximize-events` et `fix-xwayland-drags` restent. La seconde corrige un vrai bug XWayland, ce n'est pas un exemple — ne pas la supprimer avec le reste du stock.

- [ ] **Step 2: Ajouter la règle des dialogues flottants**

```lua
-- Les sélecteurs de fichiers et boîtes de confirmation sont des dialogues :
-- les tuiler de force leur donne une taille absurde.
hl.window_rule({
    name  = "float-dialogues",
    match = { title = "^(Open File|Open Files|Save File|Save As|Choose Files|Select a File|Confirm|Confirmation)$" },
    float = true,
})

hl.window_rule({
    name  = "float-portails-xdg",
    match = { class = "^(xdg-desktop-portal-gtk|xdg-desktop-portal-hyprland)$" },
    float = true,
})
```

- [ ] **Step 3: Ajouter l'inhibition de veille**

Si `idle_inhibit` est CONFIRMÉ :

```lua
-- hypridle ne doit pas verrouiller pendant une vidéo ou un jeu.
hl.window_rule({
    name         = "inhibe-veille-plein-ecran",
    match        = { fullscreen = true },
    idle_inhibit = "fullscreen",
})
```

Si en ÉCHEC, ne rien ajouter ici et modifier `hyprlock/.config/hypr/hypridle.conf` : y ajouter, dans le bloc `general`, la ligne `ignore_dbus_inhibit = false`, puis vérifier que le lecteur vidéo utilisé émet bien une inhibition D-Bus. Consigner la limite dans le message de commit.

- [ ] **Step 4: Vérifier la syntaxe, déployer, recharger**

Run: `luac -p hypr/.config/hypr/hyprland.lua && stow -R -t "$HOME" hypr && hyprctl reload && hyprctl configerrors`
Expected: aucune sortie.

- [ ] **Step 5: Test manuel**

Ouvrir un sélecteur de fichiers (`SUPER + SHIFT + F` puis Ctrl+O dans thunar, ou une boîte « Enregistrer sous » depuis firefox) : la fenêtre doit être flottante, pas tuilée.

Passer une vidéo en plein écran et attendre le délai de `hypridle` : l'écran ne doit pas se verrouiller.

- [ ] **Step 6: Commit**

```bash
git add hypr/.config/hypr/hyprland.lua hyprlock/.config/hypr/hypridle.conf
git commit -m "feat: dialogues flottants et inhibition de veille en plein écran"
```

---

### Task 7: Vérification finale et documentation

**Files:**
- Modify: `README.md` (tableau de structure, si nécessaire)

- [ ] **Step 1: Suite de tests complète**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS, aucun échec.

- [ ] **Step 2: Contrôle de contraste**

Run: `python3 bin/generate_theme.py --check-contrast`
Expected: aucun échec signalé.

- [ ] **Step 3: Vérifier que le générateur est idempotent**

Run: `python3 bin/generate_theme.py && git status --short`
Expected: aucune modification. Si un fragment change, c'est que la génération n'est pas déterministe — investiguer avant de continuer.

- [ ] **Step 4: Config sain**

Run: `luac -p hypr/.config/hypr/hyprland.lua && hyprctl configerrors`
Expected: aucune sortie.

- [ ] **Step 5: Mettre à jour le graphe de connaissance**

Run: `graphify update .`

- [ ] **Step 6: Commit final si le README a changé**

Le README ne mentionne pas les binds aujourd'hui, et ce plan n'introduit pas de nouveau fichier ni de nouveau paquet stow. **Si rien n'a changé, ne pas créer de commit vide** — passer.

```bash
git add README.md
git commit -m "docs: README à jour après la passe hyprland"
```

---

## Notes pour l'implémenteur

- **`stow -R` est obligatoire après tout ajout de fichier.** `~/.config/hypr` est un vrai dossier partagé par deux paquets (`hypr` et `hyprlock`), donc un nouveau fichier n'apparaît pas tout seul. Ici on ne fait que modifier des fichiers existants, mais le réflexe reste bon.
- **Ne jamais éditer `~/.config/hypr/hyprland.lua`** — c'est un lien vers le dépôt. Éditer la source dans `hypr/.config/hypr/`.
- **Si `hyprctl reload` casse la session** au point de ne plus pouvoir travailler : `git checkout hypr/.config/hypr/hyprland.lua && stow -R -t "$HOME" hypr && hyprctl reload` depuis un TTY (`Ctrl+Alt+F2`).
- Les animations sont **hors périmètre** — ne pas y toucher, même si elles ressemblent à du stock. C'est un choix documenté au design.
