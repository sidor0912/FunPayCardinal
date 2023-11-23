from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ["vk_api"] + collect_submodules("vk_api")
