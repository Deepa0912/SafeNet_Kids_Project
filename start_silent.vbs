' SafeNet Kids — Silent Background Launcher
' Double-click this file to start monitoring invisibly.
' No window will appear. The child cannot see or stop it.

Dim shell
Set shell = CreateObject("WScript.Shell")

' Get the folder where this VBS file lives
Dim folder
folder = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Run monitor.py silently (0 = hidden window, False = don't wait)
shell.Run "cmd /c cd /d """ & folder & """ && set SAFENET_API=https://safenetkidsproject-production.up.railway.app && python monitor.py", 0, False

WScript.Quit
