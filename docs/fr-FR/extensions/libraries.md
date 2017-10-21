---
name: Sut Libraries
---

# Sut Libraries

* [Introduction](libraries#introduction)
* [Select libraries in your test](libraries#select-libraries-to-use-in-your-test)
* [Make set of libraries as default](adapters#make-set-of-libraries-as-default)
* [List of available libraries](libraries#list-of-available-libraries)

## Introduction

Libraries must be used directly from a test or from libraries. Libraries are regrouped in one package (tar.gz). 
You can have several packages of libraries in your test server.

## Select libraries to use in your test

You can select the set of libraries to use in your test. This feature can be useful to have a branch for developement and a stable libraries.

1. From the client, create a new test and go to the test properties part 

2. Click on the `Test Design` tabulation and locate the `Libraries` option

3. Double click on it and select the version to use

## Make set of libraries as default

When you have several set of libraries, you can define one as default for testers. Follow the procedure below. 
 
1. From the client, go to the part `Module Listing > Libraries`

2. Select your set of libraries to put as default

3. Right click on it and click on the option `Set as default`

4. Repackage the libraries to save your change

## List of available libraries

List of available Libraries:

|Family|Name|Description|
|:---|---:|:---------|
|**Authentication**|||
||Basic|Basic generator|
||Digest|Digest generator|
||Hmac|Hmac generator|
||Oauth|Oauth generator|
||Wsse|Wsse generator|
|**Ciphers**|||
||AES|Encrypt or decrypt data with AES cipher|
||Blowfish|Encrypt or decrypt data with Blowfish cipher|
||OpenSSL|Wrapper to the openssl library|
||RC4|Encrypt or decrypt data with RC4 cipher|
||XOR|Encrypt or decrypt data with XOR cipher|
|**Codecs**|||
||Base64|Encode or decode data in base64|
||Excel|Read excel file|
||G711A|A-Law audio encoder and decoder.|
||G711U|U-Law audio encoder and decoder.|
||JSON|JSON Decoder/Encoder|
||XML|XML Decoder/Encoder|
|**Compression**|||
||GZIP|Compress or uncrompress with Gzip|
|**Misc**|||
||Dummy|Just a library example|
|**Hashing**|||
||CRC32|Compute a CRC-32 (Cyclic Redundancy Check) algorithm.|
||Checksum|Compute a checksum.|
||HMAC MD5|Compute a message authentication code (MAC) involving a cryptographic hash function in combination with a secret cryptographic key.|
||HMAC SHA1|Compute a message authentication code (MAC) involving a cryptographic hash function in combination with a secret cryptographic key.|
||HMAC SHA256|Compute a message authentication code (MAC) involving a cryptographic hash function in combination with a secret cryptographic key.|
||MD5|Compute the RSA's MD5 (Message-Digest) algorithm.|
||SHA1|Compute the SHA-1 cryptographic hash.|
||SHA256|Compute the SHA-2 256 cryptographic hash.|
||SHA512|Compute the SHA-2 512 cryptographic hash.|
|**Identifiers**|||
||SessionID|Generate session ID|
||UUIDS|Generate UUIDs (Universally Unique IDentifier).|
|**Media**|||
||ChartsJS|Chart.js library generator|
||DialTones|Dial tones generator|
||Image|Manipulate image|
||Noise|Noise generator|
||SDP|Encode or decode sdp and contructs sdp offer and answer.|
||WavContainer|Wav file container|
||Waves|Waves generator|
|**Time**|||
||Timestamp|Get seconds since epoch (UTC).|
|**Units**|||
||Bytes|Bytes converter|