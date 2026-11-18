from first_setup import setup_telegram_proxy
import colorama
import os
import sys

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":
    colorama.init()
    setup_telegram_proxy()
