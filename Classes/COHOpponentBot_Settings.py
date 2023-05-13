import logging
import json  # for loading and saving data to a convenient json file
import os.path
import ssl  # required for urllib certificates
import urllib.request  # more for loadings jsons from urls
import winreg  # to get steamlocation automatically
import platform
import html
import ctypes.wintypes

# for finding the windows home directory will throw error on linux


class Settings:
    """Shared Settings Saved to and Loaded from file."""

    def __init__(self):

        # Set default Variables
        self.data = {}
        self.privatedata = {}

        # IRC connection variables
        self.privatedata['IRCnick'] = 'COHopponentBot'
        # The default username used to connect to IRC.
        oauth = "oauth:6lwp9xs2oye948hx2hpv5hilldl68g"
        self.privatedata['IRCpassword'] = oauth
        # The default password used to connect to IRC
        # using the username above.
        # yes I know you shouldn't post oauth codes to github
        # but I don't think this matter because this is a
        # multi-user throw away account... lets see what happens.
        self.privatedata['IRCserver'] = 'irc.chat.twitch.tv'
        self.privatedata['IRCport'] = 80
        self.privatedata['adminUserName'] = 'xcomreborn'

        # User information for server identification and authorisation
        userInfo = ",".join(platform.uname()) + "," + os.getlogin()
        userInfo = html.escape(userInfo)
        self.privatedata['userInfo'] = userInfo.replace(" ", "%20")

        # Append a steam64ID number
        self.privatedata['relicServerProxyStatRequest'] = (
            "https://xcoins.co.uk/relicLink.php?token=example&"
            f"comments={self.privatedata.get('userInfo')}&"
            "steamUserID="
        )

        # Append a relic profile ID number
        self.privatedata['relicServerProxyStatRequestByProfileID'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}&"
            "profile_ids="
        )

        # Append a steam64ID number
        self.privatedata['relicServerProxyMatchHistoryRequest'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}&"
            "matchHistory="
        )

        # Returns all available leaderboards
        self.privatedata['relicServerProxyLeaderBoards'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}&"
            "availableLeaderboards=true"
        )

        # Append a steam64ID number
        self.privatedata['relicServerProxySteamSummary'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}&"
            "playerSteamSummary="
        )

        # Append a steam64ID number
        self.privatedata['relicServerProxyAvatarStat'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}&"
            "avatarStat="
        )

        # Append a steam user name returns nearest match
        self.privatedata['relicServerProxyStatRequestByName'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}&"
            "search="
        )

        # custom display toggles
        # what to show in stat string constuct

        self.data['botUserName'] = ""
        self.data['botOAuthKey'] = ""
        self.data['whisperTo'] = "xcoinbetbot"
        self.data['showOwn'] = False
        self.data['logErrorsToFile'] = True
        self.data['filePollInterval'] = 10
        self.data['showSteamProfile'] = False
        self.data['automaticTrigger'] = True
        self.data['automaticSetBettingOdds'] = False
        self.data['writeIWonLostInChat'] = False
        self.data['writePlaceYourBetsInChat'] = False
        self.data['clearOverlayAfterGameOver'] = True
        self.data['logPath'] = ""
        self.data['temprecReplayPath'] = ""
        self.data['steamFolder'] = ""
        self.data['cohPath'] = ""
        self.data['cohUCSPath'] = ""
        self.data['useOverlayPreFormat'] = True
        temp = "$NAME$ ($FLAGICON$) $LEVELICON$ $RANK$ $FACTIONICON$"
        self.data['overlayStringPreFormatLeft'] = temp
        self.data['mirrorLeftToRightOverlay'] = True
        temp = "$FACTIONICON$ $RANK$ $LEVELICON$ ($FLAGICON$) $NAME$"
        self.data['overlayStringPreFormatRight'] = temp
        self.data['overlayStyleCSSFilePath'] = os.path.normpath(
            "Styles/OverlayStyle.css")

        self.data['useCustomPreFormat'] = True
        temp = (
            "$NAME$ : $COUNTRY$ : $FACTION$ : $MATCHTYPE$"
            " Rank $RANK$ : lvl $LEVEL$ : $STEAMPROFILE$"
        )
        self.data['customStringPreFormat'] = temp

        # your personal steam number
        self.data['steamNumber'] = None
        # 'EnterYourSteamNumberHere (17 digits)'
        self.data['steamAlias'] = None
        # 'EnterYourSteamAliasHere'  # eg 'xereborn'
        self.data['channel'] = None
        # 'EnterYourChannelNameHere'  # eg 'xereborn'

        # location of the COH log file
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value

        self.stringFormattingDictionary = {}
        self.stringFormattingDictionary['$NAME$'] = None
        self.stringFormattingDictionary['$FACTION$'] = None
        self.stringFormattingDictionary['$COUNTRY$'] = None
        self.stringFormattingDictionary['$TOTALWINS$'] = None
        self.stringFormattingDictionary['$TOTALLOSSES$'] = None
        self.stringFormattingDictionary['$TOTALWLRATIO$'] = None

        self.stringFormattingDictionary['$WINS$'] = None
        self.stringFormattingDictionary['$LOSSES$'] = None
        self.stringFormattingDictionary['$DISPUTES$'] = None
        self.stringFormattingDictionary['$STREAK$'] = None
        self.stringFormattingDictionary['$DROPS$'] = None
        self.stringFormattingDictionary['$RANK$'] = None
        self.stringFormattingDictionary['$LEVEL$'] = None
        self.stringFormattingDictionary['$WLRATIO$'] = None

        self.stringFormattingDictionary['$MATCHTYPE$'] = None
        self.stringFormattingDictionary['$COHSTATSLINK$'] = None
        self.stringFormattingDictionary['$STEAMPROFILE$'] = None

        self.imageOverlayFormattingDictionary = {}
        self.imageOverlayFormattingDictionary['$FLAGICON$'] = None
        self.imageOverlayFormattingDictionary['$FACTIONICON$'] = None
        self.imageOverlayFormattingDictionary['$LEVELICON$'] = None

        # load all the values saved in the data.json file
        self.load()

        # the following is windows specific code
        # using ctypes.win will not compile on linux
        # sets logpath from my documents folder location
        # sets steamNumber

        if (not self.data.get('logPath')):
            try:
                buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                ctypes.windll.shell32.SHGetFolderPathW(
                    None,
                    CSIDL_PERSONAL,
                    None,
                    SHGFP_TYPE_CURRENT,
                    buf
                )

                loc = "\\My Games\\Company of Heroes Relaunch\\warnings.log"
                logPath = buf.value + loc
                self.data['logPath'] = logPath
            except Exception as e:
                logging.error(str(e))
                logging.exception("Exception : ")

        if not self.data.get('steamNumber'):
            # attempt to extract users steamNumber from logfile
            if (os.path.isfile(logPath)):
                logging.info("the logPath file was found")
                try:
                    with open(
                        self.data['logPath'],
                        encoding='ISO-8859-1'
                    ) as file:
                        content = file.readlines()
                    for item in content:
                        if ("RLINK -- Found profile:") in item:
                            steamNumber = self.find_between(
                                item,
                                "steam/",
                                "\n"
                            )
                            self.data['steamNumber'] = steamNumber
                            # print("SteamNumber : " + str(steamNumber))
                except Exception as e:
                    logging.error(str(e))
                    logging.exception("Exception : ")

        # Set the location of cohPath from all steam folder installations
        # Set cohPath
        # Set cohUCSPath
        # Set steamFolder
        if (not self.data.get('cohPath')) or (not self.data.get('cohUCSPath')):
            # connecting to key in registry
            try:
                # 64 bit windows
                access_registry = winreg.ConnectRegistry(
                    None,
                    winreg.HKEY_LOCAL_MACHINE
                )
                access_key = winreg.OpenKey(
                    access_registry,
                    r"SOFTWARE\WOW6432Node\Valve\Steam"
                )
                steam_path = winreg.QueryValueEx(access_key, "InstallPath")
                if steam_path:
                    self.data['steamFolder'] = steam_path[0]
            except Exception as e:
                if e:
                    pass
            try:
                # 32 bit windows
                access_registry = winreg.ConnectRegistry(
                    None,
                    winreg.HKEY_LOCAL_MACHINE
                )
                access_key = winreg.OpenKey(
                    access_registry,
                    r"SOFTWARE\Valve\Steam"
                )
                steam_path = winreg.QueryValueEx(access_key, "InstallPath")
                if steam_path:
                    self.data['steamFolder'] = steam_path[0]
            except Exception as e:
                if e:
                    pass

            libraryFolder = "\\steamapps\\libraryfolders.vdf"
            filePath = self.data.get('steamFolder') + libraryFolder
            # print(filePath)
            steamlibraryBases = []

            if self.data.get('steamFolder'):
                steamlibraryBases.append(self.data['steamFolder'])

            # Get all steam library install locations
            try:
                if (os.path.isfile(filePath)):
                    with open(filePath) as f:
                        for line in f:
                            words = line.split()
                            try:
                                if "path" in line:
                                    location = " ".join(words[1:]).replace(
                                        '"',
                                        ""
                                    )
                                    steamlibraryBases.append(location)
                            except Exception as e:
                                logging.error(str(e))

                # Assign check each library install file
                # for the location of cohPath
                for steamBase in steamlibraryBases:
                    # print(steamBase)
                    gameLoc = (
                        "\\steamapps\\common\\Company of Heroes Relaunch"
                        "\\RelicCOH.exe"
                    )
                    cohPath = steamBase + gameLoc
                    if (os.path.isfile(cohPath)):
                        self.data['cohPath'] = cohPath
                        langUCS = (
                            "\\steamapps\\common\\Company of Heroes"
                            " Relaunch\\CoH\\Engine\\Locale\\English"
                            "\\RelicCOH.English.ucs"
                        )
                        ucsPath = steamBase + langUCS
                        if (os.path.isfile(ucsPath)):
                            self.data['cohUCSPath'] = ucsPath
                            logging.info(f"ucsPath {ucsPath}")

            except Exception as e:
                logging.error("Problem in load")
                logging.error(str(e))
                logging.exception("Exception : ")

        if not self.data.get('temprecReplayPath'):
            logPath = self.data.get('logPath')
            if logPath and isinstance(logPath, str):
                self.data['temprecReplayPath'] = logPath.replace(
                    "warnings.log",
                    "playback\\temp.rec"
                )

        if (
            not self.data.get('channel')
            and not self.data.get('alias')
        ):
            # Set channel
            # Set steamAlias
            # attempt to get userName from steamNumber
            try:
                statString = "/steam/" + str(self.data['steamNumber'])
                if (
                    not os.environ.get('PYTHONHTTPSVERIFY', '')
                    and getattr(ssl, '_create_unverified_context', None)
                ):
                    context = ssl._create_unverified_context
                    ssl._create_default_https_context = context
                # ensure steam64Number is valid
                # check stat number is 17 digit and can be converted
                # to int if not int
                steam64ID = str(self.data['steamNumber'])
                stringLength = len(steam64ID)
                assert(stringLength == 17)
                assert(int(steam64ID))

                response = urllib.request.urlopen(
                    str(self.privatedata.get('relicServerProxyStatRequest'))
                    + str(self.data['steamNumber'])
                ).read()
                statdata = json.loads(response.decode('utf-8'))
                # print(statdata)
                if (statdata['result']['message'] == "SUCCESS"):
                    logging.info("statdata load succeeded")
                    if statdata['statGroups'][0]['members'][0]['alias']:
                        for item in statdata['statGroups']:
                            for value in item['members']:
                                if (value['name'] == statString):
                                    self.data['channel'] = value['alias']
                                    self.data['steamAlias'] = value['alias']
            except Exception as e:
                logging.error(str(e))
                logging.exception("Exception : ")

    def load(self, filePath="data.json"):
        try:
            if (os.path.isfile(filePath)):
                with open(filePath) as json_file:
                    data = json.load(json_file)
                    success = self.check_data_integrity(data)
                    if success:
                        self.data = data
                        logging.info("data loaded sucessfully")
                        return True
                    else:
                        logging.info("data not loaded")
                        return False
        except Exception as e:
            logging.error("Problem in load")
            logging.error(str(e))
            logging.exception("Exception : ")

    def check_data_integrity(self, data):
        success = True
        for key, value in data.items():
            if key not in self.data:
                logging.error(f"Key missing from data.json {str(key)}")
                success = False
                break
        return success

    def save(self, filePath="data.json"):
        try:
            with open(filePath, 'w') as outfile:
                json.dump(self.data, outfile)
        except Exception as e:
            logging.error("Problem in save")
            logging.error(str(e))
            logging.exception("Exception : ")

    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""
