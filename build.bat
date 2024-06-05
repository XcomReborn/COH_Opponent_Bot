REM This script requires pyinstaller and winrar to create an executable and compress it.
REM python version used 3.12.0
REM pyinstall version 6.7.0
REM installed using "pip install pyinstaller"
REM winrar version 7.01 - trial version
REM the exe file produced by PyInstaller is often flagged as a virus this is a false positive.

py -m PyInstaller --clean --onefile --windowed --icon=icons/coh.ico coh_opponent_bot.py
IF EXIST dist\coh_opponent_bot.zip DEL /F dist\coh_opponent_bot.zip
winrar a -ep -afzip dist\coh_opponent_bot dist\coh_opponent_bot.exe
winrar a -ep -afzip dist\coh_opponent_bot overlay.html 
winrar a -r -afzip dist\coh_opponent_bot overlay_images\*.png styles\overlay_style.css styles\overlay_display_style.css
del dist\coh_opponent_bot.exe
pause 