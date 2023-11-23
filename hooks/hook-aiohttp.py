from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ["aiohttp"] + collect_submodules("aiohttp")
