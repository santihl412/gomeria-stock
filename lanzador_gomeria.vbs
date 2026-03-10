Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd.exe /c streamlit run app.py --browser.gatherUsageStats false", 0
Set WshShell = Nothing