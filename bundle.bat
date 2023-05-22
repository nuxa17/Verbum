@echo off

call env\Scripts\activate
md Verbum
md _pyinstaller
cd _pyinstaller
START /wait pyinstaller ../src/main.py -F -n Verbum -w --distpath ../Verbum -i ../res/logo.ico --splash ../res/splash.png ^
--add-data "../config/default.json;config" --add-data "../config/contractions.json;config" --add-data "../res;res" ^
--add-data "../data;data" ^
--add-data ../env/Lib/site-packages/textblob/en/en-entities.txt;textblob/en ^
--add-data ../env/Lib/site-packages/textblob/en/en-morphology.txt;textblob/en ^
--add-data ../env/Lib/site-packages/textblob/en/en-spelling.txt;textblob/en ^
--add-data ../env/Lib/site-packages/textblob/en/en-context.txt;textblob/en ^
--add-data ../env/Lib/site-packages/textblob/en/en-lexicon.txt;textblob/en ^
--add-data ../env/Lib/site-packages/textblob/en/en-sentiment.xml;textblob/en
cd ..
rd /s /q _pyinstaller
deactivate