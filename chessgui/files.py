from pathlib import Path
try:
    from importlib import resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as resources


def get_icon(name, file_extension='svg'):
    path = resources.files('chessgui').joinpath('icons')
    return Path(path.joinpath(f'{name}.{file_extension}'))
