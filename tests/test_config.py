from pathlib import Path

from bfg_sync.config import read_config


def test_config_no_directory(mocker):
    mocker.patch(
        'bfg_sync.config.CONFIG_PATH',
        Path(
            Path(__file__).parent,
            'test_data',
            'not a directory',
            'config.toml')
        )

    config = read_config()
    assert config.local_env == ''


def test_config_save(mocker):
    mocker.patch(
        'bfg_sync.config.CONFIG_PATH',
        Path(Path(__file__).parent, 'test_data', 'config', 'config.toml')
        )

    config = read_config()
    if config.path.is_file():
        config.path.unlink()

    config = read_config()
    config.update('local_env', 'abc')
    config.save()

    config = read_config()

    assert config.local_env == 'abc'
    config.update('local_env', '')
