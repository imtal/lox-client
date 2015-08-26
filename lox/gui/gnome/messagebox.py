import gtk
import gettext
_ = gettext.gettext


def info(message):
    m = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
            gtk.BUTTONS_CLOSE, message)
    result = m.run()
    m.destroy()
    return result

def error(message):
    m = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
            gtk.BUTTONS_CLOSE, message)
    result = m.run()
    m.destroy()
    return result

def ask(message):
    m = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO, message)
    result = m.run()
    m.destroy()
    return result == gtk.RESPONSE_YES
