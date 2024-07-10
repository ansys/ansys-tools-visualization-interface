@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
if "%SPHINXOPTS%" == "" (
	set SPHINXOPTS=-j auto -W --color
)
set SOURCEDIR=source
set APIDIR=api
set EXAMPLESDIR=examples
set BUILDDIR=_build

if "%1" == "" goto help
if "%1" == "clean" goto clean
if "%1" == "pdf" goto pdf
if "%1" == "html" goto html


REM Check if vtk is installed - if so, uninstall and install vtk-osmesa
set IS_VTK_INSTALLED=0
pip show vtk >NUL 2>NUL
if %ERRORLEVEL% EQU 0 (
	set IS_VTK_INSTALLED=1
	echo Uninstalling vtk...
	pip uninstall -y vtk
)
if %IS_VTK_INSTALLED% EQU 1 (
	echo Installing vtk-osmesa...
	pip install --extra-index-url https://wheels.vtk.org vtk-osmesa==9.3.0
)


%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.http://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:html
%SPHINXBUILD% -M html %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:pdf
%SPHINXBUILD% -M latex %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
cd "%BUILDDIR%\latex"
for %%f in (*.tex) do (
pdflatex "%%f" --interaction=nonstopmode)
if NOT EXIST ansys-tools-visualization-interface.pdf (
	Echo "no pdf generated!"
	exit /b 1)
Echo "pdf generated!"
goto end

:clean
rmdir /s /q %BUILDDIR% > /NUL 2>&1
for /d /r %SOURCEDIR% %%d in (%APIDIR%, %EXAMPLESDIR%) do @if exist "%%d" rmdir /s /q "%%d"
goto end

:end
popd
