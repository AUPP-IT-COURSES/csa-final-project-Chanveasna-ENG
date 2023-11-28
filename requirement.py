"""
install requirement for the project
"""
import os
import sys
import subprocess


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def main():
    install('numpy')
    install('opencv-python')
    install('pytesseract')
    install('pillow')


if __name__ == '__main__':
    main()