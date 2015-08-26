'''
Module levert een eenvoudige cache gebaseerd op shelve
Bij openen wordt gecontroleerd op versienummer en
of het dezelfde directory betreft, anders wordt de cache
geleegd (want niet geldig).

Usage:
    s = LoxCache(name) # determines location from config
    s["key"] = "values" # automatically does sync()
    del s["key"] # okay even if key does not exist

'''

import os
import lox.config as config
from lox.api import LoxApi
from shelve import DbfilenameShelf

class LoxCache(DbfilenameShelf):

    # default to newer pickle protocol and writeback=True
    def __init__(self, name, logger):
        filename = os.environ['HOME'] + '/.lox/.' + name + '.cache'
        DbfilenameShelf.__init__(self, filename, protocol=2, writeback=True)
        api = LoxApi(name)
        api_version = api.version()
        config_dir = config.settings[name]['local_dir']
        try:
            my_dir = self.get('local_dir',None)
            assert config_dir == my_dir
            my_version = self.get('version',None)
            assert api_version == my_version
        except AssertionError:
            # Cache is considered not safe, so re-initialized
            logger.warn("Initializing cache")
            self.clear()
            self[u'local_dir'] = config_dir
            self[u'version'] = api_version

    #def __del__(self):
    #    self.close()

    def get(self,name,default=None):
        key = name.encode('utf8')
        if DbfilenameShelf.has_key(self,key):
            return DbfilenameShelf.__getitem__(self, key)
        else:
            return default


    def __setitem__(self, name, value):
        key = name.encode('utf8')
        DbfilenameShelf.__setitem__(self, key, value)
        self.sync()

    def __getitem__(self, name):
        key = name.encode('utf8')
        value = DbfilenameShelf.__getitem__(self, key)
        return value

    def __delitem__(self, name):
        key = name.encode('utf8')
        if DbfilenameShelf.has_key(self,key):
            DbfilenameShelf.__delitem__(self, key)
            self.sync()
