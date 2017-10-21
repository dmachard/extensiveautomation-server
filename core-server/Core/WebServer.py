#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2017 Denis Machard
# This file is part of the extensive testing project
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA
# -------------------------------------------------------------------

from Libs import Settings, Logger

import httplib2
import time 

def isUp():
    """
    Check if the web server if ready (apache)
    """
    try:
        # init the http 
        timeoutVal = Settings.getInt('Boot','timeout-http-server')
        http = httplib2.Http(timeout=timeoutVal, disable_ssl_certificate_validation=True, 
                            ca_certs="%s/Libs/cacerts.txt" % Settings.getDirExec() )
        http.add_credentials( Settings.get('Web','login'), Settings.get('Web','password') )
        http.force_exception_to_status_code = True
        scheme = 'http'
        portHttp = Settings.get('Web','http-port')
        if Settings.getInt('Web','https'):
            scheme = 'https'
            portHttp = Settings.get('Web','https-port')
        uri = '%s://%s:%s/%s/index.php' % ( scheme, Settings.get('Web','fqdn'), portHttp, Settings.get('Web', 'path') )
        
        timeout = False
        go = False
        startTime = time.time()
        while (not go) and (not timeout):
            # timeout elapsed ?
            if (time.time() - startTime) >= timeoutVal:
                timeout = True
            else:
                # test the web server
                Logger.debug("Get index: %s" % uri)
                resp, content = http.request(uri, "GET")
                if resp['status'] == '200':
                    Logger.debug( "200 OK received" )
                    go = True
                else:
                    Logger.debug( "response incorrect (%s)" % resp['status'] )
                    Logger.debug( "response (%s)" % resp )
                    Logger.debug( "response content (%s)" % content )
                    Logger.debug( "retry in %s second" % Settings.get('Web','retry-connect') )
                    time.sleep( int(Settings.get('Web','retry-connect')) )
        
        if timeout:
            raise Exception("timeout" )
            
    except Exception as e:
        raise Exception("server web not ready: %s" % str(e) )
