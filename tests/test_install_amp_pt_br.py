import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
INSTALLER = REPO / "scripts" / "install_amp_pt_br.py"
DOM_HARNESS = REPO / "tests" / "locale_dom_context.cjs"

AMP_JS = '''function SettingSubcategoryVM(name, category, settings) {
            this.displayName = replaceWithNonBreakingSpace(displayName);
}
async function checkVersionMismatch(moduleInfo) {
            const versionParam = "2.8.0.10";
            await UI.ShowModalAsync("AMP Version Mismatch", `The AMP frontend that has been loaded (v${versionParam}) does not match the backend (v${moduleInfo.APIVersion}). Please clear your browser cache (or force reload with CTRL+F5) as well as any upstream proxy caches.`, UI.Icons.Exclamation, UI.OKActionOnly);
}
'''

LEGACY_APPLY = '''        ApplyLocale: function (context) {
            $((context || "body") + " *")
                .contents()
                .filter((_, e) => e.nodeType === Node.TEXT_NODE && e.textContent.match(/[a-zA-Z]\\w/) && !e.textContent.contains("<!-- ko"))
                .each(function (_, e) {
                    e.textContent = e.textContent.replace(/^(\\s*)([a-zA-Z ].+?)(\\s*)$/, (match, p1, p2, p3) => `${p1}${obj.GetLocaleMessage(p2)}${p3}`);
                });
        },'''

JQUERY_APPLY = '''        ApplyLocale: function (context) {
            const elements = $(context || "body").find("*").addBack();
            elements.each(function () {
                for (const attribute of ["placeholder", "title", "aria-label"]) {
                    if (this.hasAttribute(attribute)) {
                        this.setAttribute(attribute, obj.GetLocaleMessage(this.getAttribute(attribute)));
                    }
                }
            });
            elements
                .contents()
                .filter((_, e) => e.nodeType === Node.TEXT_NODE && e.textContent.match(/[a-zA-Z]\\w/) && !e.textContent.contains("<!-- ko") && e.parentElement && !["SCRIPT", "STYLE"].includes(e.parentElement.tagName))
                .each(function (_, e) {
                    const translated = e.textContent.replace(/^(\\s*)(.+?)(\\s*)$/, (match, p1, p2, p3) => `${p1}${obj.GetLocaleMessage(p2)}${p3}`); if (translated !== e.textContent) { e.textContent = translated; }
                });
        },'''


def installer_string_constant(name):
    tree = ast.parse(INSTALLER.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(f"Missing installer constant: {name}")


def locale_fixture(apply_source, with_observer=False):
    observer = ""
    if with_observer:
        observer = "\n\n" + installer_string_constant("LOCALE_OBSERVER_BLOCK")
    return '''const Locale = (function () {
    let localeData = {};
    let loadedLocale = "en";
    const obj = {
        LoadLocale: async function (iso) {
            loadedLocale = iso;
            localeData = {
                "Re-run Setup": "Executar a configuração novamente",
                "Default Authentication Server": "Servidor de autenticação padrão",
                "Role Management": "Gerenciamento de funções",
                "Settings": "Configurações",
                "Search...": "Pesquisar..."
            };
        },
        GetLocaleMessage: function (original) { return localeData[original] || original; },
        APPLY_SOURCE
        ListLocale: function () {},
    };
    obj.l = obj.GetLocaleMessage;OBSERVER
    return obj;
})();
'''.replace("APPLY_SOURCE", apply_source).replace("OBSERVER", observer)


LOCALE_JS = locale_fixture(LEGACY_APPLY, with_observer=False)
LEGACY_LOCALE_JS = locale_fixture(LEGACY_APPLY, with_observer=True)
JQUERY_LOCALE_JS = locale_fixture(JQUERY_APPLY, with_observer=True)

AMP_HTML = '''<script src="/Scripts/Locale.js?v=2.8.0.10" defer></script>
<script src="/Scripts/AMP.js?v=2.8.0.10"></script>
<script src="/Scripts/AMP.js?v=2.8.0.10"></script>
'''


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="amp-ptbr-installer-")
        self.webroot = Path(self.temp.name) / "WebRoot"
        (self.webroot / "Scripts").mkdir(parents=True)
        (self.webroot / "Locale").mkdir()
        (self.webroot / "Scripts" / "AMP.js").write_text(AMP_JS, encoding="utf-8")
        (self.webroot / "Scripts" / "Locale.js").write_text(LOCALE_JS, encoding="utf-8")
        (self.webroot / "AMP.html").write_text(AMP_HTML, encoding="utf-8")
        self.env = os.environ.copy()
        self.env["AMP_WEBROOT"] = str(self.webroot)

    def tearDown(self):
        self.temp.cleanup()

    def run_installer(self):
        return subprocess.run(
            [sys.executable, str(INSTALLER)], env=self.env,
            text=True, capture_output=True, check=False,
        )

    def assert_dom_runtime(self, original, patched, mode):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is needed for the DOM behavior test")
        result = subprocess.run(
            [node, str(DOM_HARNESS), str(original), str(patched), mode],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_clean_install_and_idempotent_rerun(self):
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        locale = self.webroot / "Locale" / "pt.json"
        locale_js = self.webroot / "Scripts" / "Locale.js"
        amp_js = self.webroot / "Scripts" / "AMP.js"
        html = self.webroot / "AMP.html"
        self.assertTrue(locale.is_file())
        installed_locale = json.loads(locale.read_text(encoding="utf-8"))
        expected_setup_strings = {
            "AMP First Time Setup": "Configuração inicial do AMP",
            "Welcome to": "Bem-vindo ao",
            "Please click Next >> to continue setup.": "Clique em Avançar >> para continuar a configuração.",
            "Next >>": "Avançar >>",
            "Default Authentication Server": "Servidor de autenticação padrão",
            "Re-run Setup": "Executar a configuração novamente",
        }
        for key, value in expected_setup_strings.items():
            self.assertEqual(installed_locale["Strings"].get(key), value)
        patched_locale_js = locale_js.read_text(encoding="utf-8")
        self.assertIn("startLocaleObserver", patched_locale_js)
        self.assertIn("context.nodeType === Node.ELEMENT_NODE", patched_locale_js)
        self.assertIn('root.find("*").addBack()', patched_locale_js)
        self.assertIn("replaceWithNonBreakingSpace(Locale.l(displayName))", amp_js.read_text(encoding="utf-8"))
        saved_html = html.read_text(encoding="utf-8")
        self.assertEqual(saved_html.count("ptbr=1"), 3)
        self.assertIn('/Scripts/Locale.js?v=2.8.0.10&amp;ptbr=1"', saved_html)
        self.assertEqual(len(list(self.webroot.rglob("*.bak.*"))), 3)
        repeated = self.run_installer()
        self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
        self.assertIn("nada foi alterado", repeated.stdout)

    def test_existing_locale_keeps_local_keys_and_receives_repository_strings(self):
        locale_path = self.webroot / "Locale" / "pt.json"
        locale_path.write_text(json.dumps({
            "LocaleName": "pt",
            "Strings": {
                "Local custom label": "Rótulo local",
                "Re-run Setup": "Texto antigo"
            }
        }, ensure_ascii=False), encoding="utf-8")
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        saved = json.loads(locale_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["Strings"]["Local custom label"], "Rótulo local")
        self.assertEqual(saved["Strings"]["Re-run Setup"], "Executar a configuração novamente")
        self.assertEqual(saved["Strings"]["Welcome to"], "Bem-vindo ao")

    def test_legacy_selector_dom_context_and_dynamic_insertions(self):
        original = self.webroot / "Scripts" / "Locale.before.js"
        original.write_text(LEGACY_LOCALE_JS, encoding="utf-8")
        path = self.webroot / "Scripts" / "Locale.js"
        path.write_text(LEGACY_LOCALE_JS, encoding="utf-8")
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        saved = path.read_text(encoding="utf-8")
        self.assertIn("context.nodeType === Node.ELEMENT_NODE", saved)
        self.assertIn('const elements = root.find("*").addBack();', saved)
        self.assertIn("elements\n                .contents()", saved)
        self.assertEqual(saved.count("const startLocaleObserver = function () {"), 1)
        self.assert_dom_runtime(original, path, "legacy")
        repeated = self.run_installer()
        self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
        self.assertIn("nada foi alterado", repeated.stdout)

    def test_jquery_context_shape_and_existing_observer(self):
        original = self.webroot / "Scripts" / "Locale.before.js"
        original.write_text(JQUERY_LOCALE_JS, encoding="utf-8")
        path = self.webroot / "Scripts" / "Locale.js"
        path.write_text(JQUERY_LOCALE_JS, encoding="utf-8")
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        saved = path.read_text(encoding="utf-8")
        self.assertIn("context.nodeType === Node.ELEMENT_NODE", saved)
        self.assertEqual(saved.count("const startLocaleObserver = function () {"), 1)
        self.assert_dom_runtime(original, path, "jquery")

    def test_refreshes_locale_url_after_previous_installer_run(self):
        first = self.run_installer()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        html = self.webroot / "AMP.html"
        saved_html = html.read_text(encoding="utf-8")
        self.assertIn('/Scripts/Locale.js?v=2.8.0.10&amp;ptbr=1"', saved_html)
        html.write_text(saved_html.replace(
            '/Scripts/Locale.js?v=2.8.0.10&amp;ptbr=1"',
            '/Scripts/Locale.js?v=2.8.0.10"',
        ), encoding="utf-8")
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('/Scripts/Locale.js?v=2.8.0.10&amp;ptbr=1"', html.read_text(encoding="utf-8"))
        self.assertIn("Locale.js", result.stdout)

    def test_unrecognized_locale_observer_fails_without_changes(self):
        path = self.webroot / "Scripts" / "Locale.js"
        path.write_text(LOCALE_JS.replace(
            "    return obj;", "    const customObserver = new MutationObserver(() => {});\n    return obj;"
        ), encoding="utf-8")
        before = {p.relative_to(self.webroot): p.read_bytes() for p in self.webroot.rglob("*") if p.is_file()}
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Locale.js já tem um observador diferente", result.stderr)
        after = {p.relative_to(self.webroot): p.read_bytes() for p in self.webroot.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(list(self.webroot.rglob("*.bak.*")), [])

    def test_public_locale_contains_setup_strings_and_tutorial_teaches_lang_query(self):
        locale = json.loads((REPO / "locale" / "pt.json").read_text(encoding="utf-8"))
        expected = {
            "AMP First Time Setup": "Configuração inicial do AMP",
            "Welcome to": "Bem-vindo ao",
            "Please click Next >> to continue setup.": "Clique em Avançar >> para continuar a configuração.",
            "Next >>": "Avançar >>",
            "Default Authentication Server": "Servidor de autenticação padrão",
            "Re-run Setup": "Executar a configuração novamente",
        }
        for key, value in expected.items():
            self.assertEqual(locale["Strings"].get(key), value)
        tutorial = (REPO / "docs" / "tutorial-locale-pt-br.md").read_text(encoding="utf-8")
        self.assertIn("https://amp.exemplo.org/configuration/instancedeployment?lang=pt", tutorial)
        self.assertIn("Se o endereço já tiver um `?`", tutorial)
        self.assertIn("&lang=pt", tutorial)
        self.assertIn("Não coloque `?lang=pt` entre o domínio e o caminho", tutorial)
        self.assertIn("Controller/Target não compartilha", tutorial)


if __name__ == "__main__":
    unittest.main()
