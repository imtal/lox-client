'''
Module that implements a daemon class where
the Python program runs as a Unix daemon

Usage:

    from daemon import Daemon

    class MyDaemon(Daemon):

        def run():
            # do my daemon stuff here
            pass

'''

import sys
import os
import time
import atexit
import signal

class DaemonError(Exception):
    def __init__(self,reason):
        self.value = reason
    def __str__(self):
        return self.value


class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() and signal() methods
    """
    def __init__(self, pidfile, path=None, umask=0, stdin=None, stdout=None, stderr=None, preserve=[]):
        self.pidfile = pidfile
        devnull = os.devnull if (hasattr(os,"devnull")) else "/dev/null"
        self.stdin = devnull if (stdin is None) else stdin
        self.stdout = devnull if (stdout is None) else stdout
        self.stderr = devnull if (stderr is None) else stderr
        self.path = os.environ['HOME'] if (path is None) else path
        self.path = path
        self.umask = umask
        self.preserve = preserve
        self._restart = False

    def __daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        pid = os.fork()
        if pid > 0:
            # This is the first parent
            sys.exit(0)
        # Decouple from parent environment
        os.chdir(self.path)
        os.setsid()
        os.umask(self.umask)

        # do second fork
        pid = os.fork()
        if pid > 0:
            # This is the second parent
            sys.exit(0)

        # run started before redirecting I/O
        self.started(restart = self._restart)
        self._restart = False
        '''
        # Close all open file descriptors
        import resource # Resource usage information.
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if (maxfd == resource.RLIM_INFINITY):
            maxfd = 1024
        for fd in range(0, maxfd): # Iterate through and close all file descriptors
            #if not fd in self.preserve:
                try:
                    os.close(fd)
                except OSError: # On error, fd wasn't open to begin with (ignored)
                    pass
        '''
        # Redirect standard I/O file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdin = open(self.stdin, 'r')
        sys.stdout = open(self.stdout, 'a+')
        sys.stderr = open(self.stderr, 'a+', 0)
        # Create the pidfile
        pid = str(os.getpid())
        with open(self.pidfile,'w+') as f:
            f.write("{0}\n".format(pid))

        # Register handler at SIGTERM and exit
        #signal.signal(signal.SIGTERM,self.__cleanup)
        atexit.register(self.__cleanup)

    def __cleanup(self):
        self.terminate()
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except Exception as e:
            raise(e)

        if pid:
            raise DaemonError('already running')

        # Start the daemon
        self.__daemonize()
        self._restart = False
        self.run()
        self.__cleanup()

    def stop(self):
        """DaemonError('
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            raise DaemonError('not running')

        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

        # Try killing the daemon process
        if pid==os.getpid():
            os.remove(self.pidfile)
            sys.exit(0)
        else:
            try:
                while 1:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.1)
            except OSError as e:
                error = str(e)
                if error.find("No such process") == 0:
                    raise DaemonError(error)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self._restart = True
        self.start()

    def status(self):
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
            return pid
        except IOError:
            return None

    def started(self, restart):
        """
        Override this method when you subclass Daemon.
        It will be called by the parent process after the process has been
        daemonized by start() or restart().
        """
        pass

    def run(self):
        """
        Override this method when you subclass Daemon.
        It will be called by the child process after the process has been
        daemonized by start() or restart().
        """
        pass

    def terminate(self):
        """
        Override this method when you subclass Daemon.
        It will be called when the process is killed.
        """
        pass
