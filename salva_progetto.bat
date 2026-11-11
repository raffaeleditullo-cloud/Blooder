@echo off
cd /d "%~dp0"
echo [Blooder] Verifica database, controllo anti-chiavi ed esportazione catalogo...
python sync_libreria.py
if errorlevel 1 (
    echo [ERRORE] Controllo fallito o chiave privata rilevata! Salvataggio bloccato per sicurezza.
    if not "%1"=="--auto" pause
    exit /b 1
)

git add -A
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Aggiornamento libreria Blooder (%date% %time%)"
    echo [Blooder] Punto di salvataggio locale creato.
) else (
    echo [Blooder] Nessuna nuova modifica locale da registrare.
)

git remote get-url origin >nul 2>&1
if not errorlevel 1 (
    echo [Blooder] Sincronizzazione con GitHub (ramo main)...
    git push -u origin HEAD:main
    if errorlevel 1 (
        echo [AVVISO] Salvataggio locale riuscito, ma invio a GitHub non completato. Controlla la connessione.
    ) else (
        echo [Blooder] Libreria pubblicata e allineata su GitHub con successo!
    )
)

if not "%1"=="--auto" pause
