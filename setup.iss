[Setup]
AppName=GioHuAI Translator
AppVersion=0.1
DefaultDirName={pf}\GioHuAI
DefaultGroupName=GioHuAI
OutputDir=.
OutputBaseFilename=GioHuAI_v0.1_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=asset\icon_installer.ico

[Files]
; App files to Program Files
Source: "dist\main\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "asset\icon.ico"; DestDir: "{app}"

; Config files to %APPDATA%\GioHuAI (created only if missing)
Source: "config.json"; DestDir: "{userappdata}\GioHuAI"; Flags: onlyifdoesntexist
Source: "characters.json"; DestDir: "{userappdata}\GioHuAI"; Flags: onlyifdoesntexist

[Dirs]
; Create %APPDATA%\GioHuAI directory (in case config isn't written yet)
Name: "{userappdata}\GioHuAI"

[Icons]
Name: "{group}\GioHuAI"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"
Name: "{commondesktop}\GioHuAI"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
