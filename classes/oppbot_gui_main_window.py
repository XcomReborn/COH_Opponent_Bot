import sys
import re
import os
import os.path
import base64

import logging
import threading
import webbrowser

import tkinter as tkinter
import tkinter.filedialog
from tkinter import (
    DISABLED,
    END,
    N,
    E,
    NORMAL,
    S,
    W,
    Menu,
    messagebox
    )

from tkinter.ttk import Style
from tkinter import ttk
from TkToolTip import ToolTip

from queue import Queue

from classes.oppbot_icon import Icon
from classes.oppbot_game_data import GameData
from classes.oppbot_memory_monitor import MemoryMonitor
from classes.oppbot_gui_options_window import GUIOptionsWindow
from classes.oppbot_irc_client import IRC_Client
from classes.oppbot_settings import Settings
from classes.oppbot_http_server import OppBotHttpServer

class GUIMainWindow:
    "Graphical User Interface for the COH Opponent Bot."

    def __init__(self):
        # reference to the opponentbot
        self.irc_twitch_client = None
        # reference for coh memory monitor
        self.coh_memory_monitor = None
        # reference to the html server
        self.http_server = None

        self.settings = Settings()

        self.build_date = self.settings.privatedata.get('build_date')
        self.version_number = self.settings.privatedata.get('version_number')

        self.master = tkinter.Tk()

        self.options_menu = None

        self.style = Style()

        self.master.title("COH Opponent Bot")

        self.frame_game_info = tkinter.LabelFrame(
            self.master,
            text="Required Information"
        )
        self.frame_game_info.grid(sticky=N+S+E+W)
        self.frame_game_info.grid_rowconfigure(0, weight=1)
        self.frame_game_info.grid_columnconfigure(0, weight=1)

        # Labels

        tkinter.Label(
            self.frame_game_info,
            text="Steam Name"
            ).grid(row=0, sticky=W)
        tkinter.Label(
            self.frame_game_info,
            text="Steam64ID Number"
            ).grid(row=1, sticky=W)
        tkinter.Label(
            self.frame_game_info,
            text="RelicCOH.exe path"
            ).grid(row=2, sticky=W)
        
        # Entry Widgets

        # Steam Name

        self.entry_steam_name = tkinter.Entry(self.frame_game_info, width=70)
        self.entry_steam_name.grid(row=0, column=1)
        steam_name = "Enter Your Steam Name Here"
        if self.settings.data.get('steamAlias'):
            steam_name = self.settings.data.get('steamAlias')
        self.entry_steam_name.insert(0, str(steam_name))
        self.entry_steam_name.config(state="disabled")

        # SteamID64

        self.entry_steam64id_number = tkinter.Entry(self.frame_game_info, width=70)
        self.entry_steam64id_number.grid(row=1, column=1)
        steam_number = "Enter Your Steam Number Here (17 digits)"
        if self.settings.data.get('steamNumber'):
            steam_number = self.settings.data.get('steamNumber')
        self.entry_steam64id_number.insert(0, steam_number)
        self.entry_steam64id_number.config(state="disabled")

        # Relic COH Path

        self.entry_relic_coh_path = tkinter.Entry(self.frame_game_info, width=70)        
        self.entry_relic_coh_path.grid(row=2, column=1)

        coh_path = self.settings.data.get('cohPath')
        if (coh_path):
            self.entry_relic_coh_path.insert(0, str(coh_path))        
        self.entry_relic_coh_path.config(state="disabled")

        # Edit Buttons

        # Steam Name Button

        self.button_steam_name = tkinter.Button(
            self.frame_game_info,
            text="edit",
            command=self.edit_steam_name)
        
        self.button_steam_name.config(width=10)
        self.button_steam_name.grid(row=0, column=2)

        # SteamID Button

        self.button_steam64id_number = tkinter.Button(
            self.frame_game_info,
            text="edit",
            command=self.edit_steam_number)
        
        self.button_steam64id_number.config(width=10)
        self.button_steam64id_number.grid(row=1, column=2)

        # COH Location Button

        self.button_coh_browse = tkinter.Button(
            self.frame_game_info,
            text="browse",
            command=self.locate_coh)

        self.button_coh_browse.config(width=10)
        self.button_coh_browse.grid(row=2, column=2)

        # Twitch Frame

        self.frame_twitch = tkinter.LabelFrame(
            self.master,
            text="Twitch"
        )
        self.frame_twitch.grid(sticky=N+S+W+E)
        self.frame_twitch.grid_rowconfigure(0, weight=1)
        self.frame_twitch.grid_columnconfigure(0, weight=1)

        # Connect Button

        self.button_connect = ttk.Button(
            self.frame_twitch,
            text="Connect",
            style='Connect.TButton',
            command=self.connect_irc
            )

        self.style.configure(
            'Connect.TButton',
            font='calibri',
            size=10,
            foreground='red')

        self.button_connect.grid(
            sticky=W+E+N+S,
            padx=30,
            pady=30,
            row=0,
            column=0)
        
        button_initial_state = False
        try:
            button_initial_state = bool(
                self.settings.data.get('enable_twitch_bot'))
        except TypeError:
            logging.error('twitch enable initial state error')
        if button_initial_state:
            self.button_connect.configure(state=NORMAL)
        else:
            self.button_connect.configure(state=DISABLED)

        # Connect Button Tool Tip

        self.tooltip_connect_button = ToolTip(
            self.button_connect,
            msg="Press to connect to twitch. (optional)",
            delay=1)

        # Options Button

        self.button_options = tkinter.Button(
            self.frame_twitch,
            text="options",
            command=self.create_twitch_options_menu)

        self.button_options.config(width=10)
        self.button_options.grid(
            sticky=E,
            row=0,
            column= 1)
        
        # test output button

        self.button_test = None
        if self.settings.privatedata.get("devMode"):

            self.button_test = tkinter.Button(
                self.frame_twitch,
                text="Test Output",
                command=self.test_stats)

            self.button_test.config(width=10)
            self.button_test.grid(
                sticky=E,
                row=1,
                column=1)
            self.button_test.config(state=DISABLED)

        #Add in extra entry field for sending messages to twitch chat as the bot.
        if self.settings.privatedata.get('devMode'):

            # Frame messaage

            self.frame_message = tkinter.LabelFrame(
                self.frame_twitch,
                text="Send To Chat"
            )
            self.frame_message.grid(sticky=N+S+W+E, columnspan=2)
            self.frame_message.grid_rowconfigure(0, weight=1)
            self.frame_message.grid_columnconfigure(0, weight=1)

            #create entry field

            self.entry_send_message = tkinter.Entry(
                self.frame_message,
                width=70)
            self.entry_send_message.grid(sticky=W, row=0)
            self.entry_send_message.bind(
                '<Return>',
                self.send_to_chat)

            #create send button

            self.button_send = tkinter.Button(
            self.frame_message, text="send",
            command=self.send_to_chat)
            self.button_send.config(width=10)
            self.button_send.grid(sticky=E, row=0, column=1)

        # Overlay Frame

        self.frame_overlay = tkinter.LabelFrame(
            self.master,
            text="Overlay"
        )

        self.frame_overlay.grid(sticky=N+S+W+E)
        self.frame_overlay.grid_rowconfigure(0, weight=1)
        self.frame_overlay.grid_columnconfigure(0, weight=1)

        # Overlay Options Button

        self.button_options = tkinter.Button(
            self.frame_overlay,
            text="options",
            command=self.create_overlay_options_menu)

        self.button_options.config(width=10)
        self.button_options.grid(
            sticky=E+W,
            row=0,
            column= 1)

        # Open Overlay Button

        self.button_open_overlay = ttk.Button(
            self.frame_overlay,
            text="Open Overlay in Browser",
            style='Overlay.TButton',
            command=self.open_overlay_browser)
        
        self.button_open_overlay.config(width=20)
        self.button_open_overlay.grid(
            sticky=W+E,
            row=0,
            column=0,
            padx=30,
            pady=30)
        
        self.style.configure(
            'Overlay.TButton',
            font='calibri',
            size=10,
            foreground='blue')
        
        # Tooltip Overlay Button

        self.tooltip_overlay_button = ToolTip(
            self.button_open_overlay,
            msg="Display Overlay in your Web-browser, will be blank \n"
                "until a the COH game has started.",
                delay=1
        )

        # Clear Overlay Button

        self.clear_overlay_button = tkinter.Button(
            self.frame_overlay,
            text="Clear Overlay",
            command=GameData.clear_overlay_HTML)
        
        self.clear_overlay_button.config(width=10)
        self.clear_overlay_button.grid(
            sticky=E,
            row=1,
            column=1,
            pady=(0,5))
        

        # Console Output Frame

        self.frame_console = tkinter.LabelFrame(
            self.master,
            text="Console Output:"
            )
        self.frame_console.grid()

        # Text Console

        self.txt_console = tkinter.Text(
            self.frame_console,
            height=10)
        self.txt_console.grid(sticky="nsew", row=1, column=0, padx=2, pady=2)

        # create a Scrollbar and associate it with txt
        scrollbar = ttk.Scrollbar(self.frame_console, command=self.txt_console.yview)
        scrollbar.grid(sticky='nsew', row=1, column=1)
        self.txt_console['yscrollcommand'] = scrollbar.set

        # copy from console window
        # Create a menu

        self.the_menu = tkinter.Menu(self.master, tearoff=0)
        self.the_menu.add_command(label="Cut")
        self.the_menu.add_command(label="Copy")
        self.the_menu.add_command(label="Paste")

        # Bind a func to right click
        self.txt_console.bind_class("Text" , '<Button-3>', self.show_menu)
        self.master.bind_class("Entry", '<Button-3>', self.show_menu)

        # import icon base64 data from separate icon.py file
        icon = Icon.icon

        icondata = base64.b64decode(icon)
        # The temp file is icon.ico
        temp_file = "Icon.ico"
        icon_file_handle = open(temp_file, "wb")
        # Extract the icon
        icon_file_handle.write(icondata)
        icon_file_handle.close()
        self.master.wm_iconbitmap(temp_file)
        # Delete the tempfile
        os.remove(temp_file)

        # Add Menu bar
        self.menu_bar = Menu(self.master)
        self.menu_file = Menu(self.menu_bar, tearoff=0)

        # File Menu

        self.menu_bar.add_cascade(label="File", menu=self.menu_file)

        self.menu_file.add_command(
            label="Load Preferences",
            command=self.load_preferences)
        self.menu_file.add_command(
            label="Save Preferences",
            command=self.save_preferences)
        self.menu_file.add_separator()

        self.menu_file.add_command(label="Exit", command=self.master.quit)

        # Edit Menu
        
        self.menu_edit = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.menu_edit)

        self.menu_edit.add_command(
            label="Cut",
            command=lambda: self.master.event_generate('<Control-x>')
        )
        self.menu_edit.add_command(
            label="Copy",
            command=lambda: self.master.event_generate('<Control-c>')
        )
        self.menu_edit.add_command(
            label="Paste",
            command=lambda: self.master.event_generate('<Control-v>')
        )


        # Setting Menu

        self.menu_settings = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=self.menu_settings)

        self.menu_settings.add_command(
            label="Settings",
            command=self.create_general_options_menu)

        # Help Menu

        self.menu_help = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.menu_help)
       
        self.menu_help.add_command(
            label="About...",
            command=self.show_about_dialogue)
        
        self.master.config(menu=self.menu_bar)
        
        # Assign Delete function

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start Memory Monitor

        self.start_coh_monitor()

        # start HTML Server
        if self.settings.data.get('http_server_enabled'):
            self.http_server_start()

        self.master.mainloop()

    #@staticmethod
    def open_overlay_browser(self):
        try:
            game_data = GameData(settings=self.settings)
            game_data.get_data_from_game()
            game_data.output_opponent_data()
            webbrowser.open("overlay.html", new=2)
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")

    def show_menu(self, e):
        "Cut Copy Paste."
        w = e.widget
        self.the_menu.entryconfigure("Cut",
        command=lambda: w.event_generate("<<Cut>>"))
        self.the_menu.entryconfigure("Copy",
        command=lambda: w.event_generate("<<Copy>>"))
        self.the_menu.entryconfigure("Paste",
        command=lambda: w.event_generate("<<Paste>>"))
        self.the_menu.tk.call("tk_popup", self.the_menu, e.x_root, e.y_root)

    def send_to_tkconsole(self, message):
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
            if self.txt_console:
                self.txt_console.insert(END, message + "\n")
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")

    def send_to_chat(self, e = None):
        "send to chat."
        if self.irc_twitch_client:
            message = self.entry_send_message.get()
            self.irc_twitch_client.send_private_message_to_IRC(message)
            self.entry_send_message.delete(0, END)

    def save_preferences(self):
        "Save preferences drop down."

        files = [('Json', '*.json'), ('All Files', '*.*')]
        working_directory = os.getcwd()
        logging.info(f"Working Directory : {working_directory}")
        self.master.filename = tkinter.filedialog.asksaveasfilename(
            initialdir=working_directory,
            initialfile="data.json",
            title="Save Preferences File",
            filetypes=files)
        logging.info("File Path : %s", self.master.filename)
        logging.info("File Path : " + str(self.master.filename))
        if(self.master.filename):
            pattern = re.compile(r"\u20A9|\uFFE6|\u00A5|\uFFE5")
            # replaces both Won sign varients for korean language
            # and Yen symbol for Japanese language paths
            the_file_name = re.sub(pattern, "/", self.master.filename)
            self.settings.save(the_file_name)
            if self.coh_memory_monitor:
                self.coh_memory_monitor.settings = self.settings

    def load_preferences(self):
        "load preferences drop down."

        files = [('Json', '*.json'), ('All Files', '*.*')]
        working_directory = os.getcwd()
        logging.info(f"workingDirectory : {working_directory}")
        self.master.filename = tkinter.filedialog.askopenfilename(
            initialdir=working_directory,
            initialfile="data.json",
            title="Load Preferences File",
            filetypes=files)
        logging.info("File Path : %s" , self.master.filename)
        if(self.master.filename):
            pattern = re.compile(r"\u20A9|\uFFE6|\u00A5|\uFFE5")
            # replaces both Won sign varients for korean language
            # and Yen symbol for Japanese language paths
            filename = re.sub(pattern, "/", self.master.filename)
            self.settings.load(filename)
            self.refresh_settings()

    def refresh_settings(self):
        "reloads settings into self.settings."
        self.settings = Settings()

    def show_about_dialogue(self):
        "shows about dialogue."
        information_string = (
            f"Version : {self.version_number}\n\n"
            f"Build Date : {self.build_date}\n\n"
            "Created by : XcomReborn\n\n"
            "Special thanks : AveatorReborn"
        )
        tkinter.messagebox.showinfo("Information", information_string)

    def create_general_options_menu(self):
        "creates general option menu."
        if not self.options_menu:
            self.options_menu = GUIOptionsWindow(self, "general")
        else:
            self.options_menu.on_close_options()
            self.options_menu = GUIOptionsWindow(self, "general")

    def create_twitch_options_menu(self):
        "creates twitch option menu."
        if not self.options_menu:
            self.options_menu = GUIOptionsWindow(self, "twitch")
        else:
            self.options_menu.on_close_options()
            self.options_menu = GUIOptionsWindow(self, "twitch")

    def create_overlay_options_menu(self):
        "creates overlay option menu."
        if not self.options_menu:
            self.options_menu = GUIOptionsWindow(self, "overlay")
        else:
            self.options_menu.on_close_options()
            self.options_menu = GUIOptionsWindow(self, "overlay")


    def test_stats(self):
        "tests the stats output."
        logging.info("Testing Stats")
        if (self.irc_twitch_client):
            self.irc_twitch_client.queue.put('TEST')


    def disable_everything(self):
        "disable everything, all widgets."
        self.button_steam_name.config(state=DISABLED)
        self.button_steam64id_number.config(state=DISABLED)
        self.button_coh_browse.config(state=DISABLED)
        self.button_connect.config(state=DISABLED)

        self.entry_steam64id_number.config(state=DISABLED)
        self.entry_relic_coh_path.config(state=DISABLED)


    def enable_buttons(self):
        "enable buttons."
        self.button_steam_name.config(state=NORMAL)
        self.button_steam64id_number.config(state=NORMAL)
        self.button_coh_browse.config(state=NORMAL)
        # need to load uncase set by another widget.
        self.settings.load()
        if bool(self.settings.data.get('enable_twitch_bot')):
            self.button_connect.config(state=NORMAL)



    def edit_steam_number(self):
        "edit steam number."
        the_state = self.entry_steam64id_number.cget('state')
        if(the_state == "disabled"):
            self.disable_everything()
            self.button_steam64id_number.config(state=NORMAL)
            self.entry_steam64id_number.config(state=NORMAL)

        if(the_state == "normal"):
            if self.check_steam_number(self.entry_steam64id_number.get()):
                self.entry_steam64id_number.config(state=DISABLED)
                self.enable_buttons()
                steam64ID = self.entry_steam64id_number.get()
                self.settings.data['steamNumber'] = steam64ID
                self.settings.save()
                if self.coh_memory_monitor:
                    self.coh_memory_monitor.settings = self.settings
            else:
                messagebox.showerror(
                    "Invaid Steam Number", "Please enter your steam number\n"
                    "It Should be an integer 17 characters long")

    def edit_steam_name(self):
        "edit steam name."
        the_state = self.entry_steam_name.cget('state')
        if(the_state == DISABLED):
            self.disable_everything()
            self.entry_steam_name.config(state=NORMAL)
            self.button_steam_name.config(state=NORMAL)

        if(the_state == NORMAL):
            self.entry_steam_name.config(state=DISABLED)
            self.enable_buttons()
            self.settings.data['steamAlias'] = self.entry_steam_name.get()
            self.settings.save()
            if self.coh_memory_monitor:
                self.coh_memory_monitor.settings = self.settings

    def special_match(
            self,
            strg,
            search=re.compile(r'^[a-zA-Z0-9][\w]{3,24}$').search
            ):
        """special match for twitch usernames."""
        if strg == "":
            return True  # empty returns True
        return bool(search(strg))
        # Allowed twitch username returns True,
        # if None, it returns False

    def check_steam_number(self, number):
        "check steam number."
        try:
            number = int(number)
            if isinstance(number, int):
                if (len(str(number)) == 17):
                    return True
            return False
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")

    def locate_coh(self):
        "locate COH."
        self.disable_everything()
        self.master.filename = tkinter.filedialog.askopenfilename(
            initialdir="/",
            title="Select location of RelicCOH.exe file",
            filetypes=(("RelicCOH", "*.exe"), ("all files", "*.*")))
        logging.info("File Path : %s", self.master.filename)
        if(self.master.filename != ""):
            # set cohPath
            if (os.path.isfile(self.master.filename)):
                self.settings.data['cohPath'] = self.master.filename
            # set ucsPath
            d = os.path.dirname(self.master.filename)
            ucs_path = d + (
                "\\CoH\\Engine\\Locale\\English"
                "\\RelicCOH.English.ucs")
            if (os.path.isfile(ucs_path)):
                self.settings.data['cohUCSPath'] = ucs_path
            self.entry_relic_coh_path.config(state=NORMAL)
            self.entry_relic_coh_path.delete(0, tkinter.END)
            cohpath = self.settings.data.get('cohPath')
            if cohpath:
                self.entry_relic_coh_path.insert(0, str(cohpath))
            self.entry_relic_coh_path.config(state=DISABLED)
            self.settings.save()
            if self.coh_memory_monitor:
                self.coh_memory_monitor.settings = self.settings
        self.enable_buttons()

    def reenable_connect_button(self):
        "re-enables button after connection failure"
        self.enable_buttons()
        self.button_connect.config(text="Connect")
        if self.irc_twitch_client:
            self.irc_twitch_client.close()
        self.irc_twitch_client = None

    def reenable_disconnect_button(self):
        "re-enables button after connection success"
        self.enable_buttons()
        self.button_connect.config(text="Disconnect")

    def connect_irc(self):
        "connect irc."
        self.settings.load()
        if (
            self.check_steam_number(self.settings.data.get('steamNumber'))
            and self.special_match(self.settings.data.get('channel'))
        ):
            # connect if there is no thread running
            # disconnect if thread is running
            if self.irc_twitch_client:
                # close thread
                try:
                    self.irc_twitch_client.close()

                except Exception as e:
                    logging.error(str(e))
                    logging.exception("Exception : ")
                if self.button_test:
                    self.button_test.config(state=DISABLED)
                self.enable_buttons()
                self.button_connect.config(text="Connect")
                self.irc_twitch_client = None

            else:
                # start thread
                self.disable_everything()
                self.button_connect.config(text="Disconnect")
                if self.button_test:
                    self.button_test.config(state=NORMAL)
                self.irc_twitch_client = IRC_Client(self, self.txt_console)
                self.irc_twitch_client.start()
                # Assign reference to memory monitor to pass messages
                if self.coh_memory_monitor:
                    self.coh_memory_monitor.irc_client = self.irc_twitch_client
        else:
            messagebox.showerror(
                "Invalid details",
                "Please check that your twitch username and "
                "Steam Number are valid.")

    def start_coh_monitor(self):
        "start monitor."
        # Ensure they are off if running
        if self.coh_memory_monitor:
            self.coh_memory_monitor.close()
        # Create Monitor Thread.
        self.coh_memory_monitor = MemoryMonitor(
            poll_interval=self.settings.data.get('filePollInterval'),
            settings=self.settings,
            tkconsole=self.txt_console)
        self.coh_memory_monitor.start()

    def http_server_start(self):
        logging.info("Starting Local HTML Server")
        if not self.http_server:
            self.settings.load()
            port = self.settings.data.get('http_server_port')
            if not port:
                logging.info("No HTML Server Port set: server will not start.")
                return
            self.http_server = OppBotHttpServer(port=port)
            self.http_server.start()
        else:
            logging.info("HTML Server is already running, nothing to do.")

    def http_server_stop(self):
        logging.info("Stopping Local HTML Server")
        if self.http_server:
            # Stop the HTML server
            self.http_server.stop()
            # Wait for the thread to finish
            self.http_server.join()
            # set reference to None
            self.http_server = None
        else:
            logging.info("HTML Server was not running, nothing to stop.")

    def on_closing(self):
        "on closing."
        logging.info("In on_closing program (Closing)")
        try:
            if self.irc_twitch_client:
                self.irc_twitch_client.close()
                self.irc_twitch_client.join()
            
            if self.coh_memory_monitor:
                self.coh_memory_monitor.close()
                self.coh_memory_monitor.join()

            if self.http_server:
                if self.http_server.is_alive():
                    logging.info("Stopping HTML Server")
                    self.http_server.stop()
                    # Wait for the thread to finish
                    self.http_server.join()
                
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")
        while (threading.active_count() > 1):
            pass
        logging.info("Exiting main thread")
        sys.exit()
