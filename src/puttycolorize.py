import winreg

from pathlib import Path


class Putty:

    hive = winreg.HKEY_CURRENT_USER
    regKey = r"Software\SimonTatham\PuTTY\Sessions"
    regFullKey = r"HKEY_CURRENT_USER" + "\\" + regKey

    def __init__(self):
        self.rootDir = Path(__file__).parent
        # self.includeFile = os.path.normpath(os.path.join(self.binPath, "include.txt"))

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

    def get_immediate_subkeys(self, hive, key_path):
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
            print(f"\nKey: {reg_path}")

            try:
                # Get values in current key
                i = 0
                while True:
                    try:
                        name, value, type = winreg.EnumValue(registry_key, i)
                        print(f"Value {i + 1}:")
                        print(f"  Name: {name}")
                        print(f"  Data: {value}")
                        print(f"  Type: {type}")
                        i += 1
                    except WindowsError as err:
                        print(err)
                        break
            except WindowsError:
                pass

            try:
                # Get subkeys
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(registry_key, i)
                        subkey_path = f"{reg_path}\\{subkey_name}"
                        # Recursive call for subkeys
                        get_all_keys_and_subkeys(hive, subkey_path)
                        i += 1
                    except WindowsError:
                        break
            except WindowsError:
                pass

            winreg.CloseKey(registry_key)

        except WindowsError as e:
            print(f"Error accessing {reg_path}: {str(e)}")

    def exportPutty(self):
        print(f"*** Reading from {self.regFullKey} ***")
        print("=" * 50)

        subkeys = self.get_immediate_subkeys(self.hive, self.regKey)
        for key in subkeys:
            newkey = self.regKey + "\\" + key

            self.get_all_keys_and_subkeys(self.hive, newkey)

        # Example usage
        session_name = "Default%20Settings"  # Use the exact name as in registry
        setting_name = "Colour0"
        new_value = "131,148,150"

        change_putty_setting(session_name, setting_name, new_value)

    def start(self):
        self.exportPutty()


if __name__ == "__main__":
    putty = Putty()
    putty.start()
