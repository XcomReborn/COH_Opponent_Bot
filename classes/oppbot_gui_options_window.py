import os
from posixpath import relpath
import re
import tkinter
import logging

from tkinter import (
    DISABLED, END, N, E, NORMAL, S, W, WORD, IntVar, Menu, StringVar, Tk, messagebox
    )
import tkinter.scrolledtext

from classes.oppbot_gui_options_general import OptionsGeneral
from classes.oppbot_gui_options_overlay import OptionsOverlay
from classes.oppbot_gui_options_twitch_chat import OptionsTwitchChat
from classes.oppbot_settings import Settings

class GUIOptionsWindow:
    "Graphical User Interface Options Window for the COH Opponent Bot."

    def __init__(self, mainwindow, type="general"):
        "Create New TopLevel Options Window"

        self.mainwindow = mainwindow
        self.settings = Settings()

        self.options_menu = tkinter.Toplevel(mainwindow.master)
        self.options_menu.protocol(
            "WM_DELETE_WINDOW",
            self.on_close_options)
        self.options_menu.title("Options")

        if type == "general":
            self.frame_general = OptionsGeneral(self.mainwindow, self.options_menu)
        if type == "twitch":
            self.frame_twitch_chat = OptionsTwitchChat(self.mainwindow, self.options_menu)
        if type == "overlay":
            self.frame_overlay = OptionsOverlay(self.mainwindow, self.options_menu)

        try:
            self.options_menu.focus()
        except Exception as e:
            logging.error('Exception : %s' , str(e))

    def on_close_options(self):
        "on close options destroy window."
        self.options_menu.destroy()
        self.mainwindow.options_menu = None
        logging.info("Options Window Closed")
