#!/bin/bash

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
# This file is part of the extensive automation project
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
OU=ExtensiveAutomation.ORG
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
