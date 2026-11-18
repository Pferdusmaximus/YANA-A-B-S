"""YANA: ergänzt den neuen Router und die Links, ohne bestehende Dateien zu ersetzen.
Aus dem Git-Repository-Stamm ausführen: python tools/apply_integration.py
Schreibt vor jeder Änderung eine Sicherung in das Benutzerprofil.
"""
from datetime import datetime
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / 'services' / 'api'
MAIN = API / 'main.py'
LIST = API / 'templates' / 'portal' / 'hilfestellen.html'
CSS = API / 'static' / 'css' / 'style.css'
CSS_ADDITION = API / 'static' / 'css' / 'yana_changes_append.css'

files = (MAIN, LIST, CSS)
for path in (*files, CSS_ADDITION, API / 'portal_facility_changes.py',
             API / 'templates' / 'portal' / 'aenderung_bearbeiten.html',
             API / 'templates' / 'portal' / 'aenderungen_pruefen.html'):
    if not path.exists():
        raise SystemExit(f'FEHLT: {path}. ZIP bitte im Repository-Stamm entpacken.')

main = MAIN.read_text(encoding='utf-8')
html = LIST.read_text(encoding='utf-8')
css = CSS.read_text(encoding='utf-8')
addition = CSS_ADDITION.read_text(encoding='utf-8')

# Bekannte Anker aus dem bisherigen YANA-Code.
if 'from portal_facility_changes import router as changes_router' not in main:
    needle = 'from portal_facilities_status import router as status_router'
    if needle not in main:
        raise SystemExit('Import-Anker in main.py fehlt. Bitte Datei statt Blindpatch prüfen.')
    main = main.replace(needle, needle + '\nfrom portal_facility_changes import router as changes_router', 1)
if 'app.include_router(changes_router)' not in main:
    needle = 'app.include_router(status_router)'
    if needle not in main:
        raise SystemExit('Router-Anker in main.py fehlt. Bitte Datei statt Blindpatch prüfen.')
    main = main.replace(needle, needle + '\napp.include_router(changes_router)', 1)

link_marker = '/portal/hilfestellen/{{ facility.facility_id }}/aenderung'
if link_marker not in html:
    needle = '<div class="facility-actions">'
    if needle not in html:
        raise SystemExit('Aktionen-Anker in hilfestellen.html fehlt. Bitte HTML zur Anpassung hochladen.')
    snippet = '''<div class="facility-actions">
                            {% if facility.publication_status == "published" %}
                                <a href="/portal/hilfestellen/{{ facility.facility_id }}/aenderung"
                                   class="facility-edit-link">Änderung vorschlagen</a>
                            {% endif %}'''
    html = html.replace(needle, snippet, 1)

if '/portal/aenderungen' not in html:
    needle = '<div class="facility-overview">'
    if needle not in html:
        raise SystemExit('Übersichts-Anker in hilfestellen.html fehlt. Bitte HTML zur Anpassung hochladen.')
    snippet = '''{% if account.role == "admin" %}
        <p><a href="/portal/aenderungen" class="facility-edit-link">Änderungsanträge prüfen</a></p>
        {% endif %}

        <div class="facility-overview">'''
    html = html.replace(needle, snippet, 1)

if '.yana-change-page {' not in css:
    css = css.rstrip() + '\n\n' + addition.rstrip() + '\n'

backup = Path.home() / 'yana-revision-backups' / datetime.now().strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True, exist_ok=True)
for src in files:
    if src == MAIN:
        dest = main
    elif src == LIST:
        dest = html
    else:
        dest = css
    original = src.read_text(encoding='utf-8')
    if original != dest:
        shutil.copy2(src, backup / src.name)
        src.write_text(dest, encoding='utf-8')
        print('Aktualisiert:', src.relative_to(ROOT))
    else:
        print('Bereits aktuell:', src.relative_to(ROOT))
print('Sicherungsverzeichnis:', backup)
print('Fertig. Jetzt py_compile, git diff und Tests ausführen.')
