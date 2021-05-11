#!/bin/bash

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -------------------------------------------------------------------

# Generate private key and gGenerate CSR 
cat > csr_details.txt <<-EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn
 
[ dn ]
C=FR
ST=CALVADOS
L=CAEN
O=ExtensiveAutomation
OU=ExtensiveAutomation.org
emailAddress=d.machard@gmail.com
CN=demo.extensiveautomation.org 
 
[ req_ext ]
subjectAltName = @alt_names
 
[ alt_names ]
DNS.1 = www.extensiveautomation.org
DNS.2 = www.extensive-automation.org
DNS.3 = demo.extensive-automation.org
EOF
openssl req -new -nodes -sha256 -out ca.csr -newkey rsa:2048 -keyout ca.key -extensions req_ext -config <( cat csr_details.txt )

# Generate Self Signed Key
openssl x509 -req -sha256 -days 730 -in ca.csr -signkey ca.key -out ca.crt -extfile <( cat csr_details.txt )

# Remove CSR
rm -rf ca.csr
rm -rf csr_details.txt
