from pathlib import Path
import paramiko
from stat import S_ISDIR
from dateutil.parser import parse
# from termcolor import ic, colored
import socket
import datetime
import json
from io import BytesIO

from comparison import FileData
# from common import handle_error
# from constants import ERROR_COLOUR, INFO_COLOUR

ERROR_COLOUR, INFO_COLOUR = 1, 2

TIMEOUT = 5
IGNORE_DIRS = ['.git', '.vscode', '__pycache__', 'locale', 'tests']

MODULE_COLOUR = 'blue'


class FtpConnection(paramiko.SSHClient):
    def __init__(self, config):
        super().__init__()

        self.config = config
        self.load_system_host_keys()
        self._make_connection()
        self.sftp = self.open_sftp()

    def _make_connection(self):
        ic(f'Connecting to remote server: {self.config.host_name} ...',
               INFO_COLOUR)
        # ic(f'{self.config.host_name=}', INFO_COLOUR)
        # ic(f'{self.config.port=}', INFO_COLOUR)
        # ic(f'{self.config.username=}', INFO_COLOUR)
        # ic(f'{self.config.private_key_file=}', INFO_COLOUR)

        private_key_file = Path(Path.home(), *self.config.private_key_file)
        try:
            self.connect(hostname=self.config.host_name, port=self.config.port,
                         username=self.config.username,
                         key_filename=str(private_key_file),
                         timeout=TIMEOUT)
        except FileNotFoundError:
            handle_error('No host keys file', private_key_file)
        except ValueError:
            handle_error('Invalid username', self.config.username)
        except socket.gaierror:
            handle_error('Invalid hostname:', self.config.host_name)
        except socket.timeout:
            handle_error('Socket timeout. Incorrect port?', self.config.port)
        except paramiko.ssh_exception.BadHostKeyException as err:
            handle_error('', err)
        except paramiko.ssh_exception.SSHException as err:
            handle_error('', err)

    def close_connection(self):
        # try:
        self.sftp.close()
        ic('Connection closed', INFO_COLOUR)
        # except:
        #     ic('Connection failed to closed', ERROR_COLOUR)
        #     ic(f'{sys.exc_info()[0]}', ERROR_COLOUR)

    def file_data(self):
        dirs = {}
        dir_list = self._get_dir_list()
        for dir in dir_list:
            mode = dir.st_mode
            if S_ISDIR(mode):
                attrs = dir.__str__().split()
                dir_name = attrs[8]
                ignore = self.ignore_dir(dir_name)
                if not ignore:
                    files = self._get_files_in_dir(dir_name)
                    dirs[dir_name] = files
        return dirs

    def _get_dir_list(self):
        try:
            dir_list = self.sftp.listdir_attr(self.config.remote_dir)
            return dir_list
        except FileNotFoundError:
            ic(f'No remote dir: {self.config.remote_dir}', ERROR_COLOUR)
            self.shutting_down()

    def _get_files_in_dir(self, dir_name):
        files = {}
        files_list = self.sftp.listdir(f'{self.config.remote_dir}/{dir_name}')
        for file in files_list:
            if file.endswith('.py'):
                path = f'{self.config.remote_dir}/{dir_name}/{file}'
                file_stats = self.sftp.stat(path)
                file_attrs = file_stats.__str__().split()
                date = parse(
                        f'{file_attrs[5]} {file_attrs[6]} {file_attrs[7]}'
                    )
                flo = BytesIO()
                self.sftp.getfo(path, flo)
                text = flo.getvalue().decode("utf-8")
                content = text.split('\n')
                file_data = FileData(path, file, date, content)
                files[file] = file_data
        return files

    @staticmethod
    def ignore_dir(dir_name):
        for ignore_dir in IGNORE_DIRS:
            if ignore_dir in dir_name:
                return True
        return False

    def sync_files(self, modified_items, remote_dirs, packages):
        self.download_files(modified_items, packages)
        self.upload_files(modified_items, remote_dirs)

    def upload_files(self, modified_items, remote_dirs):
        print('')
        print(ic('Uploading: ', INFO_COLOUR), end='')
        for item in modified_items:
            if item.dir not in remote_dirs:
                self.sftp.mkdir(f'{self.config.remote_dir}/{item.dir}')
            local_file = f'{self.config.local_dir}/{item.dir}/{item.name}'
            remote_file = f'{self.config.remote_dir}/{item.dir}/{item.name}'
            self.sftp.put(local_file, remote_file)
            print(ic('.', INFO_COLOUR), end='')
        print('')

    def download_files(self, modified_items, packages):
        print('')
        backup_dir = self._get_backup_dir()
        if not Path(backup_dir).is_dir():
            ic()
            Path(backup_dir).mkdir()

        print(f'Downloading backup to: {backup_dir} ', INFO_COLOUR, end='')
        for item in modified_items:
            if not Path(backup_dir, item.dir).is_dir():
                Path(backup_dir, item.dir).mkdir()
            local_file = Path(backup_dir, item.dir, item.name)
            remote_file = f'{self.config.remote_dir}/{item.dir}/{item.name}'
            self.sftp.get(remote_file, local_file)
            print(ic('.', INFO_COLOUR), end='')
        with open(Path(backup_dir, 'packages.json'), 'w') as f_packages:
            json.dump(packages, f_packages)
        print('')
        print('')

    def _get_backup_dir(self) -> str:
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        backup_dir = str(Path(Path.home(), *self.config.backup_dir))
        backup_dir = backup_dir.replace('YYYYMMDD', date_str)
        while Path(backup_dir).is_dir():
            for index, letter in enumerate(backup_dir[::-1]):
                if letter == '_':
                    file_number = int(backup_dir[len(backup_dir)-index:]) + 1
                    backup_dir = (
                        f'{backup_dir[:len(backup_dir)-index]}'
                        f'{file_number}'
                    )
                    break
        return backup_dir

    def shutting_down(self):
        print('Shutting down')
        self.close()

    @property
    def handle_error(message, value):
        ic(f'{message}: {value}', ERROR_COLOUR)
        ic('Shutting down ...', ERROR_COLOUR)
        sys.exit()
