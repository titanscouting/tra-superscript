set pathtospec="superscript.spec"
set pathtodist="../dist/"
set pathtowork="temp/"

pyinstaller --clean --distpath %pathtodist% --workpath %pathtowork% %pathtospec%