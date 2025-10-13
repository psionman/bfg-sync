import os
import json
import re
from importlib.metadata import version
from pathlib import Path
from dataclasses import dataclass
import datetime
import requests

from config import read_config
from remote import execute_remote_command, get_remote_files

ERROR_COLOUR, INFO_COLOUR, VERSION_URI = 0, 1, 2


@dataclass
class FileData:
    dir: str
    name: str
    date: datetime
    content: str


@dataclass
class ComparisonData:
    dir: str
    name: str
    local_date: datetime
    remote_date: datetime


class Comparison():
    def __init__(self):
        config = read_config()
        self.config = config
        self.last_download = None
        self.local_versions = self._get_local_versions()
        # ic(self.local_versions)

        self.remote_versions = self._get_remote_versions()

    def download_remote_files(self, use_ignore: bool = True) -> None:
        ignore = []
        if use_ignore:
            ignore = self.config.ignore
        local_path = Path(Path(__file__).parent.parent.parent, 'data')
        get_remote_files('bfg/bfg_wag', local_path, ignore)
        print('Done ...')

    def compare_files(self, use_ignore: bool) -> dict:
        paths = self._get_file_dict(use_ignore)
        for item in paths.values():
            if item['local'] == 'missing' or item['remote'] == 'missing':
                continue
            local = self._read_file(item['local'])
            remote = self._read_file(item['remote'])
            item['match'] = local == remote
        return paths

    def _read_file(self, path) -> str:
        with open(path, 'r') as f_file:
            return f_file.read()

    def _get_file_dict(self, use_ignore: bool) -> dict:
        ignore = ''
        if use_ignore:
            ignore = f'({'|'.join(self.config.ignore)})'

        paths = {}

        # Local files
        search_dir = self.config.development_dir
        local_files = self._get_list_of_files(search_dir, ignore)
        for file in local_files:
            parent = str(file.parent).replace(
                f'{self.config.development_dir}/', '')
            key = f'{parent}:{file.name}'
            paths[key] = {'local': file, 'remote': 'missing', 'match': False}

        # Remote files
        search_dir = self.config.download_dir
        remote_files = self._get_list_of_files(search_dir, ignore)
        for file in remote_files:
            parent = str(file.parent).replace(
                f'{self.config.download_dir}/', '')
            key = f'{parent}:{file.name}'
            if key in paths:

                last_download = datetime.datetime.fromtimestamp(
                    os.path.getmtime(Path(parent, file)))
                self.last_download = last_download.strftime(
                    '%d %b %Y at %H:%M')
                paths[key]['remote'] = file
            else:
                paths[key] = {
                    'local': 'missing', 'remote': file, 'match': False}
        return paths

    def _get_list_of_files(self, root: str, ignore: str) -> list:
        files = []
        for directory_name, subdir_list, file_list in os.walk(root):
            if ignore and re.search(ignore, directory_name):
                continue
            for file_name in file_list:
                file_path = Path(directory_name, file_name)
                if ((ignore and re.search(ignore, file_name))
                        or str(file_path.parent)[-3:] == 'src'):
                    continue
                files.append(file_path)
        return files

    def _get_local_versions(self) -> dict:
        envs_dir = Path(
            self.config.local_env,
            'lib',
            f'python{self.config.python_version}',
            'site-packages')
        local_dirs = [str(path) for path in envs_dir.iterdir()]
        return self._get_package_versions(local_dirs)

    def _get_remote_versions(self) -> dict:
        command = (
            f'ls -l {self.config.remote_env}/{self.config.python_version}'
            f'/lib/python{self.config.python_version}/site-packages')

        remote_dirs = execute_remote_command(command)
        env_files = remote_dirs.split('\n')
        return self._get_package_versions(env_files)

    def _get_package_versions(self, env_files: list) -> dict:
        package_versions = {}
        package_re = r'-\d{1,}\.\d{1,}\.\d{1,}\.dist-info'
        version_re = r'\d{1,}\.\d{1,}\.\d{1,}'

        for item in env_files:
            for package in self.config.packages:
                re_test = rf'{package}{package_re}'
                res = re.search(re_test, item)
                if res:
                    version_res = re.search(version_re, item)
                    package_version = item[
                        version_res.start():version_res.end()]
                    package_versions[package] = package_version
        return package_versions
