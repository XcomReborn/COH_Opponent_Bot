import os
from posixpath import relpath
import re
import tkinter
import logging

from tkinter import (
    BOTH, DISABLED, END, N, E, NORMAL, S, W, WORD, IntVar, Menu, StringVar, Tk, messagebox
    )
import tkinter.scrolledtext

from classes.oppbot_settings import Settings

class OptionsTwitchChat:
    "Graphical User Interface Options Window for the COH Opponent Bot."

    def __init__(self,main_window, parent_frame):
        "Twitch Chat Options"

        self.main_window = main_window
        self.parent_frame = parent_frame
        self.settings = Settings()

        self.frame = tkinter.LabelFrame(
        self.parent_frame,
        text="Twitch Chat Options",
        padx=5,
        pady=5)

        self.frame.grid(sticky=N+S+W+E)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)        

        v = int(bool(self.settings.data.get('showOwn')))
        self.intvar_show_own = IntVar(value=v)
        v = int(bool(self.settings.data.get('writeIWonLostInChat')))
        self.intvar_write_won_lost = IntVar(value=v)
        v = int(bool(self.settings.data.get('automaticSetBettingOdds')))
        self.intvar_setodds = IntVar(value=v)
        v = int(bool(self.settings.data.get('writePlaceYourBetsInChat')))
        self.intvar_place_bets = IntVar(value=v)
        v = int(bool(self.settings.data.get('enable_twitch_bot')))
        self.intvar_enable_twitch_bot = IntVar(value=v)

        self.stringvar_twitch_chat_pf = StringVar()

        # enable check

        self.check_enable_twitch_bot = tkinter.Checkbutton(
            self.frame,
            text="Enable Twitch Bot",
            variable=self.intvar_enable_twitch_bot,
            command=self.toggle_enable_twitch)

        self.check_enable_twitch_bot.grid(sticky=W)

        # label Frame
        self.frame_twitch_channel = tkinter.LabelFrame(
            self.frame,
            text="Twitch Channel",
            padx=5,
            pady=5)
        self.frame_twitch_channel.grid(sticky=W+E)
        self.frame_twitch_channel.grid_rowconfigure(0, weight=1)
        self.frame_twitch_channel.grid_columnconfigure(0, weight=1)

        # twitch channel label 
        tkinter.Label(
            self.frame_twitch_channel,
            text="Connect To Channel"
            ).grid(row=0, column=0, sticky=W)
        
        # twitch entry
        
        self.entry_twitch_channel = tkinter.Entry(self.frame_twitch_channel, width=100)
        self.entry_twitch_channel.grid(row=0, column=1)

        twitch_name = "Enter Your Twitch Channel Name Here"
        if self.settings.data.get('channel'):
            twitch_name = self.settings.data.get('channel')
        self.entry_twitch_channel.insert(0, twitch_name)

        self.entry_twitch_channel.config(state="disabled")

        # twitch button

        self.button_twitch_channel = tkinter.Button(
            self.frame_twitch_channel, text="edit", command=self.edit_twitch_name)
        self.button_twitch_channel.config(width=10)
        self.button_twitch_channel.grid(row=0, column=2) 

        # show own stats check

        self.check_own = tkinter.Checkbutton(
            self.frame,
            text="Show Own Stats",
            variable=self.intvar_show_own,
            command=self.save_toggles)

        self.check_own.grid(sticky=W)

        # Text Variables

        self.frame_overlay_text = tkinter.LabelFrame(
            self.frame,
            text="Text Variables",
            padx=5,
            pady=5
            )
        self.frame_overlay_text.grid(sticky=N+W+E)

        self.string_format_labels = []
        self.my_label_frames = []
        # create all custom variables from dictionary keys
        column_number = 0
        row_number = 0

        sfd = self.settings.stringFormattingDictionary
        for key, value in sfd.items():

            my_label_frame = tkinter.LabelFrame(
                self.frame_overlay_text,
                padx=5,
                pady=5)
            self.frame.columnconfigure(
                column_number)
            self.my_label_frames.append(my_label_frame)
            my_label = tkinter.Label(my_label_frame, text=str(key), width=15)
            my_label.grid()

            my_label_frame.grid(
                row=row_number,
                column=column_number,
                sticky=N + W + E)
            column_number += 1
            if column_number > 6:
                row_number += 1
                column_number = 0
            self.string_format_labels.append(my_label)

        # Entry

        self.label_chat_preformat = tkinter.Label(
            self.frame,
            text="Chat Output Pre-Format")
        self.label_chat_preformat.grid(sticky=W)

        self.entry_chat_custom = tkinter.Entry(
            self.frame,
            width=120,
            textvariable=self.stringvar_twitch_chat_pf,
            validate="all",
            validatecommand=self.save_custom_chat_preformat)
        
        if self.settings.data.get('chat_custom_pf'):
            self.stringvar_twitch_chat_pf.set(
                self.settings.data.get('chat_custom_pf'))

        self.entry_chat_custom.grid(sticky=W)

        # CustomBotCredientials

        # label Frame
        self.frame_optional_bot_credentials = tkinter.LabelFrame(
            self.frame,
            text="Optional Bot Credentials",
            padx=5,
            pady=5)
        self.frame_optional_bot_credentials.grid(sticky=W+E)
        self.frame_optional_bot_credentials.grid_rowconfigure(0, weight=1)
        self.frame_optional_bot_credentials.grid_columnconfigure(0, weight=1)

        # entry
        self.label_botacc = tkinter.Label(
            self.frame_optional_bot_credentials,
            text="Bot Account Name")
        self.label_botacc.grid(sticky=W, row=0, column=0)
        
        self.entry_bot_account_name = tkinter.Entry(
            self.frame_optional_bot_credentials,
            width=100)
        
        self.entry_bot_account_name.grid(sticky=E, row=0, column=1)

        if (self.settings.data.get('botUserName')):
            self.entry_bot_account_name.insert(
                0,
                str(self.settings.data.get('botUserName')))
            
        self.entry_bot_account_name.config(state="disabled")
            
        # button
        self.button_bot_account_name = tkinter.Button(
            self.frame_optional_bot_credentials,
            text="edit",
            command=self.edit_bot_name)
        self.button_bot_account_name.config(width=10)
        self.button_bot_account_name.grid(sticky=E, row=0, column=2)


        # label

        self.label_botkey = tkinter.Label(
            self.frame_optional_bot_credentials,
            text="Bot oAuth Key")
        self.label_botkey.grid(sticky=W, row=1, column=0)

        # entry

        self.entry_bot_oAuthKey = tkinter.Entry(
            self.frame_optional_bot_credentials,
            width=100)
        
        self.entry_bot_oAuthKey.grid(sticky=E, row=1, column=1)

        if (self.settings.data.get('botOAuthKey')):
            self.entry_bot_oAuthKey.insert(
                0,
                str(self.settings.data.get('botOAuthKey')))

        self.entry_bot_oAuthKey.config(show="*")
        self.entry_bot_oAuthKey.config(state="disabled")

        # button

        self.button_bot_OAuthKey = tkinter.Button(
            self.frame_optional_bot_credentials,
            text="edit",
            command=self.edit_oauth_key)
        self.button_bot_OAuthKey.config(width=10)
        self.button_bot_OAuthKey.grid(sticky=E, row=1, column=2)

    def save_custom_chat_preformat(self):
        "saves custom chat preformat."
        if self.stringvar_twitch_chat_pf:
            cco = self.stringvar_twitch_chat_pf.get()
            self.settings.data['chat_custom_pf'] = cco
        self.settings.save()
        if self.main_window.coh_memory_monitor:
            self.main_window.coh_memory_monitor.settings = self.settings

        return True  # must return true to a validate entry method

    def save_toggles(self):
        "saves all toggles."

        self.settings.data['showOwn'] = bool(self.intvar_show_own.get())

        self.settings.data['automaticSetBettingOdds'] = (
            bool(self.intvar_setodds.get()))

        self.settings.data['writeIWonLostInChat'] = (
            bool(self.intvar_write_won_lost.get()))

        self.settings.data['writePlaceYourBetsInChat'] = (
            bool(self.intvar_place_bets.get()))

        self.settings.data['enable_twitch_bot'] = (
            bool(self.intvar_enable_twitch_bot.get()))

        self.settings.save()
        if self.main_window.coh_memory_monitor:
            self.main_window.coh_memory_monitor.settings = self.settings


    def toggle_enable_twitch(self):
        """enables or disables toggle"""
        checkState = bool(self.intvar_enable_twitch_bot.get())
        if checkState:
            self.main_window.button_connect.config(state=NORMAL)
        else:
            self.main_window.button_connect.config(state=DISABLED)

        self.save_toggles()


    def edit_twitch_name(self):
        "edit twitch name."
        theState = self.entry_twitch_channel.cget('state')
        if(theState == DISABLED):
            self.main_window.disable_everything()
            self.entry_twitch_channel.config(state=NORMAL)
            self.button_twitch_channel.config(state=NORMAL)

        if(theState == NORMAL):
            if(self.special_match(self.entry_twitch_channel.get())):
                self.entry_twitch_channel.config(state=DISABLED)
                self.main_window.enable_buttons()
                self.settings.data['channel'] = self.entry_twitch_channel.get()
                self.settings.save()
                if self.main_window.coh_memory_monitor:
                    self.main_window.coh_memory_monitor.settings = self.settings

            else:
                messagebox.showerror(
                    "Invalid Twitch channel",
                    "That doesn't look like a valid channel name\n"
                    "Twitch user names should be 4-24 characters long\n"
                    "and only contain letters numbers and underscores.")

    def edit_bot_name(self):
        "edit bot name."
        the_state = self.entry_bot_account_name.cget('state')
        if(the_state == "disabled"):
            self.main_window.disable_everything()
            self.button_bot_account_name.config(state=NORMAL)
            self.entry_bot_account_name.config(state=NORMAL)

        if(the_state == "normal"):
            if(self.special_match(self.entry_bot_account_name.get())):
                self.entry_bot_account_name.config(state="disabled")
                self.main_window.enable_buttons()
                botacc = self.entry_bot_account_name.get()
                self.settings.data['botUserName'] = botacc
                self.settings.save()
                if self.main_window.coh_memory_monitor:
                    self.main_window.coh_memory_monitor.settings = self.settings

            else:
                messagebox.showerror(
                    "Invalid Twitch channel",
                    "That doesn't look like a valid Twitch user name\n"
                    "Twitch user names should be 4-24 characters long\n"
                    "and only contain letters numbers and underscores.")

    def edit_oauth_key(self):
        "edit oauth key."
        the_state = self.entry_bot_oAuthKey.cget('state')
        if(the_state == "disabled"):
            self.main_window.disable_everything()
            self.button_bot_OAuthKey.config(state=NORMAL)
            self.entry_bot_oAuthKey.config(state=NORMAL)

        if(the_state == "normal"):
            if self.check_oauth_key(self.entry_bot_oAuthKey.get()):
                self.entry_bot_oAuthKey.config(state="disabled")
                self.main_window.enable_buttons()
                oAuth = self.entry_bot_oAuthKey.get()
                self.settings.data['botOAuthKey'] = oAuth
                self.settings.save()
                if self.main_window.coh_memory_monitor:
                    self.main_window.coh_memory_monitor.settings = self.settings

            else:
                messagebox.showerror(
                    "Invaid OAuth Key",
                    "Please enter your bots OAuth Key\n"
                    "It Should be an 36 characters long and "
                    "start with oauth:\n"
                    "You can find it here https://twitchapps.com/tmi/")
                
    def check_oauth_key(self, oauthkey):
        "check oauth key."
        try:
            if (oauthkey[:6] == "oauth:") or (oauthkey == ""):
                return True
            return False
        except Exception as e:
            logging.error(str(e))
            logging.exception("Exception : ")
            return False

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
