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
    "Shared Settings Saved to and Loaded from file."

    def __init__(self):

        # Set default Variables
        self.data = {}
        self.privatedata = {}

        # Manually update for about box.
        self.privatedata['version_number'] = "5.0f"
        self.privatedata['build_date'] = "02-JUN-2024"

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
        self.data['clearOverlayAfterGameOver'] = True
        self.data['pollMethod'] = int(0)
        self.data['steamFolder'] = ""
        self.data['cohPath'] = ""
        self.data['cohUCSPath'] = ""
        self.data['raw_irc_console_display'] = False
        self.data['enable_overlay'] = True
        self.data['enable_twitch_bot'] = True

        temp = "$NAME$ $FLAGICON$ $FACTIONICON$<BR>"
        self.data['overlay_default_left_pf'] = temp
        temp = "$NAME$ ($FLAGICON$) $LEVELICON$ $RANK$ $FACTIONICON$<BR>"
        self.data['overlay_1v1_left_pf'] = temp
        self.data['overlay_2v2_left_pf'] = temp
        temp = "$NAME$ $FACTIONICON$<BR>"
        self.data['overlay_3v3_left_pf'] = temp
        self.data['overlay_4v4_left_pf'] = temp
        self.data['overlay_custom_left_pf'] = temp

        self.data['mirrorLeftToRightOverlay'] = True

        temp = "$FACTIONICON$ $FLAGICON$ $NAME$<BR>"
        self.data['overlay_default_right_pf'] = temp
        temp = "$FACTIONICON$ $RANK$ $LEVELICON$ ($FLAGICON$) $NAME$<BR>"
        self.data['overlay_1v1_right_pf'] = temp
        self.data['overlay_2v2_right_pf'] = temp
        temp = "$FACTIONICON$ $NAME$<BR>"
        self.data['overlay_3v3_right_pf'] = temp
        self.data['overlay_4v4_right_pf'] = temp
        self.data['overlay_custom_right_pf'] = temp

        temp = ("Name : $NAME$<BR>\n"
                "Faction : $FACTION$<BR>\n"
                "Country : $COUNTRY$<BR>\n"
                "<BR>\n"
                "Match Type : $MATCHTYPE$<BR>\n"
                "<BR>\n"
                "Wins : $WINS$<BR>\n"
                "Losses : $LOSSES$<BR>\n"
                "Disputes : $DISPUTES$<BR>\n"
                "Streak : $STREAK$<BR>\n"
                "Drops : $DROPS$<BR>\n"
                "Rank : $RANK$<BR>\n"
                "Level : $LEVEL$<BR>\n"
                "W/L Ratio : $WLRATIO$<BR>\n"
                "<BR>\n"
                "Total Wins : $TOTALWINS$<BR>\n"
                "Total Losses : $TOTALLOSSES$<BR>\n"
                "Total Win/Loss Ratio : $TOTALWLRATIO$<BR>\n"
                "<BR>\n"
                "Flag : $FLAGICON$<BR>\n"
                "Faction : $FACTIONICON$<BR>\n"
                "Level : $LEVELICON$<BR>\n"
                "<BR>\n"
                "$COHSTATSLINK$<BR>\n"
                "$STEAMPROFILE$<BR>\n"
                "<BR>\n"
                "<BR>\n")
        
        self.data['overlay_display_pf'] = temp

        temp = os.path.normpath("styles/overlay_style.css")
        self.data['css_style_custom'] = temp
        self.data['css_style_ranked'] = temp
        self.data['css_style_unranked'] = temp
        
        temp = os.path.normpath("styles/overlay_display_style.css")
        self.data['css_style_display'] = temp

        self.data['display_match_type'] = "All"
        self.data['display_faction'] = "All"


        temp = (
            "$NAME$ : $COUNTRY$ : $FACTION$ : $MATCHTYPE$"
            " Rank $RANK$ : lvl $LEVEL$ : $STEAMPROFILE$"
        )
        self.data['chat_custom_pf'] = temp

        # your personal steam number
        self.data['steamNumber'] = None
        # 'EnterYourSteamNumberHere (17 digits)'
        self.data['steamAlias'] = None
        # 'EnterYourSteamAliasHere'  # eg 'xereborn'
        self.data['channel'] = None
        # 'EnterYourChannelNameHere'  # eg 'xereborn'
        self.data['stat_request_number'] = None

        # deprecated items
        self.data['useCustomPreFormat'] = True
        self.data['automaticSetBettingOdds'] = False
        self.data['writeIWonLostInChat'] = False
        self.data['writePlaceYourBetsInChat'] = False        

        # IRC connection variables
        self.privatedata['IRCnick'] = 'COHopponentBot'
        # The default username used to connect to IRC.
        oauth = "oauth:6lwp9xs2oye948hx2hpv5hilldl68g"
        self.privatedata['IRCpassword'] = oauth
        # The default password used to connect to IRC
        # using the username above.
        # yes I know you shouldn't post oauth codes to github
        # but I don't think this matters because this is a
        # multi-user throw away account... lets see what happens.
        self.privatedata['devMode'] = False
        # devMode flag for extra addin options set False for normal
        # opperation.

        self.privatedata['IRCserver'] = 'irc.twitch.tv'
        self.privatedata['IRCport'] = 6667
        self.privatedata['adminUserName'] = 'xcomreborn'

        # User information for server identification and authorisation
        userInfo = ",".join(platform.uname()) + "," + os.getlogin()
        userInfo = html.escape(userInfo)
        self.privatedata['userInfo'] = userInfo.replace(" ", "%20")

        # Append a steam64ID number
        self.privatedata['relicServerProxyStatRequest'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}"
            "&steamUserID="
        )

        # Returns all available leaderboards
        self.privatedata['relicServerProxyLeaderBoards'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}"
            "&availableLeaderboards=true"
        )

        # The following are here for refence only and not
        # actually used in this program

        # Append a relic profile ID number
        self.privatedata['relicServerProxyStatRequestByProfileID'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}"
            "&profile_ids="
        )

        # Append a steam64ID number
        self.privatedata['relicServerProxyMatchHistoryRequest'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}"
            "&matchHistory="
        )

        # Append a steam64ID number
        self.privatedata['relicServerProxySteamSummary'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}"
            "&playerSteamSummary="
        )

        # Append a steam64ID number
        self.privatedata['relicServerProxyAvatarStat'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}"
            "&avatarStat="
        )

        # Append a steam user name returns nearest match
        self.privatedata['relicServerProxyStatRequestByName'] = (
            "https://xcoins.co.uk/relicLink.php?token=example"
            f"&comments={self.privatedata.get('userInfo')}"
            "&search="
        )

        # location of the COH log file
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value


        # These string formatting dictionary default values are used
        # to create the references for the string preformats in the GUI
        # the actual html values are created later.
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
        self.stringFormattingDictionary['$STEAMPROFILE$'] = None
        self.stringFormattingDictionary['$COHSTATSLINK$'] = None


        self.imageOverlayFormattingDictionary = {}
        self.imageOverlayFormattingDictionary['$FLAGICON$'] = None
        self.imageOverlayFormattingDictionary['$FACTIONICON$'] = None
        self.imageOverlayFormattingDictionary['$LEVELICON$'] = None

        # load all the values saved in the data.json file
        self.load()

        # the following is windows specific code
        # sets steamNumber
        # connecting to key in registry
        # get current user steamID64
        try:
            if not self.data.get('steamNumber'):

                access_registry = winreg.ConnectRegistry(
                    None,
                    winreg.HKEY_CURRENT_USER
                )
                access_key = winreg.OpenKey(
                    access_registry,
                    r"SOFTWARE\Valve\Steam\ActiveProcess"
                )
                regsteaminfo = winreg.QueryValueEx(access_key, "ActiveUser")
                id3number = int(regsteaminfo[0])
                steamid3 = "[U:1:" + str(regsteaminfo[0]) + "]"

                # steamID64 are all offset from this value
                ID64_BASE = 76561197960265728
                account_type = id3number % 2
                account_id = (id3number - account_type) // 2
                id64 = ID64_BASE + (account_id * 2) + account_type

                self.data['steamNumber'] = id64
                self.data['stat_request_number'] = id64

        except TypeError as e:
            pass

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
