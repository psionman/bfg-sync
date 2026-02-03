""" Handle standard text for psiutils."""

from copy import copy


psi_strings = {
    'BACKUP': 'Backup',
    'BUILD': 'Build',
    'CANCEL': 'Cancel',
    'CHECK': 'Check',
    'CLEAR': 'Clear',
    'CLOSE': 'Close',
    'CODE': 'Code',
    'COMPARE': 'Compare',
    'CONFIG': 'Config',
    'COPY': 'Copy',
    'DECREMENT_ARROW': '▼',
    'DELETE': 'Delete',
    'DELETE_THESE_ITEMS': 'Are you sure you want to delete these item(s)?',
    'DIFF': 'Diff',
    'DONE': 'Done',
    'DOWNLOAD': 'Download',
    'EDIT': 'Edit',
    'ELLIPSIS': ' ...',
    'EVENT': 'Event',
    'EXIT': 'Exit',
    'HELP': 'Help',
    'INCREMENT_ARROW': '▲',
    'LOGS': 'Logs',
    'NEW': 'New',
    'NEXT': 'Next',
    'NO': 'No',
    'NO_SUCH_FILE': 'no such file or directory',
    'OK': 'OK',
    'OPEN': 'Open',
    'PAUSE': 'Pause',
    'PREFERENCES': 'Preferences',
    'PREVIOUS': 'Prev',
    'PROCESS': 'Process',
    'QUIT': 'Quit',
    'REDO': 'Redo',
    'REFRESH': 'Refresh',
    'REPORT': 'Report',
    'RENAME': 'Rename',
    'RESET': 'Reset',
    'RESTORE': 'Restore',
    'REVERT': 'Revert',
    'RUN': 'Run',
    'SAVE': 'Save',
    'SCRIPT': 'Script',
    'SAVE_PDF': 'Save as PDF',
    'SEARCH': 'Search',
    'SEND': 'Send',
    'START': 'Start',
    'UPDATE': 'Update',
    'UPGRADE': 'Upgrade',
    'UPLOAD': 'Upload',
    'USE': 'Use',
    'WINDOWS': 'Windows',
    'YES': 'Yes',
}

strings = copy(psi_strings)


class Text():
    """Combines package level and psiutils strings."""
    def __init__(self) -> None:
        """
        Initialise the object with attributes based on the key-value pairs
        in the `strings` dictionary.

        Args:
            self: The instance of the class.

        Returns:
            None
        """
        self.strings = strings
        for key, string in strings.items():
            setattr(self, key, string)

        # Optionally display contents of `strings`
    def display(self, compare: dict = None) -> None:
        """Print out contents of `strings` and compare if
        a dict of strings is provided."""
        duplicates = 0
        overrides = 0
        app_strings = 0
        if not compare:
            compare = {}

        for key, item in compare.items():
            if key not in strings:
                strings[key] = item

        for item in sorted(list(strings)):
            output = f'{item:.<20} {strings[item]}'
            if item in compare:
                if strings[item] != compare[item]:
                    output = (f'{output}, {compare[item]} '
                              f'<{"-"*10} //override//')
                    overrides += 1
                elif item not in psi_strings:
                    output = f'{output} <{"="*10} //app string//'
                    app_strings += 1
                else:
                    output = f'{output} <{"="*10} //duplicate//'
                    duplicates += 1
            print(output)

        if duplicates:
            print()
            print(f'{duplicates} duplicates found')

        if overrides:
            print()
            print(f'{overrides} overrides found')

        if app_strings:
            print()
            print(f'{app_strings} application strings found')
