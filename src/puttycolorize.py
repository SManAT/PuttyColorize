import winreg
import os

from pathlib import Path


class Putty:

    hive = winreg.HKEY_CURRENT_USER
    regKey = r"Software\SimonTatham\PuTTY\Sessions"
    regFullKey = r"HKEY_CURRENT_USER" + "\\" + regKey

    data = []

    def __init__(self):
        self.rootPath = Path(__file__).parent
        self.regFile = os.path.normpath(os.path.join(self.rootPath, "PuttyBackup.reg"))

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

    def start(self):
        self.exportPutty()


if __name__ == "__main__":
    putty = Putty()
    putty.start()
