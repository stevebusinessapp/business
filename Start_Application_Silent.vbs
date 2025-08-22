' Multi-Purpose Business Application Silent Launcher
' This script runs the PowerShell launcher without showing a console window

Option Explicit

Dim objShell, strPath, strCommand

' Get the directory where this script is located
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Create shell object
Set objShell = CreateObject("WScript.Shell")

' Change to the application directory
objShell.CurrentDirectory = strPath

' Build the PowerShell command
strCommand = "powershell.exe -ExecutionPolicy Bypass -File """ & strPath & "\Start_Application.ps1"" -Silent"

' Run the PowerShell script
objShell.Run strCommand, 0, False

' Clean up
Set objShell = Nothing
