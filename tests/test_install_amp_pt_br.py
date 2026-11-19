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
        ApplyLocale: function (context) { return context; },
    };
    obj.l = obj.GetLocaleMessage;
    return obj;
})();
'''
AMP_HTML = '''<script src="/Scripts/AMP.js?v=2.8.0.10"></script>
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
        self.assertIn("startLocaleObserver", locale_js.read_text(encoding="utf-8"))
        self.assertIn("replaceWithNonBreakingSpace(Locale.l(displayName))", amp_js.read_text(encoding="utf-8"))
        self.assertEqual(html.read_text(encoding="utf-8").count("ptbr=1"), 2)
        self.assertEqual(len(list(self.webroot.rglob("*.bak.*"))), 3)
        repeated = self.run_installer()
        self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
        self.assertIn("nada foi alterado", repeated.stdout)

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
