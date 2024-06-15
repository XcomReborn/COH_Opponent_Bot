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

        self.event = threading.Event()
        self.gameData : GameData = None
 
        try:
            self.poll_interval = int(poll_interval)
        except TypeError:
            self.poll_interval = 10

        self.irc_client : IRC_Client = None
        self.tkconsole = tkconsole

        # for checking if game has changed
        self.game_in_progress = False


    def run(self):
        try:

            self.gameData = GameData(irc_client=self.irc_client, tkconsole=self.tkconsole, settings=self.settings)

            while self.running:
                # Reference to irc client
                # may not exist when first started
                self.gameData.irc_client = self.irc_client
                self.gameData.get_data_from_game()
                if self.gameData.game_in_progress:
                    # game is in progress
                    if self.game_in_progress != self.gameData.game_in_progress:
                        # the state has changed (game started)
                        # set the local state to the game state
                        self.game_in_progress = self.gameData.game_in_progress
                        # do game started method
                        self.game_started()
                else:
                    # game is not in progress
                    if self.game_in_progress != self.gameData.game_in_progress:
                        # the state has changed (game over)
                        # set the local state to the game state
                        self.game_in_progress = self.gameData.game_in_progress        
                        # do game over method                
                        self.game_over()

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
