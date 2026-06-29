' SafeNet Kids — Stop Monitoring (Parent Only)
' Run this script to stop the background monitoring agent.

Dim shell
Set shell = CreateObject("WScript.Shell")
shell.Run "taskkill /F /IM python.exe /T", 0, True

MsgBox "SafeNet Kids monitoring has been stopped.", vbInformation, "SafeNet Kids"
