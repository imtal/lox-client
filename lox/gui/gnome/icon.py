'''
Helper function for icons
'''


import os


def icon(ref='localbox',size=32):
    this = os.path.realpath(__file__)
    path = os.path.dirname(this)
    filename = '{0}_{1}.png'.format(ref,size)
    full_path = os.path.join(path,filename)
    return full_path
