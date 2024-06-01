import logging

from classes.oppbot_game_data import GameData
from classes.oppbot_gui_main_window import GUIMainWindow

# Program Entry Starts here
# Default error logging log file location:
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    format='%(asctime)s (%(threadName)-10s) [%(levelname)s] %(message)s',
    filename='COH_Opponent_Bot.log',
    filemode="w",
    level=logging.INFO)

GameData.clear_overlay_HTML()

main = GUIMainWindow()
