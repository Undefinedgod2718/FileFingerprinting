; Build: tools\build-installer.ps1 -LegacyCoreSource <path>
; Requires: publish\installer-staging\ from publish.ps1 -ForInstaller

#ifndef StagingDir
  #define StagingDir "..\..\publish\installer-staging"
#endif
#ifndef OutputDir
  #define OutputDir "..\..\publish\installer"
#endif

[Setup]
AppId={{A7B3C9E1-4F2D-4A8B-9C0E-F1D2E3A4B5C6}
AppName={cm:MyAppName}
AppVersion=1.0.1
AppPublisher={cm:MyAppPublisher}
DefaultDirName={autopf}\File Fingerprinting
DefaultGroupName={cm:MyAppName}
OutputDir={#OutputDir}
OutputBaseFilename=FileFingerprinting-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=..\..\src\TpFileM.App\Assets\logo.ico
WizardSmallImageFile=assets\wizard_small.bmp
UninstallDisplayIcon={app}\FileFingerprinting.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesetrad"; MessagesFile: "languages\ChineseTraditional.isl"

[CustomMessages]
english.MyAppName=File Fingerprinting
chinesetrad.MyAppName=文件指紋識別
english.MyAppPublisher=File Fingerprinting
chinesetrad.MyAppPublisher=文件指紋識別

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#StagingDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "*.pdb"

[Icons]
Name: "{group}\{cm:MyAppName}"; Filename: "{app}\FileFingerprinting.exe"
Name: "{autodesktop}\{cm:MyAppName}"; Filename: "{app}\FileFingerprinting.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\FileFingerprinting.exe"; Description: "{cm:LaunchProgram,{cm:MyAppName}}"; Flags: nowait postinstall skipifsilent
