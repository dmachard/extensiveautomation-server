---
name: Installation Guide
---

# Installation

* [Installer for Windows](installation#installer-for-windows)
* [Portable version for Windows](installation#portable-version-for-windows)
* [Package for Linux](installation#package-for-linux)

## Installer for Windows

1. Connect to the test center and go to the menu `Overview > Packages > Toolbox`. Download the toolbox package according to your environment (Windows or Linux)

    ![](/docs/images/web_overview_pkgs4.png)
    
2. Execute the package `ExtensiveTestingToolbox_XX.XX.XX_<32bit|64bit>_Setup.exe`

3. Accept the license

    ![](/docs/images/toolbox_step1.png)
    
4. Select components to install, select all by default

    ![](/docs/images/toolbox_step2.png)
    
5. Follow steps of the wizard installation. The installation takes some minutes.  When the installation is terminated, open-it! A shortcut is also available on your desktop. The toolbox is automatically installed on the startup folder of the operating system.

    ![](/docs/images/toolbox_offline.png)
    
## Portable version for Windows

1. Use the portable version if you have restricted rights on your Windows pc. Go to your online test center and navigate in the menu to `Overview > Packages`. Download the portable version.

    ![](/docs/images/web_overview_pkgs3.png)
    
2. Unzip the file `ExtensiveTestingToolbox_XX.XX.XX_<32bit|64bit>_Portable.zip` and go inside.

3. Execute the file `ExtensiveTestingToolbox.exe` to open the toolbox.

    ![](/docs/images/toolbox_portable.png)
    
## Package for Linux

1. Go to your online test center and navigate in the menu to `Overview > Packages`. Download the Linux package.

2. Untar the file `ExtensiveTestingToolbox_XX.XX.XX_Setup.tar.gz` and go inside.

3. Execute the script `./toolagent` or `./toolprobe` to display the help

        ./toolagent
        Command line tool launcher

        Usage: ./toolagent [test-server-ip] [test-server-port] [ssl-support] [ftp|sikulix|socket|dummy|database|selenium|gateway-sms|command|soapui|file|adb|ssh] [tool-name] [tool-description] [[proxy-ip] [proxy-port]]

        * Server parameters
        [test-server-ip]: your test server ip or hostname. This option is mandatory.
        [test-server-port]: your test server port. This option is mandatory.
        [ssl-support=True/False]: ssl support. This option is mandatory.

        * Tools parameters
        [Values expected: ftp|sikulix|socket|dummy|database|selenium|gateway-sms|command|soapui|file|adb|ssh]: tool type to start. This option is mandatory.
        [tool-name]: The tool name. This option is mandatory.
        [tool-description]: The tool description. This option is mandatory.

        * Proxy parameters
        [proxy-ip]: proxy address. This option is optional.
        [proxy-port]: proxy port. This option is optional.

        ./toolprobe
        Command line tool launcher

        Usage: ./toolprobe [test-server-ip] [test-server-port] [ssl-support] [dummy|textual|network|file] [tool-name] [tool-description] [[proxy-ip] [proxy-port]]

        * Server parameters
        [test-server-ip]: your test server ip or hostname. This option is mandatory.
        [test-server-port]: your test server port. This option is mandatory.
        [ssl-support=True/False]: ssl support. This option is mandatory.

        * Tools parameters
        [Values expected: dummy|textual|network|file]: tool type to start. This option is mandatory.
        [tool-name]: The tool name. This option is mandatory.
        [tool-description]: The tool description. This option is mandatory.

        * Proxy parameters
        [proxy-ip]: proxy address. This option is optional.
        [proxy-port]: proxy port. This option is optional.
