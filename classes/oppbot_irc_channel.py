import threading
import logging
import re

from queue import Queue
from socket import socket
from threading import Thread
from tkinter import END

from classes.oppbot_settings import Settings
from classes.oppbot_game_data import GameData


class IRC_Channel(threading.Thread):
    "Implements an IRC Channel Connection. Checks User Commands."

    def __init__(
        self,
        irc_client,
        irc_socket: socket,
        queue : Queue,
        channel,
        settings=None
            ):
        Thread.__init__(self)
        self.irc_client = irc_client
        self.running = True
        self.irc_socket = irc_socket
        self.queue = queue
        self.channel = channel

        self.settings = settings
        if not settings:
            self.settings = Settings()

        self.game_data = GameData(self.irc_client, settings=self.settings)

    def run(self):
        self.irc_socket.send(('JOIN ' + self.channel + '\r\n').encode("utf8"))
        while self.running:
            line = self.queue.get()
            line = str.rstrip(line)
            line = str.split(line)
            if (line[0] == "EXITTHREAD"):
                self.close()
            if (line[0] == "OPPONENT"):
                self.check_for_user_command("self", "opp")
            if (line[0] == "TEST"):
                self.test_output()
            if (line[0] == "IWON"):
                self.irc_client.send_private_message_to_IRC("!i won")
            if (line[0] == "ILOST"):
                self.irc_client.send_private_message_to_IRC("!i lost")
            if (line[0] == "CLEAROVERLAY"):
                GameData.clear_overlay_HTML()
            if (
                len(line) >= 4
                and "PRIVMSG" == line[2]
                and "jtv" not in line[0]
            ):
                # call function to handle user message
                self.user_message(line)

    def user_message(self, line):
        "Processes IRC returned raw string data."

        # Dissect out the useful parts of the raw data line
        # into username and message and remove certain characters
        msgFirst = line[1]
        msgUserName = msgFirst[1:]
        msgUserName = msgUserName.split("!")[0]
        # msgType = line [1];
        # msgChannel = line [3]
        msgMessage = " ".join(line[4:])
        msgMessage = msgMessage[1:]
        messageString = str(msgUserName) + " : " + str(msgMessage)
        logging.info(str(messageString).encode('utf8'))

        # Check for UserCommands
        self.check_for_user_command(msgUserName, msgMessage)

        if (
            msgMessage == "exit"
            and msgUserName == self.irc_client.adminUserName
        ):
            self.irc_client.send_private_message_to_IRC("Exiting")
            self.close()

    def check_for_user_command(self, userName, message):
        "Performs string comparisons for hardcoded commands."

        logging.info("Checking For User Comamnd")
        try:
            if (
                bool(re.match(r"^(!)?opponent(\?)?$", message.lower()))
                or bool(re.match(r"^(!)?place your bets$", message.lower()))
                or bool(re.match(r"^(!)?opp(\?)?$", message.lower()))
                    ):

                self.game_data = GameData(
                    irc_client=self.irc_client,
                    settings=self.settings
                )
                if self.game_data.get_data_from_game():
                    self.game_data.output_opponent_data()
                else:
                    self.irc_client.send_private_message_to_IRC(
                        "Can't find the opponent right now."
                    )

            user = str(userName).lower()
            admin = str(self.settings.privatedata.get('adminUserName'))
            channel = str(self.settings.data.get('channel'))
            if (
                message.lower() == "test"
                and (
                    user == admin.lower()
                    or user == channel.lower())
                    ):
                self.irc_client.send_private_message_to_IRC(
                    "I'm here! Pls give me mod to prevent twitch"
                    " from autobanning me for spam if I have to send"
                    " a few messages quickly."
                )
                self.irc_client.output.insert(
                    END,
                    f"Oh hi again, I heard you in the {self.channel[1:]}"
                    " channel.\n"
                )

            if (bool(re.match(r"^(!)?gameinfo(\?)?$", message.lower()))):
                self.game_info()

            if (bool(re.match(r"^(!)?story(\?)?$", message.lower()))):
                self.story()

            if (bool(re.match(r"^(!)?debug(\?)?$", message.lower()))):
                self.print_info_to_debug()

        except Exception as e:
            logging.error("Problem in CheckForUserCommand")
            logging.error(str(e))
            logging.exception("Exception : ")

    def print_info_to_debug(self):
        "Outputs gameData to the log file."

        try:
            self.game_data = GameData(
                self.irc_client,
                settings=self.settings
            )
            self.game_data.get_data_from_game()
            self.game_data.get_mapDescriptionFull_from_UCS_file()
            self.game_data.get_mapNameFull_from_UCS_file()
            logging.info(self.game_data)
            self.irc_client.send_private_message_to_IRC(
                "GameData saved to log file."
            )
        except Exception as e:
            logging.error("Problem in PrintInfoToDebug")
            logging.error(str(e))
            logging.exception("Exception : ")

    def game_info(self):
        "Outputs a summary of the current game to IRC."

        self.game_data = GameData(self.irc_client, settings=self.settings)
        if self.game_data.get_data_from_game():
            self.irc_client.send_private_message_to_IRC(
                f"Map : {self.game_data.mapNameFull},"
                f" High Resources : {self.game_data.highResources},"
                f" Automatch : {self.game_data.automatch},"
                f" Slots : {self.game_data.slots},"
                f" Players : {self.game_data.numberOfPlayers}."
            )

    def story(self):
        "Outputs the game description to IRC."

        self.game_data = GameData(self.irc_client, settings=self.settings)
        logging.info(str(self.game_data))
        if self.game_data.get_data_from_game():
            logging.info(str(self.game_data))
            # Requires parsing the map description from
            # the UCS file this takes time so must be done first
            self.game_data.get_mapDescriptionFull_from_UCS_file()
            self.irc_client.send_private_message_to_IRC(
                "{}.".format(self.game_data.mapDescriptionFull))

    def test_output(self):
        "Outputs information general on pressing test button."

        if not self.game_data:
            self.game_data = GameData(
                self.irc_client,
                settings=self.settings
            )
            self.game_data.get_data_from_game()
        self.game_data.test_output()

    def close(self):
        "Closes the IRC channel."

        self.running = False
        logging.info("Closing Channel " + str(self.channel) + " thread.")
