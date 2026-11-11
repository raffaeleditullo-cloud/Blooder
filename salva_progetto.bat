@echo off
cd /d "%~dp0"
echo [Blooder] Verifica database ed esportazione backup JSON...
python -c "import json; from blooder_db import init_db, list_skills, get_connection; init_db(); c = get_connection(); ok = c.execute('PRAGMA integrity_check').fetchone()[0]; c.close(); assert ok == 'ok', ok; data = {'skills': list_skills(kind='skill'), 'tools': list_skills(kind='tool')}; open('backup_libreria.json', 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=2)); print(f'Integrita DB: {ok} | Salvate {len(data[\"skills\"])} skill e {len(data[\"tools\"])} strumenti in backup_libreria.json')"
if errorlevel 1 (
    echo [ERRORE] Verifica database fallita!
    if not "%1"=="--auto" pause
    exit /b 1
)

git add -A
git diff --cached --quiet
if errorlevel 1 (
    for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set TODAY=%%c-%%b-%%a
    git commit -m "Salvataggio progetto Blooder (%date% %time%)"
    echo [Blooder] Nuovo punto di salvataggio Git creato con successo!
) else (
    echo [Blooder] Tutto gia allineato, nessuna nuova modifica da salvare in Git.
)

if not "%1"=="--auto" pause
