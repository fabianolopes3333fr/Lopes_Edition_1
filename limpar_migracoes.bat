@echo off
chcp 65001 > nul
color 0A

echo ================================================================================
echo LIMPEZA COMPLETA DE MIGRAÇÕES - DJANGO PROJECT
echo ================================================================================
echo.

echo ⚠️  ATENÇÃO: Esta ação irá:
echo   • Deletar TODAS as migrações de todos os apps
echo   • Deletar o banco de dados db.sqlite3
echo   • Deletar arquivos __pycache__ das migrações
echo.

set /p confirma="Deseja continuar? Digite SIM para confirmar: "
if /i not "%confirma%"=="SIM" (
    echo.
    echo ✗ Operação cancelada
    pause
    exit /b
)

echo.
echo ================================================================================
echo INICIANDO LIMPEZA...
echo ================================================================================
echo.

REM Deletar migrações de cada app
echo 🔧 Deletando migrações do app ACCOUNTS...
if exist accounts\migrations (
    for %%f in (accounts\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul && echo   ✓ Deletado: %%~nxf
        )
    )
    if exist accounts\migrations\__pycache__ (
        rmdir /s /q accounts\migrations\__pycache__ 2>nul
        echo   ✓ Deletado: __pycache__
    )
)

echo.
echo 🔧 Deletando migrações do app BLOG...
if exist blog\migrations (
    for %%f in (blog\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul && echo   ✓ Deletado: %%~nxf
        )
    )
    if exist blog\migrations\__pycache__ (
        rmdir /s /q blog\migrations\__pycache__ 2>nul
        echo   ✓ Deletado: __pycache__
    )
)

echo.
echo 🔧 Deletando migrações do app CLIENTES...
if exist clientes\migrations (
    for %%f in (clientes\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul && echo   ✓ Deletado: %%~nxf
        )
    )
    if exist clientes\migrations\__pycache__ (
        rmdir /s /q clientes\migrations\__pycache__ 2>nul
        echo   ✓ Deletado: __pycache__
    )
)

echo.
echo 🔧 Deletando migrações do app CONTATO...
if exist contato\migrations (
    for %%f in (contato\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul && echo   ✓ Deletado: %%~nxf
        )
    )
    if exist contato\migrations\__pycache__ (
        rmdir /s /q contato\migrations\__pycache__ 2>nul
        echo   ✓ Deletado: __pycache__
    )
)

echo.
echo 🔧 Deletando migrações do app HOME...
if exist home\migrations (
    for %%f in (home\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul && echo   ✓ Deletado: %%~nxf
        )
    )
    if exist home\migrations\__pycache__ (
        rmdir /s /q home\migrations\__pycache__ 2>nul
        echo   ✓ Deletado: __pycache__
    )
)

echo.
echo 🔧 Deletando migrações do app ORCAMENTOS...
if exist orcamentos\migrations (
    for %%f in (orcamentos\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul && echo   ✓ Deletado: %%~nxf
        )
    )
    if exist orcamentos\migrations\__pycache__ (
        rmdir /s /q orcamentos\migrations\__pycache__ 2>nul
        echo   ✓ Deletado: __pycache__
    )
)

echo.
echo 🔧 Deletando migrações do app PROFILES...
if exist profiles\migrations (
    for %%f in (profiles\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul && echo   ✓ Deletado: %%~nxf
        )
    )
    if exist profiles\migrations\__pycache__ (
        rmdir /s /q profiles\migrations\__pycache__ 2>nul
        echo   ✓ Deletado: __pycache__
    )
)

echo.
echo 🔧 Deletando migrações do app PROJETOS...
if exist projetos\migrations (
    for %%f in (projetos\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul && echo   ✓ Deletado: %%~nxf
        )
    )
    if exist projetos\migrations\__pycache__ (
        rmdir /s /q projetos\migrations\__pycache__ 2>nul
        echo   ✓ Deletado: __pycache__
    )
)

echo.
echo 🗄️  Deletando banco de dados...
if exist db.sqlite3 (
    del db.sqlite3 2>nul && echo   ✓ Banco de dados deletado
) else (
    echo   ℹ Banco de dados não encontrado
)

echo.
echo ================================================================================
echo ✓ LIMPEZA CONCLUÍDA!
echo ================================================================================
echo.
echo 📝 PRÓXIMOS PASSOS:
echo.
echo 1. Criar novas migrações:
echo    python manage.py makemigrations
echo.
echo 2. Aplicar migrações:
echo    python manage.py migrate
echo.
echo 3. Criar superusuário:
echo    python manage.py createsuperuser
echo.
echo ================================================================================
echo.

set /p executar="Deseja executar os comandos agora? (S/N): "
if /i "%executar%"=="S" (
    echo.
    echo 📦 Criando migrações...
    python manage.py makemigrations

    echo.
    echo 📦 Aplicando migrações...
    python manage.py migrate

    echo.
    echo 👤 Criar superusuário...
    python manage.py createsuperuser

    echo.
    echo ✓ Processo concluído!
)

echo.
pause

