# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\USER\\Desktop\\JJ\\python\\mirror-window\\mirror-window\\.venv2\\Lib\\site-packages', 'C:\\Users\\USER\\Desktop\\JJ\\python\\mirror-window\\mirror-window'],
             binaries=[],
             datas=[],
             hiddenimports=['pywintypes','win32gui'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Mirror Window',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
		  icon=['icon.ico'])
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
