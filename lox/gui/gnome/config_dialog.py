'''
Module that defines the configuration window class

'''
import gtk
import gobject

import lox.config
from lox.gui.gnome.icon import icon
from lox.gui.gnome.settings_dialog import SettingsDialog

import gettext
_ = gettext.gettext


class ConfigDialog(gtk.Dialog):

    def __init__(self):
        super(ConfigDialog,self).__init__(_("Localbox configuration"), None,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                   (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.connect("response", self.response)
        self.set_icon_from_file(icon(size=64))
        self.set_border_width(10)
        self.set_size_request(640,320)
        self.set_position(gtk.WIN_POS_CENTER)

        self._selected_session = None

        layout = gtk.Table(4, 2, False)
        layout.set_col_spacings(3)
        self.vbox.pack_start(layout)

        # session liststore
        self._liststore = gtk.ListStore(gobject.TYPE_STRING)
        for session in lox.config.settings.iterkeys():
            self._liststore.append([session])

        # session listview
        self._treeview = gtk.TreeView(self._liststore)
        #self._treeview.set_headers_visible(False)
        self._selection = self._treeview.get_selection()
        self._selection.set_mode(gtk.SELECTION_SINGLE)
        self._selection.connect("changed", self._select)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_('Session name'), cell)
        column.set_cell_data_func(cell, self._update_cell) # function to update the cell
        self._treeview.append_column(column)
        layout.attach(self._treeview, 0, 1, 1, 2, gtk.FILL | gtk.EXPAND,
            gtk.FILL | gtk.EXPAND, 1, 1)

        # buttons right
        self._add = gtk.Button(_("Add"))
        self._add.connect('clicked', self.on_add, None)

        self._edit = gtk.Button(_("Edit"))
        self._edit.set_sensitive(False)
        self._edit.connect('clicked', self.on_edit, None)

        self._delete = gtk.Button(_("Remove"))
        self._delete.set_sensitive(False)
        self._delete.connect('clicked', self.on_delete, None)

        buttoncol = gtk.VButtonBox()
        buttoncol.set_layout(gtk.BUTTONBOX_START)
        buttoncol.add(self._add)
        buttoncol.add(self._edit)
        buttoncol.add(self._delete)
        layout.attach(buttoncol,1,2,1,2, gtk.SHRINK, gtk.EXPAND|gtk.FILL,16,8)

        # separator
        line = gtk.HSeparator()
        layout.attach(line,0,2,2,3,gtk.EXPAND|gtk.FILL,gtk.SHRINK,0,8)

        layout.show_all()

    def _update_cell(self, column, cell, model, iter):
        session_name = model.get_value(iter, 0)
        cell.set_property('text',session_name)
        return

    def _select(self,selected):
        self._edit.set_sensitive(True)
        self._delete.set_sensitive(True)
        (model, pathlist) = self._selection.get_selected_rows()
        for path in pathlist :
            tree_iter = model.get_iter(path)
            self._selected_session = model.get_value(tree_iter,0)

    def on_add(self, widget, obj):
        d = SettingsDialog()
        d.do_load(None)
        d.run()
        # refresh
        self._liststore.clear()
        for session in lox.config.settings.iterkeys():
            self._liststore.append([session])

    def on_edit(self, widget, obj):
        d = SettingsDialog()
        d.do_load(self._selected_session)
        d.run()
        # refresh
        self._liststore.clear()
        for session in lox.config.settings.iterkeys():
            self._liststore.append([session])

    def on_delete(self, widget, obj):
        settings.pop(self._selected_session)
        save()
        self.do_refresh()

    def on_close(self, widget, obj):
        # hide window, do not destroy
        self.hide()
        return True

    def response(self, widget, response):
        self.destroy()


