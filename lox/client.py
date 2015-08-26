'''

Main module

Usage:

    import lox.client

    lox.client.main()

'''

import os
import sys
import time
import traceback
import crypto
from getpass import getpass
import lox
import lox.config as config
from lox.api import LoxApi
from lox.daemon import Daemon, DaemonError
from lox.session import LoxSession
from lox.error import LoxError
import lox.gui as gui
import gettext
_ = gettext.gettext

pidfile = os.environ['HOME']+'/.lox/lox-client.pid'
logfile = os.environ['HOME']+'/.lox/lox-client.log'

class Supervisor(Daemon):
    '''
    The daemon: start the sessions as threads and start the GUI
    '''
    sessions = dict()

    def started(self, restart=False):
        print
        if restart:
            print _("Localbox daemon restarted")
        else:
            print _("Localbox daemon started")
        print

    def run(self):
        for name in config.settings.iterkeys():
            self.sessions[name] = LoxSession(name)
            self.sessions[name].start()
        gui.mainloop()
        for name in self.sessions.iterkeys():
            self.sessions[name].stop()


    def terminate(self):
        for name in config.settings.iterkeys():
            self.remove(name)

    '''
    Use the following functions only from within the daemon
    '''
    def add(self, name):
        self.sessions[name] = LoxSession(name)
        self.sessions[name].start()

    def remove(self, name):
        self.sessions[name].stop()
        while self.sessions[name].is_alive():
            time.sleep(1)
        del self.sessions[name]

    def restart(self,name):
        self.sessions[name].stop()
        while self.sessions[name].is_alive():
            time.sleep(1)
        self.sessions[name].start()


def need_sessions():
    '''
    Check if there are any sessions specified in config file
    '''
    if len(config.settings)==0:
        print
        print _("No sessions configured, use command 'add'")
        print
        sys.exit(2) # ENOENT

def cmd_start():
    '''
    Start the deamon
    '''
    global pidfile, logfile
    config.load()
    need_sessions()
    daemon = Supervisor(pidfile, path=os.environ['HOME'], umask=100, stdout=logfile, stderr=logfile)
    if daemon.status() is None:
        password = gui.get_password()
        #crypto.set_passphrase(password)
        daemon.start()
    else:
        print _("Error: already running")
        print
        sys.exit(114) # EALREADY

def cmd_stop():
    '''
    Stop the daemon
    '''
    global pidfile, logfile
    config.load()
    daemon = Supervisor(pidfile, path=os.environ['HOME'], umask=100, stdout=logfile, stderr=logfile)
    print
    if not daemon.status() is None:
        daemon.stop()
        print _("Localbox daemon stopped")
    else:
        print _("Localbox daemon not running")
    print

def cmd_run():
    '''
    Run the deamon in the foreground
    '''
    global pidfile, logfile
    config.load()
    need_sessions()
    daemon = Supervisor(pidfile, path=os.environ['HOME'], umask=100, stdout=logfile, stderr=logfile)
    print
    print "Localbox running in foreground"
    print
    daemon.run()

def cmd_restart():
    '''
    Restart daemon
    '''
    global pidfile, logfile
    config.load()
    need_sessions()
    daemon = Supervisor(pidfile, path=os.environ['HOME'], umask=100, stdout=logfile, stderr=logfile)
    daemon.restart()

def cmd_status():
    '''
    Show status of daemon
    '''
    global pidfile, logfile
    daemon = Supervisor(pidfile, path=os.environ['HOME'], umask=100, stdout=logfile, stderr=logfile)
    s = daemon.status()
    print
    if s is None:
        print _("Localbox daemon not running ...")
    else:
        print _("Localbox daemon running with pid {}").format(s)
    print

def cmd_add():
    '''
    Add account
    '''
    config.load()
    if len(sys.argv)>2:
        name = sys.argv[2]
        if config.settings.has_key(name):
            print _("Error: a session with name '{}' already exists").format(name)
        else:
            print
            print _("Add Localbox session '{}':").format(name)
            for (setting,caption,default,ext) in config.METADATA:
                print name, setting
                value = raw_input("- {0} [{1}]: ".format(caption,default))
                config.settings[name][setting] = default if value=="" else value
            config.save()
            daemon = Supervisor(pidfile, path=os.environ['HOME'], umask=100, stdout=logfile, stderr=logfile)
            if not daemon.status() is None:
                y = raw_input(_("Start session [yes]: "))
                if y=="" or y==_("yes"):
                    daemon.restart()
        print
    else:
        cmd = os.path.basename(sys.argv[0])
        print
        print _("Usage: {0} add <name>").format(cmd,sys.argv[1])
        print

def cmd_delete():
    '''
    Delete account
    '''
    config.load()
    if len(sys.argv)>2:
        name = sys.argv[2]
        if not config.settings.has_key(name):
            print
            print _("Error: a session with name '{}' is not configured").format(name)
            print
        else:
            config.settings.pop(name)
            config.save()
            daemon = Supervisor(pidfile, path=os.environ['HOME'], umask=100, stdout=logfile, stderr=logfile)
            if not daemon.status() is None:
                daemon.restart()
            print
    else:
        cmd = os.path.basename(sys.argv[0])
        print
        print _("Usage: {0} delete <name>").format(cmd,sys.argv[1])
        print

def cmd_edit():
    '''
    Edit configuration walking through accounts one by one
    '''
    if len(sys.argv)>2:
        name = sys.argv[2]
    else:
        name = None
    gui.settings(name)
    print

def cmd_list():
    '''
    List the configured sessions
    '''
    gui.config()
    print

def cmd_help():
    '''
    Show help
    '''
    cmd = os.path.basename(sys.argv[0])
    print
    print _("Localbox desktop sync version {}").format(lox.VERSION)
    print
    print _("Usage: {} [command]").format(cmd)
    print
    for c in commands.iterkeys():
        (f,description) = commands[c]
        print "  {0:12} - {1}".format(c,description)
    print
    sys.exit(0)

def cmd_invitations():
    '''
    Show invirtations for each session
    '''
    need_sessions()
    config.load()
    daemon = Supervisor(pidfile, path=os.environ['HOME'], umask=100, stdout=logfile, stderr=logfile)
    print
    print _("Localbox invitations")
    for name in config.settings.iterkeys():
        print
        print _("Session '{}': ").format(name)
        try:
            api = LoxApi(name)
            invitations = api.invitations()
            for invite in invitations:
                share = invite[u'share']
                item = share[u'item']
                print "id=%s: '%s' (%s)" % (invite[u'id'],item[u'path'],invite[u'state'])
        except IOError as e:
            print
            print _("Error: {}").format(str(e))
            print
        else:
            print
    sys.exit(0)

def cmd_clean():
    '''
    Cleanup the config directory. TODO: cleanup session files as well
    '''
    if gui.ask(_("Are you sure to delete all configurations")):
        conf_dir = os.environ['HOME']+'/.lox'
        os.remove(os.path.join(conf_dir,"lox-client.conf"))
        os.remove(os.path.join(conf_dir,"lox-client.log"))
    print

def cmd_accept():
    pass

def cmd_revoke():
    pass

def cmd_about():
    lox.gui.about()

def cmd_usage():
    cmd = os.path.basename(sys.argv[0])
    print
    print _("Usage: {0} start|stop|run|status|help|... ").format(cmd)
    print
    sys.exit(22) # EINVAL

commands = {
                "start": (cmd_start,_("starts the client")),
                "stop": (cmd_stop,_("stops the client")),
                "run": (cmd_run,_("run in foreground (interactive)")),
                "restart": (cmd_restart,_("reloads the confguration")),
                "list": (cmd_list,_("list configured sessions")),
                "edit": (cmd_edit,_("edit configuration")),
                "delete": (cmd_delete,_("delete session from configuration")),
                "clean": (cmd_clean,_("cleanup configuration")),
                "status": (cmd_status,_("show the status of the client")),
                "invitations": (cmd_invitations,_("show invitations")),
                "accept": (cmd_accept,_("accept invitation")),
                "revoke": (cmd_revoke,_("revoke invitation")),
                "about": (cmd_about,_("about this application")),
                "help": (cmd_help,_("show this help"))
           }

def main():
    '''
    Main routine: call routine from command
    '''
    gettext.bindtextdomain('lox-client')
    gettext.textdomain('lox-client')
    cmd = sys.argv[1].lower() if len(sys.argv)>1 else cmd_usage()
    try:
        if commands.has_key(cmd):
            (func,description) = commands[cmd]
            func()
        else:
            print
            print _("Error: invalid command")
            cmd_usage()
            sys.exit(22) # EINVAL
    except (DaemonError, LoxError) as e:
        print
        print _("Error: {}").format(str(e))
        print
        sys.exit(5) # EIO
    except KeyboardInterrupt as e:
        print
        print _("Error: interrupted")
        print
        sys.exit(4) # EINTR
    except Exception as e:
        print
        print _("Error: {}").format(str(e))
        print
        traceback.print_exc()
        sys.exit(1) # EPERM
