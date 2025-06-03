[Setup]
AppName=Wuwa AI Translator
AppVersion=1.0
DefaultDirName={pf}\WuwaAITrans
DefaultGroupName=WuwaAITrans
OutputDir=.
OutputBaseFilename=WuwaAITrans_Setup

[Files]
Source: "dist\main\*"; DestDir: "{app}"; Flags: recursesubdirs
Source: "dist\main\characters.json"; DestDir: "{app}"

[Icons]
Name: "{group}\WuwaAITrans"; Filename: "{app}\main.exe"
