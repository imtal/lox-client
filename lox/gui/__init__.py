'''
The GUI module loads the appropriate user interface
depending on environment vaiable and the platform
'''
import os
import sys

if sys.platform=='linux2':
    if not (os.getenv('DISPLAY') is None):
        from gnome import *
    else:
        from text import *
elif sys.platform=='darwin':
    from cocoa import *
else:
    from tkinter import *
