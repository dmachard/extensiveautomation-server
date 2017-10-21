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

import TestInteropLib
from TestInteropLib import doc_public

import requests
import xml.etree.ElementTree as ET

class Nexus(TestInteropLib.InteropPlugin):
    """
    Sonatype nexus plugin
    """
    @doc_public
    def __init__(self, parent, url, verifySsl=False, proxies={}):
        """
        Sonar nexus interop

        @param parent: testcase parent
        @type parent: testcase
        
        @param url: nexus server url
        @type url: string
        
        @param verifySsl: check ssl server cert (default=False)
        @type verifySsl: boolean
        
        @param proxies: proxies to use {'http': '', 'https': ''}
        @type proxies: dict
        """
        TestInteropLib.InteropPlugin.__init__(self, parent)
        
        self.__nexusUrl = url
        self.__certCheck = verifySsl
        self.__proxies = proxies
    @doc_public    
    def downloadArtefact(self, destFolder, groupId, artefactId, artefactVersion="LATEST", repositoryName="snapshots", packaging="jar"):
        """
        Download artefact and put it in a specific folder
        
        @param destFolder: destination folder of the downloaded artefact
        @type destFolder: string
        
        @param groupId: group id
        @type groupId: string
        
        @param artefactId: the artefact id to download
        @type artefactId: string
        
        @param artefactVersion: artefact version (default=LATEST)
        @type artefactVersion: string
        
        @param repositoryName: the repository name (default=snapshots)
        @type repositoryName: string
        
        @param packaging: packaging jar, war, ... (default=jar)
        @type packaging: string
        
        @return: filename on success, empty otherwise
        @rtype: boolean
        """
        ret = ''

        nexusUri = [ "/content/repositories/" ]
        nexusUri.append( "%s/" % repositoryName )
        nexusUri.append( "%s/" % groupId)
        nexusUri.append( "%s/" % artefactId)
        nexusUri.append( "maven-metadata.xml" )

        # log message
        content = {'nexus-url': self.__nexusUrl, 'cmd': 'download-artefact', 'nexus-reposity': repositoryName,
                  'artefact-id': artefactId, 'artefactVersion': artefactVersion, 'nexus-group': groupId }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="download-artefact", details=tpl )

        try:
            # get artefact url
            r = requests.get( "%s/%s" % (self.__nexusUrl, "".join(nexusUri)), headers={},
                                verify=self.__certCheck, proxies=self.__proxies)
            if r.status_code != 200:
                content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'resolve-artefact' }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="resolve artefact error", details=tpl )
            else:
                nexusDOM = ET.fromstring( r.text.encode("utf8") )
                if artefactVersion == "LATEST":
                    artefactVer  = nexusDOM.find("./versioning/latest").text
                else:
                    artefactVer = artefactVersion
                fileName = "%s-%s.%s" % (artefactId, artefactVer, packaging)

                # download it
                with open('%s/%s' % (destFolder, fileName), 'wb') as handle:
                    downloadUri = [ "/content/repositories/" ]
                    downloadUri.append( "%s/" % repositoryName )
                    downloadUri.append( "%s/" % groupId)
                    downloadUri.append( "%s/" % artefactId)
                    downloadUri.append( "%s/" % artefactVer)
                    downloadUri.append( "%s" % fileName )

                    r = requests.get("%s/%s" % (self.__nexusUrl, "".join(downloadUri) ), stream=True, headers={},
                                            verify=self.__certCheck, proxies=self.__proxies)
                    if r.status_code != 200:
                        content = {'response-code': "%s" % r.status_code, 'response-more': "%s" % r.text, 'cmd': 'download-artefact' }
                        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                        self.logResponse(msg="download artefact error", details=tpl )
                    else:
                        for block in r.iter_content(1024):
                            handle.write(block)
                        ret = fileName

                content = { "filename": "%s" % fileName, "cmd": "download-artefact" }
                tpl = self.template(name=self.__class__.__name__.upper(), content=content )
                self.logResponse(msg="artefact downloaded", details=tpl )

        except Exception as e:  # log message
            content = { "download-error": "%s" % e, "cmd": "download-artefact" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="download artefact exception", details=tpl )
        return ret
        