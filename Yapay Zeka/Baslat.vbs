Set WshShell = CreateObject("WScript.Shell")

WshShell.CurrentDirectory = "C:\Users\PC\Desktop\Yapay Zeka"

WshShell.Run """C:\Users\PC\AppData\Local\Programs\Python\Python39\python.exe"" ""C:\Users\PC\Desktop\Yapay Zeka\Doner.py""", 0, False