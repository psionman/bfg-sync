
from functools import partial
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from dateutil.parser import parse

from text import Text

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


class DatePicker(tk.Frame):
    def __init__(
            self, master: tk.Frame,
            initial_date: datetime = None,
            date_format: str = ''):
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
        return parse(self._date_input.get())

    def _date_increment(
            self,
            textvariable: tk.StringVar,
            increment: int = 1, *args) -> None:
        date = parse(textvariable.get(), dayfirst=True).date()
        new_date = date + timedelta(days=increment)
        textvariable.set(new_date.strftime(DATE_FORMAT))


class TimePicker(tk.Frame):
    def __init__(
            self, master: tk.Frame,
            use_seconds: bool = False,
            use_labels: bool = False):
        super().__init__(master)
        self.use_seconds = use_seconds
        self.use_labels = use_labels

        self._hour_input = tk.StringVar(value='00')
        self._minute_input = tk.StringVar(value='00')
        self._second_input = tk.StringVar(value='00')

        style = ttk.Style()
        style.configure('Increment.TButton', font=('Helvetica', 8))

        main_frame = self._picker()
        main_frame.grid(row=0, column=0)

    def _picker(self) -> tk.Frame:
        frame = ttk.Frame(self)

        column = 0
        row = 0
        if self.use_labels:
            label = ttk.Label(frame, text='Hour')
            label.grid(row=row, column=column, sticky=tk.W)

            label = ttk.Label(frame, text='Mins')
            label.grid(row=row, column=column+1, sticky=tk.W)

            if self.use_seconds:
                label = ttk.Label(frame, text='Secs')
                label.grid(row=row, column=column+5, sticky=tk.E)

        row += 1
        hour_timer = self._timer_element(frame, self._hour_input, MAX_HOURS)
        hour_timer.grid(row=row, column=column)

        column += 1
        minute_timer = self._timer_element(frame, self._minute_input)
        minute_timer.grid(row=row, column=column)

        if self.use_seconds:
            column += 1
            second_timer = self._timer_element(frame, self._second_input)
            second_timer.grid(row=row, column=column)

        return frame

    def _timer_element(
            self,
            master: tk.Frame,
            textvariable: tk.StringVar,
            max_value: int = MAX_MINS,
            ) -> tk.Frame:
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
        value = int(textvariable.get()) + increment
        if value < 0:
            value = max_value
        if value > max_value:
            value = 0
        textvariable.set(f'{value:02d}')

    @property
    def time(self) -> datetime:
        return datetime(
            hours=int(self._hour_input.get()),
            minutes=int(self._minute_input.get()),
            seconds=int(self._second_input.get()),
            )
