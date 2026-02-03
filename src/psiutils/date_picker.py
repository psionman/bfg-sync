"""
    Implement DayPicker an TimePicker widgets for psiutils.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from dataclasses import dataclass
from functools import partial
from tkcalendar import DateEntry
from dateutil.parser import parse

from psiutils.text import Text

txt = Text()

PAD = 2
TIME_WIDTH = 3
INCREMENT_BUTTON_SIZE = 2
INCREMENT_BUTTON_FONT_SIZE = 8
DATE_FORMAT = '%d/%m/%Y'
PICKER_DATE_PATTERN = 'dd/mm/yyyy'
MAX_HOURS = 23
MAX_MINS = 59
TALL_COMBO_PADDING = 6

HOUR_COL = 0
MINUTE_COL = 1
SECOND_COL = 2


class DatePicker(tk.Frame):
    """
    A Tkinter widget for selecting a date using a calendar picker
    with increment and decrement controls.

    The widget displays a date entry field backed by a StringVar and
    allows the user to adjust the selected date one day at a time
    using arrow buttons.

    Example:
        picker = DatePicker(root)
        picker.pack()

        selected_date = picker.date
    """
    def __init__(
            self, master: tk.Frame,
            initial_date: datetime = None,
            date_format: str = ''):
        """
        Initialize the DatePicker widget.

        Args:
            master (tk.Frame): Parent widget.
            initial_date (datetime, optional): Initial date to display.
                Defaults to the current date.
            date_format (str, optional): Format string used to display
                the date. Defaults to DATE_FORMAT.
        """
        super().__init__(master)
        if not initial_date:
            initial_date = datetime.now()
        if not date_format:
            date_format = DATE_FORMAT

        self._date_input = tk.StringVar(
            value=initial_date.strftime(DATE_FORMAT))

        style = ttk.Style()
        style.configure(
            'Increment.TButton',
            font=('Helvetica', INCREMENT_BUTTON_FONT_SIZE),
            padding=0,)
        style.configure('Tall.TCombobox', padding=TALL_COMBO_PADDING)

        main_frame = self._picker()
        main_frame.pack()

    def _picker(self) -> tk.Frame:
        """
        Create and layout the main date picker UI.

        Returns:
            tk.Frame: The populated frame containing the date entry
            and increment/decrement buttons.
        """
        frame = ttk.Frame(self)

        column = 0
        date_picker = self._date_picker(frame, self._date_input)
        date_picker.grid(row=0, column=column, rowspan=2, sticky=tk.NS)

        column += 1
        button = ttk.Button(
            frame,
            text=txt.INCREMENT_ARROW,
            command=partial(self._date_increment, self._date_input),
            width=INCREMENT_BUTTON_SIZE,
            style='Increment.TButton',
            )
        button.grid(row=0, column=column, padx=PAD)

        button = ttk.Button(
            frame,
            text=txt.DECREMENT_ARROW,
            command=partial(self._date_increment, self._date_input, -1),
            width=INCREMENT_BUTTON_SIZE,
            style='Increment.TButton',
            )
        button.grid(row=1, column=column, padx=PAD)

        column += 1

        return frame

    def _date_picker(
            self, master: tk.Frame, textvariable: tk.StringVar) -> DateEntry:
        """
        Create a calendar-based date entry widget.

        Args:
            master (tk.Frame): Parent container.
            textvariable (tk.StringVar): Variable bound to the selected date.

        Returns:
            DateEntry: A configured calendar date entry widget.
        """
        event_date = datetime.now()
        return DateEntry(
            master,
            date_pattern=PICKER_DATE_PATTERN,
            year=event_date.year,
            month=event_date.month,
            day=event_date.day,
            textvariable=textvariable,
            )

    @property
    def date(self) -> datetime:
        """
        Get the currently selected date.

        Returns:
            datetime: The selected date parsed from the input field.
        """
        return parse(self._date_input.get())

    @date.setter
    def date(self, value: datetime) -> None:
        """
        Set the currently selected date.
        """
        self._date_input.set(value.strftime(DATE_FORMAT))

    def _date_increment(
            self,
            textvariable: tk.StringVar,
            increment: int = 1,
            ) -> None:
        """
        Increment or decrement the selected date by a number of days.

        Args:
            textvariable (tk.StringVar): The date value to update.
            increment (int): Number of days to add or subtract.
                Defaults to 1.
        """
        date = parse(textvariable.get(), dayfirst=True).date()
        new_date = date + timedelta(days=increment)
        textvariable.set(new_date.strftime(DATE_FORMAT))


@dataclass
class Time():
    """
    Simple value object representing a time selection.

    Attributes:
        hour (int): Hour value (0-24).
        minute (int): Minute value (0-59).
        second (int): Second value (0-59).
    """
    hour: int = 0
    minute: int = 0
    second: int = 0

    def on(self, date: datetime) -> datetime:
        """Return a datetime by applying this time to the given date."""
        return datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
        )


DAY_START = Time(0, 0, 0)
MIDNIGHT = Time(23, 59, 59)


class TimePicker(tk.Frame):
    """
    A Tkinter widget for selecting a time using comboboxes and
    increment/decrement buttons.

    The widget supports hours and minutes by default, with optional
    seconds and optional column labels.

    Example:
        picker = TimePicker(root, use_seconds=True, use_labels=True)
        picker.pack()

        selected_time = picker.time
        print(selected_time.hour, selected_time.minute, selected_time.second)
    """
    def __init__(
            self,
            master: tk.Frame,
            time: Time = Time(0, 0, 0),
            use_seconds: bool = False,
            use_labels: bool = False):
        """
        Initialize the TimePicker widget.

        Args:
            master (tk.Frame): Parent widget.
            time (Time): The initial time setting (hour, minute, second)
            use_seconds (bool): Whether to include a seconds selector.
            use_labels (bool): Whether to show labels above each selector.
        """
        super().__init__(master)
        self.use_seconds = use_seconds
        self.use_labels = use_labels

        self._hour_input = tk.StringVar(value=f'{time.hour:02d}')
        self._minute_input = tk.StringVar(value=f'{time.minute:02d}')
        self._second_input = tk.StringVar(value=f'{time.second:02d}')

        style = ttk.Style()
        style.configure('Increment.TButton', font=('Helvetica', 8))

        main_frame = self._picker()
        main_frame.grid(row=0, column=0)

    def _picker(self) -> tk.Frame:
        """
        Create and layout the main picker UI.

        Returns:
            tk.Frame: The populated frame containing the time controls.
        """
        frame = ttk.Frame(self)

        row = 0
        if self.use_labels:
            row = self._label_row(frame, row)

        hour_timer = self._timer_element(frame, self._hour_input, MAX_HOURS)
        hour_timer.grid(row=row, column=HOUR_COL)

        minute_timer = self._timer_element(frame, self._minute_input)
        minute_timer.grid(row=row, column=MINUTE_COL)

        if self.use_seconds:
            second_timer = self._timer_element(frame, self._second_input)
            second_timer.grid(row=row, column=SECOND_COL)

        return frame

    def _label_row(self, frame: tk.Frame, row: int) -> int:
        """
        Create and place the label row for the time picker.

        Adds column headers for hours and minutes, and optionally seconds,
        aligned with their corresponding timer controls.

        Args:
            frame (tk.Frame): The parent container in which the labels are placed.
            row (int): The grid row index to place the labels on.

        Returns:
            int: The row index used for the labels (unchanged).
        """
        label = ttk.Label(frame, text='Hour')
        label.grid(row=row, column=HOUR_COL, sticky=tk.W)

        label = ttk.Label(frame, text='Mins')
        label.grid(row=row, column=MINUTE_COL, sticky=tk.W)

        if self.use_seconds:
            label = ttk.Label(frame, text='Secs')
            label.grid(row=row, column=SECOND_COL, sticky=tk.E)
        return row + 1

    def _timer_element(
            self,
            master: tk.Frame,
            textvariable: tk.StringVar,
            max_value: int = MAX_MINS,
            ) -> tk.Frame:
        """
        Create a single timer control consisting of a combobox and
        increment/decrement buttons.

        Args:
            master (tk.Frame): Parent container.
            textvariable (tk.StringVar): Variable bound to the combobox value.
            max_value (int): Maximum allowed value (wraps around).

        Returns:
            tk.Frame: The assembled timer element.
        """
        frame = ttk.Frame(master)
        column = 0

        combobox = ttk.Combobox(
            frame,
            textvariable=textvariable,
            values=[f'{x:02d}' for x in range(max_value+1)],
            width=TIME_WIDTH,
            style='Tall.TCombobox',
            )
        combobox.grid(row=0, column=column, rowspan=2, sticky=tk.W)

        column += 1

        button = ttk.Button(
            frame,
            text=txt.INCREMENT_ARROW,
            command=partial(self._time_increment, textvariable, 1, max_value),
            width=INCREMENT_BUTTON_SIZE,
            style='Increment.TButton',
            )
        button.grid(row=0, column=column, padx=PAD)

        button = ttk.Button(
            frame,
            text=txt.DECREMENT_ARROW,
            command=partial(self._time_increment, textvariable, -1, max_value),
            width=INCREMENT_BUTTON_SIZE,
            style='Increment.TButton',
            )
        button.grid(row=1, column=column, padx=PAD)
        return frame

    def _time_increment(
            self,
            textvariable: tk.StringVar,
            increment,
            max_value) -> None:
        """
        Increment or decrement a time value with wrap-around behavior.

        Args:
            textvariable (tk.StringVar): The value to update.
            increment (int): Amount to add (usually ±1).
            max_value (int): Maximum allowed value.
        """
        value = int(textvariable.get()) + increment
        if value < 0:
            value = max_value
        if value > max_value:
            value = 0
        textvariable.set(f'{value:02d}')

    @property
    def time(self) -> Time:
        """
        Get the currently selected time as a Time object.

        Returns:
            Time: The selected hour, minute, and second values.
        """
        return Time(self.hour, self.minute, self.second)

    @time.setter
    def time(self, value: Time) -> None:
        """
        Set the currently selected time.
        """
        self._hour_input.set(f'{value.hour:02d}')
        self._minute_input.set(f'{value.minute:02d}')
        self._second_input.set(f'{value.second:02d}')

    @property
    def hour(self) -> int:
        """Return the selected hour value."""
        return int(self._hour_input.get())

    @property
    def minute(self) -> int:
        """Return the selected minute value."""
        return int(self._minute_input.get())

    @property
    def second(self) -> int:
        """Return the selected second value."""
        return int(self._second_input.get())

    def on(self, date: datetime) -> datetime:
        """Return a datetime by applying this time to the given date."""
        return datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
        )
