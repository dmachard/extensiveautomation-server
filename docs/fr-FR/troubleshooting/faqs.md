---
name: FAQs
---

# FAQs

* [How to debug server after bad installation?][faqs#how-to-debug-server-after-bad-installation]
* [How to display the version of the server?][faqs#how-to-display-the-version-of-the-server]
* [How to install the server in a specific folder?](faqs#how-to-install-the-server-in-a-specific-folder)
* [How to fix elliptic curve error on toolbox connection?](faqs#how-to-fix-elliptic-curve-error-on-toolbox-connection)
* [How to accept connections on server side on another port than tcp 443?](faqs#how-to-accept-connections-on-server-side-on-another-port-than-tcp-443)
* [Read a test file as a simple text file](faqs#read-a-test-file-as-a-simple-text-file)
* [Error during test design generation](faqs#error-during-test-design-generation)
* [Sikulix or Selenium agents does not start on Windows 10 Family version](faqs#sikulix-or-selenium-agents-does-not-start-on-windows-10-family-version)
* [Installation stucked on adding external libraries ](faqs#installation-stucked-on-adding-external-libraries)

## How to debug server after bad installation

If the server does not start after a from sratch installation, please to follow the procedure

1. Edit the file /opt/xtc/current/Var/Logs/output.log and search "ERROR" tags, if no errors exists take a look to the installation file logs

2. Edit the file /root/ExtensiveTesting-XX-XX-XX/install.logs, search ERROR or FATAL messages.

3. If errors are not explicit, please to retrieve theses logs and provide them to the main developer throught the support page.


## How to display the version of the server

Connect as root on your test server and execute the following command

```
# xtctl version
Server version: 16.0.0
```

## How to install the server in a specific folder

By default the product is installed in `/opt/xtc/`, to change this folder:

* Edit the file `default.cfg`
* Update the key `INSTALL` with the destination folder

```
INSTALL=/opt/xtc/
```

## How to fix elliptic curve error on toolbox connection

The following error can occurred when the server is running with `Apache 2.4` and the toolbox running with `Python 2.6`.

```
[Errno 1] _ssl.c:490: error:100AE081:elliptic curve routines:EC_GROUP_new_by_curve_name:unknown group.
```

To fix this error (be aware, this is just a workaround!), you need to disable all elliptic curves cipher on apache. 
Edit the virtual host dedicated and add the following line.

```
SSLCipherSuite HIGH:MEDIUM:!aNULL:!MD5:!ECDH:!ECDHE:!AECDH
``` 

## How to accept connections on server side on another port than tcp 443

### On server side

1. Edit the HTTP configuration file `/etc/httpd/conf.d/extensivetesting.conf` and find the following virtual host

    ```
    <VirtualHost *:443>
    .....
    </VirtualHost>
    ```

2. Replace the port `443` by the new one `MY_NEW_PORT`

    ```
    <VirtualHost *:MY_NEW_PORT>
    .....
    </VirtualHost>
    ```

3. Also edit the general configuration `/etc/httpd/conf/httpd.conf` of apache to listen on this new port

4. Restart apache

### On client side

1. Go to `File > Preferences > Networking`

2. Update fields `tcp/data` and `tcp/api` with the new port `MY_NEW_PORT`
    ![](/docs/images/preferences_network_ports.png)

3. Save changes and connect as usual

### On toolbox side

1. Edit the file configuration file `settings.ini`

2. Replace the following keys in the section `[server]` with the new port `MY_NEW_PORT`

    ```
    port = 443
    port-xmlrpc = 443
    ```

3. Save the file and restart the toolbox as usual.

## Read a test file as a simple text file

Execute the following command from the server to extract xml content from a test file without the client

```
openssl zlib -d -in 00_Wait.tux > 00_Wait.xml
```

## Error during test design generation

Generate the test design can be impossible because of several reasons.
Please to check if :

- the version of adapters and libraries used in your test is correct (good versions ? syntax error in your adapter ? )
- No syntax error exists in your test ?
- The cache feature is used in the initialization of your steps ? in this case the design can be generated only after the execution of your test

## Sikulix or Selenium agents does not start on Windows 10 Family version

Users report a issue to start the sikulix/selenium agents on the windows family version. 
I am not able to fix this issue because I don't have a Windows family version so if you want to help to fix this issue, make a donation throught Paypal.

## Installation stucked on adding external libraries 

If the installation is struck on the adding external libraries step, then perphaps it is because the process "yum" is already running and busy.
Take a look the installation log and check if you have the following error:

```
Repodata is over 2 weeks old. Install yum-cron? Or run: yum makecache fast
Existing lock /var/run/yum.pid: another copy is running as pid 3293.
Another app is currently holding the yum lock; waiting for it to exit...
  The other application is: PackageKit
    Memory :  26 M RSS (429 MB VSZ)
    Started: Tue Nov  1 11:09:25 2016 - 00:42 ago
    State  : Sleeping, pid: 3293
```

Workaround: kill manually the yum process and try to reinstall the product.


## Unable to navigate in the web interface

The login is successful but unable to navigate in the web interface. Please to check the date and time of your server.
The cookie generated by the server can be outdated.

