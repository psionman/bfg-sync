
from pathlib import Path
import os
import paramiko
import socket
from stat import S_ISDIR, S_ISREG
from dotenv import load_dotenv

from bfg_sync import logger

load_dotenv()

# Access variables
hostname = os.getenv('HOSTNAME')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
port = os.getenv('PORT')
key_filename = os.getenv('PRIVATE_KEY_FILE')
known_hosts_file_name = os.getenv('KNOWN_HOSTS')


class SSHClient(paramiko.client.SSHClient):
    def __init__(self):
        super().__init__()
        self.load_host_keys(known_hosts_file_name)
        self.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            self.connect(
                hostname=hostname,
                username=username,
                port=port,
                key_filename=key_filename,
                auth_timeout=5,
                )
        except paramiko.ssh_exception.AuthenticationException:
            logger.error(
                'Authentication error - not connected to remote server')
        except socket.gaierror:
            logger.error('Socket error - not connected to remote server')

        self.sftp_client = self.open_sftp()


def execute_remote_command(command: str) -> str:
    ssh_client = SSHClient()

    _stdin, _stdout, _stderr = ssh_client.exec_command(command)
    if _stderr.read().decode():
        logger.warning('Server side error', err=_stderr.read().decode())
    ssh_client.close()
    return _stdout.read().decode()


def get_remote_files(remote_dir: str, local_dir: str, ignore: list = None):
    ssh_client = SSHClient()
    _get_remote_files(ssh_client, remote_dir, local_dir, ignore)


def _get_remote_files(
        ssh_client: paramiko.client.SSHClient,
        remote_dir: str,
        local_dir: str,
        ignore: list = None):

    if not ignore:
        ignore = []

    if not Path(local_dir).is_dir():
        logger.info('Create local', dir=local_dir)
        os.mkdir(local_dir)

    logger.info('Open dir', remote=remote_dir, local=local_dir)

    for entry in ssh_client.sftp_client.listdir_attr(remote_dir):
        if entry.filename in ignore:
            continue
        remote_path = f'{remote_dir}/{entry.filename}'
        local_path = os.path.join(local_dir, entry.filename)
        mode = entry.st_mode
        if S_ISDIR(mode):
            get_remote_files(remote_path, local_path, ignore)
        elif S_ISREG(mode):
            ssh_client.sftp_client.get(remote_path, local_path)
            logger.info('Download file', name=entry.filename)
