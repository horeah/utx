from distutils.core import setup
import py2exe

setup(
    name = 'lsx', 
    console = [
        {
            'script': 'lsx.py',
        }
    ],
    options = {'py2exe': { 'bundle_files' : 1 }},
    zipfile = None
)
