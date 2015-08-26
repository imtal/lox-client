'''
Module that defines the password dialogs
'''

import gtk
from lox.gui.gnome.icon import icon
import gettext
_ = gettext.gettext


class PasswordDialog(gtk.Dialog):

    def __init__(self, new=False):
        self.password = None
        super(PasswordDialog,self).__init__(_("Localbox password"), None,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                   (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.connect("response", self.response)
        self.set_default_response(gtk.RESPONSE_ACCEPT)
        self.set_icon_from_file(icon(size=64))
        #self.connect('delete_event',self.delete_event)
        #self.connect('destroy',self.on_destroy)
        self.set_border_width(10)
        self.set_size_request(400,160)

        layout = gtk.Table(4, 2, False)
        layout.set_col_spacings(3)
        self.vbox.pack_start(layout)

        self.icon = gtk.Image()
        self.icon.set_from_file(icon(size=64))
        self.icon.set_alignment(xalign=0.3, yalign=0.5)
        layout.attach(self.icon,0,1,0,2)

        self.label = gtk.Label(_('Enter passcode:'))
        self.label.set_alignment(xalign=0.0, yalign=0.5)
        layout.attach(self.label,1,2,0,1,gtk.EXPAND|gtk.FILL)

        self.entry = gtk.Entry()
        self.entry.set_visibility(False)
        self.entry.set_invisible_char("*")
        layout.attach(self.entry,1,2,1,2,gtk.EXPAND|gtk.FILL)
        self.entry.set_activates_default(gtk.TRUE)

        self.show_all()

    def delete_event(self, widget, event, data=None):
        self.hide()
        return True

    def on_destroy(self, widget, obj):
        self.hide()
        return True

    def response(self, widget, response):
        if response == gtk.RESPONSE_ACCEPT:
            self.password = self.entry.get_text()
        else:
            self.password = ""
        self.destroy()

    def run(self):
        result = super(PasswordDialog, self).run()
        return self.password

