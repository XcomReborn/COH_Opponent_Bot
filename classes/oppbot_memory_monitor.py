import logging
import threading
import tkinter

from classes.oppbot_settings import Settings
from classes.oppbot_game_data import GameData
from classes.oppbot_irc_client import IRC_Client

class MemoryMonitor(threading.Thread):
    "Checks when COH1 game has started/ended."

    def __init__(
        self,
        poll_interval=10,
        settings = None,
        tkconsole : tkinter.Text = None
                ):
        threading.Thread.__init__(self)
        logging.info("Memory Monitor Started!")
        self.running = True
        
        self.settings = settings
        if not settings:
            self.settings = Settings()
        
        self.gameInProgress = False
        
        self.event = threading.Event()
        self.gameData : GameData = None
 
        try:
            self.poll_interval = int(poll_interval)
        except TypeError:
            self.poll_interval = 10

        self.irc_client : IRC_Client = None
        self.tkconsole = tkconsole

        self.replay_path = ""

    def run(self):
        try:

            self.gameData = GameData(irc_client=self.irc_client, tkconsole=self.tkconsole, settings=self.settings)

            while self.running:
                # Reference to irc client
                # may not exist when first started
                self.gameData.irc_client = self.irc_client
                self.gameData.get_data_from_game()
                if self.gameData.gameInProgress:
                    # COH_REC exists game running
                    if ((self.gameData.gameInProgress != self.gameInProgress) or
                        (self.replay_path != self.gameData.replay_full_path)):
                        # coh wasn't running and now it is (game started)
                        self.game_started()

                else:
                    # COH_REC doesn't exists game not running
                    if self.gameData.gameInProgress != self.gameInProgress:
                        # coh was running and now its not (game over)
                        self.game_over()
                self.gameInProgress = self.gameData.gameInProgress
                # set local gameInProgress flag to it can be compared with
                # any changes to it in the next loop
                self.event.wait(self.poll_interval)
        except Exception as e:
            logging.error("In FileMonitor run")
            logging.error(str(e))
            logging.exception("Exception : ")
        logging.info("Memory Monitor Exiting Main Loop!")

    def game_started(self):

        # legacy posting of data to opponent bot channel
        self.gameData.output_opponent_data()
        # enable to output to the opponent bot channel
        self.post_steam_number()
        # enable to output to the opponent bot channel
        self.post_data()
        # if a replay
        if self.gameData.is_replay:
            self.replay_path = self.gameData.replay_full_path

    def post_steam_number(self):
        try:
            if self.irc_client:
                channel = str(self.settings.data.get('channel'))
                steamNumber = str(self.settings.data.get('steamNumber'))
                message = f"!setsteam,{channel},{steamNumber}"
                self.irc_client.send_message_to_opponentbot_channel(message)
        except Exception as e:
            logging.error("Problem in PostSteamNumber")
            logging.exception("Exception : ")
            logging.error(str(e))

    def post_data(self):
        # Sending to cohopponentbot channel about game,
        # this requires parsing mapName First
        if self.irc_client:
            message = self.gameData.get_game_description_string()
            if message:
                self.irc_client.send_message_to_opponentbot_channel(message)

    def game_over(self):
        try:
            # Clear the overlay
            if (self.settings.data.get('clearOverlayAfterGameOver')):
                if self.gameData:
                    self.gameData.clear_overlay_HTML()
        except Exception as e:
            logging.info("Problem in GameOver")
            logging.error(str(e))
            logging.exception("Exception : ")

    def close(self):
        logging.info("Memory Monitor Closing!")
        self.running = False
        # break out of loops if waiting
        if self.event:
            self.event.set()


    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""
