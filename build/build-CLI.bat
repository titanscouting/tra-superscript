set pathtospec="../src/cli/superscript.spec"
set pathtodist="../dist/"
set pathtowork="temp/"

pyinstaller --clean --distpath %pathtodist% --workpath %pathtowork% %pathtospec%