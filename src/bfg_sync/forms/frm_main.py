
"""MainFrame for bfg-sync."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from datetime import datetime
import subprocess

from dataclasses import dataclass

from psiutils.constants import PAD
from psiutils.buttons import ButtonFrame, Button
from psiutils.utilities import window_resize
from psiutils.widgets import separator_frame, WaitCursor, vertical_scroll_bar
from psiutils.treeview import sort_treeview
from psiutils.menus import Menu, MenuItem

from constants import APP_TITLE
from config import read_config, save_config
import text

from comparison import Comparison

from main_menu import MainMenu

FRAME_TITLE = APP_TITLE

TREE_COLUMNS = (
    ('dir', 'Directory', 200),
    ('file', 'File name', 300),
)


class MainFrame():
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = read_config()
        self.comparison_frame = None
        self.tree = None
        self.selected_item = None
        self.button_frame = None
        self.selected_values = None

        self.mismatch = 'mismatch'
        if not self.config.last_download:
            self.config.last_download = 'Not downloaded'

        self.comparison = Comparison()
        print(f'{self.comparison.last_download=}')

        # tk variables
        self.use_ignore = tk.BooleanVar(value=True)
        self.show_only_mismatches = tk.BooleanVar(value=True)
        self.last_download = tk.StringVar(value=self.comparison.last_download)
        self.download_dir = tk.StringVar(value=self.config.download_dir)

        self.show()
        self.context_menu = self._context_menu()

        self._populate_tree()
        # self.show_only_mismatches.set(False)

    def show(self):
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.title(FRAME_TITLE)

        root.bind('<Control-x>', self.dismiss)
        root.bind('<Control-o>', self._process)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        main_menu = MainMenu(self)
        main_menu.create()

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)

        package_frame = self._package_frame(frame)
        package_frame.grid(row=0, column=0, sticky=tk.W)

        comparison_frame = self._comparison_frame(frame)
        comparison_frame.grid(row=1, column=0, sticky=tk.W)

        control_frame = self._control_frame(frame)
        control_frame.grid(row=1, column=1, rowspan=9, sticky=tk.NS)

        return frame

    def _package_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)

        row = 0
        separator = separator_frame(frame, 'Package Versions')
        separator.grid(row=row, column=0, columnspan=3,
                       sticky=tk.EW, padx=PAD)

        row += 1
        label = ttk.Label(frame, text='Package')
        label.grid(row=row, column=0, sticky=tk.W, padx=PAD)
        label = ttk.Label(frame, text='Local')
        label.grid(row=row, column=1, sticky=tk.W, padx=PAD)
        label = ttk.Label(frame, text='Remote')
        label.grid(row=row, column=2, sticky=tk.W, padx=PAD)

        local_packages = self.comparison.local_versions
        remote_packages = self.comparison.remote_versions
        for package in self.config.packages:
            row += 1
            label = ttk.Label(frame, text=package)
            label.grid(row=row, column=0, sticky=tk.W, padx=PAD)

            style = 'red-fg.TLabel'
            local_version = 'Missing'
            if package in local_packages:
                local_version = local_packages[package]
                style = ''
            label = ttk.Label(frame, text=local_version, style=style)
            label.grid(row=row, column=1, sticky=tk.E, padx=PAD)

            style = 'red-fg.TLabel'
            remote_version = 'Missing'
            if package in remote_packages:
                remote_version = remote_packages[package]
                style = ''
                if local_version != remote_version:
                    style = 'orange-fg.TLabel'
            label = ttk.Label(frame, text=remote_version, style=style)
            label.grid(row=row, column=2, sticky=tk.E, padx=PAD)

        return frame

    def _comparison_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        row = 0
        separator = separator_frame(frame, 'File comparison')
        separator.grid(row=row, column=0, columnspan=4,
                       sticky=tk.EW, padx=PAD)

        row += 1
        label = ttk.Label(frame, text='Download dir')
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        label = ttk.Label(
            frame,
            textvariable=self.download_dir,
            borderwidth=1,
            relief=tk.SUNKEN)
        label.grid(row=row, column=1, sticky=tk.EW, padx=PAD, pady=PAD)

        row += 1
        label = ttk.Label(frame, text='Last downloaded')
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        label = ttk.Label(
            frame,
            textvariable=self.last_download,
            borderwidth=1,
            relief=tk.SUNKEN)
        label.grid(row=row, column=1, sticky=tk.W, padx=PAD, pady=PAD)

        row += 1
        check_button = ttk.Checkbutton(
            frame,
            text='Show only mismatches',
            variable=self.show_only_mismatches,
            command=self._populate_tree)
        check_button.grid(row=row, column=0, sticky=tk.W)

        row += 1
        self.tree = self._get_tree(frame)
        self.tree.grid(row=row, column=0, columnspan=2, sticky=tk.NSEW)
        self._populate_tree()

        v_scroll = vertical_scroll_bar(frame, self.tree)
        v_scroll.grid(row=row, column=2, sticky=tk.NS)

        return frame

    def _control_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(1, weight=1)

        row = 0
        check_button = ttk.Checkbutton(
            frame, text='Use ignore', variable=self.use_ignore)
        check_button.grid(row=row, column=0, sticky=tk.W)

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(row=1, column=0,
                               sticky=tk.NS, padx=PAD, pady=PAD)

        return frame

    def _get_tree(self, master: tk.Frame) -> ttk.Treeview:
        """Return  a tree widget."""
        tree = ttk.Treeview(
            master,
            selectmode='browse',
            height=15,
            show='headings',
            )
        tree.bind('<<TreeviewSelect>>', self._tree_clicked)
        tree.bind('<Button-3>', self._show_context_menu)

        col_list = tuple([col[0] for col in TREE_COLUMNS])
        tree['columns'] = col_list
        for col in TREE_COLUMNS:
            (col_key, col_text, col_width) = (col[0], col[1], col[2])
            tree.heading(col_key, text=col_text,
                         command=lambda c=col_key:
                         sort_treeview(tree, c, False))
            tree.column(col_key, width=col_width, anchor=tk.W)
        # tree.column(<'right-align-column-name'>, stretch=0, anchor=tk.E)
        return tree

    def _populate_tree(self, *args) -> None:
        self.last_download.set(self.comparison.last_download)
        self.tree.delete(*self.tree.get_children())
        style = ttk.Style()
        style.map(
            'Treeview',
            background=self._fixed_map(style, 'background'))
        self.tree.tag_configure('mismatch', background='pink')
        self.tree.tag_configure('match', background='white')

        comparison = self.comparison.compare_files(self.use_ignore.get())
        for key, item in comparison.items():
            if not item['match'] or not self.show_only_mismatches.get():
                tag = 'match'
                if not item['match']:
                    tag = 'mismatch'
                values = key.split(':')
                self.tree.insert('', 'end', values=values, tags=(tag,))

    @staticmethod
    def _fixed_map(style, option):
        return [elm for elm in style.map("Treeview", query_opt=option)
                if elm[:2] != ("!disabled", "!selected")]

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        buttons = [
            ButtonDefn(text.REFRESH, self._populate_tree, dimmable=False),
            ButtonDefn(text.DOWNLOAD, self._download, dimmable=False),
            ButtonDefn(text.COMPARE, self._compare),
            ButtonDefn(text.EXIT, self.dismiss,
                       sticky=tk.S, underline=1, dimmable=False),
        ]
        return ButtonBuilder(master, buttons, tk.VERTICAL)

    def _download(self, *args) -> None:
        with WaitCursor(self.root):
            self.comparison.download_remote_files(self.use_ignore.get())
            self.last_download.set(
                datetime.now().strftime('%d %B %Y %H:%M:%S'))
            self.config.update('last_download', self.last_download.get())
            save_config(self.config)

    def _tree_clicked(self, *args) -> None:
        self.selected_item = self.tree.selection()
        self.button_frame.enable()
        self.context_menu.enable()
        self.selected_values = self.tree.item(self.selected_item)['values']

    def _show_context_menu(self, event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)
        selected_item = self.tree.identify_row(event.y)
        self.tree.selection_set(selected_item)

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem(text.COMPARE, self._compare, dimmable=True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _compare(self, *args) -> None:
        directory = self.selected_values[0]
        file = self.selected_values[1]
        paths = [
            str(Path(self.config.development_dir, directory, file)),
            str(Path(self.config.download_dir, directory, file)),
        ]
        self.root.withdraw()
        subprocess.run(['meld', *paths])
        self.root.deiconify()

    def _process(self, *args) -> None:
        ...

    def dismiss(self, *args) -> None:
        """
        Close the main window and terminate the application.

        Destroys the top-level window associated with the application.
        """
        self.root.destroy()


class ButtonBuilder(ButtonFrame):
    """Class for building psiutils ButtonFrame."""
    def __init__(
            self,
            master: ttk.Frame,
            button_definitions: list,
            orientation: int = tk.HORIZONTAL) -> None:
        super().__init__(master, orientation=orientation)

        buttons = []
        for button in button_definitions:
            buttons.append(
                Button(
                    self,
                    text=button.text,
                    command=button.command,
                    underline=button.underline,
                    dimmable=button.dimmable,
                    sticky=button.sticky,
                )
            )
        self.buttons = buttons
        self.enable(False)


@dataclass(unsafe_hash=True)
class ButtonDefn:
    """Class for defining psiutils button attributes."""
    text: str
    command: object
    underline: int = 0
    sticky: int = tk.W
    dimmable: bool = True
