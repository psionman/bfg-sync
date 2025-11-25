
from pathlib import Path
import contextlib
import os
import paramiko
import socket
from stat import S_ISDIR, S_ISREG
from dotenv import load_dotenv

from bfg_sync import logger

load_dotenv()


class SSHServer:
    def __init__(self):
        self.hostname = os.getenv('HOSTNAME')
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        self.port = os.getenv('PORT')
        self.key_filename = os.getenv('PRIVATE_KEY_FILE')
        self.known_hosts_file_name = os.getenv('KNOWN_HOSTS')
        self._ssh_client = None

    def get_ssh_client(self):
        if (self._ssh_client is None
                or self._ssh_client.get_transport() is None):
            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            self._ssh_client.connect(
                hostname=self.hostname,
                username=self.username,
                key_filename=self.key_filename,
                known_hosts_file_name=self.known_hosts_file_name)
        return self._ssh_client

    def get_sftp(self):
        return self.get_ssh_client().open_sftp()

    @property
    def ssh_client(self):
        return

    def execute_remote_command(self, command: str) -> str:
        if ssh_client := get_ssh_client():
            _stdin, _stdout, _stderr = ssh_client.exec_command(command)
            if _stderr.read().decode():
                print(f'Server side error: {_stderr.read().decode()}')
            ssh_client.close()
            return _stdout.read().decode()
        return ''


# def get_ssh_client() -> paramiko.client.SSHClient:
#     ssh_client = paramiko.client.SSHClient()
#     ssh_client.load_host_keys(known_hosts_file_name)
#     ssh_client.set_missing_host_key_policy(paramiko.RejectPolicy())
#     try:
#         ssh_client.connect(
#             hostname=hostname,
#             username=username,
#             port=port,
#             key_filename=key_filename,
#             auth_timeout=5,
#             )
#         return ssh_client
#     except paramiko.ssh_exception.AuthenticationException:
#         print('Authentication error - not connected to remote server')
#     except socket.gaierror:
#         print('Socket error - not connected to remote server')
#     return None


# def execute_remote_command(command: str) -> str:
#     if ssh_client := get_ssh_client():
#         _stdin, _stdout, _stderr = ssh_client.exec_command(command)
#         if _stderr.read().decode():
#             print(f'Server side error: {_stderr.read().decode()}')
#         ssh_client.close()
#         return _stdout.read().decode()
#     return ''


    def get_remote_files(
            self, remote_dir: str, local_dir: str, ignore: list = None):
        """Recursively download files from remote dir and add to local dir."""
        if not ignore:
            ignore = []

        if not Path(local_dir).is_dir():
            os.mkdir(local_dir)

        logger.info('Download', remote_dir=remote_dir, local_dir=str(local_dir))
        for remote_file in self.stfp_client.listdir_attr(remote_dir):
            if remote_file.filename in ignore:
                continue
            remote_path = f'{remote_dir}/{remote_file.filename}'
            local_path = os.path.join(local_dir, remote_file.filename)
            mode = remote_file.st_mode
            if S_ISDIR(mode):
                with contextlib.suppress(OSError):
                    os.mkdir(local_path)
                get_remote_files(remote_path, local_path, ignore)
            elif S_ISREG(mode):
                self.stfp_client.get(remote_path, local_path)
                logger.info('File downloaded', name= remote_file.filename)
                ...
