import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
INSTALLER = REPO / "scripts" / "install_amp_pt_br.py"

AMP_JS = '''function SettingSubcategoryVM(name, category, settings) {
            this.displayName = replaceWithNonBreakingSpace(displayName);
}
async function checkVersionMismatch(moduleInfo) {
            const versionParam = "2.8.0.10";
            await UI.ShowModalAsync("AMP Version Mismatch", `The AMP frontend that has been loaded (v${versionParam}) does not match the backend (v${moduleInfo.APIVersion}). Please clear your browser cache (or force reload with CTRL+F5) as well as any upstream proxy caches.`, UI.Icons.Exclamation, UI.OKActionOnly);
}
'''
LOCALE_JS = '''const Locale = (function () {
    let loadedLocale = "pt";
    const obj = {
        GetLocaleMessage: function (original) { return original; },
        ApplyLocale: function (context) {
            const elements = $((context || "body") + " *");
            elements.each(function () {});
        },
        ListLocale: function () {},
    };
    obj.l = obj.GetLocaleMessage;
    return obj;
})();
'''
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
        self.assertIn("startLocaleObserver", locale_js.read_text(encoding="utf-8"))
        self.assertIn("context.nodeType === Node.ELEMENT_NODE", locale_js.read_text(encoding="utf-8"))
        self.assertIn('root.find("*").addBack()', locale_js.read_text(encoding="utf-8"))
        self.assertIn("replaceWithNonBreakingSpace(Locale.l(displayName))", amp_js.read_text(encoding="utf-8"))
        saved_html = html.read_text(encoding="utf-8")
        self.assertEqual(saved_html.count("ptbr=1"), 3)
        self.assertIn('/Scripts/Locale.js?v=2.8.0.10&amp;ptbr=1"', saved_html)
        self.assertEqual(len(list(self.webroot.rglob("*.bak.*"))), 3)
        repeated = self.run_installer()
        self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
        self.assertIn("nada foi alterado", repeated.stdout)

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


if __name__ == "__main__":
    unittest.main()
