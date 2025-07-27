"""ConfigFrame for bfg-sync."""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

from psiutils.buttons import ButtonFrame, Button
from psiutils.constants import PAD, Pad
from psiutils.utilities import window_resize
from psiutils.widgets import separator_frame, vertical_scroll_bar

from constants import APP_TITLE
from config import read_config, save_config
import text


class ConfigFrame():
    """
    A configuration dialog for editing application settings.

    This class creates a modal top-level window allowing the user to view
    and update configuration values such as file paths and other settings.

    Attributes:
        root (tk.Toplevel): The top-level window for the dialog.
        parent (ModuleCaller): The calling parent object.
        config (Config): The loaded configuration object.
        xxx (tk.StringVar): A Tk variable bound to a configuration value.
        data_directory (tk.StringVar): Tk variable for the data directory path.
        button_frame (ButtonFrame): Frame containing Save/Exit buttons.

    Methods:
        show(): Set up and display the form GUI.
        _main_frame(master): Build the main content frame.
        _button_frame(master): Build the frame containing action buttons.
        _value_changed(): Return True if any config field was modified.
        _enable_buttons(*args): Enable buttons based on config change.
        _get_data_directory(*args): Prompt user to select a directory.
        _save_config(*args): Save changes and exit the dialog.
        dismiss(*args): Close the dialog window.
    """
    def __init__(self, parent: tk.Frame) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = read_config()
        self.packages_text = None
        self.ignore_text = None

        # tk variables
        self.packages = tk.StringVar(value='\n'.join(self.config.packages))
        self.python_version = tk.StringVar(value=self.config.python_version)
        self.development_dir = tk.StringVar(value=self.config.development_dir)
        self.local_pyenv = tk.StringVar(value=self.config.local_env)
        self.remote_pyenv = tk.StringVar(value=self.config.remote_env)
        self.download_dir = tk.StringVar(value=self.config.download_dir)
        self.ignore = tk.StringVar(value='\n'.join(self.config.ignore))

        self.python_version.trace_add('write', self._enable_buttons)
        self.development_dir.trace_add('write', self._enable_buttons)
        self.local_pyenv.trace_add('write', self._enable_buttons)
        self.remote_pyenv.trace_add('write', self._enable_buttons)
        self.download_dir.trace_add('write', self._enable_buttons)

        self.show()

    def show(self) -> None:
        """
        Initialize and display the configuration form GUI.

        This method configures the top-level window, sets up geometry,
        keybindings, resizability, and embeds the main and button frames.
        It also includes a sizegrip widget for manual resizing.

        Keybindings:
            - Ctrl+X: Close the dialog.
            - Ctrl+S: Save configuration and exit.
            - <Configure>: Trigger window size persistence on resize.

        Layout:
            - A main frame with form fields.
            - A button frame with Save and Exit buttons.
            - A sizegrip for resizing support.
        """
        root = self.root
        root.geometry(self.config.geometry[Path(__file__).stem])
        root.transient(self.parent.root)
        root.title(f'{APP_TITLE} - {text.CONFIG}')

        root.bind('<Control-x>', self.dismiss)
        root.bind('<Control-s>', self._save_config)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=8, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        """
        Create and return the main frame containing form input widgets.

        This frame includes:
            - A label describing the input field.
            - An entry widget bound to the data_directory variable.
            - A button to open a directory selection dialog.

        The frame is configured to allow resizing and proper layout behaviour
        using row and column weights.

        Args:
            master (tk.Frame): The parent widget to contain the frame.

        Returns:
            ttk.Frame: The constructed main frame with input controls.
        """
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        row = 0
        separator = separator_frame(frame, 'Development Directory')
        separator.grid(row=row, column=0, columnspan=3,
                       sticky=tk.EW, padx=PAD)

        row += 1
        label = ttk.Label(frame, text='Development directory')
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.development_dir)
        entry.grid(row=row, column=1, sticky=tk.EW)

        button = ttk.Button(
            frame, text=text.ELLIPSIS, command=self._get_development_dir)
        button.grid(row=row, column=2, padx=PAD)

        row += 1
        separator = separator_frame(frame, 'Virtual Environment')
        separator.grid(row=row, column=0, columnspan=3,
                       sticky=tk.EW, padx=PAD)

        row += 1
        label = ttk.Label(frame, text='Local env directory')
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.local_pyenv)
        entry.grid(row=row, column=1, sticky=tk.EW)

        button = ttk.Button(
            frame, text=text.ELLIPSIS, command=self._get_local_env)
        button.grid(row=row, column=2, padx=PAD)

        row += 1
        label = ttk.Label(frame, text='Remote env directory')
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.remote_pyenv)
        entry.grid(row=row, column=1, sticky=tk.EW)

        row += 1
        label = ttk.Label(frame, text='Python version')
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.python_version)
        entry.grid(row=row, column=1, sticky=tk.EW)

        row += 1
        separator = separator_frame(frame, 'Packages')
        separator.grid(row=row, column=0, columnspan=3,
                       sticky=tk.EW, padx=PAD)

        row += 1
        packages = self._packages_frame(frame)
        packages.grid(row=row, column=0, columnspan=2, sticky=tk.NSEW)

        row += 1
        separator = separator_frame(frame, 'Downloads')
        separator.grid(row=row, column=0, columnspan=3,
                       sticky=tk.EW, padx=PAD)

        row += 1
        label = ttk.Label(frame, text='Local download directory')
        label.grid(row=row, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.download_dir)
        entry.grid(row=row, column=1, sticky=tk.EW)

        button = ttk.Button(
            frame, text=text.ELLIPSIS, command=self._get_local_dir)
        button.grid(row=row, column=2, padx=PAD)

        row += 1
        separator = separator_frame(frame, 'Ignore')
        separator.grid(row=row, column=0, columnspan=3,
                       sticky=tk.EW, padx=PAD)

        row += 1
        ignore = self._ignore_frame(frame)
        ignore.grid(row=row, column=0, columnspan=2, sticky=tk.NSEW)

        row += 1
        comparison = self._comparison_frame(frame)
        comparison.grid(row=row, column=0, columnspan=2, sticky=tk.NSEW)

        return frame

    def _packages_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        packages_text = tk.Text(frame, height=10, width=10)
        packages_text.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
        packages_text.insert('0.0', self.packages.get())
        packages_text.bind('<KeyRelease>', self._enable_buttons)
        self.packages_text = packages_text

        v_scroll = vertical_scroll_bar(frame, packages_text)
        v_scroll.grid(row=0, column=2, sticky=tk.NS)
        return frame

    def _ignore_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        ignore_text = tk.Text(frame, height=10, width=10)
        ignore_text.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
        ignore_text.insert('0.0', self.ignore.get())
        ignore_text.bind('<KeyRelease>', self._enable_buttons)
        self.ignore_text = ignore_text

        v_scroll = vertical_scroll_bar(frame, ignore_text)
        v_scroll.grid(row=0, column=2, sticky=tk.NS)
        return frame

    def _comparison_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        return frame


    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        """
        Create and return the button frame for the form.

        This frame contains two buttons:
            - 'Save' to store the current configuration and exit.
            - 'Exit' to close the window without saving changes.

        The buttons are initially disabled and will be enabled based on user
        interaction. The frame is laid out horizontally.

        Args:
            master (tk.Frame): The parent widget that will contain the frame.

        Returns:
            tk.Frame: The constructed frame containing the control buttons.
        """
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            Button(
                frame,
                text=text.SAVE,
                command=self._save_config,
                underline=0,
                dimmable=True),
            Button(
                frame,
                text=text.EXIT,
                command=self.dismiss,
                sticky=tk.E,
                underline=1),
        ]
        frame.enable(False)
        return frame

    def _get_development_dir(self, *args) -> None:
        self._get_directory(self.development_dir)

    def _get_local_env(self, *args) -> None:
        self._get_directory(self.local_pyenv)

    def _get_local_dir(self, *args) -> None:
        self._get_directory(self.download_dir)

    def _get_directory(self, string_var: tk.StringVar) -> None:
        this_dir = filedialog.askdirectory(
            initialdir=Path(string_var.get()),
            parent=self.root,
        )
        if this_dir:
            string_var.set(this_dir)

    def _value_changed(self) -> bool:
        """
        Determine whether any configuration value has changed.

        Compares the current state of the form's variables with the saved
        configuration to identify changes made by the user.

        Returns:
            bool: True if at least one value has been altered; False otherwise.
        """
        return (
            self.packages.get() != self.packages_text.get('0.0', tk.END) or
            self.ignore.get() != self.ignore_text.get('0.0', tk.END) or
            self.python_version.get() != self.config.python_version or
            self.development_dir.get() != self.config.development_dir or
            self.local_pyenv.get() != self.config.local_env or
            self.remote_pyenv.get() != self.config.remote_env or
            self.download_dir.get() != self.config.download_dir or
            ...
        )

    def _enable_buttons(self, *args) -> None:
        """
        Enable or disable form buttons based on changes in configuration.

        Checks whether any tracked values have changed and enables the form's
        buttons accordingly to allow the user to save or exit.
        """
        enable = bool(self._value_changed())
        self.button_frame.enable(enable)

    def _save_config(self, *args) -> None:
        """
        Save the current configuration and close the application window.

        Updates the configuration with values from the form, writes them to
        persistent storage, and then closes the config window.
        """
        # To generate assignments from tk-vars run script: assignment-invert
        self.config.update('python_version', self.python_version.get())
        self.config.update('development_dir', self.development_dir.get())
        self.config.update('download_dir', self.download_dir.get())
        self.config.update('local_env', self.local_pyenv.get())
        self.config.update('remote_env', self.remote_pyenv.get())
        packages = [
            item for item in self.packages_text.get('0.0', tk.END).split('\n')
            if item]
        self.config.update('packages', sorted(packages))
        ignore = [
            item for item in self.ignore_text.get('0.0', tk.END).split('\n')
            if item]
        self.config.update('ignore', sorted(ignore))
        save_config(self.config)
        self.dismiss()

    def dismiss(self, *args) -> None:
        """
        Close the configuration window and terminate the application.

        Destroys the top-level window associated with the configuration form.
        """
        self.root.destroy()
