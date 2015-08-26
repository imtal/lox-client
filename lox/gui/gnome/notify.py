import pynotify
from lox.gui.gnome.icon import icon

import gettext
_ = gettext.gettext


def notify(title,message):
    pynotify.init("LocalBox")
    n = pynotify.Notification("LocalBox",message,icon(size=64))
    #n.set_icon_from_pixbuf()
    #n.set_timeout(2000)
    if not n.show():
        print _("failed to send notification")


