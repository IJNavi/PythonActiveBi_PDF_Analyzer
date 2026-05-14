@echo off
echo ========================================
echo Criando executavel do Analisador de PDF
echo ========================================
echo.

echo Instalando PyInstaller...
pip install pyinstaller

echo.
echo Criando executavel...
pyinstaller --onefile --windowed --name "ActiveIA" gui.py

echo.
echo ========================================
echo Executavel criado na pasta "dist"
echo Arquivo: ActiveIA.exe
echo ========================================
pause