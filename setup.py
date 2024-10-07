from pip._internal.cli.main import main

common_packages = [
    "psutil>=5.9.4",
    "beautifulsoup4>=4.11.1",
    "colorama>=0.4.6",
    "requests==2.28.1",
    "pytelegrambotapi==4.15.2",
    "pillow>=9.3.0",
    "aiohttp==3.9.0",
    "requests_toolbelt==0.10.1",
    "lxml>=5.3.0",
    "bcrypt>=4.2.0"
]


def install_packages(packages_list: list[str]):
    for pkg in packages_list:
        main(["install", "-U", pkg])


if __name__ == '__main__':
    install_packages(common_packages)
