'''
Description:

    Module for lox-client configuration. Not a class so not needed to
    instantiate throughout the application. Globally loads or saves the client
    configuration with the load() and save() functions. The configuration
    can be accessed as a dict of session settings through the variable named
    settings. Each session entry in the dict is again a dict of name/value
    pairs. At both levels all dict oprations apply. Metadata about settings is
    found in the variable METADATA.

    The configuration contains account information and is therefore encrypted
    using scrypt() before stored as a pickle. The module stores the passphrase
    for convenience in memory. For now it is considered that the user defines
    only one passphrase for all accounts. And we want that the program only
    asks once for it. Therefore it is a module variable. Any attempt to hide
    is not the slightest secure, because Python is an extremely introspective
    scripting language. With the non mutable state of objects in mind the
    passphrase is copied by stack (passed as parameter) as much as possible.


Usage:

    import config # note that the config is not loaded yet

    config.load() # exits when user does not enter correct password
    user = config.settings['localhost']['username']
    config.settings['localhost']['username'] = 'newuser'
    config.save()
    if 'local_dir' in config.settings['localhost'].changed():
        # do something because changeing the directory
        # without flushing the cache is like 'rm -r *'

'''

import sys
import os
import base64
import pickle
import scrypt
import ConfigParser
import collections
from lox.error import LoxError
import lox.gui
import gettext
_ = gettext.gettext

#                name         description                          default   type
METADATA = [
                ("local_dir", _("Local directory to synchronize"),    "",       "text"),
                ("lox_url",   _("URL of the Localbox server"),        "",       "text"),
                ("auth_type", _("Authentication type"),               0,        ["localbox","oauth2","saml"]),
                ("encrypt",   _("Encrypt new folders by default"),    0,        ["yes","no"]),
                ("username",  _("Account username"),                  "",       "text"),
                ("password",  _("Account password"),                  "",       "text"),
                ("interval",  _("Time (s) between synchronizations"), 300,      "int"),
                ("log_level", _("Log level"),                         1,        ["none","error","warn","info","debug","traffic"])
           ]


class SectionSettings(collections.MutableMapping):
    '''
    A dictionary that keeps track of changes
    Deletion of keys is not supported
    '''
    def __init__(self):
        '''
        Initialize with default settings
        '''
        self._store = dict()
        self._changed = set()
        for (key,caption,default,ext) in METADATA:
            if type(ext) is list:
                self._store[key] = ext[default]
            else:
                self._store[key] = default
        #self.update(dict(DEFAULT))
        self.confirm()

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        '''
        Keep track of changed settings
        '''
        self._store[key] = value
        self._changed.add(key)

    def __delitem__(self, key):
        pass

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def changed(self):
        '''
        Return changed settings
        '''
        return self._changed

    def confirm(self):
        '''
        Accept changed settings
        '''
        self._changed = set()

class Sections(collections.MutableMapping):
    '''
    A dictionary that never gives a KeyError
    Deletion of keys is not supported
    '''
    def __init__(self):
        self._store = dict()

    def __getitem__(self, key):
        global _loaded
        if not _loaded:
            raise ValueError('Configuration not loaded')
        if not self._store.has_key(key):
            self._store[key] = SectionSettings()
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        pass

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def has_key(self, key):
        return self._store.has_key(key)

    def iterkeys(self):
        return self._store.iterkeys()

    def pop(self, key):
        return self._store.pop(key, None)

_loaded = False

def load():
    '''
    Load the config file as the current settings,
    all previous settings are flushed
    '''
    global settings
    global _loaded
    settings = Sections()
    conf_dir = os.environ['HOME']+'/.lox'
    if not os.path.isdir(conf_dir):
        os.mkdir(conf_dir)
    if not os.path.isfile(conf_dir+"/lox-client.conf"):
        print
        print _("Creating an empty config file ...")
        # -- ConfigParser create of dict()
        #save()
        # -- encrypted pickle create of dict()
        f = open(conf_dir+"/lox-client.conf",'ab+')
        serialized = pickle.dumps(Sections())
        encrypted = scrypt.encrypt(serialized,new_passphrase(),maxtime=0.2)
        f.write(encrypted)
        f.close()
        print
    else:
        f = open(conf_dir+"/lox-client.conf",'rb')
        # -- ConfigParser load of dict()
        #config = ConfigParser.RawConfigParser()
        #config.readfp(f)
        #for session in config.sections():
        #    settings[session] = SectionSettings()
        #    for key,value in config.items(session):
        #        settings[session][key] = value
        # -- encrypted pickle load of dict()
        retries = 0
        encrypted = f.read()
        while True:
            try:
                serialized = scrypt.decrypt(encrypted,passphrase(retries>0),maxtime=0.2)
                settings = pickle.loads(serialized)
                break
            except scrypt.error:
                retries += 1
                if retries<3:
                    lox.gui.error(_("Invalid password, try again"))
                    pass
                else:
                    lox.gui.error(_("Invalid password still, quitting."))
                    sys.exit(13) # EACCESS
        f.close()
    _loaded = True

def save():
    '''
    Load the current settings to the config file
    '''
    global settings
    conf_dir = os.environ['HOME']+'/.lox'
    if not os.path.isdir(conf_dir):
        os.mkdir(conf_dir)
    path = os.environ['HOME']+'/.lox/lox-client.conf'
    f = open(path, 'wb')
    # -- ConfigParser save of dict()
    #config = ConfigParser.RawConfigParser()
    #for session,d in settings.iteritems():
    #    config.add_section(session)
    #    for item,value in d.iteritems():
    #        config.set(session,item,value)
    #config.write(f)
    # -- encrypted pickle save of dict()
    serialized = pickle.dumps(settings)
    encrypted = scrypt.encrypt(serialized,passphrase(),maxtime=0.2)
    f.write(encrypted)
    f.close()

_passphrase = None

def passphrase(retry=False):
    '''
    Return passphrase
    '''
    global _passphrase
    if _passphrase is None or retry:
        _passphrase = base64.b64encode(lox.gui.get_password())
    return base64.b64decode(_passphrase)

def new_passphrase():
    '''
    Ask new passprase and return that one
    '''
    global _passphrase
    _passphrase = base64.b64encode(lox.gui.new_password())
    return base64.b64decode(_passphrase)

settings = Sections()
#load()

