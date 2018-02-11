#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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

BIN_SENDMAIL = "/usr/sbin/sendmail"

class Email(TestInteropLib.InteropPlugin):
    """
    Email plugin
    """
    @doc_public
    def __init__(self, parent):
        """
        Email interop
        
        @param parent: testcase parent
        @type parent: testcase
        """
        TestInteropLib.InteropPlugin.__init__(self, parent)
    @doc_public
    def send(self, toAddr, subject, body='', attachment=None, attachmentName="interop.txt", fromAddr="interop@extensivetesting.org"):
        """
        Send email in html format.
        Attachment file can be added
        
        @param toAddr: destination address
        @type toAddr: string     
        
        @param subject: subject of the email
        @type subject: string   
        
        @param body: email content
        @type body: string   
        
        @param attachment: content of the attachment file (default=None)
        @type attachment: string/none
        
        @param attachmentName: name of the attachment file (default=interop.txt)
        @type attachmentName: string 
        
        @param fromAddr: from address (default=interop@extensivetesting.org)
        @type fromAddr: string     
        """
        # log message
        content = {'cmd': 'sending' }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="sending email", details=tpl )

        try:
            p = os.popen("%s -t" % BIN_SENDMAIL, "w")
            p.write("From: %s\n" % fromAddr)
            p.write("To: %s\n" % toAddr)
            p.write("Subject: %s\n" % subject.encode('utf-8'))
            
            p.write("Content-Type: multipart/mixed; boundary=\"-q1w2e3r4t5\"\n")
            p.write("MIME-Version: 1.0\n")
            p.write("\n")
            
            p.write("---q1w2e3r4t5\n")
            p.write("Content-Type: text/html\n")
            p.write("Content-Disposition: inline\n")
            p.write("\n")
            p.write("<html><body>%s</body></html>\n" % body.encode('utf-8') )
            
            if attachment is not None:
                p.write("---q1w2e3r4t5\n")
                p.write("Content-Transfer-Encoding: base64\n")
                p.write("Content-Type: application/octet-stream; name=%s\n" % attachmentName)
                p.write("Content-Disposition: attachment; filename=%s\n" % attachmentName)
                p.write("\n")
                p.write(base64.b64encode(attachment.encode("utf-8")))
                p.write("\n")
            
            p.write("---q1w2e3r4t5--")
            p.write()

            status = p.close()
            if status is not None:
                if status != 0 :
                    pass #error
                else:
                    pass # mail sent!
                    
            content = {'cmd': 'sending' }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content)
            self.logResponse(msg="email sent", details=tpl  )
            
        except Exception as e:
            content = {'cmd': 'sending' }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="sending email error", details=tpl )
            
            
            