'''
Module with auxiliary functions
'''

import os
import binascii
from datetime import datetime
import iso8601


def to_timestamp(dt, epoch=datetime(1970,1,1,tzinfo=iso8601.UTC)):
    '''
    Convert a DateTime object to a Unix timestamp
    '''
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e6

def get_conflict_name(original):
    '''
    Generate a filename to resolve a conflict.
    An original name 'My Document.docx'
    returns 'My Document_conflict_3a28fd.docx'
    where '3a28fd' is a six digit random hex number
    '''
    base,ext = os.path.splitext(original)
    if base[-16:-6]=="_conflict_":
        base = base[:-16]
    x0 = os.urandom(3)
    x1 = binascii.hexlify(x0)
    # TODO: check if file exists and loop generating random extension until no conflict
    new_name =  "{0}_conflict_{1}{2}".format(base, x1, ext)
    return new_name

def get_tmp_name(original, state='download'):
    '''
    Get a temporary name for download.
    An original name 'My Document.docx'
    returns '.download_3a28fd.My Document.docx'
    where '3a28fd' is a six digit random hex number
    '''
    path,ext = os.path.splitext(original)
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    x0 = os.urandom(3)
    x1 = binascii.hexlify(x0)
    new_name = "{0}/.{4}_{1}.{2}{3}".format(dirname,x1,basename,ext,state)
    return new_name
