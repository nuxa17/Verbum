cd -- "$(dirname "$BASH_SOURCE")"
source env/bin/activate
mkdir _pyinstaller
cd _pyinstaller
pyinstaller ../src/main.py -F -n Verbum --distpath ../Verbum \
-w -i ../res/logo.icns \
--add-data "../config/default.json:config" --add-data "../config/contractions.json:config" --add-data "../data:data" --add-data "../res:res" --add-data "../env/lib/python3.11/site-packages/textblob/en/en-entities.txt:textblob/en" --add-data ../env/lib/python3.11/site-packages/textblob/en/en-morphology.txt:textblob/en --add-data ../env/lib/python3.11/site-packages/textblob/en/en-spelling.txt:textblob/en --add-data ../env/lib/python3.11/site-packages/textblob/en/en-context.txt:textblob/en --add-data ../env/lib/python3.11/site-packages/textblob/en/en-lexicon.txt:textblob/en --add-data ../env/lib/python3.11/site-packages/textblob/en/en-sentiment.xml:textblob/en --noconfirm
cd ..
rm -r _pyinstaller