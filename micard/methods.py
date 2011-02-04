# python-micard's method factory code is based on tweepy's, though modifications have
# been made.
# The following notice is included in accordance with the terms of the MIT 
# license:
#
# MIT License
# Copyright (c) 2009-2010 Joshua Roesslein
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import httplib
import urllib
import time
import re
import simplejson

from error import MicardError
from utils import convert_to_utf8_str, is_iterable

def method_factory(**config):
    class APIMethod(object):
        path = config['path']
        allowed_param = config.get('allowed_param', [])
        method = config.get('method', 'GET')
        require_auth = config.get('require_auth', False)

        def __init__(self, api, args, kargs):
            # If authentication is required and no credentials
            # are provided, throw an error.
            if self.require_auth and not api.auth:
                raise MicardError('Authentication required!')

            self.api = api
            self.post_data = kargs.pop('post_data', {})
            if self.method == 'POST':
                self.headers = kargs.pop('headers', \
                    {"Content-type":"application/x-www-form-urlencoded",
                     "Accept": "text/plain"}
                )
                
            else:
                self.headers = kargs.pop('headers', {})
                
            if self.method == 'POST':
                self.build_post_body(args, kargs)
            else:
                self.build_parameters(args, kargs)
                
            self.path = self.api.api_root + self.path
        
        def build_post_body(self, args, kargs):
            self.parameters = {}
            
            if not self.post_data == {}:
                return
            
            post_body = []
            
            for idx, arg in enumerate(args):
                if arg is None:
                    continue
                
                try:
                    if not is_iterable(arg):
                        post_body.append((self.allowed_param[idx], arg))
                    else:
                        for value in arg:
                            post_body.append((self.allowed_param[idx], value))
                except:
                    raise MicardError('Too many parameters supplied!')
                
            for k, arg in kargs.items():
                if arg is None:
                    continue
                
                if not is_iterable(arg):
                    post_body.append((k, arg))
                else:
                    for value in arg:
                        post_body.append((k,value))
            
            self.post_data = post_body
            
        def build_parameters(self, args, kargs):
            self.parameters = {}
            for idx, arg in enumerate(args):
                if arg is None:
                    continue

                try:
                    self.parameters[self.allowed_param[idx]] = convert_to_utf8_str(arg)
                except IndexError:
                    raise MicardError('Too many parameters supplied!')

            for k, arg in kargs.items():
                if arg is None:
                    continue
                if k in self.parameters:
                    raise MicardError('Multiple values for parameter %s supplied!' % k)

                self.parameters[k] = convert_to_utf8_str(arg)

        def execute(self):
            # Build the request URL
            url = self.path
            if len(self.parameters):
                url = '%s?%s' % (url, urllib.urlencode(self.parameters))
            
            if self.api.host.startswith('https'):
                conn = httplib.HTTPSConnection(self.api.host[8:])
            else:
                conn = httplib.HTTPConnection(self.api.host[7:])
            
            if self.method == 'POST':
                data = self.post_data
            else:
                data = self.parameters
                
            # Apply authentication
            if self.api.auth and self.require_auth:
                self.api.auth.apply_auth(
                        self.api.host + url,
                        self.method, self.headers, data
                )

            # Execute request
            try:
                conn.request(self.method, url, headers=self.headers, body=urllib.urlencode(self.post_data))
                resp = conn.getresponse()
            except Exception, e:
                raise MicardError('Failed to send request: %s' % e)

            if not resp.status in (200, 201, 204,):
                error_msg = "miCARD error response: status code = %s" % resp.status
                raise MicardError(error_msg, resp)

            # Parse the response payload
            try:
                result = simplejson.loads(resp.read())
            except:
                result = True
                
            conn.close()

            return result


    def _call(api, *args, **kargs):

        method = APIMethod(api, args, kargs)
        return method.execute()
    
    return _call