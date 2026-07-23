-- Configuration Hyprland — rice Clair Obscur.
-- Les couleurs viennent de colors.lua, généré depuis palette.toml.
-- Ne pas y écrire de couleur en dur.


------------------
---- MONITORS ----
------------------

hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = "auto",
})


---------------------
---- MY PROGRAMS ----
---------------------

local terminal    = "kitty"
local fileManager = "thunar"
local menu        = "rofi -show drun"
local browser     = "firefox"
local locker      = "hyprlock"
local colors = dofile(os.getenv("HOME") .. "/.config/hypr/colors.lua")

-------------------
---- AUTOSTART ----
-------------------

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


-------------------------------
---- ENVIRONMENT VARIABLES ----
-------------------------------

hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")


-----------------------
---- LOOK AND FEEL ----
-----------------------

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

-- Courbes et animations par défaut de Hyprland — non retouchées (hors périmètre design).
hl.curve("easeOutQuint",   { type = "bezier", points = { {0.23, 1},    {0.32, 1}    } })
hl.curve("easeInOutCubic", { type = "bezier", points = { {0.65, 0.05}, {0.36, 1}    } })
hl.curve("linear",         { type = "bezier", points = { {0, 0},       {1, 1}       } })
hl.curve("almostLinear",   { type = "bezier", points = { {0.5, 0.5},   {0.75, 1}    } })
hl.curve("quick",          { type = "bezier", points = { {0.15, 0},    {0.1, 1}     } })

hl.curve("easy",           { type = "spring", mass = 1, stiffness = 71.2633, dampening = 15.8273644 })

hl.animation({ leaf = "global",        enabled = true,  speed = 10,   bezier = "default" })
hl.animation({ leaf = "border",        enabled = true,  speed = 5.39, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows",       enabled = true,  speed = 4.79, spring = "easy" })
hl.animation({ leaf = "windowsIn",     enabled = true,  speed = 4.1,  spring = "easy",         style = "popin 87%" })
hl.animation({ leaf = "windowsOut",    enabled = true,  speed = 1.49, bezier = "linear",       style = "popin 87%" })
hl.animation({ leaf = "fadeIn",        enabled = true,  speed = 1.73, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut",       enabled = true,  speed = 1.46, bezier = "almostLinear" })
hl.animation({ leaf = "fade",          enabled = true,  speed = 3.03, bezier = "quick" })
hl.animation({ leaf = "layers",        enabled = true,  speed = 3.81, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersIn",      enabled = true,  speed = 4,    bezier = "easeOutQuint", style = "fade" })
hl.animation({ leaf = "layersOut",     enabled = true,  speed = 1.5,  bezier = "linear",       style = "fade" })
hl.animation({ leaf = "fadeLayersIn",  enabled = true,  speed = 1.79, bezier = "almostLinear" })
hl.animation({ leaf = "fadeLayersOut", enabled = true,  speed = 1.39, bezier = "almostLinear" })
hl.animation({ leaf = "workspaces",    enabled = true,  speed = 1.94, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesIn",  enabled = true,  speed = 1.21, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesOut", enabled = true,  speed = 1.94, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "zoomFactor",    enabled = true,  speed = 7,    bezier = "quick" })

-- dwindle : preserve_split garde l'orientation d'une découpe existante
hl.config({
    dwindle = {
        preserve_split = true,
    },
})

----------------
----  MISC  ----
----------------

hl.config({
    misc = {
        disable_hyprland_logo = true,   -- pas de mascotte dans une galerie
    },
})


---------------
---- INPUT ----
---------------

hl.config({
    input = {
        kb_layout  = "us",
        kb_variant = "",
        kb_model   = "",
        kb_options = "",
        kb_rules   = "",

        follow_mouse = 1,

        sensitivity = 0, -- plage -1.0 à 1.0 ; 0 = pas de modification

        touchpad = {
            natural_scroll = false,
        },
    },
})

hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace"
})


---------------------
---- KEYBINDINGS ----
---------------------

local mainMod = "SUPER"

hl.bind(mainMod .. " + Return", hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + W", hl.dsp.window.close())
hl.bind(mainMod .. " + SHIFT + M", hl.dsp.exec_cmd("command -v hyprshutdown >/dev/null 2>&1 && hyprshutdown || hyprctl dispatch exit"))
hl.bind(mainMod .. " + SHIFT + F", hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + V", hl.dsp.window.float({ action = "toggle" }))
-- Le menu est le raccourci le plus frappé de la session : deux touches, pas trois.
hl.bind(mainMod .. " + D", hl.dsp.exec_cmd(menu))
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo())
hl.bind(mainMod .. " + SHIFT + B", hl.dsp.exec_cmd(browser))
hl.bind(mainMod .. " + J", hl.dsp.layout("togglesplit"))    -- N'a d'effet qu'en layout dwindle (voir LOOK AND FEEL) ; togglesplit n'existe pas en layout master.
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen())
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.exec_cmd("grim -g \"$(slurp)\" - | wl-copy && notify-send 'Copied screenshot'"))
hl.bind(mainMod .. " + SHIFT + P", hl.dsp.exec_cmd("grim -g \"$(slurp)\" ~/Pictures/screenshot_$(date +%Y%m%d_%H%M%S).png"))
hl.bind(mainMod .. " + L", hl.dsp.exec_cmd(locker))

hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }))

-- Déplacer la fenêtre dans le layout. C'était le manque le plus net du config
-- d'origine : on pouvait déplacer le focus, jamais les fenêtres.
hl.bind(mainMod .. " + SHIFT + left",  hl.dsp.window.move({ direction = "left" }))
hl.bind(mainMod .. " + SHIFT + right", hl.dsp.window.move({ direction = "right" }))
hl.bind(mainMod .. " + SHIFT + up",    hl.dsp.window.move({ direction = "up" }))
hl.bind(mainMod .. " + SHIFT + down",  hl.dsp.window.move({ direction = "down" }))

for i = 1, 10 do
    local key = i % 10 -- i = 10 devient la touche "0" : il n'y a pas de touche "10" au clavier.
    hl.bind(mainMod .. " + " .. key,             hl.dsp.focus({ workspace = i}))
    hl.bind(mainMod .. " + SHIFT + " .. key,     hl.dsp.window.move({ workspace = i }))
end

hl.bind(mainMod .. " + S",         hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + SHIFT + X", hl.dsp.window.move({ workspace = "special:magic" }))

hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))

hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

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

-- Touches multimédia de clavier portable (volume, luminosité de l'écran) : brightnessctl
-- pilote le rétroéclairage LCD, absent sur un moniteur de bureau classique.
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),      { locked = true, repeating = true })
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),     { locked = true, repeating = true })
hl.bind("XF86AudioMicMute",     hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),   { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp",  hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"),                  { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown",hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"),                  { locked = true, repeating = true })

-- playerctl doit être installé : ces binds n'ont aucun effet sans lui.
hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("playerctl next"),       { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),   { locked = true })


--------------------------------
---- WINDOWS AND WORKSPACES ----
--------------------------------

-- Voir https://wiki.hypr.land/Configuring/Basics/Window-Rules/
-- et https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/

hl.window_rule({
    name  = "suppress-maximize-events",
    match = { class = ".*" },

    suppress_event = "maximize",
})

-- Corrige un bug réel de XWayland : pendant un drag-and-drop, XWayland fait
-- apparaître une fenêtre transitoire sans classe ni titre ; lui retirer le
-- focus évite qu'elle le vole à la fenêtre réellement déplacée.
hl.window_rule({
    name  = "fix-xwayland-drags",
    match = {
        class      = "^$",
        title      = "^$",
        xwayland   = true,
        float      = true,
        fullscreen = false,
        pin        = false,
    },

    no_focus = true,
})

hl.window_rule({
    name  = "move-hyprland-run",
    match = { class = "hyprland-run" },

    move  = "20 monitor_h-120",
    float = true,
})

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

-- hypridle ne doit pas verrouiller pendant une vidéo ou un jeu.
hl.window_rule({
    name         = "inhibe-veille-plein-ecran",
    match        = { fullscreen = true },
    idle_inhibit = "fullscreen",
})
