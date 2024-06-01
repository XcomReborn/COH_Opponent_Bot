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
from queue import Queue

from classes.oppbot_icon import Icon
from classes.oppbot_game_data import GameData
from classes.oppbot_memory_monitor import MemoryMonitor
from classes.oppbot_gui_options_window import GUIOptionsWindow
from classes.oppbot_player import Player
from classes.oppbot_stats_request import StatsRequest
from classes.oppbot_irc_client import IRC_Client
from classes.oppbot_settings import Settings

class GUIMainWindow:
    "Graphical User Interface for the COH Opponent Bot."

    def __init__(self):
        # reference to the opponentbot
        self.irc_twitch_client = None
        # reference for coh memory monitor
        self.coh_memory_monitor = None

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

        self.button_connect = ttk.Button(
            self.frame_twitch,
            text="Connect",
            style='W.TButton',
            command=self.connect_irc
            )

        self.style.configure(
            'W.TButton',
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
        if self.settings.data.get("devMode"):

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
            column= 4)

        # Open Overlay Button

        self.button_open_overlay = tkinter.Button(
            self.frame_overlay,
            text="Open Overlay in Browser",
            command=self.open_overlay_browser)
        
        self.button_open_overlay.config(width=20)
        self.button_open_overlay.grid(
            sticky=W+E,
            row=1,
            column=3)

        # Clear Overlay Button

        self.clear_overlay_button = tkinter.Button(
            self.frame_overlay,
            text="Clear Overlay",
            command=GameData.clear_overlay_HTML)
        
        self.clear_overlay_button.config(width=10)
        self.clear_overlay_button.grid(
            sticky=E,
            row=1,
            column=4)
        
        # Label
        self.label_stat_request = tkinter.Label(
            self.frame_overlay,
            text="Request Stat For : "
        )
        self.label_stat_request.grid(
            sticky=W,
            row=2,
            column=0
        )
        
        # Steam Number Entry
        self.entry_stat_request = tkinter.Entry(self.frame_overlay, width=40)
        self.entry_stat_request.grid(
            sticky=W,
            row=2,
            column=1,
            padx=(5,5)
        )

        steam_number = "Enter Your Steam Number Here (17 digits)"
        if self.settings.data.get('stat_request_number'):
            steam_number = self.settings.data.get('stat_request_number')
        self.entry_stat_request.insert(0, steam_number)

        self.entry_stat_request.config(state=DISABLED)


        # Steam Number Entry Edit Button

        self.button_stat_edit = tkinter.Button(
            self.frame_overlay,
            text="Edit",
            command=self.edit_stat_request
        )
        self.button_stat_edit.grid(
            sticky=W,
            row=2,
            column=2
        )
        self.button_stat_edit.configure(width=10)

        
        # Display Stats Button

        self.button_display_stats = tkinter.Button(
            self.frame_overlay,
            text="Display Stats in Browser",
            command=self.open_stats_browser)
        
        self.button_display_stats.config(width=20)
        self.button_display_stats.grid(
            sticky=W+E,
            row=2,
            column=3)
                
        # Clear Stats Button

        self.clear_overlay_button = tkinter.Button(
            self.frame_overlay,
            text="Clear Stats",
            command=GameData.clear_stats_HTML)
        
        self.clear_overlay_button.config(width=10)
        self.clear_overlay_button.grid(
            sticky=E+W,
            row=2,
            column=4)

        # Console Output Frame

        self.frame_console = tkinter.LabelFrame(
            self.master,
            text="Console Output:"
            )
        self.frame_console.grid()

        # Text widget

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
       

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.master.config(menu=self.menu_bar)

        #Add in extra entry field for sending messages to twitch chat as the bot.
        if self.settings.privatedata.get('devMode'):
            self.frame_message = tkinter.LabelFrame(
                self.master,
                text="Send To Chat"
            )
            self.frame_message.grid(sticky=N+S+W+E)
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

        self.start_coh_monitor()

        self.master.mainloop()

    @staticmethod
    def open_overlay_browser():
        try:
            webbrowser.open("overlay.html", new=2)
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")

    def open_stats_browser(self):
        try:
            # create gamedata
            gamedata = GameData(tkconsole=self.txt_console)
            # create a player object based on steamnumber
            player = Player()
            stats_request = StatsRequest()
            stat = stats_request.return_stats(self.settings.data.get('stat_request_number'))
            player.stats = stat
            if stat:
                player.name = stat.alias
            gamedata.create_stats_html(player)
            webbrowser.open("stats.html", new=2)
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
        print(f"Working Directory : {working_directory}")
        self.master.filename = tkinter.filedialog.asksaveasfilename(
            initialdir=working_directory,
            initialfile="data.json",
            title="Save Preferences File",
            filetypes=files)
        logging.info("File Path : %s", self.master.filename)
        print("File Path : " + str(self.master.filename))
        if(self.master.filename):
            pattern = re.compile(r"\u20A9|\uFFE6|\u00A5|\uFFE5")
            # replaces both Won sign varients for korean language
            # and Yen symbol for Japanese language paths
            the_file_name = re.sub(pattern, "/", self.master.filename)
            self.settings.save(the_file_name)

    def load_preferences(self):
        "load preferences drop down."

        files = [('Json', '*.json'), ('All Files', '*.*')]
        working_directory = os.getcwd()
        print(f"workingDirectory : {working_directory}")
        self.master.filename = tkinter.filedialog.askopenfilename(
            initialdir=working_directory,
            initialfile="data.json",
            title="Load Preferences File",
            filetypes=files)
        logging.info("File Path : %s" , self.master.filename)
        print("File Path : " + str(self.master.filename))
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

    def create_twitch_options_menu(self):
        "creates twitch option menu."
        if not self.options_menu:
            self.options_menu = GUIOptionsWindow(self, "twitch")

    def create_overlay_options_menu(self):
        "creates overlay option menu."
        if not self.options_menu:
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

    def edit_stat_request(self):
        "edit stat request"
        the_state = self.entry_stat_request.cget('state')
        if(the_state == "disabled"):
            self.entry_stat_request.config(state=NORMAL)
        if(the_state == "normal"):
            if self.check_steam_number(self.entry_stat_request.get()):
                self.entry_stat_request.config(state=DISABLED)
                self.enable_buttons()
                steam64ID = self.entry_stat_request.get()
                self.settings.data['stat_request_number'] = steam64ID
                self.settings.save()
            else:
                messagebox.showerror(
                    "Invaid Steam Number", "Please enter your steam number\n"
                    "It Should be an integer 17 characters long")

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
        print(f"File Path : {self.master.filename}")
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
        self.enable_buttons()

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
                self.irc_twitch_client = IRC_Client(self.txt_console)
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
        self.close_coh_monitor()
        # Create Monitor Thread.
        self.coh_memory_monitor = MemoryMonitor(
            poll_interval=self.settings.data.get('filePollInterval'),
            settings=self.settings,
            tkconsole=self.txt_console)
        self.coh_memory_monitor.start()

    def close_coh_monitor(self):
        "close monitors."
        if self.coh_memory_monitor:
            self.coh_memory_monitor.close()

    def on_closing(self):
        "on closing."
        logging.info("In on_closing program (Closing)")
        try:
            if(self.irc_twitch_client):
                self.irc_twitch_client.close()
            self.close_coh_monitor()
            while ((self.irc_twitch_client) and (self.coh_memory_monitor)):
                # wait for irc_twitch_client and coh_memory_monitor
                # to exit and become None
                pass
                
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")
        while (threading.active_count() > 1):
            pass
        logging.info("Exiting main thread")
        sys.exit()
