# -*- mode: python -*-

block_cipher = None


a = Analysis(['Main.py'],
             pathex=[ '.', './Dlls64/' ],
             binaries=[],
             datas=[ 
                        ('./Resources/releasenotes.txt', '.'),
                        ('./Resources/small_installer.bmp', '.'),
                        ( './Files', 'Files' ),
                        ('./HISTORY', '.'),
                        ('./LICENSE-LGPLv21', '.'),
                        ( './Dlls64/opengl32sw.dll', '.' ),
                        ( './Dlls64/imageformats', 'imageformats' ),
                        ( './Files', 'Files' )
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
          name='ExtensiveTestingClient',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='./Resources/ExtensiveTestingClient.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ExtensiveTestingClient')
