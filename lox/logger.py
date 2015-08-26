'''

Module for logging sessions

Usage:

    Create an instance per session.

    Info messages and critical messages are shown always.

    Info messages are logged to the log file alone,
    other messages are printed to the console as well
    when running interactive.

    Critical messages also generate a messagebox in
    the GUI.

'''
import os
from datetime import datetime
import lox.config
import lox.gui


(INFO, CRITICAL, ERROR, WARN, DEBUG) = (0, 1, 2, 3, 4)
LOGLEVELS = ["info", "critical", "error", "warn", "debug"]

class LoxLogger:
    '''
    Logger class
    '''

    def __init__(self, name):
        '''
        Constructor: open logfile and initialize
        '''
        self.__name = name
        self.__log_file = os.environ['HOME']+'/.lox/.'+name+'.log'
        self.__handle = open(self.__log_file, 'a')
        try:
            self.__log_level = LOGLEVELS.index(lox.config.settings[name]['log_level'])
        except KeyError:
            self.__log_level = ERROR

    #def __del__(self):
    #    '''
    #    Destructor: close logfile
    #    '''
    #    self.__handle.close()

    def __log(self, level, msg, console_msg=True):
        '''
        Print message
        '''
        datetime_now = datetime.now()
        self.__handle.write('{:%Y-%m-%d %H:%M:%S}'.format(datetime_now))
        self.__handle.write(' - [{0}] '.format(level))
        self.__handle.write(msg)
        self.__handle.write(os.linesep)
        self.__handle.flush()
        if console_msg:
            print "({0}) {1}".format(self.__name, msg)

    def set_level(self, level):
        '''
        Set logging level
        '''
        self.__log_level = level

    def info(self, msg):
        '''
        Send message to logfile only regardless of loglevel
        '''
        self.__log("INFO", msg, console_msg=True)

    def critical(self, msg):
        '''
        Send critical message to logfile and console
        '''
        self.__log("CRITICAL", msg)
        lox.gui.error(msg)

    def error(self, msg):
        '''
        Send error message to logfile and console
        '''
        if self.__log_level >= ERROR:
            self.__log("ERROR", msg)

    def warn(self, msg):
        '''
        Send warning message to logfile and console
        '''
        if self.__log_level >= WARN:
            self.__log("WARN", msg)

    def debug(self, msg):
        '''
        Send debug message to logfile and console
        '''
        if self.__log_level >= DEBUG:
            self.__log("DEBUG", msg)


