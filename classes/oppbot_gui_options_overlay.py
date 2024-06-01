import os
from posixpath import relpath
import re
import tkinter
import logging

from tkinter import (
    DISABLED, END, N, E, NORMAL, S, W, WORD, IntVar, Menu, StringVar, Tk, messagebox
    )
from tkinter import ttk
import tkinter.scrolledtext

from classes.oppbot_settings import Settings

class OptionsOverlay:
    "Graphical User Interface Options Window for the COH Opponent Bot."

    def __init__(self, main_window, parent_frame):
        "Overlay Options"

        self.main_window = main_window
        self.parent_frame = parent_frame
        self.settings = Settings()

        v = int(bool(self.settings.data.get('enable_overlay')))
        self.intvar_enable_overlay = IntVar(value=v)
        v = int(bool(self.settings.data.get('clearOverlayAfterGameOver')))
        self.intvar_clear_overlay_gameover = IntVar(value=v)

        self.textvar_default_left = StringVar()
        self.textvar_default_right = StringVar()
        self.textvar_1v1_left = StringVar()
        self.textvar_1v1_right = StringVar()
        self.textvar_2v2_left = StringVar()
        self.textvar_2v2_right = StringVar()
        self.textvar_3v3_left = StringVar()
        self.textvar_3v3_right = StringVar()
        self.textvar_4v4_left = StringVar()
        self.textvar_4v4_right = StringVar()
        self.textvar_custom_left = StringVar()
        self.textvar_custom_right = StringVar()
        self.textvar_display = StringVar()


        self.frame = tkinter.LabelFrame(
        self.parent_frame,
        text="Overlay Options",
        padx=5,
        pady=5)

        self.frame.grid()

        # Enable Overlay

        self.check_enable_overlay = tkinter.Checkbutton(
            self.frame,
            text="Enable Overlay",
            variable=self.intvar_enable_overlay,
            command=self.save_toggles)
        self.check_enable_overlay.grid(sticky=W)

        # TextVaribles

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
            if column_number > 5:
                row_number += 1
                column_number = 0
            self.string_format_labels.append(my_label)

        self.frame_overlay_image_icons = tkinter.LabelFrame(
            self.frame,
            text="HTML Overlay Only Image Icons",
            padx=5,
            pady=5)
        self.frame_overlay_image_icons.grid(sticky=N+W+E)

        # create all custom icon variables from dictionary keys

        column_number = 0
        row_number = 0
        iofd = self.settings.imageOverlayFormattingDictionary.items()
        for key, value in iofd:

            my_label_frame = tkinter.LabelFrame(
                self.frame_overlay_image_icons,
                padx=5,
                pady=5)
            self.frame_overlay_image_icons.columnconfigure(
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

        self.check_clear_overlay_after_game = tkinter.Checkbutton(
            self.frame,
            text="Clear overlay after game over",
            variable=self.intvar_clear_overlay_gameover,
            command=self.save_toggles)
        self.check_clear_overlay_after_game.grid(sticky=W)

        # Overlay Preformats

        self.frame_overlay_pf = tkinter.LabelFrame(
                self.frame,
                text="Overlay Preformat Text",
                padx=5,
                pady=5)
        self.frame_overlay_pf.grid()

        self.label_left = tkinter.Label(self.frame_overlay_pf, text="Left - Your Team")
        self.label_left.grid(sticky=W, row=0, column=1)

        self.label_right = tkinter.Label(self.frame_overlay_pf, text="Right - Opponent Team")
        self.label_right.grid(sticky=W, row=0, column=2)


        # Default Label
        self.label_default = tkinter.Label(self.frame_overlay_pf, text="Default")
        self.label_default.grid(sticky=W, row=1, column=0)

        entryWidth = 65

        # Default Left
        self.entry_default_pf_left = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_default_left,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_default_left_pf'):
            self.textvar_default_left.set(
                self.settings.data.get('overlay_default_left_pf'))
        self.entry_default_pf_left.grid(sticky=W, row=1, column=1)

        # Default Right
        self.entry_default_pf_right = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_default_right,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_default_right_pf'):
            self.textvar_default_right.set(
                self.settings.data.get('overlay_default_right_pf'))
        self.entry_default_pf_right.grid(sticky=W, row=1, column=2)

        # button mirror
        self.button_mirror_default_pf = tkinter.Button(
            self.frame_overlay_pf,
            text="Mirror <=>")
        self.button_mirror_default_pf.configure(
            command=lambda : self.mirror_left_right_entry(self.entry_default_pf_right))
        self.button_mirror_default_pf.grid(sticky=E, row=1, column=3)

        # 1v1 Label
        self.label_1v1 = tkinter.Label(self.frame_overlay_pf, text="1v1")
        self.label_1v1.grid(sticky=W, row=2, column=0)

        # 1v1 Left
        self.entry_1v1_pf_left = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_1v1_left,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_1v1_left_pf'):
            self.textvar_1v1_left.set(
                self.settings.data.get('overlay_1v1_left_pf'))
        self.entry_1v1_pf_left.grid(sticky=W, row=2, column=1)

        # 1v1 Right
        self.entry_1v1_pf_right = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_1v1_right,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_1v1_right_pf'):
            self.textvar_1v1_right.set(
                self.settings.data.get('overlay_1v1_right_pf'))
        self.entry_1v1_pf_right.grid(sticky=W, row=2, column=2)

        # button mirror
        self.button_mirror_1v1_pf = tkinter.Button(
            self.frame_overlay_pf,
            text="Mirror <=>")
        self.button_mirror_1v1_pf.configure(
            command=lambda : self.mirror_left_right_entry(self.entry_1v1_pf_right))
        self.button_mirror_1v1_pf.grid(sticky=E, row=2, column=3)

        # 2v2 Label
        self.label_2v2 = tkinter.Label(self.frame_overlay_pf, text="2v2")
        self.label_2v2.grid(sticky=W, row=3, column=0)

        # 2v2 Left
        self.entry_2v2_pf_left = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_2v2_left,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_2v2_left_pf'):
            self.textvar_2v2_left.set(
                self.settings.data.get('overlay_2v2_left_pf'))
        self.entry_2v2_pf_left.grid(sticky=W, row=3, column=1)

        # 2v2 Right
        self.entry_2v2_pf_right = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_2v2_right,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_2v2_right_pf'):
            self.textvar_2v2_right.set(
                self.settings.data.get('overlay_2v2_right_pf'))
        self.entry_2v2_pf_right.grid(sticky=W, row=3, column=2)

        # button mirror
        self.button_mirror_2v2_pf = tkinter.Button(
            self.frame_overlay_pf,
            text="Mirror <=>")
        self.button_mirror_2v2_pf.configure(
            command=lambda : self.mirror_left_right_entry(self.entry_2v2_pf_right))
        self.button_mirror_2v2_pf.grid(sticky=E, row=3, column=3)

        # 3v3 Label
        self.label_3v3 = tkinter.Label(self.frame_overlay_pf, text="3v3")
        self.label_3v3.grid(sticky=W, row=4, column=0)

        # 3v3 Left
        self.entry_3v3_pf_left = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_3v3_left,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_3v3_left_pf'):
            self.textvar_3v3_left.set(
                self.settings.data.get('overlay_3v3_left_pf'))
        self.entry_3v3_pf_left.grid(sticky=W, row=4, column=1)

        # 3v3 Right
        self.entry_3v3_pf_right = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_3v3_right,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_3v3_right_pf'):
            self.textvar_3v3_right.set(
                self.settings.data.get('overlay_3v3_right_pf'))
        self.entry_3v3_pf_right.grid(sticky=W, row=4, column=2)

        # button mirror
        self.button_mirror_3v3_pf = tkinter.Button(
            self.frame_overlay_pf,
            text="Mirror <=>")
        self.button_mirror_3v3_pf.configure(
            command=lambda : self.mirror_left_right_entry(self.entry_3v3_pf_right))
        self.button_mirror_3v3_pf.grid(sticky=E, row=4, column=3)

        # 4v4 Label
        self.label_4v4 = tkinter.Label(self.frame_overlay_pf, text="4v4")
        self.label_4v4.grid(sticky=W, row=5, column=0)

        # 4v4 Left
        self.entry_4v4_pf_left = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_4v4_left,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_4v4_left_pf'):
            self.textvar_4v4_left.set(
                self.settings.data.get('overlay_4v4_left_pf'))
        self.entry_4v4_pf_left.grid(sticky=W, row=5, column=1)

        # 4v4 Right
        self.entry_4v4_pf_right = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_4v4_right,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_4v4_right_pf'):
            self.textvar_4v4_right.set(
                self.settings.data.get('overlay_4v4_right_pf'))
        self.entry_4v4_pf_right.grid(sticky=W, row=5, column=2)

        # button mirror
        self.button_mirror_4v4_pf = tkinter.Button(
            self.frame_overlay_pf,
            text="Mirror <=>")
        self.button_mirror_4v4_pf.configure(
            command=lambda : self.mirror_left_right_entry(self.entry_4v4_pf_right))
        self.button_mirror_4v4_pf.grid(sticky=E, row=5, column=3)

        # Custom Label
        self.label_custom = tkinter.Label(self.frame_overlay_pf, text="Custom")
        self.label_custom.grid(sticky=W, row=6, column=0)

        # Custom Left
        self.entry_custom_pf_left = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_custom_left,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_custom_left_pf'):
            self.textvar_custom_left.set(
                self.settings.data.get('overlay_custom_left_pf'))
        self.entry_custom_pf_left.grid(sticky=W, row=6, column=1)

        # Custom Right
        self.entry_custom_pf_right = tkinter.Entry(
            self.frame_overlay_pf,
            width=entryWidth,
            textvariable=self.textvar_custom_right,
            validate="all",
            validatecommand=self.save_textvars)
        if self.settings.data.get('overlay_custom_right_pf'):
            self.textvar_custom_right.set(
                self.settings.data.get('overlay_custom_right_pf'))
        self.entry_custom_pf_right.grid(sticky=W, row=6, column=2)

        # button mirror
        self.button_mirror_custom_pf = tkinter.Button(
            self.frame_overlay_pf,
            text="Mirror <=>")
        self.button_mirror_custom_pf.configure(
            command=lambda : self.mirror_left_right_entry(self.entry_custom_pf_right))
        self.button_mirror_custom_pf.grid(sticky=E, row=6, column=3)

        # CSS File Location Frame

        self.frame_css_file_path = tkinter.LabelFrame(
            self.frame,
            text="CSS Format Files",
            padx=5,
            pady=5)
        self.frame_css_file_path.grid(sticky=N+W+E)

        # CSS Label Custom

        self.label_css_custom = tkinter.Label(
            self.frame_css_file_path,
            text="Custom CSS Path"
        )
        self.label_css_custom.grid(row=0, column=0, sticky=W)

        # CSS Entry Custom

        self.entry_css_custom = tkinter.Entry(
            self.frame_css_file_path,
            width=49
        )
        self.entry_css_custom.grid(row=0, column=1)

        if(self.settings.data.get('css_style_custom')):
            self.entry_css_custom.insert(
                0,
                str(self.settings.data.get('css_style_custom')))

        self.entry_css_custom.config(state=DISABLED)

        # CSS Browse Button Custom

        self.button_css_custom_path = tkinter.Button(
            self.frame_css_file_path,
            text="Browse",
            command=self.browse_css_custom_path)
        self.button_css_custom_path.config(width=10)
        self.button_css_custom_path.grid(row=0, column=2, sticky=W)

        # CSS Label Ranked

        self.label_css_ranked = tkinter.Label(
            self.frame_css_file_path,
            text="Ranked CSS Path"
        )
        self.label_css_ranked.grid(row=1, column=0, sticky=W)

        # CSS Entry Ranked

        self.entry_css_ranked = tkinter.Entry(
            self.frame_css_file_path,
            width=49
        )
        self.entry_css_ranked.grid(row=1, column=1)

        if(self.settings.data.get('css_style_ranked')):
            self.entry_css_ranked.insert(
                0,
                str(self.settings.data.get('css_style_ranked')))

        self.entry_css_ranked.config(state=DISABLED)

        # CSS Browse Button Ranked

        self.button_css_ranked_path = tkinter.Button(
            self.frame_css_file_path,
            text="Browse",
            command=self.browse_css_ranked_path)
        self.button_css_ranked_path.config(width=10)
        self.button_css_ranked_path.grid(row=1, column=2, sticky=W)

        # CSS Label Unranked

        self.label_css_unranked = tkinter.Label(
            self.frame_css_file_path,
            text="Unranked CSS Path"
        )
        self.label_css_unranked.grid(row=2, column=0, sticky=W)

        # CSS Entry Unranked

        self.entry_css_unranked = tkinter.Entry(
            self.frame_css_file_path,
            width=49
        )
        self.entry_css_unranked.grid(row=2, column=1)

        if(self.settings.data.get('css_style_custom')):
            self.entry_css_unranked.insert(
                0,
                str(self.settings.data.get('css_style_custom')))

        self.entry_css_unranked.config(state=DISABLED)

        # CSS Browse Button Unranked

        self.button_css_unranked_path = tkinter.Button(
            self.frame_css_file_path,
            text="Browse",
            command=self.browse_css_unranked_path)
        self.button_css_unranked_path.config(width=10)
        self.button_css_unranked_path.grid(row=2, column=2, sticky=W)

        # Stats Display PreFormat

        self.frame_stats_pf = tkinter.LabelFrame(
                self.frame,
                text="Stats Display Preformat Text",
                padx=5,
                pady=5)

        self.frame_stats_pf.grid(sticky=N+S+W+E)
        self.frame_stats_pf.grid_rowconfigure(0, weight=1)
        self.frame_stats_pf.grid_columnconfigure(0, weight=1)

        self.textbox_stats_pf = tkinter.Text(
            self.frame_stats_pf,
            height=10)
        self.textbox_stats_pf.grid(sticky="nsew", row=1, column=0, padx=2, pady=2)

        text = ""
        if self.settings.data.get("overlay_display_pf"):
            text = self.settings.data.get("overlay_display_pf")

        self.textbox_stats_pf.insert(END, text)

        # create a Scrollbar and associate it with txt
        scrollbar = ttk.Scrollbar(self.frame_stats_pf, command=self.textbox_stats_pf.yview)
        scrollbar.grid(sticky='nsew', row=1, column=1)
        self.textbox_stats_pf['yscrollcommand'] = scrollbar.set

        # save button

        self.button_save = tkinter.Button(
            self.frame_stats_pf,
            text="Save",
            command=self.save_display
        )
        self.button_save.grid()

        # CSS File Location Stats Frame

        self.frame_css_file_path_display = tkinter.LabelFrame(
            self.frame,
            text="CSS Format File",
            padx=5,
            pady=5)
        self.frame_css_file_path_display.grid(sticky=N+W+E)


        # CSS Label Display

        self.label_css_display = tkinter.Label(
            self.frame_css_file_path_display,
            text="Stat Display CSS Path"
        )
        self.label_css_display.grid(row=3, column=0, sticky=W)

        # CSS Entry Display

        self.entry_css_display_file_path = tkinter.Entry(
            self.frame_css_file_path_display,
            width=49
        )
        self.entry_css_display_file_path.grid(row=3, column=1)

        if(self.settings.data.get('css_style_display')):
            self.entry_css_display_file_path.insert(
                0,
                str(self.settings.data.get('css_style_display')))

        self.entry_css_display_file_path.config(state=DISABLED)

        # CSS Browse Button Display

        self.button_css_custom_path = tkinter.Button(
            self.frame_css_file_path_display,
            text="Browse",
            command=self.browse_css_display_file_path_button)
        self.button_css_custom_path.config(width=10)
        self.button_css_custom_path.grid(row=3, column=2, sticky=W)



    def mirror_left_right_entry(self, entry : tkinter.Entry):
        "toggle mirror left to right overlay."

        # write in the left version mirror
        left_string = entry.get()
        left_list = left_string.split()
        left_list.reverse()
        right_string = " ".join(left_list)
        entry.delete(0, END)
        entry.insert(0, right_string)
        self.save_textvars()

    def save_display(self):
        "save the display text"
        text = self.textbox_stats_pf.get("1.0", END)
        self.settings.data['overlay_display_pf'] = text
        self.settings.save()

    def save_textvars(self):
        "saves the textvars."
        if self.textvar_default_left.get():
            text = self.textvar_default_left.get()
            self.settings.data['overlay_default_left_pf'] = text
        if self.textvar_default_right.get():
            text = self.textvar_default_right.get()
            self.settings.data['overlay_default_right_pf'] = text
        if self.textvar_1v1_left.get():
            text = self.textvar_1v1_left.get()
            self.settings.data['overlay_1v1_left_pf'] = text
        if self.textvar_1v1_right.get():
            text = self.textvar_1v1_right.get()
            self.settings.data['overlay_1v1_right_pf'] = text
        if self.textvar_2v2_left.get():
            text = self.textvar_2v2_left.get()
            self.settings.data['overlay_2v2_left_pf'] = text
        if self.textvar_2v2_right.get():
            text = self.textvar_2v2_right.get()
            self.settings.data['overlay_2v2_right_pf'] = text
        if self.textvar_3v3_left.get():
            text = self.textvar_3v3_left.get()
            self.settings.data['overlay_3v3_left_pf'] = text
        if self.textvar_3v3_right.get():
            text = self.textvar_3v3_right.get()
            self.settings.data['overlay_3v3_right_pf'] = text
        if self.textvar_4v4_left.get():
            text = self.textvar_4v4_left.get()
            self.settings.data['overlay_4v4_left_pf'] = text
        if self.textvar_4v4_right.get():
            text = self.textvar_4v4_right.get()
            self.settings.data['overlay_4v4_right_pf'] = text
        if self.textvar_custom_left.get():
            text = self.textvar_custom_left.get()
            self.settings.data['overlay_custom_left_pf'] = text
        if self.textvar_custom_right.get():
            text = self.textvar_custom_right.get()
            self.settings.data['overlay_custom_right_pf'] = text

        self.settings.save()
        return True  # must return true to a validate entry method

    def browse_css_custom_path(self):
        "browse CSS file path."
        self.main_window.disable_everything()
        cwd = os.getcwd()
        filename = tkinter.filedialog.askopenfilename(
            initialdir=cwd,
            title="Select location of CSS file",
            filetypes=(("css file", "*.css"), ("all files", "*.*")))

        if os.path.isfile(filename):
            filename = os.path.relpath(filename, cwd)
            self.settings.data['css_style_custom'] = filename
            self.entry_css_custom.config(state=NORMAL)
            self.entry_css_custom.delete(0, tkinter.END)
            css_path = self.settings.data.get('css_style_custom')
            if css_path:
                self.entry_css_custom.insert(0, str(css_path))
            self.entry_css_custom.config(state=DISABLED)
            self.settings.save()
        self.main_window.enable_buttons()

    def browse_css_ranked_path(self):
        "browse CSS file path."
        self.main_window.disable_everything()
        cwd = os.getcwd()
        filename = tkinter.filedialog.askopenfilename(
            initialdir=cwd,
            title="Select location of CSS file",
            filetypes=(("css file", "*.css"), ("all files", "*.*")))

        if os.path.isfile(filename):
            filename = os.path.relpath(filename, cwd)
            self.settings.data['css_style_ranked'] = filename
            self.entry_css_ranked.config(state=NORMAL)
            self.entry_css_ranked.delete(0, tkinter.END)
            css_path = self.settings.data.get('css_style_ranked')
            if css_path:
                self.entry_css_ranked.insert(0, str(css_path))
            self.entry_css_ranked.config(state=DISABLED)
            self.settings.save()
        self.main_window.enable_buttons()

    def browse_css_unranked_path(self):
        "browse CSS file path."
        self.main_window.disable_everything()
        cwd = os.getcwd()
        filename = tkinter.filedialog.askopenfilename(
            initialdir=cwd,
            title="Select location of CSS file",
            filetypes=(("css file", "*.css"), ("all files", "*.*")))

        if os.path.isfile(filename):
            filename = os.path.relpath(filename, cwd)
            self.settings.data['css_style_unranked'] = filename
            self.entry_css_unranked.config(state=NORMAL)
            self.entry_css_unranked.delete(0, tkinter.END)
            css_path = self.settings.data.get('css_style_unranked')
            if css_path:
                self.entry_css_unranked.insert(0, str(css_path))
            self.entry_css_unranked.config(state=DISABLED)
            self.settings.save()
        self.main_window.enable_buttons()

    def browse_css_display_file_path_button(self):
        "browse CSS file path."
        self.main_window.disable_everything()
        cwd = os.getcwd()
        filename = tkinter.filedialog.askopenfilename(
            initialdir=cwd,
            title="Select location of CSS file",
            filetypes=(("css file", "*.css"), ("all files", "*.*")))

        if os.path.isfile(filename):
            filename = os.path.relpath(filename, cwd)
            self.settings.data['css_style_display'] = filename
            self.entry_css_display_file_path.config(state=NORMAL)
            self.entry_css_display_file_path.delete(0, tkinter.END)
            css_path = self.settings.data.get('css_style_display')
            if css_path:
                self.entry_css_display_file_path.insert(0, str(css_path))
            self.entry_css_display_file_path.config(state=DISABLED)
            self.settings.save()
        self.main_window.enable_buttons()

    def save_toggles(self):
        "saves all toggles."

        self.settings.data['clearOverlayAfterGameOver'] = (
            bool(self.intvar_clear_overlay_gameover.get()))

        self.settings.data['enable_overlay'] = (
            bool(self.intvar_enable_overlay.get()))

        self.settings.save()
