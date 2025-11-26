list:
    just --list

run arg1="":
    uv run src/bfg_sync/main.py {{arg1}}

test:
    uv run -m pytest
