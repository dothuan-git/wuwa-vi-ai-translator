[Setup]
AppName=GioHuAI Translator
AppVersion=0.1
DefaultDirName={pf}\GioHuAI
DefaultGroupName=GioHuAI
OutputDir=.
OutputBaseFilename=GioHuAI_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\main\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "asset\icon.ico"; DestDir: "{app}"

[Icons]
Name: "{group}\GioHuAI"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"
Name: "{commondesktop}\GioHuAI"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
