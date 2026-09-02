Set WshShell = CreateObject("WScript.Shell")
Set shortcut = WshShell.CreateShortcut("C:\Users\nongj\Desktop\CookieRun Bot.lnk")
shortcut.TargetPath = ""C:\Users\nongj\AppData\Local\Programs\Python\Python314\pythonw.exe""
shortcut.Arguments = """C:\Users\nongj\Desktop\Cookie bot\gui_bot.py"""
shortcut.WorkingDirectory = ""C:\Users\nongj\Desktop\Cookie bot""
shortcut.Description = "CookieRun AutoBot GUI"
shortcut.Save
