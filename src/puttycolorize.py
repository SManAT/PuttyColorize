import winreg

from pathlib import Path


class Putty:

    regKey = r"Software\SimonTatham\PuTTY"
    regFullKey = r"HKEY_CURRENT_USER" + "\\" + regKey

    def __init__(self):
        self.rootDir = Path(__file__).parent
        # self.includeFile = os.path.normpath(os.path.join(self.binPath, "include.txt"))

    def get_keys(self, path, i=0):
        try:
            yield winreg.EnumValue(winreg.OpenKey(winreg.HKEY_CURRENT_USER, path), i)
            yield from get_keys(path, i + 1)
        except WindowsError as err:
            pass

    def exportPutty(self):
        aReg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        print(f"*** Reading from {self.regFullKey} ***")

        for name, value, type in aReg.get_keys(self.regFullKey):
            print(f"{name} => {value} ({type})")

        aKey = winreg.OpenKey(aReg, self.regKey)
        for i in range(1024):
            try:
                aValue_name = winreg.EnumKey(aKey, i)
                oKey = winreg.OpenKey(aKey, aValue_name)
                # sValue = winreg.QueryValueEx(oKey, "DisplayName")
                print(aValue_name)
                print(oKey)

            except EnvironmentError:
                break

    def start(self):
        self.exportPutty()


if __name__ == "__main__":
    putty = Putty()
    putty.start()
