$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('C:\Users\nongj\Desktop\CookieRun Bot.lnk')
$s.TargetPath = 'C:\Users\nongj\AppData\Local\Programs\Python\Python314\pythonw.exe'
$s.Arguments = '"C:\Users\nongj\Desktop\Cookie bot\gui_bot.py"'
$s.WorkingDirectory = 'C:\Users\nongj\Desktop\Cookie bot'
$s.Save()
