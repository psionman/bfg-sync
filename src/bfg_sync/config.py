"""Config for bfg-sync."""

from psiconfig import TomlConfig

from bfg_sync.constants import CONFIG_PATH

DEFAULT_CONFIG = {
    'development_dir': '',
    'local_env': '',
    'remote_env': '',
    'python_version': '',
    'download_dir': '',
    'ignore': [],
    'packages': [],
    'last_download': '',
    'geometry': {
        'frm_main': '500x600',
        'frm_config': '700x300',
    },
}


def read_config(restore_defaults: bool = False) -> TomlConfig:
    """Return the config file."""
    return TomlConfig(
        path=CONFIG_PATH,
        defaults=DEFAULT_CONFIG,
        restore_defaults=restore_defaults)


def save_config(config: TomlConfig) -> TomlConfig | None:
    result = config.save()
    if result != config.STATUS_OK:
        return None
    config = TomlConfig(CONFIG_PATH)
    return config


config = read_config()
