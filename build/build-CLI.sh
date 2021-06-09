pathtospec="../src/superscript.spec"
pathtodist="../dist/"
pathtowork="temp/"

pyinstaller --onefile --clean --distpath ${pathtodist} --workpath ${pathtowork} ${pathtospec}