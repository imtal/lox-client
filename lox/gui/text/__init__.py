'''
Text mode GUI functions


Usage:

    import lox.gui.text as gui

    gui.mainloop()

'''
import os
import sys
import syslog
import lox
import lox.config
from getpass import getpass
from time import sleep
import gettext
_ = gettext.gettext


def notify(message):
    '''
    Log a background system notification
    '''
    syslog.syslog(message)

def info(message):
    '''
    Show an interactive information message
    '''
    sys.stdout.write(message)

def error(message):
    '''
    Show an interactive error message
    '''
    sys.stderr.write("ERROR: {0}".format(message))
    sys.stderr.write(os.linesep)

def ask(message):
    '''
    Ask an interactive Yes/No question
    '''
    y = raw_input(_("{0} [yes]: ").format(message))
    return y=="" or y==_("yes")

def config():
    '''
    List configurations
    '''
    lox.config.load()
    print
    print _("Localbox sessions configured:")
    print "  {0:16} {1}".format("NAME","ADDRESS")
    for name in lox.config.settings.iterkeys():
        print "  {0:16} ({1})".format(name,lox.config.settings[name]["lox_url"])
    print ""

def settings(name=None):
    '''
    Edit settings, when name is not defined an emtpy settings form is shown
    '''
    lox.config.load()
    if name is None:
        name = raw_input(_("Enter a session name: "))
    if not lox.config.settings.has_key(name):
        print _("Add Localbox session '{}':").format(name)
    else:
        print _("Edit Localbox session '{}':").format(name)
    for (setting,caption,default,ext) in lox.config.METADATA:
        value = raw_input("- {0} [{1}]: ".format(caption,lox.config.settings[name][setting]))
        lox.config.settings[name][setting] = lox.config.settings[name][setting] if value=="" else value
    lox.config.save()

def get_password():
    '''
    Ask for a password
    '''
    print
    return getpass(_("Enter password to unlock: "))

def new_password():
    '''
    Ask for a new password
    '''
    retries = 0
    while retries<3:
        pass1 = getpass(_("Enter new password: "))
        pass2 = getpass(_("Enter password again to verify: "))
        if pass1 == pass2:
            return pass1
        error(_("Passwords entered are not the same ..."))
    error(_("You tried three times, now quitting"))
    sys.exit(2)

def about():
    '''
    Show an interactive about messsage
    '''
    print
    print _("{0} version {1} - {2}").format(os.path.basename(sys.argv[0]),lox.VERSION,lox.DESCRIPTION)
    print

def mainloop():
    '''
    Enter the main loop of the program, which is needed for most GUI's
    '''
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt as e:
        raise e

