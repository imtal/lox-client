'''

Usage:

    import lox.gui_gnome as gui

    gui.mainloop()

Dependencies:

    sudo apt-get install python-appindicator
    sudo apt-get install python-notify

'''
import gtk
import gobject
import lox.config
from lox.gui.gnome.messagebox import info, error, ask
from lox.gui.gnome.notify import notify
from lox.gui.gnome.icon import icon
from lox.gui.gnome.indicator import Indicator, show_about
from lox.gui.gnome.config_dialog import ConfigDialog
from lox.gui.gnome.settings_dialog import SettingsDialog
from lox.gui.gnome.password_dialog import PasswordDialog
import gettext
_ = gettext.gettext



def get_password():
    d = PasswordDialog()
    return d.run()

def new_password():
    d = PasswordDialog(new=True)
    return d.run()

def config():
    d = ConfigDialog()
    d.run()

def settings(name=None):
    d = SettingsDialog()
    d.do_load(name)
    d.run()

def about():
    show_about()

def mainloop():
    global config_window
    global settings_window
    gobject.threads_init()
    indicator = Indicator()
    try:
        gtk.main()
    except KeyboardInterrupt:
        indicator.destroy()

