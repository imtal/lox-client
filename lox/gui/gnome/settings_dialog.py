'''
Module that defines the settings dialog
'''

import gtk
import lox.config
from lox.gui.gnome.icon import icon
import gettext
_ = gettext.gettext


class SettingsDialog(gtk.Dialog):

    def __init__(self):
        super(SettingsDialog,self).__init__(_("Localbox settings"), None,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                   (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.connect("response", self.response)
        self.set_title(_("Session settings"))
        self.set_icon_from_file(icon(size=64))
        self.set_border_width(10)
        self.set_size_request(640,380)
        self.set_position(gtk.WIN_POS_MOUSE)
        # keep original name
        self._name = None
        # set up grid
        rows = len(lox.config.METADATA) + 3
        cols = 2
        layout = gtk.Table(rows, cols, False)
        layout.set_col_spacings(3)
        self.vbox.pack_start(layout)
        self._label = dict()
        self._entry = dict()
        # place session setting fields in grid
        self._label['name'] = gtk.Label(_("Session name"))
        self._label['name'].set_alignment(0, 0.5)
        self._entry['name'] = gtk.Entry()
        layout.attach(self._label['name'],0,1,0,1)
        layout.attach(self._entry['name'],1,2,0,1)
        i = 1
        for (key,caption,default,ext) in lox.config.METADATA:
            self._label[key] = gtk.Label(caption)
            self._label[key].set_alignment(0, 0.5)
            layout.attach(self._label[key],0,1,i,i+1)
            if ext == "text":
                self._entry[key] = gtk.Entry()
            if ext == "int":
                self._entry[key] = gtk.SpinButton()
                self._entry[key].set_range(60,6000)
            if type(ext) is list:
                self._entry[key] = gtk.combo_box_new_text()
                for value in ext:
                    self._entry[key].append_text(value)
            layout.attach(self._entry[key],1,2,i,i+1)
            i = i+1
        # separator
        line = gtk.HSeparator()
        layout.attach(line,0,2,i,i+1)
        # show
        layout.show_all()

    def do_load(self,name = None):
        if name is None:
            self._name = _("New account")
            self._entry["name"].set_text(self._name)
            for (key,caption,default,ext) in lox.config.METADATA:
                if ext == "text":
                    self._entry[key].set_text(default)
                if ext == "int":
                    self._entry[key].set_value(default)
                if type(ext) is list:
                    self._entry[key].set_active(default)
        else:
            self._name = name # keep track of original name in case it is changed
            self._entry["name"].set_text(name)
            for (key,caption,default,ext) in lox.config.METADATA:
                if ext == "text":
                    self._entry[key].set_text(lox.config.settings[name][key])
                if ext == "int":
                    self._entry[key].set_value(int(lox.config.settings[name][key]))
                if type(ext) is list:
                    value = lox.config.settings[name][key]
                    if value in ext:
                        self._entry[key].set_active(ext.index(value))
                    else:
                        self._entry[key].set_active(default)

    def response(self, widget, response):
        if response == gtk.RESPONSE_ACCEPT:
            # save settings
            name = self._entry['name'].get_text()
            d = dict()
            for (key,caption,default,ext) in lox.config.METADATA:
                if ext == "text":
                    d[key] = self._entry[key].get_text()
                if ext == "int":
                    d[key] = str(self._entry[key].get_value_as_int())
                if type(ext) is list:
                    index = self._entry[key].get_active()
                    d[key] = ext[index]
            try:
                if not (self.name is None):
                    lox.config.settings.pop(self._name)
                lox.config.settings[name] = d
                lox.config.save()
            except Exception as e:
                lox.gui.gnome.messagebox(ERROR,_("Cannot save settings: {0}").format(str(e)))
                return True
        self.destroy()

    def run(self):
        result = super(SettingsDialog, self).run()
        return result

