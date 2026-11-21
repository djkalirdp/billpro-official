@echo off
chcp 65001 >nul 2>&1
title Billing Software Installer

color 0F
cls
echo.
echo  ================================================================
echo   BILLING SOFTWARE - WINDOWS INSTALLER
echo  ================================================================
echo.
echo  Yeh window band mat karna jab tak COMPLETE na dikhe!
echo.
echo  ================================================================
echo.

:: ----------------------------------------------------------------
:: STEP 1: PYTHON CHECK
:: ----------------------------------------------------------------
echo  [1/8]  Python check kar raha hoon...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        color 4F
        echo.
        echo  ================================================================
        echo   ERROR: Python nahi mila!
        echo  ================================================================
        echo.
        echo   Kya karo:
        echo   1. https://www.python.org/downloads/ kholo
        echo   2. Python 3.11 download karo
        echo   3. Install karo - ADD TO PATH zaroor tick karo
        echo   4. Computer restart karo
        echo   5. Dobara install.bat chalao
        echo.
        pause
        exit /b 1
    )
    set PYTHON=py
) else (
    set PYTHON=python
)

for /f "tokens=*" %%v in ('%PYTHON% --version 2^>^&1') do (
    echo  [1/8]  DONE - %%v mila
)

timeout /t 1 /nobreak >nul

:: ----------------------------------------------------------------
:: STEP 2: FIND THE APP FILES (download ONLY if they are missing)
:: ----------------------------------------------------------------
echo.
echo  [2/8]  App files check kar raha hoon...

:: Always work from the folder install.bat is in (not from wherever cmd was opened)
set "SELF=%~dp0"
if "%SELF:~-1%"=="\" set "SELF=%SELF:~0,-1%"
cd /d "%SELF%"

set "FORCE_UPDATE=0"
if /i "%~1"=="update" set "FORCE_UPDATE=1"

:: Case A: whole repo was downloaded and install.bat is inside it -> use this folder
:: Case B: otherwise use (or create) the billing-app folder next to install.bat
set "DEST=%SELF%\billing-app"
if exist "%SELF%\app.py" if exist "%SELF%\database_manager.py" if exist "%SELF%\templates\" set "DEST=%SELF%"

if "%FORCE_UPDATE%"=="1" goto :download_files
if exist "%DEST%\app.py" if exist "%DEST%\database_manager.py" if exist "%DEST%\templates\" goto :files_present
goto :download_files

:files_present
echo  [2/8]  DONE - Files pehle se maujood hain, download nahi karunga
echo         Folder: "%DEST%"
echo         (Naya version chahiye to chalao:  install.bat update)
goto :files_ready

:download_files
echo.
echo  [2/8]  GitHub se files download kar raha hoon...
echo         (Internet chahiye - 1-2 minute lag sakte hain)
echo.

if exist "billing-main.zip" (
    echo         Purana zip mila - delete kar raha hoon...
    del /f /q "billing-main.zip"
)

powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host '         Connecting to GitHub...'; Invoke-WebRequest -Uri 'https://github.com/djkalirdp/billpro-official/archive/refs/heads/main.zip' -OutFile 'billing-main.zip' -UseBasicParsing; Write-Host '         Download complete!'"

if not exist "billing-main.zip" (
    color 4F
    echo.
    echo  ================================================================
    echo   ERROR: Download fail ho gaya!
    echo  ================================================================
    echo.
    echo   Reasons:
    echo   - Internet connection check karo
    echo   - GitHub.com khul raha hai browser mein?
    echo   - Antivirus block kar raha ho to temporarily off karo
    echo.
    pause
    exit /b 1
)

for %%A in ("billing-main.zip") do (
    echo  [2/8]  DONE - %%~zA bytes download hua
)

timeout /t 1 /nobreak >nul

:: ----------------------------------------------------------------
:: STEP 3: EXTRACT FILES  (your data and settings are never overwritten)
:: ----------------------------------------------------------------
echo.
echo  [3/8]  Files extract kar raha hoon...

if exist "_bp_extract" rmdir /s /q "_bp_extract"

powershell -NoProfile -Command "Write-Host '         Extracting ZIP...'; Expand-Archive -Path 'billing-main.zip' -DestinationPath '_bp_extract' -Force; Write-Host '         Done!'"

:: GitHub names the top folder <repo>-main (billpro-official-main), so find it instead of guessing
set "SRC="
for /d %%D in ("_bp_extract\*") do set "SRC=%%~fD"

if not defined SRC (
    color 4F
    echo.
    echo  ERROR: Extract fail ho gaya!
    echo  Dobara chalao
    echo.
    pause
    exit /b 1
)

:: Files that must never be replaced by the downloaded copy
(
    echo \data\billing_app.db
    echo \settings.json
    echo \static\uploads\
    echo \install.bat
) > "_bp_exclude.txt"

if not exist "%DEST%" mkdir "%DEST%"

echo         Files copy kar raha hoon...
xcopy "%SRC%\*" "%DEST%\" /E /Y /Q /I /EXCLUDE:_bp_exclude.txt >nul 2>&1
if errorlevel 1 (
    color 4F
    echo.
    echo  ERROR: Files copy nahi huin! Dobara chalao
    echo.
    pause
    exit /b 1
)

rmdir /s /q "_bp_extract"
del /f /q "_bp_exclude.txt"
del /f /q "billing-main.zip"

echo  [3/8]  DONE - Files ready

timeout /t 1 /nobreak >nul

:files_ready
cd /d "%DEST%"

if not exist "data"            mkdir "data"
if not exist "backups"         mkdir "backups"
if not exist "invoices"        mkdir "invoices"
if not exist "reports"         mkdir "reports"
if not exist "static\uploads"  mkdir "static\uploads"

:: ----------------------------------------------------------------
:: STEP 4: VIRTUAL ENVIRONMENT
:: ----------------------------------------------------------------
echo.
echo  [4/8]  Python virtual environment bana raha hoon...

if exist "venv\Scripts\python.exe" (
    echo  [4/8]  DONE - Pehle se bana hua hai
) else (
    %PYTHON% -m venv venv
    if %errorlevel% neq 0 (
        color 4F
        echo  ERROR: venv nahi bana! Python reinstall karo
        pause
        exit /b 1
    )
    echo  [4/8]  DONE - Virtual environment ready
)

timeout /t 1 /nobreak >nul

:: ----------------------------------------------------------------
:: STEP 5: PIP UPGRADE
:: ----------------------------------------------------------------
echo.
echo  [5/8]  pip upgrade kar raha hoon...
venv\Scripts\python.exe -m pip install --upgrade pip -q
echo  [5/8]  DONE

timeout /t 1 /nobreak >nul

:: ----------------------------------------------------------------
:: STEP 6: INSTALL PACKAGES
:: ----------------------------------------------------------------
echo.
echo  [6/8]  Python packages install kar raha hoon...
echo         (2-5 minute lag sakte hain - wait karo)
echo.

echo         [1/6] flask...
venv\Scripts\pip.exe install flask -q
echo         [1/6] flask DONE

echo         [2/6] werkzeug...
venv\Scripts\pip.exe install werkzeug -q
echo         [2/6] werkzeug DONE

echo         [3/6] reportlab (PDF engine)...
venv\Scripts\pip.exe install reportlab -q
echo         [3/6] reportlab DONE

echo         [4/6] openpyxl (Excel)...
venv\Scripts\pip.exe install openpyxl -q
echo         [4/6] openpyxl DONE

echo         [5/6] num2words...
venv\Scripts\pip.exe install num2words -q
echo         [5/6] num2words DONE

echo         [6/6] qrcode + Pillow...
venv\Scripts\pip.exe install qrcode[pil] Pillow -q
echo         [6/6] qrcode DONE

echo.
echo  [6/8]  DONE - Saare packages ready

timeout /t 1 /nobreak >nul

:: ----------------------------------------------------------------
:: STEP 7: FONTS
:: ----------------------------------------------------------------
echo.
echo  [7/8]  Rupee symbol fonts download kar raha hoon...

if exist "DejaVuSans.ttf" (
    echo  [7/8]  DONE - Font pehle se hai
) else (
    powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf' -OutFile 'DejaVuSans.ttf' -UseBasicParsing" >nul 2>&1
    powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf' -OutFile 'DejaVuSans-Bold.ttf' -UseBasicParsing" >nul 2>&1
    if exist "DejaVuSans.ttf" (
        echo  [7/8]  DONE - Fonts ready
    ) else (
        echo  [7/8]  WARN - Font nahi mila, PDF mein Rs. dikhega
    )
)

timeout /t 1 /nobreak >nul

:: ----------------------------------------------------------------
:: STEP 8: CREATE start.bat
:: ----------------------------------------------------------------
echo.
echo  [8/8]  start.bat bana raha hoon...

(
    echo @echo off
    echo title Billing Software
    echo cd /d "%%~dp0"
    echo cls
    echo color 0A
    echo echo.
    echo echo  ================================================
    echo echo   BILLING SOFTWARE - Running
    echo echo   Browser mein kholo: http://localhost:5000
    echo echo   Login: admin / admin123
    echo echo   Band karne ke liye yeh window band karo
    echo echo  ================================================
    echo echo.
    echo start "" "http://localhost:5000"
    echo venv\Scripts\python.exe app.py
    echo pause
) > start.bat

echo  [8/8]  DONE - start.bat ready

:: ----------------------------------------------------------------
:: VERIFY
:: ----------------------------------------------------------------
echo.
echo  ----------------------------------------------------------------
echo   Quick verify kar raha hoon...
echo  ----------------------------------------------------------------
echo.

venv\Scripts\python.exe -c "import flask; print('  flask    - OK  v' + flask.__version__)" 2>nul || echo   flask    - ERROR
venv\Scripts\python.exe -c "import reportlab; print('  reportlab- OK')" 2>nul || echo   reportlab- ERROR
venv\Scripts\python.exe -c "import openpyxl; print('  openpyxl - OK  v' + openpyxl.__version__)" 2>nul || echo   openpyxl - ERROR
venv\Scripts\python.exe -c "from num2words import num2words; print('  num2words- OK')" 2>nul || echo   num2words- ERROR
venv\Scripts\python.exe -c "import qrcode; print('  qrcode   - OK')" 2>nul || echo   qrcode   - WARN (optional)

:: ----------------------------------------------------------------
:: DONE SCREEN
:: ----------------------------------------------------------------
color 0A
echo.
echo  ================================================================
echo.
echo   INSTALLATION COMPLETE!  Sab kuch ready hai!
echo.
echo  ================================================================
echo.
echo   APP START KARNE KE LIYE:
echo.
echo     Yeh folder kholo: "%CD%"
echo     start.bat pe DOUBLE-CLICK karo
echo.
echo   Browser mein:  http://localhost:5000
echo   Username:      admin
echo   Password:      admin123
echo.
echo   NOTE: Pehli login ke baad password badlo!
echo.
echo  ================================================================
echo.

set /p STARTNOW=  App abhi start karu? (y/n): 

if /i "%STARTNOW%"=="y" (
    echo.
    echo  Starting app... 3 second mein browser khulega
    echo  Yeh window band MAT karna!
    echo.
    timeout /t 3 /nobreak >nul
    start "" "http://localhost:5000"
    venv\Scripts\python.exe app.py
) else (
    echo.
    echo  Theek hai! Baad mein is folder ka start.bat double-click karna.
    echo.
)

pause
