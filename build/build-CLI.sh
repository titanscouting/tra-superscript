pathtospec="../src/cli/superscript.spec"
pathtodist="../dist/"
pathtowork="temp/"

pyinstaller --onefile --clean --distpath ${pathtodist} --workpath ${pathtowork} ${pathtospec}