from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ["requests_toolbelt"] + collect_submodules("requests_toolbelt")
