# COH_Opponent_Bot

Current Version : 

![Version_v5-0k](https://github.com/XcomReborn/COH_Opponent_Bot/assets/4015491/413be163-d795-4b3c-aee0-897ba9786604)


General information and how it works:

The COH_Opponent_Bot is an application for finding and displaying in game user statistics for yourself and your opponents while playing the computer game
Company Of Heroes (COH) on the steam distribution platform for personal computers (PC). Its can run in the background and output the results while the game
is in progress to either its in-built console, a web-browser that can be stand-alone or for use as an overlay, or in a selected chat channel of the computer game streaming platform twitch.tv.

The application periodically reads the game application memory looking for the internal game replay file.

Once it finds it, it parses that information using a simple game header replay parser and gets the opponent information.

The program also contacts the relic statistic rank server via a proxy and gets data for each player including wins,losses,ranks,levels ... etc.


It is for use with COH 1 only. (And only for Windows, tested only on Windows 10) because it relies on reading windows memory.


# Usage


To execute it from source code:

Download all files in the repo then:

From the command line in the appropriate directory use. "python coh_opponent_bot.py"

Currently built with:<br>
<br>
python version 3.12.0<br>
PyInstaller version 6.7.0<br>
<br>
Python Dependencies :<br>
<br>
requests version 2.31.0<br>
mem_edit version 0.7<br>
pymem version 1.13.0<br>
<br>
These can be installed using pip <br>
<br>
"pip install pyinstaller"<br>
"pip install requests"<br>
"pip install mem_edit"<br>
"pip install pymem"<br>
<br>
On Windows you can compile a single executable using pyinstaller, the commands can be executed in the build.bat batch file.
pyinstaller has a nasty habit of producing programs that immediately get flagged as a virus by windows anti virus.
An exception must be added the the windows defender in order to use the program as an .exe or it will most likely be automatically 
quarantined by the operating system. 

# A precompiled windows 10 compatible executable can be downloaded :

HERE : https://github.com/XcomReborn/COH_Opponent_Bot/releases

To use the executable:

1. Download the zip file and decompress (unzip) it into a new folder.
1. Execute the main file (coh_opponent_bot.exe) by double clicking on the icon.
2. Check the information is correct, if not edit the fields using the buttons with your steam user name, your Steam64ID*, and location of the game.
3. Optionally enter your twitch channel in the twitch options and press the Connect button.
4. When the game is running : Any user typing "opponent" or "!opponent" or "!opp" or "opp" in chat will trigger the bot to find you opponents name, steam profile and COH stats.

See all available options in the options menu in the graphical user interface of the program.

The program allows you to add a twitch username to the bot user name field you'll also need to add an OAuth key to the bot OAuth key field.
Doing so will connect using this user name as your bot. It is ok to use the same user account as your channel user or a different one.

Get your OAuth Key from twitch at this address  : https://twitchapps.com/tmi/


IF NOT:

* Your Steam64 ID can be found by:

  1.  Open up your Steam client and choose View, then click Settings
  2.  Choose Interface and check the box that reads, "Display Steam URL address when available"
  3.  Click OK
  4.  Now click on your Steam Profile Name and select View Profile

Alternatively, visit https://steamid.co/ and enter your steam account name if your ID number doesn't show up in the steam client URL



# Twitch TV Chat Bot Commands

After connecting to your twitch channel typing:<BR>
<BR>
'opponent' or 
'!opponent' or
'!opp' or
'opp'

Will result in the bot displaying the selected statistic data in the twitch.tv chat according to the preformat options set in the 
twitch chat options menu.


# To use the overlay in OBS:

![Example5](https://github.com/XcomReborn/COH_Opponent_Bot/assets/4015491/f5d85233-3bc0-4a0f-b637-0036025211aa)

Prerequisite : https://obsproject.com/ (download from here, requires the browser plugin - default in the windows version)

![Example8](https://github.com/XcomReborn/COH_Opponent_Bot/assets/4015491/bc7ff4ed-9e33-4a84-a50e-90f0ff893aba)

![Example7](https://github.com/XcomReborn/COH_Opponent_Bot/assets/4015491/513065a3-a254-48ed-881f-a7157ebd1ff2)

1. Create a new source of type browser.   
2. Set the size of the browser to the size of your stream output (eg: 1920 width x 1080 height)
3. Tick the box for using local file.
4. Setting the use custom frame rate tick box to true (on) and entering a frame rate of 2 in the FPS field will prevent the overlay from flickering.
5. Use the file browse button to point the browser at local file overlay.html in the programs base directory. (if overlay.html doesn't exist, run the program once and press test, this will create one)
7. If the created source doesn't fill the preview screen (it should if you set the resolution correctly) expand the source to overlay/cover the entire preview screen.

![Example9](https://github.com/XcomReborn/COH_Opponent_Bot/assets/4015491/137b6a7b-d36a-4035-be73-8123b4d97827)

- The next time you get an opponent or type !opp in your connected twitch chat during a game the overlay will show the opponents.
- The overlay custom output preformat string can be set in the overlay options menu.
- The overlay can be further customized if you alter the overlay_style.css file manually.


Enjoy, 

XeReborn aka Xcom.
