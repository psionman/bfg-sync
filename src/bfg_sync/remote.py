
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


def _get_ssh_client() -> paramiko.client.SSHClient:
    ssh_client = paramiko.client.SSHClient()
    ssh_client.load_host_keys(known_hosts_file_name)
    ssh_client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        ssh_client.connect(
            hostname=hostname,
            username=username,
            port=port,
            key_filename=key_filename,
            auth_timeout=5,
            )
        return ssh_client
    except paramiko.ssh_exception.AuthenticationException:
        logger.warning('Authentication error - not connected to remote server')
    except socket.gaierror:
        logger.warning('Socket error - not connected to remote server')
    return None


def execute_remote_command(command: str) -> str:
    if ssh_client := _get_ssh_client():
        _stdin, _stdout, _stderr = ssh_client.exec_command(command)
        if _stderr.read().decode():
            logger.warning('Server side error', err=_stderr.read().decode())
        ssh_client.close()
        return _stdout.read().decode()
    return ''


def get_remote_files(remote_dir: str, local_dir: str, ignore: list = None):
    ssh_client = _get_ssh_client()
    sftp_client = ssh_client.open_sftp()
    _get_remote_files(ssh_client, sftp_client, remote_dir, local_dir, ignore)


def _get_remote_files(
        ssh_client: paramiko.client.SSHClient,
        sftp_client,
        remote_dir: str,
        local_dir: str,
        ignore: list = None):

    if not ignore:
        ignore = []

    if not Path(local_dir).is_dir():
        logger.info('Create local', dir=local_dir)
        os.mkdir(local_dir)

    logger.info('Open dir', remote=remote_dir, local=local_dir)

    for entry in sftp_client.listdir_attr(remote_dir):
        if entry.filename in ignore:
            continue
        remote_path = f'{remote_dir}/{entry.filename}'
        local_path = os.path.join(local_dir, entry.filename)
        mode = entry.st_mode
        if S_ISDIR(mode):
            get_remote_files(remote_path, local_path, ignore)
        elif S_ISREG(mode):
            sftp_client.get(remote_path, local_path)
            logger.info('Download file', name=entry.filename)
            ...
