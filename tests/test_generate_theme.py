# tests/test_generate_theme.py
import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# bin/ n'est pas un paquet Python : on charge le module par chemin.
_spec = importlib.util.spec_from_file_location(
    "generate_theme", REPO / "bin" / "generate_theme.py"
)
generate_theme = importlib.util.module_from_spec(_spec)
sys.modules["generate_theme"] = generate_theme
_spec.loader.exec_module(generate_theme)


class TestContrastRatio(unittest.TestCase):
    def test_blanc_sur_noir_est_21(self):
        self.assertAlmostEqual(
            generate_theme.contrast_ratio("#ffffff", "#000000"), 21.0, places=2
        )

    def test_identique_est_1(self):
        self.assertAlmostEqual(
            generate_theme.contrast_ratio("#c9a961", "#c9a961"), 1.0, places=2
        )

    def test_symetrique(self):
        a = generate_theme.contrast_ratio("#e8dcc8", "#0d0b0a")
        b = generate_theme.contrast_ratio("#0d0b0a", "#e8dcc8")
        self.assertAlmostEqual(a, b, places=6)

    def test_valeur_connue_de_la_palette(self):
        # text_muted retenu = 4,73:1 sur bg_primary (mesuré au design).
        self.assertAlmostEqual(
            generate_theme.contrast_ratio("#857b6e", "#0d0b0a"), 4.73, places=2
        )


class TestLoadPalette(unittest.TestCase):
    def test_charge_la_variante_par_defaut(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertEqual(p["roles"]["accent_gold"], "#c9a961")
        self.assertEqual(p["ansi"]["red"], "#b84a4a")

    def test_variante_explicite(self):
        p = generate_theme.load_palette(REPO / "palette.toml", variant="nuit")
        self.assertEqual(p["roles"]["bg_primary"], "#0d0b0a")

    def test_variante_inconnue_leve_keyerror(self):
        with self.assertRaises(KeyError):
            generate_theme.load_palette(REPO / "palette.toml", variant="inexistante")

    def test_les_16_ansi_sont_presentes(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertEqual(len(p["ansi"]), 16)

    def test_le_role_shadow_existe(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertEqual(p["roles"]["shadow"], "#050403")


class TestCheckContrast(unittest.TestCase):
    def test_la_palette_livree_passe(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertEqual(generate_theme.check_contrast(p), [])

    def test_detecte_un_role_trop_faible(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        p["roles"]["text_muted"] = "#6b6459"  # 3,36:1 — sous le seuil AA
        echecs = generate_theme.check_contrast(p)
        self.assertTrue(any("text_muted" in e for e in echecs))

    def test_black_est_exempte(self):
        # black est à 1,08:1 dans la palette livrée et ne doit PAS échouer.
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertEqual(generate_theme.check_contrast(p), [])

    def test_detecte_un_ansi_trop_faible(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        p["ansi"]["bright_black"] = "#3d3730"  # 1,67:1 — commentaires illisibles
        echecs = generate_theme.check_contrast(p)
        self.assertTrue(any("bright_black" in e for e in echecs))

    def test_shadow_n_est_pas_controle(self):
        # shadow est à 1,04:1 sur bg_primary — c'est le but, une ombre doit
        # creuser sous le fond. Il n'est pas dans ROLES_TEXTE, donc la liste
        # blanche l'ignore : aucune exemption à inventer, contrairement à black.
        p = generate_theme.load_palette(REPO / "palette.toml")
        self.assertIn("shadow", p["roles"])
        self.assertEqual(generate_theme.check_contrast(p), [])


class TestEmetteurs(unittest.TestCase):
    def setUp(self):
        self.p = generate_theme.load_palette(REPO / "palette.toml")

    def test_lua_est_une_table_avec_rgb(self):
        out = generate_theme.emit_lua(self.p)
        self.assertIn("return {", out)
        self.assertIn('accent_gold = "rgb(c9a961)"', out)
        self.assertTrue(out.startswith("--"))  # en-tête en commentaire Lua

    def test_css_utilise_define_color(self):
        out = generate_theme.emit_css(self.p)
        self.assertIn("@define-color accent_gold #c9a961;", out)
        self.assertTrue(out.startswith("/*"))

    def test_rasi_normalise_en_tirets(self):
        out = generate_theme.emit_rasi(self.p)
        self.assertIn("accent-gold: #c9a961;", out)
        self.assertIn("* {", out)

    def test_hyprlang_utilise_des_variables(self):
        out = generate_theme.emit_hyprlang(self.p)
        self.assertIn("$accent_gold = rgb(c9a961)", out)
        self.assertTrue(out.startswith("#"))

    def test_kitty_mappe_les_16_ansi(self):
        out = generate_theme.emit_kitty(self.p)
        self.assertIn("color3 #c9a961", out)   # yellow = or
        self.assertIn("color15 #f5ecdd", out)  # bright_white
        self.assertIn("background #0d0b0a", out)
        self.assertIn("foreground #e8dcc8", out)

    def test_tous_les_fragments_portent_l_entete(self):
        for emetteur in (
            generate_theme.emit_lua,
            generate_theme.emit_css,
            generate_theme.emit_rasi,
            generate_theme.emit_hyprlang,
            generate_theme.emit_kitty,
        ):
            self.assertIn("NE PAS ÉDITER", emetteur(self.p))
            self.assertIn("palette.toml", emetteur(self.p))

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


class TestIdempotence(unittest.TestCase):
    def test_deux_passages_donnent_le_meme_contenu(self):
        p = generate_theme.load_palette(REPO / "palette.toml")
        emetteurs = (
            generate_theme.emit_lua, generate_theme.emit_css,
            generate_theme.emit_rasi, generate_theme.emit_hyprlang,
            generate_theme.emit_kitty,
        )
        premier = {e.__name__: e(p) for e in emetteurs}
        second = {e.__name__: e(p) for e in emetteurs}
        self.assertEqual(premier, second)


class TestDunstrc(unittest.TestCase):
    def setUp(self):
        self.p = generate_theme.load_palette(REPO / "palette.toml")
        self.out = generate_theme.emit_dunstrc(self.p)

    def test_porte_l_entete(self):
        self.assertIn("NE PAS ÉDITER", self.out)

    def test_aucun_placeholder_ne_subsiste(self):
        self.assertNotIn("{{", self.out)
        self.assertNotIn("}}", self.out)

    def test_les_couleurs_sont_entre_guillemets(self):
        # dunst interprète un # non quoté comme un commentaire.
        self.assertIn('background = "#1a1512"', self.out)

    def test_critical_est_un_bandeau_rouge_a_texte_creme(self):
        bloc = self.out.split("[urgency_critical]")[1]
        self.assertIn('background = "#7a1f1f"', bloc)
        self.assertIn('foreground = "#e8dcc8"', bloc)

    def test_les_trois_urgences_sont_presentes(self):
        for section in ("[urgency_low]", "[urgency_normal]", "[urgency_critical]"):
            self.assertIn(section, self.out)


if __name__ == "__main__":
    unittest.main()
