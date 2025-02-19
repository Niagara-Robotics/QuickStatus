import os
from shutil import which
if which('pip') is not None:
    os.system("pip install toml")
    os.system("pip install pyqt6")
    os.system("pip install robotpy")
else:
    print("bro does NOT have pip")