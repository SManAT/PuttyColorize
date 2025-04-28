import winreg
aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
print(r"*** Reading from %s ***" % aKey)

aKey = winreg.OpenKey(aReg, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall')
for i in range(1024):
    try:
        aValue_name = winreg.EnumKey(aKey, i)
        oKey = winreg.OpenKey(aKey, aValue_name)
        sValue = winreg.QueryValueEx(oKey, "DisplayName")
        print(sValue)
    except EnvironmentError:
        break
