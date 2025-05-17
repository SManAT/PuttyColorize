import winreg
import os
import questionary

from pathlib import Path

from libs.TerminalColors import TerminalColors


class Putty:

    hive = winreg.HKEY_CURRENT_USER
    regKey = r"Software\SimonTatham\PuTTY\Sessions"
    regFullKey = r"HKEY_CURRENT_USER" + "\\" + regKey

    defaultProfile = "-All-"

    data = []

    def __init__(self):
        self.rootPath = Path(__file__).parent
        self.regFile = os.path.normpath(os.path.join(self.rootPath, "PuttyBackup.reg"))

        self.term = TerminalColors()
        self.term.set_BackgroundColor()

    def printNStore(self, msg):
        print(msg.strip())
        self.data.append(msg)

    def change_putty_setting(session_name, setting_name, new_value):
        # Base path for PuTTY session
        base_path = r"SOFTWARE\SimonTatham\PuTTY\Sessions"
        session_path = f"{base_path}\\{session_name}"

        try:
            # Open the key with write access
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, session_path, 0, winreg.KEY_WRITE)

            # Set the new value
            winreg.SetValueEx(key, setting_name, 0, winreg.REG_SZ, new_value)

            # Close the key
            winreg.CloseKey(key)
            print(f"Successfully changed {setting_name} to {new_value}")

        except WindowsError as e:
            print(f"Error: {str(e)}")

    def get_subkeys(self, hive, key_path):
        """get all Subkeys from a Key"""
        try:
            # Open the registry key
            key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)

            # List to store subkeys
            subkeys = []

            # Enumerate all subkeys
            i = 0
            while True:
                try:
                    # Get subkey name
                    subkey_name = winreg.EnumKey(key, i)
                    subkeys.append(subkey_name)
                    i += 1
                except WindowsError:
                    break

            winreg.CloseKey(key)
            return subkeys

        except WindowsError as e:
            print(f"Error accessing {key_path}: {str(e)}")
            return []

    def getType(self, type):
        if type == 4:
            return "dword:"
        return ""

    def get_all_keys_and_subkeys(self, hive, reg_path):
        """
        Recursively get all keys and their subkeys from a specified registry path
        Args:
            hive: Registry hive (e.g., winreg.HKEY_LOCAL_MACHINE)
            reg_path: Registry path to start from
        """
        try:
            # Open the registry key
            registry_key = winreg.OpenKey(hive, reg_path, 0, winreg.KEY_READ)
            # Print current key path
            self.printNStore(f"\n[HKEY_CURRENT_USER\\{reg_path}]\n")

            try:
                # Get values in current key
                i = 0
                while True:
                    try:
                        name, value, type = winreg.EnumValue(registry_key, i)
                        if self.getType(type) == "":
                            self.printNStore(f'"{name}"="{value}"\n')
                        else:
                            self.printNStore(f'"{name}"={self.getType(type)}{value}\n')
                        i += 1
                    except WindowsError as err:
                        # print(err)
                        break
            except WindowsError:
                pass

        except WindowsError as e:
            print(f"Error accessing {reg_path}: {str(e)}")

    def savetoFile(self):
        """save putty export to *.reg File"""
        with open(self.regFile, "w") as f:
            for d in self.data:
                f.write(d)
        f.close()
        s = os.path.join("src", os.path.basename(self.regFile))
        self.term.print(f"\nPutty Config saved to  {s} ...", "RED")

    def exportPutty(self):
        print(f"*** Reading from {self.regFullKey} ***")
        print("=" * 50)

        msg = f"\n[{self.regFullKey}]\n"
        self.data.append(msg)

        subkeys = self.get_subkeys(self.hive, self.regKey)
        for key in subkeys:
            newkey = self.regKey + "\\" + key
            self.get_all_keys_and_subkeys(self.hive, newkey)

        self.savetoFile()

        # ???Example usage ---------------------------------------------
        session_name = "Default%20Settings"  # Use the exact name as in registry
        setting_name = "Colour0"
        new_value = "131,148,150"

        # change_putty_setting(session_name, setting_name, new_value)

    def search_files_in_dir(self, directory=".", pattern=""):
        """
        search for pattern in directory NOT recursive
        :param directory: path where to search. relative or absolute
        :param pattern: a list e.g. ['.jpg', '.gif']
        """
        data = []
        for child in Path(directory).iterdir():
            if child.is_file():
                # print(f"{child.name}")
                if pattern == "":
                    data.append(os.path.join(directory, child.name))
                else:
                    for p in pattern:
                        if child.name.endswith(p):
                            data.append(os.path.join(directory, child.name))
        return data

    def loadThemes(self):
        """Load all themes, my own first"""
        myfiles = self.search_files_in_dir(self.rootPath, ".reg")
        themesPath = os.path.normpath(os.path.join(self.rootPath, "themes"))
        files = self.search_files_in_dir(themesPath)
        data = []
        for f in myfiles:
            if os.path.basename(f) != "PuttyBackup.reg":
                data.append(os.path.basename(f))
        # Trennlinien
        data.append("------")
        for f in files:
            data.append(os.path.basename(f))
        return data

    def loadProfiles(self):
        f = open(self.regFile, "r")
        lines = f.readlines()
        f.close()

        data = []
        data.append(self.defaultProfile)
        for l in lines:
            if self.regFullKey in l:
                parts = l.split("\\")
                name = parts[len(parts) - 1]
                name = name.strip()
                name = name[:-1]
                if name != "Sessions":
                    data.append(name)
        return data

    def start(self):
        self.term.print(f"\nSee https://github.com/mbadolato/iTerm2-Color-Schemes ...", "YELLOW")

        self.exportPutty()

        profiles = self.loadProfiles()
        p_answ = questionary.select("Which Profile to modify?", choices=profiles).ask()

        themes = self.loadThemes()
        answ = "------"
        while answ == "------":
            answ = questionary.select("Which Color Theme to apply?", choices=themes).ask()

        if p_answ == self.defaultProfile:
            ok = questionary.confirm(f"Using theme {answ} for all profiles?").ask()
        else:
            ok = questionary.confirm(f"Using theme {answ} for profile {p_answ}?").ask()

        if ok:
            print("changing")


if __name__ == "__main__":
    putty = Putty()
    putty.start()
