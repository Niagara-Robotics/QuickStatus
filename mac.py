##### run with "python3 mac.py py2app" #####
from setuptools import setup

APP = ['__main__.py']
DATA_FILES = []
OPTIONS = {
    'includes': ['jaraco.text', 'pynput'],
    'resources': 'resources',
    'iconfile': 'resources/icons/icon.icns',
    'packages': ['quickstatus', 'pynput']
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name='QuickStatus'
)