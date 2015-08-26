try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
#from distutils.core import setup
from distutils import cmd
from distutils.command.install_data import install_data as _install_data
from distutils.command.build import build as _build
from distutils.core import setup
from babel.messages import frontend as babel
import lox

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    description = lox.DESCRIPTION,
    long_description = readme()
    author = lox.AUTHOR,
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: EUPL-1.1',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
    keywords='desktop sync secure cloud storage',
    url = 'http://github.com/2EK/Linux-Sync',
    download_url = 'https://github.com/2EK/Linux-Sync/archive/master.zip',
    author_email = lox.AUTHOR_EMAIL,
    version = lox.VERSION,
    packages = ['lox','lox.gui'],
    install_requires = [
        'iso8601',
        'gnupg'
    ],
    data_files = [
        ('/usr/share/locale/nl/LC_MESSAGES',["build/locale/nl/LC_MESSAGES/lox-client.mo"]),
        ('/usr/share/locale/fy/LC_MESSAGES',["build/locale/fy/LC_MESSAGES/lox-client.mo"]),
        ('/usr/share/applications',["lox-client.desktop"]),
        ('/usr/share/icons',["lox/gui/localbox_256.png"])
    ],
    package_data = {
        'lox.gui': ['*.png']
    },
    scripts = ['lox-client'],
    name = 'lox-client'
)

