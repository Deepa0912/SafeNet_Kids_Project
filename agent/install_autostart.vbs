' SafeNet Kids — Add to Windows Startup
' Run this ONCE as Administrator to make monitoring start automatically on every boot.
' The child will never know it is running.

Dim fso, shell, folder, shortcutPath, startupFolder

Set fso   = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' Folder where THIS vbs file lives
folder = fso.GetParentFolderName(WScript.ScriptFullName)

' Windows Startup folder path
startupFolder = shell.SpecialFolders("Startup")

' Create a shortcut to start_silent.vbs in the Startup folder
shortcutPath = startupFolder & "\SafeNet_Kids_Monitor.lnk"

Dim shortcut
Set shortcut = shell.CreateShortcut(shortcutPath)
shortcut.TargetPath   = folder & "\start_silent.vbs"
shortcut.WorkingDirectory = folder
shortcut.Description  = "SafeNet Kids Child Monitor"
shortcut.Save

MsgBox "SafeNet Kids monitoring will now start automatically on every boot." & Chr(13) & _
       "The child cannot see or stop it.", vbInformation, "SafeNet Kids — Setup Complete"
