```bat
@echo off
setlocal EnableDelayedExpansion

title Active IA - Analisador de Documentos
color 0A

echo ==================================================
echo    Active IA - Analisador de Documentos com IA
echo ==================================================
echo.

:: ------------------------------------------------------------
:: 1. Verificar Git
:: ------------------------------------------------------------
echo [1/7] Verificando instalacao do Git...

where git >nul 2>&1

if errorlevel 1 (
    echo       Git NAO encontrado.
    echo.
    choice /c SN /n /m "Deseja instalar o Git agora? (S/N): "

    if errorlevel 2 (
        echo       Continuando sem Git...
    ) else (
        echo       Instalando Git via winget...

        winget install --id Git.Git --silent --accept-package-agreements --accept-source-agreements

        if errorlevel 1 (
            echo.
            echo       Falha na instalacao automatica.
            echo       Instale manualmente:
            echo       https://git-scm.com
            pause
            exit /b 1
        )

        echo.
        echo       Git instalado com sucesso.
        echo       Reinicie o script.
        pause
        exit /b
    )
) else (
    echo       Git encontrado.
)

echo.

:: ------------------------------------------------------------
:: 2. Verificar Python
:: ------------------------------------------------------------
echo [2/7] Verificando instalacao do Python...

where python >nul 2>&1

if errorlevel 1 goto instalar_python

for /f "tokens=2" %%v in ('python --version 2^>^&1') do (
    set PYTHON_VER=%%v
)

echo       Python versao !PYTHON_VER! encontrado.

for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VER!") do (
    set PY_MAJ=%%a
    set PY_MIN=%%b
)

if !PY_MAJ! LSS 3 goto versao_antiga
if !PY_MAJ! EQU 3 if !PY_MIN! LSS 8 goto versao_antiga

echo       Versao do Python OK.
goto python_ok

:versao_antiga
echo.
echo       Python muito antigo.
choice /c SN /n /m "Deseja instalar Python 3.12? (S/N): "

if errorlevel 2 (
    echo       Instalacao cancelada.
    pause
    exit /b 1
)

:instalar_python
echo.
echo       Instalando Python 3.12...

winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements

if errorlevel 1 (
    echo.
    echo       Falha ao instalar Python.
    echo       Baixe manualmente:
    echo       https://python.org
    pause
    exit /b 1
)

echo.
echo       Python instalado.
echo       Reinicie o script.
pause
exit /b

:python_ok
echo.

:: ------------------------------------------------------------
:: 3. Verificar pip
:: ------------------------------------------------------------
echo [3/7] Verificando pip...

python -m pip --version >nul 2>&1

if errorlevel 1 (
    echo       Pip nao encontrado.
    echo       Instalando pip...

    python -m ensurepip --upgrade

    if errorlevel 1 (
        echo       Falha ao instalar pip.
        pause
        exit /b 1
    )
)

echo       Pip OK.
echo.

:: ------------------------------------------------------------
:: 4. Ambiente virtual
:: ------------------------------------------------------------
echo [4/7] Verificando ambiente virtual...

if not exist ".venv\" (
    echo       Criando ambiente virtual...

    python -m venv .venv

    if errorlevel 1 (
        echo       Erro ao criar ambiente virtual.
        pause
        exit /b 1
    )

    echo       Ambiente virtual criado.
) else (
    echo       Ambiente virtual encontrado.
)

echo.

:: ------------------------------------------------------------
:: 5. Ativar ambiente virtual
:: ------------------------------------------------------------
echo [5/7] Ativando ambiente virtual...

call .venv\Scripts\activate.bat

if errorlevel 1 (
    echo       Falha ao ativar ambiente virtual.
    pause
    exit /b 1
)

echo       Ambiente ativado.
echo.

:: ------------------------------------------------------------
:: 6. Instalar dependencias
:: ------------------------------------------------------------
echo [6/7] Instalando dependencias...
echo.

python -m pip install --upgrade pip

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo       Erro ao instalar dependencias.
    echo       Execute manualmente:
    echo       pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo       Dependencias OK.
echo.

:: ------------------------------------------------------------
:: 7. Arquivo .env
:: ------------------------------------------------------------
echo [7/7] Verificando .env...

if not exist ".env" (
    echo OPENAI_API_KEY=COLE_SUA_CHAVE_AQUI > .env
    echo OPENAI_MODEL=gpt-4o-mini >> .env

    echo.
    echo       Arquivo .env criado.
    echo       Edite sua chave da OpenAI antes de continuar.
    pause
) else (
    echo       Arquivo .env encontrado.
)

echo.

:: ------------------------------------------------------------
:: 8. Executar programa
:: ------------------------------------------------------------
echo ==================================================
echo  Tudo pronto! Iniciando...
echo ==================================================
echo.

python gui.py

echo.
echo ==================================================
echo  Programa encerrado.
echo ==================================================
pause

endlocal
exit /b 0
```
