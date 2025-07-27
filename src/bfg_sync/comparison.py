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
        self.local_versions = self._get_local_versions()
        # ic(self.local_versions)

        self.remote_versions = self._get_remote_versions()
        # ic(self.remote_versions)

        # ic(remote_files)
        # self.package_list = config.packages

        # (missing_remote_dir, missing_local_dir) = self._missing_dirs()
        # self.missing_local_dir = missing_local_dir
        # self.missing_remote_dir = missing_remote_dir

        # (missing_local_files, missing_remote_files) = self._missing_files()
        # self.missing_local_files = missing_local_files
        # self.missing_remote_files = missing_remote_files
        # self.packages = self._get_package_versions()

        # self.missing = (missing_remote_dir or missing_local_dir or
        #                 missing_remote_files or missing_local_files)
        # self.compare_files()

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


    # def _missing_dirs(self):
    #     missing_remote_dir = self._identify_missing_dirs(
    #         self.local_dirs,
    #         self.remote_dirs,
    #         'remote')
    #     missing_local_dir = self._identify_missing_dirs(
    #         self.remote_dirs,
    #         self.local_dirs,
    #         'local')
    #     if not missing_remote_dir and not missing_local_dir:
    #         ic("No directory mismatches", INFO_COLOUR)
    #     return (missing_remote_dir, missing_local_dir)

    # @staticmethod
    # def _identify_missing_dirs(first_dict, second_dict, locale):
    #     if locale == 'local':
    #         print('')
    #         print('Directory comparison')
    #     missing = []
    #     for item_name, item in first_dict.items():
    #         if item_name not in second_dict:
    #             if locale == 'local':
    #                 ic(f'No {locale} dir: {item_name}', ERROR_COLOUR)
    #             missing.append(item_name)
    #     return missing

    # def _missing_files(self):
    #     missing_remote_files = []
    #     for dir, local_files in self.local_dirs.items():
    #         if dir in self.missing_remote_dir:
    #             continue
    #         remote_files = self.remote_dirs[dir]
    #         missing_remote_files += self._identify_missing_files(
    #             local_files,
    #             remote_files,
    #             'remote',
    #             dir
    #             )

    #     missing_local_files = []
    #     for dir, remote_files in self.remote_dirs.items():
    #         if dir in self.missing_local_dir:
    #             continue
    #         local_files = self.local_dirs[dir]
    #         missing_local_files += self._identify_missing_files(
    #             remote_files,
    #             local_files,
    #             'local',
    #             dir
    #             )

    #     return (missing_local_files, missing_remote_files)

    # @staticmethod
    # def _identify_missing_files(first_dict, second_dict, locale, dir):
    #     missing = []
    #     for item_name in first_dict.keys():
    #         if item_name not in second_dict:
    #             if locale == 'local':
    #                 ic(
    #                     f'No {locale} file: {dir}/{item_name}',
    #                     ERROR_COLOUR
    #                     )
    #             missing.append(item_name)
    #     return missing

    # def _get_package_versions(self) -> dict[str: list[str]]:
    #     print('')
    #     print('Package comparison')
    #     print(f"{'Package':<15} {'Remote':<8} {'Local':<8}")
    #     remote_response = requests.get(VERSION_URI)
    #     if remote_response.status_code != 200:
    #         ic("Cannot access remote versions", ERROR_COLOUR)
    #         return

    #     packages = {}
    #     local_packages = self._local_package_versions()
    #     remote_packages = remote_response.content
    #     remote_packages = json.loads(
    #         remote_response.content.decode(encoding='UTF-8')
    #         )

    #     missing = False
    #     for package in self.package_list:
    #         packages[package] = {}
    #         if package not in local_packages:
    #             local_package = ic('missing', ERROR_COLOUR)
    #             missing = True
    #         else:
    #             local_package = local_packages[package]
    #         packages[package]['local'] = local_package

    #         if package not in remote_packages:
    #             remote_package = ic('missing', ERROR_COLOUR)
    #             missing = True
    #         else:
    #             remote_package = remote_packages[package]
    #         packages[package]['remote'] = remote_package

    #         remote_colour = INFO_COLOUR
    #         if local_package != remote_package:
    #             remote_colour = ERROR_COLOUR
    #             missing = True
    #         local_package = ic(f'{local_package:<8}', INFO_COLOUR)
    #         remote_package = ic(f'{remote_package:<8}', remote_colour)

    #         print(f'{package:<15} {remote_package} {local_package}')

    #     if not missing:
    #         ic("No package mismatches", INFO_COLOUR)
    #     else:
    #         ic("Package mismatches", ERROR_COLOUR)

    #     return packages

    # def _local_package_versions(self):
    #     versions = {}
    #     for package in self.package_list:
    #         versions[package] = version(package)
    #     return versions

    # def compare_files(self) -> None:
    #     print('')
    #     print('File mismatches')
    #     heading = f"{'Directory':<10} {'File':<15} {'Remote':>6} {'Local':>6}"
    #     print(heading)
    #     sorted_dirs = sorted(self.local_dirs, key=lambda x: x)
    #     for dir in sorted_dirs:
    #         local_files = self.local_dirs[dir]
    #         sorted_files = sorted(local_files, key=lambda x: x)
    #         remote_files = self.remote_dirs[dir]
    #         for file_name in sorted_files:
    #             local_data = local_files[file_name]
    #             remote_data = remote_files[file_name]
    #             if len(local_data.content) != len(remote_data.content):
    #                 output = (f'{dir:<10} {file_name:<15} '
    #                           f'{len(local_data.content):>6} '
    #                           f'{len(remote_data.content):>6}')
    #                 print(output)

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
