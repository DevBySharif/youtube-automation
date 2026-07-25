; installer.iss
; Inno Setup Script for Timestamp Script Analyzer (v1.0.0)
;
; To build the installer:
;   1. Download & install Inno Setup: https://jrsoftware.org/isdl.php
;   2. Open installer.iss in Inno Setup Compiler and click Compile (Ctrl+F9)
;   3. Output installer will be created in Output\TimestampScriptAnalyzer_Setup_v1.0.0.exe

#define MyAppName "Timestamp Script Analyzer"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "TimestampAnalyzer Team"
#define MyAppURL "https://github.com/espeak-ng/espeak-ng"
#define MyAppExeName "Timestamp Script Analyzer.exe"

[Setup]
AppId={{E91C59FF-DFF2-4585-B6A4-CDE51C26F303}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=TimestampScriptAnalyzer_Setup_v1.0.0
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Timestamp Script Analyzer\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Timestamp Script Analyzer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
