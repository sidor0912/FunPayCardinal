from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ["PIL"] + collect_submodules("PIL")
