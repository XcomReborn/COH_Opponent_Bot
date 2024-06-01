import socket
import sys
import collections  # for deque
import os  # to allow directory exists checking etc.
import os.path
import threading
import logging
from tkinter import END
from queue import Queue

# import all settings from settings file
from classes.oppbot_settings import Settings
from classes.oppbot_irc_channel import IRC_Channel

# Here are the message lines held until sent
messageDeque = collections.deque()
toSend = False


class IRC_Client(threading.Thread):
    "IRC Chat Client Maintains Socket and Message Send Buffer."

    def __init__(self, output = None):

        threading.Thread.__init__(self)

        self.output = output

        self.settings = Settings()
        self.settings.load()

        self.adminUserName = self.settings.privatedata.get('adminUserName')
        # This username will be able to use admin commands
        # exit the program and bypass some limits.

        # use botusername or get default if not set
        if (self.settings.data.get('botUserName') == ""):
            self.nick = self.settings.privatedata.get('IRCnick')
            # This value is the username used to connect to IRC
            # eg: "xcomreborn".
        else:
            self.nick = self.settings.data.get('botUserName')

        self.channel = "#" + self.settings.data.get('channel').lower()
        # The channel name for your channel eg: "#xcomreborn".

        # use botoauthkey or get default if not set
        if (self.settings.data.get('botOAuthKey') == ""):
            self.password = self.settings.privatedata.get('IRCpassword')
        else:
            self.password = self.settings.data.get('botOAuthKey')

        self.server = self.settings.privatedata.get('IRCserver')
        self.port = self.settings.privatedata.get('IRCport')
        rsp = self.settings.privatedata.get('relicServerProxy')
        self.relicServerProxy = rsp

        # create IRC socket
        try:
            self.ircSocket = socket.socket()
        except Exception as e:
            logging.error("A problem occurred trying to connect")
            logging.error("In IRCClient")
            logging.error(str(e))
            logging.exception("Exception : ")
            self.ircSocket.close()
            sys.exit(0)

        # irc send message buffer
        self.ircMessageBuffer = collections.deque()
        self.messageBufferTimer = None

        self.running = True

        # Start checking send buffer every 3 seconds.

        self.check_IRC_send_buffer_every_three_seconds()
        # only call this once.

        try:
            self.ircSocket.connect((self.server, self.port))
        except Exception as e:
            logging.error("A problem occurred trying to connect")
            logging.error("In IRCClient")
            logging.error(str(e))
            logging.exception("Exception : ")
            self.ircSocket.close()
            sys.exit(0)

        # sends variables for connection to twitch chat
        self.ircSocket.send(('PASS ' + self.password + '\r\n').encode("utf8"))
        self.ircSocket.send(('USER ' + self.nick + '\r\n').encode("utf8"))
        self.ircSocket.send(('NICK ' + self.nick + '\r\n').encode("utf8"))
        self.ircSocket.send(
            ('CAP REQ :twitch.tv/membership' + '\r\n').encode("utf8"))
        # sends a twitch specific request
        # necessary to recieve mode messages
        self.ircSocket.send(
            ('CAP REQ :twitch.tv/tags' + '\r\n').encode("utf8"))
        # sends a twitch specific request for extra data
        # contained in the PRIVMSG changes the way it is parsed
        self.ircSocket.send(
            ('CAP REQ :twitch.tv/commands' + '\r\n').encode("utf8"))

        # start sub thread that uses shared Queue to communicate
        # pass it irc for messaging, channel to join and queue
        self.queue = Queue()
        self.channelThread = IRC_Channel(
            self,
            self.ircSocket,
            self.queue,
            self.channel,
            settings=self.settings
        )
        self.channelThread.start()

    def run(self):
        self.running = True
        timeoutTimer = threading.Timer(5, self.connection_timedout)
        timeoutTimer.start()
        # create readbuffer to hold strings from IRC
        readbuffer = ""
        self.ircSocket.setblocking(0)

        # This is the main loop
        while self.running:
            try:
                # maintain non blocking recieve buffer from IRC
                readbuffer = readbuffer+self.ircSocket.recv(
                    1024).decode("utf-8")
                temp = str.split(readbuffer, "\n")
                readbuffer = temp.pop()
                for line in temp:
                    self.queue.put(line)
                    # send copy of recieved line to channel thread
                    line = str.rstrip(line)
                    line = str.split(line)
                    logging.info(str(line).encode('utf8'))
                    displayConsoleOut = bool(
                        self.settings.data.get('raw_irc_console_display'))
                    if (displayConsoleOut):
                        try:
                            message = "".join(line) + "\n"
                            self.send_to_outputfield(message)
                        except Exception as e:
                            logging.error("In run")
                            logging.error(str(e))
                            logging.exception("Exception : ")

                    if (
                        len(line) >= 3
                        and "JOIN" == line[1]
                        and ":" + self.nick.lower() + "!" + self.nick.lower() +
                        "@" + self.nick.lower() + ".tmi.twitch.tv" == line[0]
                    ):
                        # cancel auto closing the thread
                        timeoutTimer.cancel()
                        try:
                            message = "Joined "+self.channel+" successfully.\n"
                            self.send_to_outputfield(message)
                            message = (
                                "You can type 'test' in the "
                                f"{self.channel[1:]}"
                                "channel to say hello!\n"
                            )
                            self.send_to_outputfield(message)
                        except Exception as e:
                            logging.error(str(e))
                            logging.exception("Exception : ")

                    if(line[0] == "PING"):
                        self.ircSocket.send(
                            ("PONG %s\r\n" % line[0]).encode("utf8"))
            except Exception as e:
                if e:
                    pass

    def connection_timedout(self):
        "Displays notification when IRC fails to connect."

        try:
            message = (
                f"Connection to {self.channel} timed out, was the channel"
                " spelt correctly and is port 6667 open?\n"
            )
            self.send_to_outputfield(message)
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")
        self.close()

    def close(self):
        "Close handles cleanup of closing the IRC connection."

        self.queue.put("EXITTHREAD")
        logging.info("in close in thread")
        try:
            # send closing message immediately
            """             if self.ircSocket:
                self.ircSocket.send(
                    (
                        f"PRIVMSG {self.channel} :closing opponent"
                        " bot\r\n").encode('utf8')
                    ) """
            while self.channelThread.is_alive():
                pass
            self.running = False
            if self.messageBufferTimer:
                self.messageBufferTimer.cancel()
        except Exception as e:
            logging.error("In close")
            logging.error(str(e))
            logging.exception("Exception : ")

    def assure_path_exists(self, path):
        "Checks directory exists, if not creates it."

        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)

    def check_IRC_send_buffer_every_three_seconds(self):
        "Starts a new threading timer that calls itself every 3 seconds."

        if (self.running):
            self.messageBufferTimer = threading.Timer(
                3.0,
                self.check_IRC_send_buffer_every_three_seconds
            )
            self.messageBufferTimer.start()
        self.IRC_send_called_every_three_seconds()
    # above is the send to IRC timer loop that runs every three seconds

    def send_private_message_to_IRC(self, message):
        "Outputs message to IRC chat channel."

        message = (
            "PRIVMSG " + str(self.channel) + " :" +
            str(message) + "\r\n"
        )
        self.ircMessageBuffer.append(message)
        # removed this to stop message being sent to IRC

    def send_whisper_to_IRC(self, message, whisperTo):
        "Whispers message to an individual."

        try:
            # whisper is currently disabled by twitch
            self.ircMessageBuffer.append(
                "PRIVMSG " + str(self.channel) + " :/w " + str(whisperTo) +
                " " + str(message) + "\r\n"
            )
        except Exception as e:
            logging.error("Error in SendWhisperToIRC")
            logging.error(str(e))
            logging.exception("Exception : ")

    def send_message_to_opponentbot_channel(self, message):
        "Sends a message to the opponent bot channel."

        try:
            self.ircMessageBuffer.append(
                (
                    "PRIVMSG " + str("#" + self.nick).lower() + " :" +
                    str(message) + "\r\n"
                )
            )
        except Exception as e:
            logging.error("Error in SendMessageToOpponentBotChannelIRC")
            logging.error(str(e))
            logging.exception("Exception : ")

    def send_to_outputfield(self, message):
        "Sends a message to the output field of the GUI."

        try:
            # First strip characters outside of range
            # that cannot be handled by tkinter output field
            char_list = ''
            for x in range(len(message)):
                if ord(message[x]) in range(65536):
                    char_list += message[x]
            message = char_list
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")
        try:
            self.output.insert(END, message + "\n")
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")

    def IRC_send_called_every_three_seconds(self):
        "Sends a message from the message buffer every three seconds."

        if (self.ircMessageBuffer):
            try:
                # print("Buffered")
                stringToSend = str(self.ircMessageBuffer.popleft())
                print("string to send : " + stringToSend)
                if self.ircSocket:
                    self.ircSocket.send((stringToSend).encode('utf8'))
            except Exception as e:
                logging.error("IRC send error:")
                logging.error("In IRCSendCalledEveryThreeSeconds")
                logging.error(str(e))
                logging.exception("Exception : ")
    # above is called by the timer every three seconds
    # and checks for items in buffer to be sent, if there is one it'll send it
