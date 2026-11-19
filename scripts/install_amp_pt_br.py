#!/usr/bin/env python3
"""Apply the tested AMP 2.8.0.10 PT-BR locale and compatibility fixes.

Set AMP_WEBROOT to the target AMP WebRoot before running.
"""
from datetime import datetime
from pathlib import Path
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from html import unescape
from urllib.parse import parse_qs, urlsplit

_webroot = os.environ.get("AMP_WEBROOT")
if not _webroot:
    raise SystemExit("Defina AMP_WEBROOT com o caminho do WebRoot da instância AMP; nada foi alterado.")
if not Path(_webroot).expanduser().is_absolute():
    raise SystemExit("AMP_WEBROOT precisa ser um caminho absoluto; nada foi alterado.")
WEBROOT = Path(_webroot).expanduser().resolve()
AMP_JS = WEBROOT / "Scripts/AMP.js"
HTML = WEBROOT / "AMP.html"
LOCALE = WEBROOT / "Locale/pt.json"
OLD_REF = '/Scripts/AMP.js?v=2.8.0.10-ptbr-category1'
# Keep the AMP-owned version parameter exact; use a separate cache-busting parameter.
NEW_REF = '/Scripts/AMP.js?v=2.8.0.10&amp;ptbr=1'
OLD_CATEGORY_FIX = 'this.displayName = replaceWithNonBreakingSpace(displayName);'
CATEGORY_FIX = 'this.displayName = replaceWithNonBreakingSpace(Locale.l(displayName));'
OLD_WARNING_LINE = '            await UI.ShowModalAsync("AMP Version Mismatch", `The AMP frontend that has been loaded (v${versionParam}) does not match the backend (v${moduleInfo.APIVersion}). Please clear your browser cache (or force reload with CTRL+F5) as well as any upstream proxy caches.`, UI.Icons.Exclamation, UI.OKActionOnly);'
NEW_WARNING_BLOCK = '''            const mismatchTitle = Locale.GetLocaleMessage("AMP Version Mismatch");
            const mismatchTemplate = Locale.GetLocaleMessage("The AMP frontend that has been loaded ({frontendVersion}) does not match the backend ({backendVersion}). Please clear your browser cache (or force reload with CTRL+F5) as well as any upstream proxy caches.");
            const mismatchText = mismatchTemplate.replace("{frontendVersion}", versionParam).replace("{backendVersion}", moduleInfo.APIVersion);
            await UI.ShowModalAsync(mismatchTitle, mismatchText, UI.Icons.Exclamation, UI.OKActionOnly);'''
TRANSLATIONS = {
    "AMP Version Mismatch": "Incompatibilidade de versão do AMP",
    "The AMP frontend that has been loaded ({frontendVersion}) does not match the backend ({backendVersion}). Please clear your browser cache (or force reload with CTRL+F5) as well as any upstream proxy caches.": "A versão da interface do AMP carregada (v{frontendVersion}) não corresponde à do servidor (v{backendVersion}). Limpe o cache do navegador (ou force a atualização com Ctrl+F5) e também o cache de proxies intermediários.",
}

for path in (AMP_JS, HTML, LOCALE):
    if path.is_symlink() or not path.is_file():
        raise SystemExit(f"Parado sem alterar nada: arquivo esperado ausente ou link simbólico: {path}")

try:
    raw_js = AMP_JS.read_bytes()
    raw_html = HTML.read_bytes()
    raw_locale = LOCALE.read_bytes()
    js_bom = raw_js.startswith(b"\xef\xbb\xbf")
    html_bom = raw_html.startswith(b"\xef\xbb\xbf")
    locale_bom = raw_locale.startswith(b"\xef\xbb\xbf")
    js_nl = "\r\n" if b"\r\n" in raw_js else "\n"
    html_nl = "\r\n" if b"\r\n" in raw_html else "\n"
    js = raw_js.decode("utf-8-sig").replace("\r\n", "\n")
    html = raw_html.decode("utf-8-sig").replace("\r\n", "\n")
    locale = json.loads(raw_locale.decode("utf-8-sig"))
except Exception as exc:
    raise SystemExit(f"Parado sem alterar nada: falha ao ler os arquivos: {exc}")

strings = locale.get("Strings")
if locale.get("LocaleName") != "pt" or not isinstance(strings, dict):
    raise SystemExit("Parado sem alterar nada: pt.json não é um locale PT válido.")
if strings.get("Monitoring and Metrics") != "Monitoramento e métricas":
    raise SystemExit("Parado sem alterar nada: falta a tradução da aba já corrigida.")
if "function SettingSubcategoryVM(name, category, settings) {" not in js:
    raise SystemExit("Parado sem alterar nada: SettingSubcategoryVM não corresponde ao AMP 2.8.0.10 esperado.")
old_category_count, new_category_count = js.count(OLD_CATEGORY_FIX), js.count(CATEGORY_FIX)
if old_category_count == 1 and new_category_count == 0:
    js = js.replace(OLD_CATEGORY_FIX, CATEGORY_FIX, 1)
elif old_category_count == 0 and new_category_count == 1:
    pass  # Already fixed; safe to rerun.
else:
    raise SystemExit(f"Parado sem alterar nada: código da aba inesperado (original={old_category_count}, corrigido={new_category_count}).")
if "function checkVersionMismatch(moduleInfo)" not in js or "moduleInfo.APIVersion" not in js:
    raise SystemExit("Parado sem alterar nada: AMP.js não contém a verificação de versão esperada.")

old_line_count = js.count(OLD_WARNING_LINE)
new_block_count = js.count(NEW_WARNING_BLOCK)
if old_line_count == 1 and new_block_count == 0:
    js = js.replace(OLD_WARNING_LINE, NEW_WARNING_BLOCK, 1)
elif old_line_count == 0 and new_block_count == 1:
    pass  # Already localized; allow a safe repeat.
else:
    raise SystemExit(f"Parado sem alterar nada: aviso de incompatibilidade ambíguo (original={old_line_count}, corrigido={new_block_count}).")

for key, value in TRANSLATIONS.items():
    strings[key] = value
if strings.get("Monitoring and Metrics") != "Monitoramento e métricas":
    raise SystemExit("Parado sem alterar nada: validação da tradução da aba falhou.")

old_ref_count, new_ref_count = html.count(OLD_REF), html.count(NEW_REF)
if old_ref_count == 2 and new_ref_count == 0:
    html = html.replace(OLD_REF, NEW_REF)
elif old_ref_count == 0 and new_ref_count == 2:
    pass  # Already fixed; safe to rerun.
else:
    raise SystemExit(f"Parado sem alterar nada: referências AMP.js inesperadas (antiga={old_ref_count}, corrigida={new_ref_count}).")
if html.count(NEW_REF) != 2:
    raise SystemExit("Parado sem alterar nada: não atualizei as duas referências AMP.js.")
# This query is what AMP's backend comparison reads; it must remain exactly 2.8.0.10.
if NEW_REF.split("?", 1)[1].split("&amp;", 1)[0] != "v=2.8.0.10":
    raise SystemExit("Parado sem alterar nada: o parâmetro de versão não corresponde ao backend.")

new_js_bytes = (b"\xef\xbb\xbf" if js_bom else b"") + js.replace("\n", js_nl).encode("utf-8")
new_html_bytes = (b"\xef\xbb\xbf" if html_bom else b"") + html.replace("\n", html_nl).encode("utf-8")
locale_text = json.dumps(locale, ensure_ascii=False, separators=(",", ":"))
new_locale_bytes = (b"\xef\xbb\xbf" if locale_bom else b"") + locale_text.encode("utf-8")
changes = {AMP_JS: new_js_bytes, HTML: new_html_bytes, LOCALE: new_locale_bytes}
if all(path.read_bytes() == data for path, data in changes.items()):
    print("A URL de versão, o aviso traduzido e as traduções já estão aplicados; nada foi alterado.")
    raise SystemExit(0)

# Validate JavaScript before writing anything.
node = shutil.which("node")
if node:
    check = subprocess.run([node, "--check", "-"], input=js, text=True, capture_output=True)
    if check.returncode:
        raise SystemExit("Parado sem alterar nada: AMP.js falhou na validação de sintaxe.\n" + check.stderr)

stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backups, staged, replaced = {}, {}, []
try:
    for path, data in changes.items():
        original_stat = path.stat()
        backup = path.with_name(path.name + ".bak." + stamp)
        shutil.copy2(path, backup)
        backups[path] = backup
        fd, temp_name = tempfile.mkstemp(prefix=path.name + ".wabi-", suffix=".tmp", dir=path.parent)
        temp_path = Path(temp_name)
        staged[path] = temp_path
        with os.fdopen(fd, "wb") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.chmod(temp_path, stat.S_IMODE(original_stat.st_mode))
        os.chown(temp_path, original_stat.st_uid, original_stat.st_gid)
    for path, temp_path in staged.items():
        os.replace(temp_path, path)
        replaced.append(path)
except Exception as exc:
    for path in reversed(replaced):
        shutil.copy2(backups[path], path)
    for temp_path in staged.values():
        temp_path.unlink(missing_ok=True)
    raise SystemExit(f"Falha ao instalar; restaurei os arquivos alterados pelos backups: {exc}")

try:
    saved_js = AMP_JS.read_text(encoding="utf-8-sig")
    saved_html = HTML.read_text(encoding="utf-8-sig")
    saved_locale = json.loads(LOCALE.read_text(encoding="utf-8-sig"))
    saved_strings = saved_locale["Strings"]
    parsed_refs = [parse_qs(urlsplit(unescape(ref)).query) for ref in re.findall(r'(?:src|href)="([^" ]*AMP\.js\?[^" ]*)"', saved_html)]
    valid = (
        CATEGORY_FIX in saved_js
        and NEW_WARNING_BLOCK in saved_js
        and saved_html.count(NEW_REF) == 2
        and len(parsed_refs) == 2
        and all(ref.get("v") == ["2.8.0.10"] and ref.get("ptbr") == ["1"] for ref in parsed_refs)
        and saved_strings.get("Monitoring and Metrics") == "Monitoramento e métricas"
        and all(saved_strings.get(k) == v for k, v in TRANSLATIONS.items())
    )
    if not valid:
        raise ValueError("a verificação pós-instalação não encontrou todos os valores esperados")
    if node:
        check = subprocess.run([node, "--check", str(AMP_JS)], capture_output=True, text=True)
        if check.returncode:
            raise ValueError("AMP.js salvo não passou na verificação de sintaxe: " + check.stderr)
except Exception as exc:
    for path in reversed(replaced):
        shutil.copy2(backups[path], path)
    raise SystemExit(f"Verificação final falhou; restaurei os arquivos pelos backups. {exc}")

print("Corrigido: o parâmetro v da URL do AMP.js continua exatamente 2.8.0.10; ptbr=1 só renova o cache.")
print("A chave Monitoring and Metrics continua traduzida, e AMP Version Mismatch agora tem título e mensagem em português.")
for path, backup in backups.items():
    print(f"Backup: {backup}")
print("Recarregue o painel uma vez; limpe também qualquer cache intermediário se a versão continuar divergente.")
