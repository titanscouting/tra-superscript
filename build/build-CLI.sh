pathtospec="superscript.spec"
pathtodist="../dist/"
pathtowork="temp/"

pyinstaller --clean --distpath ${pathtodist} --workpath ${pathtowork} ${pathtospec}