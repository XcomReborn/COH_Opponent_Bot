import os
from posixpath import relpath
import re
import tkinter
import logging

from tkinter import (
    DISABLED, END, N, E, NORMAL, S, W, WORD, IntVar, Menu, StringVar, Tk, messagebox
    )
import tkinter.scrolledtext

from classes.oppbot_settings import Settings

class OptionsGeneral:
    "Graphical User Interface Options Window for the COH Opponent Bot."

    def __init__(self,main_window, parent_frame):
        "Twitch Chat Options"

        self.main_window = main_window
        self.parent_frame = parent_frame
        self.settings = Settings()

        self.frame = tkinter.LabelFrame(
        self.parent_frame,
        text="General Options",
        padx=5,
        pady=5)

        self.frame.grid(sticky=W+E)

        v = int(bool(self.settings.data.get('automaticTrigger')))
        self.intvar_automatic_trigger = IntVar(value=v)

        v = int(bool(self.settings.data.get('logErrorsToFile')))
        self.intvar_log_errors_to_file = IntVar(value=v)

        v = int(bool(self.settings.data.get('raw_irc_console_display')))
        self.intvar_console_display_bool = IntVar(value=v)

        #try:
        #    v = int(self.settings.data.get('pollMethod'))
        #except TypeError:
        #    v = 0
        #self.intvar_poll_method = IntVar(value=v)

        #self.frame_radio = tkinter.LabelFrame(
        #    self.frame,
        #    text="Mode",
        #    padx=5,
        #    pady=5)
        #self.frame_radio.grid(sticky=W+E)

        #self.radio_button_1 = tkinter.Radiobutton(
        #    self.frame_radio,
        #    text="Inspect Game Memory",
        #    variable=self.intvar_poll_method,
        #    value=0,
        #    command=self.save_toggles)

        #self.radio_button_1.grid( sticky= W )

        #self.radio_button_2 = tkinter.Radiobutton(
        #    self.frame_radio,
        #    text="Poll Warning File",
        #    variable=self.intvar_poll_method,
        #    value=1,
        #    command=self.save_toggles)

        #self.radio_button_2.grid( sticky= W )


        self.check_automatic_trigger = tkinter.Checkbutton(
            self.frame,
            text="Automatic Trigger",
            variable=self.intvar_automatic_trigger,
            command=self.save_toggles)
        self.check_automatic_trigger.grid(sticky=W)

        # Console Display Check

        self.check_raw_console_display = tkinter.Checkbutton(
            self.frame,
            text="Raw IRC Log To Console",
            variable=self.intvar_console_display_bool,
            command=self.save_toggles)
        self.check_raw_console_display.grid(sticky=W)

        # Log Errors Check

        self.check_log_error_to_file = tkinter.Checkbutton(
            self.frame,
            text="Log Errors To File",
            variable=self.intvar_log_errors_to_file,
            command=self.toggle_log_errors_to_file
        )
        self.check_log_error_to_file.grid(sticky=W)

    def save_toggles(self):
        "saves all toggles."

        self.settings.data['automaticTrigger'] = (
            bool(self.intvar_automatic_trigger.get()))

        self.settings.data['logErrorsToFile'] = (
            bool(self.intvar_log_errors_to_file.get()))

        self.settings.data['raw_irc_console_display'] = (
            bool(self.intvar_console_display_bool.get()))
        
        self.settings.save()

    def toggle_log_errors_to_file(self):
        "Change preference for logging errors to file."

        if (bool(self.intvar_log_errors_to_file.get())):
            logging.getLogger().disabled = False
            logging.info("Logging Started")
            logging.info(self.settings.privatedata.get("version_number"))
        else:
            logging.info("Stop Logging")
            logging.getLogger().disabled = True

        self.save_toggles()