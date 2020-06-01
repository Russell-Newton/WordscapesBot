from win32gui import GetForegroundWindow, GetWindowText, GetWindowRect,  PumpMessages
import time
from game import Game
import pyHook
from threading import Thread
import os


last_keypress = -1


def OnKeyboardEvent(event):
    global last_keypress
    # print(event.Key)
    last_keypress = int(event.KeyID)
    return True


class Driver:
    def __init__(self):
        self.current_window = None
        self.previous_window = None
        self.game = None

    def setup(self):
        self.current_window = self.previous_window = GetForegroundWindow()

        while not GetWindowText(self.current_window).startswith("BlueStacks"):
            self.update_window_information()
            print("Switch to BlueStacks!")
            time.sleep(1)

        self.game = Game(self.current_window, save_images=True)
        self.game.load_level()

    def loop(self):
        global last_keypress
        finished_level = False
        while last_keypress is not 67:          # C
            if self.game.enter_word() is None:
                if not finished_level:
                    print("Done! Press enter to start solving the next level or C to exit.")
                    finished_level = True
            time.sleep(0.1)

            if finished_level and last_keypress is 13:      # Enter
                print("Starting new level.")
                last_keypress = ""
                finished_level = False
                self.game.load_level()

        os._exit(-1)

    def update_window_information(self):
        self.current_window = GetForegroundWindow()
        if self.current_window != self.previous_window:
            bbox = GetWindowRect(self.current_window)
            print(GetWindowText(self.current_window))
            print("({}, {}), w: {}, h: {}".format(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]))
            print()
        self.previous_window = self.current_window

if __name__ == '__main__':
    driver = Driver()
    hook_manager = pyHook.HookManager()
    hook_manager.KeyDown = OnKeyboardEvent

    driver.setup()
    # while True:
    time.sleep(0.75)

    hook_manager.HookKeyboard()
    Thread(target=driver.loop).start()
    PumpMessages()
