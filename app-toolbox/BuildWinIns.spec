# -*- mode: python -*-

block_cipher = None


a = Analysis(['Systray.py'],
             pathex=[ '.', './Dlls64/' ],
             binaries=[],
             datas=[ 
                        ( './releasenotes.txt', '.'),
                        ( './Resources/small_installer.bmp', '.'),
                        ( './settings.ini', '.' ),
                        ( './HISTORY', '.'),
                        ( './VERSION', '.'),
                        ( './LICENSE-LGPLv21', '.'),
                        ( './Dlls64/opengl32sw.dll', '.' ),
                        ( './Dlls64/imageformats', 'imageformats' ),
                        ( './Bin/Adb', './Bin/Adb' ),
                        ( './Bin/Java8', './Bin/Java8' ),
                        ( './Bin/MicrosoftSQL', './Bin/MicrosoftSQL' ),
                        ( './Bin/Selenium', './Bin/Selenium' ),
                        ( './Bin/Selenium2', './Bin/Selenium2' ),
                        ( './Bin/Selenium3', './Bin/Selenium3' ),
                        ( './Bin/Sikuli', './Bin/Sikuli' ),
                        ( './Resources/ExtensiveTestingToolbox.ico', '.' )
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='ExtensiveTestingToolbox',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='./Resources/ExtensiveTestingToolbox.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ExtensiveTestingToolbox')
