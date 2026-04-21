@echo off
REM ============================================================================
REM  Ascend Research Stack - installer Windows (cmd / PowerShell compatible)
REM ============================================================================
REM  Installe :
REM    - les skills et agents custom du stack
REM    - les skills externes Weizhena/Deep-Research-skills
REM    - les skills externes 199-biotechnologies/claude-deep-research-skill
REM    - la dependance Python pyyaml
REM ============================================================================

setlocal enableextensions enabledelayedexpansion

set "REPO_ROOT=%~dp0"
if "%REPO_ROOT:~-1%"=="\" set "REPO_ROOT=%REPO_ROOT:~0,-1%"

REM ---- Parse CLI args -------------------------------------------------------
set "DRY_RUN="
set "FORCE="
:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--dry-run" (set "DRY_RUN=1" & shift & goto parse_args)
if /i "%~1"=="--force"   (set "FORCE=1"   & shift & goto parse_args)
if /i "%~1"=="--help"    (call :usage & exit /b 0)
if /i "%~1"=="-h"        (call :usage & exit /b 0)
echo [fail] Unknown option: %~1  (try --help)
exit /b 1
:args_done

set "SMART_OPTS="
if defined DRY_RUN set "SMART_OPTS=%SMART_OPTS% --dry-run"
if defined FORCE   set "SMART_OPTS=%SMART_OPTS% --force"

if defined CLAUDE_HOME (
  set "CLAUDE_DIR=%CLAUDE_HOME%"
) else (
  set "CLAUDE_DIR=%USERPROFILE%\.claude"
)

set "SKILLS_DIR=%CLAUDE_DIR%\skills"
set "AGENTS_DIR=%CLAUDE_DIR%\agents"
set "TMP_DIR=%TEMP%\ascend-research-stack-%RANDOM%"

echo.
echo [install] Ascend Research Stack - installation Windows
echo [install] Repo    : %REPO_ROOT%
echo [install] Claude  : %CLAUDE_DIR%
if defined DRY_RUN echo [warn] Mode --dry-run : aucune ecriture sur ~/.claude/. Prerequis et git clone temp s'executent normalement.
if defined FORCE   echo [warn] Mode --force : les fichiers user modifies seront ecrases ^(backup .bak^).
echo.

REM ---- 1. Prerequis ---------------------------------------------------------
where git >nul 2>&1
if errorlevel 1 (
  echo [fail] git introuvable. Installe Git for Windows.
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo [fail] python introuvable. Installe Python 3.x.
    exit /b 1
  )
)

where claude >nul 2>&1
if errorlevel 1 (
  echo [warn] Claude Code non detecte dans le PATH. Installe-le depuis https://claude.com/claude-code.
) else (
  echo [ ok ] Claude Code detecte.
)

if not exist "%SKILLS_DIR%" mkdir "%SKILLS_DIR%"
if not exist "%AGENTS_DIR%" mkdir "%AGENTS_DIR%"
if not exist "%TMP_DIR%"    mkdir "%TMP_DIR%"

REM ---- 1bis. Config consultant (nom, email, handle) ------------------------
set "CONFIG_FILE=%REPO_ROOT%\config\consultant.json"
if exist "%CONFIG_FILE%" (
  echo [ ok ] Config consultant existe deja : %CONFIG_FILE%
  goto consultant_done
)

echo [install] Premiere installation : configuration du consultant.
set "_DEFAULT_NAME="
set "_DEFAULT_EMAIL="
for /f "delims=" %%a in ('git -C "%REPO_ROOT%" config user.name 2^>nul') do set "_DEFAULT_NAME=%%a"
for /f "delims=" %%a in ('git -C "%REPO_ROOT%" config user.email 2^>nul') do set "_DEFAULT_EMAIL=%%a"

set /p "_CN=Nom du consultant [%_DEFAULT_NAME%] : "
if "%_CN%"=="" set "_CN=%_DEFAULT_NAME%"
set /p "_CE=Email [%_DEFAULT_EMAIL%] : "
if "%_CE%"=="" set "_CE=%_DEFAULT_EMAIL%"
set /p "_CH=Handle (optionnel) : "

if "%_CN%"=="" goto consultant_warn
if "%_CE%"=="" goto consultant_warn

if defined DRY_RUN (
  echo [dry-run] WOULD WRITE %CONFIG_FILE%
  goto consultant_done
)
if not exist "%REPO_ROOT%\config" mkdir "%REPO_ROOT%\config"
> "%CONFIG_FILE%" echo {
>> "%CONFIG_FILE%" echo   "consultant_name": "%_CN%",
>> "%CONFIG_FILE%" echo   "consultant_email": "%_CE%",
>> "%CONFIG_FILE%" echo   "consultant_handle": "%_CH%"
>> "%CONFIG_FILE%" echo }
echo [ ok ] Config consultant creee : %CONFIG_FILE%
goto consultant_done

:consultant_warn
echo [warn] Nom ou email vide — config consultant non creee. Les placeholders {{CONSULTANT_*}} resteront non substitues.
echo [warn] Pour corriger : copier config\consultant.example.json en config\consultant.json, puis rejouer install.bat.

:consultant_done
echo.

REM ---- 2. Skills externes ---------------------------------------------------
echo [install] Clonage des skills externes...

git clone --depth 1 https://github.com/Weizhena/Deep-Research-skills.git "%TMP_DIR%\deep-research-skills" >nul 2>&1
if errorlevel 1 (
  echo [warn] Clonage Deep-Research-skills echoue.
) else (
  if exist "%TMP_DIR%\deep-research-skills\skills" (
    call python "%REPO_ROOT%\scripts\install_helpers.py" smart-copy %SMART_OPTS% "%TMP_DIR%\deep-research-skills\skills" "%SKILLS_DIR%"
    echo [ ok ] Deep-Research-skills traite.
  ) else (
    call python "%REPO_ROOT%\scripts\install_helpers.py" smart-copy %SMART_OPTS% "%TMP_DIR%\deep-research-skills" "%SKILLS_DIR%\deep-research-skills"
    echo [ ok ] Deep-Research-skills traite ^(structure alternative^).
  )
)

git clone --depth 1 https://github.com/199-biotechnologies/claude-deep-research-skill.git "%TMP_DIR%\claude-deep-research-skill" >nul 2>&1
if errorlevel 1 (
  echo [warn] Clonage claude-deep-research-skill echoue.
) else (
  if exist "%TMP_DIR%\claude-deep-research-skill\skills" (
    call python "%REPO_ROOT%\scripts\install_helpers.py" smart-copy %SMART_OPTS% "%TMP_DIR%\claude-deep-research-skill\skills" "%SKILLS_DIR%"
  ) else (
    call python "%REPO_ROOT%\scripts\install_helpers.py" smart-copy %SMART_OPTS% "%TMP_DIR%\claude-deep-research-skill" "%SKILLS_DIR%\claude-deep-research-skill"
  )
  echo [ ok ] claude-deep-research-skill traite.
)

REM ---- 3. Skills custom Ascend ---------------------------------------------
echo [install] Installation des skills custom Ascend...
if exist "%REPO_ROOT%\skills" (
  call python "%REPO_ROOT%\scripts\install_helpers.py" smart-copy %SMART_OPTS% "%REPO_ROOT%\skills" "%SKILLS_DIR%"
  echo [ ok ] Skills custom traites ^(voir stats ci-dessus^).
) else (
  echo [fail] Dossier skills/ introuvable.
  exit /b 1
)

REM ---- 4. Agents custom Ascend ---------------------------------------------
echo [install] Installation des agents custom Ascend...
if exist "%REPO_ROOT%\agents" (
  call python "%REPO_ROOT%\scripts\install_helpers.py" smart-copy %SMART_OPTS% "%REPO_ROOT%\agents" "%AGENTS_DIR%"
  echo [ ok ] Agents custom traites ^(voir stats ci-dessus^).
) else (
  echo [warn] Dossier agents/ introuvable.
)

REM ---- 4bis. Application de la config consultant ---------------------------
if defined DRY_RUN (
  echo [dry-run] WOULD apply consultant config to installed skills and agents.
  goto post_consultant
)
if exist "%CONFIG_FILE%" (
  echo [install] Application de la config consultant aux skills et agents installes...
  where python >nul 2>&1
  if not errorlevel 1 (
    call python "%REPO_ROOT%\scripts\apply_consultant_config.py" "%CONFIG_FILE%" "%SKILLS_DIR%" "%AGENTS_DIR%"
    if errorlevel 1 (
      echo [warn] Substitution consultant echouee.
    ) else (
      echo [ ok ] Placeholders {{CONSULTANT_*}} substitues.
    )
  ) else (
    echo [warn] Python introuvable — substitution consultant skipee.
  )
) else (
  echo [warn] Pas de config\consultant.json — skills et agents conservent les placeholders.
)
:post_consultant

REM ---- 5. Python deps (pyyaml + jsonschema + openpyxl + python-docx) ------
if defined DRY_RUN (
  echo [dry-run] WOULD pip install --user pyyaml jsonschema openpyxl python-docx
  goto post_pyyaml
)
echo [install] Installation de pyyaml + jsonschema + openpyxl + python-docx...
where python >nul 2>&1
if not errorlevel 1 (
  python -m pip install --quiet --user pyyaml jsonschema openpyxl python-docx
) else (
  py -m pip install --quiet --user pyyaml jsonschema openpyxl python-docx
)
echo [ ok ] Dependances Python OK.
:post_pyyaml

REM ---- 6. MCP Firecrawl (optionnel mais recommande) -------------------------
echo.
echo [install] Configuration du MCP Firecrawl...

if defined DRY_RUN (
  echo [dry-run] WOULD configure Firecrawl MCP via 'claude mcp add'.
  goto firecrawl_done
)

where claude >nul 2>&1
if errorlevel 1 (
  echo [warn] Claude Code absent : skip MCP Firecrawl.
  goto firecrawl_done
)

claude mcp list 2>nul | findstr /C:"firecrawl" >nul 2>&1
if %errorlevel% EQU 0 (
  echo [ ok ] MCP Firecrawl deja configure.
  goto firecrawl_done
)

if "%FIRECRAWL_API_KEY%"=="" (
  echo [install] Firecrawl permet aux investigator de scraper les sites editeurs.
  echo [install] Inscription gratuite : https://www.firecrawl.dev
  set /p "FIRECRAWL_API_KEY=Cle Firecrawl (fc-...) ou Entree pour skip : "
)

if "%FIRECRAWL_API_KEY%"=="" (
  echo [warn] Cle Firecrawl non fournie. Investigator en mode degrade ^(WebFetch seul^).
  echo [warn] Pour l'ajouter plus tard :
  echo [warn]   claude mcp add --scope user firecrawl -e FIRECRAWL_API_KEY=fc-xxx -- npx -y firecrawl-mcp
  goto firecrawl_done
)

call claude mcp add --scope user firecrawl -e FIRECRAWL_API_KEY=%FIRECRAWL_API_KEY% -- npx -y firecrawl-mcp
if errorlevel 1 (
  echo [warn] Echec ajout MCP Firecrawl, a faire manuellement.
) else (
  echo [ ok ] MCP Firecrawl ajoute ^(scope user^).
)

:firecrawl_done
echo.

REM ---- 7. Cleanup + resume --------------------------------------------------
rmdir /S /Q "%TMP_DIR%" >nul 2>&1

echo.
echo -------------------------------------------------------------------
echo   Ascend Research Stack installe avec succes.
echo -------------------------------------------------------------------
echo.
echo Skills installes  : %SKILLS_DIR%
echo Agents installes  : %AGENTS_DIR%
echo.
echo Next steps :
echo   1. cd %REPO_ROOT%
echo   2. claude
echo   3. Essaie : "Benchmark-moi les solutions de RAG d entreprise, grille health-ai"
echo.

endlocal
exit /b 0

:usage
echo Usage: install.bat [--dry-run] [--force]
echo   --dry-run   Affiche ce qui changerait sur %%USERPROFILE%%\.claude\ sans ecrire.
echo   --force     Ecrase les fichiers user modifies (backup .bak en silence).
echo               Sans --force, un prompt [k/o/b] s'affiche par fichier modifie.
echo   --help      Affiche cette aide.
exit /b 0
