'''

Module that implements communication with a LocalBox store

Usage: create an instance per account


'''

from httplib import HTTPConnection, HTTPSConnection
import ssl
import sys
import urllib
import json
import urlparse

import lox.config
from lox.auth import Localbox
from lox.error import LoxError, LoxFatal


class LoxApiResponse:
    '''
    API abstraction class
    '''
    status = None
    headers = None
    reason = None
    body = None

class LoxApi:
    '''
    Class that forms the API to a LocalBox store.
    Each instance containts its own HTTP(S)Connection, can be used to
    manage multiple connections.
    API calls are based on version 1.1.5,
    version can not be checked at the moment
    '''

    def __init__(self, name):
        '''
        Initialize an API instance
        '''
        authtype = lox.config.settings[name]['auth_type']
        if authtype.lower() == 'localbox':
            self.auth = Localbox(name)
        else:
            raise LoxFatal('authentication type "{0}" not supported'.format(authtype))
        self.agent = {"Agent":"lox-client"}
        url = lox.config.settings[name]['lox_url']
        ref = urlparse.urlparse(url)
        self.server = ref.netloc
        self.port = ref.port
        self.uri_path = ref.path
        if ref.path[-1:] != '/':
            self.uri_path += '/'
        self.ssl = (ref.scheme == 'https')

    def __do_request(self, method, url, body="", headers={}):
        '''
        Actually to the request
        '''
        response = LoxApiResponse()
        if self.ssl:
            if sys.version_info > (2, 7, 9):
                ssl_context = ssl.create_default_context()
                ssl_context.verify_mode = ssl.CERT_NONE # make configurable!
                connection = HTTPSConnection(self.server, self.port, context=ssl_context)
            else:
                connection = HTTPSConnection(self.server, self.port)
        else:
            connection = HTTPConnection(self.server, self.port)
        connection.connect()
        connection.request(method, url, body, headers)
        r = connection.getresponse()
        response.status = r.status
        response.reason = r.reason
        response.body = r.read()
        response.headers = r.getheaders()
        connection.close()
        return response

    def identities(self, Begin):
        '''
        Query user identities
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "lox_api/identities/"+Begin
        resp = self.__do_request("GET", url, "", headers)
        if resp.status == 200:
            return json.loads(resp.body)
        else:
            raise LoxError(resp.reason)

    def get_user_info(self, name=None):
        '''
        Get user info
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "lox_api/user"
        if not name is None:
            url += "/"+name
        resp = self.__do_request("GET", url, "", headers)
        if resp.status == 200:
            return json.loads(resp.body)
        else:
            raise LoxError(resp.reason)

    def set_user_info(self, public_key, private_key='PRIVATE'):
        '''
        Set user info
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "lox_api/user"
        body = json.dumps({'public_key':public_key, 'private_key':private_key})
        resp = self.__do_request("POST", url, body, headers)
        if resp.status != 200:
            raise LoxError(resp.reason)
        else:
            resp.read()

    def meta(self, path):
        '''
        Get metadata
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "lox_api/meta/"+urllib.pathname2url(path)
        resp = self.__do_request("GET", url, "", headers)
        if resp.status == 200:
            return json.loads(resp.body)
        elif resp.status == 404:
            return None
        else:
            raise LoxError('lox_api/meta/ got {0}'.format(resp.status))

    def upload(self, path, content_type, body):
        '''
        Upload file
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        headers.update({"Content-Type":content_type})
        url = self.uri_path
        url += "lox_api/files"+urllib.pathname2url(path)
        resp = self.__do_request("POST", url, body, headers)
        if resp.status != 201:
            raise LoxError(resp.reason)

    def download(self, path):
        '''
        Download file
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "lox_api/files/"+urllib.pathname2url(path)
        resp = self.__do_request("GET", url, "", headers)
        if resp.status == 200:
            return resp.body
        else:
            raise LoxError(resp.reason)

    def create_folder(self, path):
        '''
        Create folder
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        headers.update({"Content-Type":"application/x-www-form-urlencoded"})
        url = self.uri_path
        url += "lox_api/operations/create_folder"
        body = "path="+urllib.pathname2url(path)
        resp = self.__do_request("POST", url, body, headers)
        if resp.status != 200:
            raise LoxError(resp.reason)

    def delete(self, path):
        '''
        Delete file or folder
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        headers.update({"Content-Type":"application/x-www-form-urlencoded"})
        url = self.uri_path
        url += "lox_api/operations/delete"
        body = "path="+urllib.pathname2url(path)
        resp = self.__do_request("POST", url, body, headers)
        if resp.status != 200:
            raise LoxError(resp.reason)

    def get_key(self, path):
        '''
        Get the key and iv of a folder
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "lox_api/key/"+urllib.pathname2url(path)
        resp = self.__do_request("GET", url, "", headers)
        if resp.status == 200:
            return json.loads(resp.body)
        else:
            raise LoxError(resp.reason)

    def set_key(self, path, key, iv, user=None):
        '''
        Attach an AES key and iv to a folder
        the key and iv need to be RSA encrypted with the public key of the user
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "lox_api/key/"+urllib.pathname2url(path)
        if user is None:
            body = json.dumps({u'key':key, u'iv':iv})
        else:
            body = json.dumps({'username':user, 'key':key, 'iv':iv})
        resp = self.__do_request("POST", url, body, headers)
        if resp.status != 200:
            raise LoxError(resp.reason)

    def key_revoke(self, path, user):
        '''
        Revoke a key
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "lox_api/key_revoke/"+urllib.pathname2url(path)
        body = json.dumps({'username':user})
        resp = self.__do_request("POST", url, body, headers)
        if resp.status != 200:
            raise LoxError(resp.reason)

    def invitations(self):
        '''
        Get invitations
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "lox_api/invitations"
        resp = self.__do_request("GET", url, "", headers)
        if resp.status == 200:
            return json.loads(resp.body)
        else:
            raise LoxError(resp.reason)

    def invite_accept(self, ref):
        '''
        Accept invitation
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "lox_api/invite/"+ref+"/accept"
        resp = self.__do_request("POST", url, "", headers)
        if resp.status == 200:
            return json.loads(resp.body)
        else:
            raise LoxError(resp.reason)

    def invite_revoke(self, ref):
        '''
        Revoke invitation
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "lox_api/invite/"+ref+"/revoke"
        resp = self.__do_request("POST", url, "", headers)
        if resp.status == 200:
            return resp.body
        else:
            raise LoxError(resp.reason)

    def notifications(self):
        '''
        Read notifications, not part of API
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "notifications/unread/"
        headers.update({"X-Requested-With":"XMLHttpRequest"})
        resp = self.__do_request("GET", url, "", headers)
        if resp.status == 200:
            return json.loads(resp.body)
        else:
            raise LoxError(resp.reason)

    def register_app(self):
        '''
        Not an actual API call?
        Strange implementation because needs other authentication
        '''
        headers = self.auth.header()
        headers.update(self.agent)
        url = self.uri_path
        url += "register_app"
        #headers.update({"Cookie":"PHPSESSID=8spg15vollt3eqjh7i9kpggog5; REMEMBERME=UmVkbm9zZVxGcmFtZXdvcmtCdW5kbGVcRW50aXR5XFVzZXI6WVdSdGFXND06MTQ0NzE5MTc0ODowOTJlMGQwZDJlMDFlZWYwMzJkMzdmMmUwMmEwMWJlYmQ4N2U3NjI4MDkyOTVjYzRiNGRlYzJmZDI1NzU0OTdh
        resp = self.__do_request("GET", url, "", headers)
        if resp.status == 200:
            return json.loads(resp.body)
        else:
            raise LoxError(resp.reason)

    def version(self):
        '''
        Version can up to 1.1.17b not be obtained from API
        '''
        return "1.1.17b"
