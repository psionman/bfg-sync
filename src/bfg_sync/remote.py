
import os
import paramiko
import socket
from stat import S_ISDIR, S_ISREG
from dotenv import load_dotenv

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
        print('Authentication error - not connected to remote server')
    except socket.gaierror:
        print('Socket error - not connected to remote server')
    return None



def execute_remote_command(command: str) -> str:
    ssh_client = _get_ssh_client()
    if ssh_client:
        _stdin, _stdout, _stderr = ssh_client.exec_command(command)
        if _stderr.read().decode():
            print(f'Server side error: {_stderr.read().decode()}')
        ssh_client.close()
        return _stdout.read().decode()
    return ''


def get_remote_files(remote_dir:str, local_dir: str, ignore: list = None):
    if not ignore:
        ignore = []
    ssh_client = _get_ssh_client()
    stfp_client = ssh_client.open_sftp()
    for entry in stfp_client.listdir_attr(remote_dir):
        if entry.filename in ignore:
            continue
        ic(entry.filename)
        remote_path = remote_dir + "/" + entry.filename
        local_path = os.path.join(local_dir, entry.filename)
        mode = entry.st_mode
        if S_ISDIR(mode):
            try:
                os.mkdir(local_path)
            except OSError:
                pass
            get_remote_files(remote_path, local_path, ignore)
        elif S_ISREG(mode):
            stfp_client.get(remote_path, local_path)
            ...
